"""Summarize decisions and call mechanics, preserving pilot blinding and missing usage."""

from typing import Any

import numpy as np
import pandas as pd

from kinloyalty.analysis.loading import SavedData


def decision_descriptives(frame: pd.DataFrame, *, pilot: bool = False) -> pd.DataFrame:
    """Describe whole-dollar distributions; pilot grouping never includes labels."""
    group = ["model", "decision"] + ([] if pilot else ["label"])
    if frame.empty:
        return pd.DataFrame(columns=[*group, "n", "mean", "median", "sd", "share_equal_split", "share_zero", "modal_share", "distinct_values"])
    rows = []
    for keys, cell in frame.groupby(group, sort=True):
        values = cell.outcome
        rows.append({**dict(zip(group, keys, strict=True)), "n": len(values),
                     "mean": values.mean(), "median": values.median(),
                     "sd": values.std(ddof=1), "share_equal_split": (values == 50).mean(),
                     "share_zero": (values == 0).mean(),
                     "modal_share": values.value_counts().max() / len(values),
                     "distinct_values": values.nunique()})
    return pd.DataFrame(rows)


def attempt_diagnostics(data: SavedData, *, pilot: bool = False) -> pd.DataFrame:
    """Count re-asked/excluded/unfinished draws; never classify API errors as exclusions."""
    group = ["model", "decision"] + ([] if pilot else ["label"])
    return data.trials.groupby(group, sort=True).agg(
        draws_observed=("trial_id", "count"), valid=("valid", "sum"),
        reasked_draws=("reasks", "sum"), excluded=("excluded", "sum"),
        unfinished=("unfinished", "sum"), attempts=("attempts", "sum"),
        api_errors=("api_errors", "sum"),
    ).reset_index()


def usage_tables(data: SavedData) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Retain every response's usage, including invalid replies and missing cache fields."""
    rows = []
    for record in sorted(data.attempts, key=lambda record: record["record_id"]):
        response = record["response"]
        rows.append({"record_id": record["record_id"], "trial_id": record["trial_id"],
                     "model": record["model"], "provider": record["request"]["provider"],
                     "has_response": response is not None,
                     "valid": record["outcome"]["valid"],
                     "returned_model_version": response["returned_model_version"] if response else None,
                     "finish_reason": response["finish_reason"] if response else None,
                     "output_truncated": response["output_truncated"] if response else None,
                     **{name: response["usage"][name] if response else None for name in (
                         "input_tokens", "output_tokens", "reasoning_tokens", "cache_read_tokens", "cache_write_tokens")}})
    calls = pd.DataFrame(rows)
    summary = []
    for (model, provider), cell in calls.groupby(["model", "provider"], sort=True):
        for metric in ("input_tokens", "output_tokens", "reasoning_tokens", "cache_read_tokens", "cache_write_tokens"):
            values = cell.loc[cell.has_response, metric].dropna()
            summary.append({"model": model, "provider": provider, "metric": metric,
                            "responses": int(cell.has_response.sum()), "observed": len(values),
                            "missing": int(cell.has_response.sum()) - len(values),
                            "mean": values.mean(), "median": values.median(),
                            "minimum": values.min(), "maximum": values.max()})
    return calls, pd.DataFrame(summary)


