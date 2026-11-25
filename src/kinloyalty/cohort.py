"""Run separate frozen batches concurrently under shared limits and fatal-error stops."""

import asyncio
from pathlib import Path

from kinloyalty.clients.base import ClientError, ModelClient, ModelRequest, ModelResponse
from kinloyalty.manifest import read_manifest
from kinloyalty.runner import RunnerLimits, RunnerPolicy, RunSummary, run_manifest


class CohortStopped(RuntimeError):
    """Describe a non-retryable API failure without raw exceptions, keys, or headers."""

    def __init__(self, failure: dict) -> None:
        """Expose only the already-sanitized error identity/status for review."""
        self.failure = failure
        super().__init__("Cohort stopped after a non-retryable API error; inspect durable attempt metadata.")


class _MonitoredClient:
    def __init__(self, client: ModelClient) -> None:
        self.client = client
        self.execution_mode = client.execution_mode
        self.stopped = asyncio.Event()
        self.failure: dict | None = None

    async def complete(self, request: ModelRequest) -> ModelResponse:
        """Signal a fatal categorized error while allowing its durable log record."""
        try:
            return await self.client.complete(request)
        except ClientError as error:
            if not error.retryable and self.failure is None:
                self.failure = {"trial_id": request.trial_id, "kind": error.kind,
                                "status_code": error.status_code, "retryable": False}
                self.stopped.set()
            # Let the ordinary runner persist the real categorized failure first.
            raise

    async def aclose(self) -> None:
        """Delegate resource cleanup if the caller requests it."""
        await self.client.aclose()


async def run_cohort(batches: dict[str, tuple[str | Path, str | Path]], client: ModelClient) -> dict[str, RunSummary]:
    """Run one invocation per batch, sharing four/one limits without merging logs.

    Non-retryable provider errors cancel the other work after preserving the
    triggering API error. In-flight cancellations remain interrupted/unfinished.
    This function never starts another invocation or closes the caller's client.
    """
    if not batches:
        raise ValueError("A cohort requires at least one batch.")
    plans = {name: read_manifest(manifest) for name, (manifest, _) in batches.items()}
    policies = [RunnerPolicy(**plan[0]["runner_settings"]) for plan in plans.values()]
    if any(policy != policies[0] for policy in policies):
        raise ValueError("Cohort batches must use the same frozen runner policy.")
    logs = [Path(log).resolve() for _, log in batches.values()]
    if len(set(logs)) != len(logs):
        raise ValueError("Cohort batches require separate attempt logs.")
    ids = [trial["trial_id"] for plan in plans.values() for trial in plan]
    if len(set(ids)) != len(ids):
        raise ValueError("Cohort batches cannot overlap trial IDs.")
    models = list({trial["model"] for plan in plans.values() for trial in plan})
    limits = RunnerLimits(policies[0], models)
    monitored = _MonitoredClient(client)
    jobs = [asyncio.create_task(run_manifest(manifest, log, monitored, shared_limits=limits))
            for manifest, log in batches.values()]
    completed = asyncio.gather(*jobs)
    stopped = asyncio.create_task(monitored.stopped.wait())
    try:
        await asyncio.wait([completed, stopped], return_when=asyncio.FIRST_COMPLETED)
        if monitored.failure is not None:
            raise CohortStopped(monitored.failure)
        return dict(zip(batches, await completed, strict=True))
    finally:
        stopped.cancel()
        for job in jobs:
            if not job.done():
                job.cancel()
        await asyncio.gather(*jobs, completed, stopped, return_exceptions=True)
