"""Build deterministic Study 1 plans containing the exact frozen request for each draw."""

import os
import random
from copy import deepcopy
from dataclasses import asdict, replace
from pathlib import Path
from typing import Any

import yaml

from kinloyalty.clients.base import ModelRequest
from kinloyalty.clients.payloads import build_api_payload
from kinloyalty.logs import assert_no_credentials, file_hash, json_line, read_jsonl
from kinloyalty.prompts import load_prompt_library, render_prompt
from kinloyalty.validate import check_schema


def _check_allocation(study: dict[str, Any], models: dict[str, Any], phase: str) -> None:
    paraphrases = len(study["paraphrases"])
    if phase == "pilot":
        spec = study[phase]
        if (
            spec["draws_per_label"] != spec["minimum_draws_per_paraphrase"] * paraphrases + 1
            or spec["draws_per_model_decision"] != len(study["labels"]) * spec["draws_per_label"]
            or spec["extra_paraphrase_rule"] != "label_plus_model_plus_decision_index_modulo_3"
            or spec["other_lab_rule"] != "cycle_roster_with_decision_offset"
        ):
            raise ValueError("Pilot allocation fields are inconsistent or use an unsupported rule.")
    if phase == "comprehension":
        spec = study[phase]
        matrix = spec["other_lab_joint_counts"]
        if (
            len(spec["paraphrase_counts"]) != paraphrases
            or sum(spec["paraphrase_counts"]) != spec["draws_per_model_label"]
            or len(matrix) != paraphrases
            or any(len(row) != len(spec["other_lab_name_counts"]) for row in matrix)
            or [sum(row) for row in matrix] != spec["paraphrase_counts"]
            or [sum(row[index] for row in matrix) for index in range(len(spec["other_lab_name_counts"]))] != spec["other_lab_name_counts"]
        ):
            raise ValueError("Comprehension matrix and configured 7/7/6 margins disagree.")
    for model in models.values():
        others = sum(value["lab"] != model["lab"] for value in models.values())
        if phase == "main":
            spec = study[phase]
            counts = spec["other_lab"]["counts_within_paraphrase"]
            if len(counts) != others or sum(counts) != spec["draws_per_model_decision_label_paraphrase"]:
                raise ValueError("Main other-lab counts do not match the roster or cell size.")
            if spec["other_lab"]["rotate_shortfall_across_paraphrases"] and paraphrases != others:
                raise ValueError("Rotating other-lab shortfalls requires one paraphrase per other model.")
        if phase == "comprehension" and others != len(study[phase]["other_lab_name_counts"]):
            raise ValueError("Comprehension matrix does not match the other-lab roster.")


