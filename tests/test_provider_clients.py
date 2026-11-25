"""Exercise official SDK serialization on in-memory HTTP transports, never real endpoints."""

import asyncio
import json
from copy import deepcopy
from dataclasses import replace
from pathlib import Path

import anthropic
import httpx2
import openai
import pytest
from google import genai
from google.genai import types

from kinloyalty.clients.anthropic import AnthropicClient
from kinloyalty.clients.base import ClientError, ModelRequest
from kinloyalty.clients.factory import KEY_NAMES, create_provider_clients, load_api_keys
from kinloyalty.clients.google import GoogleClient
from kinloyalty.clients.moonshot import MoonshotClient
from kinloyalty.clients.openai import OpenAIClient
from kinloyalty.clients.payloads import build_api_payload, frozen_api_payload
from kinloyalty.clients.response_data import anthropic_response, chat_response, google_response
from kinloyalty.logs import read_jsonl
from kinloyalty.manifest import build_manifest, write_manifest
from kinloyalty.prompts import load_prompt_library, render_prompt
from kinloyalty.runner import RunnerPolicy, run_manifest
from kinloyalty.validate import validate_response


ROOT = Path(__file__).resolve().parents[1]
PROVIDERS = ("anthropic", "openai", "google", "moonshot")
FAKE_KEY = "fake-key-only-for-in-memory-tests"


@pytest.fixture(scope="module")
def requests() -> dict[str, ModelRequest]:
    """Freeze a smoke request per provider using the verified configuration."""
    return {trial["request"]["provider"]: ModelRequest(**trial["request"]) for trial in build_manifest(ROOT / "configs/study1.yaml", "smoke")}


def _body(provider: str, request: ModelRequest, *, truncated: bool = False) -> dict:
    values = {name: 40 if spec["type"] == "integer" else ("unsure" if "enum" in spec else "Fixture response.") for name, spec in request.json_schema["properties"].items()}
    text = json.dumps(values)
    if provider == "anthropic":
        return {
            "id": "msg_fixture", "model": request.api_model_id + "-fixture", "type": "message", "role": "assistant",
            "content": [{"type": "thinking", "thinking": "Fixture thinking.", "signature": "fixture"}, {"type": "text", "text": text}],
            "stop_reason": "max_tokens" if truncated else "end_turn",
            "usage": {"input_tokens": 110, "output_tokens": 35, "cache_read_input_tokens": 0, "cache_creation_input_tokens": 0, "output_tokens_details": {"thinking_tokens": 13}},
            "_fixture": True, "opaque_field": {"preserve": "unchanged"},
        }
    if provider == "google":
        return {
            "modelVersion": request.api_model_id + "-fixture",
            "candidates": [{"index": 0, "content": {"role": "model", "parts": [{"thought": True, "text": "Fixture thinking."}, {"text": text}]}, "finishReason": "MAX_TOKENS" if truncated else "STOP"}],
            "usageMetadata": {"promptTokenCount": 110, "candidatesTokenCount": 22, "thoughtsTokenCount": 13, "cachedContentTokenCount": 0, "totalTokenCount": 145},
            "_fixture": True, "opaque_field": {"preserve": "unchanged"},
        }
    return {
        "id": "chatcmpl-fixture", "object": "chat.completion", "created": 0, "model": request.api_model_id + "-fixture",
        "choices": [{"index": 0, "message": {"role": "assistant", "content": text, "reasoning_content": "Fixture thinking."}, "finish_reason": "length" if truncated else "stop"}],
        "usage": {"prompt_tokens": 110, "completion_tokens": 35, "total_tokens": 145, "completion_tokens_details": {"reasoning_tokens": 13}, "prompt_tokens_details": {"cached_tokens": 7 if provider == "moonshot" else 0, "cache_write_tokens": 8 if provider == "moonshot" else 0}},
        "_fixture": True, "opaque_field": {"preserve": "unchanged"},
    }


