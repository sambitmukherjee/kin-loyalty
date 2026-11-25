"""Estimate fixed-effect contrasts with stratified bootstrap and permutation tests."""

import hashlib
from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd


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


def coefficients(design: ModelDesign, y: np.ndarray, belief: np.ndarray | None = None) -> np.ndarray:
    """Fit many paired resamples by Frisch–Waugh–Lovell, keeping belief paired."""
    y = np.atleast_2d(y)
    beta = y @ design.inverse.T
    if belief is None:
        return beta
    belief = np.atleast_2d(belief)
    b_beta = belief @ design.inverse.T
    residual_b = belief - b_beta @ design.x.T
    denominator = np.sum(residual_b * residual_b, axis=1)
    if np.any(denominator < 1e-10):
        raise ValueError("Belief-adjusted regression is not identifiable in at least one resample.")
    slope = np.sum(residual_b * y, axis=1) / denominator
    return beta - slope[:, None] * b_beta


def bootstrap_coefficients(design: ModelDesign, *, resamples: int, seed: int, key: str) -> tuple[np.ndarray, np.ndarray | None]:
    """Resample draws within label × paraphrase cells; retain joint offer/belief pairs."""
    rng = seeded_rng(seed, f"bootstrap:{key}:{design.model}")
    ordinary, adjusted = [], []
    for start in range(0, resamples, 250):
        size = min(250, resamples - start)
        indexes = np.tile(np.arange(len(design.y)), (size, 1))
        for cell in design.cells:
            indexes[:, cell] = rng.choice(cell, size=(size, len(cell)), replace=True)
        y = design.y[indexes]
        ordinary.append(coefficients(design, y))
        if design.belief is not None:
            adjusted.append(coefficients(design, y, design.belief[indexes]))
    return np.concatenate(ordinary), np.concatenate(adjusted) if adjusted else None


def contrast_vector(design: ModelDesign, left: str, right: str) -> np.ndarray:
    """Represent a directional difference in label coefficients."""
    vector = np.zeros(design.x.shape[1])
    vector[design.labels.index(left)], vector[design.labels.index(right)] = 1, -1
    return vector


def permutation_contrasts(design: ModelDesign, left: str, right: str, *, resamples: int, seed: int, key: str, adjusted: bool = False) -> np.ndarray:
    """Permute tested labels, or reduced-model residuals for belief-adjusted S1."""
    rng = seeded_rng(seed, f"permutation:{key}:{left}:{right}:{adjusted}:{design.model}")
    vector = contrast_vector(design, left, right)
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
        groups = design.strata
        source = residuals
    else:
        fitted = np.zeros_like(design.y)
        source = design.y
        weights = vector @ design.inverse
        groups = [group[np.isin(design.frame.label.to_numpy()[group], [left, right])] for group in design.strata]
    result = []
    for start in range(0, resamples, 250):
        size = min(250, resamples - start)
        values = np.tile(source, (size, 1))
        for group in groups:
            values[:, group] = rng.permuted(np.tile(source[group], (size, 1)), axis=1)
        result.append((values + fitted) @ weights)
    return np.concatenate(result)


def two_sided_p(observed: float, null: np.ndarray) -> float:
    """Use absolute-statistic tails and the conservative randomized +1 correction."""
    return float((1 + np.count_nonzero(np.abs(null) >= abs(observed) - 1e-12)) / (len(null) + 1))


def bootstrap_interval(observed: float, samples: np.ndarray, confidence: float = .95) -> tuple[float, float]:
    """Return a basic bootstrap interval by reflecting the bootstrap error quantiles."""
    tail = (1 - confidence) / 2
    low, high = np.quantile(samples - observed, [tail, 1 - tail])
    return float(observed - high), float(observed - low)


def bootstrap_tost(observed: float, samples: np.ndarray, *, bound: float, alpha: float = .05) -> dict[str, Any]:
    """Test both equivalence boundaries using null-centered bootstrap errors."""
    if bound <= 0:
        raise ValueError("Equivalence bound must be positive.")
    error = samples - observed
    lower = (1 + np.count_nonzero(error >= observed + bound - 1e-12)) / (len(error) + 1)
    upper = (1 + np.count_nonzero(error <= observed - bound + 1e-12)) / (len(error) + 1)
    low, high = bootstrap_interval(observed, samples, 1 - 2 * alpha)
    return {"estimate": observed, "bound": bound, "p_lower": lower, "p_upper": upper,
            "p_tost": max(lower, upper), "equivalent": bool(lower < alpha and upper < alpha),
            "equivalence_ci_level": 1 - 2 * alpha, "equivalence_ci_low": low, "equivalence_ci_high": high}
