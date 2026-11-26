# Study 2 Phase 8 — local registration lock

Snapshot date: 2026-11-26 (Asia/Kolkata). Phase 7 commit
`aa115dd7038cefe94b7014b9e3826c9e0f27b549` was pushed and independently verified
before this phase. The researcher then authorized Phase 8. **Main collection
remains unstarted.** The Phase 8 commit/annotated tag are local until a separately
approved push; this report does not claim a remote timestamped lock.

## Deliverables

- Final `preregistration/study2.md`, referring to the unchanged Study 1 hypotheses
  and P2 estimand, with protocol, disclosure, scenario rules, seeds, schema/
  validation exceptions, logging/replay, pilot versions/limits, all analyses,
  deviations policy, exact reproduce command, source hashes, all ten prompt
  sources in full, five resolved card texts, and three unique canonical schemas.
- `data/study2/main/manifest.jsonl`: **960** planned episodes, **320** unique
  scenarios, **16** ordered pairs, 20 scenarios/pair reused under all three
  conditions. Scenario/order/swapped seeds are 2026112605/2026112606/2026112610.
  SHA-256: `293fecc0f30249e46a794d3d4e1d7d2eacb51e3ad2e13b2113da7067e0a7b814`.
  There is no collected main episode or attempt; only the manifest exists.
- `preregistration/study2-lock.json`: machine-readable source/data/document
  inventory, ordered canonical schemas, seed/analysis settings, main and pilot
  references, analysis/runtime commits, preserved Study 1 identities and
  validation record. Its own hash is excluded to avoid self-reference; the
  annotated tag binds the registration JSON and every registered artifact.
- Offline `kinloyalty.negotiation.registration` verifier and four tests for
  deterministic main-plan/payload verification, tamper detection, path bounds,
  exact prompt appendices and canonical schema property order. It never loads
  credentials, calls a model, scores a main outcome, or runs inference.
- Updated decision log, data dictionary, adding-a-game guide, and README status.
  Scientific config/prompts, provider adapters, engine, runner, and Phase 5
  analysis remain unchanged. The verifier is lock tooling, not a protocol fix.

## Verification

All **558 offline tests passed in 132.55 seconds**, including four new lock
checks and the existing Study 1/Study 2 regression suite. The main plan
regenerates byte-identically, and the exact balance/rotation checks pass.
Scientific source/config/prompt/client bytes and the Phase 5 analysis are
unchanged. The locked Study 1 manifest was rebuilt in memory to its exact
SHA-256, and both immutable Study 1 tags and all 48 smoke/pilot artifact digests
remain preserved. The original rendered prompt review and all three approved
analysis definitions were checked; `codex_prompts/` stays ignored/untracked.

Two fresh Study 2 reproduce runs on the same explicitly synthetic 960-episode
log fixture, each at **10,000 bootstrap and 10,000 permutation replications**,
produced **27 byte-identical artifacts** including all PDF/PNG and NPZ files.
They recover the planted −0.20 share contrast, +0.20 signed-concession contrast,
and zero interaction within 1e-12, with the required interval ranks. These are
mock test inputs/results, not empirical findings or actual main data. The full
verification record is `docs/study2_phase8_validation.json`, including tested
source/output hashes. No actual main inference or paid call was performed.

The validator checks exact file hashes, regenerates the main manifest
byte-identically, validates every one of **11,520** possible request positions
(960 × 12) with disposable offer prefixes, and confirms default sampling,
low effort, 8,192 output caps and provider payload bindings. Those prefixes are
shape fixtures only: no model reply, negotiation outcome or main data record is
generated or saved. Canonical schema property order is preserved exactly.

Full synthetic reproduction uses independent fixture seeds (73101/73102/73103),
not main limits or scenarios, and the production 10,000 bootstrap/permutation
counts. It invokes Study 2 alone. No real smoke/pilot or Study 1 main outcome
inference is part of this phase. All prior smoke/pilot artifacts stay unchanged.

## Checking the lock

From the frozen checkout and repository environment:

```sh
.venv/bin/python -m kinloyalty.negotiation.registration --require-unrun --tag
.venv/bin/python -m pytest -q
```

`--tag` checks that `prereg-study2` is annotated and contains every registered
byte, including the registration JSON. Before the tag is created, omit that
flag. `--require-unrun` is appropriate at this gate: only the manifest may exist
in the main directory. After a later authorized collection, omit that flag to
check the registration snapshot without analysing any outcome.

After a separately approved main collection, the exact results command is:

```sh
.venv/bin/kinloyalty study2 reproduce \
  --manifest data/study2/main/manifest.jsonl \
  --directory data/study2/main \
  --output results/study2/main
```

Do not run it on the uncollected plan. No main collection or analysis command
was executed in this phase. Future main execution requires separate researcher
scope/budget approval; any authorization glue or other change after this lock
must be recorded under the addendum's deviations policy. Current live entry
points remain smoke/pilot-only.

## Scope boundary

No post-pilot mechanical fix was made. Gemini's unobserved natural final-turn
rate and missing provider cache fields remain explicit limitations, with prior
fixed probes kept separate. All three approved analysis clarifications remain
in the final addendum. No Study 1 outcome log was read or analysed, immutable
Study 1 tags/data/results remain preserved, and `codex_prompts/` remains ignored
and untracked.

Commit and create the annotated local `prereg-study2` tag after checks pass.
Then stop for permission to push the concrete commit/tag. The main run is a
separate future instruction; unused smoke/pilot budgets do not authorize it.
