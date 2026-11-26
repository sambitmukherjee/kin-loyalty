"""Render exact Study 2 requests without keys, SDK imports, or schema decisions."""

import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from kinloyalty.negotiation import Role
from kinloyalty.negotiation.cards import Disclosure, seller_disclosure
from kinloyalty.negotiation.config import Study2Config, template_text
from kinloyalty.negotiation.scenarios import Scenario, pair_id
from kinloyalty.negotiation.transcript import TranscriptTurn, other_role, render_transcript


@dataclass(frozen=True)
class RenderedPrompt:
    """Keep complete stateless messages and card metadata outside the prompt text."""

    system_prompt: str
    user_message: str
    disclosure: Disclosure


def render_template(config: Study2Config, filename: str, values: Mapping[str, object]) -> str:
    """Replace uppercase placeholders once, preserving literal JSON and whitespace."""
    template = template_text(config, filename).removesuffix("\n")

    def substitute(match: re.Match[str]) -> str:
        name = match.group(1)
        if name not in values:
            raise ValueError(f"Missing template value: {name}")
        return str(values[name])

    # Substituted messages are never reinterpreted as templates or instructions.
    return re.sub(r"\{([A-Z][A-Z0-9_]*)\}", substitute, template)


def render_card(config: Study2Config, *, profile: Mapping[str, str], model_text: str) -> str:
    """Fill the ordered plain-text card without adding trust or quality fields."""
    return render_template(config, "agent_card.txt", {
        "REPRESENTS": profile["represents"], "AGENT_TYPE": profile["agent_type"],
        "AGENT_ID": profile["agent_id"], "PROTOCOL": profile["protocol"],
        "COUNTERPARTY_MODEL_TEXT": model_text,
    })


def render_system_prompt(
    config: Study2Config, *, model: str, role: Role, scenario: Scenario,
    counterparty_card: str | None,
) -> str:
    """Render a role's mandate with an optional card, exposing only its own limit.

    This low-level renderer permits either role's optional card for reuse.
    Study 2's assignment wrapper supplies a buyer card and no seller card.
    """
    counterparty = other_role(role)
    if model not in config.models:
        raise ValueError("Unknown model identity.")
    if counterparty_card is None:
        description = render_template(config, "counterparty_without_card.txt", {
            "COUNTERPARTY_ROLE": counterparty,
        })
    else:
        description = render_template(config, "counterparty_with_card.txt", {
            "COUNTERPARTY_ROLE": counterparty, "AGENT_CARD": counterparty_card,
        })
    identity = config.models[model]
    # Do not even pass the other participant's limit to the template renderer.
    values = {
        "SELF_EXACT_MODEL": identity["display_name"], "SELF_LAB": identity["lab"],
        "ITEM": scenario.item, "REFERENCE_PRICE": scenario.reference_price,
        "MESSAGE_LIMIT": config.message_limit, "COUNTERPARTY_DESCRIPTION": description,
        "BUYER_MAX" if role == "buyer" else "SELLER_MIN": (
            scenario.buyer_max if role == "buyer" else scenario.seller_min
        ),
    }
    return render_template(config, f"{role}_system.txt", values)


def render_user_message(
    config: Study2Config, *, role: Role, scenario: Scenario, transcript: Sequence[TranscriptTurn],
) -> str:
    """Render a live prefix and the appropriate opening, last-offer, or final notice."""
    counterparty = other_role(role)
    number = len(transcript) + 1
    if number > config.message_limit:
        raise ValueError("No request may follow the final message.")
    for index, turn in enumerate(transcript):
        expected = scenario.opener if index % 2 == 0 else other_role(scenario.opener)
        if turn.role != expected or turn.action != "offer":
            raise ValueError("A live transcript must alternate offers from the configured opener.")
    mover = scenario.opener if number % 2 else other_role(scenario.opener)
    if role != mover:
        raise ValueError("The requested role is not the next mover.")
    if transcript:
        heading = render_template(config, "transcript_heading.txt", {})
        block = f"{heading}\n{render_transcript(transcript, mover=role)}"
    else:
        block = render_template(config, "opening.txt", {})
    notice = ""
    if number == config.message_limit - 1:
        notice = render_template(config, "last_offer.txt", {"COUNTERPARTY_ROLE": counterparty}) + "\n"
    elif number == config.message_limit:
        notice = render_template(config, "final_message.txt", {"COUNTERPARTY_ROLE": counterparty}) + "\n"
    return render_template(config, "turn.txt", {
        "TRANSCRIPT_BLOCK": block, "K": number, "MESSAGE_LIMIT": config.message_limit,
        "TURN_NOTICE": notice,
    })


def render_turn_prompt(
    config: Study2Config, *, buyer_model: str, seller_model: str, condition: str,
    role: Role, scenario: Scenario, transcript: Sequence[TranscriptTurn] = (),
    swapped_model: str | None = None,
) -> RenderedPrompt:
    """Render one Study 2 request, always buyer-only disclosure and one wording."""
    if scenario.pair_id != pair_id(config, buyer_model, seller_model):
        raise ValueError("Scenario and participant pair do not match.")
    if config.study["cards"]["seller"] is not None or config.study["cards"]["buyer"] is None:
        raise ValueError("Study 2 requires a buyer card and no seller card.")
    disclosure = seller_disclosure(
        config, buyer_model=buyer_model, seller_model=seller_model,
        condition=condition, swapped_model=swapped_model,
    )
    card = render_card(config, profile=config.study["cards"]["buyer"], model_text=disclosure.model_text)
    return RenderedPrompt(
        system_prompt=render_system_prompt(
            config, model=buyer_model if role == "buyer" else seller_model,
            role=role, scenario=scenario, counterparty_card=card if role == "buyer" else None,
        ),
        user_message=render_user_message(config, role=role, scenario=scenario, transcript=transcript),
        disclosure=disclosure,
    )
