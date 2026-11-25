"""Check attempt histories and reconstruct trial state without rerendering prompts."""

from dataclasses import dataclass
from typing import Any

from kinloyalty.clients.base import ModelResponse, TokenUsage
from kinloyalty.logs import content_hash
from kinloyalty.validate import validate_response


@dataclass
class TrialState:
    """Track API attempts separately from invalid model replies and terminal draws."""

    attempts: int = 0
    invalid_replies: int = 0
    final: bool = False
    excluded: bool = False


def check_record_binding(
    record: dict[str, Any], trials: dict[str, dict[str, Any]], manifest_hash: str, mode: str,
) -> None:
    """Refuse to combine logs with another plan, altered request, or execution backend."""
    trial = trials.get(record["trial_id"])
    if (
        trial is None or record.get("manifest_sha256") != manifest_hash
        or record.get("execution_mode") != mode
        or record.get("synthetic") != (mode == "mock")
        or record.get("trial_sha256") != content_hash(trial)
        or content_hash(record.get("request")) != content_hash(trial["request"])
        or any(content_hash(record.get(key)) != content_hash(value) for key, value in trial.items() if key != "request")
    ):
        raise ValueError("Attempt history does not match the frozen manifest and execution mode.")


def reconstruct_states(
    trials: dict[str, dict[str, Any]], records: list[dict[str, Any]],
    manifest_hash: str, mode: str, invalid_reasks: int,
) -> dict[str, TrialState]:
    """Verify counters, terminal records, and actual validation outcomes before resuming."""
    states = {trial_id: TrialState() for trial_id in trials}
    dispatches: set[int] = set()
    for record in records:
        check_record_binding(record, trials, manifest_hash, mode)
        trial_id = record["trial_id"]
        state = states[trial_id]
        attempt = state.attempts + 1
        if (
            state.final or record["attempt_number"] != attempt
            or record["record_id"] != f"{trial_id}/attempt-{attempt:04d}"
            or record["response_number"] != state.invalid_replies + 1
            or record["dispatch_sequence"] in dispatches
            or record["runner_policy"]["invalid_reasks"] != invalid_reasks
        ):
            raise ValueError("Attempt history has inconsistent identities, counters, or re-ask policy.")
        dispatches.add(record["dispatch_sequence"])
        outcome = record["outcome"]
        if record["response"] is None:
            expected = {"valid": None, "parsed_json": None, "invalid_reason": None, "is_final": False, "excluded": False}
            if record["api_error"] is None or outcome != expected:
                raise ValueError("An unfinished API attempt cannot be final or excluded.")
        else:
            response_data = dict(record["response"])
            response_data["usage"] = TokenUsage(**response_data["usage"])
            validated = validate_response(ModelResponse(**response_data), record["request"]["json_schema"])
            if not validated.valid:
                state.invalid_replies += 1
            excluded = not validated.valid and state.invalid_replies > invalid_reasks
            expected = {
                "valid": validated.valid, "parsed_json": validated.parsed_json,
                "invalid_reason": validated.invalid_reason,
                "is_final": validated.valid or excluded, "excluded": excluded,
            }
            if record["api_error"] is not None or outcome != expected:
                raise ValueError("Logged validation does not match the saved response and schema.")
        state.attempts = attempt
        state.final = outcome["is_final"]
        state.excluded = outcome["excluded"]
    return states
