# Study 2 Phase 2: pure rules, validation, and mock episode execution

Date: 2026-11-26 (Asia/Kolkata).

The researcher instructed: "Push the commit. Then proceed with Phase 2."
Pushed the existing three-commit chain through Phase 1 commit
`facd973d5e3aad7d63c568ef790862e38bb3bc63` to `origin/main`. A remote
`git ls-remote` check independently confirmed that exact branch tip. No tag was
pushed or moved. Phase 2 work is a new local commit and is not included in that
earlier push.

## Implementation and files

All implementation additions are under `src/kinloyalty/negotiation/`:

| File | Responsibility |
| --- | --- |
| `state.py` | Episode assignment, frozen state/terminal outcome, and score dataclasses |
| `rules.py` | Pure allowed actions, state transitions/replay checks, exclusion, and scoring |
| `schemas.py` | Fresh per-request schemas for first, middle, and final messages |
| `validate.py` | Strict JSON, field/type/action/offer checks, truncation, and the non-offer-price exception |
| `requests.py` | Stateless prompt/schema/payload construction using existing clients and exact templates |
| `engine.py` | Sequential mock calls, one re-ask, separate retries, attempt snapshots, and in-memory resumes |
| `mock.py` | Rule-based negotiations, scripts/errors, final-turn/walk-away strategies, and planted label effects |

Added `tests/test_study2_rules.py`, `test_study2_validation.py`,
`test_study2_engine.py`, and `test_study2_requests.py`. Extended the data
dictionary and adding-a-game guide with the Study 2 contract. Recorded this
phase in `docs/decisions.md`. No existing Study 1 implementation, test, prompt,
configuration, saved data/result, registration, or tag was changed. No shared
CLI, client, validator, or runner extension was needed; the engine reuses the
existing `RunnerPolicy` and payload builder without editing them.

## Behavior and explicit conventions

The action list is `offer`/`walk_away` on message 1, all three actions on
messages 2–11, and `accept`/`walk_away` on message 12. Every offer needs a
positive whole-dollar price. `accept` always implements the counterparty's
latest offer, regardless of prices mentioned in free text or supplied in the
acceptance's price field. Walking away before message 12 and on message 12 have
distinct impasse outcomes. Two invalid replies stop the episode as excluded.

Schemas have all three required fields and no extra properties. The flat price
schema is nullable integer with minimum 1; action-dependent rules are local
checks, avoiding conditional schemas that providers may not support. Local
validation follows the researcher-approved exception: any supplied finite JSON
price value on `accept` or `walk_away` is retained and ignored, even when it
would not match the submitted price type/bounds. Missing fields, invalid JSON,
duplicate keys, non-finite/overflowed numeric values, wrong message/action
types, forbidden actions, and output-cap truncation remain invalid.

An `accept` with a non-null supplied price unequal to the latest offer is
flagged on both the terminal outcome and its successful attempt record. Equal
numeric values such as 500 and 500.0 do not flag; a nonnumeric supplied value
does. Each attempt identifies the responding model and role, enabling the
approved pooled per-model pilot counts later. No automatic frequency threshold
or corrective prompt was introduced. Raw supplied prices remain in the parsed
reply, public turn, and original response.

The pure scorer records `(b-p)/(b-s)` for deals without clipping, zero for
impasses, and unavailable values for exclusions. It flags accepted deals above
the buyer maximum or below the seller minimum, whoever accepted. Unaccepted
out-of-limit offers create no mandate violation. An unfinished state cannot be
scored. Message counts are the valid committed messages; exclusions additionally
identify the failed message number and role, without inventing a valid turn.

The engine keeps all calls stateless. An invalid response's one re-ask is a
fresh identical request with no corrective text or hidden reasoning history.
API errors never consume response opportunities. The default timeout/retry
policy is unchanged: 120 seconds, four API attempts per response opportunity,
and 1/2/4-second exponential backoffs. Exhaustion/nonretryable API errors leave
the episode unfinished. Explicit resume restarts the API-error budget, keeps
the invalid-reply count, and reuses the exact pending request. Attempt numbers
continue across resumes. Re-asks count unique second-response opportunities;
retries count attempts following API errors/interruption, including resumed
attempts. The per-opportunity `api_retry_index` starts at 1 on resume.

Client inputs, returned attempt snapshots, and observer snapshots are detached
copies so client/observer mutation cannot alter the canonical re-ask. Unexpected
exceptions/cancellation are recorded as safe interrupted attempts for the optional
observer and then propagate; their raw text is not inserted into attempt records.

The mock client uses the mover's own private limit and public offers. Its
positive `label_effect` shifts a same-label buyer's target upward in reference-
price units, planting a lower buyer-surplus effect for analysis tests. This
synthetic mechanism has no claim about real model behavior. Scripted responses
can exercise arbitrary legal negotiations, invalid/truncated replies, and API
errors without changing Study 1's existing mock client.

## Checks and limits

Run from the repository root:

```sh
.venv/bin/python -m pytest
.venv/bin/python -m pytest tests/test_study2_rules.py \
  tests/test_study2_validation.py tests/test_study2_requests.py \
  tests/test_study2_engine.py
```

The new tests cover every reachable action/termination boundary for both openers
at limits 2, 8, and 12; all model pairings; invalid first/second replies;
truncation; supplied-price preservation/mismatch flags; unclipped scoring;
API errors/timeouts; re-ask interruption/resumption; mid-negotiation resume;
tampered pending requests; and planted label effects with the actual seller fixed.

Twenty-four SDK serialization calls (four providers, both roles, messages 1/11/12)
used injected in-memory HTTP transports, fake keys, and the test suite's socket
block. They preserved nullable prices, changing enums, stateless messages, and
the existing Anthropic numeric-bound omission. This verifies SDK serialization,
not live provider acceptance. There were **zero real provider calls** and no
credential reads. Live schema acceptance/version checks remain Phase 4 work.

The final full suite passed **485 tests** in 32.73 seconds: all 347 tests from
Phase 1 and 138 additional Phase 2 checks. The Study 1 manifest rebuilt in memory
and its saved file both retain the registered SHA-256:
`a583fe4366893e74735f22fc7f1e45ee7e8d136be5e06ad5d770dfcc1225ee55`.
The unchanged Phase 1 review still reproduces byte for byte with SHA-256
`efc39ef410303fb9b9275b4a675ef4652638919afd390e0270a35826675aedb9`.
No Study 1 main response log or outcome was inspected or analysed. The configured
Study 2 main scenarios remain undrawn and the main manifest is not generated.

Phase 2 intentionally supplies in-memory records and explicit checkpoint objects.
It does not yet provide durable collection, disk resumption/replay, batch
scheduling, or live execution. The mock-only guard prevents accidentally using
this incomplete collection layer for a paid experiment.

## Next gate

No unresolved protocol questions remain for this phase. With approval, Phase 3
will add balanced manifests, concurrent scheduling with sequential turns,
per-pair append-only logs, pending journals, durable mid-episode resumption,
episode records, replay, and bounded smoke-probe execution using mock calls.
It will also add the proposed backward-compatible `study2` CLI group while
preserving existing Study 1 commands and defaults. That shared CLI extension
requires explicit approval before editing. Commit Phase 2 locally, do not push
it under the earlier Phase 1 push authorization, and stop at this phase gate.
