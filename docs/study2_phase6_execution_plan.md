# Study 2 Phase 6 pilot execution plan

Date: 2026-11-26 (Asia/Kolkata). The researcher explicitly approved the proposed
80-episode pilot and 7,680-attempt ceiling, then instructed: "Push the Phase 5
commit. Then proceed with Phase 6." Pushed Phase 5 and independently verified
remote `main` at `a91efd59f082ee9cb72ea67d6b7e47d6ebce6eec` before preparation.

## Approved scope

- Exactly 80 natural pilot episodes: five for each of 16 ordered pairs,
  including self-pairs. No probes and no replacements for exclusions.
- At most 960 ordinary calls (12 valid message positions × 80 episodes).
  One identical invalid-response re-ask per turn and four API attempts per
  response opportunity give an approved total ceiling of **7,680 attempts**.
  The saved contract and counters enforce this ceiling across resumptions,
  including API failures and uncertain interrupted reservations.
- Concurrency four overall and one request per model. Turns within an episode
  remain sequential. Existing 120-second timeout and 1/2/4-second backoffs;
  provider SDK hidden retries stay disabled.
- No model, prompt, card, schema, sampling, output-cap, mandate, or scientific
  configuration change. Reuse the existing provider adapters unchanged, with
  low effort, default sampling, 8,192 output caps, and frozen endpoints/caching.

The externally frozen manifest has 80 episodes, 16 pairs, five per pair, one
item per pair, and opener/condition rotation as implemented and reviewed in
Phase 3. Pilot scenario/order seeds are **2026112603 / 2026112604**, separate
from the unused main seeds. Manifest SHA-256:

`9e68d40288fc68621359c254c1d30e60d67684f5a09157748f215e6a08f6278e`

The original is `/private/tmp/kinloyalty-study2-pilot-20261126-dotblv2t/manifest.jsonl`.
Collect externally from clean committed preparation; then copy the original raw
files unchanged into `data/study2/pilot/` and the report into
`results/study2/pilot-report/`. All .env credentials were present; no value was
printed. Credentials are read only from the checkout's ignored `.env`, explicitly
excluding process environment values, using the already tested shared loader.

## Authorization and drift controls

`PilotAuthorization` fixes `phase: pilot`, `natural_attempt_cap: 7680`, and
`probe_attempt_cap: 0`, researcher/date approval, and prior returned versions.
Smoke authorization cannot run pilot and pilot cannot run smoke/main. Ordinary
CLI `run` remains mock-only; the dedicated approved live entry point is
`python -m kinloyalty.negotiation.pilot`. It refuses dirty code and wrong scopes.
Replay now enforces the exact approved pilot budget contract.

Required prior returned strings are unchanged:
`claude-sonnet-5-5`, `gpt-6.1-terra`, `gemini-4-hydrogen`, `kimi-k3.1-pro`.
Read only Study 1's locked registration version table, not its outcome logs.
Each response is durably recorded before any model-version drift halts dispatch.
Missing or changed versions stop queued calls and require researcher review;
there is no automatic substitution or continuation after logged drift.

Retryable exhaustion leaves an episode unfinished, not excluded. Resume the
same frozen manifest with the same contract and existing counters until all
80 terminate, within the approved total budget. Halt and report incompatible
requests, nonretryable errors, version drift, or exhausted phase budget. Do not
silently edit prompts, schemas, API parameters, or data to resolve a problem.

## Blind mechanical report

`kinloyalty.negotiation.pilot_report` performs full attempt replay and reports:

- Received-response validity per model for message 1, messages 2–11, and message
  12, plus a role breakdown. Validity must exceed 95%; API errors are separate
  from invalid responses. Unobserved cells are marked not observed and retained
  as coverage flags, never treated as 100% valid. Earlier smoke probes do not
  enter pilot denominators or outcome tables.
- Complete/impossible/unfinished states, truncation, reasoning counts, caches,
  maximum provider input tokens against 4,096, version strings and clean-code
  provenance, budget use, and episode-length distributions/reach of message 12.
  Missing token fields remain null, distinct from zero, as previously approved.
- Outcomes per pair **pooled over all disclosure conditions**: deals, both
  impasse types, exclusions, retained shares, episode lengths, and mandate
  violations. No disclosure comparison, P2 estimate, hypothesis test, or main
  analysis is computed. The inference loader continues to reject pilot input.
- Valid acceptances and acceptance-price mismatches per actual responding model,
  pooled over labels/pairs, retaining role breakdowns. Supplied prices remain
  recorded and ignored. No frequency-based automatic fix threshold exists;
  the researcher decides whether observed mismatches suggest misunderstanding.

Offline tests cover exact scope/caps, resume and immutable contracts, API retry
exhaustion, drift preservation/halting, wrong/dirty entry points, report blindness,
actual responding-model mismatch attribution, invalid exclusions, unobserved
validity cells, and continued rejection by the inference loader. Commit and pass
full offline/preservation checks before starting paid execution.

Preparation verification: **554 offline tests passed in 119.15 seconds**,
including seven new pilot tests and all existing Study 1/Study 2 checks. Verified
the locked Study 1 manifest digest/tags, unchanged scientific sources, clients,
Phase 5 analysis, addendum draft and real smoke artifacts, exact Phase 1 rendered
review, frozen external pilot digest, unused main manifest, and untracked
`codex_prompts/`. Commit this preparation before making any real provider call.

## Stop after Phase 6

Copy and hash the raw artifacts/report, independently replay them, scan for any
exact credential value without exposing it, finish `docs/study2_phase6_report.md`,
and commit locally. Push only if subsequently requested. The report may identify
mechanical problems, but Phase 7 fixes require separate researcher approval;
none are triggered by outcome levels. Do not generate main scenarios, finalize
the unlocked addendum, create the registration tag, or start a main run.
