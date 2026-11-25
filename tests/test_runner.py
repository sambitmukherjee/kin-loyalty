"""Test API faults, re-asks, exclusions, durable resume, and bounded scheduling offline."""

import asyncio
import json
import subprocess
import sys
import time
from collections import defaultdict
from copy import deepcopy
from pathlib import Path

import pytest

from kinloyalty.clients.base import ClientError, ModelResponse
from kinloyalty.clients.mock import MockClient
from kinloyalty.logs import AttemptLog, json_line, read_jsonl
from kinloyalty.manifest import build_manifest, write_manifest
from kinloyalty.runner import RunnerPolicy, run_manifest


ROOT = Path(__file__).resolve().parents[1]
VALID = ModelResponse('{"amount_to_counterparty":40,"reason":"Synthetic response."}', finish_reason="stop")
INVALID = ModelResponse('not json', finish_reason="stop")


@pytest.fixture
def plan(tmp_path: Path) -> tuple[Path, Path, list[dict]]:
    """Provide the four-trial smoke plan as a temporary mock-only test artifact."""
    trials = build_manifest(ROOT / "configs/study1.yaml", "smoke")
    manifest = tmp_path / "manifest.jsonl"
    write_manifest(trials, manifest)
    return manifest, tmp_path / "attempts.jsonl", trials


def _policy(**changes: object) -> RunnerPolicy:
    return RunnerPolicy(**{"concurrency": 2, "timeout_seconds": 1, "backoff_initial_seconds": 0, "backoff_max_seconds": 0, **changes})


def _run(plan: tuple, client: MockClient, **changes: object):
    return asyncio.run(run_manifest(plan[0], plan[1], client, policy=_policy(**changes)))


def test_valid_log_and_idempotent_resume(plan: tuple, monkeypatch: pytest.MonkeyPatch) -> None:
    """Persist complete request/response provenance and skip every already-final draw."""
    monkeypatch.setenv("OPENAI_API_KEY", "fake-secret-for-leak-check")
    client = MockClient(seed=123)
    summary = _run(plan, client)
    assert (summary.valid, summary.excluded, summary.calls_started) == (4, 0, 4)
    assert summary.unfinished_trial_ids == []
    records = read_jsonl(plan[1])
    assert len(records) == 4
    for record in records:
        assert record["synthetic"] is True
        assert record["execution_mode"] == "mock"
        assert record["response"]["returned_model_version"].startswith("mock/")
        assert record["response"]["usage"]["reasoning_tokens"] is not None
        assert record["timestamp_utc"].endswith("+00:00")
        assert record["git_commit"]
        assert record["package_version"] == "0.1.0"
        assert set(record["sdk_versions"]) == {"anthropic", "openai", "google-genai"}
        assert record["outcome"]["is_final"] is True
        assert record["latency_seconds"] >= 0
    assert "fake-secret-for-leak-check" not in plan[1].read_text()
    original = plan[1].read_bytes()
    repeated = MockClient(seed=123)
    again = _run(plan, repeated)
    assert (again.already_final, again.calls_started, again.attempt_records_written) == (4, 0, 0)
    assert not repeated.requests
    assert plan[1].read_bytes() == original


def test_invalid_reply_gets_one_identical_fresh_reask(plan: tuple) -> None:
    """Keep the trial ID, request text/schema/settings, and response-stage counter exact."""
    target = plan[2][0]["trial_id"]
    client = MockClient(scripts={target: [INVALID, VALID]})
    summary = _run(plan, client)
    assert summary.valid == 4
    assert client.call_counts[target] == 2
    requests = [request for request in client.requests if request.trial_id == target]
    assert requests[0] == requests[1]
    records = [record for record in read_jsonl(plan[1]) if record["trial_id"] == target]
    assert [r["attempt_number"] for r in records] == [1, 2]
    assert [r["response_number"] for r in records] == [1, 2]
    assert records[0]["outcome"]["is_final"] is False
    assert records[1]["outcome"]["is_final"] is True
    assert records[0]["request"] == records[1]["request"]


