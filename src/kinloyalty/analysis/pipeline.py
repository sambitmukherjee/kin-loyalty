"""Produce Study 1 estimates and reproducible artifacts from validated saved logs."""

import json
from dataclasses import dataclass
from importlib.metadata import version
from itertools import product
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml

from kinloyalty.analysis.inference import (
    belief_cell_counts, belief_estimability, bootstrap_coefficients, bootstrap_interval, bootstrap_tost, coefficients,
    contrast_vector, make_design, permutation_contrasts, two_sided_p,
)
from kinloyalty.analysis.loading import SavedData, load_saved_data
from kinloyalty.analysis.reports import (
    attempt_diagnostics, comprehension_table, decision_descriptives, pilot_checks, usage_tables,
)
from kinloyalty.logs import file_hash
from kinloyalty.provenance import collect_provenance


@dataclass
class StudyEstimates:
    """Collect inference outputs and explicit S1 estimability diagnostics."""

    contrasts: pd.DataFrame
    equivalence: pd.DataFrame
    coefficient_changes: pd.DataFrame
    distributions: dict[str, np.ndarray]
    belief_diagnostics: pd.DataFrame
    belief_cells: pd.DataFrame


def load_analysis_config(path: str | Path) -> tuple[dict[str, Any], dict[str, Any]]:
    """Read analysis/identity configuration without reading any prompt templates or keys."""
    path = Path(path).resolve()
    study = yaml.safe_load(path.read_text())
    roster = yaml.safe_load((path.parent / study["models_file"]).read_text())["models"]
    spec = study["analysis"]
    if (spec["tost_method"] != "percentile_bootstrap_tail_probabilities"
        or spec["contrast_permutation_rule"] != "tested_pair_within_model_paraphrase"
        or spec.get("adjusted_permutation_rule") != "freedman_lane_within_model_paraphrase"
        or spec.get("bootstrap_interval") != "percentile_count_matched"
        or spec["accepted_decision_phase"] != "main"):
        raise ValueError("Analysis methods must match the researcher-approved configuration.")
    required = {"primary_decision": "dictator", "primary_contrast": ["own_model", "other_lab"],
                "model_weighting": "equal", "fixed_effects": "model_by_paraphrase",
                "bootstrap_strata": ["model", "label", "paraphrase"],
                "permutation_strata": ["model", "paraphrase"],
                "alternative": "two_sided", "multiple_comparison_correction": "none",
                "s1_belief_slopes": "model_specific",
                "s1_belief_estimability": {"minimum_nonmodal_percent": 10,
                    "modal_cell": ["label", "paraphrase"], "mode_tie_break": "lowest",
                    "denominator": "retained_valid_proposer_draws", "frozen_before_pilot": True},
                "figure_formats": ["pdf", "png"]}
    if any(spec.get(key) != value for key, value in required.items()):
        raise ValueError("Unsupported analysis specification; do not silently substitute methods.")
    for key in ("bootstrap_resamples", "permutation_resamples"):
        if type(spec[key]) is not int or spec[key] < 1:
            raise ValueError("Resampling counts must be positive integers.")
    if not 0 < spec["alpha"] < .5 or spec["confidence_level"] != 1 - spec["alpha"]:
        raise ValueError("Alpha and confidence level are inconsistent.")
    return study, roster


def check_roster(data: SavedData, roster: dict[str, Any]) -> None:
    """Reject unknown model keys and requested IDs inconsistent with the supplied roster."""
    for record in data.attempts:
        model = roster.get(record["model"])
        if model is None or model["api_model_id"] != record["api_model_id"]:
            raise ValueError("Saved model identity is not in the configured roster.")


def coverage_table(data: SavedData, study: dict[str, Any], models: list[str]) -> pd.DataFrame:
    """Require every planned main draw to have a terminal record before inference."""
    rows = []
    planned = study["main"]["draws_per_model_decision_label_paraphrase"]
    for model, decision, label, paraphrase in product(models, study["decisions"], study["labels"], [p["id"] for p in study["paraphrases"]]):
        cell = data.trials[(data.trials.model == model) & (data.trials.decision == decision)
                           & (data.trials.label == label) & (data.trials.paraphrase_id == paraphrase)]
        if len(cell) != planned or set(cell.draw_index) != set(range(1, planned + 1)) or cell.unfinished.any():
            raise ValueError("Main inference requires all configured draws to be attempted and terminal; resume missing/unfinished work first.")
        rows.append({"model": model, "decision": decision, "label": label,
                     "paraphrase_id": paraphrase, "planned": planned, "valid": int(cell.valid.sum()),
                     "excluded": int(cell.excluded.sum())})
    return pd.DataFrame(rows)


