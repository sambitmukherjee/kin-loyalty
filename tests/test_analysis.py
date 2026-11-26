"""Check inferential results against independent fits and saved-log failure cases."""

import asyncio
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import statsmodels.formula.api as smf
import yaml

from kinloyalty.analysis.inference import (
    INFERENCE_TIE_TOLERANCE,
    belief_cell_counts, belief_estimability, bootstrap_coefficients, bootstrap_interval, bootstrap_interval_ranks, bootstrap_tost, coefficients,
    contrast_vector, make_design, permutation_contrasts, two_sided_p,
)
from kinloyalty.analysis.loading import load_saved_data
from kinloyalty.analysis.pipeline import analyze_study1, estimate_all, load_analysis_config, report_batch
from kinloyalty.analysis.reports import comprehension_table
from kinloyalty.analysis.reports import attempt_diagnostics, usage_tables
from kinloyalty.analysis.simulate import simulate_study1
from kinloyalty.cli import main
from kinloyalty.logs import json_line, read_jsonl
from kinloyalty.clients.base import ClientError, ModelResponse
from kinloyalty.clients.mock import MockClient
from kinloyalty.manifest import write_manifest
from kinloyalty.runner import RunnerPolicy, run_manifest


ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def batches(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, Path]:
    """Use the actual mock client/runner for balanced main, pilot, and check histories."""
    directory = tmp_path_factory.mktemp("analysis-input")
    study = yaml.safe_load((ROOT / "configs/study1.yaml").read_text())
    study["models_file"] = str(ROOT / "configs/models.yaml")
    study["prompt_directory"] = str(ROOT / "prompts/study1")
    study["data_directory"] = str(ROOT / "data/study1")
    study["results_directory"] = str(ROOT / "results/study1")
    study["main"]["draws_per_model_decision_label_paraphrase"] = 3
    study["main"]["other_lab"]["counts_within_paraphrase"] = [1, 1, 1]
    study["main"]["expected_total_draws"] = 540
    study["main"]["other_lab"]["expected_draws_per_named_model_per_model_decision"] = 3
    study["analysis"]["bootstrap_resamples"] = 99
    study["analysis"]["permutation_resamples"] = 99
    config = directory / "study.yaml"
    config.write_text(yaml.safe_dump(study, sort_keys=False))
    data = directory / "synthetic"
    asyncio.run(simulate_study1(config, data, own_model_effect=12))
    return config, data


def _frame(*, unequal: bool = True) -> pd.DataFrame:
    rng = np.random.default_rng(14)
    rows = []
    for label, shift in [("own_model", 12), ("other_lab", 0), ("fictional", -3)]:
        for p in [1, 2, 3]:
            count = 3 + p + int(label == "other_lab") * 3 if unequal else 12
            for draw in range(count):
                belief = 20 + shift / 2 + rng.normal(0, 4)
                rows.append(dict(model="m", label=label, paraphrase_id=p,
                                 trial_id=f"{label}:{p}:{draw:02d}", belief=belief,
                                 outcome=10 + shift + p * 8 + 1.5 * belief + rng.normal(0, 2)))
    return pd.DataFrame(rows)


def test_fixed_effect_and_belief_fits_match_independent_ols() -> None:
    """Unequal cells must use the actual fixed-effect fit, not raw mean differences."""
    frame = _frame()
    design = make_design(frame, "m", ["own_model", "other_lab", "fictional"], [1, 2, 3])
    vector = contrast_vector(design, "own_model", "other_lab")
    for adjusted in [False, True]:
        fit = smf.ols("outcome ~ C(label) + C(paraphrase_id)" + (" + belief" if adjusted else ""), data=frame).fit()
        expected = fit.params["C(label)[T.own_model]"] - fit.params["C(label)[T.other_lab]"]
        actual = coefficients(design, design.y, design.belief if adjusted else None)[0] @ vector
        assert actual == pytest.approx(expected, abs=1e-10)


def test_bootstrap_keeps_offer_belief_pairs_and_is_order_stable() -> None:
    """A noiseless conditional effect remains exact when paired draws are resampled."""
    frame = _frame(unequal=False)
    frame.outcome = frame.belief * 2 + np.where(frame.label == "own_model", 12, 0) + frame.paraphrase_id * 4
    design = make_design(frame, "m", ["own_model", "other_lab", "fictional"], [1, 2, 3])
    first = bootstrap_coefficients(design, resamples=101, seed=2, key="paired")
    second_design = make_design(frame.sample(frac=1, random_state=9), "m", design.labels, [1, 2, 3])
    second = bootstrap_coefficients(second_design, resamples=101, seed=2, key="paired")
    assert np.array_equal(first[0], second[0])
    assert np.array_equal(first[1], second[1])
    assert np.allclose(first[1] @ contrast_vector(design, "own_model", "other_lab"), 12)


