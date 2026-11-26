"""Exercise whole mock negotiations, identical re-asks, retries, and in-memory resumes."""

import asyncio
import json
from copy import deepcopy
from dataclasses import asdict, replace
from pathlib import Path

import pytest

from kinloyalty.clients.base import ClientError, ModelResponse, TokenUsage
from kinloyalty.logs import json_line
from kinloyalty.negotiation.config import load_config
from kinloyalty.negotiation.engine import EpisodeProgress, run_episode
from kinloyalty.negotiation.mock import NegotiationMockClient
from kinloyalty.negotiation.review import load_fixed_positions
from kinloyalty.negotiation.rules import exclude_episode, score_outcome
from kinloyalty.negotiation.state import EpisodeSpec, EpisodeState
from kinloyalty.runner import RunnerPolicy


ROOT = Path(__file__).resolve().parents[1]


def _setup(opener: str = "buyer", buyer_index: int = 0, seller_index: int = 1):
    config = load_config(ROOT / "configs/study2.yaml")
    buyer, seller = config.model_order[buyer_index], config.model_order[seller_index]
    scenario, _ = load_fixed_positions(config).position(
        config, buyer_model=buyer, seller_model=seller, role=opener, message_number=1,
    )
    spec = EpisodeSpec("synthetic-episode", buyer, seller, "not_disclosed", scenario)
    return config, spec


def _response(action: str = "offer", price: object = 500, **kwargs) -> ModelResponse:
    return ModelResponse(
        json.dumps({"message": "Public reply.", "action": action, "price": price}),
        raw_response={"fixture": True}, usage=TokenUsage(input_tokens=100, reasoning_tokens=8), **kwargs,
    )


async def _no_sleep(delay: float) -> None:
    pass


def _clients(config, client):
    return {model: client for model in config.model_order}


@pytest.mark.parametrize("opener", ["buyer", "seller"])
@pytest.mark.parametrize("buyer_index,seller_index", [(b, s) for b in range(4) for s in range(4)])
def test_complete_rule_based_negotiations(opener: str, buyer_index: int, seller_index: int) -> None:
    config, spec = _setup(opener, buyer_index, seller_index)
    client = NegotiationMockClient(seed=17)
    result = asyncio.run(run_episode(config, spec, _clients(config, client)))
    state = result.progress.state
    assert state.outcome.kind == "deal"
    assert 2 <= len(state.turns) <= 12
    assert not score_outcome(state).buyer_mandate_violation
    assert not score_outcome(state).seller_mandate_violation
    assert result.progress.reasks == result.progress.retries == 0
    assert result.progress.pending_request is None
    for index, attempt in enumerate(result.attempts, 1):
        assert attempt.attempt_number == attempt.message_number == index
        assert attempt.validation.valid and attempt.is_final_for_turn and not attempt.excluded
        assert attempt.synthetic and attempt.execution_mode == "mock" and not attempt.is_probe
        assert attempt.timestamp_utc <= attempt.completed_at_utc and attempt.latency_seconds >= 0
        assert attempt.response.usage.reasoning_tokens is not None
        json_line(asdict(attempt))
    again = asyncio.run(run_episode(config, spec, _clients(config, client), progress=result.progress))
    assert again.progress == result.progress and not again.attempts


@pytest.mark.parametrize("strategy,outcome,messages", [
    ("walk_away", "walk_away_impasse", 1), ("final_only", "final_message_impasse", 12),
])
def test_mock_walkaway_and_final_only_strategies(strategy: str, outcome: str, messages: int) -> None:
    config, spec = _setup()
    result = asyncio.run(run_episode(config, spec, _clients(config, NegotiationMockClient(strategy=strategy))))
    assert result.progress.state.outcome.kind == outcome
    assert len(result.progress.state.turns) == messages
    assert result.attempts[0].allowed_actions == ("offer", "walk_away")
    if messages == 12:
        assert result.attempts[-1].allowed_actions == ("accept", "walk_away")
        assert result.attempts[-1].request.json_schema["properties"]["action"]["enum"] == ["accept", "walk_away"]


