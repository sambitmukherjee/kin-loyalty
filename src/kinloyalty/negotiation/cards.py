"""Resolve exact seller-card labels independently of actual negotiation behavior."""

from dataclasses import dataclass

from kinloyalty.negotiation.config import Study2Config
from kinloyalty.negotiation.scenarios import pair_id


@dataclass(frozen=True)
class Disclosure:
    """Distinguish the assigned condition, displayed relationship, and named model."""

    condition: str
    card_says: str
    model_key: str | None
    model_text: str


def seller_disclosure(
    config: Study2Config, *, buyer_model: str, seller_model: str, condition: str,
    swapped_model: str | None = None,
) -> Disclosure:
    """Resolve a card without sampling or comparative language in its model text.

    Swapped self-pairs require an explicit scheduled alternative. Never choose
    one silently at render time or change the real seller to match the label.
    """
    pair_id(config, buyer_model, seller_model)
    if condition not in config.study["conditions"]:
        raise ValueError("Unknown disclosure condition.")
    self_pair = buyer_model == seller_model
    needs_alternative = condition == "swapped" and self_pair
    if swapped_model is not None and not needs_alternative:
        raise ValueError("Supply an alternative only for swapped self-pairs.")
    if condition == "not_disclosed":
        return Disclosure(condition, "none", None, config.study["not_disclosed_model_text"])
    if condition == "true":
        named = seller_model
    elif self_pair:
        if swapped_model not in config.models or swapped_model == buyer_model:
            raise ValueError("A swapped self-pair needs an explicit alternative model.")
        named = swapped_model
    else:
        named = buyer_model
    model = config.models[named]
    if named != buyer_model and model["lab"] == config.models[buyer_model]["lab"]:
        raise ValueError("An other-model card must name another lab for this study.")
    return Disclosure(
        condition, "same" if named == buyer_model else "other", named,
        f"{model['display_name']} ({model['lab']})",
    )
