"""Call Google generateContent once, preserving raw body and default thinking visibility."""

import json
from typing import Any

import httpx2
from google import genai
from google.genai import errors, types

from kinloyalty.clients.base import ClientError, ModelRequest, ModelResponse
from kinloyalty.clients.payloads import BASE_URLS, frozen_api_payload
from kinloyalty.clients.response_data import google_response, status_error


class GoogleClient:
    """Disable SDK retries/continuations and capture the raw JSON body without headers."""

    execution_mode = "live"

    def __init__(self, *, api_key: str | None = None, sdk: Any = None) -> None:
        """Accept an explicit key or an injected SDK for offline transport tests."""
        if sdk is None and not api_key:
            raise ValueError("GOOGLE_API_KEY is required.")
        self.sdk = sdk if sdk is not None else genai.Client(
            api_key=api_key, vertexai=False, enterprise=False,
            http_options=types.HttpOptions(
                base_url=BASE_URLS["google"], api_version="v1beta",
                retry_options=types.HttpRetryOptions(attempts=1), timeout=120000,
            ),
        )

    async def complete(self, request: ModelRequest) -> ModelResponse:
        """Use the SDK raw-body option; do not request extra thought summaries."""
        payload = frozen_api_payload(request, "google")
        try:
            response = await self.sdk.aio.models.generate_content(**payload)
        except errors.APIError as error:
            raise status_error(error.code) from None
        except httpx2.TimeoutException:
            raise ClientError("timeout") from None
        except httpx2.TransportError:
            raise ClientError("connection") from None
        if response.sdk_http_response is None or response.sdk_http_response.body is None:
            raise ValueError("Google SDK did not expose the requested raw JSON body.")
        return google_response(json.loads(response.sdk_http_response.body))

    async def aclose(self) -> None:
        """Release asynchronous and synchronous SDK resources without making a request."""
        await self.sdk.aio.aclose()
        self.sdk.close()
