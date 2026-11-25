"""Check exact allocations, frozen requests, stable identities, and seeded execution order."""

from collections import Counter, defaultdict
from copy import deepcopy
from pathlib import Path
import shutil

import pytest
import yaml

from kinloyalty.logs import content_hash, json_line
from kinloyalty.manifest import build_manifest, read_manifest, write_manifest


ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def plans() -> dict[str, list[dict]]:
    """Build each configured batch without making a client call."""
    return {phase: build_manifest(ROOT / "configs/study1.yaml", phase) for phase in ("smoke", "pilot", "comprehension", "main")}


def test_main_exact_counts_and_rotations(plans: dict) -> None:
    """Enforce 900/model, 60/model-decision-label, 20/smallest cell and named other model."""
    trials = plans["main"]
    assert len(trials) == 3600
    assert set(Counter(trial["model"] for trial in trials).values()) == {900}
    assert set(Counter((t["model"], t["decision"], t["label"]) for t in trials).values()) == {60}
    assert set(Counter((t["model"], t["decision"], t["label"], t["paraphrase_id"]) for t in trials).values()) == {20}
    others = [t for t in trials if t["label"] == "other_lab"]
    assert set(Counter((t["model"], t["decision"], t["other_model"]) for t in others).values()) == {20}
    cells: dict[tuple, Counter] = defaultdict(Counter)
    shortfalls: dict[tuple, list[str]] = defaultdict(list)
    for trial in others:
        cells[(trial["model"], trial["decision"], trial["paraphrase_id"])][trial["other_model"]] += 1
    for (model, decision, _), counts in cells.items():
        assert sorted(counts.values()) == [6, 7, 7]
        shortfalls[(model, decision)].extend(name for name, count in counts.items() if count == 6)
    assert all(len(set(values)) == 3 for values in shortfalls.values())


def test_pilot_approved_balance(plans: dict) -> None:
    """Enforce all 15 cells per model-decision, four draws/label, and rotated extra repetitions."""
    trials = plans["pilot"]
    assert len(trials) == 240
    assert set(Counter((t["model"], t["decision"]) for t in trials).values()) == {20}
    assert set(Counter((t["model"], t["decision"], t["label"]) for t in trials).values()) == {4}
    smallest = Counter((t["model"], t["decision"], t["label"], t["paraphrase_id"]) for t in trials)
    assert len(smallest) == 4 * 3 * 5 * 3
    assert set(smallest.values()) == {1, 2}
    by_paraphrase: dict[tuple, Counter] = defaultdict(Counter)
    for trial in trials:
        by_paraphrase[(trial["model"], trial["decision"])][trial["paraphrase_id"]] += 1
    assert all(sorted(counts.values()) == [6, 7, 7] for counts in by_paraphrase.values())
    assert set(Counter((t["model"], t["other_model"]) for t in trials if t["label"] == "other_lab").values()) == {4}


def test_comprehension_approved_joint_rotation(plans: dict) -> None:
    """Check 320 trials, no human condition, and both 7/7/6 margins of the approved matrix."""
    trials = plans["comprehension"]
    assert len(trials) == 320
    assert {t["decision"] for t in trials} == {"comprehension"}
    assert "human" not in {t["label"] for t in trials}
    assert set(Counter((t["model"], t["label"]) for t in trials).values()) == {20}
    from kinloyalty.prompts import load_prompt_library

    models = load_prompt_library(ROOT / "configs/study1.yaml").models
    for model in models:
        other_models = [key for key in models if key != model]
        selected = [t for t in trials if t["model"] == model and t["label"] == "other_lab"]
        matrix = [[sum(t["paraphrase_id"] == p and t["other_model"] == other for t in selected) for other in other_models] for p in (1, 2, 3)]
        assert matrix == [[3, 2, 2], [2, 3, 2], [2, 2, 2]]
        for label in ("own_model", "fictional", "not_disclosed"):
            counts = Counter(t["paraphrase_id"] for t in trials if t["model"] == model and t["label"] == label)
            assert [counts[p] for p in (1, 2, 3)] == [7, 7, 6]


