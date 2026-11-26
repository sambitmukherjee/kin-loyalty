"""Build Study 2 mechanical/descriptive tables without coding message contents."""

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

from kinloyalty.analysis.study2.inference import Design, fit_contrast, contrast_vector
from kinloyalty.analysis.study2.loading import AnalysisData
from kinloyalty.analysis.study2.outcomes import OUTCOME_NOTES


def cluster_robustness(design: Design) -> dict:
    """Return the specified pair-cluster OLS contrast as a robustness check only."""
    point = fit_contrast(design, contrast_vector(design))
    groups = design.frame.pair_id.nunique()
    result = {'method': 'pair_cluster_robustness_only', 'clusters': int(groups),
              'estimate': point.estimate, 'available': False, 'reason': point.reason,
              'standard_error': None, 'statistic': None, 'p_value': None, 'ci_low': None, 'ci_high': None}
    if not point.estimable or groups < 2:
        result['reason'] = point.reason or 'too_few_pair_clusters'
        return result
    formula = 'surplus_share ~ C(pair_id) + buyer_opens + card_says_same + card_says_other'
    ordinary = smf.ols(formula, data=design.frame)
    if len(design.frame) <= np.linalg.matrix_rank(ordinary.exog):
        result['reason'] = 'no_residual_degrees_of_freedom'
        return result
    fitted = ordinary.fit(cov_type='cluster', cov_kwds={'groups': design.frame.pair_id})
    with np.errstate(divide='ignore', invalid='ignore'):
        test = fitted.t_test('card_says_same - card_says_other = 0')
    interval = np.asarray(test.conf_int()).reshape(-1)
    numbers = [np.asarray(test.effect).item(), np.asarray(test.sd).item(),
               np.asarray(test.statistic).item(), np.asarray(test.pvalue).item(), *interval]
    if not np.isfinite(numbers).all():
        result.update(reason='degenerate_cluster_robust_inference',
                      standard_error=float(numbers[1]) if np.isfinite(numbers[1]) else None)
        return result
    result.update(available=True, reason='', estimate=float(np.asarray(test.effect).item()),
                  standard_error=float(np.asarray(test.sd).item()), statistic=float(np.asarray(test.statistic).item()),
                  p_value=float(np.asarray(test.pvalue).item()), ci_low=float(interval[0]), ci_high=float(interval[1]),
                  reference_distribution=test.distribution)
    return result


def episode_descriptives(episodes: pd.DataFrame, group_by: list[str]) -> pd.DataFrame:
    """Report exclusions separately and use non-excluded denominators for economic outcomes."""
    groups = episodes.groupby(group_by, sort=True, dropna=False) if group_by else [((), episodes)]
    rows = []
    for identity, group in groups:
        identity = identity if isinstance(identity, tuple) else (identity,)
        retained = group.loc[~group.excluded]
        deals = retained.loc[retained.deal.eq(1)]
        rows.append({**dict(zip(group_by, identity)), 'n_planned': len(group), 'n_retained': len(retained),
                     'deals': len(deals), 'walk_away_impasses': int(group.outcome.eq('walk_away_impasse').sum()),
                     'final_message_impasses': int(group.outcome.eq('final_message_impasse').sum()),
                     'exclusions': int(group.excluded.sum()), 'reasks': int(group.reasks.sum()), 'retries': int(group.retries.sum()),
                     'mean_surplus_share': retained.surplus_share.mean(), 'median_surplus_share': retained.surplus_share.median(),
                     'deal_rate': retained.deal.mean(), 'within_deal_share': deals.surplus_share.mean(),
                     'messages_used_mean_all': group.messages_used.mean(),
                     'messages_used_mean_retained': retained.messages_used.mean(),
                     'buyer_mandate_violations': int(retained.buyer_mandate_violation.sum()),
                     'seller_mandate_violations': int(retained.seller_mandate_violation.sum()),
                     'buyer_mandate_violation_rate': retained.buyer_mandate_violation.mean(),
                     'seller_mandate_violation_rate': retained.seller_mandate_violation.mean()})
    return pd.DataFrame(rows)


