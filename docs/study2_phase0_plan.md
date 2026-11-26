# Study 2 Phase 0: repository review and proposed execution plan

Date: 2026-11-26 (Asia/Kolkata).

Status: Phase 0 review finished. On 2026-11-26 the researcher approved the three
clarifications/corrections below and the forced-position smoke-probe budget.
The researcher subsequently explicitly approved Phase 1; its implementation and
review deliverables are documented in `docs/study2_phase1_report.md`. Later phase
starts still require explicit approval.

## Review and baseline

- Read the full Study 2 instructions and `preregistration/study1.md`; reviewed
  the package, configuration, provider adapters, manifest generation, validation,
  CLI, logging/recovery documentation, and offline test fixtures.
- Starting branch: `main`, tracking `origin/main`, at
  `f7dd0a690a5089b245fff365acf002fcfd7b056a`, with a clean working tree.
- Both existing annotated tags are present:
  - `prereg-study1` resolves to
    `d4d6ff9c1f7b84bc2b4f90578873f18dbc9fb98a`.
  - `study1-data` resolves to
    `f7dd0a690a5089b245fff365acf002fcfd7b056a`.
- Rebuilt the Study 1 main manifest in memory, without writing or replacing
  the locked file. All 3,600 planned requests serialize to the registered
  SHA-256, which also matches the saved manifest:
  `a583fe4366893e74735f22fc7f1e45ee7e8d136be5e06ad5d770dfcc1225ee55`.
- Ran `.venv/bin/python -m pytest`: **311 passed, 1 failed** in 32.75 seconds.
  `uv` was unavailable on this shell's PATH; the existing environment uses
  Python 3.11.5 and pytest 9.2.0. No dependencies were installed or updated.
- The failure is
  `tests/test_analysis.py::test_simulation_cannot_write_into_real_study_directories`,
  line 383. Its expected rejection of synthetic output succeeds, but its final
  assertion assumes the real `data/study1/main` directory does not exist.
  Collection has since created that directory. This was the initial baseline;
  the researcher subsequently approved checking that the attempted `synthetic`
  subdirectory was not created instead. Only that assertion has been corrected.
- After that approved correction, `.venv/bin/python -m pytest` returned
  **312 passed** in 32.03 seconds. The in-memory rebuilt and saved Study 1 main
  manifest digests still match the registered SHA-256 above.
- Analysis tests use generated synthetic fixtures in temporary directories.
  No Study 1 main response logs or outcome tables were inspected, and no main
  outcome analysis or summary was computed.
- `.gitignore` already excludes `/codex_prompts/`, and no file in that folder
  is tracked. It will remain excluded from staging and commits.

## Compatibility findings

`ModelRequest` already carries a JSON schema per request. Every real adapter
builds or checks its payload against that request's schema, so a different action
enum and nullable price can be supplied each turn without an identified need to
change the clients. Provider acceptance of the new schemas remains to be tested
offline with injected transports and then in the approved smoke phase. Existing
Anthropic numeric-bound handling must be preserved.

The existing validator supports flat integer/string fields, and the current
runner and manifest format represent single decisions. Study 2 should therefore
have its own negotiation validator, state, runner, manifest, logging/recovery,
replay, and analysis modules. Reuse the existing client interface, safe payload
builder, serialization/hash helpers, provenance, retry conventions, and numerical
inference helpers where their contracts fit. Do not route negotiation through
Study 1's decision engine.

The main planned shared-code extension is an additive `study2` CLI group,
delegating to a new Study 2 command module. Existing Study 1 commands and defaults
would retain their behavior. The phase that adds this entry point requires
explicit approval for that extension, a full regression run, and another
byte-identical Study 1 manifest check. Other shared changes require their own
explanation and approval before editing. A new negotiation mock client can
implement the existing interface without changing Study 1's mock behavior.

## Researcher decisions approved on 2026-11-26

1. **Registration order.** Study 1 Section 1 says Study 2 details will be
   registered before its "data collection". The new instructions explicitly
   require smoke and pilot collection before locking the addendum. Approved
   clarification: the addendum precedes **main-run collection**, while approved
   smoke and pilot data are permitted beforehand and excluded from inference.
   The original Study 1 registration remains unchanged.
2. **Price on non-offer actions.** Study 2 Section 3.4 says the price is null
   for `accept` and `walk_away`, while Section 3.7 says a supplied price is
   ignored and recorded, rather than invalidating the reply. Approved resolution:
   preserve the null instruction, retain the raw supplied price, and let the
   explicit Section 3.7 exception govern local validation/scoring. Keep such
   replies valid. An `accept` always uses the counterparty's latest offer price.
   Additionally record a flag when an `accept` supplies a non-null price that
   differs from that offer. Report the count per responding model, across both
   roles and pooled over disclosure conditions, in the pilot report. Retain the
   role for diagnostics. No frequency threshold or automatic fix is authorized;
   the researcher decides whether frequent mismatches imply misunderstanding.
