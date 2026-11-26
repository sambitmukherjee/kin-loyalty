"""Test main execution/provenance and non-outcome reports without real API calls."""
import asyncio
from dataclasses import replace
import json
from pathlib import Path
import pytest
from kinloyalty.clients.base import ClientError, ModelResponse
from kinloyalty.logs import read_jsonl
from kinloyalty.negotiation.authorization import MAIN_MANIFEST_SHA256, MainAuthorization, ModelDriftError, REGISTRATION_COMMIT
from kinloyalty.negotiation.collection import replay_collection
from kinloyalty.negotiation.config import config_from_snapshot
from kinloyalty.negotiation.history import reconstruct, seal
from kinloyalty.negotiation.main_report import write_main_report
from kinloyalty.negotiation.manifest import read_manifest
from kinloyalty.negotiation.mock import NegotiationMockClient
import kinloyalty.negotiation.runner as runner

ROOT = Path(__file__).resolve().parents[1]
EXECUTION = 'e' * 40

class FakeLive(NegotiationMockClient):
    """Exercise the live control path with synthetic replies, never an SDK."""
    execution_mode = 'live'
    async def complete(self, request):
        return replace(await super().complete(request), returned_model_version=request.api_model_id)

@pytest.fixture
def setup(tmp_path, monkeypatch):
    manifest = ROOT / 'data/study2/main/manifest.jsonl'
    rows = read_manifest(manifest)
    config = config_from_snapshot(rows[0]['snapshot'])
    versions = {model['api_model_id']: model['api_model_id'] for model in config.models.values()}
    monkeypatch.setattr(runner, 'collect_provenance', lambda: {'git_commit': EXECUTION, 'code_dirty': False,
                                                            'package_version': 'fixture', 'sdk_versions': {}})
    return rows, manifest, tmp_path / 'run', MainAuthorization(versions, EXECUTION)

def clients(rows, client):
    return {model: client for model in config_from_snapshot(rows[0]['snapshot']).model_order}

async def no_sleep(delay):
    pass

def test_main_contract_cannot_change_registration_manifest_or_add_probes(setup):
    rows, manifest, directory, authorization = setup
    for changes in ({'registration_git_commit': 'a' * 40}, {'phase': 'pilot'}, {'probe_attempt_cap': 1}, {'natural_attempt_cap': 92160}):
        with pytest.raises(ValueError, match='Main authorization'):
            replace(authorization, **changes).contract(MAIN_MANIFEST_SHA256)
    with pytest.raises(ValueError, match='Main authorization'):
        authorization.contract('wrong-manifest')
    client = FakeLive(strategy='walk_away')
    from kinloyalty.negotiation.authorization import PilotAuthorization
    with pytest.raises(ValueError, match='exact smoke or pilot phase'):
        asyncio.run(runner.run_manifest(manifest, directory, clients(rows, client), authorization=PilotAuthorization(authorization.expected_versions)))
    assert not client.requests and not directory.exists()

def test_main_all_records_have_both_hashes_replay_and_report_no_outcomes(setup, tmp_path, monkeypatch):
    rows, manifest, directory, authorization = setup
    identity = rows[0]['spec']['episode_id']
    client = FakeLive(strategy='walk_away', scripts={identity + '/message-01': [ModelResponse('invalid'), ModelResponse('invalid')]})
    summary = asyncio.run(runner.run_manifest(manifest, directory, clients(rows, client), authorization=authorization))
    assert summary['episodes_complete'] == 960 and not summary['unfinished_unit_ids']
    records = [r for path in (directory / 'turns').glob('*.jsonl') for r in read_jsonl(path)]
    episodes = read_jsonl(directory / 'episodes.jsonl')
    for record in [*records, *episodes]:
        assert record['registration_git_commit'] == REGISTRATION_COMMIT
        assert record['execution_git_commit'] == record['git_commit'] == EXECUTION
    report = write_main_report(manifest, directory, tmp_path / 'report')
    assert report['completed'] == 960 and report['exclusions'] == report['reasks'] == 1
    assert len(report['per_pair_condition']) == 48
    assert all(row['planned'] == row['completed'] == 20 for row in report['per_pair_condition'])
    assert report['replay']['attempts_verified'] == 961 and report['both_hashes_on_every_turn_and_episode']
    forbidden = {'deal_rate', 'surplus_share', 'buyer_surplus_share', 'price', 'deal_price', 'outcome', 'mandate_violations'}
    def check(value):
        if isinstance(value, dict):
            assert not forbidden.intersection(value)
            for child in value.values(): check(child)
        elif isinstance(value, list):
            for child in value: check(child)
    check(report)
    assert not report['inference_run'] and not report['outcome_statistics_reported']
    history = [r for r in records if r['episode_id'] == identity]
    altered = [{**record, 'registration_git_commit': 'a' * 40} for record in history]
    with pytest.raises(ValueError, match='provenance'):
        reconstruct(rows[0], [seal(record) for record in altered], summary['manifest_sha256'], execution_mode='live')
    monkeypatch.setattr(runner, 'collect_provenance', lambda: {'git_commit': 'f' * 40, 'code_dirty': False})
    different = FakeLive(strategy='walk_away')
    with pytest.raises(ValueError, match='cannot reset'):
        asyncio.run(runner.run_manifest(manifest, directory, clients(rows, different),
                    authorization=replace(authorization, execution_git_commit='f' * 40)))
    assert not different.requests

