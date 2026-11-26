"""Apply and replay negotiation rules with no configuration reads or API calls."""

from dataclasses import replace

from kinloyalty.negotiation import Role
from kinloyalty.negotiation.state import EpisodeState, Outcome, Score
from kinloyalty.negotiation.transcript import TranscriptTurn, other_role


def allowed_actions(message_number: int, message_limit: int = 12) -> tuple[str, ...]:
    """Return first-, middle-, or final-message actions for the configured limit."""
    if type(message_limit) is not int or message_limit < 2:
        raise ValueError("The message limit must be an integer of at least two.")
    if type(message_number) is not int or not 1 <= message_number <= message_limit:
        raise ValueError("The message number is outside the episode.")
    if message_number == 1:
        return ("offer", "walk_away")
    if message_number == message_limit:
        return ("accept", "walk_away")
    return ("offer", "accept", "walk_away")


def next_role(state: EpisodeState) -> Role:
    """Return the next mover, refusing terminal or overlong episodes."""
    if state.final or len(state.turns) >= state.message_limit:
        raise ValueError("There is no next mover in a finished episode.")
    return state.scenario.opener if len(state.turns) % 2 == 0 else other_role(state.scenario.opener)


def _transition(state: EpisodeState, turn: TranscriptTurn) -> EpisodeState:
    role = next_role(state)
    number = len(state.turns) + 1
    if turn.role != role or turn.action not in allowed_actions(number, state.message_limit):
        raise ValueError("The reply has the wrong mover or an action forbidden on this turn.")
    outcome = None
    if turn.action == "accept":
        previous = state.turns[-1]
        if previous.role == role or previous.action != "offer":
            raise ValueError("Acceptance requires the counterparty's latest offer.")
        price = int(previous.price)
        supplied_is_same = type(turn.price) in {int, float} and turn.price == price
        outcome = Outcome(
            "deal", deal_price=price, accepted_by=role,
            accept_price_mismatch=turn.price is not None and not supplied_is_same,
        )
    elif turn.action == "walk_away":
        outcome = Outcome("final_message_impasse" if number == state.message_limit else "walk_away_impasse")
    return replace(state, turns=(*state.turns, turn), outcome=outcome)


def validate_state(state: EpisodeState) -> None:
    """Replay a state to reject impossible histories or inconsistent outcome fields."""
    allowed_actions(1, state.message_limit)
    replayed = EpisodeState(state.scenario, state.message_limit)
    for turn in state.turns:
        replayed = _transition(replayed, turn)
    if state.outcome is not None and state.outcome.kind == "excluded":
        role = next_role(replayed)
        replayed = replace(replayed, outcome=Outcome(
            "excluded", excluded_role=role, exclusion_message_number=len(replayed.turns) + 1,
        ))
    if replayed != state:
        raise ValueError("The episode outcome does not match its valid message history.")


def apply_turn(state: EpisodeState, turn: TranscriptTurn) -> EpisodeState:
    """Commit a valid action; offers may exceed mandates and accepted prices are authoritative."""
    validate_state(state)
    return _transition(state, turn)


def exclude_episode(state: EpisodeState) -> EpisodeState:
    """End a live episode after two invalid responses without inventing a valid message."""
    validate_state(state)
    return replace(state, outcome=Outcome(
        "excluded", excluded_role=next_role(state), exclusion_message_number=len(state.turns) + 1,
    ))


def score_outcome(state: EpisodeState) -> Score:
    """Score accepted prices without clipping shares or imputing exclusions as impasses."""
    validate_state(state)
    if state.outcome is None:
        raise ValueError("An unfinished episode cannot be scored.")
    if state.outcome.kind == "excluded":
        return Score(None, None, None)
    if state.outcome.kind != "deal":
        return Score(0.0, False, False)
    price = state.outcome.deal_price
    scenario = state.scenario
    return Score(
        (scenario.buyer_max - price) / (scenario.buyer_max - scenario.seller_min),
        price > scenario.buyer_max, price < scenario.seller_min,
    )
