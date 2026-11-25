# Phase 6 — pilot and comprehension report

**Execution complete; floor/variation flags require review.** All 240 pilot
and 320 comprehension draws produced valid responses. The pilot reveals an
all-zero dictator floor for GPT-6.1 Terra and Gemini 4 Hydrogen, and constant
Gemini proposer offers. All four models passed the comprehension check.

## Authorization, execution, and provenance

The researcher directed a push followed by Phase 6. Pushed the four completed
analysis/specification commits through `3f3e115` before starting this phase.
A local preparation commit, `9f77c99a92d5869a2fa4326b1550b711698da007`, froze the
real manifests and the tested coordinator before making calls. Every live
attempt records that commit and `code_dirty: false`.

The two batches ran concurrently on **2026-11-25, 23:13:47–23:32:18 IST
(Asia/Calcutta)**, one invocation each, with separate manifests/logs and shared
limits of four calls globally and one per model. Timestamps confirm actual
maxima of four globally and one per model. Prompts, schemas, model IDs, API
settings, allocations, and the previously fixed analysis plan were unchanged.

| Batch | Planned draws | Valid | HTTP attempts | API errors | Invalid replies / re-asks | Excluded / unfinished |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| Pilot | 240 | 240 | 242 | 2 | 0 / 0 | 0 / 0 |
| Comprehension | 320 | 320 | 320 | 0 | 0 / 0 | 0 / 0 |
| Total | 560 | 560 | 562 | 2 | 0 / 0 | 0 / 0 |

The authorized maximum was 4,480 HTTP attempts. One OpenAI HTTP 500 and one
Kimi HTTP 429 recovered on their next API attempt, using the frozen retry
policy. Neither consumed an invalid-reply re-ask or became an exclusion. No
extra invocation, account top-up, or other live batch was performed.

## Pilot mechanical checks

- **Response validity:** 100% for each model (60/60 model responses), above the
  required 95%. The two API errors are counted separately, not as invalid replies.
- **Comprehension:** All four models passed; details below.
- **Dictator floor:** Fails for GPT-6.1 Terra and Gemini 4 Hydrogen: all 20
  dictator transfers per model were $0. Kimi is not entirely at the floor, but
  19/20 of its dictator transfers were $0.
- **Variation:** Fails in those two dictator cells and in Gemini's proposer
  cell, where all 20 offers were $40. The other nine model × decision cells
  have at least two distinct values; detailed modal shares are in the CSV.
- **Output cap:** No response was truncated or stopped at the cap.
- **Reasoning counts:** Present for all 560 model responses; Anthropic reported
  zero for every response. Only Kimi returned default reasoning text (140/140),
  retained without enabling extra visibility. API-error attempts have no response
  or usage and retain nulls.
- **OpenAI/Anthropic caches:** All 280 responses explicitly report zero cache
  reads and writes.
- **Kimi caches:** Cache writes are present in all 140 responses (0 or 256).
  Reads are reported as 256 in 73 responses and missing/null in 67. Missing
  values were not replaced by zero. Pilot: 25 reads observed / 35 missing;
  comprehension: 48 observed / 32 missing.
- **Google caches:** Read/write counts are missing/null in all 140 responses.
  Provider-counted inputs remain below the documented implicit-cache threshold.
- **Input sizes:** Every response supplied an input count. The largest was
  722 tokens, well below 4,096.

### Decision distributions pooled over all labels

These are mechanical pilot descriptions, not main-analysis estimates. No
between-label outcome comparison, P1/S1 test, regression, bootstrap TOST, or
permutation analysis was computed on pilot decisions. Each frequency entry is
`dollar value: number of draws`; every row pools its five labels and paraphrases.

| Model | Decision | n | Complete pooled frequency distribution | Mean dollars |
| --- | --- | ---: | --- | ---: |
| Claude Sonnet 5.5 | dictator | 20 | $0: 9; $50: 11 | 27.50 |
| Claude Sonnet 5.5 | ultimatum_proposer | 20 | $30: 1; $40: 19 | 39.50 |
| Claude Sonnet 5.5 | ultimatum_responder | 20 | $20: 2; $25: 1; $30: 16; $40: 1 | 29.25 |
| GPT-6.1 Terra | dictator | 20 | $0: 20 | 0.00 |
| GPT-6.1 Terra | ultimatum_proposer | 20 | $1: 2; $20: 2; $40: 14; $50: 2 | 35.10 |
| GPT-6.1 Terra | ultimatum_responder | 20 | $0: 1; $1: 12; $30: 1; $40: 1; $50: 5 | 16.60 |
| Gemini 4 Hydrogen | dictator | 20 | $0: 20 | 0.00 |
| Gemini 4 Hydrogen | ultimatum_proposer | 20 | $40: 20 | 40.00 |
| Gemini 4 Hydrogen | ultimatum_responder | 20 | $1: 14; $20: 1; $25: 2; $30: 3 | 8.70 |
| Kimi K3.1 Pro | dictator | 20 | $0: 19; $50: 1 | 2.50 |
| Kimi K3.1 Pro | ultimatum_proposer | 20 | $1: 1; $20: 1; $40: 6; $45: 1; $50: 11 | 42.80 |
| Kimi K3.1 Pro | ultimatum_responder | 20 | $0: 4; $1: 9; $40: 1; $50: 6 | 17.45 |

