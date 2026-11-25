"""Execute only frozen manifests, separating invalid replies from retryable API failures."""

import asyncio
import math
import time
import uuid
from copy import deepcopy
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from kinloyalty.clients.base import ClientError, ModelClient, ModelRequest
from kinloyalty.logs import AttemptLog, content_hash, file_hash
from kinloyalty.manifest import read_manifest
from kinloyalty.provenance import collect_provenance
from kinloyalty.state import check_record_binding, reconstruct_states
from kinloyalty.validate import validate_response


@dataclass(frozen=True)
class RunnerPolicy:
    """Configure scheduling and API retries independently of invalid-response re-asks."""

    concurrency: int = 4
    per_model_concurrency: int = 1
    timeout_seconds: float = 120
    api_attempts_per_response: int = 4
    backoff_initial_seconds: float = 1
    backoff_multiplier: float = 2
    backoff_max_seconds: float = 30
    invalid_reasks: int = 1

    def __post_init__(self) -> None:
        """Reject non-finite, negative, or nonsensical infrastructure settings."""
        for name in ("concurrency", "per_model_concurrency", "api_attempts_per_response"):
            if type(getattr(self, name)) is not int or getattr(self, name) < 1:
                raise ValueError(f"{name} must be a positive integer.")
        if type(self.invalid_reasks) is not int or self.invalid_reasks < 0:
            raise ValueError("invalid_reasks must be a nonnegative integer.")
        for name in ("timeout_seconds", "backoff_initial_seconds", "backoff_multiplier", "backoff_max_seconds"):
            if not math.isfinite(getattr(self, name)) or getattr(self, name) < 0:
                raise ValueError(f"{name} must be finite and nonnegative.")
        if self.timeout_seconds == 0 or self.backoff_multiplier < 1:
            raise ValueError("Timeout must be positive and backoff multiplier at least one.")


@dataclass(frozen=True)
class RunSummary:
    """Summarize mechanical completion without displaying decision outcomes or label effects."""

    planned: int
    already_final: int
    valid: int
    excluded: int
    unfinished_trial_ids: list[str]
    calls_started: int
    recovered_attempts: int
    attempt_records_written: int


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


