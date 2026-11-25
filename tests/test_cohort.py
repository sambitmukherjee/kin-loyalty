"""Check shared limits and fatal-error cancellation across separate mock batches."""

import asyncio
from collections import Counter
from pathlib import Path

import pytest

from kinloyalty.clients.base import ClientError
from kinloyalty.clients.mock import MockClient
from kinloyalty.cohort import CohortStopped, run_cohort
from kinloyalty.logs import read_jsonl
from kinloyalty.manifest import build_manifest, write_manifest


ROOT = Path(__file__).resolve().parents[1]


def _batches(directory: Path) -> dict:
    batches = {}
    for phase in ("pilot", "comprehension"):
        counts, selected = Counter(), []
        for trial in build_manifest(ROOT / "configs/study1.yaml", phase):
            if counts[trial["model"]] < 2:
                counts[trial["model"]] += 1
                trial["execution_position"] = len(selected) + 1
                selected.append(trial)
        manifest, log = directory / phase / "manifest.jsonl", directory / phase / "attempts.jsonl"
        write_manifest(selected, manifest)
        batches[phase] = (manifest, log)
    return batches


def test_cohort_shares_limits_and_preserves_separate_logs(tmp_path: Path) -> None:
    """Concurrent batches cannot double global or per-model HTTP concurrency."""
    batches = _batches(tmp_path)

    class TrackingMock(MockClient):
        def __init__(self):
            super().__init__()
            self.active = 0
            self.maximum = 0
            self.by_model = Counter()
            self.model_maximum = Counter()

        async def complete(self, request):
            self.active += 1
            self.by_model[request.api_model_id] += 1
            self.maximum = max(self.maximum, self.active)
            self.model_maximum[request.api_model_id] = max(self.model_maximum[request.api_model_id], self.by_model[request.api_model_id])
            try:
                await asyncio.sleep(.01)
                return await super().complete(request)
            finally:
                self.active -= 1
                self.by_model[request.api_model_id] -= 1

    client = TrackingMock()
    summaries = asyncio.run(run_cohort(batches, client))
    assert client.maximum <= 4 and max(client.model_maximum.values()) == 1
    assert all(summary.valid == summary.planned == 8 for summary in summaries.values())
    for phase, (_, log) in batches.items():
        records = read_jsonl(log)
        assert len(records) == 8 and all(record["phase"] == phase and record["synthetic"] for record in records)
        assert not log.with_name(log.name + ".pending.json").exists()


def test_nonretryable_failure_stops_cohort_and_preserves_real_error(tmp_path: Path) -> None:
    """Do not spend the rest of a cohort after authentication/parameter failures."""
    batches = _batches(tmp_path)

    class FailingMock(MockClient):
        async def complete(self, request):
            if not self.requests:
                self.requests.append(request)
                raise ClientError("bad_request", retryable=False, status_code=400)
            await asyncio.Event().wait()

    with pytest.raises(CohortStopped) as stopped:
        asyncio.run(run_cohort(batches, FailingMock()))
    assert stopped.value.failure["kind"] == "bad_request"
    assert stopped.value.failure["status_code"] == 400
    records = [record for _, log in batches.values() for record in read_jsonl(log)]
    assert sum(record["api_error"]["kind"] == "bad_request" for record in records) == 1
    assert all(not record["outcome"]["excluded"] for record in records)
    assert all(not log.with_name(log.name + ".pending.json").exists() for _, log in batches.values())


def test_cohort_rejects_overlapping_logs_before_calls(tmp_path: Path) -> None:
    """Separate batches must not share a writer destination."""
    batches = _batches(tmp_path)
    batches["comprehension"] = (batches["comprehension"][0], batches["pilot"][1])
    client = MockClient()
    with pytest.raises(ValueError, match="separate attempt logs"):
        asyncio.run(run_cohort(batches, client))
    assert not client.requests
