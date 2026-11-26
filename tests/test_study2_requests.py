"""Verify dynamic negotiation schemas through unchanged SDK adapters in memory."""

import asyncio
import json
from pathlib import Path

import anthropic
import httpx2
import openai
import pytest
from google import genai
from google.genai import types

from kinloyalty.clients.anthropic import AnthropicClient
from kinloyalty.clients.google import GoogleClient
from kinloyalty.clients.moonshot import MoonshotClient
from kinloyalty.clients.openai import OpenAIClient
from kinloyalty.negotiation.config import load_config
from kinloyalty.negotiation.requests import build_turn_request
from kinloyalty.negotiation.review import load_fixed_positions
from kinloyalty.negotiation.rules import apply_turn
from kinloyalty.negotiation.schemas import response_schema
from kinloyalty.negotiation.state import EpisodeSpec, EpisodeState
from kinloyalty.negotiation.validate import validate_response


ROOT = Path(__file__).resolve().parents[1]
FAKE_KEY = "fake-key-only-for-offline-transports"


def _adapter(provider, transport):
    http = httpx2.AsyncClient(transport=transport)
    if provider == "anthropic":
        return AnthropicClient(sdk=anthropic.AsyncAnthropic(api_key=FAKE_KEY, max_retries=0, http_client=http))
    if provider == "google":
        return GoogleClient(sdk=genai.Client(api_key=FAKE_KEY, vertexai=False, enterprise=False, http_options=types.HttpOptions(
            base_url="https://generativelanguage.googleapis.com", api_version="v1beta",
            httpx_async_client=http, retry_options=types.HttpRetryOptions(attempts=1),
        )))
    cls = OpenAIClient if provider == "openai" else MoonshotClient
    return cls(sdk=openai.AsyncOpenAI(api_key=FAKE_KEY, base_url=cls.base_url, max_retries=0, http_client=http))


def _body(provider, request):
    text = '{"message":"Offline fixture.","action":"walk_away","price":null}'
    if provider == "anthropic":
        return {"model": request.api_model_id, "content": [{"type": "text", "text": text}],
                "stop_reason": "end_turn", "usage": {"input_tokens": 100, "output_tokens": 20}}
    if provider == "google":
        return {"modelVersion": request.api_model_id,
                "candidates": [{"content": {"role": "model", "parts": [{"text": text}]}, "finishReason": "STOP"}],
                "usageMetadata": {"promptTokenCount": 100, "candidatesTokenCount": 20, "thoughtsTokenCount": 5}}
    return {"model": request.api_model_id,
            "choices": [{"message": {"role": "assistant", "content": text}, "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 100, "completion_tokens": 20}}


@pytest.mark.parametrize("provider", ["anthropic", "openai", "google", "moonshot"])
@pytest.mark.parametrize("role", ["buyer", "seller"])
def test_dynamic_schemas_and_stateless_sdk_wire_format(provider: str, role: str) -> None:
    config = load_config(ROOT / "configs/study2.yaml")
    model = next(key for key, value in config.models.items() if value["provider"] == provider)
    positions = load_fixed_positions(config)
    seen = []
    current = None
    async def handler(http_request):
        wire = json.loads(http_request.content)
        seen.append(wire)
        return httpx2.Response(200, json=_body(provider, current))
    async def run():
        nonlocal current
        adapter = _adapter(provider, httpx2.MockTransport(handler))
        try:
            for number in (1, 11, 12):
                scenario, prefix = positions.position(config, buyer_model=model, seller_model=model,
                                                       role=role, message_number=number)
                state = EpisodeState(scenario)
                for turn in prefix:
                    state = apply_turn(state, turn)
                spec = EpisodeSpec("offline-wire", model, model, "not_disclosed", scenario)
                current = build_turn_request(config, spec, state)
                response = await adapter.complete(current)
                assert validate_response(response, role=role, message_number=number).valid
                assert current.json_schema == response_schema(number)
                assert current.context["own_limit"] == (600 if role == "buyer" else 400)
                assert "$400" not in current.system_prompt if role == "buyer" else "$600" not in current.system_prompt
                wire = seen[-1]
                if provider == "google":
                    assert wire["contents"] == [{"role": "user", "parts": [{"text": current.user_message}]}]
                    submitted = wire["generationConfig"]["responseJsonSchema"]
                else:
                    messages = wire["messages"]
                    assert all(message["role"] in {"system", "user"} for message in messages)
                    assert messages[-1]["content"] == current.user_message
                    submitted = wire["output_config"]["format"]["schema"] if provider == "anthropic" else wire["response_format"]["json_schema"]["schema"]
                assert submitted["properties"]["action"]["enum"] == response_schema(number)["properties"]["action"]["enum"]
                assert submitted["properties"]["price"]["type"] == ["integer", "null"]
                assert ("minimum" in submitted["properties"]["price"]) == (provider != "anthropic")
                assert "own_limit" not in json.dumps(wire) and "card_says" not in json.dumps(wire)
                assert "context" not in wire and "trial_id" not in wire
        finally:
            await adapter.aclose()
    asyncio.run(run())
    assert len(seen) == 3


def test_reusable_optional_cards_are_explicit_in_local_metadata() -> None:
    config = load_config(ROOT / "configs/study2.yaml")
    buyer, seller, *_ = config.model_order
    scenario, _ = load_fixed_positions(config).position(config, buyer_model=buyer, seller_model=seller,
                                                        role="seller", message_number=1)
    spec = EpisodeSpec("custom-cards", buyer, seller, "not_disclosed", scenario,
                       custom_cards=(None, "  Underlying model: not disclosed"))
    request = build_turn_request(config, spec, EpisodeState(scenario))
    assert "Here is that agent's card:\n  Underlying model: not disclosed" in request.system_prompt
    assert request.context["custom_cards"] is True
    assert request.context["card_says"] == "none"