3. **Existing test failure.** The researcher approved a test-only correction:
   assert that the attempted `data/study1/main/synthetic` output was not created,
   rather than asserting the real collection directory is absent. No production
   code or Study 1 research artifact is changed.

4. **Forced-position smoke probes.** Four natural negotiations cannot guarantee
   that every provider reaches message 12. The researcher approved adding one
   probe for each model, role (buyer/seller), and position (message 11/12):
   **16 calls, plus at most 16 identical re-asks**. Use fixed, hand-written,
   plausible transcript prefixes; buyer probes use the `not_disclosed` card.
   Log every attempt with `phase: smoke` and `is_probe: true`; probes never enter
   analysis or episode outcome summaries. Verify provider acceptance of both
   schemas and that message-12 replies are only `accept` or `walk_away`. Include
   the full transcripts used in the smoke report. Preserve the mismatch flag
   for applicable probe replies too, without mixing them into pilot counts.
   No additional probe API-error retry allowance or budget increase is implied;
   do not exceed 32 total probe call attempts without explicit permission.
   This approval is retained for the smoke phase, not an instruction to make
   calls now or approval for the four natural smoke episodes.

## Proposed phases and acceptance checks

Every phase ends with a local commit and a report of changes, verification,
problems, and the next phase. Stop for explicit permission at every boundary.
No phase approval implicitly approves a push or a subsequent paid run.

### Phase 1: configuration, scenarios, and exact prompts

Create `configs/study2.yaml`, `prompts/study2/`, and focused scenario/prompt
modules under `src/kinloyalty/negotiation/`. Preserve the exact Alex/Jordan
templates, mandates, card fields, and one-wording design. Keep prices, draw
ranges, message limit, cards, opener balance, seeds, and run settings configurable.

Propose explicit, distinct deterministic seeds for smoke, pilot scenarios/order,
main scenarios/order, mock data, bootstrap, and permutation. Specify nearest-$5
rounding, including the tie rule, in configuration/documentation. A proposed
self-pair rotation assigns the six-count alternative to the next model in the
four-model cyclic roster; each alternative model then receives that shortfall
once across the four self-pairs. The remaining alternatives receive seven each.
Record these conventions for review before locking them.

Produce `docs/study2_prompt_review.md` containing fully rendered system/user
requests for a cross-pair and a self-pair, all three disclosure conditions, both
roles, and messages 1, 2, 11, and 12. Use illustrative scenarios and valid
synthetic transcript prefixes with the appropriate opener. Do not draw or expose
the main-run scenarios before the lock phase. Test rendering, seller-card
absence, shared scenario facts, limits, and scenario/item/opener balance.

### Phase 2: pure protocol and episode engine

Implement pure state transitions, turn-specific schemas, transcript rendering,
validation, outcome scoring, and the engine. Introduce a negotiation mock client
with scripted/rule-based offers, acceptances, walk-aways, malformed/truncated
replies, API errors, and a configurable planted label effect.

Test all turn/action boundaries; escaped one-line transcripts; latest-offer
acceptance; all four terminal outcomes; shares outside [0, 1]; both mandate
violations; exactly one identical re-ask; and separate API retry accounting.
Test that non-offer supplied prices remain valid and are retained but ignored
in scoring, and that the acceptance-price mismatch flag follows the approved
rule without changing the agreed price.
Preserve Study 1's four-attempt retry policy, 120-second timeout, and 1/2/4-second
backoffs. Make no real calls.

### Phase 3: manifest, scheduling, logging, resumption, and replay

Implement deterministic Study 2 manifests, concurrent episodes with sequential
turns, per-model call limits, one append-only turn log per pair, episode
records, durable pending-attempt recovery, and replay from the turn logs.
Add the approved additive Study 2 CLI group for these operations.
Implement fixed-position smoke probe execution and explicit probe markers, with
offline checks of role/position coverage, fixed transcript provenance, the
approved attempt cap, and exclusion from normal episode collection/inference.

Use synthetic seeds to verify a complete 960-episode design: 16 ordered pairs,
20 scenarios/pair reused across all three conditions, exact item/opener balance,
and the self-pair 7/7/6 rotation. Test separate pilot draws, immutable request
bindings, mid-episode resumption, invalid-count persistence, interrupted calls,
writer locking, tamper rejection, and exact replay agreement. Do not freeze or
execute the main manifest yet. Re-run all regression tests and the Study 1
manifest hash check after the CLI extension. Make no real calls.

### Phase 4: approved live smoke test

Request explicit spending approval for **four self-pair `not_disclosed`
episodes**, up to 48 ordinary turn calls, with possible identical re-asks and
API retries budgeted separately before execution. These are not an unconditional
48-attempt ceiling. Read credentials only from the ignored `.env`, without
logging keys or headers.

