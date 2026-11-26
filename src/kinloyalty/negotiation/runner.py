"""Run frozen Study 2 units with per-pair journals, bounded calls, and disk recovery."""

import asyncio
import json
import uuid
import os
from contextlib import ExitStack
from collections.abc import Awaitable, Callable
from dataclasses import asdict
from pathlib import Path
from typing import Any

from kinloyalty.clients.base import ModelClient
from kinloyalty.logs import content_hash, file_hash
from kinloyalty.negotiation.journal import Study2Log as AttemptLog
from kinloyalty.negotiation.collection import check_terminals, load_histories, recovery_candidates, turn_path
from kinloyalty.negotiation.config import config_from_snapshot
from kinloyalty.negotiation.engine import run_episode
from kinloyalty.negotiation.history import reconstruct, seal, terminal_record, unit_complete
from kinloyalty.negotiation.manifest import read_manifest, spec_from_row
from kinloyalty.provenance import collect_provenance
from kinloyalty.runner import RunnerPolicy
from kinloyalty.negotiation.authorization import ModelDriftError, SmokeAuthorization


def check_destination(directory: str | Path, *, live: bool) -> None:
    """Reject protected study destinations before creating any collection artifact."""
    directory = Path(directory).resolve()
    root = Path(__file__).resolve().parents[3]
    protected = [root / path for path in ('data/study1', 'prompts/study1', 'results/study1', 'preregistration',
                                           'data/study2/pilot', 'data/study2/main')]
    if not live:
        protected.append(root / 'data/study2/smoke')
    if any(directory.is_relative_to(path.resolve()) for path in protected):
        raise ValueError('Collection must stay outside real-study artifact directories except approved live smoke.')


