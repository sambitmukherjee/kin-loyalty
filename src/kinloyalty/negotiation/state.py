"""Define immutable negotiation state independently of rendering and model clients."""

from dataclasses import dataclass
from typing import Literal

from kinloyalty.negotiation import Role
from kinloyalty.negotiation.scenarios import Scenario
from kinloyalty.negotiation.transcript import TranscriptTurn


OutcomeKind = Literal["deal", "walk_away_impasse", "final_message_impasse", "excluded"]


@dataclass(frozen=True)
class EpisodeSpec:
    """Bind a scenario to real participants and a disclosure assignment."""

    episode_id: str
    buyer_model: str
    seller_model: str
    condition: str
    scenario: Scenario
    swapped_model: str | None = None
    phase: str = "synthetic"
    # Optional complete cards support engine reuse; Study 2 leaves this unset.
    custom_cards: tuple[str | None, str | None] | None = None


@dataclass(frozen=True)
class Outcome:
    """Describe one terminal outcome, keeping exclusions distinct from impasses."""

    kind: OutcomeKind
    deal_price: int | None = None
    accepted_by: Role | None = None
    accept_price_mismatch: bool = False
    excluded_role: Role | None = None
    exclusion_message_number: int | None = None


@dataclass(frozen=True)
class EpisodeState:
    """Keep committed valid messages and an optional, unique terminal outcome."""

    scenario: Scenario
    message_limit: int = 12
    turns: tuple[TranscriptTurn, ...] = ()
    outcome: Outcome | None = None

    @property
    def final(self) -> bool:
        """Report whether the episode has a terminal outcome."""
        return self.outcome is not None


@dataclass(frozen=True)
class Score:
    """Hold surplus and mandate flags; exclusions have no scored outcome."""

    buyer_surplus_share: float | None
    buyer_mandate_violation: bool | None
    seller_mandate_violation: bool | None
