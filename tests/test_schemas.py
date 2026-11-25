"""Check response contracts independently of provider-specific schema support."""

from copy import deepcopy
from pathlib import Path

import pytest

from kinloyalty.prompts import load_prompt_library, render_prompt
from kinloyalty.schemas import response_schema


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_FIELDS = {
    "dictator": ["amount_to_counterparty", "reason"],
    "ultimatum_proposer": [
        "amount_offered_to_counterparty",
        "smallest_offer_you_expect_counterparty_to_accept",
        "reason",
    ],
    "ultimatum_responder": ["smallest_amount_for_your_user_you_will_accept", "reason"],
    "comprehension": ["same_model"],
}


@pytest.mark.parametrize("decision", EXPECTED_FIELDS)
def test_schema_is_identical_for_all_models_labels_and_paraphrases(decision: str) -> None:
    """Prevent labels, names, or identities from leaking through the response schema."""
    library = load_prompt_library(ROOT / "configs/study1.yaml")
    expected = response_schema(decision, library.study)
    for model in library.models:
        labels = library.study["comprehension"]["labels"] if decision == "comprehension" else library.study["labels"]
        for paraphrase in (1, 2, 3):
            for label in labels:
                others = [key for key in library.models if key != model] if label == "other_lab" else [None]
                for other in others:
                    prompt = render_prompt(
                        library, model=model, decision=decision, label=label,
                        paraphrase=paraphrase, other_model=other,
                    )
                    assert prompt.json_schema == expected
                    assert list(prompt.json_schema["properties"]) == EXPECTED_FIELDS[decision]
                    assert prompt.json_schema["required"] == EXPECTED_FIELDS[decision]
                    assert prompt.json_schema["additionalProperties"] is False
    for field, schema in expected["properties"].items():
        if field == "same_model":
            assert schema == {"type": "string", "enum": ["yes", "no", "unsure"]}
        elif field == "reason":
            assert schema["type"] == "string"
        else:
            assert schema == {"type": "integer", "minimum": 0, "maximum": 100}


@pytest.mark.parametrize("decision", EXPECTED_FIELDS)
def test_optional_provider_bounds_do_not_change_canonical_contract(decision: str) -> None:
    """Permit only the documented numeric-bound fallback without mutating local schemas."""
    library = load_prompt_library(ROOT / "configs/study1.yaml")
    canonical = response_schema(decision, library.study)
    expected_without_bounds = deepcopy(canonical)
    for schema in expected_without_bounds["properties"].values():
        schema.pop("minimum", None)
        schema.pop("maximum", None)
    assert response_schema(decision, library.study, include_numeric_bounds=False) == expected_without_bounds
    changed = response_schema(decision, library.study)
    changed["properties"].clear()
    assert response_schema(decision, library.study) == canonical


def test_new_single_decision_schema_uses_configuration() -> None:
    """Allow another integer-choice task without editing the schema builder."""
    study = {
        "decisions": {"new_task": {"outcome": "chosen_amount"}},
        "game": {"amount_min": 0, "amount_max": 10},
    }
    schema = response_schema("new_task", study)
    assert schema["properties"]["chosen_amount"] == {"type": "integer", "minimum": 0, "maximum": 10}
    assert schema["required"] == ["chosen_amount", "reason"]
    with pytest.raises(ValueError, match="Unknown decision"):
        response_schema("missing", study)