def test_pair_permutation_matches_enumerable_null() -> None:
    """For two zeros versus two tens, two of six assignments have |difference|=10."""
    frame = pd.DataFrame(dict(model=["m"] * 4, label=["own_model"] * 2 + ["other_lab"] * 2,
                              paraphrase_id=[1] * 4, trial_id=list("abcd"), outcome=[0, 0, 10, 10], belief=[None] * 4))
    design = make_design(frame, "m", ["own_model", "other_lab"], [1])
    null = permutation_contrasts(design, "own_model", "other_lab", resamples=10000, seed=8, key="enumerable")
    assert set(np.round(null, 8)) <= {-10, 0, 10}
    assert two_sided_p(-10, null) == pytest.approx(1 / 3, abs=.025)
    assert two_sided_p(0, null) == 1
    assert two_sided_p(100, null) == 1 / 10001


def test_freedman_lane_retains_belief_nuisance_relationship() -> None:
    """Removing a pure belief relationship must leave an exactly zero label statistic."""
    frame = _frame(unequal=False)
    frame.outcome = 3 * frame.belief + 5 * frame.paraphrase_id
    design = make_design(frame, "m", ["own_model", "other_lab", "fictional"], [1, 2, 3])
    null = permutation_contrasts(design, "own_model", "other_lab", resamples=100, seed=5, key="nuisance", adjusted=True)
    assert np.max(np.abs(null)) < 1e-10


def test_freedman_lane_only_shuffles_tested_pair_and_matches_independent_refits(monkeypatch: pytest.MonkeyPatch) -> None:
    """Audit shuffle blocks and compare the cached calculation to explicit full OLS fits."""
    import kinloyalty.analysis.inference as inference

    frame = _frame()
    design = make_design(frame, "m", ["own_model", "other_lab", "fictional"], [1, 2, 3])
    reference = design.frame.copy()
    pair = reference.label.isin(["own_model", "other_lab"])
    reference["merged_label"] = reference.label.where(~pair, "tested_pair")
    reduced = smf.ols("outcome ~ C(merged_label) + belief + C(paraphrase_id)", data=reference).fit()
    fitted, residual = reduced.fittedvalues.to_numpy(), reduced.resid.to_numpy()
    shuffled = residual.copy()
    expected_groups = []
    for paraphrase in [1, 2, 3]:
        indexes = np.flatnonzero(pair & (reference.paraphrase_id == paraphrase))
        expected_groups.append(residual[indexes])
        shuffled[indexes] = residual[indexes[::-1]]
    reference["permuted_offer"] = fitted + shuffled
    np.testing.assert_allclose(reference.loc[~pair, "permuted_offer"], reference.loc[~pair, "outcome"], atol=1e-10)
    full = smf.ols("permuted_offer ~ C(label) + belief + C(paraphrase_id)", data=reference).fit()
    expected = full.params["C(label)[T.own_model]"] - full.params["C(label)[T.other_lab]"]
    seen = []

    class ReversePermutation:
        def permuted(self, values: np.ndarray, axis: int) -> np.ndarray:
            assert axis == 1
            seen.append(values.copy())
            return values[:, ::-1]

    monkeypatch.setattr(inference, "seeded_rng", lambda *args: ReversePermutation())
    actual = permutation_contrasts(design, "own_model", "other_lab", resamples=7, seed=3, key="audit", adjusted=True)
    assert len(seen) == 3
    for values, group in zip(seen, expected_groups, strict=True):
        assert values.shape == (7, len(group))
        np.testing.assert_allclose(values, np.tile(group, (7, 1)), atol=1e-10)
    np.testing.assert_allclose(actual, expected, atol=1e-10)


@pytest.mark.parametrize("observed", [-5., 5.])
def test_permutation_p_counts_numerical_ties_conservatively(observed: float) -> None:
    epsilon = INFERENCE_TIE_TOLERANCE
    assert epsilon == 1e-12
    null = np.array([5 - epsilon / 2, -5 + epsilon / 2,
                     5 - 2 * epsilon, -5 + 2 * epsilon, 5, -5])
    assert two_sided_p(observed, null) == 5 / 7


@pytest.mark.parametrize("sign", [-1, 1])
@pytest.mark.parametrize("gap_in_tolerances", [.5, 1., 2.])
def test_tost_counts_and_interval_checks_share_conservative_tolerance(sign: int, gap_in_tolerances: float) -> None:
    """Endpoints within epsilon of a bound count against equivalence in both checks."""
    value = sign * (5 - gap_in_tolerances * INFERENCE_TIE_TOLERANCE)
    samples = np.concatenate([np.zeros(9500), np.full(500, value)])
    result = bootstrap_tost(0, samples, bound=5)
    expected = gap_in_tolerances > 1
    assert result["equivalent"] is expected
    assert result["equivalence_ci_strictly_inside"] is expected
    assert result["inference_tie_tolerance"] == INFERENCE_TIE_TOLERANCE


