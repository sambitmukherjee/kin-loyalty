"""Run one mock negotiation with in-memory attempt records and resumable progress."""

import asyncio
import time
from collections.abc import Awaitable, Callable, Mapping
from copy import deepcopy
from dataclasses import asdict, dataclass, replace
from datetime import datetime, timezone
from typing import Any

from kinloyalty.clients.base import ClientError, ModelClient, ModelRequest, ModelResponse
from kinloyalty.logs import content_hash
from kinloyalty.negotiation import Role
from kinloyalty.negotiation.config import Study2Config
from kinloyalty.negotiation.requests import build_turn_request
from kinloyalty.negotiation.rules import allowed_actions, apply_turn, exclude_episode, next_role, validate_state
from kinloyalty.negotiation.state import EpisodeSpec, EpisodeState
from kinloyalty.negotiation.validate import ReplyValidation, validate_response
from kinloyalty.runner import RunnerPolicy


@dataclass(frozen=True)
class EpisodeProgress:
    """Keep committed messages and pending-response counters across explicit resumes."""

    spec: EpisodeSpec
    state: EpisodeState
    attempts: int = 0
    reasks: int = 0
    retries: int = 0
    invalid_replies: int = 0
    reask_started: bool = False
    retry_pending: bool = False
    pending_request: ModelRequest | None = None


@dataclass(frozen=True)
class TurnAttempt:
    """Retain every call's request, response, validity, safe error, and finality."""

    episode_id: str
    phase: str
    message_number: int
    role: Role
    model: str
    attempt_number: int
    response_number: int
    api_retry_index: int
    allowed_actions: tuple[str, ...]
    request: ModelRequest
    response: ModelResponse | None
    validation: ReplyValidation | None
    api_error: dict[str, Any] | None
    is_final_for_turn: bool
    excluded: bool
    accept_price_mismatch: bool
    timestamp_utc: str
    completed_at_utc: str
    latency_seconds: float
    synthetic: bool = True
    execution_mode: str = "mock"
    is_probe: bool = False


@dataclass(frozen=True)
class EpisodeResult:
    """Return updated progress and only the attempts made by this invocation."""

    progress: EpisodeProgress
    attempts: tuple[TurnAttempt, ...]


def _check_progress(config: Study2Config, spec: EpisodeSpec, progress: EpisodeProgress) -> None:
    validate_state(progress.state)
    if not isinstance(spec.episode_id, str) or not spec.episode_id:
        raise ValueError("A nonempty episode identity is required.")
    if progress.spec != spec or progress.state.scenario != spec.scenario:
        raise ValueError("Cannot resume progress from a different episode assignment.")
    if progress.state.message_limit != config.message_limit:
        raise ValueError("Cannot resume with a changed message limit.")
    for value in (progress.attempts, progress.reasks, progress.retries, progress.invalid_replies):
        if type(value) is not int or value < 0:
            raise ValueError("Progress counters must be nonnegative integers.")
    if (progress.attempts < len(progress.state.turns) + progress.invalid_replies
            or progress.reasks + progress.retries > progress.attempts):
        raise ValueError("Progress counters cannot account for the committed history.")
    if progress.invalid_replies > 1 and not (
        progress.state.final and progress.state.outcome.kind == "excluded" and progress.invalid_replies == 2
    ):
        raise ValueError("Two invalid responses must terminate the episode as excluded.")
    if not progress.state.final:
        expected = build_turn_request(config, spec, progress.state)
        if progress.pending_request is not None and content_hash(asdict(progress.pending_request)) != content_hash(asdict(expected)):
            raise ValueError("Pending request differs from the current frozen turn.")
        if progress.invalid_replies and progress.pending_request is None:
            raise ValueError("An invalid-response re-ask requires its identical pending request.")
    if progress.reask_started and not progress.invalid_replies:
        raise ValueError("A re-ask cannot precede an invalid response.")
    if progress.reask_started and not progress.reasks:
        raise ValueError("A started re-ask must be counted.")
    if progress.retry_pending and (not progress.attempts or progress.pending_request is None):
        raise ValueError("A pending retry requires a prior attempt and frozen request.")
    if progress.state.final:
        if progress.state.outcome.kind == "excluded":
            if progress.invalid_replies != 2 or not progress.reask_started:
                raise ValueError("An exclusion requires the original invalid reply and its re-ask.")
            expected = build_turn_request(config, spec, replace(progress.state, outcome=None))
            if progress.pending_request is None or content_hash(asdict(progress.pending_request)) != content_hash(asdict(expected)):
                raise ValueError("An exclusion must retain the failed turn's frozen request.")
        elif progress.invalid_replies or progress.reask_started or progress.retry_pending or progress.pending_request is not None:
            raise ValueError("A valid terminal outcome cannot retain pending response work.")


