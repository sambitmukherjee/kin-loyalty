"""Estimate fixed-effect contrasts with stratified bootstrap and permutation tests."""

import hashlib
from dataclasses import dataclass
from fractions import Fraction
from typing import Any

import numpy as np
import pandas as pd


# Numerical cutoff ties count against significance/equivalence throughout inference.
INFERENCE_TIE_TOLERANCE = 1e-12


@dataclass
class ModelDesign:
    """Hold one model's fixed design and paired offer/belief observations."""

    model: str
    labels: list[str]
    x: np.ndarray
    inverse: np.ndarray
    y: np.ndarray
    belief: np.ndarray | None
    cells: list[np.ndarray]
    strata: list[np.ndarray]
    frame: pd.DataFrame


def seeded_rng(seed: int, key: str) -> np.random.Generator:
    """Derive order-independent RNG streams without Python's randomized hash."""
    digest = hashlib.sha256(f"{seed}:{key}".encode()).digest()
    return np.random.default_rng(int.from_bytes(digest[:16], "big"))


def make_design(frame: pd.DataFrame, model: str, labels: list[str], paraphrases: list[int], *, outcome: str = "outcome") -> ModelDesign:
    """Construct label indicators and paraphrase controls; reject missing cells."""
    frame = frame[frame.model == model].sort_values("trial_id").reset_index(drop=True)
    cells = [np.flatnonzero((frame.label == label) & (frame.paraphrase_id == p)) for label in labels for p in paraphrases]
    if any(len(cell) == 0 for cell in cells):
        raise ValueError(f"Non-estimable {model}: at least one label × paraphrase cell is empty.")
    x = np.column_stack([*(np.asarray(frame.label == label, float) for label in labels),
                         *(np.asarray(frame.paraphrase_id == p, float) for p in paraphrases[1:])])
    if np.linalg.matrix_rank(x) != x.shape[1]:
        raise ValueError("Fixed-effect design is rank deficient.")
    y = frame[outcome].to_numpy(float)
    belief = frame.belief.to_numpy(float) if outcome == "outcome" and frame.belief.notna().all() else None
    return ModelDesign(model, labels, x, np.linalg.pinv(x), y, belief, cells,
                       [np.flatnonzero(frame.paraphrase_id == p) for p in paraphrases], frame)


def belief_cell_counts(design: ModelDesign) -> list[dict[str, Any]]:
    """Audit each cell's lowest tied mode and number of nonmodal valid beliefs."""
    if design.belief is None:
        raise ValueError("Belief diagnostics require complete paired beliefs.")
    rows = []
    for cell in design.cells:
        beliefs = design.belief[cell]
        values, counts = np.unique(beliefs, return_counts=True)
        mode = values[np.argmax(counts)]  # Sorted values make the first tied mode the lowest.
        identity = design.frame.iloc[cell[0]]
        nonmodal = int(np.count_nonzero(beliefs != mode))
        rows.append({"model": design.model, "label": identity.label,
                     "paraphrase_id": int(identity.paraphrase_id), "n": len(cell),
                     "mode": float(mode), "modal_draws": len(cell) - nonmodal,
                     "nonmodal_draws": nonmodal})
    return rows


def belief_estimability(design: ModelDesign, *, minimum_nonmodal_percent: int) -> dict[str, Any]:
    """Apply the fixed cell-modal-count rule to retained valid proposer draws.

    Each label × paraphrase cell uses its lowest tied mode. The count rule
    applies to the observed sample, not to bootstrap replicate selection.
    """
    if type(minimum_nonmodal_percent) is not int or not 0 <= minimum_nonmodal_percent <= 100:
        raise ValueError("Minimum nonmodal belief percentage must be an integer from 0 to 100.")
    if design.belief is None:
        raise ValueError("Belief diagnostics require complete paired beliefs.")
    belief = design.belief
    nonmodal = sum(cell["nonmodal_draws"] for cell in belief_cell_counts(design))
    required = (minimum_nonmodal_percent * len(belief) + 99) // 100
    rank_deficient = np.linalg.matrix_rank(np.column_stack([design.x, belief])) < design.x.shape[1] + 1
    if nonmodal < required:
        reason = "insufficient_nonmodal_belief_draws"
    elif rank_deficient or not np.isfinite(coefficients(design, design.y, belief, allow_nonestimable=True)).all():
        reason = "numerical_rank_deficiency"
    else:
        reason = ""
    return {"model": design.model, "n": len(belief), "unique_beliefs": len(np.unique(belief)),
            "nonmodal_draws": nonmodal, "nonmodal_share": nonmodal / len(belief),
            "minimum_nonmodal_percent": minimum_nonmodal_percent, "required_nonmodal_draws": required,
            "mode_tie_break": "lowest", "rank_deficient": bool(rank_deficient),
            "estimable": not bool(reason), "not_estimable_reason": reason}


