"""Check strict reply parsing, turn schemas, and the explicit ignored-price exception."""

import json

import pytest

from kinloyalty.clients.base import ModelResponse
from kinloyalty.negotiation.schemas import response_schema
from kinloyalty.negotiation.validate import validate_response


@pytest.mark.parametrize("number", range(1, 13))
def test_schema_and_validator_agree_on_turn_actions(number: int) -> None:
    schema = response_schema(number)
    expected = ["offer", "walk_away"] if number == 1 else (
        ["accept", "walk_away"] if number == 12 else ["offer", "accept", "walk_away"]
    )
    assert schema == {
        "type": "object", "properties": {
            "message": {"type": "string"}, "action": {"type": "string", "enum": expected},
            "price": {"type": ["integer", "null"], "minimum": 1},
        }, "required": ["message", "action", "price"], "additionalProperties": False,
    }
    for action in ("offer", "accept", "walk_away", "decline"):
        response = ModelResponse(json.dumps({"message": "Reply", "action": action, "price": 501 if action == "offer" else None}))
        assert validate_response(response, role="buyer", message_number=number).valid == (action in expected)
    schema["properties"]["action"]["enum"].append("bad")
    assert "bad" not in response_schema(number)["properties"]["action"]["enum"]


@pytest.mark.parametrize("raw", [
    "not JSON", "```json\n{}\n```", "[]", "null", "{}",
    '{"message":"A","message":"B","action":"offer","price":500}',
    '{"message":"A","action":"accept","price":NaN}',
    '{"message":"A","action":"accept","price":1e400}',
    '{"message":"A","action":"accept","price":{"nested":Infinity}}',
    '{"message":"A","action":"offer","price":500,"extra":1}',
    '{"message":true,"action":"offer","price":500}',
    '{"message":"A","action":[],"price":500}',
])
def test_invalid_json_and_schema_fields(raw: str) -> None:
    assert not validate_response(ModelResponse(raw), role="buyer", message_number=2).valid


@pytest.mark.parametrize("price, valid", [
    (500, True), (500.0, True), (1, True), (True, False), (False, False),
    (0, False), (-1, False), (None, False), (1.5, False), ("500", False), ({}, False),
])
def test_positive_whole_dollar_offer_semantics(price: object, valid: bool) -> None:
    response = ModelResponse(json.dumps({"message": "Offer", "action": "offer", "price": price}))
    assert validate_response(response, role="buyer", message_number=2).valid is valid


@pytest.mark.parametrize("action", ["accept", "walk_away"])
@pytest.mark.parametrize("price", [None, 0, -500, 12.5, "ignored", True, {"any": [1, 2]}])
def test_nonoffer_price_exception_preserves_raw_value(action: str, price: object) -> None:
    response = ModelResponse(json.dumps({"message": "Reply", "action": action, "price": price}))
    result = validate_response(response, role="seller", message_number=12)
    assert result.valid
    assert result.parsed_json["price"] == price
    assert result.turn.price == price


@pytest.mark.parametrize("finish", ["length", "max_tokens", "MAX_TOKENS", "max_output_tokens"])
def test_output_cap_invalidates_even_complete_json(finish: str) -> None:
    response = ModelResponse('{"message":"Offer","action":"offer","price":500}', finish_reason=finish)
    assert validate_response(response, role="buyer", message_number=1).invalid_reason == "output_truncated"
    flagged = ModelResponse(response.output_text, finish_reason="stop", output_truncated=True)
    assert not validate_response(flagged, role="buyer", message_number=1).valid
