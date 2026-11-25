"""Validate saved attempt histories and extract outcomes without rendering prompts."""

from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from kinloyalty.logs import assert_no_credentials, content_hash, read_jsonl
from kinloyalty.state import reconstruct_states


TRIAL_FIELDS = (
    "schema_version", "study", "phase", "trial_id", "model", "model_display_name",
    "api_model_id", "decision", "label", "counterparty_model_text", "other_model",
    "paraphrase_id", "principal", "counterparty", "draw_index", "order_seed",
    "mock_seed", "source_sha256", "runner_settings", "request", "execution_position",
)


@dataclass
class SavedData:
    """Retain validated attempts, one status per observed trial, and valid outcomes."""

    attempts: list[dict[str, Any]]
    trials: pd.DataFrame
    decisions: pd.DataFrame
    files: list[Path]
    synthetic: bool


def load_saved_data(
    paths: Sequence[str | Path], *, phase: str, study: dict[str, Any],
    allow_synthetic: bool = False,
) -> SavedData:
    """Reject mixed phases/backends, altered history, duplicates, and pending calls.

    Source-of-truth requests and schemas come only from the logs. Configuration
    supplies expected identities/outcome names, never replacement prompt text.
    """
    files: list[Path] = []
    for source in paths:
        path = Path(source).resolve()
        candidates = sorted(path.glob("*attempts*.jsonl")) if path.is_dir() else [path]
        if not candidates:
            raise ValueError(f"No attempt logs found at {path}.")
        files.extend(candidates)
    if not files or len(set(files)) != len(files):
        raise ValueError("Supply distinct, nonempty attempt-log paths.")
    records: list[dict[str, Any]] = []
    for path in files:
        if not path.is_file():
            raise ValueError(f"Attempt log does not exist: {path}")
        if path.with_name(path.name + ".pending.json").exists():
            raise ValueError("Pending attempts must be recovered before reporting or analysis.")
        records.extend(read_jsonl(path))
    if not records:
        raise ValueError("Attempt logs contain no records.")
    modes = {record.get("execution_mode") for record in records}
    if len(modes) != 1 or not modes <= {"mock", "live"}:
        raise ValueError("Cannot mix execution backends or accept an unknown backend.")
    synthetic = modes == {"mock"}
    if synthetic and not allow_synthetic:
        raise ValueError("Synthetic input requires explicit --allow-synthetic.")
    mode = records[0]["execution_mode"]
    groups: dict[str, list[dict[str, Any]]] = {}
    trials: dict[str, dict[str, Any]] = {}
    record_ids: set[str] = set()
    model_ids: dict[str, str] = {}
    for record in records:
        assert_no_credentials(record)
        if record.get("study") != study["study"] or record.get("phase") != phase:
            raise ValueError(f"Only {study['study']} {phase} records are eligible; mixed phases are forbidden.")
        if record.get("schema_version") != 1 or record.get("synthetic") is not synthetic:
            raise ValueError("Unsupported record schema or inconsistent synthetic flag.")
        if record["record_id"] in record_ids:
            raise ValueError("Duplicate attempt record; do not supply overlapping logs.")
        record_ids.add(record["record_id"])
        decision = record["decision"]
        if (decision not in ({"comprehension"} if phase == "comprehension" else study["decisions"])
            or record["label"] not in (study["comprehension"]["labels"] if phase == "comprehension" else study["labels"])
            or record["paraphrase_id"] not in {entry["id"] for entry in study["paraphrases"]}):
            raise ValueError("Attempt has an unknown decision, label, or paraphrase.")
        prior_id = model_ids.setdefault(record["model"], record["api_model_id"])
        if prior_id != record["api_model_id"]:
            raise ValueError("A model key cannot combine different requested model IDs.")
        if not set(TRIAL_FIELDS) <= record.keys():
            raise ValueError("Incomplete frozen trial.")
        trial = {key: record[key] for key in TRIAL_FIELDS}
        if trial["request"]["trial_id"] != trial["trial_id"]:
            raise ValueError("Incomplete frozen trial or inconsistent request identity.")
        expected_id = f"{trial['study']}:{trial['phase']}:{trial['model']}:{trial['decision']}:{trial['label']}:p{trial['paraphrase_id']}:d{trial['draw_index']:03d}"
        if trial["trial_id"] != expected_id or trial["api_model_id"] != trial["request"]["api_model_id"]:
            raise ValueError("Frozen trial identity or requested model metadata is inconsistent.")
        old = trials.setdefault(trial["trial_id"], trial)
        if content_hash(old) != content_hash(trial):
            raise ValueError("Conflicting frozen trials share an identity.")
        groups.setdefault(record["manifest_sha256"], []).append(record)
    states = {}
    for digest, history in groups.items():
        # Completion order may differ, but dispatch sequence defines attempt order.
        history.sort(key=lambda record: record["dispatch_sequence"])
        subset = {record["trial_id"]: trials[record["trial_id"]] for record in history}
        if set(states) & set(subset):
            raise ValueError("A trial cannot belong to multiple frozen manifests.")
        states.update(reconstruct_states(subset, history, digest, mode, study["validation"]["identical_reasks_per_invalid_draw"]))
    status_rows, decision_rows = [], []
    by_trial: dict[str, list[dict[str, Any]]] = {}
    for record in records:
        by_trial.setdefault(record["trial_id"], []).append(record)
    for trial_id, trial in sorted(trials.items()):
        history = sorted(by_trial[trial_id], key=lambda record: record["attempt_number"])
        state = states[trial_id]
        base = {key: trial[key] for key in (
            "trial_id", "model", "model_display_name", "api_model_id", "decision", "label",
            "paraphrase_id", "draw_index", "counterparty_model_text", "other_model",
        )}
        status_rows.append({**base, "attempts": state.attempts,
                            "reasks": int(any(record["response_number"] == 2 for record in history)),
                            "api_errors": sum(record["api_error"] is not None for record in history),
                            "excluded": state.excluded, "unfinished": not state.final,
                            "valid": state.final and not state.excluded})
        if state.final and not state.excluded:
            final = history[-1]
            parsed = final["outcome"]["parsed_json"]
            if phase == "comprehension":
                values = {"same_model": parsed["same_model"]}
            else:
                spec = study["decisions"][trial["decision"]]
                values = {"outcome": parsed[spec["outcome"]],
                          "belief": parsed[spec["belief"]] if "belief" in spec else None}
            decision_rows.append({**base, **values, "record_id": final["record_id"],
                                  "git_commit": final["git_commit"],
                                  "manifest_sha256": final["manifest_sha256"],
                                  "returned_model_version": final["response"]["returned_model_version"]})
    decision_frame = pd.DataFrame(decision_rows)
    if decision_frame.empty:
        values = ["same_model"] if phase == "comprehension" else ["outcome", "belief"]
        decision_frame = pd.DataFrame(columns=[*base, *values, "record_id", "git_commit", "manifest_sha256", "returned_model_version"])
    return SavedData(records, pd.DataFrame(status_rows), decision_frame, files, synthetic)
