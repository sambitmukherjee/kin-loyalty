"""Check approved pilot execution/reporting with synthetic replies and no network."""

import asyncio
import csv
import json
from dataclasses import replace
from pathlib import Path

import pytest

from kinloyalty.clients.base import ClientError, ModelResponse
from kinloyalty.logs import read_jsonl
from kinloyalty.negotiation.authorization import ModelDriftError, PilotAuthorization, SmokeAuthorization, study1_versions
from kinloyalty.negotiation.collection import replay_collection
from kinloyalty.negotiation.config import config_from_snapshot
from kinloyalty.negotiation.manifest import build_manifest, write_manifest
from kinloyalty.negotiation.mock import NegotiationMockClient
from kinloyalty.negotiation.pilot_report import write_pilot_report, _outcomes
import kinloyalty.negotiation.runner as runner


ROOT = Path(__file__).resolve().parents[1]


class FakeLive(NegotiationMockClient):
    execution_mode = 'live'

    async def complete(self, request):
        return replace(await super().complete(request), returned_model_version=request.api_model_id)


@pytest.fixture
def setup(tmp_path, monkeypatch):
    rows = build_manifest(ROOT / 'configs/study2.yaml', 'pilot')
    manifest = tmp_path / 'manifest.jsonl'
    write_manifest(rows, manifest)
    monkeypatch.setattr(runner, 'collect_provenance', lambda: {'git_commit': 'offline-clean-fixture', 'code_dirty': False,
                                                            'package_version': 'fixture', 'sdk_versions': {}})
    authorization = PilotAuthorization(study1_versions(ROOT / 'preregistration/study1.md'))
    return rows, manifest, tmp_path / 'run', authorization


def _clients(rows, client):
    return {model: client for model in config_from_snapshot(rows[0]['snapshot']).model_order}


async def _no_sleep(delay):
    pass


def test_pilot_budget_and_phase_are_exact_and_scope_is_separate(setup):
    rows, manifest, directory, authorization = setup
    assert authorization.contract('digest')['natural_attempt_cap'] == 7680
    for change in ({'phase': 'main'}, {'natural_attempt_cap': 7681}, {'probe_attempt_cap': 1}):
        with pytest.raises(ValueError, match='approved pilot budget'):
            replace(authorization, **change).contract('digest')
    client = FakeLive()
    with pytest.raises(ValueError, match='exact smoke or pilot phase'):
        asyncio.run(runner.run_manifest(manifest, directory, _clients(rows, client), authorization=SmokeAuthorization(authorization.expected_versions)))
    assert not client.requests and not directory.exists()


def test_live_pilot_resumes_without_duplicate_calls_and_contract_cannot_reset(setup):
    rows, manifest, directory, authorization = setup
    client = FakeLive(strategy='walk_away')
    summary = asyncio.run(runner.run_manifest(manifest, directory, _clients(rows, client), authorization=authorization))
    assert summary['episodes_complete'] == 80 and summary['natural_attempts_used'] == 80
    assert summary['probe_attempts_used'] == summary['probe_attempt_cap'] == 0
    replay = replay_collection(manifest, directory)
    assert replay['episodes_verified'] == 80 and not replay['unfinished_unit_ids']
    resumed = FakeLive()
    assert asyncio.run(runner.run_manifest(manifest, directory, _clients(rows, resumed), authorization=authorization))['new_calls'] == 0
    changed = replace(authorization, expected_versions={key: 'changed' for key in authorization.expected_versions})
    with pytest.raises(ValueError, match='cannot reset'):
        asyncio.run(runner.run_manifest(manifest, directory, _clients(rows, resumed), authorization=changed))
    assert not resumed.requests


def test_retry_exhaustion_stays_unfinished_and_counters_persist_on_pilot_resume(setup):
    rows, manifest, directory, authorization = setup
    class Errors(FakeLive):
        async def complete(self, request):
            raise ClientError('timeout')
    first = asyncio.run(runner.run_manifest(manifest, directory, _clients(rows, Errors()),
                                           authorization=authorization, sleep=_no_sleep))
    assert first['natural_attempts_used'] == 320 and len(first['unfinished_unit_ids']) == 80
    assert first['episodes_complete'] == 0
    resumed = asyncio.run(runner.run_manifest(manifest, directory, _clients(rows, FakeLive(strategy='walk_away')),
                                             authorization=authorization, sleep=_no_sleep))
    assert resumed['natural_attempts_used'] == 400 and resumed['new_calls'] == 80
    assert resumed['episodes_complete'] == 80 and not resumed['unfinished_unit_ids']
    assert replay_collection(manifest, directory)['attempts_verified'] == 400


