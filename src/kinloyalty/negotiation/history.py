"""Reconstruct progress and terminal records from verified saved call attempts."""

from copy import deepcopy
import json
from dataclasses import asdict, replace
from typing import Any

from kinloyalty.clients.base import ModelResponse, TokenUsage
from kinloyalty.logs import content_hash
from kinloyalty.negotiation.cards import seller_disclosure
from kinloyalty.negotiation.config import config_from_snapshot
from kinloyalty.negotiation.engine import EpisodeProgress
from kinloyalty.negotiation.manifest import initial_state, spec_from_row
from kinloyalty.negotiation.requests import build_turn_request
from kinloyalty.negotiation.rules import allowed_actions, apply_turn, exclude_episode, next_role, score_outcome
from kinloyalty.negotiation.validate import validate_response
from kinloyalty.runner import RunnerPolicy


def seal(record: dict[str, Any]) -> dict[str, Any]:
    """Bind all serialized fields with a deterministic integrity digest."""
    result = deepcopy(record)
    result.pop('record_sha256', None)
    result['record_sha256'] = content_hash(result)
    return result


def check_signature(record: dict[str, Any]) -> None:
    """Reject a modified or partially formed saved record."""
    if record.get('record_sha256') != seal(record)['record_sha256']:
        raise ValueError('Saved record hash does not match its content.')


def initial_progress(row: dict[str, Any]) -> EpisodeProgress:
    """Initialize a natural episode or a marked hand-written probe position."""
    config = config_from_snapshot(row['snapshot'])
    state = initial_state(row, config)
    return EpisodeProgress(spec_from_row(row), state, initial_turn_count=len(state.turns))


def unit_complete(row: dict[str, Any], progress: EpisodeProgress, records: list[dict[str, Any]]) -> bool:
    """Treat a valid/excluded probe response as complete without scoring its fixture."""
    return bool(records and records[-1]['is_final_for_turn']) if row['is_probe'] else progress.state.final


def reconstruct(
    row: dict[str, Any], records: list[dict[str, Any]], manifest_sha256: str,
) -> EpisodeProgress:
    """Revalidate every reply and transition; saved decisions are never trusted directly."""
    config = config_from_snapshot(row['snapshot'])
    progress = initial_progress(row)
    previous = None
    for record in records:
        check_signature(record)
        if unit_complete(row, progress, [previous] if previous is not None else []):
            raise ValueError('A terminal unit has extra saved attempts.')
        spec = progress.spec
        role = next_role(progress.state)
        model = spec.buyer_model if role == 'buyer' else spec.seller_model
        number = len(progress.state.turns) + 1
        request = progress.pending_request or build_turn_request(config, spec, progress.state)
        expected_fields = {
            'schema_version': 1, 'study': 'study2',
            'record_id': f'{spec.episode_id}/attempt-{progress.attempts + 1:04d}',
            'episode_id': spec.episode_id, 'phase': spec.phase, 'pair_id': row['pair_id'],
            'manifest_sha256': manifest_sha256, 'episode_sha256': row['episode_sha256'],
            'source_sha256': row['source_sha256'], 'is_probe': row['is_probe'],
            'message_number': number, 'role': role, 'model': model,
            'attempt_number': progress.attempts + 1, 'response_number': 2 if progress.invalid_replies else 1,
            'allowed_actions': list(allowed_actions(number, config.message_limit)),
            'request': asdict(request), 'synthetic': True, 'execution_mode': 'mock',
            'runner_policy': asdict(RunnerPolicy(**config.study['runner'], invalid_reasks=1)),
        }
        for key, value in expected_fields.items():
            if key not in record or content_hash(record[key]) != content_hash(value):
                raise ValueError(f'Saved attempt has an invalid binding: {key}.')
        expected_index = 1
        if previous is not None and previous['run_id'] == record['run_id'] and (
            previous['message_number'], previous['response_number']) == (number, record['response_number']):
            if previous['api_error'] is None or not previous['api_error']['retryable'] or previous['api_error']['kind'] == 'interrupted':
                raise ValueError('An invalid extra retry appears within a response opportunity.')
            expected_index = previous['api_retry_index'] + 1
        if record['api_retry_index'] != expected_index or expected_index > config.study['runner']['api_attempts_per_response']:
            raise ValueError('Saved API retry index violates the fixed retry budget.')
        if not record.get('completed_at_utc') or type(record.get('dispatch_sequence')) is not int:
            raise ValueError('Completed attempts require timing and dispatch metadata.')
        is_reask = progress.invalid_replies == 1
        progress = replace(progress, attempts=progress.attempts + 1,
                           reasks=progress.reasks + int(is_reask and not progress.reask_started),
                           retries=progress.retries + int(progress.retry_pending),
                           reask_started=progress.reask_started or is_reask, pending_request=request)
        error = record['api_error']
        final, excluded, mismatch = False, False, False
        validation = None
        if error is not None:
            if (set(error) != {'kind', 'retryable', 'status_code'} or type(error['retryable']) is not bool
                    or error['kind'] not in {'rate_limit', 'timeout', 'server_error', 'connection',
                                             'authentication', 'bad_request', 'unknown', 'interrupted'}
                    or record['response'] is not None):
                raise ValueError('Invalid saved API-error record.')
            progress = replace(progress, retry_pending=True)
        else:
            body = dict(record['response'])
            body['usage'] = TokenUsage(**body['usage'])
            validation = validate_response(ModelResponse(**body), role=role, message_number=number,
                                           message_limit=config.message_limit)
            if validation.valid:
                state = apply_turn(progress.state, validation.turn)
                mismatch = state.outcome.accept_price_mismatch if state.outcome is not None else False
                final = True
                progress = replace(progress, state=state, invalid_replies=0, pending_request=None,
                                   reask_started=False, retry_pending=False)
            else:
                invalids = progress.invalid_replies + 1
                final = excluded = invalids == 2
                progress = replace(progress, invalid_replies=invalids, retry_pending=False,
                                   state=exclude_episode(progress.state) if excluded else progress.state)
        values = {'validation': asdict(validation) if validation is not None else None,
                  'is_final_for_turn': final, 'excluded': excluded, 'accept_price_mismatch': mismatch}
        if any(content_hash(record.get(key)) != content_hash(value) for key, value in values.items()):
            raise ValueError('Saved validation/outcome differs from replay of the response.')
        previous = record
    return progress


