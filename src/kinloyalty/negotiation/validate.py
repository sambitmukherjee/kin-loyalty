"""Validate negotiation replies with the approved non-offer-price exception."""

import json
import math
from dataclasses import dataclass
from typing import Any

from kinloyalty.clients.base import ModelResponse
from kinloyalty.negotiation import Role
from kinloyalty.negotiation.rules import allowed_actions
from kinloyalty.negotiation.transcript import TranscriptTurn, other_role


@dataclass(frozen=True)
class ReplyValidation:
    """Retain original parsed content separately from a valid, renderable public turn."""

    valid: bool
    parsed_json: dict[str, Any] | None
    invalid_reason: str | None
    turn: TranscriptTurn | None = None


def _without_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate_json_key")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise ValueError("non_finite_json_number")


def _finite_float(value: str) -> float:
    result = float(value)
    if not math.isfinite(result):
        raise ValueError("non_finite_json_number")
    return result


def validate_response(
    response: ModelResponse, *, role: Role, message_number: int, message_limit: int = 12,
) -> ReplyValidation:
    """Reject malformed, truncated, or forbidden actions; preserve ignored raw prices."""
    actions = allowed_actions(message_number, message_limit)
    other_role(role)
    finish = (response.finish_reason or "").lower()
    if response.output_truncated or finish in {"length", "max_tokens", "max_output_tokens"}:
        return ReplyValidation(False, None, "output_truncated")
    try:
        parsed = json.loads(
            response.output_text, object_pairs_hook=_without_duplicates,
            parse_constant=_reject_constant, parse_float=_finite_float,
        )
    except (ValueError, TypeError, RecursionError):
        return ReplyValidation(False, None, "invalid_json")
    if not isinstance(parsed, dict):
        return ReplyValidation(False, None, "schema_not_object")
    if set(parsed) != {"message", "action", "price"}:
        return ReplyValidation(False, parsed, "schema_fields_mismatch")
    if not isinstance(parsed["message"], str):
        return ReplyValidation(False, parsed, "schema_type:message")
    if not isinstance(parsed["action"], str) or parsed["action"] not in actions:
        return ReplyValidation(False, parsed, "schema_enum:action")
    try:
        turn = TranscriptTurn(role, parsed["message"], parsed["action"], parsed["price"])
    except ValueError:
        return ReplyValidation(False, parsed, "invalid_offer_price")
    return ReplyValidation(True, parsed, None, turn)
