"""Normalize raw provider JSON without fabricating unavailable usage or version fields."""

from typing import Any

from kinloyalty.clients.base import ClientError, ModelResponse, TokenUsage


def status_error(status: int | None) -> ClientError:
    """Translate HTTP status into safe metadata without response/error/header text."""
    if status in {401, 403}:
        return ClientError("authentication", retryable=False, status_code=status)
    if status == 429:
        return ClientError("rate_limit", status_code=status)
    if status in {408, 504}:
        return ClientError("timeout", status_code=status)
    if status is not None and status >= 500:
        return ClientError("server_error", status_code=status)
    return ClientError("bad_request" if status is not None and 400 <= status < 500 else "unknown", retryable=False, status_code=status)


def chat_response(body: dict[str, Any]) -> ModelResponse:
    """Read OpenAI-compatible response fields, including Kimi reasoning and cache writes."""
    choices = body.get("choices") or []
    choice = choices[0] if choices else {}
    message = choice.get("message") or {}
    usage = body.get("usage") or {}
    inputs = usage.get("prompt_tokens_details") or {}
    outputs = usage.get("completion_tokens_details") or {}
    return ModelResponse(
        output_text=message.get("content") or "", returned_model_version=body.get("model"),
        raw_response=body, reasoning_text=message.get("reasoning_content"),
        finish_reason=choice.get("finish_reason"),
        output_truncated=choice.get("finish_reason") == "length",
        usage=TokenUsage(
            input_tokens=usage.get("prompt_tokens"), output_tokens=usage.get("completion_tokens"),
            reasoning_tokens=outputs.get("reasoning_tokens"),
            cache_read_tokens=inputs.get("cached_tokens"), cache_write_tokens=inputs.get("cache_write_tokens"),
        ),
    )


def anthropic_response(body: dict[str, Any]) -> ModelResponse:
    """Keep default thinking blocks separate from the final JSON text."""
    blocks = body.get("content") or []
    thoughts = [block["thinking"] for block in blocks if block.get("type") == "thinking" and isinstance(block.get("thinking"), str)]
    usage = body.get("usage") or {}
    return ModelResponse(
        output_text="".join(block["text"] for block in blocks if block.get("type") == "text"),
        returned_model_version=body.get("model"), raw_response=body,
        reasoning_text="\n".join(thoughts) if thoughts else None,
        finish_reason=body.get("stop_reason"), output_truncated=body.get("stop_reason") == "max_tokens",
        usage=TokenUsage(
            input_tokens=usage.get("input_tokens"), output_tokens=usage.get("output_tokens"),
            reasoning_tokens=(usage.get("output_tokens_details") or {}).get("thinking_tokens"),
            cache_read_tokens=usage.get("cache_read_input_tokens"),
            cache_write_tokens=usage.get("cache_creation_input_tokens"),
        ),
    )


def google_response(body: dict[str, Any]) -> ModelResponse:
    """Read generateContent's camelCase raw body, retaining missing cache fields as None."""
    candidates = body.get("candidates") or []
    candidate = candidates[0] if candidates else {}
    parts = (candidate.get("content") or {}).get("parts") or []
    thoughts = [part["text"] for part in parts if part.get("thought") and isinstance(part.get("text"), str)]
    usage = body.get("usageMetadata") or {}
    finish = candidate.get("finishReason")
    return ModelResponse(
        output_text="".join(part["text"] for part in parts if not part.get("thought") and isinstance(part.get("text"), str)),
        returned_model_version=body.get("modelVersion"), raw_response=body,
        reasoning_text="\n".join(thoughts) if thoughts else None, finish_reason=finish,
        output_truncated=finish in {"MAX_TOKENS", "CONTINUATION"},
        usage=TokenUsage(
            input_tokens=usage.get("promptTokenCount"), output_tokens=usage.get("candidatesTokenCount"),
            reasoning_tokens=usage.get("thoughtsTokenCount"), cache_read_tokens=usage.get("cachedContentTokenCount"),
        ),
    )
