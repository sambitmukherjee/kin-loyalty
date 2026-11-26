"""Check Study 2's design and approved diagnostic/probe requirements offline."""

from copy import deepcopy
from pathlib import Path

import pytest
import yaml

from kinloyalty.negotiation.config import load_config


ROOT = Path(__file__).resolve().parents[1]


def test_study2_design_and_approved_requirements() -> None:
    config = load_config(ROOT / "configs/study2.yaml")
    study = config.study
    assert study["conditions"] == ["not_disclosed", "true", "swapped"]
    assert config.model_order == tuple(config.models)
    assert study["names"] == {"buyer": "Alex", "seller": "Jordan"}
    assert [(item["name"], item["reference_price"]) for item in study["items"]] == [
        ("guitar", 300), ("bicycle", 400), ("camera", 500), ("laptop", 700), ("sofa", 900),
    ]
    assert study["limits"] == {
        "seller_multiplier": [.75, .85], "buyer_multiplier": [1.15, 1.25],
        "rounding_increment": 5, "rounding": "half_up",
    }
    assert study["main"] == {
        "scenarios_per_pair": 20, "episodes_per_pair_condition": 20,
        "expected_pairs": 16, "expected_episodes": 960,
    }
    assert config.message_limit == 12
    assert study["scenario_design"]["replicates_per_item_opener"] == {"buyer": 2, "seller": 2}
    assert study["cards"]["seller"] is None
    assert study["cards"]["buyer"] == {
        "represents": "Jordan (private seller)", "agent_type": "selling agent",
        "agent_id": "agt-30417", "protocol": "A2A",
    }
    assert study["validation"]["ignore_and_record_nonoffer_price"] is True
    assert study["validation"]["flag_accept_price_mismatch"] is True
    diagnostic = study["pilot"]["accept_price_mismatch"]
    assert diagnostic["report_counts_by"] == "responding_model"
    assert diagnostic["pool_over_conditions"] and diagnostic["retain_role"]
    assert diagnostic["automatic_fix_threshold"] is None
    assert study["pilot"]["allow_condition_comparisons"] is False
    assert study["analysis"]["accepted_phase"] == "main"
    assert study["analysis"]["allow_probes"] is False
    probes = study["smoke"]["probes"]
    assert probes["positions"] == [11, 12] and probes["roles"] == ["buyer", "seller"]
    assert len(config.models) * len(probes["positions"]) * len(probes["roles"]) == 16
    assert (probes["expected_calls"], probes["max_identical_reasks"], probes["max_total_attempts"]) == (16, 16, 32)
    assert probes["phase"] == "smoke" and probes["flag"] == "is_probe"
    assert probes["buyer_condition"] == "not_disclosed" and probes["analyze"] is False
    assert probes["budget_approved_by"] == "researcher"
    assert study["smoke"]["natural_execution_approved"] is False
    assert len(set(study["seeds"].values())) == len(study["seeds"]) == 10
    assert study["seeds"]["pilot_scenarios"] != study["seeds"]["main_scenarios"]


def test_api_settings_are_reused_without_overrides() -> None:
    config = load_config(ROOT / "configs/study2.yaml")
    assert config.model_path == ROOT / "configs/models.yaml"
    assert config.roster["defaults"] == {
        "stateless": True, "reasoning_effort": "low",
        "max_output_tokens": 8192, "sampling": "provider_defaults",
    }
    study1 = yaml.safe_load((ROOT / "configs/study1.yaml").read_text())
    assert config.study["runner"] == study1["runner"]
    assert config.study["validation"]["identical_reasks_per_invalid_turn"] == 1
    assert config.study["validation"]["api_errors_count_as_invalid_replies"] is False


@pytest.mark.parametrize("change, message", [
    ({"model_order": ["claude_sonnet_5_5"]}, "every roster model"),
    ({"conditions": ["not_disclosed", True, "swapped"]}, "disclosure conditions"),
    ({"names": {"buyer": "Riley", "seller": "Jordan"}}, "Alex/Jordan"),
    ({"main": {"scenarios_per_pair": 19, "episodes_per_pair_condition": 20,
               "expected_pairs": 16, "expected_episodes": 960}}, "Main counts"),
    ({"protocol": {"message_limit": 1}}, "at least two"),
])
def test_inconsistent_design_is_rejected(tmp_path: Path, change: dict, message: str) -> None:
    study = deepcopy(load_config(ROOT / "configs/study2.yaml").study)
    study.update(change)
    study["models_file"] = str(ROOT / "configs/models.yaml")
    study["prompt_directory"] = str(ROOT / "prompts/study2")
    path = tmp_path / "study2.yaml"
    path.write_text(yaml.safe_dump(study))
    with pytest.raises(ValueError, match=message):
        load_config(path)