def coefficients(design: ModelDesign, y: np.ndarray, belief: np.ndarray | None = None, *, allow_nonestimable: bool = False) -> np.ndarray:
    """Fit paired resamples; optionally preserve singular replicates as NaN rows."""
    y = np.atleast_2d(y)
    beta = y @ design.inverse.T
    if belief is None:
        return beta
    belief = np.atleast_2d(belief)
    b_beta = belief @ design.inverse.T
    residual_b = belief - b_beta @ design.x.T
    denominator = np.sum(residual_b * residual_b, axis=1)
    valid = denominator >= 1e-10
    if not allow_nonestimable and not valid.all():
        raise ValueError("Belief-adjusted regression is not identifiable in at least one resample.")
    slope = np.full(len(y), np.nan)
    np.divide(np.sum(residual_b * y, axis=1), denominator, out=slope, where=valid)
    return beta - slope[:, None] * b_beta


def bootstrap_coefficients(design: ModelDesign, *, resamples: int, seed: int, key: str, include_adjusted: bool = True) -> tuple[np.ndarray, np.ndarray | None]:
    """Resample pairs once for both fits; keep singular adjusted replicates explicit."""
    rng = seeded_rng(seed, f"bootstrap:{key}:{design.model}")
    ordinary, adjusted = [], []
    for start in range(0, resamples, 250):
        size = min(250, resamples - start)
        indexes = np.tile(np.arange(len(design.y)), (size, 1))
        for cell in design.cells:
            indexes[:, cell] = rng.choice(cell, size=(size, len(cell)), replace=True)
        y = design.y[indexes]
        ordinary.append(coefficients(design, y))
        if design.belief is not None and include_adjusted:
            adjusted.append(coefficients(design, y, design.belief[indexes], allow_nonestimable=True))
    return np.concatenate(ordinary), np.concatenate(adjusted) if adjusted else None


def contrast_vector(design: ModelDesign, left: str, right: str) -> np.ndarray:
    """Represent a directional difference in label coefficients."""
    vector = np.zeros(design.x.shape[1])
    vector[design.labels.index(left)], vector[design.labels.index(right)] = 1, -1
    return vector


def permutation_contrasts(design: ModelDesign, left: str, right: str, *, resamples: int, seed: int, key: str, adjusted: bool = False) -> np.ndarray:
    """Shuffle only the tested pair within strata, including for adjusted residuals."""
    rng = seeded_rng(seed, f"permutation:{key}:{left}:{right}:{adjusted}:{design.model}")
    vector = contrast_vector(design, left, right)
    pair = np.isin(design.frame.label.to_numpy(), [left, right])
    groups = [group[pair[group]] for group in design.strata]
    if adjusted:
        if design.belief is None:
            raise ValueError("Adjusted permutation requires paired beliefs.")
        full = np.column_stack([design.x, design.belief])
        if np.linalg.matrix_rank(full) != full.shape[1]:
            raise ValueError("Adjusted design is rank deficient.")
        # Under H0 beta_left == beta_right: merge their columns in the reduced model.
        li, ri = design.labels.index(left), design.labels.index(right)
        reduced = full.copy()
        reduced[:, li] += reduced[:, ri]
        reduced = np.delete(reduced, ri, axis=1)
        fitted = reduced @ np.linalg.lstsq(reduced, design.y, rcond=None)[0]
        residuals = design.y - fitted
        weights = np.append(vector, 0) @ np.linalg.pinv(full)
        source = residuals
    else:
        fitted = np.zeros_like(design.y)
        source = design.y
        weights = vector @ design.inverse
    result = []
    for start in range(0, resamples, 250):
        size = min(250, resamples - start)
        values = np.tile(source, (size, 1))
        for group in groups:
            values[:, group] = rng.permuted(np.tile(source[group], (size, 1)), axis=1)
        # The fixed design lets us reuse its OLS projection for each full-model refit.
        result.append((values + fitted) @ weights)
    return np.concatenate(result)


