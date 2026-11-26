# Study 2 Phase 1: configuration, scenarios, and prompt review

Date: 2026-11-26 (Asia/Kolkata).

The researcher explicitly approved Phase 1 after resolving the Phase 0 questions.
This phase adds offline configuration, scenario generation, exact prompt
rendering, and the requested complete review examples. It makes no real calls
and does not start Phase 2.

## Files and implementation

- `configs/study2.yaml`: the unchanged four-model roster by reference, all
  ordered pairs, conditions, items/prices, private-limit distributions, opener
  balance, seeds, message limit, buyer-only cards, retry settings, pilot/analysis
  separation, acceptance-price diagnostic, and approved smoke-probe budget.
- `prompts/study2/`: complete role system templates, card/introductions, turn
  instructions, opening/late-turn notices, and fixed hand-written review/probe
  transcripts. `README.md` explains composition and reproduction.
- `src/kinloyalty/negotiation/config.py`, `scenarios.py`, and `cards.py`: configuration
  checks, explicit-seed scenario draws, pair identities, balanced alternative
  names, and deterministic disclosure assignments.
- `src/kinloyalty/negotiation/prompts.py`, `transcript.py`, and `review.py`: exact
  stateless system/user rendering, one-line JSON-escaped transcripts, privacy
  boundaries, fixed-position fixtures, and review generation. The package
  `__init__.py` defines the common buyer/seller role type.
- `docs/study2_prompt_review.md`: **48 complete requests**, one self-pair
  (Claude/Claude) and one cross-pair (GPT/Kimi), under all three conditions,
  for both roles at messages 1, 2, 11, and 12. Each request uses the appropriate
  opener and transcript prefix. Source SHA-256 values appear at the top.
- `tests/test_study2_configuration.py`, `test_study2_scenarios.py`, and
  `test_study2_prompts.py`: offline design, assignment, exact-text, privacy,
  escaping, configurability, and reproduction checks.
- `docs/decisions.md` and `docs/study2_phase0_plan.md`: record Phase 1 authorization,
  implementation choices, completion, and the next gate.

All new implementation is isolated under `kinloyalty.negotiation`. Existing
Study 1 source, tests, settings, prompts, saved data/results, registration, and
tags are unchanged in this phase. No shared client, validator, runner, manifest,
or CLI extension was needed. The low-level system renderer accepts an optional
card for either role; the Study 2 wrapper enforces buyer-only disclosure.

## Explicit implementation conventions for review

These implement the approved Phase 1 plan. They are recorded for review before
the final addendum; no main manifest or main scenario has been generated.

Limits use independent `random.Random.uniform` draws. Each decimal-string draw
is multiplied by its item's reference price using `Decimal`, then rounded to
the nearest $5 with `ROUND_HALF_UP`: an exact $402.50 becomes $405. Random streams
are derived by SHA-256 of compact JSON `[seed, pair_id, purpose]`; the digest
seeds Python's `random.Random`. Scenario IDs/order are canonical by item, opener,
and replicate. The manifest phase will separately shuffle episode execution.
Pair streams do not depend on which pair was generated first.

The default opener counts are two buyer-opened and two seller-opened scenarios
per item. Counts are separate configuration values so other experiments can
change the opener balance. For Study 2 this yields 20 scenarios/pair and 10
buyer-opened scenarios in every pair/condition. Scenario facts are independent
of disclosure; callers reuse the same scenario across all three conditions.

On swapped self-pair cards, the next model in the cyclic roster receives the
six-count allocation; the remaining alternatives receive seven each:

| Self-pair | Alternative with six names | Other alternatives |
| --- | --- | --- |
| Claude/Claude | GPT-6.1 Terra | Gemini, Kimi: seven each |
| GPT/GPT | Gemini 4 Hydrogen | Kimi, Claude: seven each |
| Gemini/Gemini | Kimi K3.1 Pro | Claude, GPT: seven each |
| Kimi/Kimi | Claude Sonnet 5.5 | GPT, Gemini: seven each |

Assignments are shuffled with a separate named random stream. Rendering a
swapped self-pair requires the caller to supply that scheduled alternative;
the renderer never silently selects one.

| Seed purpose | Value |
| --- | --- |
| Smoke scenarios / order | 2026112601 / 2026112602 |
| Pilot scenarios / order | 2026112603 / 2026112604 |
| Main scenarios / order | 2026112605 / 2026112606 |
| Bootstrap / permutation | 2026112607 / 2026112608 |
| Mock / swapped names | 2026112609 / 2026112610 |

These are local design/order/inference controls, never API sampling settings.
Tests use explicit synthetic seeds, and review/probe positions use hand-written
facts (camera, P=$500, s=$400, b=$600). The configured main seed has not been used.

The approved non-offer-price exception and acceptance-price mismatch flag are
recorded in configuration. Actual validation, scoring, flagging, logging, and
pilot reporting belong to the later engine/logging/report phases. Likewise,
this phase prepares fixed smoke transcripts and budget metadata, not a live
probe runner. No implementation is claimed for those later-phase components.

## Verification and review commands

From the repository root:

```sh
.venv/bin/python -m pytest
.venv/bin/python -m pytest tests/test_study2_configuration.py \
  tests/test_study2_scenarios.py tests/test_study2_prompts.py
.venv/bin/python -m kinloyalty.negotiation.review \
  --config configs/study2.yaml --output /tmp/kinloyalty-study2-review.md
diff -u docs/study2_prompt_review.md /tmp/kinloyalty-study2-review.md
```

Choose a fresh output path; generation refuses to overwrite existing files.
Review the full buyer/seller text, all card model lines, and the message-11/12
notices in `docs/study2_prompt_review.md`. Its private-limit metadata is only for
the researcher and is not included in either agent's request.

The tests cover all 16 pairings and disclosure conditions at each requested
position, with seller requests invariant across conditions. A full synthetic
design check yields 320 distinct scenarios and 960 condition assignments,
including 320 each of card-says-none/same/other. Main execution manifests and
API calls are not involved. Transcript checks include quotes, newlines, carriage
returns, tabs, backslashes, Unicode line separators, and literal placeholder
text. Configuration/review checks include an external config file, a custom
message limit, different items/price ranges, and unequal opener counts.

The final full suite passed **347 tests** in 32.83 seconds, including all 312
existing tests and 35 new Study 2 checks. Independent CLI generation in a fresh
temporary directory reproduced the review byte for byte. Review SHA-256:
`efc39ef410303fb9b9275b4a675ef4652638919afd390e0270a35826675aedb9`.

The Study 1 main manifest was rebuilt in memory and compared with the saved
manifest and registered digest. All three match:
`a583fe4366893e74735f22fc7f1e45ee7e8d136be5e06ad5d770dfcc1225ee55`.
Existing Study 1 source/research paths and both tags remain unchanged from the
start of Phase 1. No Study 1 main-run outcomes or response logs were read or
analysed. No dependency was installed or updated. `codex_prompts/` remains ignored
and untracked.

## Remaining gate

There are no new unresolved design questions. The conventions above and exact
prompts are ready for researcher review. With explicit approval, Phase 2 will
add the pure state/rules, per-turn JSON schemas, validation and scoring, the
negotiation mock client, and episode engine tests, including the approved
acceptance-price mismatch behavior. Phase 2 uses mock calls only. Commit Phase 1
locally, do not push, and stop for permission before beginning that work.