@pytest.mark.parametrize("observed,equivalent", [(0, True), (5, False), (-5, False), (8, False), (-8, False)])
def test_tost_null_and_equivalence_boundaries(observed: float, equivalent: bool) -> None:
    """Both one-sided tests, including effects exactly on a bound, determine equivalence."""
    samples = observed + np.linspace(-2, 2, 10001)
    result = bootstrap_tost(observed, samples, bound=5)
    assert result["equivalent"] is equivalent
    assert result["p_tost"] == max(result["p_lower"], result["p_upper"])
    assert result["p_lower"] > 0 and result["p_upper"] > 0
    if observed == 5:
        assert result["p_upper"] == pytest.approx(.5, abs=.001)
    if observed == -5:
        assert result["p_lower"] == pytest.approx(.5, abs=.001)


def test_percentile_tost_uses_raw_tail_areas_on_an_asymmetric_distribution() -> None:
    """A positive upper tail cannot be ignored by reflecting centered bootstrap errors."""
    samples = np.concatenate([np.zeros(9500), np.full(500, 6.)])
    result = bootstrap_tost(0, samples, bound=5)
    assert result["p_lower"] == 1 / 10001
    assert result["p_upper"] == 501 / 10001
    assert result["equivalent"] is False
    # Once the bootstrap estimates are supplied, their tail areas are not recentered.
    shifted_reported_estimate = bootstrap_tost(2, samples, bound=5)
    assert shifted_reported_estimate["p_lower"] == result["p_lower"]
    assert shifted_reported_estimate["p_upper"] == result["p_upper"]


def test_percentile_tost_counts_values_exactly_on_each_bound() -> None:
    samples = np.concatenate([np.full(20, -5.), np.zeros(9960), np.full(20, 5.)])
    result = bootstrap_tost(0, samples, bound=5)
    assert result["p_lower"] == result["p_upper"] == 21 / 10001
    assert result["p_tost"] == 21 / 10001 and result["equivalent"]


@pytest.mark.parametrize("tail_count", [499, 500])
@pytest.mark.parametrize("tail_value", [-6., -5., 5., 6.])
def test_corrected_tost_and_strict_percentile_endpoints_agree_at_the_cutoff(tail_count: int, tail_value: float) -> None:
    """The 500th/9,501st limits invert inclusive counts, including exact-bound ties."""
    samples = np.concatenate([np.zeros(10000 - tail_count), np.full(tail_count, tail_value)])
    result = bootstrap_tost(0, samples, bound=5)
    assert result["equivalent"] is (tail_count == 499)
    assert result["equivalence_ci_strictly_inside"] is result["equivalent"]
    assert (result["equivalence_ci_lower_rank"], result["equivalence_ci_upper_rank"]) == (500, 9501)
    assert (result["contrast_ci_lower_rank"], result["contrast_ci_upper_rank"]) == (250, 9751)
    if tail_count == 500:
        endpoint = result["equivalence_ci_low"] if tail_value < 0 else result["equivalence_ci_high"]
        assert endpoint == tail_value


def test_tost_plus_one_and_strict_alpha_also_match_with_small_test_counts() -> None:
    """At B=99, p=.05 must fail; the generalized rank convention respects strictness."""
    for count, equivalent in [(3, True), (4, False)]:
        samples = np.concatenate([np.zeros(99 - count), np.full(count, 5.)])
        result = bootstrap_tost(0, samples, bound=5)
        assert result["equivalent"] is equivalent
        assert result["equivalence_ci_strictly_inside"] is equivalent
    assert bootstrap_interval_ranks(99, .9) == (4, 96)


@pytest.mark.parametrize("samples", [np.array([]), np.array([0., np.nan]), np.array([0., np.inf])])
def test_tost_does_not_silently_drop_missing_or_nonfinite_estimates(samples: np.ndarray) -> None:
    with pytest.raises(ValueError, match="nonempty finite"):
        bootstrap_tost(0, samples, bound=5)


def test_all_bootstrap_intervals_use_explicit_empirical_ranks_without_interpolation() -> None:
    """The asymmetric sample exposes reflection/interpolation; original pairing is preserved."""
    samples = (np.arange(10000, dtype=float) ** 2)[::-1]
    original = samples.copy()
    for level, ranks in [(.9, (500, 9501)), (.95, (250, 9751))]:
        assert bootstrap_interval_ranks(10000, level) == ranks
        low, high = bootstrap_interval(samples, level)
        assert (low, high) == ((ranks[0] - 1) ** 2, (ranks[1] - 1) ** 2)
        assert low in samples and high in samples
    assert np.array_equal(samples, original)


