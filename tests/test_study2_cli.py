"""Check the additive CLI, privacy-preserving raw-price logs, and permit timing."""

import asyncio
import json
import subprocess
import sys
from pathlib import Path

import pytest

from kinloyalty.cli import main
from kinloyalty.clients.base import ModelResponse
from kinloyalty.logs import read_jsonl
from kinloyalty.negotiation.config import config_from_snapshot
from kinloyalty.negotiation.engine import run_episode
from kinloyalty.negotiation.manifest import build_manifest, spec_from_row, write_manifest
from kinloyalty.negotiation.mock import NegotiationMockClient
from kinloyalty.negotiation.runner import run_manifest
from kinloyalty.runner import RunnerPolicy


ROOT = Path(__file__).resolve().parents[1]


def test_installed_cli_manifest_run_resume_replay_and_probe_report(tmp_path: Path) -> None:
    executable = Path(sys.executable).parent / 'kinloyalty'
    manifest, directory, report = tmp_path / 'smoke.jsonl', tmp_path / 'run', tmp_path / 'probes.json'
    def invoke(*arguments):
        return subprocess.run([str(executable), 'study2', *map(str, arguments)], capture_output=True, text=True, check=True)
    invoke('manifest', '--phase', 'smoke', '--output', manifest)
    first = json.loads(invoke('run', '--manifest', manifest, '--directory', directory, '--client', 'mock').stdout)
    second = json.loads(invoke('run', '--manifest', manifest, '--directory', directory, '--client', 'mock').stdout)
    replay = json.loads(invoke('replay', '--manifest', manifest, '--directory', directory).stdout)
    invoke('probe-report', '--manifest', manifest, '--directory', directory, '--output', report)
    assert first['episodes_complete'] == replay['episodes_verified'] == 4
    assert second['new_calls'] == 0 and replay['probes_verified'] == 16
    assert len(json.loads(report.read_text())['probes']) == 16
    rejected = subprocess.run([str(executable), 'study2', 'run', '--manifest', str(manifest), '--directory', str(directory), '--client', 'live'],
                              capture_output=True, text=True)
    assert rejected.returncode == 2


def test_root_dispatch_leaves_study1_cli_entry_points_intact(capsys) -> None:
    with pytest.raises(SystemExit) as result:
        main(['study2', '--help'])
    assert result.value.code == 0 and 'probe-report' in capsys.readouterr().out
    with pytest.raises(SystemExit) as result:
        main(['--help'])
    help_text = capsys.readouterr().out
    assert result.value.code == 0 and 'study2' in help_text and 'simulate-study1' in help_text


def test_arbitrary_supplied_acceptance_price_is_preserved_and_flagged(tmp_path: Path) -> None:
    rows = build_manifest(ROOT / 'configs/study2.yaml', 'smoke')
    target = next(spec_from_row(row) for row in rows if not row['is_probe'])
    manifest = tmp_path / 'manifest.jsonl'
    write_manifest(rows, manifest)
    raw_price = {'headers': {'not_a_transport_header': 'model reply content'}}
    client = NegotiationMockClient(scripts={
        target.episode_id + '/message-01': [ModelResponse(json.dumps({'message': 'Offer', 'action': 'offer', 'price': 500}))],
        target.episode_id + '/message-02': [ModelResponse(json.dumps({'message': 'Agreed', 'action': 'accept', 'price': raw_price}))],
    })
    clients = {model: client for model in config_from_snapshot(rows[0]['snapshot']).model_order}
    directory = tmp_path / 'run'
    asyncio.run(run_manifest(manifest, directory, clients))
    episode = next(record for record in read_jsonl(directory / 'episodes.jsonl') if record['episode_id'] == target.episode_id)
    assert episode['deal_price'] == 500 and episode['accept_price_mismatch']
    assert json.loads(episode['accept_supplied_price_json']) == raw_price
    assert episode['buyer_mandate_violation'] and episode['buyer_surplus_share'] < 0


def test_queue_wait_occurs_before_api_timeout() -> None:
    row = next(row for row in build_manifest(ROOT / 'configs/study2.yaml', 'smoke') if not row['is_probe'])
    config, spec = config_from_snapshot(row['snapshot']), spec_from_row(row)
    client = NegotiationMockClient(strategy='walk_away')
    released = []
    async def acquire(model):
        await asyncio.sleep(.04)
    policy = RunnerPolicy(timeout_seconds=.02)
    result = asyncio.run(run_episode(config, spec, {spec.buyer_model: client}, policy=policy,
                                    acquire=acquire, release=lambda model: released.append(model)))
    assert result.progress.state.outcome.kind == 'walk_away_impasse'
    assert result.attempts[0].api_error is None and released == [spec.buyer_model]


def test_mock_runner_refuses_real_study_directories(tmp_path: Path) -> None:
    rows = build_manifest(ROOT / 'configs/study2.yaml', 'smoke')
    manifest = tmp_path / 'manifest.jsonl'
    write_manifest(rows, manifest)
    client = NegotiationMockClient()
    clients = {model: client for model in config_from_snapshot(rows[0]['snapshot']).model_order}
    for relative in ('data/study1', 'results/study1', 'prompts/study1', 'data/study2/main', 'data/study2/smoke', 'preregistration'):
        path = ROOT / relative
        existed = path.exists()
        with pytest.raises(ValueError, match='outside real-study'):
            asyncio.run(run_manifest(manifest, path, clients))
        assert path.exists() == existed
    assert not client.requests