def _adapter(provider: str, transport: httpx2.MockTransport):
    http = httpx2.AsyncClient(transport=transport)
    if provider == "anthropic":
        sdk = anthropic.AsyncAnthropic(api_key=FAKE_KEY, base_url="https://api.anthropic.com", max_retries=0, http_client=http)
        return AnthropicClient(sdk=sdk)
    if provider == "google":
        sdk = genai.Client(api_key=FAKE_KEY, vertexai=False, enterprise=False, http_options=types.HttpOptions(
            api_version="v1beta", base_url="https://generativelanguage.googleapis.com",
            httpx_async_client=http, retry_options=types.HttpRetryOptions(attempts=1),
        ))
        return GoogleClient(sdk=sdk)
    cls = OpenAIClient if provider == "openai" else MoonshotClient
    sdk = openai.AsyncOpenAI(api_key=FAKE_KEY, base_url=cls.base_url, max_retries=0, http_client=http)
    return cls(sdk=sdk)


@pytest.mark.parametrize("provider", PROVIDERS)
@pytest.mark.parametrize("decision", ("dictator", "ultimatum_proposer", "ultimatum_responder", "comprehension"))
def test_official_sdk_wire_format_and_full_response(provider: str, decision: str, requests: dict) -> None:
    """Verify low effort, 8192 cap, strict schema, raw metadata, and no sampling overrides."""
    base = requests[provider]
    library = load_prompt_library(ROOT / "configs/study1.yaml")
    model = next(key for key, value in library.models.items() if value["provider"] == provider)
    rendered = render_prompt(library, model=model, decision=decision, label="not_disclosed", paraphrase=1)
    request = replace(base, trial_id=f"fixture:{provider}:{decision}", system_prompt=rendered.system_prompt, user_message=rendered.user_message, json_schema=rendered.json_schema)
    request = replace(request, api_payload=build_api_payload(request))
    body = _body(provider, request)
    seen = []

    async def handler(http_request):
        seen.append((http_request.url, json.loads(http_request.content)))
        return httpx2.Response(200, json=body)

    async def run():
        adapter = _adapter(provider, httpx2.MockTransport(handler))
        try:
            return await adapter.complete(request)
        finally:
            await adapter.aclose()

    response = asyncio.run(run())
    assert len(seen) == 1
    assert response.raw_response == body
    assert response.returned_model_version == request.api_model_id + "-fixture"
    assert response.reasoning_text == "Fixture thinking."
    assert response.usage.reasoning_tokens == 13
    assert response.usage.input_tokens == 110
    assert response.usage.cache_read_tokens == (7 if provider == "moonshot" else 0)
    assert response.usage.cache_write_tokens == (None if provider == "google" else 8 if provider == "moonshot" else 0)
    assert validate_response(response, request.json_schema).valid
    url, wire = seen[0]
    assert url.host == {"anthropic": "api.anthropic.com", "openai": "api.openai.com", "google": "generativelanguage.googleapis.com", "moonshot": "api.moonshot.ai"}[provider]
    assert "temperature" not in wire and "top_p" not in wire and "top_k" not in wire
    assert "context" not in wire and "trial_id" not in wire
    if provider == "anthropic":
        assert url.path == "/v1/messages"
        assert wire["max_tokens"] == 8192
        assert wire["output_config"]["effort"] == "low"
        assert wire["system"] == request.system_prompt
        assert wire["messages"] == [{"role": "user", "content": request.user_message}]
        schema = wire["output_config"]["format"]["schema"]
        assert all("minimum" not in value and "maximum" not in value for value in schema["properties"].values())
        assert "cache_control" not in wire and "thinking" not in wire
    elif provider == "google":
        assert url.path == "/v1beta/models/gemini-4-hydrogen:generateContent"
        config = wire["generationConfig"]
        assert config["maxOutputTokens"] == 8192
        thinking = config["thinkingConfig"]
        # ProtoJSON accepts both the original proto name and lowerCamelCase.
        assert thinking.get("thinkingLevel", thinking.get("thinking_level")).lower() == "low"
        assert "includeThoughts" not in config["thinkingConfig"]
        assert not {"temperature", "topP", "topK"} & set(config)
        assert "cachedContent" not in wire
        assert "automaticContinuation" not in wire and "shouldReturnHttpResponse" not in wire
        schema = config["responseJsonSchema"]
    else:
        assert url.path == "/v1/chat/completions"
        assert wire["reasoning_effort"] == "low"
        assert wire["max_completion_tokens"] == 8192
        assert wire["response_format"]["json_schema"]["strict"] is True
        assert len(wire["messages"]) == 2
        schema = wire["response_format"]["json_schema"]["schema"]
        if provider == "openai":
            assert wire["prompt_cache_options"] == {"mode": "explicit"}
            assert wire["store"] is False
        else:
            assert "prompt_cache_options" not in wire
    assert list(schema["properties"]) == list(request.json_schema["properties"])
    assert request.json_schema == rendered.json_schema