def test_two_invalid_replies_exclude_and_never_get_a_third_call(plan: tuple) -> None:
    """Count parseable JSON cut off at the cap as the second invalid response."""
    target = plan[2][0]["trial_id"]
    truncated = ModelResponse(VALID.output_text, finish_reason="length")
    client = MockClient(scripts={target: [INVALID, truncated, VALID]})
    summary = _run(plan, client)
    assert (summary.valid, summary.excluded) == (3, 1)
    assert client.call_counts[target] == 2
    records = [record for record in read_jsonl(plan[1]) if record["trial_id"] == target]
    assert records[-1]["outcome"]["invalid_reason"] == "output_truncated"
    assert records[-1]["outcome"]["excluded"] is True
    assert _run(plan, MockClient()).calls_started == 0


def test_api_errors_do_not_consume_invalid_reasks(plan: tuple) -> None:
    """Retry failures within each response stage rather than adding corrective messages."""
    target = plan[2][0]["trial_id"]
    error = ClientError("rate_limit", status_code=429)
    client = MockClient(scripts={target: [error, INVALID, error, VALID]})
    summary = _run(plan, client)
    assert summary.valid == 4
    records = [r for r in read_jsonl(plan[1]) if r["trial_id"] == target]
    assert [r["attempt_number"] for r in records] == [1, 2, 3, 4]
    assert [r["response_number"] for r in records] == [1, 1, 2, 2]
    assert [r["api_retry_index"] for r in records] == [1, 2, 1, 2]
    assert records[0]["outcome"]["valid"] is None
    assert all(not r["outcome"]["excluded"] for r in records)
    assert all(r["request"] == records[0]["request"] for r in records)


@pytest.mark.parametrize("first_invalid", (False, True))
def test_exhausted_errors_resume_without_resetting_reask_state(plan: tuple, first_invalid: bool) -> None:
    """Leave exhausted errors unfinished and preserve any invalid response across a new run."""
    target = plan[2][0]["trial_id"]
    sequence = ([INVALID] if first_invalid else []) + [ClientError("server_error")] * 3
    first = _run(plan, MockClient(scripts={target: sequence}), api_attempts_per_response=3)
    assert first.unfinished_trial_ids == [target]
    assert first.excluded == 0
    prefix = plan[1].read_bytes()
    resumed_client = MockClient(scripts={target: [INVALID]}) if first_invalid else MockClient()
    resumed = _run(plan, resumed_client, api_attempts_per_response=3)
    assert resumed.already_final == 3
    assert resumed.calls_started == 1
    assert resumed.unfinished_trial_ids == []
    assert resumed.excluded == int(first_invalid)
    assert plan[1].read_bytes().startswith(prefix)
    records = [r for r in read_jsonl(plan[1]) if r["trial_id"] == target]
    assert records[-1]["attempt_number"] == 4 + int(first_invalid)
    assert records[-1]["response_number"] == 1 + int(first_invalid)


def test_nonretryable_api_error_is_unfinished_not_excluded(plan: tuple) -> None:
    """Avoid retry loops on authentication errors without treating them as model answers."""
    target = plan[2][0]["trial_id"]
    client = MockClient(scripts={target: [ClientError("authentication", retryable=False, status_code=401)]})
    summary = _run(plan, client)
    assert client.call_counts[target] == 1
    assert summary.unfinished_trial_ids == [target]
    assert summary.excluded == 0


