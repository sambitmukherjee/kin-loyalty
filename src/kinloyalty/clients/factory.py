"""Load local API credentials and construct provider clients without sending requests."""

import os
import shlex
from collections.abc import Mapping, Sequence
from pathlib import Path

from kinloyalty.clients.base import ModelClient, ModelRequest, ModelResponse
from kinloyalty.clients.payloads import frozen_api_payload


KEY_NAMES = {
    "anthropic": "ANTHROPIC_API_KEY", "openai": "OPENAI_API_KEY",
    "google": "GOOGLE_API_KEY", "moonshot": "MOONSHOT_API_KEY",
}


def load_api_keys(
    providers: Sequence[str], env_path: str | Path = ".env",
    *, environ: Mapping[str, str] | None = None,
) -> dict[str, str]:
    """Read known keys only; nonempty process values take precedence over .env.

    Accept single-line KEY=value, optional export, quotes and inline comments.
    Never evaluate shell commands, interpolate variables, or echo line contents.
    """
    names = {provider: KEY_NAMES[provider] for provider in providers}
    environment = os.environ if environ is None else environ
    values = {name: environment[name] for name in names.values() if environment.get(name)}
    path = Path(env_path)
    if path.exists():
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            line = line.strip()
            if line.startswith("export "):
                line = line[7:].lstrip()
            name, separator, value = line.partition("=")
            name = name.strip()
            if not separator or name not in names.values() or name in values:
                continue
            try:
                parts = shlex.split(value, comments=True, posix=True)
            except ValueError:
                raise ValueError(f"Invalid .env quoting on line {number}; contents omitted.") from None
            if len(parts) > 1:
                raise ValueError(f"Quote the .env value on line {number}; contents omitted.")
            values[name] = parts[0] if parts else ""
    missing = [name for name in names.values() if not values.get(name) or values[name].startswith("replace_with_")]
    if missing:
        raise ValueError("Missing API credentials: " + ", ".join(missing))
    return {provider: values[name] for provider, name in names.items()}


class ProviderClients:
    """Route a frozen request to its provider while sharing the runner's client interface."""

    execution_mode = "live"

    def __init__(self, clients: Mapping[str, ModelClient]) -> None:
        """Register explicitly constructed provider adapters."""
        self.clients = dict(clients)

    async def complete(self, request: ModelRequest) -> ModelResponse:
        """Delegate once without adding history, messages, or local context to the API."""
        return await self.clients[request.provider].complete(request)

    async def aclose(self) -> None:
        """Close every registered provider's SDK resources."""
        for client in self.clients.values():
            await client.aclose()


def create_provider_clients(
    requests: Sequence[ModelRequest], *, env_path: str | Path = ".env",
) -> ProviderClients:
    """Check frozen arguments and keys before constructing SDKs; make no API calls."""
    from kinloyalty.clients.anthropic import AnthropicClient
    from kinloyalty.clients.google import GoogleClient
    from kinloyalty.clients.moonshot import MoonshotClient
    from kinloyalty.clients.openai import OpenAIClient

    constructors = {
        "anthropic": AnthropicClient, "openai": OpenAIClient,
        "google": GoogleClient, "moonshot": MoonshotClient,
    }
    if not requests:
        raise ValueError("At least one frozen provider request is required.")
    for request in requests:
        frozen_api_payload(request, request.provider)
    providers = list(dict.fromkeys(request.provider for request in requests))
    keys = load_api_keys(providers, env_path)
    return ProviderClients({provider: constructors[provider](api_key=keys[provider]) for provider in providers})