@pytest.mark.parametrize("provider", PROVIDERS)
@pytest.mark.parametrize("status,kind,retryable", [(400, "bad_request", False), (401, "authentication", False), (429, "rate_limit", True), (500, "server_error", True)])
def test_sdk_errors_are_safe_and_have_no_hidden_retries(provider: str, status: int, kind: str, retryable: bool, requests: dict) -> None:
    """A failing HTTP response consumes one recorded attempt, with no raw error/header leakage."""
    calls = []

    async def handler(request):
        calls.append(request)
        return httpx2.Response(status, json={"error": {"message": FAKE_KEY, "code": status, "status": "RESOURCE_EXHAUSTED", "type": "fixture_error"}}, headers={"fixture-secret": FAKE_KEY})

    async def run():
        adapter = _adapter(provider, httpx2.MockTransport(handler))
        try:
            with pytest.raises(ClientError) as raised:
                await adapter.complete(requests[provider])
            assert raised.value.kind == kind
            assert raised.value.status_code == status
            assert raised.value.retryable is retryable
            assert FAKE_KEY not in str(raised.value)
        finally:
            await adapter.aclose()

    asyncio.run(run())
    assert len(calls) == 1


@pytest.mark.parametrize("provider", PROVIDERS)
def test_truncation_and_missing_usage_are_not_fabricated(provider: str, requests: dict) -> None:
    """Normalize cap stops and preserve unavailable provider fields as null."""
    parser = anthropic_response if provider == "anthropic" else google_response if provider == "google" else chat_response
    response = parser(_body(provider, requests[provider], truncated=True))
    assert response.output_truncated
    assert not validate_response(response, requests[provider].json_schema).valid
    missing = parser({})
    assert missing.returned_model_version is None
    assert missing.usage.reasoning_tokens is None
    assert missing.usage.cache_read_tokens is None
    assert missing.usage.cache_write_tokens is None


def test_frozen_payload_guard_catches_changes(requests: dict) -> None:
    """A client must not silently regenerate changed or provider-mismatched arguments."""
    request = deepcopy(requests["openai"])
    request.api_payload["reasoning_effort"] = "high"
    with pytest.raises(ValueError, match="disagree"):
        frozen_api_payload(request, "openai")
    with pytest.raises(ValueError, match="own provider"):
        frozen_api_payload(requests["openai"], "moonshot")
    with pytest.raises(ValueError, match="frozen"):
        frozen_api_payload(replace(requests["openai"], api_payload=None), "openai")


def test_env_loading_precedence_quotes_comments_and_no_execution(tmp_path: Path) -> None:
    """Load only known keys with process precedence, no interpolation, and no shell evaluation."""
    path = tmp_path / ".env"
    marker = tmp_path / "must_not_exist"
    path.write_text(f'export OPENAI_API_KEY="file-key" # comment\nMOONSHOT_API_KEY=\'literal-$(touch {marker})\'\nUNUSED_KEY=ignored\n')
    keys = load_api_keys(["openai", "moonshot"], path, environ={"OPENAI_API_KEY": "process-key"})
    assert keys["openai"] == "process-key"
    assert keys["moonshot"].startswith("literal-$(touch ")
    assert not marker.exists()
    assert set(keys) == {"openai", "moonshot"}


def test_env_errors_never_echo_values(tmp_path: Path) -> None:
    """Report missing names or a line number without exposing invalid/placeholder secrets."""
    path = tmp_path / ".env"
    path.write_text('OPENAI_API_KEY="' + FAKE_KEY)
    with pytest.raises(ValueError) as raised:
        load_api_keys(["openai"], path, environ={})
    assert FAKE_KEY not in str(raised.value)
    path.write_text("OPENAI_API_KEY=replace_with_openai_key\n")
    with pytest.raises(ValueError, match="OPENAI_API_KEY"):
        load_api_keys(["openai"], path, environ={})


