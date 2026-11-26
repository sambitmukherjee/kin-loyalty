"""Render role-relative transcript lines with JSON-escaped free text."""

import json
import math
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Literal

from kinloyalty.negotiation import Role


@dataclass(frozen=True)
class TranscriptTurn:
    """Hold public reply content, retaining supplied prices on terminal actions."""

    role: Role
    message: str
    action: Literal["offer", "accept", "walk_away"]
    price: object = None

    def __post_init__(self) -> None:
        """Require renderable content; full reply/state validation belongs to the engine."""
        if self.role not in {"buyer", "seller"} or not isinstance(self.message, str):
            raise ValueError("Transcript turns require a known role and string message.")
        if self.action not in {"offer", "accept", "walk_away"}:
            raise ValueError("Unknown transcript action.")
        if self.action == "offer":
            whole = type(self.price) is int or (
                type(self.price) is float and math.isfinite(self.price) and self.price.is_integer()
            )
            if not whole or self.price <= 0:
                raise ValueError("An offer needs a positive whole-dollar price.")


def other_role(role: Role) -> Role:
    """Return the counterparty role, rejecting misspellings before rendering."""
    if role not in {"buyer", "seller"}:
        raise ValueError("Unknown participant role.")
    return "seller" if role == "buyer" else "buyer"


def render_transcript(turns: Sequence[TranscriptTurn], *, mover: Role) -> str:
    """Keep every earlier message on one line from the mover's point of view.

    Escape Unicode line separators too, so arbitrary message text cannot create
    an apparent extra transcript line. Prices on terminal actions are omitted.
    """
    counterparty = other_role(mover)
    lines = []
    for turn in turns:
        label = "You" if turn.role == mover else f"{counterparty.capitalize()}'s agent"
        line = f"[{label}] message: {json.dumps(turn.message)} | action: {turn.action}"
        if turn.action == "offer":
            line += f" | price: ${int(turn.price)}"
        lines.append(line)
    return "\n".join(lines)
