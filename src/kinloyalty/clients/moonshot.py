"""Use Moonshot's verified OpenAI-compatible endpoint without changing cache defaults."""

from kinloyalty.clients.openai import OpenAIClient
from kinloyalty.clients.payloads import BASE_URLS


class MoonshotClient(OpenAIClient):
    """Share only the Chat Completions transport; payload/cache behavior remains provider-specific."""

    provider = "moonshot"
    base_url = BASE_URLS["moonshot"]
    key_name = "MOONSHOT_API_KEY"