def comprehension_table(data: SavedData, study: dict[str, Any], models: list[str]) -> pd.DataFrame:
    """Apply the preregistered 18/20 rule with exclusions in the planned denominator."""
    rows = []
    expected = study["comprehension"]["draws_per_model_label"]
    minimum = study["comprehension"]["minimum_correct_per_scored_label"]
    for model in models:
        for label in study["comprehension"]["labels"]:
            decisions = data.decisions
            cell = decisions[(decisions.model == model) & (decisions.label == label)] if not decisions.empty else decisions
            status = data.trials[(data.trials.model == model) & (data.trials.label == label)]
            if len(status) > expected:
                raise ValueError("Comprehension cell exceeds its planned draw count.")
            counts = {answer: int((cell.same_model == answer).sum()) if not cell.empty else 0
                      for answer in study["comprehension"]["allowed_answers"]}
            correct_answer = study["comprehension"]["expected_answers"].get(label)
            complete = len(status) == expected and not status.unfinished.any()
            passed = counts.get(correct_answer, 0) >= minimum if correct_answer and complete else None
            rows.append({"model": model, "label": label, "planned": expected, "valid": len(cell),
                         "excluded": int(status.excluded.sum()), "unfinished": int(status.unfinished.sum()),
                         "not_started": expected - len(status), "complete": complete,
                         **{f"n_{answer}": count for answer, count in counts.items()},
                         **{f"share_{answer}": count / expected for answer, count in counts.items()},
                         "expected_answer": correct_answer, "correct": counts.get(correct_answer, np.nan),
                         "scored": correct_answer is not None, "label_pass": passed})
    table = pd.DataFrame(rows)
    passes = {}
    for model, cell in table[table.scored].groupby("model"):
        passes[model] = bool(cell.label_pass.eq(True).all()) if cell.complete.all() else None
    table["model_pass"] = table.model.map(passes)
    return table


def pilot_checks(data: SavedData, study: dict[str, Any], models: list[str]) -> pd.DataFrame:
    """Report mechanical pilot checks per model, pooling every label."""
    rows = []
    for model in models:
        records = [record for record in data.attempts if record["model"] == model]
        responses = [record for record in records if record["response"] is not None]
        decisions = data.decisions[data.decisions.model == model] if not data.decisions.empty else data.decisions
        valid = sum(record["outcome"]["valid"] is True for record in responses)
        inputs = [record["response"]["usage"]["input_tokens"] for record in responses]
        cache_reads = [record["response"]["usage"]["cache_read_tokens"] for record in responses]
        cache_writes = [record["response"]["usage"]["cache_write_tokens"] for record in responses]
        zero_cache_required = any(record["request"]["provider"] in {"openai", "anthropic"} for record in records)
        dictator = decisions[decisions.decision == "dictator"] if not decisions.empty else decisions
        statuses = data.trials[data.trials.model == model]
        planned = study["pilot"]["draws_per_model_decision"] * len(study["decisions"])
        if len(statuses) > planned:
            raise ValueError("Pilot model exceeds its planned draw count.")
        row = {"model": model, "planned_draws": planned, "draws_observed": len(statuses),
               "not_started": planned - len(statuses), "unfinished": int(statuses.unfinished.sum()),
               "complete": len(statuses) == planned and not statuses.unfinished.any(),
               "response_attempts": len(responses),
               "valid_response_rate": valid / len(responses) if responses else None,
               "parse_rate_pass": valid / len(responses) > study["pilot"]["parse_rate_must_exceed"] if responses else None,
               "truncated": sum(record["response"]["output_truncated"] for record in responses),
               "missing_reasoning_counts": sum(record["response"]["usage"]["reasoning_tokens"] is None for record in responses),
               "missing_input_counts": inputs.count(None),
               "missing_cache_read_counts": cache_reads.count(None),
               "missing_cache_write_counts": cache_writes.count(None),
               "zero_cache_required": zero_cache_required,
               "zero_cache_verified": all(value == 0 for value in [*cache_reads, *cache_writes]) if responses and zero_cache_required else None,
               "input_max": max((value for value in inputs if value is not None), default=None),
               "all_inputs_below_limit": all(value is not None and value < study["pilot"]["prompt_tokens_must_be_below"] for value in inputs) if responses else None,
               "dictator_all_zero": bool(dictator.outcome.eq(0).all()) if not dictator.empty else None}
        for decision in study["decisions"]:
            cell = decisions[decisions.decision == decision] if not decisions.empty else decisions
            row[f"{decision}_varies"] = cell.outcome.nunique() > 1 if not cell.empty else None
        rows.append(row)
    return pd.DataFrame(rows)
