"""Draw paired scenario facts with explicit seeds and balanced item/opener strata."""

import hashlib
import json
import random
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from itertools import product

from kinloyalty.negotiation import Role
from kinloyalty.negotiation.config import Study2Config


@dataclass(frozen=True)
class Scenario:
    """Hold one condition-independent set of private and public negotiation facts."""

    scenario_id: str
    pair_id: str
    item: str
    reference_price: int
    seller_min: int
    buyer_max: int
    opener: Role

    def __post_init__(self) -> None:
        """Reject facts that cannot define a positive-surplus negotiation."""
        if self.opener not in {"buyer", "seller"}:
            raise ValueError("Unknown opener.")
        if any(type(value) is not int or value <= 0 for value in
               (self.reference_price, self.seller_min, self.buyer_max)):
            raise ValueError("Scenario prices and limits must be positive whole dollars.")
        if self.buyer_max <= self.seller_min:
            raise ValueError("A scenario must have a positive zone of agreement.")


def ordered_pairs(config: Study2Config) -> tuple[tuple[str, str], ...]:
    """Enumerate every ordered buyer/seller pairing, including self-pairs."""
    return tuple(product(config.model_order, repeat=2))


def pair_id(config: Study2Config, buyer_model: str, seller_model: str) -> str:
    """Build a stable pair identity from configured model keys."""
    if buyer_model not in config.models or seller_model not in config.models:
        raise ValueError("Both participants must be configured models.")
    return f"{buyer_model}__{seller_model}"


def _rng(seed: int, pair: str, purpose: str) -> random.Random:
    if type(seed) is not int:
        raise ValueError("An explicit integer seed is required.")
    encoded = json.dumps([seed, pair, purpose], separators=(",", ":")).encode("utf-8")
    return random.Random(int.from_bytes(hashlib.sha256(encoded).digest(), "big"))


def round_price(value: Decimal | int | float, increment: int = 5) -> int:
    """Round to the nearest dollar multiple, with positive exact half-steps upward."""
    amount = Decimal(str(value))
    if not amount.is_finite() or amount < 0 or type(increment) is not int or increment <= 0:
        raise ValueError("Rounding needs a nonnegative finite amount and positive integer increment.")
    return int((amount / increment).quantize(Decimal("1"), rounding=ROUND_HALF_UP)) * increment


def draw_balanced_scenarios(
    config: Study2Config, *, buyer_model: str, seller_model: str, seed: int, batch_id: str,
) -> tuple[Scenario, ...]:
    """Draw once per item/opener/replicate; callers reuse each scenario across cards.

    The seed is mandatory: this function never silently selects or exposes the
    configured main seed. Pair-specific streams are independent of call order.
    Scenario order is canonical; the later manifest layer shuffles episodes.
    """
    if not batch_id or ":" in batch_id:
        raise ValueError("A nonempty batch ID without a colon is required.")
    pair = pair_id(config, buyer_model, seller_model)
    rng = _rng(seed, pair, "scenario_limits")
    limits = config.study["limits"]
    design = config.study["scenario_design"]
    scenarios = []
    strata = ((item, opener) for item, opener in product(config.study["items"], design["openers"])
              for _ in range(design["replicates_per_item_opener"][opener]))
    for item, opener in strata:
        reference = item["reference_price"]
        # Convert the uniform draw's decimal representation before multiplication
        # so an exact half-step follows the documented rule, not binary rounding.
        seller = Decimal(reference) * Decimal(str(rng.uniform(*limits["seller_multiplier"])))
        buyer = Decimal(reference) * Decimal(str(rng.uniform(*limits["buyer_multiplier"])))
        scenarios.append(Scenario(
            scenario_id=f"study2:{batch_id}:{pair}:s{len(scenarios) + 1:03d}",
            pair_id=pair, item=item["name"], reference_price=reference,
            seller_min=round_price(seller, limits["rounding_increment"]),
            buyer_max=round_price(buyer, limits["rounding_increment"]), opener=opener,
        ))
    return tuple(scenarios)


def swapped_self_names(
    config: Study2Config, *, buyer_model: str, count: int, seed: int,
) -> tuple[str, ...]:
    """Balance alternative names, rotating the six-count model with the buyer.

    Traverse the other models cyclically, starting with the next roster model.
    Allocate the remainder to the last alternatives and then shuffle assignments
    with a separate named stream. At count 20 the next model gets six, the other
    two get seven; across four self-pairs each model gets the shortfall once.
    """
    pair = pair_id(config, buyer_model, buyer_model)
    if type(count) is not int or count < 1:
        raise ValueError("A positive integer name count is required.")
    order = config.model_order
    index = order.index(buyer_model)
    alternatives = [order[(index + offset) % len(order)] for offset in range(1, len(order))]
    base, remainder = divmod(count, len(alternatives))
    names = [model for position, model in enumerate(alternatives)
             for _ in range(base + int(position >= len(alternatives) - remainder))]
    _rng(seed, pair, "swapped_names").shuffle(names)
    return tuple(names)