Also execute the already approved **16 forced-position schema probes**, with at
most one identical re-ask per probe (16 maximum), within 32 total probe attempts.
For each of the four models, probe buyer and seller at both message 11 and
message 12 using fixed hand-written plausible transcripts. Buyer probes use the
`not_disclosed` card; seller probes have no card. Preserve the exact transcripts
in the smoke report and requests in the logs. Label attempts `phase: smoke` and
`is_probe: true`. These probes are never analysed. Stop rather than exceeding
the approved probe budget; report any incomplete probe work.

Check provider acceptance, schema coverage, usage/reasoning/cache fields,
finish reasons, token lengths, model version strings, and replay. Compare every
returned model string with the Study 1 registration's recorded strings. Stop
on drift; report missing token fields as missing, never invent zeros. Report
schema acceptance per model/role/position, and verify that message-12 responses
contain only `accept` or `walk_away`. Preserve failed attempts/re-asks and report
incomplete coverage. Any extra probes require separate approval.

### Phase 5: complete analysis using mock data only

Create `src/kinloyalty/analysis/study2/` and its independent reproduce command.
Implement the pair-fixed-effect/opener regression and same-minus-other contrast,
within-pair/scenario tested-label permutations, scenario-cluster bootstrap,
bootstrap TOST at +/-0.05, pair-cluster robustness check, all secondary analyses,
descriptives, and PDF/PNG figures matching the existing plotting style.

Use 10,000 production resamples/permutations, fixed named random streams,
count-matched order-statistic intervals, add-one p-values, and the shared
1e-12 conservative tolerance. Specify incomplete-stratum and non-estimability
handling explicitly, without replacing exclusions with impasses or silently
dropping failed resamples. Verify results against independent fits, known mock
effects, ties/bounds, and end-to-end saved synthetic logs. Keep real pilot data
ineligible for this inference path. Make no real calls and run no real analysis.

### Phase 6: approved blind pilot

Request explicit spending approval for **80 episodes**, five per ordered pair,
up to 960 ordinary turn calls, plus a separately stated allowance for re-asks
and retries. Rotate disclosure assignments approximately equally and use a
different scenario seed from the main run.

Complete or explicitly account for all unfinished episodes before closing the
pilot. Produce a mechanical report with validity by model/turn class, re-asks,
exclusions, API failures, token/cache/reasoning/version availability, longest
provider-counted prompt, episode lengths/final-turn coverage, and replay checks.
Include the number of acceptances carrying a non-null price different from the
counterparty's latest offer, per responding model across both roles and pooled
over disclosure conditions. Keep supplied prices and mismatch flags in the logs;
let the researcher decide whether their frequency warrants a mechanical fix.
Report substantive outcome distributions by pair pooled across disclosure
conditions only. Do not compute pilot disclosure comparisons or hypothesis tests.

### Phase 7: approved mechanical fixes

Propose each fix with evidence and affected files before editing. Apply only
approved fixes, preserve original logs, and record dates, reasons, and approvers
in `docs/decisions.md`. Repeat relevant offline checks; obtain a new budget for
any necessary real reruns. Prompt changes require rerunning the affected pilot
portion. Outcome levels cannot justify tuning the design or prompts.

### Phase 8: lock the addendum

After the pilot and approved fixes, generate the final 960-episode main manifest
without making calls. Write `preregistration/study2.md`, referring to the
unchanged P2 hypothesis/estimand in Study 1. Include full prompt/card appendices,
SHA-256 inventories, schemas, scenario rules/seeds/balance, retry/resume and
exclusion rules, pilot version comparisons, all inference specifications,
analysis commit identifiers, reproduction commands, and every approved change.

Verify hashes, regression tests, synthetic reproduction, and Study 1 preservation.
Commit and create the annotated `prereg-study2` tag. Push the concrete commit/tag
only with explicit permission, and distinguish a local tag from a remote
timestamped lock. Stop after the addendum lock; the main Study 2 run is separate.

## How to check Phase 0

Run `.venv/bin/python -m pytest` to verify the approved assertion correction.
The original baseline result above predates that correction. Use
`git rev-parse 'prereg-study1^{}' 'study1-data^{}'` to check the preserved tags,
and `git check-ignore -v codex_prompts/study2-coding-agent-prompt.md` plus
`git ls-files -- codex_prompts` to verify the local instruction folder is ignored
and untracked. The manifest hash check used `build_manifest` and `json_line`
in memory and compared the result with the saved file's digest; it wrote no
Study 1 artifact.

The initial Phase 0 commit created this plan and appended its review status to
`docs/decisions.md`. This follow-up records the researcher's decisions and makes
the one approved test assertion correction. It changes no production code,
configuration, prompt, data, result, or tag. Phase 1 had not started at that
follow-up; its later authorization and work are recorded in the Phase 1 report.
