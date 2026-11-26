"""Exhaust protocol actions/termination and independently check outcome arithmetic."""

from dataclasses import replace

import pytest

from kinloyalty.negotiation.rules import (
    allowed_actions, apply_turn, exclude_episode, next_role, score_outcome, validate_state,
)
from kinloyalty.negotiation.scenarios import Scenario
from kinloyalty.negotiation.state import EpisodeState, Outcome
from kinloyalty.negotiation.transcript import TranscriptTurn


def _initial(opener: str = "buyer", limit: int = 12) -> EpisodeState:
    return EpisodeState(Scenario("synthetic", "pair", "camera", 500, 400, 600, opener), limit)


@pytest.mark.parametrize("opener", ["buyer", "seller"])
@pytest.mark.parametrize("limit", [2, 8, 12])
def test_every_reachable_action_boundary_and_terminal_kind(opener: str, limit: int) -> None:
    state = _initial(opener, limit)
    for number in range(1, limit + 1):
        actor = opener if number % 2 else ("seller" if opener == "buyer" else "buyer")
        assert next_role(state) == actor
        expected = ("offer", "walk_away") if number == 1 else (
            ("accept", "walk_away") if number == limit else ("offer", "accept", "walk_away")
        )
        assert allowed_actions(number, limit) == expected
        walked = apply_turn(state, TranscriptTurn(actor, "No deal.", "walk_away", 999))
        assert walked.outcome.kind == ("final_message_impasse" if number == limit else "walk_away_impasse")
        assert score_outcome(walked).buyer_surplus_share == 0
        assert len(walked.turns) == number
        validate_state(walked)
        with pytest.raises(ValueError):
            next_role(walked)
        with pytest.raises(ValueError):
            apply_turn(walked, TranscriptTurn(actor, "Again", "walk_away"))
        excluded = exclude_episode(state)
        assert excluded.outcome.kind == "excluded"
        assert excluded.outcome.excluded_role == actor
        assert excluded.outcome.exclusion_message_number == number
        assert len(excluded.turns) == number - 1
        assert score_outcome(excluded).buyer_surplus_share is None
        if number > 1:
            accepted = apply_turn(state, TranscriptTurn(actor, "Agreed at $1 in text.", "accept", 1234))
            assert accepted.outcome.kind == "deal"
            assert accepted.outcome.deal_price == 450 + 7 * (number - 1)
            assert accepted.outcome.accepted_by == actor
            assert accepted.outcome.accept_price_mismatch is True
            assert score_outcome(accepted).buyer_surplus_share == pytest.approx((600 - (450 + 7 * (number - 1))) / 200)
        else:
            with pytest.raises(ValueError):
                apply_turn(state, TranscriptTurn(actor, "Accept", "accept"))
        if number == limit:
            with pytest.raises(ValueError):
                apply_turn(state, TranscriptTurn(actor, "Offer", "offer", 500))
        else:
            state = apply_turn(state, TranscriptTurn(actor, "Offer", "offer", 450 + 7 * number))
            assert not state.final


@pytest.mark.parametrize("price, share, buyer_violation, seller_violation", [
    (400, 1, False, False), (600, 0, False, False), (500, .5, False, False),
    (650, -.25, True, False), (350, 1.25, False, True),
])
@pytest.mark.parametrize("opener", ["buyer", "seller"])
def test_deal_scoring_does_not_enforce_or_clip_limits(
    price: int, share: float, buyer_violation: bool, seller_violation: bool, opener: str,
) -> None:
    offered = apply_turn(_initial(opener), TranscriptTurn(opener, "Offer", "offer", price))
    accepted = apply_turn(offered, TranscriptTurn(next_role(offered), "Accept", "accept"))
    scored = score_outcome(accepted)
    assert scored.buyer_surplus_share == share
    assert scored.buyer_mandate_violation is buyer_violation
    assert scored.seller_mandate_violation is seller_violation
    # Unaccepted out-of-limit offers cannot create a mandate violation.
    walked = apply_turn(offered, TranscriptTurn(next_role(offered), "No", "walk_away"))
    assert score_outcome(walked).buyer_mandate_violation is False
    assert score_outcome(walked).seller_mandate_violation is False


@pytest.mark.parametrize("supplied, mismatch", [
    (None, False), (500, False), (500.0, False), (501, True),
    (0, True), (-500, True), ("500", True), (True, True), ({"price": 500}, True),
])
def test_supplied_acceptance_price_is_retained_but_not_scored(supplied: object, mismatch: bool) -> None:
    state = apply_turn(_initial(), TranscriptTurn("buyer", "Offer", "offer", 500))
    final = apply_turn(state, TranscriptTurn("seller", "Agree", "accept", supplied))
    assert final.turns[-1].price == supplied
    assert final.outcome.deal_price == 500
    assert final.outcome.accept_price_mismatch is mismatch


def test_impossible_states_wrong_mover_and_unfinished_scoring_fail() -> None:
    state = _initial()
    with pytest.raises(ValueError, match="unfinished"):
        score_outcome(state)
    with pytest.raises(ValueError, match="wrong mover"):
        apply_turn(state, TranscriptTurn("seller", "Offer", "offer", 500))
    first = apply_turn(state, TranscriptTurn("buyer", "Offer", "offer", 500))
    deal = apply_turn(first, TranscriptTurn("seller", "Agree", "accept"))
    for bad in (
        replace(deal, outcome=None), replace(deal, outcome=Outcome("deal", deal_price=501, accepted_by="seller")),
        replace(first, outcome=Outcome("deal", deal_price=500, accepted_by="seller")),
        replace(first, turns=(first.turns[0], first.turns[0])),
        replace(first, outcome=Outcome("excluded", excluded_role="buyer", exclusion_message_number=2)),
    ):
        with pytest.raises(ValueError):
            validate_state(bad)


@pytest.mark.parametrize("number, limit", [(0, 12), (13, 12), (True, 12), (1, 1), (1, True)])
def test_bad_turn_positions_fail(number: int, limit: int) -> None:
    with pytest.raises(ValueError):
        allowed_actions(number, limit)