def test_smoke_and_stable_interleaved_order(plans: dict) -> None:
    """Keep smoke at four non-disclosure draws and regenerate the full plan byte-for-byte."""
    assert len(plans["smoke"]) == 4
    assert {(t["decision"], t["label"], t["paraphrase_id"]) for t in plans["smoke"]} == {("dictator", "not_disclosed", 1)}
    rebuilt = build_manifest(ROOT / "configs/study1.yaml", "main")
    assert content_hash(rebuilt) == content_hash(plans["main"])
    assert [t["execution_position"] for t in rebuilt] == list(range(1, 3601))
    assert len({t["trial_id"] for t in rebuilt}) == 3600
    assert len({t["model"] for t in rebuilt[:60]}) == 4
    assert len({t["label"] for t in rebuilt[:60]}) == 5


def test_manifest_roundtrip_preserves_schema_order_and_is_immutable(tmp_path: Path, plans: dict) -> None:
    """Never reorder proposer fields or overwrite a saved plan by regeneration."""
    path = tmp_path / "manifest.jsonl"
    write_manifest(plans["pilot"], path)
    restored = read_manifest(path)
    assert restored == plans["pilot"]
    proposer = next(t for t in restored if t["decision"] == "ultimatum_proposer")
    assert list(proposer["request"]["json_schema"]["properties"]) == [
        "amount_offered_to_counterparty", "smallest_offer_you_expect_counterparty_to_accept", "reason"
    ]
    with pytest.raises(FileExistsError):
        write_manifest(plans["pilot"], path)


@pytest.mark.parametrize("change", ("duplicate", "position", "phase", "model", "credentials"))
def test_bad_manifests_are_rejected_before_execution(tmp_path: Path, plans: dict, change: str) -> None:
    """Refuse mismatched identities or secret-bearing request fields."""
    trials = deepcopy(plans["smoke"])
    if change == "duplicate":
        trials[1]["trial_id"] = trials[0]["trial_id"]
        trials[1]["request"]["trial_id"] = trials[0]["trial_id"]
    elif change == "position":
        trials[0]["execution_position"] = 2
    elif change == "phase":
        trials[1]["phase"] = "pilot"
    elif change == "model":
        trials[0]["api_model_id"] = "changed"
    else:
        trials[0]["request"]["settings"]["api_key"] = "must-not-be-written"
    path = tmp_path / "bad.jsonl"
    path.write_text("".join(json_line(t) for t in trials))
    with pytest.raises(ValueError):
        read_manifest(path)


def test_order_seed_changes_order_without_changing_trial_ids(tmp_path: Path, plans: dict) -> None:
    """Keep draw identity independent of seed-shuffled position and filesystem location."""
    shutil.copytree(ROOT / "configs", tmp_path / "configs")
    shutil.copytree(ROOT / "prompts", tmp_path / "prompts")
    path = tmp_path / "configs/study1.yaml"
    study = yaml.safe_load(path.read_text())
    study["seeds"]["main_order"] += 1
    path.write_text(yaml.safe_dump(study, sort_keys=False))
    changed = build_manifest(path, "main")
    original_ids = [trial["trial_id"] for trial in plans["main"]]
    changed_ids = [trial["trial_id"] for trial in changed]
    assert set(original_ids) == set(changed_ids)
    assert original_ids != changed_ids


@pytest.mark.parametrize("phase", ("pilot", "comprehension", "main"))
def test_inconsistent_allocation_config_does_not_get_silently_ignored(tmp_path: Path, phase: str) -> None:
    """Catch contradictory quantitative fields before even producing a frozen plan."""
    shutil.copytree(ROOT / "configs", tmp_path / "configs")
    shutil.copytree(ROOT / "prompts", tmp_path / "prompts")
    path = tmp_path / "configs/study1.yaml"
    study = yaml.safe_load(path.read_text())
    if phase == "pilot":
        study[phase]["draws_per_label"] = 5
    elif phase == "comprehension":
        study[phase]["other_lab_joint_counts"][0][0] = 4
    else:
        study[phase]["other_lab"]["counts_within_paraphrase"] = [8, 7, 6]
    path.write_text(yaml.safe_dump(study, sort_keys=False))
    with pytest.raises(ValueError):
        build_manifest(path, phase)
