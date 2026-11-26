"""Generate explicit synthetic negotiation logs with a known buyer-label effect."""

import asyncio
import json
from pathlib import Path

from kinloyalty.clients.base import ModelResponse, TokenUsage
from kinloyalty.negotiation.cards import seller_disclosure
from kinloyalty.negotiation.config import config_from_snapshot
from kinloyalty.negotiation.manifest import build_manifest, spec_from_row, write_manifest
from kinloyalty.negotiation.mock import NegotiationMockClient
from kinloyalty.negotiation.runner import check_destination, run_manifest


def _reply(action: str, price: int | None, api_id: str) -> ModelResponse:
    content = {'message': 'Synthetic planted-effect verification reply.', 'action': action, 'price': price}
    text = json.dumps(content)
    return ModelResponse(text, returned_model_version=f'mock/{api_id}',
                         raw_response={'synthetic': True, 'content': content}, finish_reason='stop',
                         usage=TokenUsage(input_tokens=100, output_tokens=len(text.split()), reasoning_tokens=5,
                                          cache_read_tokens=0, cache_write_tokens=0))


def simulate_collection(
    config_path: str | Path, directory: str | Path, *, label_effect: float = .2,
    scenario_seed: int = 73101, order_seed: int = 73102, swapped_seed: int = 73103,
    edge_cases: bool = False,
) -> dict:
    """Run scripted mock agents through the actual manifest/engine/logger.

    Both sides make legal offers. The seller's script is label-blind: it asks
    the same price under each card and accepts the buyer's eventual counteroffer.
    The buyer makes two offers; only its final offer changes with a same-model
    card. At effect .2 the planted within-scenario surplus difference is exactly
    -.2 because limits are multiples of five. No real data or API is accessed.
    """
    directory = Path(directory)
    check_destination(directory, live=False)
    if directory.exists():
        raise ValueError('Choose a fresh synthetic collection directory.')
    rows = build_manifest(config_path, 'synthetic', scenario_seed=scenario_seed,
                          order_seed=order_seed, swapped_seed=swapped_seed)
    config = config_from_snapshot(rows[0]['snapshot'])
    scripts = {}
    for row in rows:
        spec = spec_from_row(row)
        scenario = spec.scenario
        zone = scenario.buyer_max - scenario.seller_min
        disclosure = seller_disclosure(config, buyer_model=spec.buyer_model, seller_model=spec.seller_model,
                                      condition=spec.condition, swapped_model=spec.swapped_model)
        first = round(scenario.seller_min + .25 * zone)
        final = round(scenario.seller_min + .5 * zone) + (round(label_effect * zone) if disclosure.card_says == 'same' else 0)
        if final <= 0:
            raise ValueError('This planted effect would produce a nonpositive offer; choose another fixture.')
        actions = [('offer', first), ('offer', scenario.buyer_max), ('offer', final), ('accept', None)]
        if scenario.opener == 'seller':
            actions = [('offer', scenario.buyer_max), ('offer', first), ('offer', scenario.buyer_max),
                       ('offer', final), ('accept', None)]
        for number, (action, price) in enumerate(actions, 1):
            role = scenario.opener if number % 2 else ('seller' if scenario.opener == 'buyer' else 'buyer')
            model = spec.buyer_model if role == 'buyer' else spec.seller_model
            scripts[f'{spec.episode_id}/message-{number:02d}'] = [_reply(action, price, config.models[model]['api_model_id'])]
    if edge_cases:
        # A separate explicit fixture exercises analysis eligibility and replay;
        # it deliberately no longer has the exact planted primary contrast.
        identities = list(dict.fromkeys(key.split('/message-')[0] for key in scripts))
        def set_reply(identity, number, action, price):
            scripts[f'{identity}/message-{number:02d}'] = [_reply(action, price, 'edge-fixture')]
        scripts[f'{identities[0]}/message-01'] = [ModelResponse('invalid JSON'), ModelResponse('invalid JSON')]
        set_reply(identities[1], 1, 'walk_away', None)
        for number in range(1, config.message_limit + 1):
            set_reply(identities[2], number, 'offer' if number < config.message_limit else 'walk_away',
                      500 if number < config.message_limit else None)
        for index, price in ((3, 500), (5, 1), (6, 100000)):
            set_reply(identities[index], 1, 'offer', price)
            set_reply(identities[index], 2, 'accept', None)
        first = f'{identities[4]}/message-01'
        scripts[first] = [ModelResponse('invalid JSON'), *scripts[first]]
        last_buyer = 4 if f'{identities[7]}/message-05' in scripts else 3
        set_reply(identities[7], last_buyer, 'offer', 1)
    # Guards in the runner prevent even synthetic artifacts from entering real
    # study directories. The explicit synthetic phase is preserved in every log.
    directory.mkdir(parents=True)
    manifest = directory / 'manifest.jsonl'
    write_manifest(rows, manifest)
    client = NegotiationMockClient(seed=config.study['seeds']['mock'], scripts=scripts)
    summary = asyncio.run(run_manifest(manifest, directory / 'collection', {model: client for model in config.model_order}))
    (directory / 'simulation.json').write_text(json.dumps({
        'synthetic': True, 'label_effect': label_effect, 'mechanism': 'buyer_final_offer_shift_in_zone_units',
        'scenario_seed': scenario_seed, 'order_seed': order_seed, 'swapped_seed': swapped_seed,
        'edge_cases': edge_cases,
        'expected_primary_contrast': None if edge_cases else (-label_effect if label_effect == .2 else 'rounding-dependent'),
    }, indent=2) + '\n')
    return summary
