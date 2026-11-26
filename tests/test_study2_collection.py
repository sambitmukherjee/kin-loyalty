"""Check durable per-pair collection, replay, locking, budgets, and crash recovery."""

import asyncio
import json
import subprocess
import sys
import time
from collections import Counter, defaultdict
from copy import deepcopy
from dataclasses import asdict
from pathlib import Path

import pytest

from kinloyalty.clients.base import ClientError, ModelResponse
from kinloyalty.logs import AttemptLog, json_line, read_jsonl
from kinloyalty.negotiation.collection import replay_collection, turn_path
from kinloyalty.negotiation.config import config_from_snapshot
from kinloyalty.negotiation.history import seal
from kinloyalty.negotiation.manifest import build_manifest, read_manifest, spec_from_row, write_manifest
from kinloyalty.negotiation.mock import NegotiationMockClient
from kinloyalty.negotiation.probes import write_probe_report
from kinloyalty.negotiation.runner import run_manifest


ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def plan(tmp_path: Path):
    rows = build_manifest(ROOT / 'configs/study2.yaml', 'smoke')
    manifest = tmp_path / 'manifest.jsonl'
    write_manifest(rows, manifest)
    return rows, manifest, tmp_path / 'collection'


def _clients(rows, client=None):
    models = config_from_snapshot(rows[0]['snapshot']).model_order
    return {model: client if client is not None else NegotiationMockClient() for model in models}


async def _no_sleep(delay):
    pass


def test_full_synthetic_collection_and_independent_replay(tmp_path: Path) -> None:
    rows = build_manifest(ROOT / 'configs/study2.yaml', 'synthetic', scenario_seed=111, order_seed=112, swapped_seed=113)
    manifest = tmp_path / 'synthetic.jsonl'
    write_manifest(rows, manifest)
    directory = tmp_path / 'collection'
    summary = asyncio.run(run_manifest(manifest, directory, _clients(rows)))
    assert summary['episodes_complete'] == 960 and summary['probes_complete'] == 0
    assert summary['new_calls'] == 6240 and not summary['unfinished_unit_ids']
    assert len(summary['pair_log_bytes']) == 16 and max(summary['pair_log_bytes'].values()) < 50_000_000
    replay = replay_collection(manifest, directory)
    assert replay['episodes_verified'] == 960 and replay['attempts_verified'] == 6240
    before = {path: path.read_bytes() for path in directory.rglob('*.jsonl')}
    again = asyncio.run(run_manifest(manifest, directory, _clients(rows)))
    assert again['already_final'] == 960 and again['new_calls'] == 0
    assert all(path.read_bytes() == data for path, data in before.items())


def test_smoke_probes_are_unscored_and_report_exact_transcripts(plan, tmp_path: Path) -> None:
    rows, manifest, directory = plan
    summary = asyncio.run(run_manifest(manifest, directory, _clients(rows)))
    assert summary['episodes_complete'] == 4 and summary['probes_complete'] == 16
    assert summary['probe_attempts_used'] == 16
    episodes = read_jsonl(directory / 'episodes.jsonl')
    probes = read_jsonl(directory / 'probes.jsonl')
    assert all(not record['is_probe'] for record in episodes)
    assert all(record['is_probe'] and 'buyer_surplus_share' not in record for record in probes)
    assert set(record['action'] for record in probes if record['message_number'] == 12) <= {'accept', 'walk_away'}
    report = tmp_path / 'probe-report.json'
    write_probe_report(manifest, directory, report)
    data = json.loads(report.read_text())
    assert data['inference_eligible'] is False and len(data['probes']) == 16
    planned = {row['spec']['episode_id']: row for row in rows}
    for probe in data['probes']:
        assert probe['user_message'] == planned[probe['episode_id']]['probe_request']['user_message']
        assert len(probe['initial_turns']) == probe['message_number'] - 1


