"""Build turn-specific schemas while keeping action-dependent checks local."""

from typing import Any

from kinloyalty.negotiation.rules import allowed_actions


def response_schema(message_number: int, message_limit: int = 12) -> dict[str, Any]:
    """Allow only the turn's actions and a nullable whole-dollar price.

    A flat nullable price avoids provider-specific conditional-schema features.
    The prompt requests null on non-offers; the approved local exception ignores
    and records any supplied non-offer price. Offers require positive integers.
    """
    return {
        "type": "object",
        "properties": {
            "message": {"type": "string"},
            "action": {"type": "string", "enum": list(allowed_actions(message_number, message_limit))},
            "price": {"type": ["integer", "null"], "minimum": 1},
        },
        "required": ["message", "action", "price"],
        "additionalProperties": False,
    }