def test_runner_records_api_arguments_and_controls_the_only_retry_loop(tmp_path: Path) -> None:
    """Integrate a real SDK fixture with the runner, marking its saved records synthetic."""
    trials = [trial for trial in build_manifest(ROOT / "configs/study1.yaml", "smoke") if trial["request"]["provider"] == "openai"]
    trials[0]["execution_position"] = 1
    manifest, log = tmp_path / "plan.jsonl", tmp_path / "attempts.jsonl"
    write_manifest(trials, manifest)
    request = ModelRequest(**trials[0]["request"])
    calls = []

    async def handler(http_request):
        calls.append(json.loads(http_request.content))
        if len(calls) == 1:
            return httpx2.Response(429, json={"error": {"message": FAKE_KEY, "type": "rate_limit"}})
        return httpx2.Response(200, json=_body("openai", request))

    async def run():
        adapter = _adapter("openai", httpx2.MockTransport(handler))

        class FixtureClient:
            execution_mode = "mock"

            async def complete(self, selected):
                return await adapter.complete(selected)

        try:
            return await run_manifest(manifest, log, FixtureClient(), policy=RunnerPolicy(backoff_initial_seconds=0))
        finally:
            await adapter.aclose()

    summary = asyncio.run(run())
    assert summary.calls_started == 2 and summary.valid == 1
    records = read_jsonl(log)
    assert len(records) == len(calls) == 2
    assert all(record["synthetic"] for record in records)
    assert records[0]["request"]["api_payload"] == calls[0] == calls[1]
    assert FAKE_KEY not in log.read_text()


@pytest.mark.parametrize("provider", PROVIDERS)
@pytest.mark.parametrize("failure,kind", [(httpx2.ReadTimeout, "timeout"), (httpx2.ConnectError, "connection")])
def test_sdk_transport_errors_are_normalized_once(provider: str, failure: type, kind: str, requests: dict) -> None:
    """Keep transport timeouts/disconnects visible to the runner instead of hidden SDK retries."""
    calls = []

    async def handler(request):
        calls.append(request)
        raise failure(FAKE_KEY, request=request)

    async def run():
        adapter = _adapter(provider, httpx2.MockTransport(handler))
        try:
            with pytest.raises(ClientError) as raised:
                await adapter.complete(requests[provider])
            assert raised.value.kind == kind
            assert FAKE_KEY not in str(raised.value)
        finally:
            await adapter.aclose()

    asyncio.run(run())
    assert len(calls) == 1


def test_factory_constructs_sdk_clients_without_network_and_disables_retries(requests: dict, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Construct the actual default adapters with fake process keys, then close without a call."""
    for name in KEY_NAMES.values():
        monkeypatch.setenv(name, FAKE_KEY)

    async def run():
        clients = create_provider_clients(list(requests.values()), env_path=tmp_path / ".env")
        try:
            assert set(clients.clients) == set(PROVIDERS)
            for provider in ("anthropic", "openai", "moonshot"):
                assert clients.clients[provider].sdk.max_retries == 0
            assert clients.clients["google"].sdk._api_client._http_options.retry_options.attempts == 1
        finally:
            await clients.aclose()

    asyncio.run(run())


@pytest.mark.parametrize("provider", PROVIDERS)
def test_unverified_origin_does_not_silently_use_the_adapter_default(provider: str, requests: dict) -> None:
    """Reject disagreement between recorded destination and the verified client endpoint."""
    request = deepcopy(requests[provider])
    request.settings["transport"]["base_url"] = "https://example.invalid"
    with pytest.raises(ValueError, match="origin differs"):
        frozen_api_payload(request, provider)


def test_future_smoke_verified_status_keeps_payloads_usable(requests: dict) -> None:
    """Permit a later verified batch while continuing to reject unreviewed settings."""
    request = deepcopy(requests["openai"])
    request.settings["verification_status"] = "smoke_verified"
    assert frozen_api_payload(request, "openai") == request.api_payload
    request.settings["verification_status"] = "pending_official_documentation_review"
    with pytest.raises(ValueError, match="documentation must be verified"):
        build_api_payload(request)