def test_exponential_backoff_is_capped(plan: tuple, monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify the actual wait schedule while keeping test execution immediate."""
    delays = []

    async def record_sleep(delay: float) -> None:
        delays.append(delay)

    monkeypatch.setattr("kinloyalty.runner.asyncio.sleep", record_sleep)
    target = plan[2][0]["trial_id"]
    client = MockClient(scripts={target: [ClientError("connection")] * 3 + [VALID]})
    summary = _run(plan, client, backoff_initial_seconds=2, backoff_multiplier=3, backoff_max_seconds=4)
    assert summary.valid == 4
    assert delays == [2, 4, 4]


def test_timeout_is_an_api_error(plan: tuple) -> None:
    """Retry timed-out calls without consuming either of the model's two reply opportunities."""
    class SlowClient(MockClient):
        async def complete(self, request):
            self.requests.append(request)
            await asyncio.sleep(1)

    client = SlowClient()
    summary = _run(plan, client, timeout_seconds=0.005, api_attempts_per_response=2)
    assert (summary.valid, summary.excluded, summary.calls_started) == (0, 0, 8)
    assert len(summary.unfinished_trial_ids) == 4
    assert all(r["api_error"]["kind"] == "timeout" for r in read_jsonl(plan[1]))
    assert {r["response_number"] for r in read_jsonl(plan[1])} == {1}


def test_concurrency_limits_apply_globally_and_per_model(tmp_path: Path) -> None:
    """Allow parallel models while preserving the configured within-model bound."""
    trials = build_manifest(ROOT / "configs/study1.yaml", "pilot")
    groups = defaultdict(list)
    for trial in trials:
        groups[trial["model"]].append(trial)
    selected = [group[draw] for draw in (0, 1) for group in groups.values()]
    for position, trial in enumerate(selected, 1):
        trial["execution_position"] = position
    manifest, log = tmp_path / "manifest.jsonl", tmp_path / "attempts.jsonl"
    write_manifest(selected, manifest)

    class TrackingClient(MockClient):
        active = 0
        maximum = 0

        def __init__(self):
            super().__init__()
            self.per_model = defaultdict(int)
            self.model_max = defaultdict(int)

        async def complete(self, request):
            self.active += 1
            self.maximum = max(self.maximum, self.active)
            self.per_model[request.api_model_id] += 1
            self.model_max[request.api_model_id] = max(self.model_max[request.api_model_id], self.per_model[request.api_model_id])
            try:
                await asyncio.sleep(0.005)
                return await super().complete(request)
            finally:
                self.active -= 1
                self.per_model[request.api_model_id] -= 1

    client = TrackingClient()
    summary = asyncio.run(run_manifest(manifest, log, client, policy=_policy(concurrency=3)))
    assert summary.valid == 8
    assert client.maximum == 3
    assert set(client.model_max.values()) == {1}


def test_local_canonical_bounds_survive_client_mutation(plan: tuple) -> None:
    """A transport's schema adaptation must not weaken local validation or re-ask content."""
    class MutatingClient(MockClient):
        async def complete(self, request):
            request.json_schema["properties"]["amount_to_counterparty"].pop("maximum")
            return ModelResponse('{"amount_to_counterparty":101,"reason":"Synthetic."}')

    summary = _run(plan, MutatingClient())
    assert summary.excluded == 4
    records = read_jsonl(plan[1])
    assert all(r["request"]["json_schema"]["properties"]["amount_to_counterparty"]["maximum"] == 100 for r in records)


def test_unexpected_interruption_is_logged_without_exception_text_and_resumes(plan: tuple) -> None:
    """Preserve unfinished state and avoid logging arbitrary exception strings."""
    target = plan[2][0]["trial_id"]
    failing = MockClient(scripts={target: [RuntimeError("fake-private-exception-text")]})
    with pytest.raises(RuntimeError, match="fake-private-exception-text"):
        _run(plan, failing, concurrency=1)
    assert len(failing.requests) == 1
    assert "fake-private-exception-text" not in plan[1].read_text()
    records = [r for r in read_jsonl(plan[1]) if r["trial_id"] == target]
    assert records[0]["api_error"]["kind"] == "interrupted"
    assert records[0]["outcome"]["is_final"] is False
    assert _run(plan, MockClient()).valid == 4


@pytest.mark.parametrize("first_invalid", (False, True))
def test_hard_process_kill_recovers_pending_attempt(plan: tuple, tmp_path: Path, first_invalid: bool) -> None:
    """Recover a killed request without resetting a previously used invalid-reply opportunity."""
    ready = tmp_path / "ready"
    code = '''
import asyncio
import sys
from pathlib import Path
from kinloyalty.clients.mock import MockClient
from kinloyalty.clients.base import ModelResponse
from kinloyalty.runner import RunnerPolicy, run_manifest
class BlockingClient(MockClient):
    first = True
    async def complete(self, request):
        if sys.argv[4] == "1" and self.first:
            self.first = False
            return ModelResponse("not json")
        Path(sys.argv[3]).write_text("ready")
        await asyncio.Event().wait()
asyncio.run(run_manifest(sys.argv[1], sys.argv[2], BlockingClient(), policy=RunnerPolicy(concurrency=1)))
'''
    process = subprocess.Popen([sys.executable, "-c", code, str(plan[0]), str(plan[1]), str(ready), str(int(first_invalid))], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        deadline = time.monotonic() + 5
        while not ready.exists() and process.poll() is None and time.monotonic() < deadline:
            time.sleep(0.01)
        assert ready.exists(), process.poll()
        process.kill()
        process.communicate(timeout=5)
    finally:
        if process.poll() is None:
            process.kill()
            process.communicate(timeout=5)
    client = MockClient(scripts={plan[2][0]["trial_id"]: [INVALID]}) if first_invalid else MockClient()
    summary = _run(plan, client, concurrency=1)
    assert summary.recovered_attempts == 1
    assert (summary.calls_started, summary.valid, summary.excluded) == (4, 4 - int(first_invalid), int(first_invalid))
    records = read_jsonl(plan[1])
    assert len(records) == 5 + int(first_invalid)
    recovered = next(record for record in records if record["api_error"] and record["api_error"]["kind"] == "interrupted")
    assert recovered["latency_seconds"] is None
    assert recovered["response_number"] == 1 + int(first_invalid)
    assert not plan[1].with_name(plan[1].name + ".pending.json").exists()


def test_stale_journal_for_already_appended_record_is_cleared_once(plan: tuple) -> None:
    """Handle a crash after log fsync but before the journal entry was removed."""
    _run(plan, MockClient())
    original = plan[1].read_bytes()
    record = deepcopy(read_jsonl(plan[1])[0])
    record["response"] = None
    record["outcome"] = {"valid": None, "parsed_json": None, "invalid_reason": None, "is_final": False, "excluded": False}
    with AttemptLog(plan[1]) as store:
        store.reserve(record)
    summary = _run(plan, MockClient())
    assert summary.calls_started == summary.recovered_attempts == 0
    assert plan[1].read_bytes() == original


@pytest.mark.parametrize("change", ("manifest", "request_order", "outcome", "cell_metadata", "duplicate_record", "partial_tail"))
def test_inconsistent_history_fails_without_calls_or_log_changes(plan: tuple, change: str) -> None:
    """Never resume across a changed plan, altered audit data, or corrupt final write."""
    _run(plan, MockClient())
    records = read_jsonl(plan[1])
    if change == "manifest":
        trials = deepcopy(plan[2])
        trials[0]["request"]["system_prompt"] += " changed"
        plan[0].write_text("".join(json_line(t) for t in trials))
    elif change == "request_order":
        records[0]["request"] = dict(reversed(list(records[0]["request"].items())))
    elif change == "outcome":
        records[0]["outcome"]["is_final"] = False
    elif change == "cell_metadata":
        records[0]["principal"] = "Changed"
    elif change == "duplicate_record":
        records.append(deepcopy(records[0]))
    if change != "manifest":
        content = "".join(json_line(record) for record in records)
        if change == "partial_tail":
            content += '{"unfinished":'
        plan[1].write_text(content)
    original = plan[1].read_bytes()
    client = MockClient()
    with pytest.raises(ValueError):
        _run(plan, client)
    assert not client.requests
    assert plan[1].read_bytes() == original


def test_log_cannot_have_two_writers(plan: tuple) -> None:
    """Fail before any client calls if another local process holds the run lock."""
    with AttemptLog(plan[1]):
        client = MockClient()
        with pytest.raises(BlockingIOError):
            _run(plan, client)
        assert not client.requests


def test_runner_never_rerenders_frozen_requests(plan: tuple, monkeypatch: pytest.MonkeyPatch) -> None:
    """Execute the exact saved plan even if current templates/config cannot be loaded."""
    def fail(*args: object, **kwargs: object) -> None:
        raise AssertionError("Runner must not reconstruct requests from current templates.")

    monkeypatch.setattr("kinloyalty.manifest.render_prompt", fail)
    monkeypatch.setattr("kinloyalty.prompts.load_prompt_library", fail)
    assert _run(plan, MockClient()).valid == 4


def test_cli_manifest_and_mock_run_resume(tmp_path: Path) -> None:
    """Exercise the installed offline commands and inspect completion summaries, not outcomes."""
    executable = Path(sys.executable).parent / "kinloyalty"
    manifest, log = tmp_path / "smoke.jsonl", tmp_path / "attempts.jsonl"
    built = subprocess.run([str(executable), "manifest", "--config", str(ROOT / "configs/study1.yaml"), "--phase", "smoke", "--output", str(manifest)], text=True, capture_output=True, check=True)
    assert "4 planned trials" in built.stdout
    command = [str(executable), "run", "--manifest", str(manifest), "--log", str(log), "--client", "mock"]
    first = subprocess.run(command, text=True, capture_output=True, check=True)
    second = subprocess.run(command, text=True, capture_output=True, check=True)
    assert json.loads(first.stdout)["calls_started"] == 4
    assert json.loads(second.stdout)["calls_started"] == 0
    assert all(record["synthetic"] for record in read_jsonl(log))
