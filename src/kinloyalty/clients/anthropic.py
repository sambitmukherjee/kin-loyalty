"""Call Anthropic's stateless Messages API once per runner attempt."""

from typing import Any

import anthropic

from kinloyalty.clients.base import ClientError, ModelRequest, ModelResponse
from kinloyalty.clients.payloads import BASE_URLS, frozen_api_payload
from kinloyalty.clients.response_data import anthropic_response, status_error


class AnthropicClient:
    """Use the official SDK with hidden retries disabled and body-only response capture."""

    execution_mode = "live"

    def __init__(self, *, api_key: str | None = None, sdk: Any = None) -> None:
        """Accept an explicit key or an injected SDK for offline transport tests."""
        if sdk is None and not api_key:
            raise ValueError("ANTHROPIC_API_KEY is required.")
        self.sdk = sdk if sdk is not None else anthropic.AsyncAnthropic(
            api_key=api_key, base_url=BASE_URLS["anthropic"], max_retries=0, timeout=120,
        )

    async def complete(self, request: ModelRequest) -> ModelResponse:
        """Send only the frozen arguments and capture no headers or credentials."""
        payload = frozen_api_payload(request, "anthropic")
        try:
            response = await self.sdk.with_raw_response.messages.create(**payload)
            body = await response.json()
        except anthropic.APITimeoutError:
            raise ClientError("timeout") from None
        except anthropic.APIConnectionError:
            raise ClientError("connection") from None
        except anthropic.APIStatusError as error:
            raise status_error(error.status_code) from None
        return anthropic_response(body)

    async def aclose(self) -> None:
        """Release SDK HTTP resources without making a request."""
        await self.sdk.close()