def test_api_errors_and_one_identical_reask_are_separate() -> None:
    config, spec = _setup()
    client = NegotiationMockClient(scripts={
        f"{spec.episode_id}/message-01": [ClientError("rate_limit", status_code=429), ModelResponse("bad JSON"),
                                      ClientError("timeout"), _response(reasoning_text="Hidden reasoning stays private.")],
        f"{spec.episode_id}/message-02": [_response("accept", 999)],
    })
    delays = []
    async def sleep(delay):
        delays.append(delay)
    result = asyncio.run(run_episode(config, spec, _clients(config, client), sleep=sleep))
    assert result.progress.state.outcome.deal_price == 500
    assert result.progress.state.outcome.accept_price_mismatch
    assert result.attempts[-1].model == spec.seller_model
    assert result.attempts[-1].accept_price_mismatch
    assert result.attempts[-1].validation.parsed_json["price"] == 999
    assert result.progress.reasks == 1 and result.progress.retries == 2
    assert [a.response_number for a in result.attempts] == [1, 1, 2, 2, 1]
    assert [a.api_retry_index for a in result.attempts] == [1, 2, 1, 2, 1]
    assert [a.is_final_for_turn for a in result.attempts] == [False, False, False, True, True]
    assert delays == [1, 1]
    first = asdict(result.attempts[0].request)
    assert all(asdict(a.request) == first for a in result.attempts[:4])
    assert "Hidden reasoning" not in result.attempts[-1].request.user_message
    assert "Public reply." in result.attempts[-1].request.user_message
    assert result.attempts[0].validation is None and result.attempts[0].response is None


def test_two_invalid_responses_exclude_without_a_scored_impasse() -> None:
    config, spec = _setup()
    client = NegotiationMockClient(scripts={f"{spec.episode_id}/message-01": [ModelResponse("bad"), _response("accept", None)]})
    result = asyncio.run(run_episode(config, spec, _clients(config, client)))
    assert result.progress.state.outcome.kind == "excluded"
    assert result.progress.state.outcome.exclusion_message_number == 1
    assert result.progress.state.turns == ()
    assert score_outcome(result.progress.state).buyer_surplus_share is None
    assert len(result.attempts) == 2 and result.progress.reasks == 1
    assert not result.attempts[0].is_final_for_turn
    assert result.attempts[-1].is_final_for_turn and result.attempts[-1].excluded


def test_truncated_replies_do_not_commit_a_turn_or_reset_the_reask_count() -> None:
    config, spec = _setup()
    client = NegotiationMockClient(scripts={
        f"{spec.episode_id}/message-01": [_response()],
        f"{spec.episode_id}/message-02": [_response("accept", None, finish_reason="length"),
                                        _response("accept", None, output_truncated=True)],
    })
    result = asyncio.run(run_episode(config, spec, _clients(config, client)))
    assert result.progress.state.outcome.kind == "excluded"
    assert result.progress.state.outcome.exclusion_message_number == 2
    assert len(result.progress.state.turns) == 1
    assert result.progress.reasks == 1
    assert all(a.validation.invalid_reason == "output_truncated" for a in result.attempts[1:])


def test_resume_after_invalid_reply_and_exhausted_reask_api_budget() -> None:
    config, spec = _setup()
    client = NegotiationMockClient(scripts={f"{spec.episode_id}/message-01": [
        ModelResponse("invalid first reply"), *[ClientError("server_error") for _ in range(4)],
        ModelResponse("invalid re-ask reply"),
    ]})
    first = asyncio.run(run_episode(config, spec, _clients(config, client), sleep=_no_sleep))
    assert not first.progress.state.final
    assert first.progress.invalid_replies == first.progress.reasks == 1
    assert first.progress.attempts == 5
    assert first.progress.retries == 3
    assert first.progress.state.turns == ()
    second = asyncio.run(run_episode(config, spec, _clients(config, client), progress=first.progress, sleep=_no_sleep))
    assert second.progress.state.outcome.kind == "excluded"
    assert second.progress.attempts == 6 and second.progress.reasks == 1
    assert second.progress.retries == 4
    assert len(second.attempts) == 1 and second.attempts[0].response_number == 2
    assert second.attempts[0].api_retry_index == 1
    assert second.attempts[0].request == first.attempts[0].request


def test_midnegotiation_resume_keeps_committed_transcript() -> None:
    config, spec = _setup()
    client = NegotiationMockClient(scripts={
        f"{spec.episode_id}/message-01": [_response(price=450)],
        f"{spec.episode_id}/message-02": [_response(price=550)],
        f"{spec.episode_id}/message-03": [*[ClientError("timeout") for _ in range(4)], _response("accept", None)],
    })
    first = asyncio.run(run_episode(config, spec, _clients(config, client), sleep=_no_sleep))
    assert len(first.progress.state.turns) == 2 and not first.progress.state.final
    assert first.progress.invalid_replies == 0
    resumed = asyncio.run(run_episode(config, spec, _clients(config, client), progress=first.progress, sleep=_no_sleep))
    assert len(resumed.progress.state.turns) == 3
    assert resumed.progress.state.outcome.deal_price == 550
    assert resumed.attempts[0].request == first.attempts[-1].request
    assert resumed.attempts[0].attempt_number == 7
    assert len(client.requests) == 7
    tampered = replace(first.progress, pending_request=replace(first.progress.pending_request, user_message="changed"))
    with pytest.raises(ValueError, match="Pending request"):
        asyncio.run(run_episode(config, spec, _clients(config, client), progress=tampered))
    with pytest.raises(ValueError, match="different episode"):
        asyncio.run(run_episode(config, replace(spec, condition="true"), _clients(config, client), progress=first.progress))


