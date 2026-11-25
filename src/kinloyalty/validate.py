"""Validate strict JSON against the flat response-schema subset used by the study."""

import json
import math
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from kinloyalty.clients.base import ModelResponse


@dataclass(frozen=True)
class ValidationResult:
    """Distinguish a parsed reply from a valid, non-truncated response."""

    valid: bool
    parsed_json: dict[str, Any] | None
    invalid_reason: str | None = None


def check_schema(schema: Mapping[str, Any]) -> None:
    """Reject unsupported schema features as configuration errors before calling."""
    if set(schema) - {"type", "properties", "required", "additionalProperties", "description"}:
        raise ValueError("Unsupported response-schema keyword.")
    if schema.get("type") != "object" or schema.get("additionalProperties") is not False:
        raise ValueError("Response schema must describe an object without extra fields.")
    properties = schema.get("properties")
    if not isinstance(properties, dict) or set(schema.get("required", [])) != set(properties):
        raise ValueError("Every response field must be required.")
    for value in properties.values():
        if set(value) - {"type", "enum", "minimum", "maximum", "description"}:
            raise ValueError("Unsupported response-field keyword.")
        if value.get("type") not in {"integer", "string"}:
            raise ValueError("Only flat integer/string response fields are supported.")


def _object_without_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate_json_key")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise ValueError("non_finite_json_number")


def validate_response(response: ModelResponse, schema: Mapping[str, Any]) -> ValidationResult:
    """Apply JSON/schema/range checks; truncation is invalid even for parseable JSON.

    JSON Schema defines integers mathematically, so 1.0 is a whole number, while
    true, fractional numbers, strings, and non-finite numbers are not integers.
    Field order and sentence count are instructions, not extra exclusion rules.
    """
    check_schema(schema)
    finish = (response.finish_reason or "").lower()
    if response.output_truncated or finish in {"length", "max_tokens", "max_output_tokens"}:
        return ValidationResult(False, None, "output_truncated")
    try:
        parsed = json.loads(
            response.output_text, object_pairs_hook=_object_without_duplicates,
            parse_constant=_reject_constant,
        )
    except (ValueError, TypeError, RecursionError):
        return ValidationResult(False, None, "invalid_json")
    if not isinstance(parsed, dict):
        return ValidationResult(False, None, "schema_not_object")
    if set(parsed) != set(schema["properties"]):
        return ValidationResult(False, parsed, "schema_fields_mismatch")
    for name, spec in schema["properties"].items():
        value = parsed[name]
        if spec["type"] == "integer":
            whole = type(value) is int or (
                type(value) is float and math.isfinite(value) and value.is_integer()
            )
            if not whole:
                return ValidationResult(False, parsed, f"schema_type:{name}")
            if value < spec.get("minimum", -math.inf) or value > spec.get("maximum", math.inf):
                return ValidationResult(False, parsed, f"schema_range:{name}")
        elif not isinstance(value, str):
            return ValidationResult(False, parsed, f"schema_type:{name}")
        if "enum" in spec and value not in spec["enum"]:
            return ValidationResult(False, parsed, f"schema_enum:{name}")
    return ValidationResult(True, parsed)
