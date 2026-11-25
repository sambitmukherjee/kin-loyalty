"""Exercise JSON/schema/range/truncation rules without changing the approved contract."""

from copy import deepcopy
from pathlib import Path

import pytest

from kinloyalty.clients.base import ModelResponse
from kinloyalty.prompts import load_prompt_library
from kinloyalty.schemas import response_schema
from kinloyalty.validate import check_schema, validate_response


ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def schema() -> dict:
    """Return the canonical bounded dictator schema."""
    return response_schema("dictator", load_prompt_library(ROOT / "configs/study1.yaml").study)


@pytest.mark.parametrize("text,valid", [
    ('{"amount_to_counterparty":0,"reason":"A sentence."}', True),
    ('{"amount_to_counterparty":100,"reason":"A sentence."}', True),
    ('{"reason":"A sentence.","amount_to_counterparty":20}', True),
    ('{"amount_to_counterparty":1.0,"reason":"A sentence."}', True),
    ('{"amount_to_counterparty":1e1,"reason":"A sentence."}', True),
    ('{"amount_to_counterparty":20,"reason":""}', True),
    ('{"amount_to_counterparty":-1,"reason":"A sentence."}', False),
    ('{"amount_to_counterparty":101,"reason":"A sentence."}', False),
    ('{"amount_to_counterparty":true,"reason":"A sentence."}', False),
    ('{"amount_to_counterparty":1.5,"reason":"A sentence."}', False),
    ('{"amount_to_counterparty":"20","reason":"A sentence."}', False),
    ('{"amount_to_counterparty":20,"reason":null}', False),
    ('{"amount_to_counterparty":20}', False),
    ('{"amount_to_counterparty":20,"reason":"A sentence.","extra":1}', False),
    ('{"amount_to_counterparty":1,"amount_to_counterparty":20,"reason":"A sentence."}', False),
    ('{"amount_to_counterparty":NaN,"reason":"A sentence."}', False),
    ('{"amount_to_counterparty":Infinity,"reason":"A sentence."}', False),
    ('{"amount_to_counterparty":1e999,"reason":"A sentence."}', False),
    ('[]', False), ('null', False), ('not json', False),
    ('```json\n{"amount_to_counterparty":20,"reason":"A sentence."}\n```', False),
])
def test_strict_json_and_schema_contract(schema: dict, text: str, valid: bool) -> None:
    """Accept schema-valid whole dollars; reject booleans, fractions, extras, and invalid JSON."""
    assert validate_response(ModelResponse(text), schema).valid is valid


@pytest.mark.parametrize("finish,flag", [("length", False), ("max_tokens", False), ("MAX_TOKENS", False), ("stop", True)])
def test_parseable_but_truncated_json_is_invalid(schema: dict, finish: str, flag: bool) -> None:
    """Treat an output-cap stop as invalid regardless of successful JSON parsing."""
    response = ModelResponse('{"amount_to_counterparty":20,"reason":"A sentence."}', finish_reason=finish, output_truncated=flag)
    result = validate_response(response, schema)
    assert result.valid is False
    assert result.invalid_reason == "output_truncated"


@pytest.mark.parametrize("answer,valid", [("yes", True), ("no", True), ("unsure", True), ("Yes", False), ("maybe", False)])
def test_comprehension_enum(answer: str, valid: bool) -> None:
    """Keep the check separate and restrict answers exactly to its three strings."""
    study = load_prompt_library(ROOT / "configs/study1.yaml").study
    result = validate_response(ModelResponse('{"same_model":"' + answer + '"}'), response_schema("comprehension", study))
    assert result.valid is valid


def test_unsupported_schema_is_a_configuration_error(schema: dict) -> None:
    """Never silently ignore schema features or blame a model for a broken validator config."""
    unsupported = deepcopy(schema)
    unsupported["properties"]["reason"]["minLength"] = 1
    with pytest.raises(ValueError, match="Unsupported"):
        check_schema(unsupported)