def terminal_record(
    row: dict[str, Any], progress: EpisodeProgress, records: list[dict[str, Any]], manifest_sha256: str,
) -> dict[str, Any]:
    """Derive a deterministic episode or unscored probe summary from its attempts."""
    if not unit_complete(row, progress, records):
        raise ValueError('An unfinished unit has no terminal record.')
    spec = progress.spec
    base = {'record_id': spec.episode_id, 'episode_id': spec.episode_id, 'phase': spec.phase,
            'pair_id': row['pair_id'], 'manifest_sha256': manifest_sha256,
            'episode_sha256': row['episode_sha256'], 'is_probe': row['is_probe'],
            'synthetic': True, 'execution_mode': 'mock', 'attempts': progress.attempts,
            'reasks': progress.reasks, 'retries': progress.retries,
            'completed_at_utc': records[-1]['completed_at_utc']}
    if row['is_probe']:
        return seal({**base, 'model': records[-1]['model'], 'role': row['probe_role'],
                     'message_number': row['probe_position'], 'status': 'excluded' if records[-1]['excluded'] else 'valid',
                     'action': records[-1]['validation']['turn']['action'] if not records[-1]['excluded'] else None})
    disclosure = seller_disclosure(config_from_snapshot(row['snapshot']), buyer_model=spec.buyer_model,
                                  seller_model=spec.seller_model, condition=spec.condition, swapped_model=spec.swapped_model)
    outcome = progress.state.outcome
    return seal({**base, 'buyer_model': spec.buyer_model, 'seller_model': spec.seller_model,
                 'self_pair': spec.buyer_model == spec.seller_model, 'condition': spec.condition,
                 'card_says': disclosure.card_says, 'card_model_text': disclosure.model_text,
                 **asdict(spec.scenario), 'outcome': outcome.kind, 'deal_price': outcome.deal_price,
                 'accepted_by': outcome.accepted_by, 'messages_used': len(progress.state.turns),
                 'accept_price_mismatch': outcome.accept_price_mismatch,
                 'accept_supplied_price_json': json.dumps(progress.state.turns[-1].price) if outcome.kind == 'deal' else None,
                 'excluded_role': outcome.excluded_role, 'exclusion_message_number': outcome.exclusion_message_number,
                 **asdict(score_outcome(progress.state))})