def build_manifest(config_path: str | Path, phase: str) -> list[dict[str, Any]]:
    """Create a balanced plan and seed-shuffled order without calling any model."""
    if phase not in {"smoke", "pilot", "comprehension", "main"}:
        raise ValueError(f"Unknown phase: {phase}")
    config_path = Path(config_path).resolve()
    library = load_prompt_library(config_path)
    study = library.study
    _check_allocation(study, library.models, phase)
    roster_path = config_path.parent / study["models_file"]
    roster = yaml.safe_load(roster_path.read_text(encoding="utf-8"))
    source_hashes = {
        "study_config": file_hash(config_path), "model_config": file_hash(roster_path),
        "templates": {path.name: file_hash(path) for path in sorted(library.template_directory.glob("*.txt"))},
    }
    seed = study["seeds"][f"{phase}_order"]
    trials: list[dict[str, Any]] = []

    def add(model: str, decision: str, label: str, paraphrase: int, draw: int, other: str | None) -> None:
        prompt = render_prompt(
            library, model=model, decision=decision, label=label,
            paraphrase=paraphrase, other_model=other,
        )
        names = next(entry for entry in study["paraphrases"] if entry["id"] == paraphrase)
        selected = library.models[model]
        trial_id = f"{study['study']}:{phase}:{model}:{decision}:{label}:p{paraphrase}:d{draw:03d}"
        settings = deepcopy(roster["defaults"])
        settings.update({"requested_parameters": selected["requested_parameters"], "caching": selected["caching"]})
        settings.update(verification_status=roster["verification_status"], transport=selected["transport"])
        context = {"label": label}
        if decision == "comprehension":
            context["expected_answer"] = study["comprehension"]["expected_answers"].get(label, "unsure")
        request = ModelRequest(
            trial_id=trial_id, provider=selected["provider"], api_model_id=selected["api_model_id"],
            endpoint=selected["endpoint"], settings=settings, system_prompt=prompt.system_prompt,
            user_message=prompt.user_message, json_schema=prompt.json_schema, context=context,
        )
        request = replace(request, api_payload=build_api_payload(request))
        trials.append({
            "schema_version": 1, "study": study["study"], "phase": phase,
            "trial_id": trial_id, "model": model, "model_display_name": selected["display_name"],
            "api_model_id": selected["api_model_id"], "decision": decision, "label": label,
            "counterparty_model_text": prompt.counterparty_model_text, "other_model": other,
            "paraphrase_id": paraphrase, "principal": names["principal"],
            "counterparty": names["counterparty"], "draw_index": draw, "order_seed": seed,
            "mock_seed": study["seeds"]["mock"],
            "source_sha256": source_hashes,
            "runner_settings": {**study["runner"], "invalid_reasks": study["validation"]["identical_reasks_per_invalid_draw"]},
            "request": asdict(request),
        })

    for model_index, (model, selected) in enumerate(library.models.items()):
        others = [key for key, value in library.models.items() if value["lab"] != selected["lab"]]
        if phase == "smoke":
            spec = study["smoke"]
            for draw in range(1, spec["draws_per_model"] + 1):
                add(model, spec["decision"], spec["label"], spec["paraphrase"], draw, None)
            continue
        if phase == "comprehension":
            spec = study["comprehension"]
            for label in spec["labels"]:
                for p_index, names in enumerate(study["paraphrases"]):
                    schedule = (
                        [other for other, count in zip(others, spec["other_lab_joint_counts"][p_index], strict=True)
                         for _ in range(count)]
                        if label == "other_lab" else [None] * spec["paraphrase_counts"][p_index]
                    )
                    for draw, other in enumerate(schedule, 1):
                        add(model, "comprehension", label, names["id"], draw, other)
            continue
        for decision_index, decision in enumerate(study["decisions"]):
            for label_index, label in enumerate(study["labels"]):
                pilot_other_index = 0
                for p_index, names in enumerate(study["paraphrases"]):
                    if phase == "main":
                        count = study["main"]["draws_per_model_decision_label_paraphrase"]
                        rotation = study["main"]["other_lab"]["counts_within_paraphrase"]
                        shift = p_index if study["main"]["other_lab"]["rotate_shortfall_across_paraphrases"] else 0
                        schedule = (
                            [other for index, other in enumerate(others)
                             for _ in range(rotation[(index - shift) % len(others)])]
                            if label == "other_lab" else [None] * count
                        )
                    else:
                        extra = (label_index + model_index + decision_index) % len(study["paraphrases"])
                        count = study["pilot"]["minimum_draws_per_paraphrase"] + int(p_index == extra)
                        schedule = []
                        for _ in range(count):
                            other = others[(pilot_other_index + decision_index) % len(others)] if label == "other_lab" else None
                            schedule.append(other)
                            pilot_other_index += 1
                    for draw, other in enumerate(schedule, 1):
                        add(model, decision, label, names["id"], draw, other)
    if len(trials) != study[phase]["expected_total_draws"]:
        raise ValueError("Configured design allocation does not match expected_total_draws.")
    random.Random(seed).shuffle(trials)
    for position, trial in enumerate(trials, 1):
        trial["execution_position"] = position
    return trials


def write_manifest(trials: list[dict[str, Any]], path: str | Path) -> None:
    """Save a new immutable plan, refusing to overwrite an existing file."""
    path = Path(path)
    content = "".join(json_line(trial) for trial in trials)
    assert_no_credentials(trials)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as stream:
        stream.write(content)
        stream.flush()
        os.fsync(stream.fileno())


def read_manifest(path: str | Path) -> list[dict[str, Any]]:
    """Validate saved plan identities, order, and response schemas before execution."""
    trials = read_jsonl(path)
    if not trials:
        raise ValueError("A manifest must contain at least one planned trial.")
    ids: set[str] = set()
    for position, trial in enumerate(trials, 1):
        assert_no_credentials(trial)
        if trial.get("schema_version") != 1 or trial.get("execution_position") != position:
            raise ValueError("Unsupported manifest schema or non-contiguous execution positions.")
        trial_id = trial["trial_id"]
        if trial_id in ids or trial["request"]["trial_id"] != trial_id:
            raise ValueError("Duplicate or inconsistent manifest trial identity.")
        if trial["study"] != trials[0]["study"] or trial["phase"] != trials[0]["phase"]:
            raise ValueError("A manifest cannot mix studies or phases.")
        if trial["api_model_id"] != trial["request"]["api_model_id"]:
            raise ValueError("Manifest model metadata disagrees with the frozen request.")
        ModelRequest(**trial["request"])
        check_schema(trial["request"]["json_schema"])
        ids.add(trial_id)
    return trials