def test_probe_budget_and_reasks_persist_across_resumes(plan) -> None:
    rows, manifest, directory = plan
    scripts = {row['probe_request']['trial_id']: [ModelResponse('invalid'), ModelResponse('invalid re-ask')]
               for row in rows if row['is_probe']}
    client = NegotiationMockClient(scripts=scripts)
    summary = asyncio.run(run_manifest(manifest, directory, _clients(rows, client)))
    assert summary['probe_attempts_used'] == 32 and summary['probes_complete'] == 16
    assert all(record['status'] == 'excluded' and record['reasks'] == 1 for record in read_jsonl(directory / 'probes.jsonl'))
    again = asyncio.run(run_manifest(manifest, directory, _clients(rows)))
    assert again['probe_attempts_used'] == 32 and again['new_calls'] == 0


def test_probe_api_failures_consume_global_cap_without_reset(plan) -> None:
    rows, manifest, directory = plan
    class FailingProbes(NegotiationMockClient):
        async def complete(self, request):
            if ':probe:' in request.trial_id:
                raise ClientError('server_error')
            return await super().complete(request)
    summary = asyncio.run(run_manifest(manifest, directory, _clients(rows, FailingProbes()), sleep=_no_sleep))
    assert summary['probe_attempts_used'] == 32 and summary['probes_complete'] == 0
    assert summary['episodes_complete'] == 4 and len(summary['unfinished_unit_ids']) == 16
    resumed = asyncio.run(run_manifest(manifest, directory, _clients(rows), sleep=_no_sleep))
    assert resumed['new_calls'] == 0 and resumed['probe_attempts_used'] == 32


def test_per_model_global_and_per_episode_concurrency_limits(plan) -> None:
    rows, manifest, directory = plan
    active, peak = Counter(), Counter()
    class Observed(NegotiationMockClient):
        async def complete(self, request):
            unit = request.trial_id.rsplit('/message-', 1)[0]
            keys = ['global', request.api_model_id, unit]
            for key in keys:
                active[key] += 1
                peak[key] = max(peak[key], active[key])
            try:
                await asyncio.sleep(.002)
                return await super().complete(request)
            finally:
                for key in keys:
                    active[key] -= 1
    asyncio.run(run_manifest(manifest, directory, _clients(rows, Observed())))
    assert 2 <= peak['global'] <= 4
    assert all(value == 1 for key, value in peak.items() if key != 'global')
    assert not any(active.values())


@pytest.mark.parametrize('change', ['request', 'validation', 'terminal', 'duplicate'])
def test_tampering_is_rejected_before_any_new_call(plan, change: str) -> None:
    rows, manifest, directory = plan
    asyncio.run(run_manifest(manifest, directory, _clients(rows)))
    if change in {'request', 'validation'}:
        path = next((directory / 'turns').glob('*.jsonl'))
        records = read_jsonl(path)
        if change == 'request':
            records[0]['request']['user_message'] = 'tampered'
        else:
            records[0]['validation']['valid'] = False
        records[0] = seal(records[0])
        path.write_text(''.join(map(json_line, records)))
    else:
        path = directory / 'episodes.jsonl'
        records = read_jsonl(path)
        if change == 'terminal':
            records[0]['deal_price'] = -1
            records[0] = seal(records[0])
        else:
            records.append(records[0])
        path.write_text(''.join(map(json_line, records)))
    client = NegotiationMockClient()
    with pytest.raises(ValueError):
        asyncio.run(run_manifest(manifest, directory, _clients(rows, client)))
    with pytest.raises(ValueError):
        replay_collection(manifest, directory)
    assert not client.requests


def test_partial_log_tail_and_writer_lock_fail_without_calls(plan) -> None:
    rows, manifest, directory = plan
    client = NegotiationMockClient()
    with AttemptLog(directory / 'episodes.jsonl'):
        with pytest.raises(BlockingIOError):
            asyncio.run(run_manifest(manifest, directory, _clients(rows, client)))
    assert not client.requests
    asyncio.run(run_manifest(manifest, directory, _clients(rows)))
    path = next((directory / 'turns').glob('*.jsonl'))
    damaged = path.read_bytes() + b'{'
    path.write_bytes(damaged)
    with pytest.raises(ValueError, match='Incomplete JSONL'):
        asyncio.run(run_manifest(manifest, directory, _clients(rows, client)))
    assert path.read_bytes() == damaged and not client.requests


