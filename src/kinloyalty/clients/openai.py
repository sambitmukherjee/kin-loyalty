"""Call OpenAI Chat Completions with strict JSON and explicit-only cache mode."""

from typing import Any

import openai

from kinloyalty.clients.base import ClientError, ModelRequest, ModelResponse
from kinloyalty.clients.payloads import BASE_URLS, frozen_api_payload
from kinloyalty.clients.response_data import chat_response, status_error


class OpenAIClient:
    """Use the official SDK once per attempt, without Responses or retained messages."""

    execution_mode = "live"
    provider = "openai"
    base_url = BASE_URLS["openai"]
    key_name = "OPENAI_API_KEY"

    def __init__(self, *, api_key: str | None = None, sdk: Any = None) -> None:
        """Accept an explicit key or an injected SDK for offline transport tests."""
        if sdk is None and not api_key:
            raise ValueError(f"{self.key_name} is required.")
        self.sdk = sdk if sdk is not None else openai.AsyncOpenAI(
            api_key=api_key, base_url=self.base_url, max_retries=0, timeout=120,
        )

    async def complete(self, request: ModelRequest) -> ModelResponse:
        """Read the complete raw JSON body while excluding all response/request headers."""
        payload = frozen_api_payload(request, self.provider)
        try:
            response = await self.sdk.with_raw_response.chat.completions.create(**payload)
            body = response.http_response.json()
        except openai.APITimeoutError:
            raise ClientError("timeout") from None
        except openai.APIConnectionError:
            raise ClientError("connection") from None
        except openai.APIStatusError as error:
            raise status_error(error.status_code) from None
        return chat_response(body)

    async def aclose(self) -> None:
        """Release SDK HTTP resources without making a request."""
        await self.sdk.close()