def test_main_resumes_exhausted_errors_and_reports_episode_resumption(setup, tmp_path):
    rows, manifest, directory, authorization = setup
    identity = rows[0]['spec']['episode_id']
    class Errors(FakeLive):
        async def complete(self, request):
            if request.trial_id.startswith(identity + '/'):
                raise ClientError('timeout')
            return await super().complete(request)
    first = asyncio.run(runner.run_manifest(manifest, directory, clients(rows, Errors(strategy='walk_away')),
                                           authorization=authorization, sleep=no_sleep))
    assert first['episodes_complete'] == 959 and first['unfinished_unit_ids'] == [identity]
    resumed = asyncio.run(runner.run_manifest(manifest, directory, clients(rows, FakeLive(strategy='walk_away')),
                                             authorization=authorization, sleep=no_sleep))
    assert resumed['new_calls'] == 1 and resumed['episodes_complete'] == 960
    report = write_main_report(manifest, directory, tmp_path / 'report')
    assert report['api_errors'] == 4 and report['resumptions'] == report['resumed_episodes'] == 1
    assert report['collection_invocations_with_attempts'] == 2 and not report['unfinished']
    assert replay_collection(manifest, directory)['attempts_verified'] == 964

def test_main_drift_is_preserved_and_blocks_resume(setup, tmp_path):
    rows, manifest, directory, authorization = setup
    class Drift(FakeLive):
        async def complete(self, request):
            return replace(await super().complete(request), returned_model_version='changed')
    client = Drift(strategy='walk_away')
    with pytest.raises(ModelDriftError):
        asyncio.run(runner.run_manifest(manifest, directory, clients(rows, client), authorization=authorization))
    assert len(client.requests) <= 4
    report = write_main_report(manifest, directory, tmp_path / 'report')
    assert report['model_drift_responses'] > 0 and report['unfinished'] > 0
    clean = FakeLive(strategy='walk_away')
    with pytest.raises(ModelDriftError, match='already records'):
        asyncio.run(runner.run_manifest(manifest, directory, clients(rows, clean), authorization=authorization))
    assert not clean.requests

def test_main_entry_rejects_dirty_checkout_before_keys(setup, monkeypatch):
    _, manifest, directory, _ = setup
    import kinloyalty.negotiation.main_run as main
    monkeypatch.setattr(main, 'collect_provenance', lambda: {'git_commit': EXECUTION, 'code_dirty': True})
    monkeypatch.setattr(main, 'create_live_clients', lambda *_: pytest.fail('Credentials loaded before clean-code check.'))
    with pytest.raises(ValueError, match='same clean committed'):
        asyncio.run(main.run_live_main(manifest, directory, ROOT / '.env', EXECUTION))

def test_main_manifest_mismatch_stops_before_credentials(setup, tmp_path, monkeypatch):
    import kinloyalty.negotiation.main_run as main
    monkeypatch.setattr(main, 'collect_provenance', lambda: {'git_commit': EXECUTION, 'code_dirty': False})
    monkeypatch.setattr(main, 'create_live_clients', lambda *_: pytest.fail('Credentials loaded for a changed manifest.'))
    changed = tmp_path / 'changed.jsonl'
    changed.write_bytes(b'not the registered manifest')
    with pytest.raises(ValueError, match='SHA-256 differs'):
        asyncio.run(main.run_live_main(changed, tmp_path / 'output', ROOT / '.env', EXECUTION))

def test_main_entry_automatically_resumes_until_complete(setup, monkeypatch):
    _, manifest, directory, authorization = setup
    import kinloyalty.negotiation.main_run as main
    lock = json.loads((ROOT / 'preregistration/study2-lock.json').read_text())
    monkeypatch.setattr(main, 'verify_main_sources', lambda *_: (lock, {'git_commit': EXECUTION, 'code_dirty': False}))
    class Router:
        closed = False
        async def aclose(self): self.closed = True
    router = Router()
    monkeypatch.setattr(main, 'create_live_clients', lambda *_: router)
    calls = []
    async def run(*args, **kwargs):
        calls.append(kwargs['authorization'])
        final = len(calls) == 2
        return {'status': 'complete' if final else 'unfinished', 'episodes_complete': 960 if final else 959,
                'new_calls': 1, 'natural_attempts_used': len(calls), 'unfinished_unit_ids': [] if final else ['pending']}
    monkeypatch.setattr(main, 'run_manifest', run)
    result = asyncio.run(main.run_live_main(manifest, directory, ROOT / '.env', EXECUTION))
    assert result['episodes_complete'] == 960 and len(calls) == 2 and router.closed
    assert all(call.registration_git_commit == REGISTRATION_COMMIT and call.execution_git_commit == EXECUTION for call in calls)
