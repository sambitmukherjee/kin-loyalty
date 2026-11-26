"""Compute Study 2 primary, equivalence, robustness, and secondary tests."""

import numpy as np
import pandas as pd

from kinloyalty.analysis.inference import bootstrap_tost, two_sided_p
from kinloyalty.analysis.study2.inference import (
    bootstrap_contrasts, contrast_vector, fit_contrast, make_design, matched_pairs,
    permutation_from_pairs, scenario_draws, summarize_samples,
)
from kinloyalty.analysis.study2.loading import AnalysisData
from kinloyalty.analysis.study2.outcomes import OUTCOME_NOTES
from kinloyalty.analysis.study2.reports import cluster_robustness


def analyze_core(data: AnalysisData, *, resamples: int | None = None) -> tuple[dict, dict[str, pd.DataFrame], dict[str, np.ndarray]]:
    """Use frozen seeds and the same scenario resamples for every primary CI/TOST.

    Replication overrides are for explicit synthetic fixtures only. No real
    smoke, pilot, or Study 1 collection can become AnalysisData via the loader.
    All eligible episodes enter OLS and the paired scenario bootstrap. Only
    complete tested-label pairs swap; third-condition availability is irrelevant.
    """
    settings = data.config.study['analysis']
    if resamples is not None and not data.synthetic:
        raise ValueError('Replication overrides are allowed only for synthetic verification.')
    bootstrap_count = settings['bootstrap_resamples'] if resamples is None else resamples
    permutation_count = settings['permutation_resamples'] if resamples is None else resamples
    # Check that the smallest required (95%) count-matched interval exists.
    from kinloyalty.analysis.inference import bootstrap_interval_ranks
    bootstrap_interval_ranks(bootstrap_count)
    seeds = data.config.study['seeds']
    draws = scenario_draws(data.scenarios, resamples=bootstrap_count, seed=seeds['bootstrap'])
    arrays = {'bootstrap_scenario_indices': draws}
    primary = make_design(data.episodes, data.scenarios, 'surplus_share')
    vectors = {key: contrast_vector(primary, left, right) for key, left, right in
               [('p2', 'same', 'other'), ('same_vs_none', 'same', 'none'), ('other_vs_none', 'other', 'none')]}
    bootstraps = bootstrap_contrasts(primary, draws, vectors)
    rows = []

    def result(design, vector, bootstrap, *, key, left='same', right='other', analysis='secondary', buyer_model='all', outcome='surplus_share'):
        point = fit_contrast(design, vector)
        swaps, counts = matched_pairs(design, left, right)
        null = permutation_from_pairs(design, point, swaps, resamples=permutation_count,
                                      seed=seeds['permutation'], key=key)
        arrays[f'bootstrap_{key}'] = bootstrap
        arrays[f'permutation_{key}'] = null
        row = {'analysis': analysis, 'test': key, 'outcome': outcome, 'outcome_note': OUTCOME_NOTES[outcome], 'buyer_model': buyer_model,
               'sign_convention': f'{left} minus {right}',
               'left_label': left, 'right_label': right, 'n': len(design.frame),
               'pairs_with_eligible_rows': int(design.frame.pair_id.nunique()),
               'estimable': point.estimable, 'unavailable_reason': point.reason,
               'permutation_resamples': permutation_count,
               'permutation_p_value': two_sided_p(point.estimate, null) if point.estimable else None,
               **counts, **summarize_samples(point.estimate, bootstrap)}
        rows.append(row)
        return point

    p2 = result(primary, vectors['p2'], bootstraps['p2'], key='p2', analysis='primary')
    for key, left in [('same_vs_none', 'same'), ('other_vs_none', 'other')]:
        result(primary, vectors[key], bootstraps[key], key=key, left=left, right='none')
    for model in data.config.model_order:
        design = make_design(data.episodes, data.scenarios, 'surplus_share', buyer_model=model)
        vector = contrast_vector(design)
        key = f'buyer_{model}'
        samples = bootstrap_contrasts(design, draws, {key: vector})[key]
        result(design, vector, samples, key=key, buyer_model=model)

    for outcome in OUTCOME_NOTES:
        if outcome == 'surplus_share':
            continue
        design = make_design(data.episodes, data.scenarios, outcome)
        vector = contrast_vector(design)
        key = f'secondary_{outcome}'
        samples = bootstrap_contrasts(design, draws, {key: vector})[key]
        result(design, vector, samples, key=key, outcome=outcome)

    interaction = make_design(data.episodes, data.scenarios, 'surplus_share', interaction=True)
    vector = contrast_vector(interaction, interaction=True)
    point = fit_contrast(interaction, vector)
    key = 'label_x_actual_self_pair'
    samples = bootstrap_contrasts(interaction, draws, {key: vector})[key]
    arrays[f'bootstrap_{key}'] = samples
    rows.append({'analysis': 'secondary', 'test': key, 'outcome': 'surplus_share', 'buyer_model': 'all',
                 'outcome_note': OUTCOME_NOTES['surplus_share'],
                 'sign_convention': '(same - other in self-pairs) - (same - other in cross-pairs); difference of card x self-pair coefficients',
                 'left_label': 'same', 'right_label': 'other', 'n': len(interaction.frame),
                 'pairs_with_eligible_rows': int(interaction.frame.pair_id.nunique()),
                 'estimable': point.estimable, 'unavailable_reason': point.reason,
                 'permutation_resamples': 0, 'permutation_p_value': None,
                 **summarize_samples(point.estimate, samples)})

    if p2.estimable and np.isfinite(bootstraps['p2']).all():
        tost = bootstrap_tost(p2.estimate, bootstraps['p2'], bound=settings['equivalence_bound'], alpha=settings['alpha'])
        tost['equivalent'] = tost['equivalent'] and tost['equivalence_ci_strictly_inside']
        tost['available'] = True
    else:
        tost = {'available': False, 'equivalent': None, 'reason': 'point_or_bootstrap_not_estimable',
                'bound': settings['equivalence_bound'], 'alpha': settings['alpha'],
                'bootstrap_resamples': bootstrap_count,
                'bootstrap_unavailable': int((~np.isfinite(bootstraps['p2'])).sum())}
    metadata = {'synthetic': data.synthetic, 'manifest_sha256': data.manifest_sha256,
                'bootstrap_resamples': bootstrap_count, 'permutation_resamples': permutation_count,
                'bootstrap_seed': seeds['bootstrap'], 'permutation_seed': seeds['permutation'],
                'numerical_tolerance': settings['numerical_tolerance'], 'multiple_testing_correction': 'none',
                'primary_incomplete_strata': 'Retain eligible rows in OLS/bootstrap; swap only when both compared outcomes exist. Third-condition availability is irrelevant.',
                'bootstrap_missing_outcomes': 'Carry every planned scenario; excluded rows stay absent, without replacement.',
                'failed_bootstraps': 'Preserve every failed draw as NaN; report intervals/TOST unavailable, without redrawing.',
                'replay': data.replay, 'tost': tost, 'cluster_robustness': cluster_robustness(primary)}
    return metadata, {'contrasts': pd.DataFrame(rows)}, arrays