Sample SD, median, zero/equal-split shares, modal share, and number of distinct
values are in [the pooled descriptives](../results/study1/pilot-report/pooled_descriptives.csv).
The [pooled draw export](../results/study1/pilot-report/pooled_decisions.csv)
contains no condition labels or audit identifiers.

## Separate comprehension check

Pass requires at least 18/20 correct in each of own-model, other-lab, and fictional
cards. Undisclosed is reported but unscored. No draw was excluded or unfinished.
Failed models would remain in the study; none failed this run.

| Model | Own-model | Other-lab | Fictional | Undisclosed (unscored) | Model result |
| --- | --- | --- | --- | --- | --- |
| Claude Sonnet 5.5 | 20/20 yes | 20/20 no | 20/20 no | 20/20 unsure | Pass |
| GPT-6.1 Terra | 20/20 yes | 20/20 no | 20/20 no | 20/20 unsure | Pass |
| Gemini 4 Hydrogen | 20/20 yes | 20/20 no | 20/20 no | 20/20 unsure | Pass |
| Kimi K3.1 Pro | 20/20 yes | 20/20 no | 20/20 no | 20/20 unsure | Pass |

See [the complete scored table](../results/study1/comprehension-report/comprehension.csv)
for planned denominators, counts, answer shares, completeness, and pass flags.
This separate check does not enter the main decision analysis.

## Observed version and usage metadata

Each returned version string was exactly the requested API model ID; no more
specific dated build identifier was returned. Counts below combine pilot and
comprehension responses and do not compare decision outcomes by label.

| Model | Returned version (response count) | Input-token range | Cache reads reported | Cache writes reported |
| --- | --- | --- | ---: | ---: |
| Claude Sonnet 5.5 | `claude-sonnet-5-5` (140) | 487–722 | 140/140 | 140/140 |
| GPT-6.1 Terra | `gpt-6.1-terra` (140) | 199–318 | 140/140 | 140/140 |
| Gemini 4 Hydrogen | `gemini-4-hydrogen` (140) | 414–648 | 0/140 | 0/140 |
| Kimi K3.1 Pro | `kimi-k3.1-pro` (140) | 358–496 | 73/140 | 140/140 |

Usage counts retain provider definitions: Google output excludes thoughts;
other output totals include reasoning. Missing cache fields remain distinguishable
from observed zeros. All raw JSON bodies, default reasoning, stop reasons,
provider usage, frozen requests, versions, latency, attempt identities, and SDK
versions are preserved in the append-only logs. SDKs were Anthropic 2.14.0,
OpenAI 3.59.0, and Google Gen AI 3.6.1; package version 0.1.0.

## Artifacts and offline review

- `data/study1/pilot/manifest.jsonl`, `attempts.jsonl`, `run_summary.json`.
- `data/study1/comprehension/manifest.jsonl`, `attempts.jsonl`, `run_summary.json`.
- `data/study1/phase6_cohort_summary.json`: overall times, scope, and completion.
- `docs/phase6_execution_plan.json`: frozen scope, allocations, policies, hashes.
- `docs/phase6_audit.json`: exact manifest/log hashes, versions, metadata presence,
  observed concurrency, and completeness.
- `results/study1/pilot-report/`: pooled descriptives/draws/attempt diagnostics,
  mechanical checks, per-attempt usage, usage summaries, provenance, artifact hashes.
- `results/study1/comprehension-report/`: card-scored table, per-attempt usage,
  usage summaries, provenance, artifact hashes.

To regenerate the reports into new folders, without keys or paid calls:

```sh
.venv/bin/kinloyalty report pilot --data data/study1/pilot \
  --output /private/tmp/kin-loyalty-pilot-review
.venv/bin/kinloyalty report comprehension --data data/study1/comprehension \
  --output /private/tmp/kin-loyalty-comprehension-review
```

Use new output paths; existing outputs are preserved. Input report hashes and
state reconstruction passed. Audits confirm both frozen plans, one run ID per
batch, all final states, the retry/response distinction, shared concurrency,
usage presence, unchanged prompts/settings/analysis, and no supplied keys in
new artifacts. `.env` stays ignored with permissions 0600, and `codex_prompts/`
stays ignored/untracked. All 312 offline tests and both package builds passed
for the coordinator used here. No main study data or manifest exists.
Both report commands were independently rerun into new temporary folders and
reproduced byte-identical CSV/provenance/artifact hashes. Final source/package
builds passed. The completion logs and reports are committed locally; they have
not been pushed.

## Review gate

Phase 6 is complete with the above flags. No prompt, schema, API setting, model,
allocation, or analysis convention was changed after viewing the pilot. No
hypothesis-directed outcome comparison was made. The floor/variation findings
are review items; they do not by themselves establish a mechanical defect or
justify altering prompts to induce a label effect.

The next phase is Phase 7 review of these findings. Under the project agreement,
any proposed mechanical fix must be explained and approved before implementation;
if it changes prompts, comprehension must be rerun on the final text. All four
models remain in the roster. No Phase 7 fix, additional live run, registration
lock, or new GitHub push is included in this completed phase.
