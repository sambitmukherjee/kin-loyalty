"""Fit pair-fixed-effect contrasts and resample complete planned scenario blocks."""

from dataclasses import dataclass

import numpy as np
import pandas as pd

from kinloyalty.analysis.inference import (
    INFERENCE_TIE_TOLERANCE, bootstrap_interval, bootstrap_interval_ranks,
    seeded_rng,
)


@dataclass(frozen=True)
class Design:
    """Keep eligible observations and their positions in the full scenario universe."""

    frame: pd.DataFrame
    scenarios: pd.DataFrame
    z: np.ndarray
    y: np.ndarray
    pair_codes: np.ndarray
    cluster_codes: np.ndarray
    pair_levels: tuple[str, ...]
    groups: tuple[np.ndarray, ...]
    feature_names: tuple[str, ...]


@dataclass(frozen=True)
class Fit:
    """Represent an estimable contrast or an explicit reason it is unavailable."""

    estimate: float | None
    estimable: bool
    reason: str
    coefficients: np.ndarray
    weights: np.ndarray


def make_design(
    episodes: pd.DataFrame, scenarios: pd.DataFrame, outcome: str, *,
    buyer_model: str | None = None, interaction: bool = False,
) -> Design:
    """Drop only excluded/undefined outcomes while retaining every planned scenario."""
    frame = episodes.copy()
    scope_pairs = set(frame.loc[frame.buyer_model.eq(buyer_model), 'pair_id']) if buyer_model is not None else set(frame.pair_id)
    frame = frame.loc[frame.pair_id.isin(scope_pairs) & ~frame.excluded & frame[outcome].notna()].copy()
    frame = frame.sort_values('episode_id').reset_index(drop=True)
    universe = scenarios.sort_values(['pair_id', 'scenario_id']).reset_index(drop=True)
    lookup = {(row.pair_id, row.scenario_id): index for index, row in enumerate(universe.itertuples())}
    pairs = tuple(sorted(scope_pairs))
    pair_codes = np.array([pairs.index(pair) for pair in frame.pair_id], dtype=int)
    cluster_codes = np.array([lookup[(row.pair_id, row.scenario_id)] for row in frame.itertuples()], dtype=int)
    names = ('buyer_opens', 'card_says_same', 'card_says_other')
    z = frame[list(names)].to_numpy(float)
    if interaction:
        z = np.column_stack([z, frame.card_says_same.to_numpy(float) * frame.self_pair.to_numpy(float),
                             frame.card_says_other.to_numpy(float) * frame.self_pair.to_numpy(float)])
        names += ('same_x_self_pair', 'other_x_self_pair')
    y = frame[outcome].to_numpy(float)
    if not np.isfinite(y).all() or not np.isfinite(z).all():
        raise ValueError('Regression inputs must be finite after explicit outcome eligibility filtering.')
    groups = tuple(np.flatnonzero(universe.pair_id.eq(pair)) for pair in pairs)
    return Design(frame, universe, z, y, pair_codes, cluster_codes, pairs, groups, names)


def contrast_vector(design: Design, left: str = 'same', right: str = 'other', *, interaction: bool = False) -> np.ndarray:
    """Represent same/other/baseline contrasts or the label-by-actual-self contrast."""
    vector = np.zeros(len(design.feature_names))
    columns = {'none': None, 'same': 'card_says_same', 'other': 'card_says_other'}
    if interaction:
        vector[design.feature_names.index('same_x_self_pair')] = 1
        vector[design.feature_names.index('other_x_self_pair')] = -1
        return vector
    for label, sign in ((left, 1), (right, -1)):
        if label not in columns:
            raise ValueError('Unknown displayed-label contrast.')
        if columns[label] is not None:
            vector[design.feature_names.index(columns[label])] += sign
    return vector