def test_nonretryable_error_does_not_become_an_exclusion() -> None:
    config, spec = _setup()
    client = NegotiationMockClient(scripts={f"{spec.episode_id}/message-01": [ClientError("bad_request", retryable=False, status_code=400)]})
    result = asyncio.run(run_episode(config, spec, _clients(config, client)))
    assert not result.progress.state.final and len(result.attempts) == 1
    assert result.attempts[0].api_error == {"kind": "bad_request", "retryable": False, "status_code": 400}
    assert result.progress.invalid_replies == result.progress.reasks == 0


def test_actual_timeout_is_recorded_and_left_unfinished() -> None:
    config, spec = _setup()
    class SlowClient:
        execution_mode = "mock"
        async def complete(self, request):
            await asyncio.sleep(1)
    policy = RunnerPolicy(timeout_seconds=.001, api_attempts_per_response=2, backoff_initial_seconds=0)
    result = asyncio.run(run_episode(config, spec, _clients(config, SlowClient()), policy=policy, sleep=_no_sleep))
    assert not result.progress.state.final and len(result.attempts) == 2
    assert all(a.api_error["kind"] == "timeout" for a in result.attempts)
    assert result.progress.reasks == 0


def test_mock_only_guard_and_interruption_observer() -> None:
    config, spec = _setup()
    client = NegotiationMockClient()
    client.execution_mode = "live"
    with pytest.raises(ValueError, match="requires a mock"):
        asyncio.run(run_episode(config, spec, _clients(config, client)))
    assert not client.requests
    interrupted = NegotiationMockClient(scripts={f"{spec.episode_id}/message-01": [ValueError("unlogged exception detail")]})
    observed = []
    with pytest.raises(ValueError, match="unlogged exception detail"):
        asyncio.run(run_episode(config, spec, _clients(config, interrupted), on_attempt=lambda a, p: observed.append((a, p))))
    attempt, progress = observed[0]
    assert attempt.api_error["kind"] == "interrupted" and not progress.state.final
    assert "unlogged exception detail" not in json_line(asdict(attempt))
    assert progress.pending_request is not None


def test_client_and_observer_cannot_mutate_the_identical_reask() -> None:
    config, spec = _setup()
    class MutatingMock(NegotiationMockClient):
        async def complete(self, request):
            request.settings["max_output_tokens"] = 1
            request.api_payload["model"] = "mutated"
            return await super().complete(request)
    client = MutatingMock(scripts={f"{spec.episode_id}/message-01": [ModelResponse("bad"), _response()]})
    def observer(attempt, progress):
        attempt.request.settings["max_output_tokens"] = 3
        if progress.pending_request is not None:
            progress.pending_request.api_payload["model"] = "observer mutation"
    result = asyncio.run(run_episode(config, spec, _clients(config, client), on_attempt=observer))
    assert result.progress.state.final
    assert result.attempts[0].request == result.attempts[1].request
    assert result.attempts[0].request.settings["max_output_tokens"] == 8192
    assert result.attempts[0].request.api_payload["model"] == "claude-sonnet-5-5"


def test_mock_planted_label_effect_lowers_buyer_surplus_holding_seller_fixed() -> None:
    contrasts = []
    for opener in ("buyer", "seller"):
        config, base = _setup(opener)
        results = {}
        for condition in ("true", "swapped"):
            spec = replace(base, condition=condition)
            client = NegotiationMockClient(seed=22, label_effect=.10)
            result = asyncio.run(run_episode(config, spec, _clients(config, client)))
            assert result.progress.state.outcome.kind == "deal"
            results[condition] = score_outcome(result.progress.state).buyer_surplus_share
        contrasts.append(results["swapped"] - results["true"])
    assert all(contrast < 0 for contrast in contrasts)


def test_inconsistent_resume_counters_are_rejected_before_any_call() -> None:
    config, spec = _setup()
    client = NegotiationMockClient()
    initial = EpisodeProgress(spec, EpisodeState(spec.scenario))
    for bad in (
        replace(initial, reasks=1), replace(initial, retries=1),
        replace(initial, retry_pending=True), replace(initial, reask_started=True),
        replace(initial, state=exclude_episode(initial.state)),
    ):
        with pytest.raises(ValueError):
            asyncio.run(run_episode(config, spec, _clients(config, client), progress=bad))
    assert not client.requests