def test_empty_cells_and_unidentifiable_beliefs_fail_explicitly() -> None:
    frame = _frame()
    with pytest.raises(ValueError, match="empty"):
        make_design(frame[frame.paraphrase_id != 3], "m", ["own_model", "other_lab", "fictional"], [1, 2, 3])
    frame.belief = frame.paraphrase_id
    design = make_design(frame, "m", ["own_model", "other_lab", "fictional"], [1, 2, 3])
    with pytest.raises(ValueError, match="not identifiable"):
        coefficients(design, design.y, design.belief)


def test_main_analysis_rejects_other_phases_and_implicit_synthetic(batches: tuple[Path, Path]) -> None:
    config, directory = batches
    study, _ = load_analysis_config(config)
    for phase in ["pilot", "comprehension"]:
        with pytest.raises(ValueError, match="Only study1 main"):
            load_saved_data([directory / phase], phase="main", study=study, allow_synthetic=True)
    with pytest.raises(ValueError, match="Synthetic input"):
        load_saved_data([directory / "main"], phase="main", study=study)


def test_tampered_duplicate_and_pending_histories_are_rejected(batches: tuple[Path, Path], tmp_path: Path) -> None:
    config, directory = batches
    study, _ = load_analysis_config(config)
    records = read_jsonl(directory / "main/attempts.jsonl")
    tampered = tmp_path / "tampered.jsonl"
    records[0]["outcome"]["parsed_json"]["reason"] = "Changed without altering the response."
    tampered.write_text("".join(json_line(record) for record in records))
    with pytest.raises(ValueError, match="validation"):
        load_saved_data([tampered], phase="main", study=study, allow_synthetic=True)
    duplicate = tmp_path / "duplicate.jsonl"
    duplicate.write_text(json_line(records[1]) * 2)
    with pytest.raises(ValueError, match="Duplicate"):
        load_saved_data([duplicate], phase="main", study=study, allow_synthetic=True)
    duplicate.with_name(duplicate.name + ".pending.json").write_text("{}")
    with pytest.raises(ValueError, match="Pending"):
        load_saved_data([duplicate], phase="main", study=study, allow_synthetic=True)


def test_incomplete_main_refuses_inference(batches: tuple[Path, Path], tmp_path: Path) -> None:
    config, directory = batches
    records = read_jsonl(directory / "main/attempts.jsonl")
    missing = tmp_path / "incomplete.jsonl"
    missing.write_text("".join(json_line(record) for record in records[1:]))
    with pytest.raises(ValueError, match="all configured draws"):
        analyze_study1(config, [missing], tmp_path / "output", allow_synthetic=True)
    assert not (tmp_path / "output").exists()


def test_comprehension_scoring_includes_all_planned_draws(batches: tuple[Path, Path]) -> None:
    config, directory = batches
    study, models = load_analysis_config(config)
    data = load_saved_data([directory / "comprehension"], phase="comprehension", study=study, allow_synthetic=True)
    table = comprehension_table(data, study, list(models))
    assert table.model_pass.eq(True).all()
    assert table[table.scored].correct.eq(20).all()
    assert table[~table.scored].label_pass.isna().all()
    model = next(iter(models))
    indexes = data.decisions.index[(data.decisions.model == model) & (data.decisions.label == "own_model")]
    data.decisions.loc[indexes[:2], "same_model"] = "unsure"
    assert comprehension_table(data, study, list(models)).query("model == @model").model_pass.eq(True).all()
    data.decisions.loc[indexes[2], "same_model"] = "no"
    assert comprehension_table(data, study, list(models)).query("model == @model").model_pass.eq(False).all()


def test_pilot_report_never_groups_or_exports_decisions_by_label(batches: tuple[Path, Path], tmp_path: Path) -> None:
    config, directory = batches
    output = report_batch(config, [directory / "pilot"], tmp_path / "pilot", phase="pilot", allow_synthetic=True)
    for name in ["pooled_descriptives", "pooled_attempt_diagnostics", "pooled_decisions", "mechanical_checks"]:
        frame = pd.read_csv(output / f"{name}.csv")
        assert not {"label", "left", "right", "counterparty_model_text", "trial_id"} & set(frame)
    assert len(pd.read_csv(output / "pooled_descriptives.csv")) == 12
    assert not (output / "contrasts.csv").exists()
    checks = pd.read_csv(output / "mechanical_checks.csv")
    assert checks.parse_rate_pass.all() and checks.all_inputs_below_limit.all()


