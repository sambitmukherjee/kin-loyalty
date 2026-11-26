"""Verify isolated Study 2 loading/inference using only explicit mock logs."""

from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest
import statsmodels.formula.api as smf
import json
import hashlib

from kinloyalty.analysis.study2 import loading, simulate
from kinloyalty.analysis.study2.core import analyze_core
from kinloyalty.analysis.study2.reports import diagnostic_tables
from kinloyalty.analysis.study2.outcomes import buyer_offer_outcomes
from kinloyalty.negotiation.transcript import TranscriptTurn
from kinloyalty.negotiation.collection import validate_live_contract


@pytest.fixture(scope='module')
def synthetic_data(tmp_path_factory):
    directory = tmp_path_factory.mktemp('study2-inference') / 'synthetic'
    summary = simulate.simulate_collection('configs/study2.yaml', directory)
    assert summary['episodes_complete'] == 960 and summary['new_calls'] == 4320
    assert not summary['unfinished_unit_ids']
    data = loading.load_data(directory / 'manifest.jsonl', directory / 'collection', allow_synthetic=True)
    return directory, data


@pytest.mark.parametrize('phase', ['smoke', 'pilot'])
def test_phase_rejected_before_any_response_is_read(monkeypatch, tmp_path, phase):
    monkeypatch.setattr(loading, 'read_manifest', lambda _: [{'phase': phase, 'is_probe': False}])
    monkeypatch.setattr(loading, 'replay_collection', lambda *_: pytest.fail('ineligible responses were opened'))
    with pytest.raises(ValueError, match='never smoke/pilot/probes'):
        loading.load_data(tmp_path / 'manifest', tmp_path)


@pytest.mark.parametrize('path', ['data/study1/main', 'results/study1/main', 'data/study2/smoke', 'data/study2/pilot'])
def test_protected_input_rejected_before_even_manifest_is_read(monkeypatch, path):
    monkeypatch.setattr(loading, 'read_manifest', lambda _: pytest.fail('protected input was opened'))
    with pytest.raises(ValueError, match='cannot read Study 1 or smoke/pilot'):
        loading.load_data(Path(path) / 'manifest.jsonl', path)


def test_synthetic_needs_explicit_opt_in(synthetic_data):
    directory, _ = synthetic_data
    with pytest.raises(ValueError, match='explicit allow_synthetic'):
        loading.load_data(directory / 'manifest.jsonl', directory / 'collection')


def test_synthetic_generator_checks_destination_before_any_write(monkeypatch, tmp_path):
    destination = tmp_path / 'forbidden'
    def reject(*args, **kwargs):
        raise ValueError('blocked destination')
    monkeypatch.setattr(simulate, 'check_destination', reject)
    with pytest.raises(ValueError, match='blocked destination'):
        simulate.simulate_collection('configs/study2.yaml', destination)
    assert not destination.exists()


def test_planted_effect_recovered_after_full_log_replay(synthetic_data):
    _, data = synthetic_data
    metadata, tables, arrays = analyze_core(data, resamples=99)
    contrasts = tables['contrasts'].set_index('test')
    p2 = contrasts.loc['p2']
    assert p2.estimate == pytest.approx(-.2, abs=1e-12)
    assert p2.permutation_p_value == .01
    assert p2.complete_swap_strata == 320 and p2.n == 960
    for model in data.config.model_order:
        assert contrasts.loc[f'buyer_{model}', 'estimate'] == pytest.approx(-.2, abs=1e-12)
    assert contrasts.loc['other_vs_none', 'estimate'] == pytest.approx(0, abs=1e-12)
    assert contrasts.loc['other_vs_none', 'permutation_p_value'] == 1
    assert metadata['tost']['available'] and not metadata['tost']['equivalent']
    assert metadata['tost']['lower_tail_count'] == 99 and metadata['tost']['p_lower'] == 1
    assert np.allclose(arrays['bootstrap_p2'], -.2, atol=1e-12)
    assert data.replay['episodes_verified'] == 960 and data.replay['attempts_verified'] == 4320
    first = data.episodes.buyer_first_offer_position
    assert first.notna().all() and first.between(.74, .76).all()
    independent = smf.ols('surplus_share ~ C(pair_id) + buyer_opens + card_says_same + card_says_other',
                          data=data.episodes).fit(cov_type='cluster', cov_kwds={'groups': data.episodes.pair_id})
    test = independent.t_test('card_says_same - card_says_other = 0')
    assert metadata['cluster_robustness']['standard_error'] == pytest.approx(np.asarray(test.sd).item(), abs=1e-12)


