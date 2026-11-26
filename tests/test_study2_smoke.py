"""Verify paid-smoke gates, persistent budgets, drift halts, and .env-only loading offline."""

import asyncio
import json
from dataclasses import replace
from pathlib import Path

import pytest

from kinloyalty.clients.base import ClientError
from kinloyalty.logs import read_jsonl
from kinloyalty.negotiation.authorization import ModelDriftError, SmokeAuthorization, study1_versions
from kinloyalty.negotiation.collection import replay_collection
from kinloyalty.negotiation.config import config_from_snapshot
from kinloyalty.negotiation.engine import run_episode
from kinloyalty.negotiation.manifest import build_manifest, spec_from_row, write_manifest
from kinloyalty.negotiation.mock import NegotiationMockClient
import kinloyalty.negotiation.runner as runner


ROOT = Path(__file__).resolve().parents[1]


class FakeLive(NegotiationMockClient):
    """Use synthetic replies behind a live-mode flag; no SDK/network is invoked."""

    execution_mode = 'live'

    async def complete(self, request):
        return replace(await super().complete(request), returned_model_version=request.api_model_id)


@pytest.fixture
def setup(tmp_path, monkeypatch):
    rows = build_manifest(ROOT / 'configs/study2.yaml', 'smoke')
    manifest = tmp_path / 'manifest.jsonl'
    write_manifest(rows, manifest)
    authorization = SmokeAuthorization(study1_versions(ROOT / 'preregistration/study1.md'))
    monkeypatch.setattr(runner, 'collect_provenance', lambda: {'git_commit': 'offline-clean-fixture', 'code_dirty': False,
                                                            'package_version': 'fixture', 'sdk_versions': {}})
    return rows, manifest, tmp_path / 'run', authorization


def _clients(rows, client):
    return {model: client for model in config_from_snapshot(rows[0]['snapshot']).model_order}


async def _no_sleep(delay):
    pass


def test_live_requires_authorization_clean_code_and_exact_phase(setup, monkeypatch) -> None:
    rows, manifest, directory, authorization = setup
    client = FakeLive()
    with pytest.raises(ValueError, match='explicit smoke authorization'):
        asyncio.run(runner.run_manifest(manifest, directory, _clients(rows, client)))
    monkeypatch.setattr(runner, 'collect_provenance', lambda: {'code_dirty': True, 'git_commit': 'fixture'})
    with pytest.raises(ValueError, match='clean committed'):
        asyncio.run(runner.run_manifest(manifest, directory, _clients(rows, client), authorization=authorization))
    with pytest.raises(ValueError, match='approved smoke budgets'):
        replace(authorization, natural_attempt_cap=385).contract('manifest')
    assert not client.requests


def test_live_mode_logs_replay_and_contract_cannot_reset(setup) -> None:
    rows, manifest, directory, authorization = setup
    summary = asyncio.run(runner.run_manifest(manifest, directory, _clients(rows, FakeLive()), authorization=authorization))
    assert summary['execution_mode'] == 'live' and summary['episodes_complete'] == 4 and summary['probes_complete'] == 16
    assert summary['natural_attempts_used'] == 24 and summary['probe_attempts_used'] == 16
    assert replay_collection(manifest, directory)['episodes_verified'] == 4
    assert all(not record['synthetic'] for record in read_jsonl(directory / 'episodes.jsonl'))
    changed = replace(authorization, expected_versions={key: 'changed' for key in authorization.expected_versions})
    client = FakeLive()
    with pytest.raises(ValueError, match='cannot reset'):
        asyncio.run(runner.run_manifest(manifest, directory, _clients(rows, client), authorization=changed))
    assert not client.requests


def test_drift_response_is_preserved_and_blocks_further_dispatch(setup) -> None:
    rows, manifest, directory, authorization = setup
    class Drift(FakeLive):
        async def complete(self, request):
            return replace(await super().complete(request), returned_model_version=request.api_model_id + '-changed')
    client = Drift()
    with pytest.raises(ModelDriftError):
        asyncio.run(runner.run_manifest(manifest, directory, _clients(rows, client), authorization=authorization))
    records = [record for path in (directory / 'turns').glob('*.jsonl') for record in read_jsonl(path)]
    assert any(record['model_drift'] and record['response'] is not None for record in records)
    assert len(client.requests) <= 4
    assert json.loads((directory / 'run_summary.json').read_text())['status'] == 'halted_model_drift'
    replay_collection(manifest, directory)
    clean = FakeLive()
    with pytest.raises(ModelDriftError, match='already records'):
        asyncio.run(runner.run_manifest(manifest, directory, _clients(rows, clean), authorization=authorization))
    assert not clean.requests