def test_pilot_drift_response_is_logged_and_reportable_without_continuing(setup, tmp_path):
    rows, manifest, directory, authorization = setup
    class Drift(FakeLive):
        async def complete(self, request):
            return replace(await super().complete(request), returned_model_version='changed')
    with pytest.raises(ModelDriftError):
        asyncio.run(runner.run_manifest(manifest, directory, _clients(rows, Drift()), authorization=authorization))
    audit = write_pilot_report(manifest, directory, tmp_path / 'report')
    assert audit['model_drift_responses'] >= 1 and not audit['checks']['no_model_drift']
    assert audit['status'] == 'halted_model_drift' and audit['replay']['unfinished_unit_ids']
    clean = FakeLive()
    with pytest.raises(ModelDriftError, match='already records'):
        asyncio.run(runner.run_manifest(manifest, directory, _clients(rows, clean), authorization=authorization))
    assert not clean.requests


def test_pilot_report_is_blind_and_counts_mismatch_by_actual_responding_model(setup, tmp_path):
    rows, manifest, directory, authorization = setup
    target = next(row for row in rows if row['spec']['buyer_model'] != row['spec']['seller_model'])
    bad = next(row for row in rows if row is not target)
    identity = target['spec']['episode_id']
    def reply(action, price):
        return ModelResponse(json.dumps({'message': 'Offline verification', 'action': action, 'price': price}))
    client = FakeLive(strategy='walk_away', scripts={
        identity + '/message-01': [reply('offer', 500)], identity + '/message-02': [reply('accept', 501)],
        bad['spec']['episode_id'] + '/message-01': [ModelResponse('invalid'), ModelResponse('invalid')],
    })
    asyncio.run(runner.run_manifest(manifest, directory, _clients(rows, client), authorization=authorization))
    output = tmp_path / 'report'
    audit = write_pilot_report(manifest, directory, output)
    role = 'seller' if target['spec']['scenario']['opener'] == 'buyer' else 'buyer'
    model = target['spec'][f'{role}_model']
    assert audit['pooled_outcomes']['completed'] == 80 and audit['pooled_outcomes']['exclusions'] == 1
    assert audit['pooled_outcomes']['deals'] == 1 and len(audit['pair_pooled_outcomes']) == 16
    counts = audit['accept_price_mismatches_by_model_role']
    assert sum(row['accept_price_mismatches'] for row in counts) == 1
    assert next(row['accept_price_mismatches'] for row in counts if row['model'] == model and row['role'] == role) == 1
    assert audit['unobserved_validity_cells'] and not audit['checks']['all_model_turn_classes_observed']
    assert not audit['checks']['observed_model_turn_class_validity_above_95_percent']
    assert audit['automatic_fix_threshold'] is None and not audit['inference_performed']
    forbidden = {'condition', 'card_says', 'card_model_text', 'swapped_model', 'permutation_p_value', 'ci_low'}
    def check(value):
        if isinstance(value, dict):
            assert not forbidden.intersection(value)
            for item in value.values():
                check(item)
        elif isinstance(value, list):
            for item in value:
                check(item)
    check(audit)
    for path in output.glob('*.csv'):
        with path.open() as stream:
            assert not forbidden.intersection(next(csv.reader(stream)))
    episodes = read_jsonl(directory / 'episodes.jsonl')
    permuted = [{**episode, 'condition': 'changed', 'card_says': 'changed'} for episode in episodes]
    assert _outcomes(episodes, 80, []) == _outcomes(permuted, 80, [])


def test_live_pilot_entry_rejects_dirty_code_before_loading_credentials(setup, monkeypatch):
    _, manifest, directory, _ = setup
    import kinloyalty.negotiation.pilot as pilot
    monkeypatch.setattr(pilot, 'collect_provenance', lambda: {'code_dirty': True, 'git_commit': 'fixture'})
    monkeypatch.setattr(pilot, 'create_live_clients', lambda *_: pytest.fail('credentials were loaded'))
    with pytest.raises(ValueError, match='Commit live pilot preparation'):
        asyncio.run(pilot.run_live_pilot(manifest, directory, ROOT / '.env'))


def test_report_rejects_smoke_and_inference_still_rejects_pilot(setup, tmp_path):
    _, manifest, directory, _ = setup
    from kinloyalty.analysis.study2.loading import load_data
    with pytest.raises(ValueError, match='never smoke/pilot/probes'):
        load_data(manifest, directory)
    smoke = tmp_path / 'smoke.jsonl'
    write_manifest(build_manifest(ROOT / 'configs/study2.yaml', 'smoke'), smoke)
    with pytest.raises(ValueError, match='80 pilot episodes'):
        write_pilot_report(smoke, directory, tmp_path / 'report')