@pytest.mark.parametrize('shift,expected,equivalent,p_value', [(.2, 0., True, 1.), (.4, .2, False, .01), (.15, -.05, False, .01)])
def test_null_reverse_and_boundary_in_memory_fixtures(synthetic_data, shift, expected, equivalent, p_value):
    _, data = synthetic_data
    episodes = data.episodes.copy()
    episodes['surplus_share'] += shift * episodes.card_says_same
    metadata, tables, _ = analyze_core(replace(data, episodes=episodes), resamples=99)
    row = tables['contrasts'].set_index('test').loc['p2']
    assert row.estimate == pytest.approx(expected, abs=1e-12)
    assert row.permutation_p_value == p_value
    assert metadata['tost']['equivalent'] is equivalent


def test_usage_and_descriptives_preserve_denominators(synthetic_data):
    _, data = synthetic_data
    tables = diagnostic_tables(data)
    assert len(tables['pair_condition_descriptives']) == 48
    pooled = tables['pooled_descriptives'].iloc[0]
    assert pooled.n_planned == pooled.n_retained == pooled.deals == 960
    assert pooled.exclusions == pooled.reasks == pooled.retries == 0
    assert tables['usage_summary'].calls.sum() == 4320
    assert tables['usage_summary'].reasoning_tokens_missing.sum() == 0
    assert 'message' not in tables['public_message_lengths'].columns
    assert 'raw_response' not in tables['usage_calls'].columns


def test_signed_concessions_ignore_acceptances_and_other_side_offers():
    turns = [TranscriptTurn('buyer', 'First', 'offer', 400),
             TranscriptTurn('seller', 'Counter', 'offer', 5000),
             TranscriptTurn('buyer', 'Lower', 'offer', 100),
             TranscriptTurn('seller', 'Accepted', 'accept', 99999)]
    row = buyer_offer_outcomes(turns, buyer_max=600, seller_min=400)
    assert row['buyer_offer_count'] == 2 and row['buyer_first_offer_position'] == 1
    assert row['buyer_average_concession'] == -1.5
    assert buyer_offer_outcomes(turns[:2], buyer_max=600, seller_min=400)['buyer_average_concession'] is None
    assert buyer_offer_outcomes(turns[1:2], buyer_max=600, seller_min=400)['buyer_first_offer_position'] is None
    more = [*turns[:3], TranscriptTurn('buyer', 'Raise', 'offer', 1100)]
    assert buyer_offer_outcomes(more, buyer_max=600, seller_min=400)['buyer_average_concession'] == 1.75


def test_all_secondary_outputs_and_eligibility(synthetic_data):
    _, data = synthetic_data
    episodes = data.episodes.copy()
    episodes.loc[0, 'buyer_average_concession'] = np.nan
    modified = replace(data, episodes=episodes)
    metadata, tables, arrays = analyze_core(modified, resamples=99)
    contrasts = tables['contrasts'].set_index('test')
    assert len(contrasts) == 15
    row = contrasts.loc['secondary_buyer_average_concession']
    assert row.n == 959 and row.complete_swap_strata + row.incomplete_strata == 320
    interaction = contrasts.loc['label_x_actual_self_pair']
    assert interaction.permutation_resamples == 0 and np.isnan(interaction.permutation_p_value)
    assert 'self-pairs' in interaction.sign_convention and 'cross-pairs' in interaction.sign_convention
    assert not any(key.startswith('permutation_') and 'actual_self_pair' in key for key in arrays)
    counts = diagnostic_tables(modified)['outcome_eligibility']
    counts = counts.loc[counts.grouping.eq('condition') & counts.outcome.eq('buyer_average_concession')]
    assert counts.n_eligible.sum() == 959 and counts.n_undefined_nonexcluded.sum() == 1


