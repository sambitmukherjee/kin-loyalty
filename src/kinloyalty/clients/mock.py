"""Return explicitly synthetic, reproducible responses and scripted offline faults."""

import hashlib
import json
import random
from collections import defaultdict, deque
from collections.abc import Mapping, Sequence
from copy import deepcopy
from dataclasses import asdict

from kinloyalty.clients.base import ModelRequest, ModelResponse, TokenUsage


class MockClient:
    """Mimic the model interface without reading keys, importing SDKs, or networking."""

    execution_mode = "mock"

    def __init__(
        self, *, seed: int = 0, own_model_effect: int = 0,
        scripts: Mapping[str, Sequence[ModelResponse | BaseException]] | None = None,
    ) -> None:
        """Choose deterministic outcomes and optional per-trial scripted responses/errors."""
        self.seed = seed
        self.own_model_effect = own_model_effect
        self.scripts = {key: deque(values) for key, values in (scripts or {}).items()}
        self.requests: list[ModelRequest] = []
        self.call_counts: dict[str, int] = defaultdict(int)

    async def complete(self, request: ModelRequest) -> ModelResponse:
        """Return a scripted item or deterministic synthetic JSON for this trial."""
        self.requests.append(deepcopy(request))
        self.call_counts[request.trial_id] += 1
        if self.scripts.get(request.trial_id):
            item = self.scripts[request.trial_id].popleft()
            if isinstance(item, BaseException):
                raise item
            return item
        digest = hashlib.sha256(f"{self.seed}:{request.trial_id}".encode()).digest()
        rng = random.Random(int.from_bytes(digest[:8], "big"))
        content: dict[str, int | str] = {}
        for name, spec in request.json_schema["properties"].items():
            if spec["type"] == "integer":
                value = 40 + rng.randint(-10, 10)
                if request.context.get("label") == "own_model":
                    value += self.own_model_effect
                content[name] = max(spec.get("minimum", 0), min(spec.get("maximum", 100), value))
            elif "enum" in spec:
                expected = request.context.get("expected_answer")
                content[name] = expected if expected in spec["enum"] else spec["enum"][0]
            else:
                content[name] = "Synthetic response for offline testing."
        text = json.dumps(content, ensure_ascii=False)
        usage = TokenUsage(
            input_tokens=len((request.system_prompt + request.user_message).split()),
            output_tokens=len(text.split()), reasoning_tokens=rng.randint(1, 20),
            cache_read_tokens=0, cache_write_tokens=0,
        )
        return ModelResponse(
            output_text=text, returned_model_version=f"mock/{request.api_model_id}",
            raw_response={"synthetic": True, "content": content, "usage": asdict(usage)},
            finish_reason="stop", usage=usage,
        )
