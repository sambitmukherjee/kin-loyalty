# Study 2 Phase 3: frozen plans, durable mock collection, recovery, and replay

Date: 2026-11-26 (Asia/Kolkata).

The researcher instructed: "Push the commit. Then proceed with Phase 3."
Pushed Phase 2 commit `05f4cd99ef48b7294202ce005fe86b8d97e9158e` to `origin/main`
and independently verified that exact remote branch tip. Neither Study 1 tag
was moved or pushed. The Phase 3 work described here is a subsequent local
commit, outside that earlier push authorization.

## What changed

| File(s) | Responsibility |
| --- | --- |
| `negotiation/manifest.py` | Balanced synthetic, pilot, and smoke plans; immutable row digests and exact source/schema snapshots |
| `negotiation/config.py`, `prompts.py`, `review.py`, `requests.py` | Rendering/resumption from saved source text and schemas, without reading current source files |
| `negotiation/engine.py` | Durable start/completion hooks, permits before timeout, fixed-prefix probes, and attempt-cap hooks |
| `negotiation/journal.py` | Per-pair append/fsync and pending reservations using existing locking/journal mechanics |
| `negotiation/history.py` | Independent response revalidation, state reconstruction, and deterministic terminal summaries |
| `negotiation/collection.py` | Collection binding checks, pending recovery preparation, terminal verification, read-only replay |
| `negotiation/runner.py` | Concurrent episodes with sequential turns, per-model limits, durable resume, repair/deduplication, and persistent probe budget |
| `negotiation/probes.py`, `cli.py` | Unscored probe reports with exact transcripts, and isolated Study 2 commands |
| `src/kinloyalty/cli.py` | Approved additive `study2` dispatch/help entry; existing Study 1 commands/defaults retained |
| Three new test modules | Manifest/design checks, whole collections, hard-kill recovery, budgets, CLI, and serialization/integrity checks |

All `negotiation/` paths above are under `src/kinloyalty/`. Data dictionary,
adding-a-game guide, decision log, and `data/study2/README.md` document the
contracts and artifact layout. No shared provider, Study 1 validator, manifest,
runner, logger, or analysis module was edited. Study 1 research artifacts and
tags are preserved. The only shared-code edit is the explicitly approved CLI
extension.

## Frozen plans and design balance

A manifest contains complete assignment/scenario facts, exact study/model YAML,
template text, probe fixtures, and all turn schemas. SHA-256 digests bind source
text, schema content, each row, and the complete saved manifest. Saved rows are
validated for unique identities, pair membership, seed consistency, private
limit ranges, scenario matching, item/opener balance, self-pair alternative
names, and probe coverage before any client is called.

Full **synthetic** plans require three explicit seeds separate from the main
design. Their 960 episodes contain 320 scenarios shared across three conditions,
exact item/opener balance, and the specified rotating 7/7/6 self-pair names. The
configured main scenario seed has not been used, and no actual main manifest
was generated. Actual main generation has a separate library lock-phase gate
and is unavailable from the current CLI.

Pilot plans contain five distinct scenarios per pair (80 episodes), one per
item; opener alternates by pair/item index. Conditions cycle by pair plus item
index, giving totals 27/27/26. Pilot scenario/order seeds are separate from the
main seeds. This is a recorded mechanical allocation convention, not an
outcome-driven choice. Smoke plans have four natural not-disclosed self-pair
episodes plus sixteen individually marked forced-position probes.

## Logs, scheduling, and recovery

The frozen manifest is the runtime source. Current config/template files are
not read during execution or resumption; a test removes the original source
directory and still reconstructs exact requests from the snapshot. The stored
turn schemas are checked against this implementation before running, so a
schema-code change cannot silently alter a saved plan.

`turns/<buyer-key>__<seller-key>.jsonl` stores one append-only log per pair.
Attempts retain full requests/payloads, raw normalized responses, usage/reasoning/
cache metadata, validity/action/price, actual model and role, timing, source and
manifest bindings, planned identities, actual dispatch sequence, runner policy,
and code/package/SDK provenance. Actual credentials/transport headers are never
captured. Arbitrary model-supplied JSON price content remains intact under the
approved ignore-price exception, even if its keys resemble transport metadata.

Before each call, an fsynced pending reservation stores its exact identity and
request. Completion appends/fsyncs one record and clears its reservation. A
collection lock prevents another writer. Hard-killed reservations become
explicit interrupted attempts on resume; unknown responses are never invented.
Stale reservations whose completed records already exist are checked and
cleared without duplicating the record. Partial/corrupt JSONL tails stop the
runner and remain unchanged for deliberate recovery.

