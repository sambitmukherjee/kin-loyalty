"""Build fresh, condition-independent JSON response schemas from study configuration."""

from collections.abc import Mapping
from typing import Any


def response_schema(
    decision: str, study: Mapping[str, Any], *, include_numeric_bounds: bool = True
) -> dict[str, Any]:
    """Return an ordered schema with all fields required and no additional fields.

    Numeric bounds belong to the canonical local contract. A provider adapter may
    omit them only after its documentation review establishes that they are not
    supported; local response validation must still enforce the configured range.
    """
    properties: dict[str, Any] = {}
    if decision == "comprehension":
        properties["same_model"] = {
            "type": "string",
            "enum": list(study["comprehension"]["allowed_answers"]),
        }
    else:
        if decision not in study["decisions"]:
            raise ValueError(f"Unknown decision: {decision}")
        decision_config = study["decisions"][decision]
        fields = [decision_config["outcome"]]
        if "belief" in decision_config:
            fields.append(decision_config["belief"])
        for field in fields:
            properties[field] = {"type": "integer"}
            if include_numeric_bounds:
                properties[field].update(
                    minimum=study["game"]["amount_min"],
                    maximum=study["game"]["amount_max"],
                )
        properties["reason"] = {
            "type": "string",
            "description": "One sentence explaining the decision.",
        }
    return {
        "type": "object",
        "properties": properties,
        "required": list(properties),
        "additionalProperties": False,
    }
