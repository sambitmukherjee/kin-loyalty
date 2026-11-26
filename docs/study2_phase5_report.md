# Study 2 Phase 5 — analysis pipeline

Date: 2026-11-26. Scope: implement Section 6 and independent Study 2
reproduction, verified only on explicitly synthetic mock data. The researcher
approved the phase after pushing both Phase 4 commits; remote `main` was
independently verified at `dd72fe0a24eb8117952dd566279777fee5a361c2`.

## Result and researcher decisions

The complete analysis is implemented in `src/kinloyalty/analysis/study2/`, with
standalone `kinloyalty study2 analyze` and `reproduce` commands. Both replay saved
attempts before computing results. All three researcher confirmations are
recorded in `docs/decisions.md` and the explicitly **unlocked, incomplete**
`preregistration/study2.md` draft:

1. Signed concessions average changes between consecutive own buyer offers,
   excluding acceptances, with no clipping; fewer than two offers is undefined.
   Eligible counts are reported per condition.
2. All eligible episodes remain in OLS and scenario bootstrap. Only complete
   tested-label pairs swap; incomplete pairs stay fixed. The third condition
   does not affect swap eligibility. Every permutation test reports complete/
   incomplete counts, including singleton/neither-eligible breakdowns.
3. Figure 2 groups by displayed same/other/none. The adjusted interaction is
   `(same-other in self-pairs) - (same-other in cross-pairs)`, with a labelled
   sign convention, a bootstrap interval, and no permutation test.

## Implementation

- Primary pair-fixed-effect/opener/card OLS, same-minus-other contrast,
  scenario-matched bootstrap, tested-pair permutations, shared-resample TOST,
  and the specified pair-cluster robustness check.
- All secondary buyer/baseline/outcome contrasts and the adjusted interaction;
  deal-only conditioning warnings and explicit outcome eligibility.
- Pair/condition and pooled descriptives, mandate counts/rates, actual-kinship
  descriptive means, token/cache availability, input-token maxima and message
  lengths. No semantic coding of text.
- Four PDF/PNG figures in the existing style: displayed label × actual kinship,
  price/agreement under displayed labels, buyer P2 estimates, and share
  distributions by original disclosure condition.
- Frozen analysis seeds and 10,000-replication defaults. Synthetic-only overrides
  support fast tests. Count-matched intervals, add-one tails and conservative
  1e-12 ties follow the existing numerical helpers without editing them.
- Every planned scenario remains in the resampling universe. Missing outcomes
  stay missing. Non-estimable contrasts and failed bootstrap draws are explicit;
  no redraw, imputation, clipping, or silent reduction in replication counts.
- Fresh outputs only, complete input/code/package provenance, raw-input digest
  checks, preserved resampling arrays, and a full output hash inventory.
- Real smoke/pilot/probe and Study 1 inputs rejected before reading responses.
  Synthetic input requires explicit opt-in. Reproduction loads no credentials
  and makes no model calls. Read-only replay supports future approved live
  pilot/main contracts; execution remains smoke-only.

The owned Study 2 CLI and collection reader were extended. No shared Study 1
client, engine, runner, logger, manifest, analysis module, or top-level CLI was
edited. Existing provider/protocol/scientific configurations and prompt text
are unchanged.

## Verification

A production-count verification uses **960 synthetic episodes / 4,320 mock
calls** generated through the actual manifest, engine, journal and replay. The
buyer final-offer increase of 0.20 zone units for same-labelled sellers is a
fixture input. The analysis recovers P2 **−0.20**, signed concessions **+0.20**,
and zero actual-self interaction within numerical tolerance. These are
**SIMULATED checks**, not empirical study findings.

Two fresh installed-CLI reproduce runs, each with 10,000 bootstraps and 10,000
permutations, produce **27 byte-identical artifacts**. The 95% ranks are
250/9,751 and 90% ranks 500/9,501. The planted P2 permutation p-value is
1/10,001, and equivalence is correctly rejected. The compact verification record
is `docs/study2_phase5_verification.json`, including tested source hashes and
artifact hashes. Its dirty pre-commit provenance is explicitly retained;
no real collection was performed from this development checkout.