async def run_manifest(
    manifest_path: str | Path, directory: str | Path, clients: dict[str, ModelClient], *,
    sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
    authorization: SmokeAuthorization | None = None,
) -> dict[str, Any]:
    """Execute/resume a mock plan, validating saved history before any new call.

    One writer owns the collection; episodes interleave while turns remain
    sequential. Natural episodes and probes share call limits but have separate
    terminal summaries. The probe budget counts all reserved/completed attempts,
    including API failures and uncertain interrupted calls, across invocations.
    """
    rows = read_manifest(manifest_path)
    config = config_from_snapshot(rows[0]['snapshot'])
    modes = {client.execution_mode for client in clients.values()}
    mode = next(iter(modes)) if len(modes) == 1 else None
    live = mode == 'live'
    if mode not in {'mock', 'live'} or (live and authorization is None):
        raise ValueError('Live collection requires the explicit smoke authorization; otherwise use mock clients.')
    if live and any(row['phase'] != 'smoke' for row in rows):
        raise ValueError('This authorization permits only the four-episode/16-probe smoke plan.')
    if not live and authorization is not None:
        raise ValueError('A live authorization cannot be attached to mock execution.')
    directory = Path(directory)
    check_destination(directory, live=live)
    for row in rows:
        spec = spec_from_row(row)
        if any(model not in clients or clients[model].execution_mode != mode for model in {spec.buyer_model, spec.seller_model}):
            raise ValueError('Phase 3 collection requires mock clients; real calls are not enabled.')
    policy = RunnerPolicy(**config.study['runner'], invalid_reasks=1)
    manifest_hash = file_hash(manifest_path)
    provenance, run_id = collect_provenance(), str(uuid.uuid4())
    contract = authorization.contract(manifest_hash) if live else None
    if live:
        if provenance['code_dirty'] is not False or not provenance['git_commit']:
            raise ValueError('Real smoke calls require a clean committed code checkout.')
        if set(authorization.expected_versions) != {model['api_model_id'] for model in config.models.values()}:
            raise ValueError('The smoke authorization must name all four prior model versions.')
    stopped = False
    global_slots = asyncio.Semaphore(policy.concurrency)
    model_slots = {model: asyncio.Semaphore(policy.per_model_concurrency) for model in config.model_order}
    episode_slots = asyncio.Semaphore(policy.concurrency)
    async def acquire(model):
        await model_slots[model].acquire()
        try:
            await global_slots.acquire()
        except BaseException:
            model_slots[model].release()
            raise
    def release(model):
        global_slots.release()
        model_slots[model].release()
    with ExitStack() as stack:
        episode_store = stack.enter_context(AttemptLog(directory / 'episodes.jsonl'))
        probe_store = stack.enter_context(AttemptLog(directory / 'probes.jsonl'))
        if episode_store.pending or probe_store.pending:
            raise ValueError('Terminal stores cannot contain call reservations.')
        paths = {row['pair_id']: turn_path(directory, row) for row in rows}
        if set((directory / 'turns').glob('*.jsonl')) - set(paths.values()):
            raise ValueError('Unexpected pair log is not bound to this manifest.')
        stores = {pair: stack.enter_context(AttemptLog(path)) for pair, path in sorted(paths.items())}
        candidates, additions = recovery_candidates(stores)
        contract_path = directory / 'collection.json'
        if contract_path.exists() and json.loads(contract_path.read_text()) != contract:
            raise ValueError('Saved collection authorization/budget differs; it cannot reset on resume.')
        histories, progress = load_histories(rows, candidates, manifest_hash, execution_mode=mode)
        missing_episodes = check_terminals(rows, histories, progress, manifest_hash, episode_store.records, probe=False, allow_missing=True)
        missing_probes = check_terminals(rows, histories, progress, manifest_hash, probe_store.records, probe=True, allow_missing=True)
        row_map = {spec_from_row(row).episode_id: row for row in rows}
        probe_used = sum(len(histories[identity]) for identity, row in row_map.items() if row['is_probe'])
        natural_used = sum(len(histories[identity]) for identity, row in row_map.items() if not row['is_probe'])
        probe_cap = authorization.probe_attempt_cap if live else config.study['smoke']['probes']['max_total_attempts']
        natural_cap = authorization.natural_attempt_cap if live else None
        if probe_used > probe_cap:
            raise ValueError('Saved probes exceed the approved attempt budget.')
        if natural_cap is not None and natural_used > natural_cap:
            raise ValueError('Saved natural attempts exceed the approved attempt budget.')
        if live:
            for history in histories.values():
                for record in history:
                    expected = authorization.expected_versions[record['request']['api_model_id']]
                    observed = record['response']['returned_model_version'] if record['response'] is not None else expected
                    if record.get('expected_model_version') != expected or record.get('model_drift') != (observed != expected):
                        raise ValueError('Saved model-version diagnostic differs from the authorized baseline.')
                    if record.get('model_drift'):
                        raise ModelDriftError('The collection already records model drift; researcher review is required.')
            if not contract_path.exists():
                with contract_path.open('x', encoding='utf-8') as stream:
                    stream.write(json.dumps(contract, indent=2) + '\n')
                    stream.flush()
                    os.fsync(stream.fileno())
        # All completed, pending, and terminal records have passed validation.
        for store, record in additions:
            store.append(record)
        for store in stores.values():
            store.pending.clear()
            store._save_pending()
        for identity in [*missing_episodes, *missing_probes]:
            row = row_map[identity]
            (probe_store if row['is_probe'] else episode_store).append(
                terminal_record(row, progress[identity], histories[identity], manifest_hash))
        dispatch = max((record['dispatch_sequence'] for history in histories.values() for record in history), default=0)
        already = sum(unit_complete(row, progress[identity], histories[identity]) for identity, row in row_map.items())
        calls = 0
        async def execute(row):
            nonlocal dispatch, probe_used, natural_used, calls, stopped
            identity = spec_from_row(row).episode_id
            if unit_complete(row, progress[identity], histories[identity]):
                return
            async with episode_slots:
                store = stores[row['pair_id']]
                def envelope(attempt):
                    base = {**asdict(attempt), 'schema_version': 1, 'study': 'study2',
                            'record_id': f'{identity}/attempt-{attempt.attempt_number:04d}',
                            'pair_id': row['pair_id'], 'manifest_sha256': manifest_hash,
                            'episode_sha256': row['episode_sha256'], 'source_sha256': row['source_sha256'],
                            'run_id': run_id, 'runner_policy': asdict(policy), **provenance}
                    if live:
                        expected = authorization.expected_versions[attempt.request.api_model_id]
                        base.update(expected_model_version=expected,
                                    model_drift=attempt.response is not None and attempt.response.returned_model_version != expected)
                    return base
                def start(attempt, checkpoint):
                    nonlocal dispatch, probe_used, natural_used, calls
                    dispatch += 1
                    base = envelope(attempt)
                    base['dispatch_sequence'] = dispatch
                    store.reserve(seal(base))
                    calls += 1
                    if row['is_probe']:
                        probe_used += 1
                    else:
                        natural_used += 1
                def finish(attempt, checkpoint):
                    nonlocal stopped
                    base = envelope(attempt)
                    base['dispatch_sequence'] = store.pending[base['record_id']]['dispatch_sequence']
                    record = seal(base)
                    store.append(record)
                    histories[identity].append(record)
                    progress[identity] = checkpoint
                    if record.get('model_drift'):
                        stopped = True
                        raise ModelDriftError('A returned model version changed; the response is logged and dispatch has stopped.')
                def can_start():
                    return not stopped and (probe_used < probe_cap if row['is_probe'] else natural_cap is None or natural_used < natural_cap)
                result = await run_episode(
                    config, spec_from_row(row), clients, progress=progress[identity], policy=policy, sleep=sleep,
                    on_start=start, on_attempt=finish, acquire=acquire, release=release,
                    single_turn=row['is_probe'], can_start=can_start, allow_live=live,
                )
                replayed = reconstruct(row, histories[identity], manifest_hash, execution_mode=mode)
                if result.attempts and content_hash(asdict(replayed)) != content_hash(asdict(result.progress)):
                    raise ValueError('Engine progress differs from independent attempt replay.')
                progress[identity] = replayed
                if unit_complete(row, replayed, histories[identity]):
                    (probe_store if row['is_probe'] else episode_store).append(
                        terminal_record(row, replayed, histories[identity], manifest_hash))
                elif result.attempts and result.attempts[-1].api_error is not None and not result.attempts[-1].api_error['retryable']:
                    raise ValueError('Nonretryable API error stopped the collection; inspect safe attempt metadata.')
        def summarize(status='complete'):
            unfinished = [identity for identity, row in row_map.items() if not unit_complete(row, progress[identity], histories[identity])]
            summary = {'status': status, 'execution_mode': mode, 'planned_units': len(rows), 'already_final': already, 'new_calls': calls,
                       'recovered_attempts': len(additions), 'repaired_terminal_records': len(missing_episodes) + len(missing_probes),
                       'episodes_complete': len(episode_store.records), 'probes_complete': len(probe_store.records),
                       'probe_attempts_used': probe_used, 'probe_attempt_cap': probe_cap,
                       'natural_attempts_used': natural_used, 'natural_attempt_cap': natural_cap,
                       'unfinished_unit_ids': unfinished, 'manifest_sha256': manifest_hash,
                       'pair_log_bytes': {pair: store.path.stat().st_size if store.path.exists() else 0 for pair, store in stores.items()}}
            (directory / 'run_summary.json').write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
            return summary
        tasks = [asyncio.create_task(execute(row)) for row in rows]
        try:
            await asyncio.gather(*tasks)
        except BaseException as error:
            for task in tasks:
                task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)
            # Finish pure accounting even when a drift response halted dispatch.
            for identity, row in row_map.items():
                replayed = reconstruct(row, histories[identity], manifest_hash, execution_mode=mode)
                progress[identity] = replayed
                store = probe_store if row['is_probe'] else episode_store
                if unit_complete(row, replayed, histories[identity]) and not any(record['episode_id'] == identity for record in store.records):
                    store.append(terminal_record(row, replayed, histories[identity], manifest_hash))
            summarize('halted_model_drift' if isinstance(error, ModelDriftError) else 'halted_error')
            raise
        return summarize('unfinished' if any(not unit_complete(row, progress[identity], histories[identity]) for identity, row in row_map.items()) else 'complete')
