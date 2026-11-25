"""Define the small, transport-independent interface used by model clients."""

from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass(frozen=True)
class ModelRequest:
    """Hold frozen request content; context is local metadata, never prompt text."""

    trial_id: str
    provider: str
    api_model_id: str
    endpoint: str
    settings: dict[str, Any]
    system_prompt: str
    user_message: str
    json_schema: dict[str, Any]
    context: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class TokenUsage:
    """Preserve unavailable token counts as None rather than inventing zeros."""

    input_tokens: int | None = None
    output_tokens: int | None = None
    reasoning_tokens: int | None = None
    cache_read_tokens: int | None = None
    cache_write_tokens: int | None = None


@dataclass(frozen=True)
class ModelResponse:
    """Keep the response body, provider metadata, and normalized truncation flag."""

    output_text: str
    returned_model_version: str | None = None
    raw_response: dict[str, Any] = field(default_factory=dict)
    reasoning_text: str | None = None
    finish_reason: str | None = None
    usage: TokenUsage = field(default_factory=TokenUsage)
    output_truncated: bool = False


class ClientError(Exception):
    """Expose safe API-error metadata without raw exception text or headers."""

    def __init__(self, kind: str, *, retryable: bool = True, status_code: int | None = None) -> None:
        """Create a categorized API error; provider adapters must sanitize upstream."""
        allowed = {"rate_limit", "timeout", "server_error", "connection", "authentication", "bad_request", "unknown"}
        if kind not in allowed:
            raise ValueError("ClientError requires a known, non-secret error category.")
        self.kind = kind
        self.retryable = retryable
        self.status_code = status_code
        super().__init__(kind)


class ModelClient(Protocol):
    """Provide one self-contained asynchronous model call per invocation."""

    execution_mode: str

    async def complete(self, request: ModelRequest) -> ModelResponse:
        """Return the full normalized response or raise a safe ClientError."""
        ...