Separate fixtures check null, reversed and equivalence-boundary effects, explicit
row-expanded bootstrap refits, independent statsmodels OLS/interaction fits,
explicit tested-label refits with missing outcomes, and unavailable resamples
when a point estimate is identifiable. A mixed-outcome mock collection replays
957 deals, one exclusion, one walk-away impasse, and one final-message impasse,
with two re-asks. It includes negative and above-one shares and negative
concessions. Its concession analysis has 955 eligible episodes, one exclusion,
and four undefined non-excluded episodes, correctly reported per condition.

The full offline suite passed: **547 tests in 121.41 seconds** (520 existing,
27 added for this phase). Confirmed the locked Study 1 main manifest SHA-256
`a583fe4366893e74735f22fc7f1e45ee7e8d136be5e06ad5d770dfcc1225ee55`
by rebuilding it in memory only; both immutable Study 1 tag targets, original
Study 1 artifacts, frozen Study 2 configuration/roster/prompts, real smoke
artifacts, and Phase 1 rendered prompt review remain unchanged. No Study 2 main
manifest or `prereg-study2` tag exists. `codex_prompts/` remains ignored/untracked.
All fifteen output rows, complete/incomplete-stratum counts (320 pooled, 80
per buyer in the balanced fixture), and per-condition eligibility counts were
checked. All four figures were visually inspected. Tested code hashes match
the final source snapshot; no analysis code changed after verification.

## Files and inspection

- `src/kinloyalty/analysis/study2/{loading,outcomes,inference,core,reports,figures,pipeline,simulate}.py`
- `src/kinloyalty/negotiation/{cli,collection}.py`
- `tests/test_study2_{analysis,inference}.py`
- `docs/study2_analysis.md`, `docs/study2_phase5_verification.json`, this report,
  `docs/decisions.md`, `docs/data_dictionary.md`, and the README.
- `preregistration/study2.md`: researcher-approved clarifications only, unlocked
  and incomplete pending the later pilot/fixes/lock phase.

See `docs/study2_analysis.md` for commands, all outcome definitions, methods,
column meanings, missingness conventions, and result paths. For an independent
check, choose fresh temporary paths:

```sh
.venv/bin/kinloyalty study2 simulate --output /private/tmp/study2-check
.venv/bin/kinloyalty study2 reproduce \
  --manifest /private/tmp/study2-check/manifest.jsonl \
  --directory /private/tmp/study2-check/collection \
  --output /private/tmp/study2-check-results --allow-synthetic
.venv/bin/python -m pytest -q
```

`simulate --edge-cases` creates a separate mixed-outcome fixture; it deliberately
no longer has an exactly −0.20 primary contrast. Raw fixtures/large result arrays
are kept outside the repository. The small committed verification record and
commands make the checks reviewable without adding simulated raw data to real
study directories.

## Limits and next gate

No real smoke/pilot or Study 1 main data was analysed. No paid call, actual
Study 2 main scenario draw, main manifest, registration lock/tag, or Phase 5 push
was performed. Study 1 immutable artifacts/tags and `codex_prompts/` remain
protected. No unresolved design question remains after the researcher answers.

Phase 6 requires separate approval: 80 pilot episodes (five per ordered pair),
using independent pilot seeds and approximately balanced disclosure assignment.
There are at most 960 ordinary valid-turn calls. Including one invalid re-ask
per turn and up to four API attempts per response opportunity gives a theoretical
maximum **7,680 attempts**, to be enforced across resumptions if that ceiling
is approved. Before any paid call, prepare the pilot-only authorization and
blind mechanical report, validate them offline, and execute from clean committed
code. Pilot outcome summaries pool disclosure conditions within each pair;
no disclosure-effect analysis or hypothesis test is allowed. Report acceptance-
price mismatches per actual responding model, without a frequency-based automatic
fix. Stop for the researcher to approve any mechanical fix before changing it.