def test_natural_budget_persists_across_retries_and_twenty_four_resumes(setup) -> None:
    rows, manifest, directory, authorization = setup
    class NaturalErrors(FakeLive):
        async def complete(self, request):
            if ':probe:' not in request.trial_id:
                raise ClientError('timeout')
            return await super().complete(request)
    for _ in range(24):
        summary = asyncio.run(runner.run_manifest(manifest, directory, _clients(rows, NaturalErrors()),
                                                  authorization=authorization, sleep=_no_sleep))
    assert summary['natural_attempts_used'] == 384 and summary['probe_attempts_used'] == 16
    client = FakeLive()
    resumed = asyncio.run(runner.run_manifest(manifest, directory, _clients(rows, client), authorization=authorization))
    assert resumed['new_calls'] == 0 and len(resumed['unfinished_unit_ids']) == 4 and not client.requests
    replay_collection(manifest, directory)


def test_denied_next_turn_does_not_invent_a_pending_call(setup) -> None:
    rows, _, _, _ = setup
    row = next(row for row in rows if not row['is_probe'])
    spec = spec_from_row(row)
    client = NegotiationMockClient()
    result = asyncio.run(run_episode(config_from_snapshot(row['snapshot']), spec, _clients(rows, client),
                                    can_start=lambda: len(client.requests) < 2))
    assert len(result.progress.state.turns) == 2 and result.progress.pending_request is None


def test_credentials_are_loaded_with_process_environment_excluded(monkeypatch) -> None:
    import kinloyalty.negotiation.smoke as smoke
    import kinloyalty.clients.anthropic as anthropic
    import kinloyalty.clients.openai as openai
    import kinloyalty.clients.google as google
    import kinloyalty.clients.moonshot as moonshot
    rows = build_manifest(ROOT / 'configs/study2.yaml', 'smoke')
    from kinloyalty.negotiation.manifest import initial_state
    from kinloyalty.negotiation.requests import build_turn_request
    config = config_from_snapshot(rows[0]['snapshot'])
    requests = [build_turn_request(config, spec_from_row(row), initial_state(row, config)) for row in rows]
    observed = []
    def fake_loader(providers, env_path, *, environ):
        observed.append((env_path, environ))
        return {provider: 'offline-fake-key' for provider in providers}
    monkeypatch.setattr(smoke, 'load_api_keys', fake_loader)
    for module, name in [(anthropic, 'AnthropicClient'), (openai, 'OpenAIClient'), (google, 'GoogleClient'), (moonshot, 'MoonshotClient')]:
        monkeypatch.setattr(module, name, lambda **kwargs: object())
    smoke.create_live_clients(requests, ROOT / '.env')
    assert observed == [(ROOT / '.env', {})]


def test_smoke_report_contains_live_metadata_and_all_four_transcript_prefixes(setup, tmp_path) -> None:
    from kinloyalty.negotiation.smoke_report import write_smoke_report
    rows, manifest, directory, authorization = setup
    asyncio.run(runner.run_manifest(manifest, directory, _clients(rows, FakeLive()), authorization=authorization))
    output = tmp_path / 'report'
    audit = write_smoke_report(manifest, directory, output)
    assert audit['execution_mode'] == 'live' and all(audit['checks'].values())
    text = (output / 'smoke-report.md').read_text()
    for role in ('buyer', 'seller'):
        for k in (11, 12):
            assert f'### {role}, message {k}' in text
    assert json.loads((output / 'probe-report.json').read_text())['synthetic'] is False


def test_halted_drift_collection_still_produces_a_report(setup, tmp_path) -> None:
    from kinloyalty.negotiation.smoke_report import write_smoke_report
    rows, manifest, directory, authorization = setup
    class Drift(FakeLive):
        async def complete(self, request):
            return replace(await super().complete(request), returned_model_version='changed')
    with pytest.raises(ModelDriftError):
        asyncio.run(runner.run_manifest(manifest, directory, _clients(rows, Drift()), authorization=authorization))
    audit = write_smoke_report(manifest, directory, tmp_path / 'report')
    assert audit['model_drift_responses'] >= 1 and not audit['checks']['no_model_drift']
    assert audit['status'] == 'halted_model_drift'
