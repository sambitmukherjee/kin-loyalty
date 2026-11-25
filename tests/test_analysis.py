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
    bootstrap_coefficients, bootstrap_interval, bootstrap_tost, coefficients,
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


def test_basic_interval_reflects_skewed_bootstrap_errors() -> None:
    """The interval is the reverse-error interval, not an accidental percentile CI."""
    samples = np.array([10., 11., 12., 20., 30.])
    low, high = bootstrap_interval(10, samples, .8)
    assert low == pytest.approx(20 - np.quantile(samples, .9))
    assert high == pytest.approx(20 - np.quantile(samples, .1))


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
    assert not (ROOT / "data/study1/main").exists()


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
    estimates, _, _, _ = estimate_all(frame, study, list(models))
    per_model = estimates[(estimates.decision == "dictator") & (estimates.family == "own_vs_other") & (estimates.scope != "pooled")]
    pooled = estimates[estimates.designation == "primary_P1"].estimate.iloc[0]
    assert pooled == pytest.approx(per_model.estimate.mean())
    indexed = per_model.set_index("scope").loc[list(models)].estimate
    assert abs(pooled - np.average(indexed, weights=[1, 3, 3, 3])) > 1
