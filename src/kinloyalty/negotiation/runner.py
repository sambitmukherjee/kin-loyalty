"""Run frozen Study 2 units with per-pair journals, bounded calls, and disk recovery."""

import asyncio
import json
import uuid
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


async def run_manifest(
    manifest_path: str | Path, directory: str | Path, clients: dict[str, ModelClient], *,
    sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
) -> dict[str, Any]:
    """Execute/resume a mock plan, validating saved history before any new call.

    One writer owns the collection; episodes interleave while turns remain
    sequential. Natural episodes and probes share call limits but have separate
    terminal summaries. The probe budget counts all reserved/completed attempts,
    including API failures and uncertain interrupted calls, across invocations.
    """
    rows = read_manifest(manifest_path)
    config = config_from_snapshot(rows[0]['snapshot'])
    directory = Path(directory)
    root = Path(__file__).resolve().parents[3]
    protected = [root / path for path in ('data/study1', 'prompts/study1', 'results/study1', 'preregistration',
                                           'data/study2/smoke', 'data/study2/pilot', 'data/study2/main')]
    if any(directory.resolve().is_relative_to(path.resolve()) for path in protected):
        raise ValueError('Mock collection must stay outside real-study artifact directories.')
    for row in rows:
        spec = spec_from_row(row)
        if any(model not in clients or clients[model].execution_mode != 'mock' for model in {spec.buyer_model, spec.seller_model}):
            raise ValueError('Phase 3 collection requires mock clients; real calls are not enabled.')
    policy = RunnerPolicy(**config.study['runner'], invalid_reasks=1)
    manifest_hash = file_hash(manifest_path)
    provenance, run_id = collect_provenance(), str(uuid.uuid4())
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
        histories, progress = load_histories(rows, candidates, manifest_hash)
        missing_episodes = check_terminals(rows, histories, progress, manifest_hash, episode_store.records, probe=False, allow_missing=True)
        missing_probes = check_terminals(rows, histories, progress, manifest_hash, probe_store.records, probe=True, allow_missing=True)
        row_map = {spec_from_row(row).episode_id: row for row in rows}
        probe_used = sum(len(histories[identity]) for identity, row in row_map.items() if row['is_probe'])
        probe_cap = config.study['smoke']['probes']['max_total_attempts']
        if probe_used > probe_cap:
            raise ValueError('Saved probes exceed the approved attempt budget.')
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
            nonlocal dispatch, probe_used, calls
            identity = spec_from_row(row).episode_id
            if unit_complete(row, progress[identity], histories[identity]):
                return
            async with episode_slots:
                store = stores[row['pair_id']]
                def envelope(attempt):
                    return {**asdict(attempt), 'schema_version': 1, 'study': 'study2',
                            'record_id': f'{identity}/attempt-{attempt.attempt_number:04d}',
                            'pair_id': row['pair_id'], 'manifest_sha256': manifest_hash,
                            'episode_sha256': row['episode_sha256'], 'source_sha256': row['source_sha256'],
                            'run_id': run_id, 'runner_policy': asdict(policy), **provenance}
                def start(attempt, checkpoint):
                    nonlocal dispatch, probe_used, calls
                    dispatch += 1
                    base = envelope(attempt)
                    base['dispatch_sequence'] = dispatch
                    store.reserve(seal(base))
                    calls += 1
                    if row['is_probe']:
                        probe_used += 1
                def finish(attempt, checkpoint):
                    base = envelope(attempt)
                    base['dispatch_sequence'] = store.pending[base['record_id']]['dispatch_sequence']
                    record = seal(base)
                    store.append(record)
                    histories[identity].append(record)
                    progress[identity] = checkpoint
                result = await run_episode(
                    config, spec_from_row(row), clients, progress=progress[identity], policy=policy, sleep=sleep,
                    on_start=start, on_attempt=finish, acquire=acquire, release=release,
                    single_turn=row['is_probe'], can_start=(lambda: probe_used < probe_cap) if row['is_probe'] else None,
                )
                replayed = reconstruct(row, histories[identity], manifest_hash)
                if result.attempts and content_hash(asdict(replayed)) != content_hash(asdict(result.progress)):
                    raise ValueError('Engine progress differs from independent attempt replay.')
                progress[identity] = replayed
                if unit_complete(row, replayed, histories[identity]):
                    (probe_store if row['is_probe'] else episode_store).append(
                        terminal_record(row, replayed, histories[identity], manifest_hash))
                elif result.attempts and result.attempts[-1].api_error is not None and not result.attempts[-1].api_error['retryable']:
                    raise ValueError('Nonretryable API error stopped the collection; inspect safe attempt metadata.')
        tasks = [asyncio.create_task(execute(row)) for row in rows]
        try:
            await asyncio.gather(*tasks)
        except BaseException:
            for task in tasks:
                task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)
            raise
        unfinished = [identity for identity, row in row_map.items() if not unit_complete(row, progress[identity], histories[identity])]
        summary = {'planned_units': len(rows), 'already_final': already, 'new_calls': calls,
                   'recovered_attempts': len(additions), 'repaired_terminal_records': len(missing_episodes) + len(missing_probes),
                   'episodes_complete': len(episode_store.records), 'probes_complete': len(probe_store.records),
                   'probe_attempts_used': probe_used, 'probe_attempt_cap': probe_cap,
                   'unfinished_unit_ids': unfinished, 'manifest_sha256': manifest_hash,
                   'pair_log_bytes': {pair: store.path.stat().st_size if store.path.exists() else 0 for pair, store in stores.items()}}
        # This convenience summary is replaceable; attempts/terminal records are append-only.
        (directory / 'run_summary.json').write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
        return summary
