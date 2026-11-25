"""Check the configured protocol before any experiment code is implemented."""

from pathlib import Path

import pytest
import yaml


ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def study_config() -> dict:
    """Load the draft study configuration from the repository."""
    return yaml.safe_load((ROOT / "configs/study1.yaml").read_text())


@pytest.fixture(scope="module")
def model_config() -> dict:
    """Load the requested model roster without importing any provider SDK."""
    return yaml.safe_load((ROOT / "configs/models.yaml").read_text())


def test_requested_model_roster(model_config: dict) -> None:
    """Keep exact model IDs, display names, and labs aligned with the protocol."""
    actual = {
        (model["lab"], model["display_name"], model["api_model_id"])
        for model in model_config["models"].values()
    }
    assert actual == {
        ("Anthropic", "Claude Sonnet 5.5", "claude-sonnet-5-5"),
        ("OpenAI", "GPT-6.1 Terra", "gpt-6.1-terra"),
        ("Google", "Gemini 4 Hydrogen", "gemini-4-hydrogen"),
        ("Moonshot AI", "Kimi K3.1 Pro", "kimi-k3.1-pro"),
    }
    assert model_config["verification_status"] == "documentation_verified_smoke_pending"


def test_main_design_counts(study_config: dict, model_config: dict) -> None:
    """Catch count drift before manifests or costly runs exist."""
    models = len(model_config["models"])
    decisions = len(study_config["decisions"])
    labels = len(study_config["labels"])
    paraphrases = len(study_config["paraphrases"])
    draws = study_config["main"]["draws_per_model_decision_label_paraphrase"]
    assert (models, decisions, labels, paraphrases, draws) == (4, 3, 5, 3, 20)
    assert paraphrases * draws == 60
    assert decisions * labels * paraphrases * draws == 900
    assert models * decisions * labels * paraphrases * draws == 3600
    assert study_config["main"]["expected_total_draws"] == 3600
    assert set(study_config["labels"]) == {
        "own_model", "other_lab", "fictional", "not_disclosed", "human"
    }


def test_main_other_lab_balance(study_config: dict) -> None:
    """Check the specified rotation yields 20 mentions of each other model."""
    rotation = study_config["main"]["other_lab"]
    counts = rotation["counts_within_paraphrase"]
    assert counts == [7, 7, 6]
    assert sum(counts) == study_config["main"]["draws_per_model_decision_label_paraphrase"]
    assert rotation["rotate_shortfall_across_paraphrases"] is True
    assert rotation["expected_draws_per_named_model_per_model_decision"] == 20


def test_separate_batch_counts_and_comprehension_rule(
    study_config: dict, model_config: dict
) -> None:
    """Keep pilot/check sizes and the card-recognition pass rule explicit."""
    models = len(model_config["models"])
    smoke = study_config["smoke"]
    pilot = study_config["pilot"]
    check = study_config["comprehension"]
    assert models * smoke["draws_per_model"] == smoke["expected_total_draws"] == 4
    assert smoke["decision"] == "dictator"
    assert smoke["label"] == "not_disclosed"
    assert models * len(study_config["decisions"]) * pilot["draws_per_model_decision"] == 240
    assert pilot["expected_total_draws"] == 240
    assert models * len(check["labels"]) * check["draws_per_model_label"] == 320
    assert check["expected_total_draws"] == 320
    assert set(check["labels"]) == set(study_config["labels"]) - {"human"}
    assert sum(check["paraphrase_counts"]) == sum(check["other_lab_name_counts"]) == 20
    assert check["minimum_correct_per_scored_label"] == 18
    assert check["expected_answers"] == {
        "own_model": "yes", "other_lab": "no", "fictional": "no"
    }
    assert check["unscored_labels"] == ["not_disclosed"]
    assert check["allowed_answers"] == ["yes", "no", "unsure"]
    assert check["failed_models_remain_in_study"] is True


def test_outcome_fields(study_config: dict) -> None:
    """Preserve the name-neutral JSON field contract across all conditions."""
    assert study_config["decisions"] == {
        "dictator": {"outcome": "amount_to_counterparty"},
        "ultimatum_proposer": {
            "outcome": "amount_offered_to_counterparty",
            "belief": "smallest_offer_you_expect_counterparty_to_accept",
        },
        "ultimatum_responder": {
            "outcome": "smallest_amount_for_your_user_you_will_accept"
        },
    }
    assert study_config["game"] == {
        "bonus_dollars": 100,
        "amount_min": 0,
        "amount_max": 100,
        "whole_dollars_only": True,
    }


