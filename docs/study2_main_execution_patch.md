# Study 2 main execution — approved mechanical extension

Date: 2026-11-26 (Asia/Kolkata). The researcher authorized the main run and then
explicitly approved: "make those two mechanical changes. Preserve prereg-study2,
test and commit the patch, and record both hashes in every turn and episode
record. Then run all 960 episodes under my previous instructions."

This is a documented post-registration mechanical deviation. The original
annotated `prereg-study2` tag remains untouched, pointing to
`c277054e182eb3a81a475108fa3439e96e869bb0`. The locked addendum, main manifest,
configuration, prompts/cards/schemas, model roster/providers, negotiation engine,
scoring and analysis remain unchanged. No main outcome has been observed while
preparing this patch.

## Changes

1. Add main-only execution authorization and a dedicated launcher that accepts
   exactly the frozen 960-episode manifest. SHA-256 must match the addendum:
   `293fecc0f30249e46a794d3d4e1d7d2eacb51e3ad2e13b2113da7067e0a7b814`.
   Preserve the registered concurrency, sequential turns, identical invalid
   re-ask, four API attempts/response opportunity, 120-second attempt timeout,
   1/2/4 backoffs, exclusion and recovery behavior. Resume unfinished episodes
   automatically from the same clean execution commit until none remain; halt
   on returned-version drift or nonretryable errors for researcher review.
2. Put `registration_git_commit` (the original tag's target) and
   `execution_git_commit` (the actual committed patch revision) on every main
   turn and terminal episode. The existing `git_commit` denotes actual execution,
   not an assertion that the unmodified registration code was executed. Replay
   checks both fields, clean-code provenance and the immutable resume contract.
   Prior smoke/pilot record formats and artifacts remain unchanged.

The launcher verifies all registered bytes except the explicitly approved
execution/provenance modules and accompanying decision-log/test adjustments.
New launcher/report code is pinned by the committed execution revision. It
requires that exact clean revision on every invocation. Main data are collected
externally to keep the checkout clean; no source/prompt/config edit is allowed
while collection is running. Keys come only from ignored .env, excluding process
values, using unchanged provider adapters; no key or request header is logged.

There are at most **11,520 ordinary turn calls** (960 × 12), plus the registered
invalid re-asks/API retries. A full initial response-attempt ceiling would be
92,160 if every position needed a re-ask and four attempts for each opportunity.
The researcher instructed resumption until all 960 terminate, without imposing
a cumulative attempt ceiling; exhaustion leaves episodes unfinished, never
silently excluded. The contract explicitly represents no aggregate cap while
retaining each four-attempt opportunity and every cumulative attempt/counter.
This does not increase any smoke/pilot budget or add probes.

## Checks and reporting

Synthetic no-network tests cover main scope, wrong hash/tag/dirty execution,
dual provenance on all record types, altered-provenance rejection, replay,
invalid re-asks/exclusions, exhausted retries/resumptions, automatic continuation,
model-drift halt and the immutable execution contract. Existing registration
verification tests read the original snapshot from the preserved tag, because
the approved execution patch intentionally differs from that original snapshot.
No registered artifact is overwritten to make that check pass.

The dedicated `main_report` module emits collection mechanics only: completed/
planned, exclusions, re-asks, API errors/retries and episode resumptions for all
48 pair/condition cells, unfinished identities, both hashes, replay counts and
largest log. It does not compute or report prices, deal rates, surplus shares,
mandate outcomes or hypothesis tests. No Study 2 analysis is run on main data.

Commit this tested patch before the first paid call. Record its actual full SHA
in the launch argument, preflight, immutable collection contract, every record,
and final run report. At completion check replay, hashes, no keys in logs, and
all files under 50,000,000 bytes; copy raw logs unchanged, commit only logs and
run-report artifacts, and annotate `study2-data` with a one-line mechanical
summary. Ask the researcher before pushing. Then stop before analysis.

Validation before paid execution: **565 offline tests passed in 158.78 seconds**,
including seven new main execution/provenance/reporting checks and all existing
regressions. The registration snapshot is verified from the original immutable
tag. No scientific implementation or registered artifact was changed.