def test_live_read_only_contract_support_does_not_draw_main_scenarios():
    contract = {'phase': 'main', 'natural_attempt_cap': 100, 'probe_attempt_cap': 0,
                'approved_by': 'fixture', 'approved_on': 'fixture', 'expected_versions': {'fixture': 'fixture'}}
    validate_live_contract(contract, phase='main')
    with pytest.raises(ValueError, match='manifest phase'):
        validate_live_contract(contract, phase='pilot')
    with pytest.raises(ValueError, match='authorized budgets'):
        validate_live_contract({**contract, 'phase': 'smoke'}, phase='smoke')
    with pytest.raises(ValueError, match='budgets'):
        validate_live_contract({**contract, 'natural_attempt_cap': True}, phase='main')


def test_zero_outcome_keeps_primary_tost_and_finite_metadata(synthetic_data):
    _, data = synthetic_data
    episodes = data.episodes.assign(surplus_share=0.)
    metadata, tables, _ = analyze_core(replace(data, episodes=episodes), resamples=99)
    assert tables['contrasts'].set_index('test').loc['p2', 'estimate'] == 0
    assert metadata['tost']['equivalent']
    assert metadata['cluster_robustness']['estimate'] == 0
    json.dumps(metadata, allow_nan=False)


def test_reproduce_cli_is_complete_deterministic_and_does_not_overwrite(synthetic_data, tmp_path, monkeypatch, capsys):
    directory, _ = synthetic_data
    from kinloyalty.negotiation.cli import main
    monkeypatch.setenv('MPLCONFIGDIR', str(tmp_path / 'mpl-cache'))
    outputs = [tmp_path / 'first', tmp_path / 'second']
    for command, output in zip(('analyze', 'reproduce'), outputs):
        main([command, '--manifest', str(directory / 'manifest.jsonl'), '--directory', str(directory / 'collection'),
              '--output', str(output), '--allow-synthetic', '--resamples', '99'])
        summary = json.loads(capsys.readouterr().out)
        assert summary['tests_reported'] == 15 and summary['primary_estimate'] == pytest.approx(-.2, abs=1e-12)
    inventories = [json.loads((output / 'artifacts.sha256.json').read_text()) for output in outputs]
    assert inventories[0] == inventories[1]
    for relative, digest in inventories[0].items():
        assert hashlib.sha256((outputs[0] / relative).read_bytes()).hexdigest() == digest
    assert len(list((outputs[0] / 'figures').glob('*.pdf'))) == 4
    assert len(list((outputs[0] / 'figures').glob('*.png'))) == 4
    assert 'SIMULATED VERIFICATION ONLY' in (outputs[0] / 'report.md').read_text()
    from kinloyalty.analysis.study2.pipeline import reproduce
    with pytest.raises(ValueError, match='never overwritten'):
        reproduce(directory / 'manifest.jsonl', directory / 'collection', outputs[0], allow_synthetic=True, resamples=99)


def test_edge_case_logs_replay_and_outcome_specific_samples(tmp_path):
    directory = tmp_path / 'synthetic-edges'
    summary = simulate.simulate_collection('configs/study2.yaml', directory, edge_cases=True)
    assert summary['episodes_complete'] == 960 and not summary['unfinished_unit_ids']
    data = loading.load_data(directory / 'manifest.jsonl', directory / 'collection', allow_synthetic=True)
    outcomes = data.episodes.outcome.value_counts()
    assert outcomes.to_dict() == {'deal': 957, 'excluded': 1, 'walk_away_impasse': 1, 'final_message_impasse': 1}
    assert data.episodes.reasks.sum() == 2
    assert data.episodes.surplus_share.min() < 0 and data.episodes.surplus_share.max() > 1
    assert data.episodes.buyer_average_concession.min() < 0
    assert data.episodes.buyer_average_concession.notna().sum() == 955
    metadata, tables, arrays = analyze_core(data, resamples=99)
    contrasts = tables['contrasts'].set_index('test')
    assert contrasts.loc['p2', 'n'] == 959
    assert contrasts.loc['secondary_within_deal_share', 'n'] == 957
    assert contrasts.loc['secondary_buyer_average_concession', 'n'] == 955
    counts = diagnostic_tables(data)['outcome_eligibility']
    counts = counts.loc[counts.grouping.eq('condition') & counts.outcome.eq('buyer_average_concession')]
    assert counts.n_excluded.sum() == 1 and counts.n_undefined_nonexcluded.sum() == 4
    assert counts.n_eligible.sum() == 955
