"""Load per-pair attempt stores, recover uncertain calls, and check terminal records."""

from contextlib import ExitStack
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
import json
from typing import Any

from kinloyalty.logs import content_hash, file_hash, read_jsonl
from kinloyalty.negotiation.journal import Study2Log as AttemptLog
from kinloyalty.negotiation.history import check_signature, reconstruct, seal, terminal_record, unit_complete
from kinloyalty.negotiation.manifest import read_manifest, spec_from_row
from kinloyalty.negotiation.engine import EpisodeProgress


def validate_live_contract(contract: dict, *, phase: str) -> None:
    """Validate read-only replay contracts, including future pilot/main collections.

    This reader does not authorize or enable collection. The runner remains
    smoke-only until a separate approved execution phase implements its contract.
    """
    if phase not in {'smoke', 'pilot', 'main'} or contract.get('phase') != phase:
        raise ValueError('Live collection contract must match its manifest phase.')
    if phase == 'smoke':
        if contract.get('natural_attempt_cap') != 384 or contract.get('probe_attempt_cap') != 32:
            raise ValueError('Live smoke contract differs from the authorized budgets.')
    for field, minimum in (('natural_attempt_cap', 1), ('probe_attempt_cap', 0)):
        if type(contract.get(field)) is not int or contract[field] < minimum:
            raise ValueError('Live replay requires explicit nonnegative authorized budgets.')
    if not contract.get('approved_by') or not contract.get('approved_on'):
        raise ValueError('Live replay requires recorded researcher approval metadata.')
    versions = contract.get('expected_versions')
    if not isinstance(versions, dict) or not versions or any(not isinstance(value, str) or not value for value in versions.values()):
        raise ValueError('Live replay requires an explicit model-version baseline.')


def turn_path(directory: Path, row: dict[str, Any]) -> Path:
    """Return a manifest-derived pair path without trusting arbitrary log filenames."""
    return directory / 'turns' / f"{row['pair_id']}.jsonl"


def load_histories(rows: list[dict[str, Any]], records_by_pair: dict[str, list[dict[str, Any]]],
                   manifest_hash: str, *, execution_mode: str = 'mock') -> tuple[dict[str, list[dict[str, Any]]], dict[str, EpisodeProgress]]:
    """Validate pair placement, unique dispatch IDs, and every unit's attempt history."""
    row_map = {spec_from_row(row).episode_id: row for row in rows}
    histories = {identity: [] for identity in row_map}
    dispatches = set()
    for pair, records in records_by_pair.items():
        for record in records:
            identity = record.get('episode_id')
            if identity not in row_map or row_map[identity]['pair_id'] != pair:
                raise ValueError('Attempt is not in its manifest-derived pair file.')
            dispatch = record.get('dispatch_sequence')
            if type(dispatch) is not int or dispatch < 1 or dispatch in dispatches:
                raise ValueError('Attempt dispatch identities must be positive and globally unique.')
            dispatches.add(dispatch)
            histories[identity].append(record)
    progress = {identity: reconstruct(row_map[identity], history, manifest_hash, execution_mode=execution_mode) for identity, history in histories.items()}
    return histories, progress


def recovery_candidates(stores: dict[str, AttemptLog]) -> tuple[dict[str, list[dict]], list[tuple[AttemptLog, dict]]]:
    """Prepare interrupted records without modifying any artifact before validation."""
    candidates, additions = {}, []
    mutable = {'record_sha256', 'response', 'validation', 'api_error', 'is_final_for_turn',
               'excluded', 'accept_price_mismatch', 'completed_at_utc', 'latency_seconds', 'model_drift'}
    for pair, store in stores.items():
        records = list(store.records)
        existing = {record['record_id']: record for record in records}
        for identity, pending in sorted(store.pending.items(), key=lambda item: item[1]['dispatch_sequence']):
            check_signature(pending)
            if identity != pending['record_id'] or pending['response'] is not None or pending['validation'] is not None:
                raise ValueError('Invalid pending attempt reservation.')
            if identity in existing:
                if any(content_hash(pending[key]) != content_hash(existing[identity][key]) for key in set(pending) - mutable):
                    raise ValueError('Stale pending reservation conflicts with its completed record.')
                continue
            recovered = deepcopy(pending)
            recovered.update(completed_at_utc=datetime.now(timezone.utc).isoformat(), latency_seconds=None,
                             api_error={'kind': 'interrupted', 'retryable': True, 'status_code': None})
            recovered = seal(recovered)
            records.append(recovered)
            additions.append((store, recovered))
        candidates[pair] = records
    return candidates, additions


