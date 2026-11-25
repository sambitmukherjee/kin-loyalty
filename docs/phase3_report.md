# Phase 3 report — 2026-11-25

## Completed work and approvals

Pushed the approved Phase 2 commit `a7c7ba9` to the private GitHub repository
before starting Phase 3, as directed. Recorded approval of all prompt text,
schemas, and name pairs. The 18 experimental text templates are unchanged from
that approved commit; the review's approval metadata was updated.

Implemented deterministic balanced manifests with frozen requests, a common
client interface and reproducible mock client, strict local validation, bounded
concurrency, API retries/backoff, one identical re-ask, exclusions, append-only
attempt logs, and durable resume. The CLI supports mock execution only.

The researcher selected the exact pilot and comprehension allocation proposals:
four pilot draws/label split 2/1/1 across paraphrases with rotated extras; and
the other-lab comprehension matrix `[[3,2,2],[2,3,2],[2,2,2]]`. These choices are
in the YAML and decision log.

Infrastructure defaults selected within Phase 3 are four concurrent trials,
one/model, 120-second call timeout, four API attempts per response opportunity,
and exponential 1/2/4-second backoff capped at 30 seconds. The one invalid-response
re-ask remains separate from API retries.

## Files created or changed

| Files | Work |
| --- | --- |
| `src/kinloyalty/manifest.py` | Seeded plans, exact allocations, stable IDs, source hashes, frozen requests, non-overwriting JSONL output |
| `src/kinloyalty/clients/base.py`, `clients/mock.py`, `clients/__init__.py` | Shared request/response/error interface and explicitly synthetic offline client |
| `src/kinloyalty/validate.py` | Strict JSON, flat schema, range, enum, and output-truncation checks |
| `src/kinloyalty/logs.py` | Append/fsync attempt logs, atomic in-flight journal, exclusive writer lock |
| `src/kinloyalty/state.py`, `runner.py`, `provenance.py` | Resume integrity, retries/re-asks, scheduling, mechanical summary, UTC/code/package/SDK provenance |
| `src/kinloyalty/cli.py` | `manifest` and mock-only `run`, including resume |
| `src/kinloyalty/review.py`, `docs/study1_prompt_review.md` | Prompt approval metadata; experimental request text unchanged |
| `configs/study1.yaml` | Approved prompt/name statuses, exact allocation rules/matrix, infrastructure defaults |
| `.gitignore` | Ignore empty local `*.jsonl.lock` advisory files; keep research JSONL versionable |
| `tests/conftest.py`, `test_manifest.py`, `test_validate.py`, `test_runner.py` | Network blocking, exact counts/rotations, schema failures, retries/timeouts, concurrency, interruption/recovery, CLI tests |
| Existing configuration/review tests | Reflect approval metadata and current CLI wording |
| `docs/engine.md`, `data_dictionary.md`, `decisions.md` | Complete engine behavior, every persisted field, approvals, choices, and recovery limits |
| `README.md`, template index, model/game extension guides | Current commands, approval status, engine boundaries, and reuse instructions |

No new dependencies were added. Provider implementations, real batches, analysis,
Study 2, the pre-registration lock, and the real main run remain later work.

## Verification and reproduction

The offline suite checks the exact 3,600 main / 240 pilot / 320 comprehension /
4 smoke plan counts, all rotations, deterministic serialization, stable IDs,
preserved schema order, and rejection of inconsistent allocation settings.

Engine checks cover valid replies, one identical re-ask, two-invalid exclusion,
API errors without exclusion, exponential/capped backoff, timeouts, global and
per-model concurrency, canonical local bounds after client-side adaptation,
fail-fast behavior, changed/corrupt history, concurrent-writer rejection, and
idempotent resume. Tests kill a child process during an initial call and after
an invalid first reply, then recover its journal without resetting re-ask state.

Final result: **198 offline tests passed**. Wheel/source builds passed offline;
archive checks confirm the engine modules and all exact templates are included
and local instructions/secrets are excluded. Python syntax/public docstrings,
unchanged approved text, and Git tracking rules were also checked. See the
phase-end verification entry in `docs/decisions.md`.

An installed-CLI smoke demo produced four valid synthetic records. Repeating the
same command produced zero new calls and four already-final draws. Artifacts were
created under a fresh `/private/tmp/kin-loyalty-phase3-*` directory, outside the
real study data directories. Main plans were built/tested in temporary locations;
no pre-registration/main manifest or main data were retained in the repository.

To check from the project folder:

```sh
.venv/bin/pytest
kinloyalty_demo_dir="$(mktemp -d /private/tmp/kin-loyalty-demo.XXXXXX)"
.venv/bin/kinloyalty manifest --phase smoke \
  --output "$kinloyalty_demo_dir/manifest.jsonl"
.venv/bin/kinloyalty run --client mock \
  --manifest "$kinloyalty_demo_dir/manifest.jsonl" \
  --log "$kinloyalty_demo_dir/attempts.jsonl"
# Repeat the run command: calls_started should be 0.
```

## Limits and next phase

No paid model calls were made. Mock usage is synthetic, every mock record is
marked synthetic, and no pilot label-effect comparisons were computed. Provider
support and precise SDK field mappings remain unverified.

Local locking currently uses `fcntl` on macOS/Linux. Unknown interrupted calls
are retained as unfinished attempts; a partial/corrupt JSONL write stops execution
without deleting data and needs deliberate recovery. These limits are documented
in `docs/engine.md`.

Phase 3 ends with a local commit and a stop; only the preceding Phase 2 push was
authorized. The next phase is **4a: official provider documentation verification
and real client adapters**, stopping on any model/setting mismatch. It makes no
paid calls. Phase 4b's four planned real smoke draws require separate approval,
keys, and a stated retry/re-ask allowance.