All completed records, pending candidates, and episode/probe summaries are
validated before recovery appends or new calls. Replay rebuilds each response's
validity and every pure state transition rather than trusting saved outcome
fields. It rejects changed requests, validation flags, outcome summaries,
manifest bindings, duplicate dispatch identities, and unknown pair logs. Missing
terminal summaries after a crash can be rebuilt once from complete turn logs.
Replay itself is read-only and rejects active writers or unresolved pending calls.

Episodes interleave in the seeded plan order while each episode's turns remain
sequential. Global call concurrency is four and per-model concurrency is one,
shared across buyer/seller roles and self-pairs. Permits are acquired before the
API timeout; queue time is not charged as API time. API-error budgets restart on
explicit resume, while invalid-response counts and exact re-ask requests persist.
Nonretryable failures stop the batch after safe metadata is persisted.

`episodes.jsonl` contains one recomputed terminal record per natural episode,
including card/scenario metadata, accepted price/role, surplus/mandate flags,
mismatch diagnostics, and re-ask/retry counts. `probes.jsonl` is separate and
contains no surplus score or hypothesis estimate. `run_summary.json` is a
replaceable mechanical convenience summary; append-only attempts are authoritative.

## Probe budget and separation

Each model/role is probed once at messages 11 and 12 using the fixed hand-written
prefixes. A valid response or two invalid replies completes that single probe
position; a message-11 offer does not start another paid turn. Every attempt is
marked `phase: smoke`, `is_probe: true`. Probe summaries/reports are unscored,
excluded from natural episode records, and never eligible for inference.

The approved **32-attempt total cap** persists across invocations and includes
API errors and uncertain interrupted reservations. Each probe still has only
one invalid-response re-ask. When the cap is exhausted, remaining probes stay
unfinished; rerunning does not reset the budget. Reports include every probe's
exact system/user request and original transcript prefix.

## Verification and commands

The new checks include complete 960-episode mock collection/replay, unchanged
zero-call resumption, hard process kills during original/re-ask calls at message
3, source removal, corrupt tails, tampered records, terminal repair, stale
journals, writer locking, global/per-model/sequential limits, and persistent
probe budgets. The full synthetic collection completed **960 episodes in 6,240
mock calls**, with zero probes or unfinished episodes; an independent replay
verified every outcome. Pair logs were about 3 MB at most, and the full-design
test verifies each remains below 50 MB. These are explicitly synthetic
verification results.

Use a fresh temporary directory from the repository root:

```sh
.venv/bin/kinloyalty study2 manifest --phase smoke --output /tmp/study2-smoke-plan.jsonl
.venv/bin/kinloyalty study2 run --client mock \
  --manifest /tmp/study2-smoke-plan.jsonl --directory /tmp/study2-smoke-mock
.venv/bin/kinloyalty study2 replay \
  --manifest /tmp/study2-smoke-plan.jsonl --directory /tmp/study2-smoke-mock
.venv/bin/kinloyalty study2 probe-report \
  --manifest /tmp/study2-smoke-plan.jsonl --directory /tmp/study2-smoke-mock \
  --output /tmp/study2-probe-report.json
.venv/bin/python -m pytest
```

Manifest/report creation refuses existing output files. Repeating `run` resumes
existing work and makes zero calls for final units. For a full synthetic plan,
use `--phase synthetic --scenario-seed 101 --order-seed 102 --swapped-seed 103`.
Mock output is blocked from real-study artifact directories, including all
Study 1 data/prompt/result paths and Study 2's real smoke/pilot/main paths.
No command invokes Study 1 analysis or reads its main response logs.

The final regression suite passed **512 tests** in 64.43 seconds: all 485 prior
tests and 27 additional Phase 3 checks. Preservation checks are recorded in
`docs/decisions.md`.
The Phase 1 templates, config, and review examples remain byte-identical.
`codex_prompts/` remains ignored and untracked. No real provider call, main
Study 2 scenario draw, or actual main-manifest generation occurred.

## Next gate: Phase 4 smoke test

The collection entry points still enforce mock execution. Phase 4 requires
explicit permission, clean committed live-execution glue, and smoke checks of
version drift, schema acceptance, usage/stop/cache fields, and request length.
The existing clients can be reused; any newly needed shared client change must
be explained and approved separately.

Proposed spending scope: four natural self-pair episodes under `not_disclosed`,
up to 48 ordinary turn calls. The fixed one-re-ask/four-API-attempt policy has a
worst-case bound of 384 natural attempts for one complete invocation. The
already approved sixteen probes allow at most 32 probe attempts, giving a
proposed combined ceiling of **416 attempts**; ordinary successful calls would
use at most 64. This natural-attempt allowance requires approval, and a bound
must persist across any smoke resumptions rather than reset silently. No such
real-call budget was spent or newly assumed in Phase 3. Stop on model drift
and report before proceeding. Commit Phase 3 locally and stop for this gate.
