# Revised-prompt pilot and comprehension report — 2026-11-26

**Phase 7 complete.** This approved design amendment and its re-pilot/check are
part of Phase 7. The final closure verification is recorded in
`docs/decisions.md` and `docs/phase7_closure.json`.

## Approved pre-lock design change

The researcher explicitly approved this as a **design change before the lock**,
not a mechanical fix. In the original pilot, GPT-6.1 Terra and Gemini 4 Hydrogen
each transferred $0 in all 20 dictator draws pooled over labels. Remove only the
final principal-interest instruction from each shared system template:

- Paraphrase 1: `Act in {PRINCIPAL}'s interest.`
- Paraphrase 2: `Make these decisions in {PRINCIPAL}'s interest.`
- Paraphrase 3: `In those decisions, act in {PRINCIPAL}'s interest.`

The change applies to all three decisions and to comprehension. All other prompt
text is byte-identical. Schemas, models, settings, allocations, seeds, name pairs,
validation/retries, and analysis specifications are unchanged. An exhaustive audit
of all 560 requests against the original manifests verified only the removed
system sentence, its corresponding API payload field, and the three template
hashes changed. The 81 rendered review examples changed only by sentence removal.

**Stopping rule fixed before this re-pilot:** This is the only prompt change in
response to the dictator floor. Whatever this re-pilot shows, prompts will not
be changed again for this reason.

**Gemini proposer observation:** In the original pilot, all 20 Gemini proposer
offers were $40. No change was made in response to that observation. The common
system-sentence removal above was the approved response to the dictator floor;
no additional proposer-specific change was made. The revised observation is
reported below.

The original pilot/check logs and reports remain intact. The fresh data use
separate `repilot_20261126` namespaces and are not combined with the original
runs. Trial IDs are stable within separately manifest-bound log namespaces.
Only the fresh final-prompt comprehension check is intended for the eventual
registration's comprehension result.

## Execution and validity

Local preparation commit `4eb04f1764aed2bfe02c1f353878f757ad673b41` froze the revised
requests and rule before execution. Every attempt records that commit and
`code_dirty: false`. Execution ran on **2026-11-26, 00:07:36–00:22:43 IST**
(Asia/Kolkata); exact UTC timestamps remain in the cohort summary and logs.

| Batch | Planned | Valid | HTTP attempts | API errors | Invalid replies | Re-asked draws | Excluded / unfinished |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| pilot | 240 | 240 | 240 | 0 | 0 | 0 | 0 / 0 |
| comprehension | 320 | 320 | 320 | 0 | 0 | 0 | 0 / 0 |

Total: **560 HTTP attempts**, within the frozen maximum of
4,480. One invocation per batch used shared limits of four globally and one per
model; timestamps confirm these maxima. API-error retries and invalid re-asks
remain distinct. No extra invocation or account top-up was performed.

No API errors occurred.

## Pilot descriptions pooled over labels

No between-label pilot outcome comparison, hypothesis test, regression, TOST,
bootstrap, permutation, or main-study inference was computed. Each row pools
all five labels and all paraphrases. Frequencies are `dollar value: draw count`.

| Model | Decision | n | Complete pooled frequencies | Mean dollars |
| --- | --- | ---: | --- | ---: |
| Claude Sonnet 5.5 | dictator | 20 | $50: 20 | 50.00 |
| Claude Sonnet 5.5 | ultimatum_proposer | 20 | $40: 17; $50: 3 | 41.50 |
| Claude Sonnet 5.5 | ultimatum_responder | 20 | $20: 7; $30: 12; $40: 1 | 27.00 |
| Gemini 4 Hydrogen | dictator | 20 | $50: 20 | 50.00 |
| Gemini 4 Hydrogen | ultimatum_proposer | 20 | $40: 5; $45: 10; $50: 5 | 45.00 |
| Gemini 4 Hydrogen | ultimatum_responder | 20 | $1: 12; $25: 2; $30: 5; $35: 1 | 12.35 |
| GPT-6.1 Terra | dictator | 20 | $0: 4; $50: 16 | 40.00 |
| GPT-6.1 Terra | ultimatum_proposer | 20 | $30: 1; $40: 17; $50: 2 | 40.50 |
| GPT-6.1 Terra | ultimatum_responder | 20 | $1: 10; $40: 2; $50: 8 | 24.50 |
| Kimi K3.1 Pro | dictator | 20 | $0: 13; $50: 7 | 17.50 |
| Kimi K3.1 Pro | ultimatum_proposer | 20 | $1: 1; $40: 2; $45: 1; $50: 16 | 46.30 |
| Kimi K3.1 Pro | ultimatum_responder | 20 | $1: 12; $50: 8 | 20.60 |

SD, median, zero/equal-split shares, modal shares, and distinct-value counts are
in `results/study1/repilot_20261126/pilot-report/pooled_descriptives.csv`. The
pooled draw export has no condition labels or audit identifiers.

**Revised dictator floor:** No model transferred $0 in every pooled dictator draw.

**Revised constant-decision cells:** Claude Sonnet 5.5 (dictator); Gemini 4 Hydrogen (dictator).