def _system(design: Design) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    z, y = design.z, design.y
    counts = np.bincount(design.pair_codes, minlength=len(design.pair_levels))
    sums = np.zeros((len(counts), z.shape[1]))
    totals = np.bincount(design.pair_codes, weights=y, minlength=len(counts))
    for index in range(z.shape[1]):
        sums[:, index] = np.bincount(design.pair_codes, weights=z[:, index], minlength=len(counts))
    means = np.divide(sums, counts[:, None], out=np.zeros_like(sums), where=counts[:, None] > 0)
    within = z - means[design.pair_codes]
    return within.T @ within, within.T @ y, within


def _estimates(matrix: np.ndarray, rhs: np.ndarray, vector: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    inverse = np.linalg.pinv(matrix, rcond=INFERENCE_TIE_TOLERANCE, hermitian=True)
    beta = np.einsum('...ij,...j->...i', inverse, rhs)
    projected = np.einsum('i,...ij,...jk->...k', vector, inverse, matrix)
    estimable = np.max(np.abs(projected - vector), axis=-1) <= INFERENCE_TIE_TOLERANCE
    estimates = np.where(estimable, np.einsum('...i,i->...', beta, vector), np.nan)
    return estimates, inverse


def fit_contrast(design: Design, vector: np.ndarray) -> Fit:
    """Fit OLS after eliminating pair intercepts, checking contrast estimability."""
    matrix, rhs, within = _system(design)
    estimate, inverse = _estimates(matrix, rhs, vector)
    beta = inverse @ rhs
    if not np.isfinite(estimate):
        return Fit(None, False, 'contrast_not_estimable', beta, np.full(len(design.y), np.nan))
    weights = within @ inverse @ vector
    return Fit(float(estimate), True, '', beta, weights)


def scenario_draws(scenarios: pd.DataFrame, *, resamples: int, seed: int) -> np.ndarray:
    """Resample scenario IDs within each pair, retaining all planned cluster positions."""
    if type(resamples) is not int or resamples < 1:
        raise ValueError('A positive bootstrap replication count is required.')
    universe = scenarios.sort_values(['pair_id', 'scenario_id']).reset_index(drop=True)
    result = np.empty((resamples, len(universe)), dtype=np.int32)
    for pair in sorted(universe.pair_id.unique()):
        positions = np.flatnonzero(universe.pair_id.eq(pair))
        rng = seeded_rng(seed, f'study2:bootstrap:scenarios:{pair}')
        result[:, positions] = rng.choice(positions, size=(resamples, len(positions)), replace=True)
    return result


def bootstrap_contrasts(design: Design, draws: np.ndarray, vectors: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    """Refit each scenario resample via sufficient statistics; retain singular draws as NaN."""
    clusters, features = len(design.scenarios), design.z.shape[1]
    counts = np.bincount(design.cluster_codes, minlength=clusters)
    sums = np.column_stack([np.bincount(design.cluster_codes, weights=design.z[:, j], minlength=clusters) for j in range(features)])
    totals = np.bincount(design.cluster_codes, weights=design.y, minlength=clusters)
    zy = np.column_stack([np.bincount(design.cluster_codes, weights=design.z[:, j] * design.y, minlength=clusters) for j in range(features)])
    zz = np.empty((clusters, features, features))
    for j in range(features):
        for k in range(features):
            zz[:, j, k] = np.bincount(design.cluster_codes, weights=design.z[:, j] * design.z[:, k], minlength=clusters)
    result = {key: np.full(len(draws), np.nan) for key in vectors}
    for start in range(0, len(draws), 250):
        block = draws[start:start + 250]
        matrix = np.zeros((len(block), features, features))
        rhs = np.zeros((len(block), features))
        for group in design.groups:
            indexes = block[:, group]
            n = counts[indexes].sum(axis=1)
            z = sums[indexes].sum(axis=1)
            y = totals[indexes].sum(axis=1)
            adjustment = np.divide(z, n[:, None], out=np.zeros_like(z), where=n[:, None] > 0)
            matrix += zz[indexes].sum(axis=1) - np.einsum('bi,bj->bij', adjustment, z)
            rhs += zy[indexes].sum(axis=1) - adjustment * y[:, None]
        for key, vector in vectors.items():
            result[key][start:start + len(block)] = _estimates(matrix, rhs, vector)[0]
    return result


def permutation_from_pairs(
    design: Design, fit: Fit, pairs: list[tuple[int, int]], *, resamples: int, seed: int, key: str,
) -> np.ndarray:
    """Independently swap specified matched eligible rows and recompute the exact OLS contrast.

    Matched rows have identical pair/opener controls. Swapping their labels is
    algebraically equivalent to exchanging outcomes in the fixed design, so its
    OLS projection can be reused without changing the regression specification.
    """
    if not fit.estimable:
        return np.full(resamples, np.nan)
    deltas = []
    used = set()
    for left, right in pairs:
        a, b = design.frame.iloc[left], design.frame.iloc[right]
        if (left == right or left in used or right in used or
                (a.pair_id, a.scenario_id, a.buyer_opens) != (b.pair_id, b.scenario_id, b.buyer_opens)):
            raise ValueError('Permutation pairs must be disjoint matching pair/scenario/opener rows.')
        used.update((left, right))
        deltas.append((fit.weights[left] - fit.weights[right]) * (design.y[right] - design.y[left]))
    rng = seeded_rng(seed, f'study2:permutation:{key}')
    result = np.empty(resamples)
    for start in range(0, resamples, 250):
        size = min(250, resamples - start)
        swaps = rng.integers(0, 2, size=(size, len(deltas)), dtype=np.int8)
        result[start:start + size] = fit.estimate + swaps @ np.asarray(deltas)
    return result


def matched_pairs(design: Design, left: str, right: str) -> tuple[list[tuple[int, int]], dict]:
    """Identify complete eligible two-label strata; retain other observations in OLS.

    This helper reports eligibility, rather than imputing excluded/undefined
    outcomes or substituting the third condition. Callers choose which outcome
    and eligibility rule to use before constructing a design.
    """
    if left == right or {left, right} - {'same', 'other', 'none'}:
        raise ValueError('Choose two distinct displayed labels.')
    pairs = []
    counts = {'complete_swap_strata': 0, 'singleton_strata': 0, 'neither_eligible_strata': 0}
    grouped = {identity: group for identity, group in design.frame.groupby(['pair_id', 'scenario_id'], sort=True)}
    for row in design.scenarios.itertuples():
        if row.pair_id not in design.pair_levels:
            continue
        group = grouped.get((row.pair_id, row.scenario_id))
        selected = {} if group is None else {
            label: list(group.index[group.card_says.eq(label)]) for label in (left, right)}
        if any(len(indexes) > 1 for indexes in selected.values()):
            raise ValueError('A scenario must have at most one episode per displayed label.')
        a, b = selected.get(left, []), selected.get(right, [])
        if a and b:
            pairs.append((a[0], b[0]))
            counts['complete_swap_strata'] += 1
        elif a or b:
            counts['singleton_strata'] += 1
        else:
            counts['neither_eligible_strata'] += 1
    counts['fixed_third_label_rows'] = int((~design.frame.card_says.isin([left, right])).sum())
    counts['fixed_compared_label_rows'] = counts['singleton_strata']
    counts['incomplete_strata'] = counts['singleton_strata'] + counts['neither_eligible_strata']
    counts['planned_strata'] = counts['complete_swap_strata'] + counts['incomplete_strata']
    return pairs, counts


def summarize_samples(estimate: float | None, samples: np.ndarray) -> dict:
    """Report intervals only if every requested resample is available; never redraw failures."""
    failed = int(np.count_nonzero(~np.isfinite(samples)))
    available = estimate is not None and failed == 0
    low, high = bootstrap_interval(samples) if available else (None, None)
    return {'estimate': estimate, 'ci_low': low, 'ci_high': high, 'interval_available': available,
            'bootstrap_resamples': len(samples), 'bootstrap_unavailable': failed,
            'ci_method': 'percentile_count_matched', 'ci_level': .95,
            'ci_ranks': list(bootstrap_interval_ranks(len(samples))) if available else None}