def study_contrasts(study: dict[str, Any]) -> list[tuple[str, str, str]]:
    """List the prespecified P1, reputation, disclosure, and human contrasts once."""
    contrasts = [("own_model", "other_lab", "own_vs_other"), ("other_lab", "fictional", "reputation")]
    contrasts.extend((label, "not_disclosed", "S2" if label == "human" else "disclosure")
                     for label in study["labels"] if label != "not_disclosed")
    return contrasts


def _estimate_fields(estimate: float, draws: np.ndarray, confidence: float, *, reason: str = "") -> dict[str, Any]:
    estimable = bool(np.isfinite(estimate))
    unavailable = int(np.count_nonzero(~np.isfinite(draws)))
    interval_available = estimable and unavailable == 0
    low, high = bootstrap_interval(draws, confidence) if interval_available else (np.nan, np.nan)
    return {"estimate": estimate, "ci_low": low, "ci_high": high,
            "ci_method": "percentile_count_matched", "ci_level": confidence,
            "estimable": estimable, "not_estimable_reason": reason if not estimable else "",
            "interval_available": interval_available,
            "interval_unavailable_reason": "" if interval_available else reason if not estimable else "non_estimable_bootstrap_replicates",
            "bootstrap_unavailable_count": unavailable}


def estimate_all(frame: pd.DataFrame, study: dict[str, Any], models: list[str]) -> StudyEstimates:
    """Fit contrasts, flag unavailable S1 results, and keep all models in pooled targets."""
    spec = study["analysis"]
    labels = list(study["labels"])
    paraphrases = [entry["id"] for entry in study["paraphrases"]]
    rows, changes, arrays, belief_diagnostics, belief_cells = [], [], {}, [], []
    pooled_p1 = None
    tasks = [(decision, "outcome") for decision in study["decisions"]] + [("ultimatum_proposer", "belief")]
    for decision, outcome in tasks:
        subset = frame[frame.decision == decision]
        key = f"{decision}:{outcome}"
        designs = [make_design(subset, model, labels, paraphrases, outcome=outcome) for model in models]
        s1 = decision == "ultimatum_proposer" and outcome == "outcome"
        diagnostics = [belief_estimability(design, minimum_nonmodal_percent=spec["s1_belief_estimability"]["minimum_nonmodal_percent"]) for design in designs] if s1 else []
        if s1:
            for design in designs:
                belief_cells.extend(belief_cell_counts(design))
        boots = [bootstrap_coefficients(design, resamples=spec["bootstrap_resamples"],
            seed=study["seeds"]["bootstrap"], key=key,
            include_adjusted=s1 and diagnostics[i]["estimable"]) for i, design in enumerate(designs)]
        ordinary = [coefficients(design, design.y)[0] for design in designs]
        adjusted = [coefficients(design, design.y, design.belief)[0] if diagnostics[i]["estimable"]
                    else np.full(design.x.shape[1], np.nan) for i, design in enumerate(designs)] if s1 else None
        for i, diagnostic in enumerate(diagnostics):
            adjusted_boot = boots[i][1]
            belief_diagnostics.append({**diagnostic,
                "bootstrap_fits_attempted": len(adjusted_boot) if adjusted_boot is not None else 0,
                "bootstrap_numerical_failures": int(np.count_nonzero(~np.isfinite(adjusted_boot).all(axis=1))) if adjusted_boot is not None else 0})
        for left, right, family in study_contrasts(study):
            vectors = [contrast_vector(design, left, right) for design in designs]
            for control in ([False, True] if adjusted is not None else [False]):
                method = "belief_adjusted" if control else "unadjusted"
                observed = np.array([vectors[i] @ (adjusted[i] if control else ordinary[i]) for i in range(len(models))])
                samples = np.column_stack([boots[i][int(control)] @ vectors[i] if boots[i][int(control)] is not None
                    else np.full(spec["bootstrap_resamples"], np.nan) for i in range(len(models))])
                null = np.column_stack([permutation_contrasts(design, left, right,
                    resamples=spec["permutation_resamples"], seed=study["seeds"]["permutation"],
                    key=key, adjusted=control) if not control or diagnostics[i]["estimable"]
                    else np.full(spec["permutation_resamples"], np.nan) for i, design in enumerate(designs)])
                missing_models = [models[i] for i in range(len(models)) if not np.isfinite(observed[i])]
                reasons = [diagnostic["not_estimable_reason"] for diagnostic in diagnostics] if control else [""] * len(models)
                pooled_reason = "one_or_more_models_not_estimable" if missing_models else ""
                for scope_index, scope in enumerate([*models, "pooled"]):
                    # Ordinary mean deliberately propagates unavailable models; never average three.
                    estimate = float(observed[scope_index]) if scope != "pooled" else float(observed.mean())
                    draws = samples[:, scope_index] if scope != "pooled" else samples.mean(axis=1)
                    permuted = null[:, scope_index] if scope != "pooled" else null.mean(axis=1)
                    reason = pooled_reason if scope == "pooled" else reasons[scope_index]
                    primary = decision == "dictator" and family == "own_vs_other" and scope == "pooled"
                    rows.append({"decision": decision, "outcome": outcome, "method": method,
                                 "left": left, "right": right, "family": family, "scope": scope,
                                 "designation": "primary_P1" if primary else "secondary",
                                 "interpretation": "descriptive post-card belief adjustment; not causal mediation" if control else "label contrast",
                                 **_estimate_fields(estimate, draws, spec["confidence_level"], reason=reason),
                                 "non_estimable_models": ";".join(missing_models) if scope == "pooled" else scope if not np.isfinite(estimate) else "",
                                 "permutation_p": two_sided_p(estimate, permuted) if np.isfinite(estimate) and np.isfinite(permuted).all() else np.nan,
                                 "bootstrap_resamples": len(draws), "permutation_resamples": len(permuted)})
                    array_key = f"{key}:{method}:{left}-{right}:{scope}"
                    arrays[array_key + ":bootstrap"] = draws
                    arrays[array_key + ":permutation"] = permuted
                    if primary:
                        pooled_p1 = bootstrap_tost(estimate, draws, bound=spec["equivalence_bound_dollars"], alpha=spec["alpha"])
                if control:
                    # Pair the exact same resamples for the before/after comparison.
                    before = np.array([vectors[i] @ ordinary[i] for i in range(len(models))])
                    before_samples = np.column_stack([boots[i][0] @ vectors[i] for i in range(len(models))])
                    for i, scope in enumerate([*models, "pooled"]):
                        delta = float((before - observed)[i]) if scope != "pooled" else float((before - observed).mean())
                        delta_samples = (before_samples - samples)[:, i] if scope != "pooled" else (before_samples - samples).mean(axis=1)
                        reason = pooled_reason if scope == "pooled" else reasons[i]
                        fields = _estimate_fields(delta, delta_samples, spec["confidence_level"], reason=reason)
                        fields["unadjusted_minus_adjusted"] = fields.pop("estimate")
                        changes.append({"left": left, "right": right, "scope": scope,
                                        **fields,
                                        "non_estimable_models": ";".join(missing_models) if scope == "pooled" else scope if not np.isfinite(delta) else "",
                                        "interpretation": "descriptive coefficient change; not a causal mediation estimate"})
                        arrays[f"{key}:unadjusted_minus_adjusted:{left}-{right}:{scope}:bootstrap"] = delta_samples
    return StudyEstimates(pd.DataFrame(rows), pd.DataFrame([pooled_p1]), pd.DataFrame(changes), arrays,
                          pd.DataFrame(belief_diagnostics), pd.DataFrame(belief_cells))