def test_end_to_end_recovers_effect_and_reproduces_artifacts(batches: tuple[Path, Path], tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Exercise real log loading, all inference, PDF/PNG output, and byte-identical rerun."""
    config, directory = batches
    import kinloyalty.clients.factory as factory

    def no_credentials(*args: object, **kwargs: object) -> None:
        raise AssertionError("Analysis must never load API keys.")

    monkeypatch.setattr(factory, "load_api_keys", no_credentials)
    first = analyze_study1(config, [directory / "main"], tmp_path / "first", allow_synthetic=True,
                           comprehension_paths=[directory / "comprehension"])
    second = analyze_study1(config, [directory / "main"], tmp_path / "second", allow_synthetic=True,
                            comprehension_paths=[directory / "comprehension"])
    estimates = pd.read_csv(first / "contrasts.csv")
    primary = estimates[estimates.designation == "primary_P1"].iloc[0]
    assert primary.estimate == pytest.approx(12, abs=2)
    assert primary.ci_low > 0 and primary.permutation_p <= .05
    per_model = estimates[(estimates.decision == "dictator") & (estimates.family == "own_vs_other") & (estimates.scope != "pooled")]
    assert primary.estimate == pytest.approx(per_model.estimate.mean())
    assert len(estimates) == 150
    assert len(pd.read_csv(first / "s1_coefficient_changes.csv")) == 30
    assert not pd.read_csv(first / "equivalence.csv").equivalent.iloc[0]
    equivalence = pd.read_csv(first / "equivalence.csv").iloc[0]
    assert equivalence.contrast_ci_low == pytest.approx(primary.ci_low)
    assert equivalence.contrast_ci_high == pytest.approx(primary.ci_high)
    assert primary.ci_method == equivalence.contrast_ci_method == "percentile_count_matched"
    with np.load(first / "resampling_distributions.npz") as distributions:
        pooled = distributions["dictator:outcome:unadjusted:own_model-other_lab:pooled:bootstrap"]
        assert len(pooled) == equivalence.bootstrap_resamples
        assert equivalence.lower_tail_count == np.count_nonzero(pooled <= -5 + INFERENCE_TIE_TOLERANCE)
        assert equivalence.upper_tail_count == np.count_nonzero(pooled >= 5 - INFERENCE_TIE_TOLERANCE)
        assert equivalence.equivalence_ci_strictly_inside == equivalence.equivalent
    for name in ["main_distributions", "s1_coefficients", "responder_distributions", "comprehension"]:
        assert (first / f"{name}.pdf").read_bytes().startswith(b"%PDF")
        assert (first / f"{name}.png").read_bytes().startswith(b"\x89PNG")
    assert json.loads((first / "provenance.json").read_text())["synthetic"] is True
    assert (first / "artifacts.sha256.json").read_bytes() == (second / "artifacts.sha256.json").read_bytes()
    with pytest.raises(ValueError, match="already exists"):
        analyze_study1(config, [directory / "main"], first, allow_synthetic=True)


def test_cli_reproduce_refuses_missing_and_ineligible_data(batches: tuple[Path, Path], tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    config, directory = batches
    with pytest.raises(SystemExit) as error:
        main(["reproduce", "--config", str(config), "--data", str(directory / "pilot"),
              "--output", str(tmp_path / "out"), "--allow-synthetic"])
    assert error.value.code == 2
    assert "Only study1 main" in capsys.readouterr().err
    assert not (tmp_path / "out").exists()


def test_simulation_cannot_write_into_real_study_directories(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="outside real study"):
        asyncio.run(simulate_study1(ROOT / "configs/study1.yaml", ROOT / "data/study1/main/synthetic"))
    assert not (ROOT / "data/study1/main/synthetic").exists()


def test_api_retry_then_two_invalid_replies_remain_excluded_not_zero(batches: tuple[Path, Path], tmp_path: Path) -> None:
    """Diagnostics retain API errors, one re-asked draw, exclusion, and null usage."""
    config, directory = batches
    trial = read_jsonl(directory / "main/manifest.jsonl")[0]
    manifest, log = tmp_path / "manifest.jsonl", tmp_path / "attempts.jsonl"
    write_manifest([trial], manifest)
    client = MockClient(scripts={trial["trial_id"]: [ClientError("rate_limit"), ModelResponse("{"), ModelResponse("{")]})
    summary = asyncio.run(run_manifest(manifest, log, client, policy=RunnerPolicy(backoff_initial_seconds=0)))
    assert summary.excluded == 1 and summary.calls_started == 3
    study, _ = load_analysis_config(config)
    data = load_saved_data([log], phase="main", study=study, allow_synthetic=True)
    assert data.decisions.empty
    diagnostics = attempt_diagnostics(data).iloc[0]
    assert diagnostics.excluded == 1 and diagnostics.reasked_draws == 1 and diagnostics.api_errors == 1
    calls, usage = usage_tables(data)
    assert len(calls) == 3 and usage.observed.eq(0).all()
    assert usage.missing.eq(2).all()


def test_incomplete_comprehension_does_not_claim_a_pass(batches: tuple[Path, Path], tmp_path: Path) -> None:
    config, directory = batches
    records = read_jsonl(directory / "comprehension/attempts.jsonl")
    log = tmp_path / "attempts.jsonl"
    log.write_text("".join(json_line(record) for record in records[1:]))
    study, models = load_analysis_config(config)
    data = load_saved_data([log], phase="comprehension", study=study, allow_synthetic=True)
    table = comprehension_table(data, study, list(models))
    missing = table[table.not_started > 0].iloc[0]
    assert missing.not_started == 1 and not missing.complete and missing.label_pass is None


def test_real_and_synthetic_batches_cannot_be_combined(batches: tuple[Path, Path], tmp_path: Path) -> None:
    config, directory = batches
    records = read_jsonl(directory / "main/attempts.jsonl")
    records[0]["execution_mode"] = "live"
    records[0]["synthetic"] = False
    log = tmp_path / "mixed.jsonl"
    log.write_text("".join(json_line(record) for record in records))
    study, _ = load_analysis_config(config)
    with pytest.raises(ValueError, match="mix execution"):
        load_saved_data([log], phase="main", study=study, allow_synthetic=True)


def test_pooled_contrast_keeps_equal_weights_when_model_counts_differ(batches: tuple[Path, Path]) -> None:
    """A model with fewer retained draws still contributes one quarter of pooled P1."""
    config, directory = batches
    study, models = load_analysis_config(config)
    data = load_saved_data([directory / "main"], phase="main", study=study, allow_synthetic=True)
    frame = data.decisions.copy()
    first, second = list(models)[:2]
    frame.loc[(frame.model == first) & (frame.label == "own_model"), "outcome"] += 15
    frame.loc[(frame.model == second) & (frame.label == "own_model"), "outcome"] -= 10
    frame = frame[(frame.model != first) | (frame.draw_index == 1)]
    estimates = estimate_all(frame, study, list(models)).contrasts
    per_model = estimates[(estimates.decision == "dictator") & (estimates.family == "own_vs_other") & (estimates.scope != "pooled")]
    pooled = estimates[estimates.designation == "primary_P1"].estimate.iloc[0]
    assert pooled == pytest.approx(per_model.estimate.mean())
    indexed = per_model.set_index("scope").loc[list(models)].estimate
    assert abs(pooled - np.average(indexed, weights=[1, 3, 3, 3])) > 1


def _modal_frame(nonmodal: int) -> pd.DataFrame:
    rows = []
    labels = ["own_model", "other_lab", "fictional", "not_disclosed", "human"]
    for label in labels:
        for paraphrase in [1, 2, 3]:
            for draw in range(20):
                rows.append({"model": "m", "label": label, "paraphrase_id": paraphrase,
                             "trial_id": f"{label}:{paraphrase}:{draw:02d}", "outcome": 40 + draw % 7,
                             "belief": 50})
    frame = pd.DataFrame(rows)
    # Spread deviations across cells so 50 remains each cell's mode.
    positions = [cell * 20 + draw for draw in range(2) for cell in range(15)]
    frame.loc[positions[:nonmodal], "belief"] = 51
    return frame


@pytest.mark.parametrize("nonmodal,estimable", [(0, False), (29, False), (30, True)])
def test_fixed_modal_count_rule_has_exact_thirty_of_three_hundred_boundary(nonmodal: int, estimable: bool) -> None:
    """The user-specified rule is strict below 10%; exactly 30/300 passes."""
    frame = _modal_frame(nonmodal)
    design = make_design(frame, "m", list(frame.label.unique()), [1, 2, 3])
    result = belief_estimability(design, minimum_nonmodal_percent=10)
    assert result["n"] == 300 and result["required_nonmodal_draws"] == 30
    assert result["nonmodal_draws"] == nonmodal and result["estimable"] is estimable
    if not estimable:
        assert result["not_estimable_reason"] == "insufficient_nonmodal_belief_draws"


def test_cell_mode_ties_use_lowest_and_do_not_use_the_global_mode() -> None:
    """Cell-specific modes and lowest-value tie breaking are auditable in the outputs."""
    frame = _modal_frame(0)
    for index, (_, cell) in enumerate(frame.groupby(["label", "paraphrase_id"])):
        frame.loc[cell.index[:10], "belief"] = 20 + index
        frame.loc[cell.index[10:], "belief"] = 60 + index
    design = make_design(frame, "m", list(frame.label.unique()), [1, 2, 3])
    cells = belief_cell_counts(design)
    assert len(cells) == 15 and all(cell["nonmodal_draws"] == 10 for cell in cells)
    assert {cell["mode"] for cell in cells} == set(range(20, 35))
    assert belief_estimability(design, minimum_nonmodal_percent=10)["nonmodal_draws"] == 150
    # Varying cell modes alone must not qualify as within-cell variation.
    for index, (_, cell) in enumerate(frame.groupby(["label", "paraphrase_id"])):
        frame.loc[cell.index, "belief"] = 20 + index
    design = make_design(frame, "m", list(frame.label.unique()), [1, 2, 3])
    assert belief_estimability(design, minimum_nonmodal_percent=10)["nonmodal_draws"] == 0


def test_singular_bootstrap_replicates_are_preserved_without_redrawing() -> None:
    """Rare belief variation can disappear in resamples; those draws remain explicit."""
    frame = pd.DataFrame({"model": ["m"] * 4, "label": ["own_model"] * 2 + ["other_lab"] * 2,
                          "paraphrase_id": [1] * 4, "trial_id": list("abcd"),
                          "outcome": [40, 42, 40, 40], "belief": [50, 51, 50, 50]})
    design = make_design(frame, "m", ["own_model", "other_lab"], [1])
    assert belief_estimability(design, minimum_nonmodal_percent=10)["estimable"]
    ordinary, adjusted = bootstrap_coefficients(design, resamples=1000, seed=7, key="rare")
    assert len(ordinary) == len(adjusted) == 1000
    assert np.isfinite(ordinary).all()
    invalid = ~np.isfinite(adjusted).all(axis=1)
    assert .4 < invalid.mean() < .6


def test_one_nonestimable_model_does_not_disappear_from_adjusted_pool(batches: tuple[Path, Path]) -> None:
    """Keep every scope, report unavailable adjusted results, and retain other analyses."""
    config, directory = batches
    study, models = load_analysis_config(config)
    data = load_saved_data([directory / "main"], phase="main", study=study, allow_synthetic=True)
    frame = data.decisions.copy()
    model = next(iter(models))
    frame.loc[(frame.model == model) & (frame.decision == "ultimatum_proposer"), "belief"] = 50
    result = estimate_all(frame, study, list(models))
    rows = result.contrasts
    adjusted = rows[(rows.decision == "ultimatum_proposer") & (rows.method == "belief_adjusted")]
    unavailable = adjusted[adjusted.scope.isin([model, "pooled"])]
    assert len(rows) == 150 and len(unavailable) == 12
    assert not unavailable.estimable.any()
    assert unavailable.estimate.isna().all() and unavailable.permutation_p.isna().all()
    assert unavailable.non_estimable_models.eq(model).all()
    assert adjusted[~adjusted.scope.isin([model, "pooled"])].estimable.all()
    assert rows[rows.method == "unadjusted"].estimable.all()
    assert len(result.coefficient_changes) == 30
    assert result.coefficient_changes.query("scope == 'pooled'").unadjusted_minus_adjusted.isna().all()
    diagnostic = result.belief_diagnostics.set_index("model").loc[model]
    assert diagnostic.nonmodal_draws == 0 and diagnostic.bootstrap_fits_attempted == 0
    assert diagnostic.rank_deficient and not diagnostic.estimable
    assert len(result.belief_cells) == 60


def test_s1_difference_interval_uses_the_paired_bootstrap_and_explicit_sign(batches: tuple[Path, Path]) -> None:
    """The difference and its CI use paired before-minus-after draws, including pooling."""
    config, directory = batches
    study, models = load_analysis_config(config)
    data = load_saved_data([directory / "main"], phase="main", study=study, allow_synthetic=True)
    result = estimate_all(data.decisions, study, list(models))
    for scope in [*models, "pooled"]:
        prefix = "ultimatum_proposer:outcome:"
        suffix = f":own_model-other_lab:{scope}:bootstrap"
        before = result.distributions[prefix + "unadjusted" + suffix]
        after = result.distributions[prefix + "belief_adjusted" + suffix]
        difference = result.distributions[prefix + "unadjusted_minus_adjusted" + suffix]
        assert np.array_equal(difference, before - after) or np.allclose(difference, before - after, atol=1e-12)
        row = result.coefficient_changes.query("scope == @scope and left == 'own_model' and right == 'other_lab'").iloc[0]
        low, high = bootstrap_interval(difference)
        assert row.ci_low == pytest.approx(low) and row.ci_high == pytest.approx(high)
        assert "not a causal mediation" in row.interpretation
    assert "share_explained" not in result.coefficient_changes
    assert "permutation_p" not in result.coefficient_changes
    assert not any(":unadjusted_minus_adjusted:" in key and key.endswith(":permutation") for key in result.distributions)


def test_pooled_permutation_replicates_average_all_models_at_the_same_index(batches: tuple[Path, Path]) -> None:
    """Every pooled replicate combines all four model contrasts, not their p-values."""
    config, directory = batches
    study, models = load_analysis_config(config)
    data = load_saved_data([directory / "main"], phase="main", study=study, allow_synthetic=True)
    result = estimate_all(data.decisions, study, list(models))
    pooled_rows = result.contrasts[result.contrasts.scope == "pooled"]
    for row in pooled_rows.itertuples():
        prefix = f"{row.decision}:{row.outcome}:{row.method}:{row.left}-{row.right}:"
        per_model = np.column_stack([result.distributions[prefix + model + ":permutation"] for model in models])
        pooled = result.distributions[prefix + "pooled:permutation"]
        assert per_model.shape == (study["analysis"]["permutation_resamples"], 4)
        assert np.array_equal(pooled, per_model.mean(axis=1), equal_nan=True)
        if np.isfinite(pooled).all():
            count = np.count_nonzero(np.abs(pooled) >= abs(row.estimate) - INFERENCE_TIE_TOLERANCE)
            assert row.permutation_p == (1 + count) / (len(pooled) + 1)


def test_singular_adjusted_resamples_withhold_ci_but_keep_identifiable_point(batches: tuple[Path, Path]) -> None:
    """No bootstrap deletion/redraw or three-model interval is silently substituted."""
    config, directory = batches
    study, models = load_analysis_config(config)
    study["analysis"]["bootstrap_resamples"] = 999
    data = load_saved_data([directory / "main"], phase="main", study=study, allow_synthetic=True)
    model = next(iter(models))
    frame = data.decisions.copy()
    rare = (frame.model == model) & (frame.decision == "ultimatum_proposer")
    frame = frame[~rare | (frame.draw_index <= 2)].copy()
    rare = (frame.model == model) & (frame.decision == "ultimatum_proposer")
    frame.loc[rare, "belief"] = 50
    frame.loc[rare & (frame.label == "own_model") & (frame.draw_index == 1), "belief"] = 51
    result = estimate_all(frame, study, list(models))
    diagnostic = result.belief_diagnostics.set_index("model").loc[model]
    assert diagnostic.n == 30 and diagnostic.nonmodal_draws == 3 and diagnostic.estimable
    assert diagnostic.bootstrap_numerical_failures > 0
    adjusted = result.contrasts.query("method == 'belief_adjusted'")
    affected = adjusted[adjusted.scope.isin([model, "pooled"])]
    assert affected.estimable.all() and affected.estimate.notna().all()
    assert not affected.interval_available.any() and affected.ci_low.isna().all()
    assert affected.permutation_p.notna().all()
    assert affected.bootstrap_unavailable_count.gt(0).all()
    assert result.coefficient_changes.query("scope == 'pooled'").ci_low.isna().all()


def test_fixed_modal_rule_cannot_be_silently_tuned(batches: tuple[Path, Path], tmp_path: Path) -> None:
    config, _ = batches
    study = yaml.safe_load(config.read_text())
    study["analysis"]["s1_belief_estimability"]["minimum_nonmodal_percent"] = 5
    modified = tmp_path / "modified.yaml"
    modified.write_text(yaml.safe_dump(study))
    with pytest.raises(ValueError, match="Unsupported analysis specification"):
        load_analysis_config(modified)


def test_nonestimable_model_is_exported_and_figure_keeps_its_position(batches: tuple[Path, Path], tmp_path: Path) -> None:
    """A legitimate constant-belief mock run completes reproduction with explicit NE rows."""
    config, directory = batches
    study, models = load_analysis_config(config)
    model = next(iter(models))
    trials = read_jsonl(directory / "main/manifest.jsonl")
    previous = {record["trial_id"]: record for record in read_jsonl(directory / "main/attempts.jsonl")}
    scripts = {}
    for trial in trials:
        if trial["model"] == model and trial["decision"] == "ultimatum_proposer":
            parsed = dict(previous[trial["trial_id"]]["outcome"]["parsed_json"])
            parsed["smallest_offer_you_expect_counterparty_to_accept"] = 50
            scripts[trial["trial_id"]] = [ModelResponse(json.dumps(parsed), returned_model_version="mock/constant-belief",
                                                       raw_response={"synthetic": True, "content": parsed}, finish_reason="stop")]
    manifest, log = tmp_path / "manifest.jsonl", tmp_path / "attempts.jsonl"
    write_manifest(trials, manifest)
    asyncio.run(run_manifest(manifest, log, MockClient(seed=study["seeds"]["mock"], scripts=scripts)))
    output = analyze_study1(config, [log], tmp_path / "output", allow_synthetic=True)
    diagnostics = pd.read_csv(output / "s1_belief_diagnostics.csv").set_index("model")
    assert not diagnostics.loc[model, "estimable"] and len(diagnostics) == 4
    contrasts = pd.read_csv(output / "contrasts.csv")
    assert len(contrasts) == 150
    assert not contrasts.query("method == 'belief_adjusted' and scope == 'pooled'").estimable.any()
    assert (output / "s1_coefficients.pdf").read_bytes().startswith(b"%PDF")
    assert len(pd.read_csv(output / "s1_belief_cell_counts.csv")) == 60