def test_missing_terminal_is_repaired_once_and_stale_pending_is_deduplicated(plan) -> None:
    rows, manifest, directory = plan
    asyncio.run(run_manifest(manifest, directory, _clients(rows)))
    episodes = directory / 'episodes.jsonl'
    records = read_jsonl(episodes)
    episodes.write_text(''.join(map(json_line, records[1:])))
    path = next((directory / 'turns').glob('*.jsonl'))
    before = path.read_bytes()
    pending = deepcopy(read_jsonl(path)[0])
    pending.update(response=None, validation=None, api_error=None, is_final_for_turn=False,
                   excluded=False, accept_price_mismatch=False, completed_at_utc=None, latency_seconds=None)
    path.with_name(path.name + '.pending.json').write_text(json_line({pending['record_id']: seal(pending)}))
    with pytest.raises(ValueError, match='Pending calls'):
        replay_collection(manifest, directory)
    summary = asyncio.run(run_manifest(manifest, directory, _clients(rows)))
    assert summary['new_calls'] == 0 and summary['recovered_attempts'] == 0
    assert summary['repaired_terminal_records'] == 1 and path.read_bytes() == before
    assert len(read_jsonl(episodes)) == 4
    assert replay_collection(manifest, directory)['episodes_verified'] == 4


@pytest.mark.parametrize('reask', [False, True])
def test_hard_kill_mid_episode_recovers_pending_and_invalid_count(plan, tmp_path: Path, reask: bool) -> None:
    rows, manifest, directory = plan
    target = next(row['spec']['episode_id'] for row in rows if not row['is_probe'])
    ready = tmp_path / 'ready'
    code = '''
import asyncio, sys
from pathlib import Path
from kinloyalty.clients.base import ModelResponse
from kinloyalty.negotiation.config import config_from_snapshot
from kinloyalty.negotiation.manifest import read_manifest
from kinloyalty.negotiation.mock import NegotiationMockClient
from kinloyalty.negotiation.runner import run_manifest
manifest, directory, ready, target, reask = sys.argv[1:]
class Pausing(NegotiationMockClient):
    target_calls = 0
    async def complete(self, request):
        if request.trial_id == target + '/message-03':
            self.target_calls += 1
            if reask == '1' and self.target_calls == 1:
                return ModelResponse('invalid first response')
            Path(ready).write_text('ready')
            await asyncio.sleep(3600)
        return await super().complete(request)
rows = read_manifest(manifest)
client = Pausing()
clients = {model: client for model in config_from_snapshot(rows[0]['snapshot']).model_order}
asyncio.run(run_manifest(manifest, directory, clients))
'''
    process = subprocess.Popen([sys.executable, '-c', code, str(manifest), str(directory), str(ready), target, str(int(reask))],
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        deadline = time.monotonic() + 15
        while not ready.exists() and process.poll() is None and time.monotonic() < deadline:
            time.sleep(.02)
        assert ready.exists(), process.communicate(timeout=2)
    finally:
        if process.poll() is None:
            process.kill()
        process.communicate(timeout=5)
    with pytest.raises(ValueError, match='Pending calls'):
        replay_collection(manifest, directory)
    scripts = {target + '/message-03': [ModelResponse('invalid re-ask response')]} if reask else None
    client = NegotiationMockClient(scripts=scripts)
    summary = asyncio.run(run_manifest(manifest, directory, _clients(rows, client)))
    assert summary['recovered_attempts'] >= 1 and not summary['unfinished_unit_ids']
    episode = next(record for record in read_jsonl(directory / 'episodes.jsonl') if record['episode_id'] == target)
    assert episode['outcome'] == ('excluded' if reask else 'deal')
    if reask:
        assert episode['messages_used'] == 2 and episode['exclusion_message_number'] == 3 and episode['reasks'] == 1
    assert replay_collection(manifest, directory)['episodes_verified'] == 4