async def run_manifest(
    manifest_path: str | Path, log_path: str | Path, client: ModelClient,
    *, policy: RunnerPolicy | None = None,
) -> RunSummary:
    """Resume a manifest with bounded concurrency, durable attempts, and one re-ask.

    The default policy is frozen in the manifest. API-error budgets restart when
    explicitly resuming an unfinished draw; invalid-reply counts never reset.
    No current configuration or templates are read during execution or resume.
    """
    trials = read_manifest(manifest_path)
    manifest_hash = file_hash(manifest_path)
    policy = policy or RunnerPolicy(**trials[0]["runner_settings"])
    trial_map = {trial["trial_id"]: trial for trial in trials}
    provenance = collect_provenance()
    run_id = str(uuid.uuid4())
    mode = client.execution_mode
    calls_started = 0
    fatal_error: BaseException | None = None

    with AttemptLog(log_path) as store:
        original_count = len(store.records)
        for record in [*store.records, *store.pending.values()]:
            check_record_binding(record, trial_map, manifest_hash, mode)
        # Validate existing history before appending any recovered reservations.
        reconstruct_states(trial_map, store.records, manifest_hash, mode, policy.invalid_reasks)
        recovered = store.recover_pending(_utc_now())
        states = reconstruct_states(trial_map, store.records, manifest_hash, mode, policy.invalid_reasks)
        already_final = sum(state.final for state in states.values())
        dispatch_sequence = max((record["dispatch_sequence"] for record in store.records), default=0)
        global_limit = asyncio.Semaphore(policy.concurrency)
        model_limits = {trial["model"]: asyncio.Semaphore(policy.per_model_concurrency) for trial in trials}

        async def execute(trial: dict[str, Any]) -> None:
            nonlocal calls_started, dispatch_sequence, fatal_error
            state = states[trial["trial_id"]]
            try:
                while not state.final:
                    for api_index in range(1, policy.api_attempts_per_response + 1):
                        attempt = state.attempts + 1
                        dispatch_sequence += 1
                        base = {
                            **{key: deepcopy(value) for key, value in trial.items() if key != "request"},
                            "record_id": f"{trial['trial_id']}/attempt-{attempt:04d}",
                            "run_id": run_id, "attempt_number": attempt,
                            "response_number": state.invalid_replies + 1, "api_retry_index": api_index,
                            "dispatch_sequence": dispatch_sequence, "manifest_sha256": manifest_hash,
                            "trial_sha256": content_hash(trial), "execution_mode": mode,
                            "synthetic": mode == "mock", "timestamp_utc": _utc_now(),
                            "completed_at_utc": None, "latency_seconds": None,
                            **provenance, "runner_policy": asdict(policy), "request": deepcopy(trial["request"]),
                            "response": None, "api_error": None,
                            "outcome": {"valid": None, "parsed_json": None, "invalid_reason": None, "is_final": False, "excluded": False},
                        }
                        store.reserve(base)
                        started = time.perf_counter()
                        request = ModelRequest(**deepcopy(trial["request"]))
                        api_error: ClientError | None = None
                        try:
                            calls_started += 1
                            response = await asyncio.wait_for(client.complete(request), timeout=policy.timeout_seconds)
                        except ClientError as error:
                            api_error = error
                        except TimeoutError:
                            api_error = ClientError("timeout")
                        except BaseException:
                            base["api_error"] = {"kind": "interrupted", "retryable": True, "status_code": None}
                            base["completed_at_utc"] = _utc_now()
                            base["latency_seconds"] = time.perf_counter() - started
                            store.append(base)
                            state.attempts += 1
                            raise
                        base["completed_at_utc"] = _utc_now()
                        base["latency_seconds"] = time.perf_counter() - started
                        if api_error is not None:
                            base["api_error"] = {
                                "kind": api_error.kind, "retryable": api_error.retryable,
                                "status_code": api_error.status_code,
                            }
                        else:
                            validated = validate_response(response, trial["request"]["json_schema"])
                            if not validated.valid:
                                state.invalid_replies += 1
                            excluded = not validated.valid and state.invalid_replies > policy.invalid_reasks
                            base["response"] = asdict(response)
                            base["outcome"] = {
                                "valid": validated.valid, "parsed_json": validated.parsed_json,
                                "invalid_reason": validated.invalid_reason,
                                "is_final": validated.valid or excluded, "excluded": excluded,
                            }
                            state.final = base["outcome"]["is_final"]
                            state.excluded = excluded
                        store.append(base)
                        state.attempts += 1
                        if api_error is None:
                            break
                        if not api_error.retryable or api_index == policy.api_attempts_per_response:
                            return
                        delay = min(
                            policy.backoff_initial_seconds * policy.backoff_multiplier ** (api_index - 1),
                            policy.backoff_max_seconds,
                        )
                        await asyncio.sleep(delay)
            except BaseException as error:
                fatal_error = error
                raise
            finally:
                model_limits[trial["model"]].release()
                global_limit.release()

        tasks: list[asyncio.Task[None]] = []
        try:
            for trial in trials:
                if states[trial["trial_id"]].final:
                    continue
                await global_limit.acquire()
                try:
                    if fatal_error is not None:
                        raise fatal_error
                    await model_limits[trial["model"]].acquire()
                except BaseException:
                    global_limit.release()
                    raise
                if fatal_error is not None:
                    model_limits[trial["model"]].release()
                    global_limit.release()
                    raise fatal_error
                tasks.append(asyncio.create_task(execute(trial)))
            if tasks:
                await asyncio.gather(*tasks)
        except BaseException:
            for task in tasks:
                task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)
            raise
        return RunSummary(
            planned=len(trials), already_final=already_final,
            valid=sum(state.final and not state.excluded for state in states.values()),
            excluded=sum(state.excluded for state in states.values()),
            unfinished_trial_ids=[trial["trial_id"] for trial in trials if not states[trial["trial_id"]].final],
            calls_started=calls_started, recovered_attempts=recovered,
            attempt_records_written=len(store.records) - original_count,
        )