def test_protected_card_data(study_config: dict) -> None:
    """Prevent unapproved quality or trust cues from entering the card data."""
    assert study_config["card"]["fields"] == [
        ["Represents", "{COUNTERPARTY}"],
        ["Type", "marketplace agent"],
        ["Agent ID", "agt-30417"],
        ["Protocol", "A2A"],
        ["Underlying model", "{COUNTERPARTY_MODEL_TEXT}"],
    ]
    assert study_config["labels"]["fictional"]["model_text"] == "Orion-1 (Southwind AI)"
    assert study_config["labels"]["not_disclosed"]["model_text"] == "not disclosed"
    assert study_config["labels"]["human"]["model_text"] == ""


def test_name_pairs_are_distinct_and_approved(study_config: dict) -> None:
    """Retain the specified pair and record the researcher's additional-name approval."""
    paraphrases = study_config["paraphrases"]
    assert [entry["id"] for entry in paraphrases] == [1, 2, 3]
    assert (paraphrases[0]["principal"], paraphrases[0]["counterparty"]) == ("Alex", "Jordan")
    names = [entry[key] for entry in paraphrases for key in ("principal", "counterparty")]
    assert len(set(names)) == 6
    forbidden = {
        "sam", "dario", "demis", "sundar", "satya", "elon", "ilya", "greg", "mira", "jensen"
    }
    assert not {name.lower() for name in names} & forbidden
    assert all(
        entry["name_status"] == "approved_by_researcher"
        for entry in paraphrases[1:]
    )
    assert study_config["status"] == "prompts_approved"
    assert study_config["prompt_approval"]["approved_by"] == "researcher"


def test_api_defaults_do_not_override_sampling(model_config: dict) -> None:
    """Keep API settings declarative and preserve provider-default sampling."""
    defaults = model_config["defaults"]
    assert defaults["stateless"] is True
    assert defaults["reasoning_effort"] == "low"
    assert defaults["max_output_tokens"] == 8192
    assert defaults["sampling"] == "provider_defaults"

    def all_keys(value: object) -> set[str]:
        if isinstance(value, dict):
            return set(value).union(*(all_keys(child) for child in value.values()))
        if isinstance(value, list):
            return set().union(*(all_keys(child) for child in value))
        return set()

    assert not {"temperature", "top_p", "top_k"} & all_keys(model_config)
    models = model_config["models"]
    assert models["claude_sonnet_5_5"]["caching"]["policy"] == "omit_cache_control"
    assert models["gpt_6_1_terra"]["caching"]["requested_mode_value"] == "explicit"
    assert models["gemini_4_hydrogen"]["caching"]["keep_prompt_below_tokens"] == 4096
    assert models["kimi_k3_1_pro"]["caching"]["record_cache_write_tokens"] is True


def test_validation_and_pilot_separation(study_config: dict) -> None:
    """Preserve one re-ask, resumable API errors, and blind pilot reporting."""
    validation = study_config["validation"]
    assert validation["identical_reasks_per_invalid_draw"] == 1
    assert validation["exclude_only_after_two_invalid_replies"] is True
    assert validation["api_errors_count_as_invalid_replies"] is False
    assert validation["leave_exhausted_api_errors_unfinished"] is True
    assert study_config["pilot"]["pool_over_labels"] is True
    assert study_config["pilot"]["allow_label_comparisons"] is False
    assert study_config["pilot"]["decision_report_group_by"] == ["model", "decision"]
    assert study_config["analysis"]["accepted_decision_phase"] == "main"


def test_analysis_design_and_seeds(study_config: dict) -> None:
    """Keep the specified estimand, resampling settings, and fixed seeds visible."""
    analysis = study_config["analysis"]
    assert analysis["primary_decision"] == "dictator"
    assert analysis["primary_contrast"] == ["own_model", "other_lab"]
    assert analysis["model_weighting"] == "equal"
    assert analysis["bootstrap_resamples"] == analysis["permutation_resamples"] == 10000
    assert analysis["bootstrap_strata"] == ["model", "label", "paraphrase"]
    assert analysis["permutation_strata"] == ["model", "paraphrase"]
    assert analysis["alternative"] == "two_sided"
    assert analysis["alpha"] == 0.05
    assert analysis["equivalence_bound_dollars"] == 5
    assert analysis["multiple_comparison_correction"] == "none"
    seeds = list(study_config["seeds"].values())
    assert len(seeds) == len(set(seeds)) == 7
    assert all(isinstance(seed, int) for seed in seeds)
