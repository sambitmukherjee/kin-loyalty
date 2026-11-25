"""Freeze verified SDK arguments while retaining the canonical local response schema."""

from copy import deepcopy
from typing import Any

from kinloyalty.clients.base import ModelRequest
from kinloyalty.logs import assert_no_credentials, content_hash


BASE_URLS = {
    "anthropic": "https://api.anthropic.com", "openai": "https://api.openai.com/v1",
    "google": "https://generativelanguage.googleapis.com", "moonshot": "https://api.moonshot.ai/v1",
}


def build_api_payload(request: ModelRequest) -> dict[str, Any]:
    """Map declared settings to SDK arguments without keys, headers, or local context."""
    settings = request.settings
    if settings.get("verification_status") not in {"documentation_verified_smoke_pending", "smoke_verified"}:
        raise ValueError("Provider documentation must be verified before freezing API arguments.")
    schema = deepcopy(request.json_schema)
    if not settings["transport"]["numeric_schema_bounds"]:
        for field in schema["properties"].values():
            field.pop("minimum", None)
            field.pop("maximum", None)
    limit, effort = settings["max_output_tokens"], settings["reasoning_effort"]
    if settings.get("sampling") != "provider_defaults" or not settings.get("stateless"):
        raise ValueError("These adapters require stateless calls with provider-default sampling.")
    if request.provider == "anthropic":
        payload = {
            "model": request.api_model_id, "max_tokens": limit,
            "system": request.system_prompt,
            "messages": [{"role": "user", "content": request.user_message}],
            "output_config": {"effort": effort, "format": {"type": "json_schema", "schema": schema}},
        }
    elif request.provider in {"openai", "moonshot"}:
        payload = {
            "model": request.api_model_id,
            "messages": [
                {"role": "system", "content": request.system_prompt},
                {"role": "user", "content": request.user_message},
            ],
            "reasoning_effort": effort, "max_completion_tokens": limit,
            "response_format": {"type": "json_schema", "json_schema": {
                "name": "study_response", "strict": True, "schema": schema,
            }},
        }
        if request.provider == "openai":
            payload.update(store=False, prompt_cache_options={"mode": "explicit"})
    elif request.provider == "google":
        payload = {
            "model": request.api_model_id,
            "contents": [{"role": "user", "parts": [{"text": request.user_message}]}],
            "config": {
                "system_instruction": request.system_prompt,
                "thinking_config": {"thinking_level": effort},
                "max_output_tokens": limit, "response_mime_type": "application/json",
                "response_json_schema": schema,
                # SDK-only controls keep one HTTP request and preserve the raw body.
                "automatic_function_calling": {"disable": True},
                "automatic_continuation": False, "should_return_http_response": True,
            },
        }
    else:
        raise ValueError(f"Unsupported provider: {request.provider}")
    assert_no_credentials(payload)
    return payload


def frozen_api_payload(request: ModelRequest, provider: str) -> dict[str, Any]:
    """Refuse stale/unfrozen or altered arguments before a client sends a request."""
    if request.provider != provider or request.api_payload is None:
        raise ValueError("A real client requires a frozen request for its own provider.")
    if request.settings["transport"]["base_url"] != BASE_URLS[provider]:
        raise ValueError("Configured API origin differs from this verified adapter; review it first.")
    if provider == "google" and request.settings["transport"].get("api_version") != "v1beta":
        raise ValueError("Google API version differs from the verified endpoint.")
    expected = build_api_payload(request)
    if content_hash(request.api_payload) != content_hash(expected):
        raise ValueError("Frozen API arguments disagree with the canonical request.")
    return deepcopy(request.api_payload)