async def run_episode(
    config: Study2Config, spec: EpisodeSpec, clients: Mapping[str, ModelClient], *,
    progress: EpisodeProgress | None = None, policy: RunnerPolicy | None = None,
    sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
    on_attempt: Callable[[TurnAttempt, EpisodeProgress], None] | None = None,
) -> EpisodeResult:
    """Execute sequential mock turns, preserving invalid counts through API failures.

    Durable journals, concurrent episode scheduling, and disk replay belong to
    Phase 3. This Phase 2 entry point refuses live clients. An optional observer
    receives detached attempt/progress snapshots, including interrupted calls.
    """
    for model in {spec.buyer_model, spec.seller_model}:
        if model not in clients or clients[model].execution_mode != "mock":
            raise ValueError("Phase 2 requires a mock client for each participating model.")
    policy = policy or RunnerPolicy(
        **config.study["runner"], invalid_reasks=config.study["validation"]["identical_reasks_per_invalid_turn"],
    )
    if policy.invalid_reasks != 1:
        raise ValueError("Study 2 permits exactly one invalid-response re-ask.")
    progress = deepcopy(progress) if progress is not None else EpisodeProgress(
        spec=deepcopy(spec), state=EpisodeState(spec.scenario, config.message_limit),
    )
    _check_progress(config, spec, progress)
    attempts = []

    def record(attempt: TurnAttempt) -> None:
        attempts.append(deepcopy(attempt))
        if on_attempt is not None:
            on_attempt(deepcopy(attempt), deepcopy(progress))

    while not progress.state.final:
        request = progress.pending_request or build_turn_request(config, spec, progress.state)
        progress = replace(progress, pending_request=deepcopy(request))
        role = next_role(progress.state)
        model = spec.buyer_model if role == "buyer" else spec.seller_model
        number = len(progress.state.turns) + 1
        for api_index in range(1, policy.api_attempts_per_response + 1):
            is_reask = progress.invalid_replies == 1
            progress = replace(
                progress, attempts=progress.attempts + 1,
                reasks=progress.reasks + int(is_reask and not progress.reask_started),
                reask_started=progress.reask_started or is_reask,
                retries=progress.retries + int(progress.retry_pending),
            )
            response = None
            validation = None
            error = None
            final_for_turn = False
            excluded = False
            mismatch = False
            interrupted = None
            timestamp = datetime.now(timezone.utc).isoformat()
            started = time.perf_counter()
            try:
                # A client cannot mutate the canonical request used by a re-ask.
                response = await asyncio.wait_for(clients[model].complete(deepcopy(request)), policy.timeout_seconds)
            except ClientError as failure:
                error = {"kind": failure.kind, "retryable": failure.retryable, "status_code": failure.status_code}
            except TimeoutError:
                error = {"kind": "timeout", "retryable": True, "status_code": None}
            except BaseException as failure:
                error = {"kind": "interrupted", "retryable": True, "status_code": None}
                interrupted = failure
            completed = datetime.now(timezone.utc).isoformat()
            latency = time.perf_counter() - started
            if error is not None:
                progress = replace(progress, retry_pending=True)
            else:
                validation = validate_response(
                    response, role=role, message_number=number, message_limit=progress.state.message_limit,
                )
                if validation.valid:
                    state = apply_turn(progress.state, validation.turn)
                    mismatch = state.outcome.accept_price_mismatch if state.outcome is not None else False
                    final_for_turn = True
                    progress = replace(progress, state=state, invalid_replies=0,
                                       reask_started=False, retry_pending=False, pending_request=None)
                else:
                    invalids = progress.invalid_replies + 1
                    excluded = invalids == 2
                    final_for_turn = excluded
                    progress = replace(
                        progress, invalid_replies=invalids, retry_pending=False,
                        state=exclude_episode(progress.state) if excluded else progress.state,
                    )
            record(TurnAttempt(
                episode_id=spec.episode_id, phase=spec.phase, message_number=number, role=role, model=model,
                attempt_number=progress.attempts, response_number=2 if is_reask else 1, api_retry_index=api_index,
                allowed_actions=allowed_actions(number, progress.state.message_limit), request=deepcopy(request),
                response=deepcopy(response), validation=validation, api_error=error,
                is_final_for_turn=final_for_turn, excluded=excluded, accept_price_mismatch=mismatch,
                timestamp_utc=timestamp, completed_at_utc=completed, latency_seconds=latency,
            ))
            if interrupted is not None:
                raise interrupted
            if error is None:
                break
            if not error["retryable"] or api_index == policy.api_attempts_per_response:
                return EpisodeResult(progress, tuple(attempts))
            delay = min(policy.backoff_initial_seconds * policy.backoff_multiplier ** (api_index - 1),
                        policy.backoff_max_seconds)
            await sleep(delay)
    return EpisodeResult(progress, tuple(attempts))
