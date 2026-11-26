"""Verify paired scenario facts, reproducible streams, and balanced card labels."""

from collections import Counter
from copy import deepcopy
from dataclasses import replace
from decimal import Decimal
from pathlib import Path

import pytest

from kinloyalty.negotiation.cards import seller_disclosure
from kinloyalty.negotiation.config import load_config
from kinloyalty.negotiation.scenarios import (
    draw_balanced_scenarios, ordered_pairs, round_price, swapped_self_names,
)


ROOT = Path(__file__).resolve().parents[1]


def test_full_design_balance_with_synthetic_seed_only() -> None:
    config = load_config(ROOT / "configs/study2.yaml")
    pairs = ordered_pairs(config)
    assert len(pairs) == 16 and sum(buyer == seller for buyer, seller in pairs) == 4
    episode_counts = Counter()
    card_counts = Counter()
    shortfalls = []
    scenario_ids = set()
    for buyer, seller in pairs:
        scenarios = draw_balanced_scenarios(
            config, buyer_model=buyer, seller_model=seller, seed=101, batch_id="synthetic",
        )
        assert len(scenarios) == 20
        assert Counter(s.opener for s in scenarios) == {"buyer": 10, "seller": 10}
        assert Counter(s.item for s in scenarios) == {item["name"]: 4 for item in config.study["items"]}
        assert set(Counter((s.item, s.opener) for s in scenarios).values()) == {2}
        schedule = swapped_self_names(config, buyer_model=buyer, count=20, seed=102) if buyer == seller else None
        if schedule:
            counts = Counter(schedule)
            assert sorted(counts.values()) == [6, 7, 7]
            assert buyer not in counts
            next_model = config.model_order[(config.model_order.index(buyer) + 1) % 4]
            assert counts[next_model] == 6
            shortfalls.append(next_model)
        seen_by_condition = {}
        for condition in config.study["conditions"]:
            seen_by_condition[condition] = scenarios
            for index, scenario in enumerate(scenarios):
                disclosure = seller_disclosure(
                    config, buyer_model=buyer, seller_model=seller, condition=condition,
                    swapped_model=schedule[index] if schedule and condition == "swapped" else None,
                )
                episode_counts[(buyer, seller, condition)] += 1
                card_counts[disclosure.card_says] += 1
                assert scenario.seller_min % 5 == scenario.buyer_max % 5 == 0
                assert .75 * scenario.reference_price - 2.5 <= scenario.seller_min <= .85 * scenario.reference_price + 2.5
                assert 1.15 * scenario.reference_price - 2.5 <= scenario.buyer_max <= 1.25 * scenario.reference_price + 2.5
                assert scenario.buyer_max > scenario.seller_min
        assert seen_by_condition["true"] is seen_by_condition["swapped"] is seen_by_condition["not_disclosed"]
        scenario_ids.update(s.scenario_id for s in scenarios)
    assert len(scenario_ids) == 320
    assert sum(episode_counts.values()) == 960 and set(episode_counts.values()) == {20}
    assert card_counts == {"none": 320, "same": 320, "other": 320}
    assert set(shortfalls) == set(config.model_order)


def test_pair_streams_repeat_and_do_not_depend_on_call_order() -> None:
    config = load_config(ROOT / "configs/study2.yaml")
    pairs = ordered_pairs(config)
    def draw(pair: tuple[str, str], seed: int = 17, batch: str = "synthetic") -> tuple:
        return draw_balanced_scenarios(
            config, buyer_model=pair[0], seller_model=pair[1], seed=seed, batch_id=batch,
        )
    forward = {pair: draw(pair) for pair in pairs}
    reverse = {pair: draw(pair) for pair in reversed(pairs)}
    assert forward == reverse
    facts = lambda scenarios: [(s.seller_min, s.buyer_max) for s in scenarios]
    assert facts(draw(pairs[0])) != facts(draw(pairs[1]))
    assert facts(draw(pairs[0])) != facts(draw(pairs[0], seed=18, batch="separate-pilot-test"))
    assert {s.scenario_id for s in draw(pairs[0])}.isdisjoint(
        s.scenario_id for s in draw(pairs[0], seed=18, batch="separate-pilot-test")
    )
    first = swapped_self_names(config, buyer_model=pairs[0][0], count=20, seed=19)
    assert first == swapped_self_names(config, buyer_model=pairs[0][0], count=20, seed=19)
    assert first != swapped_self_names(config, buyer_model=pairs[0][0], count=20, seed=20)


@pytest.mark.parametrize("amount, expected", [
    ("397.49", 395), ("397.5", 400), ("402.49", 400), ("402.5", 405),
    ("400", 400), ("0", 0),
])
def test_nearest_five_and_exact_half_steps(amount: str, expected: int) -> None:
    assert round_price(Decimal(amount)) == expected


@pytest.mark.parametrize("amount, increment", [(float("inf"), 5), (-1, 5), (1, 0), (1, True)])
def test_bad_rounding_inputs_fail(amount: float, increment: int) -> None:
    with pytest.raises(ValueError):
        round_price(amount, increment)


def test_scenario_parameters_are_configurable() -> None:
    config = load_config(ROOT / "configs/study2.yaml")
    study = deepcopy(config.study)
    study["items"] = [{"name": "monitor", "reference_price": 200}]
    study["limits"] = {"seller_multiplier": [.5, .6], "buyer_multiplier": [1.3, 1.4],
                       "rounding_increment": 10, "rounding": "half_up"}
    study["scenario_design"]["replicates_per_item_opener"] = {"buyer": 1, "seller": 3}
    custom = replace(config, study=study)
    scenarios = draw_balanced_scenarios(
        custom, buyer_model=config.model_order[0], seller_model=config.model_order[1],
        seed=21, batch_id="custom-synthetic",
    )
    assert len(scenarios) == 4 and {s.item for s in scenarios} == {"monitor"}
    assert Counter(s.opener for s in scenarios) == {"buyer": 1, "seller": 3}
    assert all(s.seller_min % 10 == s.buyer_max % 10 == 0 for s in scenarios)
    assert all(100 <= s.seller_min <= 120 and 260 <= s.buyer_max <= 280 for s in scenarios)


def test_disclosure_relationships_and_explicit_self_alternative() -> None:
    config = load_config(ROOT / "configs/study2.yaml")
    a, b, *_ = config.model_order
    expected = {
        (a, a, "not_disclosed"): ("none", None), (a, b, "not_disclosed"): ("none", None),
        (a, a, "true"): ("same", a), (a, b, "true"): ("other", b),
        (a, a, "swapped"): ("other", b), (a, b, "swapped"): ("same", a),
    }
    for (buyer, seller, condition), result in expected.items():
        disclosure = seller_disclosure(
            config, buyer_model=buyer, seller_model=seller, condition=condition,
            swapped_model=b if buyer == seller and condition == "swapped" else None,
        )
        assert (disclosure.card_says, disclosure.model_key) == result
        if result[1] is None:
            assert disclosure.model_text == "not disclosed"
        else:
            model = config.models[result[1]]
            assert disclosure.model_text == f"{model['display_name']} ({model['lab']})"
    for condition, seller, alternative in [("swapped", a, None), ("swapped", a, a), ("true", a, b), ("swapped", b, b)]:
        with pytest.raises(ValueError):
            seller_disclosure(config, buyer_model=a, seller_model=seller,
                              condition=condition, swapped_model=alternative)
