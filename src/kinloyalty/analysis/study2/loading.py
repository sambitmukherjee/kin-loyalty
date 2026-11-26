"""Load only terminal main/synthetic Study 2 collections after full replay validation."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from kinloyalty.logs import file_hash, read_jsonl
from kinloyalty.negotiation.collection import load_histories, replay_collection, turn_path
from kinloyalty.negotiation.config import Study2Config, config_from_snapshot
from kinloyalty.negotiation.manifest import read_manifest
from kinloyalty.analysis.study2.outcomes import buyer_offer_outcomes


@dataclass(frozen=True)
class AnalysisData:
    """Keep replayed episode/call tables and the complete planned scenario universe."""

    episodes: pd.DataFrame
    calls: pd.DataFrame
    messages: pd.DataFrame
    scenarios: pd.DataFrame
    config: Study2Config
    synthetic: bool
    manifest_sha256: str
    replay: dict[str, Any]


def check_input_paths(manifest: str | Path, directory: str | Path) -> None:
    """Reject protected Study 1 and real smoke/pilot locations before opening logs."""
    root = Path(__file__).resolve().parents[4]
    forbidden = [root / path for path in ('data/study1', 'results/study1', 'data/study2/smoke', 'data/study2/pilot')]
    for candidate in (Path(manifest).resolve(), Path(directory).resolve()):
        if any(candidate.is_relative_to(path) for path in forbidden):
            raise ValueError('Study 2 inference cannot read Study 1 or smoke/pilot data.')


def load_data(manifest_path: str | Path, directory: str | Path, *, allow_synthetic: bool = False) -> AnalysisData:
    """Validate phase/mode first, replay outcomes, and derive structured-price diagnostics."""
    check_input_paths(manifest_path, directory)
    rows = read_manifest(manifest_path)
    phase = rows[0]['phase']
    if phase not in {'main', 'synthetic'} or any(row['is_probe'] for row in rows):
        raise ValueError('Inference accepts only main or explicit synthetic designs, never smoke/pilot/probes.')
    synthetic = phase == 'synthetic'
    if synthetic and not allow_synthetic:
        raise ValueError('Synthetic input requires explicit allow_synthetic=True.')
    directory = Path(directory)
    mode = 'mock' if synthetic else 'live'
    replay = replay_collection(manifest_path, directory)
    if replay['unfinished_unit_ids']:
        raise ValueError('All planned episodes must be terminal before inference.')
    paths = {row['pair_id']: turn_path(directory, row) for row in rows}
    records_by_pair = {pair: read_jsonl(path) for pair, path in paths.items()}
    histories, progress = load_histories(rows, records_by_pair, file_hash(manifest_path), execution_mode=mode)
    terminals = read_jsonl(directory / 'episodes.jsonl')
    if any(record['synthetic'] != synthetic or record['execution_mode'] != mode or record['is_probe'] for record in terminals):
        raise ValueError('Mixed/implicit synthetic or probe episodes are not eligible for inference.')
    episodes = pd.DataFrame(terminals).sort_values('episode_id').reset_index(drop=True)
    episodes['excluded'] = episodes.outcome.eq('excluded')
    episodes['deal'] = episodes.outcome.eq('deal').astype(float)
    episodes['buyer_opens'] = episodes.opener.eq('buyer').astype(float)
    episodes['card_says_same'] = episodes.card_says.eq('same').astype(float)
    episodes['card_says_other'] = episodes.card_says.eq('other').astype(float)
    episodes['surplus_share'] = episodes.buyer_surplus_share.astype(float)
    episodes['within_deal_share'] = episodes.surplus_share.where(episodes.deal.eq(1))
    episodes['messages_to_agreement'] = episodes.messages_used.astype(float).where(episodes.deal.eq(1))
    for column in ('deal', 'buyer_mandate_violation', 'seller_mandate_violation'):
        episodes[column] = episodes[column].astype(float).where(~episodes.excluded)
    episode_metadata = episodes.set_index('episode_id')
    calls, messages = [], []
    offer_outcomes = {}
    for identity, history in histories.items():
        for record in history:
            response = record['response']
            calls.append({
                'record_id': record['record_id'], 'episode_id': identity, 'pair_id': record['pair_id'], 'model': record['model'], 'role': record['role'],
                'provider': record['request']['provider'], 'message_number': record['message_number'],
                'valid': record['validation']['valid'] if record['validation'] is not None else None,
                'api_error': record['api_error']['kind'] if record['api_error'] else None,
                'response_number': record['response_number'], 'api_retry_index': record['api_retry_index'],
                'finish_reason': response['finish_reason'] if response else None,
                'output_characters': len(response['output_text']) if response else None,
                'returned_model_version': response['returned_model_version'] if response else None,
                'accept_price_mismatch': record['accept_price_mismatch'],
                **(response['usage'] if response else {field: None for field in
                   ('input_tokens', 'output_tokens', 'reasoning_tokens', 'cache_read_tokens', 'cache_write_tokens')}),
            })
        for number, turn in enumerate(progress[identity].state.turns, 1):
            metadata = episode_metadata.loc[identity]
            messages.append({'episode_id': identity, 'pair_id': metadata.pair_id, 'role': turn.role,
                             'model': metadata.buyer_model if turn.role == 'buyer' else metadata.seller_model,
                             'message_number': number, 'action': turn.action,
                             'offer_price': int(turn.price) if turn.action == 'offer' else None,
                             'characters': len(turn.message)})
        metadata = episode_metadata.loc[identity]
        offer_outcomes[identity] = buyer_offer_outcomes(progress[identity].state.turns,
                                                       buyer_max=metadata.buyer_max, seller_min=metadata.seller_min)
    for column in ('buyer_offer_count', 'buyer_first_offer_position', 'buyer_average_concession'):
        episodes[column] = episodes.episode_id.map({identity: values[column] for identity, values in offer_outcomes.items()})
        if column != 'buyer_offer_count':
            episodes[column] = episodes[column].astype(float).where(~episodes.excluded)
    scenarios = episodes[['pair_id', 'scenario_id']].drop_duplicates().sort_values(['pair_id', 'scenario_id']).reset_index(drop=True)
    return AnalysisData(episodes, pd.DataFrame(calls), pd.DataFrame(messages), scenarios,
                        config_from_snapshot(rows[0]['snapshot']), synthetic, file_hash(manifest_path), replay)