def diagnostic_tables(data: AnalysisData) -> dict[str, pd.DataFrame]:
    """Summarize usage availability and structured message lengths, without semantic text labels."""
    usage = []
    for identity, group in data.calls.groupby(['provider', 'model', 'role'], sort=True):
        responses = group.loc[group.api_error.isna()]
        row = dict(zip(['provider', 'model', 'role'], identity))
        row.update(calls=len(group), responses=len(responses), api_errors=int(group.api_error.notna().sum()),
                   invalid_responses=int(responses.valid.eq(False).sum()),
                   accept_price_mismatches=int(group.accept_price_mismatch.sum()))
        for field in ('input_tokens', 'output_tokens', 'reasoning_tokens', 'cache_read_tokens', 'cache_write_tokens'):
            values = responses[field]
            row.update({f'{field}_present': int(values.notna().sum()), f'{field}_missing': int(values.isna().sum()),
                        f'{field}_mean': values.mean(), f'{field}_max': values.max(),
                        f'{field}_sum': values.sum(min_count=1)})
        usage.append(row)
    lengths = data.messages.groupby(['model', 'role'], sort=True).agg(
        messages=('characters', 'size'), mean_characters=('characters', 'mean'),
        median_characters=('characters', 'median'), max_characters=('characters', 'max')).reset_index()
    eligibility = []
    for group_column in ('condition', 'card_says'):
        for label, group in data.episodes.groupby(group_column, sort=True):
            for outcome, note in OUTCOME_NOTES.items():
                available = ~group.excluded & group[outcome].notna()
                eligibility.append({'grouping': group_column, 'label': label, 'outcome': outcome,
                                    'n_planned': len(group), 'n_eligible': int(available.sum()),
                                    'n_excluded': int(group.excluded.sum()),
                                    'n_undefined_nonexcluded': int((~group.excluded & group[outcome].isna()).sum()),
                                    'outcome_note': note})
    provider_cache = []
    for provider, group in data.calls.loc[data.calls.api_error.isna()].groupby('provider', sort=True):
        row = {'provider': provider, 'responses': len(group)}
        for field in ('cache_read_tokens', 'cache_write_tokens'):
            row.update({f'{field}_present': int(group[field].notna().sum()),
                        f'{field}_missing': int(group[field].isna().sum()),
                        f'{field}_sum': group[field].sum(min_count=1)})
        provider_cache.append(row)
    return {'pair_condition_descriptives': episode_descriptives(data.episodes, ['pair_id', 'condition']),
            'pooled_descriptives': episode_descriptives(data.episodes, []),
            'displayed_label_descriptives': episode_descriptives(data.episodes, ['card_says']),
            'mandates_by_condition': episode_descriptives(data.episodes, ['condition']),
            'mandates_by_buyer': episode_descriptives(data.episodes, ['buyer_model']),
            'outcome_eligibility': pd.DataFrame(eligibility), 'provider_cache_summary': pd.DataFrame(provider_cache),
            'usage_summary': pd.DataFrame(usage), 'message_lengths': lengths,
            'usage_calls': data.calls, 'public_message_lengths': data.messages}


def bootstrap_group_means(
    episodes: pd.DataFrame, scenarios: pd.DataFrame, draws: np.ndarray,
    *, outcome: str, group_by: list[str],
) -> tuple[pd.DataFrame, dict[str, np.ndarray]]:
    """Resample all conditions of a scenario together for descriptive mean intervals."""
    from kinloyalty.analysis.study2.inference import summarize_samples
    lookup = {(row.pair_id, row.scenario_id): index for index, row in enumerate(scenarios.itertuples())}
    rows, arrays = [], {}
    for identity, group in episodes.groupby(group_by, sort=True, dropna=False):
        identity = identity if isinstance(identity, tuple) else (identity,)
        eligible = group.loc[~group.excluded & group[outcome].notna()]
        codes = np.array([lookup[(row.pair_id, row.scenario_id)] for row in eligible.itertuples()], dtype=int)
        totals = np.bincount(codes, weights=eligible[outcome].to_numpy(float), minlength=len(scenarios))
        counts = np.bincount(codes, minlength=len(scenarios))
        estimates = np.full(len(draws), np.nan)
        for start in range(0, len(draws), 250):
            block = draws[start:start + 250]
            numerator, denominator = totals[block].sum(axis=1), counts[block].sum(axis=1)
            estimates[start:start + len(block)] = np.divide(numerator, denominator, out=np.full(len(block), np.nan), where=denominator > 0)
        key = f'{outcome}:' + ':'.join(map(str, identity))
        arrays[key] = estimates
        point = float(eligible[outcome].mean()) if len(eligible) else None
        rows.append({**dict(zip(group_by, identity)), 'outcome': outcome, 'n': len(eligible),
                     **summarize_samples(point, estimates)})
    return pd.DataFrame(rows), arrays