def _write_csv(frame: pd.DataFrame, path: Path) -> None:
    frame.to_csv(path, index=False, float_format="%.12g", lineterminator="\n")


def _write_metadata(output: Path, data: SavedData, config: Path, *, extra_files: list[Path] | None = None) -> None:
    source = Path(__file__).resolve().parents[1]
    inputs = [*data.files, *(extra_files or [])]
    study = yaml.safe_load(config.read_text())
    model_config = (config.parent / study["models_file"]).resolve()
    metadata = {"study": "study1", "synthetic": data.synthetic,
                "interpretation": "SIMULATED: offline verification only" if data.synthetic else "Observed saved study data",
                "inputs_sha256": {str(path): file_hash(path) for path in inputs},
                "analysis_config_sha256": file_hash(config),
                "model_config_sha256": file_hash(model_config),
                "analysis_settings": study["analysis"], "seeds": study["seeds"],
                "package_source_sha256": {str(path.relative_to(source)): file_hash(path) for path in sorted(source.rglob("*.py"))},
                "packages": {name: version(name) for name in ("numpy", "pandas", "scipy", "statsmodels", "matplotlib", "PyYAML")},
                **collect_provenance()}
    (output / "provenance.json").write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n")
    artifacts = {path.name: file_hash(path) for path in sorted(output.iterdir()) if path.is_file()}
    (output / "artifacts.sha256.json").write_text(json.dumps(artifacts, indent=2, sort_keys=True) + "\n")


