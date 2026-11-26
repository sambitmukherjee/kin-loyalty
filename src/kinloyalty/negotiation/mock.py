"""Provide rule-based negotiations, planted label effects, and scripted offline faults."""

import hashlib
import json
import math
from collections import defaultdict, deque
from collections.abc import Mapping, Sequence
from copy import deepcopy

from kinloyalty.clients.base import ModelRequest, ModelResponse, TokenUsage


class NegotiationMockClient:
    """Play either role using public offers and only the mover's private limit."""

    execution_mode = "mock"

    def __init__(
        self, *, seed: int = 0, label_effect: float = 0.0, strategy: str = "negotiate",
        scripts: Mapping[str, Sequence[ModelResponse | BaseException]] | None = None,
    ) -> None:
        """Configure synthetic buyer generosity or explicit per-message call scripts.

        Positive label_effect raises a buyer's price target under a same-model
        label in units of the reference price. It is a planted simulation control,
        not a model estimate. final_only reaches the last message and walks away.
        """
        if strategy not in {"negotiate", "walk_away", "final_only"}:
            raise ValueError("Unknown mock negotiation strategy.")
        if not math.isfinite(label_effect):
            raise ValueError("The planted label effect must be finite.")
        self.seed = seed
        self.label_effect = label_effect
        self.strategy = strategy
        self.scripts = {key: deque(values) for key, values in (scripts or {}).items()}
        self.requests: list[ModelRequest] = []
        self.call_counts: dict[str, int] = defaultdict(int)

    async def complete(self, request: ModelRequest) -> ModelResponse:
        """Return a scripted response/error or one whole-dollar synthetic action."""
        self.requests.append(deepcopy(request))
        self.call_counts[request.trial_id] += 1
        if self.scripts.get(request.trial_id):
            item = self.scripts[request.trial_id].popleft()
            if isinstance(item, BaseException):
                raise item
            return deepcopy(item)
        context = request.context
        role, limit = context["role"], context["own_limit"]
        reference, latest = context["reference_price"], context["latest_offer"]
        own_previous = context["own_latest_offer"]
        actions = request.json_schema["properties"]["action"]["enum"]
        shift = self.label_effect * reference if role == "buyer" and context["card_says"] == "same" else 0
        target = min(limit, round(.98 * reference + shift)) if role == "buyer" else max(limit, round(.98 * reference))
        acceptable = latest is not None and (latest <= target if role == "buyer" else latest >= target)
        if self.strategy == "walk_away":
            action, price = "walk_away", None
        elif self.strategy == "negotiate" and "accept" in actions and acceptable:
            action, price = "accept", None
        elif "offer" not in actions:
            action, price = "walk_away", None
        elif role == "buyer":
            price = min(target, round(.90 * reference + shift) if own_previous is None else own_previous + max(1, round(.04 * reference)))
            action, price = "offer", max(1, price)
        else:
            price = max(target, round(1.10 * reference) if own_previous is None else own_previous - max(1, round(.04 * reference)))
            action = "offer"
        content = {"message": "Synthetic negotiation reply.", "action": action, "price": price}
        text = json.dumps(content)
        digest = hashlib.sha256(f"{self.seed}:{request.trial_id}".encode()).digest()
        usage = TokenUsage(
            input_tokens=len((request.system_prompt + request.user_message).split()),
            output_tokens=len(text.split()), reasoning_tokens=digest[0] % 20,
            cache_read_tokens=0, cache_write_tokens=0,
        )
        return ModelResponse(
            output_text=text, returned_model_version=f"mock/{request.api_model_id}",
            raw_response={"synthetic": True, "content": content}, finish_reason="stop", usage=usage,
        )

    async def aclose(self) -> None:
        """Finish without keys, SDKs, network access, or external resources."""
        return None
