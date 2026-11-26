"""Compare Study 2 fixed effects and scenario resamples with independent OLS fits."""

import numpy as np
import pandas as pd
import pytest
import statsmodels.formula.api as smf

from kinloyalty.analysis.study2.inference import (
    bootstrap_contrasts, contrast_vector, fit_contrast, make_design,
    matched_pairs, permutation_from_pairs, scenario_draws, summarize_samples,
)


def _frame():
    rng = np.random.default_rng(11)
    rows = []
    for pair in range(4):
        for scenario in range(10):
            for label in ('none', 'same', 'other'):
                rows.append({'episode_id': f'{pair}:{scenario:02d}:{label}', 'pair_id': f'p{pair}',
                             'scenario_id': f's{scenario:02d}', 'buyer_model': f'b{pair // 2}',
                             'buyer_opens': float(scenario % 2), 'card_says_same': float(label == 'same'),
                             'card_says_other': float(label == 'other'), 'self_pair': pair % 2 == 0,
                             'card_says': label, 'excluded': False,
                             'surplus_share': pair + scenario % 2 * .3 - .2 * (label == 'same') + rng.normal(0, .03)})
    frame = pd.DataFrame(rows)
    universe = frame[['pair_id', 'scenario_id']].drop_duplicates().sort_values(['pair_id', 'scenario_id']).reset_index(drop=True)
    return frame, universe


def test_primary_and_interaction_match_independent_statsmodels() -> None:
    frame, universe = _frame()
    frame.loc[[2, 7, 18], 'excluded'] = True
    for interaction in (False, True):
        design = make_design(frame, universe, 'surplus_share', interaction=interaction)
        vector = contrast_vector(design, interaction=interaction)
        fitted = fit_contrast(design, vector)
        formula = 'surplus_share ~ C(pair_id) + buyer_opens + card_says_same + card_says_other'
        if interaction:
            formula += ' + card_says_same:self_pair + card_says_other:self_pair'
        independent = smf.ols(formula, data=frame.loc[~frame.excluded].assign(self_pair=lambda x: x.self_pair.astype(float))).fit()
        left, right = ('card_says_same:self_pair', 'card_says_other:self_pair') if interaction else ('card_says_same', 'card_says_other')
        assert fitted.estimable
        assert fitted.estimate == pytest.approx(independent.params[left] - independent.params[right], abs=1e-12)


def test_bootstrap_draws_keep_pairs_and_match_expanded_row_refits() -> None:
    frame, universe = _frame()
    frame.loc[[0, 1, 2, 25], 'excluded'] = True
    design = make_design(frame, universe, 'surplus_share')
    vector = contrast_vector(design)
    draws = scenario_draws(universe, resamples=99, seed=12)
    assert np.array_equal(draws, scenario_draws(universe.sample(frac=1, random_state=2), resamples=99, seed=12))
    estimates = bootstrap_contrasts(design, draws, {'P2': vector})['P2']
    for row_index in (0, 1, 17, 98):
        parts = []
        for index in draws[row_index]:
            identity = universe.iloc[index]
            parts.append(frame.loc[frame.pair_id.eq(identity.pair_id) & frame.scenario_id.eq(identity.scenario_id) & ~frame.excluded])
        expanded = pd.concat(parts)
        independent = smf.ols('surplus_share ~ C(pair_id) + buyer_opens + card_says_same + card_says_other', data=expanded).fit()
        assert estimates[row_index] == pytest.approx(independent.params.card_says_same - independent.params.card_says_other, abs=1e-12)
    for pair in universe.pair_id.unique():
        group = np.flatnonzero(universe.pair_id.eq(pair))
        assert np.isin(draws[:, group], group).all()


def test_matched_swap_projection_matches_explicit_label_refits() -> None:
    frame, universe = _frame()
    design = make_design(frame, universe, 'surplus_share')
    fit = fit_contrast(design, contrast_vector(design))
    selected = []
    for _, group in design.frame.groupby(['pair_id', 'scenario_id'], sort=True):
        selected.append((group.index[group.card_says.eq('same')][0], group.index[group.card_says.eq('other')][0]))
    distribution = permutation_from_pairs(design, fit, selected, resamples=99, seed=13, key='test')
    from kinloyalty.analysis.inference import seeded_rng
    swaps = seeded_rng(13, 'study2:permutation:test').integers(0, 2, size=(99, len(selected)), dtype=np.int8)
    for replicate in (0, 1, 25, 98):
        changed = design.frame.copy()
        for swap, (left, right) in zip(swaps[replicate], selected):
            if swap:
                changed.loc[[left, right], ['card_says_same', 'card_says_other']] = changed.loc[[right, left], ['card_says_same', 'card_says_other']].to_numpy()
        independent = smf.ols('surplus_share ~ C(pair_id) + buyer_opens + card_says_same + card_says_other', data=changed).fit()
        assert distribution[replicate] == pytest.approx(independent.params.card_says_same - independent.params.card_says_other, abs=1e-12)