def two_sided_p(observed: float, null: np.ndarray) -> float:
    """Count numerical ties conservatively and use the randomized +1 correction."""
    return float((1 + np.count_nonzero(np.abs(null) >= abs(observed) - INFERENCE_TIE_TOLERANCE)) / (len(null) + 1))


def bootstrap_interval_ranks(resamples: int, confidence: float = .95) -> tuple[int, int]:
    """Return one-based empirical ranks matching strict +1-corrected tail tests.

    For B=10,000: 90% uses ranks 500/9,501 and 95% uses 250/9,751.
    Exact rational arithmetic avoids rounding the strict tail-count boundary.
    """
    if type(resamples) is not int or resamples < 1 or not np.isfinite(confidence) or not 0 < confidence < 1:
        raise ValueError("Interval count and confidence level must be valid.")
    tail = (1 - Fraction(str(confidence))) / 2
    # Largest k satisfying (k+1)/(B+1) < tail, including the strict inequality.
    maximum_tail_count = (tail.numerator * (resamples + 1) - 1) // tail.denominator - 1
    if maximum_tail_count < 0:
        raise ValueError("Too few bootstrap estimates for this confidence level under the +1 convention.")
    return maximum_tail_count + 1, resamples - maximum_tail_count


def _finite_bootstrap_samples(samples: np.ndarray) -> np.ndarray:
    values = np.asarray(samples, dtype=float)
    if values.ndim != 1 or len(values) == 0 or not np.isfinite(values).all():
        raise ValueError("Bootstrap intervals and TOST require a nonempty finite one-dimensional sample.")
    return values


def bootstrap_interval(samples: np.ndarray, confidence: float = .95) -> tuple[float, float]:
    """Select count-matched percentile order statistics, without interpolation or centering."""
    values = _finite_bootstrap_samples(samples)
    low_rank, high_rank = bootstrap_interval_ranks(len(values), confidence)
    ordered = np.sort(values)  # Sort a copy; shared paired-bootstrap indexes must stay intact.
    return float(ordered[low_rank - 1]), float(ordered[high_rank - 1])


def bootstrap_tost(observed: float, samples: np.ndarray, *, bound: float, alpha: float = .05) -> dict[str, Any]:
    """Use inclusive percentile-bootstrap tail counts for both equivalence bounds."""
    if not np.isfinite(bound) or bound <= 0 or not np.isfinite(observed) or not np.isfinite(alpha) or not 0 < alpha < .5:
        raise ValueError("TOST requires a finite estimate, positive bound, and alpha between zero and one half.")
    samples = _finite_bootstrap_samples(samples)
    lower_cutoff = -bound + INFERENCE_TIE_TOLERANCE
    upper_cutoff = bound - INFERENCE_TIE_TOLERANCE
    lower_count = int(np.count_nonzero(samples <= lower_cutoff))
    upper_count = int(np.count_nonzero(samples >= upper_cutoff))
    lower = (1 + lower_count) / (len(samples) + 1)
    upper = (1 + upper_count) / (len(samples) + 1)
    low, high = bootstrap_interval(samples, 1 - 2 * alpha)
    contrast_low, contrast_high = bootstrap_interval(samples, 1 - alpha)
    low_rank, high_rank = bootstrap_interval_ranks(len(samples), 1 - 2 * alpha)
    contrast_low_rank, contrast_high_rank = bootstrap_interval_ranks(len(samples), 1 - alpha)
    return {"estimate": observed, "bound": bound, "p_lower": lower, "p_upper": upper,
            "p_tost": max(lower, upper), "equivalent": bool(lower < alpha and upper < alpha),
            "alpha": alpha, "bootstrap_resamples": len(samples),
            "inference_tie_tolerance": INFERENCE_TIE_TOLERANCE,
            "lower_tail_count": lower_count, "upper_tail_count": upper_count,
            "equivalence_ci_method": "percentile_count_matched", "equivalence_ci_level": 1 - 2 * alpha,
            "equivalence_ci_low": low, "equivalence_ci_high": high,
            "equivalence_ci_lower_rank": low_rank, "equivalence_ci_upper_rank": high_rank,
            "equivalence_ci_strictly_inside": bool(low > lower_cutoff and high < upper_cutoff),
            "contrast_ci_method": "percentile_count_matched", "contrast_ci_level": 1 - alpha,
            "contrast_ci_low": contrast_low, "contrast_ci_high": contrast_high,
            "contrast_ci_lower_rank": contrast_low_rank, "contrast_ci_upper_rank": contrast_high_rank}