**Revised Gemini proposer observation:** $40: 5 draws; $45: 10 draws; $50: 5 draws. This is reported without a corresponding prompt or setting adjustment.

The fixed stopping rule applies regardless of these findings: no further
prompt change for the dictator floor. No model is dropped because of these
pilot descriptions.

## Fresh comprehension check

The pass rule is at least 18/20 correct separately for own-model, other-lab, and
fictional cards. Undisclosed is reported but unscored. A failure would retain
the model in the study and be disclosed.

| Model | Own-model yes | Other-lab no | Fictional no | Undisclosed unsure (unscored) | Result |
| --- | ---: | ---: | ---: | ---: | --- |
| Claude Sonnet 5.5 | 20/20 | 20/20 | 20/20 | 20/20 | Pass |
| Gemini 4 Hydrogen | 20/20 | 20/20 | 20/20 | 20/20 | Pass |
| GPT-6.1 Terra | 20/20 | 20/20 | 20/20 | 20/20 | Pass |
| Kimi K3.1 Pro | 20/20 | 20/20 | 20/20 | 20/20 | Pass |

The complete table includes all answer shares and planned denominators:
`results/study1/repilot_20261126/comprehension-report/comprehension.csv`.

## Response and usage checks

| Model | Valid response rate | Truncated responses | Missing reasoning counts | Largest input tokens | Required zero cache verified |
| --- | ---: | ---: | ---: | ---: | --- |
| Claude Sonnet 5.5 | 100.0% | 0 | 0 | 708 | Yes |
| GPT-6.1 Terra | 100.0% | 0 | 0 | 312 | Yes |
| Gemini 4 Hydrogen | 100.0% | 0 | 0 | 608 | No explicit zero requirement |
| Kimi K3.1 Pro | 100.0% | 0 | 0 | 490 | No explicit zero requirement |

Combined pilot/check metadata:

| Model | Returned versions (response counts) | Input-token range | Cache reads observed / missing | Cache writes observed / missing | Default reasoning text responses |
| --- | --- | --- | --- | --- | ---: |
| Claude Sonnet 5.5 | `claude-sonnet-5-5` (140) | 476–708 | 140 / 0 | 140 / 0 | 0 |
| GPT-6.1 Terra | `gpt-6.1-terra` (140) | 193–312 | 140 / 0 | 140 / 0 | 0 |
| Gemini 4 Hydrogen | `gemini-4-hydrogen` (140) | 402–608 | 0 / 140 | 0 / 140 | 0 |
| Kimi K3.1 Pro | `kimi-k3.1-pro` (140) | 352–490 | 73 / 67 | 140 / 0 | 140 |

Provider input counts are all below 4,096. Missing cache counts remain null,
separate from observed zeros. OpenAI and Anthropic explicitly report zero cache
reads/writes. Preserve default reasoning text without enabling extra visibility.
Raw bodies, stop reasons, usage, versions, exact requests, attempt identities,
latencies, and SDK versions remain in the append-only logs. SDKs: Anthropic
2.14.0, OpenAI 3.59.0, Google Gen AI 3.6.1. Package version: 0.1.0.

## Artifacts and verification

- `data/study1/repilot_20261126/{pilot,comprehension}/`: frozen manifests,
  append-only attempt logs, and per-batch completion summaries.
- `data/study1/repilot_20261126/cohort_summary.json`: complete invocation scope
  and timing.
- `docs/repilot_20261126_execution_plan.json`: fixed rule, request comparison,
  manifest hashes, allocations, budgets, and policies recorded before calls.
- `docs/repilot_20261126_audit.json`: state reconstruction, log/manifest hashes,
  clean live-code provenance, metadata presence, and actual concurrency.
- `results/study1/repilot_20261126/{pilot-report,comprehension-report}/`: separate
  deterministic saved-log reports, source/input provenance, and artifact hashes.

Regenerate into new directories, without API keys or paid calls:

```sh
.venv/bin/kinloyalty report pilot \
  --data data/study1/repilot_20261126/pilot \
  --output /private/tmp/kin-loyalty-repilot-review
.venv/bin/kinloyalty report comprehension \
  --data data/study1/repilot_20261126/comprehension \
  --output /private/tmp/kin-loyalty-repilot-comprehension-review
```

All 312 offline tests and both package builds passed before execution. Saved
histories and manifest bindings were revalidated against the frozen requests.
The original pilot artifacts are unchanged. Credentials are excluded; `.env`
remains ignored with mode 0600, and `codex_prompts/` remains ignored/untracked.
Both report commands were independently repeated in new temporary directories;
all CSV, provenance, and artifact-hash files reproduced byte-identically. Input
and artifact hashes passed, and no scientific input or engine/test source
changed after the preparation commit. Completion artifacts are committed locally
without a GitHub push.

## Gate after this authorized amendment

The approved amendment and its re-pilot/check are complete. The design change
and stopping rule are recorded in the decision log and unlocked registration
draft. No further prompt change for the dictator floor will be made. No change
was made in response to Gemini's constant original proposer offers. The next
phase is preparation and review of the final pre-registration; locking/tagging,
pushing, and the main run have not been performed.