def test_nonestimable_contrasts_and_resamples_are_not_imputed_or_redrawn() -> None:
    frame, universe = _frame()
    frame.loc[frame.card_says.eq('other'), 'excluded'] = True
    design = make_design(frame, universe, 'surplus_share')
    fit = fit_contrast(design, contrast_vector(design))
    assert not fit.estimable and fit.estimate is None
    result = bootstrap_contrasts(design, scenario_draws(universe, resamples=99, seed=5), {'P2': contrast_vector(design)})['P2']
    assert np.isnan(result).all()
    summary = summarize_samples(None, result)
    assert not summary['interval_available'] and summary['bootstrap_unavailable'] == 99


@pytest.mark.parametrize('left,right,complete,singleton,neither', [('same', 'other', 37, 2, 1), ('same', 'none', 37, 3, 0)])
def test_missing_tested_pairs_stay_fixed_and_missing_third_does_not_block_swaps(left, right, complete, singleton, neither):
    frame, universe = _frame()
    for scenario, labels in [('s00', ['none']), ('s01', ['same']), ('s02', ['same', 'other'])]:
        frame.loc[frame.pair_id.eq('p0') & frame.scenario_id.eq(scenario) & frame.card_says.isin(labels), 'excluded'] = True
    frame.loc[frame.pair_id.eq('p0') & frame.scenario_id.eq('s03') & frame.card_says.eq('other'), 'surplus_share'] = np.nan
    design = make_design(frame, universe, 'surplus_share')
    pairs, counts = matched_pairs(design, left, right)
    assert counts['complete_swap_strata'] == complete and counts['incomplete_strata'] == 40 - complete
    assert counts['singleton_strata'] == singleton and counts['neither_eligible_strata'] == neither
    assert counts['planned_strata'] == 40
    point = fit_contrast(design, contrast_vector(design, left, right))
    null = permutation_from_pairs(design, point, pairs, resamples=99, seed=15, key=f'{left}-{right}')
    from kinloyalty.analysis.inference import seeded_rng
    swaps = seeded_rng(15, f'study2:permutation:{left}-{right}').integers(0, 2, size=(99, len(pairs)), dtype=np.int8)
    for replicate in (0, 98):
        changed = design.frame.copy()
        for swap, (a, b) in zip(swaps[replicate], pairs):
            if swap:
                changed.loc[[a, b], ['card_says_same', 'card_says_other']] = changed.loc[[b, a], ['card_says_same', 'card_says_other']].to_numpy()
        independent = smf.ols('surplus_share ~ C(pair_id) + buyer_opens + card_says_same + card_says_other', data=changed).fit()
        coefficients = {'none': 0, 'same': independent.params.card_says_same, 'other': independent.params.card_says_other}
        assert null[replicate] == pytest.approx(coefficients[left] - coefficients[right], abs=1e-12)


def test_interaction_sign_is_self_minus_cross():
    frame, universe = _frame()
    frame['surplus_share'] = (frame.buyer_opens * .4 + frame.card_says_same * .1
                             + frame.self_pair * frame.card_says_same * .3
                             + frame.self_pair * frame.card_says_other * .1)
    design = make_design(frame, universe, 'surplus_share', interaction=True)
    assert fit_contrast(design, contrast_vector(design, interaction=True)).estimate == pytest.approx(.2, abs=1e-12)


def test_estimable_point_can_have_failed_bootstraps_without_redrawing():
    frame, universe = _frame()
    frame['excluded'] = ~frame.card_says.eq('none') & ~(frame.pair_id.eq('p0') & frame.scenario_id.eq('s00'))
    design = make_design(frame, universe, 'surplus_share')
    point = fit_contrast(design, contrast_vector(design))
    assert point.estimable
    samples = bootstrap_contrasts(design, scenario_draws(universe, resamples=99, seed=3), {'p2': contrast_vector(design)})['p2']
    failed = int((~np.isfinite(samples)).sum())
    assert 0 < failed < 99 and len(samples) == 99
    summary = summarize_samples(point.estimate, samples)
    assert summary['estimate'] is not None and not summary['interval_available']
    assert summary['bootstrap_unavailable'] == failed