def analyze_study1(config: str | Path, paths: list[str | Path], output: str | Path, *, allow_synthetic: bool = False, comprehension_paths: list[str | Path] | None = None) -> Path:
    """Reproduce main tables/figures with no model calls, SDK imports, or key reads."""
    config, output = Path(config).resolve(), Path(output).resolve()
    if output.exists():
        raise ValueError("Output directory already exists; choose a new path to preserve artifacts.")
    study, roster = load_analysis_config(config)
    data = load_saved_data(paths, phase="main", study=study, allow_synthetic=allow_synthetic)
    check_roster(data, roster)
    coverage = coverage_table(data, study, list(roster))
    check = None
    if comprehension_paths:
        check = load_saved_data(comprehension_paths, phase="comprehension", study=study, allow_synthetic=allow_synthetic)
        check_roster(check, roster)
        if check.synthetic != data.synthetic:
            raise ValueError("Cannot combine real and synthetic batches in one reproduction.")
    estimates = estimate_all(data.decisions, study, list(roster))
    output.mkdir(parents=True)
    tables = {"decisions": data.decisions, "coverage": coverage,
              "descriptives": decision_descriptives(data.decisions),
              "attempt_diagnostics": attempt_diagnostics(data), "contrasts": estimates.contrasts,
              "equivalence": estimates.equivalence, "s1_coefficient_changes": estimates.coefficient_changes,
              "s1_belief_diagnostics": estimates.belief_diagnostics,
              "s1_belief_cell_counts": estimates.belief_cells}
    tables["usage_calls"], tables["usage_summary"] = usage_tables(data)
    if check is not None:
        tables["comprehension"] = comprehension_table(check, study, list(roster))
    for name, frame in tables.items():
        _write_csv(frame, output / f"{name}.csv")
    np.savez_compressed(output / "resampling_distributions.npz", **estimates.distributions)
    from kinloyalty.analysis.figures import create_figures

    create_figures(data.decisions, estimates.contrasts, tables.get("comprehension"), study, roster, output, synthetic=data.synthetic)
    _write_metadata(output, data, config, extra_files=check.files if check else None)
    return output


def report_batch(config: str | Path, paths: list[str | Path], output: str | Path, *, phase: str, allow_synthetic: bool = False) -> Path:
    """Write blind pilot mechanics or the separately scored comprehension report."""
    config, output = Path(config).resolve(), Path(output).resolve()
    if phase not in {"pilot", "comprehension"} or output.exists():
        raise ValueError("Choose pilot/comprehension and a new output directory.")
    study, roster = load_analysis_config(config)
    data = load_saved_data(paths, phase=phase, study=study, allow_synthetic=allow_synthetic)
    check_roster(data, roster)
    output.mkdir(parents=True)
    calls, usage = usage_tables(data)
    _write_csv(calls, output / "usage_calls.csv")
    _write_csv(usage, output / "usage_summary.csv")
    if phase == "pilot":
        _write_csv(decision_descriptives(data.decisions, pilot=True), output / "pooled_descriptives.csv")
        _write_csv(attempt_diagnostics(data, pilot=True), output / "pooled_attempt_diagnostics.csv")
        _write_csv(pilot_checks(data, study, list(roster)), output / "mechanical_checks.csv")
        pooled = data.decisions[["model", "decision", "outcome", "belief"]].sort_values(["model", "decision", "outcome", "belief"])
        _write_csv(pooled, output / "pooled_decisions.csv")
    else:
        _write_csv(comprehension_table(data, study, list(roster)), output / "comprehension.csv")
    _write_metadata(output, data, config)
    return output
