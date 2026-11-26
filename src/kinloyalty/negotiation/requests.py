"""Build one stateless request from a negotiation assignment and live state."""

from copy import deepcopy
from dataclasses import replace

from kinloyalty.clients.base import ModelRequest
from kinloyalty.clients.payloads import build_api_payload
from kinloyalty.negotiation.config import Study2Config
from kinloyalty.negotiation.prompts import render_system_prompt, render_turn_prompt
from kinloyalty.negotiation.rules import next_role, validate_state
from kinloyalty.negotiation.schemas import response_schema
from kinloyalty.negotiation.state import EpisodeSpec, EpisodeState


def build_turn_request(config: Study2Config, spec: EpisodeSpec, state: EpisodeState) -> ModelRequest:
    """Freeze the current mover's messages, schema, and provider payload without calling it."""
    validate_state(state)
    if state.scenario != spec.scenario or state.message_limit != config.message_limit:
        raise ValueError("Episode assignment, state, and configured limit do not match.")
    role = next_role(state)
    model_key = spec.buyer_model if role == "buyer" else spec.seller_model
    model = config.models[model_key]
    rendered = render_turn_prompt(
        config, buyer_model=spec.buyer_model, seller_model=spec.seller_model,
        condition=spec.condition, role=role, scenario=spec.scenario,
        transcript=state.turns, swapped_model=spec.swapped_model,
    )
    system = rendered.system_prompt
    if spec.custom_cards is not None:
        if len(spec.custom_cards) != 2 or any(
            card is not None and not isinstance(card, str) for card in spec.custom_cards
        ):
            raise ValueError("Custom cards must contain optional buyer and seller card text.")
        system = render_system_prompt(
            config, model=model_key, role=role, scenario=spec.scenario,
            counterparty_card=spec.custom_cards[0 if role == "buyer" else 1],
        )
    settings = deepcopy(config.roster["defaults"])
    settings.update({
        "requested_parameters": deepcopy(model["requested_parameters"]),
        "caching": deepcopy(model["caching"]), "transport": deepcopy(model["transport"]),
        "verification_status": config.roster["verification_status"],
    })
    own_offers = [turn for turn in state.turns if turn.role == role]
    number = len(state.turns) + 1
    request = ModelRequest(
        trial_id=f"{spec.episode_id}/message-{number:02d}", provider=model["provider"],
        api_model_id=model["api_model_id"], endpoint=model["endpoint"], settings=settings,
        system_prompt=system, user_message=rendered.user_message,
        json_schema=response_schema(number, state.message_limit),
        # Local mock metadata is not sent by any provider adapter. Even here,
        # expose only this role's private limit and the public latest offers.
        context={
            "role": role, "message_number": number, "message_limit": state.message_limit,
            "reference_price": state.scenario.reference_price,
            "own_limit": state.scenario.buyer_max if role == "buyer" else state.scenario.seller_min,
            "latest_offer": int(state.turns[-1].price) if state.turns else None,
            "own_latest_offer": int(own_offers[-1].price) if own_offers else None,
            "card_says": rendered.disclosure.card_says if role == "buyer" and spec.custom_cards is None else "none",
            "custom_cards": spec.custom_cards is not None,
        },
    )
    return replace(request, api_payload=build_api_payload(request))