def check_terminals(rows: list[dict[str, Any]], histories: dict[str, list[dict[str, Any]]],
                    progress: dict[str, EpisodeProgress], manifest_hash: str, records: list[dict[str, Any]],
                    *, probe: bool, allow_missing: bool) -> list[str]:
    """Compare saved summaries with outcomes recomputed only from attempt histories."""
    row_map = {spec_from_row(row).episode_id: row for row in rows if row['is_probe'] == probe}
    seen = set()
    for record in records:
        identity = record.get('episode_id')
        if identity not in row_map or identity in seen:
            raise ValueError('Unknown or duplicate terminal record.')
        seen.add(identity)
        expected = terminal_record(row_map[identity], progress[identity], histories[identity], manifest_hash)
        if content_hash(record) != content_hash(expected):
            raise ValueError('Terminal record differs from replay of its call attempts.')
    missing = [identity for identity, row in row_map.items()
               if unit_complete(row, progress[identity], histories[identity]) and identity not in seen]
    if missing and not allow_missing:
        raise ValueError('Completed attempt history is missing its terminal summary; resume to repair it.')
    return missing


def replay_collection(manifest_path: str | Path, directory: str | Path) -> dict[str, Any]:
    """Verify all episode/probe summaries read-only, refusing unresolved pending calls."""
    import fcntl
    rows = read_manifest(manifest_path)
    directory = Path(directory)
    lock = directory / 'episodes.jsonl.lock'
    with ExitStack() as stack:
        if lock.exists():
            handle = stack.enter_context(lock.open('rb'))
            try:
                fcntl.flock(handle, fcntl.LOCK_SH | fcntl.LOCK_NB)
            except BlockingIOError:
                raise ValueError('Collection is active; replay requires a stopped writer.') from None
        paths = {row['pair_id']: turn_path(directory, row) for row in rows}
        if set((directory / 'turns').glob('*.jsonl')) - set(paths.values()):
            raise ValueError('Unexpected pair log is not bound to this manifest.')
        for path in [directory / 'episodes.jsonl', directory / 'probes.jsonl', *paths.values()]:
            if path.with_name(path.name + '.pending.json').exists():
                raise ValueError('Pending calls require explicit runner recovery before replay.')
        manifest_hash = file_hash(manifest_path)
        contract_path = directory / 'collection.json'
        contract = json.loads(contract_path.read_text()) if contract_path.exists() else {'execution_mode': 'mock'}
        mode = contract['execution_mode']
        if mode not in {'mock', 'live'} or contract.get('manifest_sha256', manifest_hash) != manifest_hash:
            raise ValueError('Invalid collection mode or manifest binding.')
        histories, progress = load_histories(rows, {pair: read_jsonl(path) for pair, path in paths.items()}, manifest_hash, execution_mode=mode)
        if mode == 'live':
            validate_live_contract(contract, phase=rows[0]['phase'])
            natural = probes_used = 0
            for history in histories.values():
                for record in history:
                    expected = contract['expected_versions'][record['request']['api_model_id']]
                    observed = record['response']['returned_model_version'] if record['response'] is not None else expected
                    if record.get('expected_model_version') != expected or record.get('model_drift') != (observed != expected):
                        raise ValueError('Saved model-version diagnostic differs from the authorized baseline.')
                    if record['is_probe']:
                        probes_used += 1
                    else:
                        natural += 1
            if natural > contract['natural_attempt_cap'] or probes_used > contract['probe_attempt_cap']:
                raise ValueError('Saved live attempts exceed their authorized collection budgets.')
        episodes, probes = read_jsonl(directory / 'episodes.jsonl'), read_jsonl(directory / 'probes.jsonl')
        check_terminals(rows, histories, progress, manifest_hash, episodes, probe=False, allow_missing=False)
        check_terminals(rows, histories, progress, manifest_hash, probes, probe=True, allow_missing=False)
        unfinished = [spec_from_row(row).episode_id for row in rows if not unit_complete(
            row, progress[spec_from_row(row).episode_id], histories[spec_from_row(row).episode_id])]
        return {'planned_units': len(rows), 'episodes_verified': len(episodes), 'probes_verified': len(probes),
                'unfinished_unit_ids': unfinished, 'attempts_verified': sum(map(len, histories.values())),
                'manifest_sha256': manifest_hash}
