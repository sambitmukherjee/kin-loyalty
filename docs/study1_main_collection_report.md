# Study 1 main collection — mechanics only

**All 3,600 planned draws completed valid.** Collection ran on
**2026-11-26, 01:04:14–03:27:04 IST** (Asia/Kolkata),
including the registered resumption described below. There were **3,613 API
attempts**, **13 API errors**, **0 invalid replies**, **0 invalid re-asks**,
**0 exclusions**, and **0 unfinished draws**. Each of the 60 model × decision ×
label cells completed all 60 planned draws.

This report contains collection/validation counts only. No outcome analysis,
label-effect comparison, amount/belief summary, regression, resampling, or figure
was produced. Study 1 analysis remains deferred until the Study 2 addendum is
committed, as the researcher instructed.

## Tagged checkout and manifest verification

The researcher explicitly authorized main collection from `prereg-study1`, with
a clean working tree, a manifest-hash check before starting, and mechanical
reporting afterward. The checkout was detached at the tag during every live
invocation. The exact tagged commit is:

```text
d4d6ff9c1f7b84bc2b4f90578873f18dbc9fb98a
```

Before the first API call, the manifest's actual SHA-256 matched both the value
written in `preregistration/study1.md` and the registration inventory:

```text
a583fe4366893e74735f22fc7f1e45ee7e8d136be5e06ad5d770dfcc1225ee55
```

All 63 registration document/source/artifact digests were also verified before
collection and again after all calls. Prompts, schemas, models, settings, source
code, seeds, assignments, and main manifest are unchanged. Live logs were written
outside the checkout so its working tree stayed clean; no new project file was
created until collection and the external mechanical audit finished. The checkout
returned to main afterward solely to preserve raw data and collection records.
The registration tag has not moved.

**Every one of the 3,613 main log records** has
`git_commit = d4d6ff9c1f7b84bc2b4f90578873f18dbc9fb98a` and `code_dirty = false`,
including API-error attempts and the registered resumption. Every saved request,
trial/manifest hash, attempt counter, response opportunity, validation result,
and final/excluded state was checked against the frozen manifest using the
registered state validator. Observed concurrency was at most four globally and
one per model, matching the frozen policy.

## Retries and registered resumption

The initial invocation completed 3,599 draws in 3,612 attempts. One Kimi
`dictator / fictional / paraphrase 1 / draw 4` trial remained unfinished after
four retryable HTTP 429 failures. That API-error exhaustion was not an exclusion
and did not consume an invalid-reply re-ask.

After checking the failure metadata, explicitly resumed only that existing
trial using the registered resumption mechanism, from the same clean detached
tag and unchanged manifest. All 3,599 final draws were skipped. The resumed
trial succeeded on its next call; no new design draw was added and no completed
draw was repeated. The resumption was bounded at eight additional attempts and
used exactly one. Overall attempts remain within the original 28,800 bound.
Both original invocation/preflight records and the resumption records are
preserved separately; no attempt log was rewritten.

The 13 categorized errors comprise one Gemini timeout, eleven Kimi HTTP 429s,
and one Anthropic connection error. All eventually recovered under the registered
retry/resumption rules. API errors are reported separately from invalid replies.

## Per-model totals

| Model | Completed valid draws | API attempts | API errors | Invalid replies | Re-asks | Exclusions | Unfinished |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Claude Sonnet 5.5 | 900 | 901 | 1 | 0 | 0 | 0 | 0 |
| GPT-6.1 Terra | 900 | 900 | 0 | 0 | 0 | 0 | 0 |
| Gemini 4 Hydrogen | 900 | 901 | 1 | 0 | 0 | 0 | 0 |
| Kimi K3.1 Pro | 900 | 911 | 11 | 0 | 0 | 0 | 0 |

## Complete model × decision × label counts

Every row has 60 planned draws. "Completed" means terminal draws; all are valid
here because exclusions are zero. "API attempts" includes successful responses,
API-error attempts/retries, and the explicit resumption. "Re-asks" counts draws
for which a second identical response opportunity was attempted after an invalid
reply; retrying an API error is not an invalid re-ask. "Unfinished" includes any
planned draw without a terminal record, including not-started draws (zero here).
The machine-readable table is `data/study1/main/collection_counts.csv`, with
additional response/retry/not-started fields and definitions in the audit JSON.

### Claude Sonnet 5.5

| Decision | Label | Completed | API attempts | Invalid replies | Re-asks | Exclusions | Unfinished |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| dictator | own_model | 60 | 60 | 0 | 0 | 0 | 0 |
| dictator | other_lab | 60 | 60 | 0 | 0 | 0 | 0 |
| dictator | fictional | 60 | 60 | 0 | 0 | 0 | 0 |
| dictator | not_disclosed | 60 | 61 | 0 | 0 | 0 | 0 |
| dictator | human | 60 | 60 | 0 | 0 | 0 | 0 |
| ultimatum_proposer | own_model | 60 | 60 | 0 | 0 | 0 | 0 |
| ultimatum_proposer | other_lab | 60 | 60 | 0 | 0 | 0 | 0 |
| ultimatum_proposer | fictional | 60 | 60 | 0 | 0 | 0 | 0 |
| ultimatum_proposer | not_disclosed | 60 | 60 | 0 | 0 | 0 | 0 |
| ultimatum_proposer | human | 60 | 60 | 0 | 0 | 0 | 0 |
| ultimatum_responder | own_model | 60 | 60 | 0 | 0 | 0 | 0 |
| ultimatum_responder | other_lab | 60 | 60 | 0 | 0 | 0 | 0 |
| ultimatum_responder | fictional | 60 | 60 | 0 | 0 | 0 | 0 |
| ultimatum_responder | not_disclosed | 60 | 60 | 0 | 0 | 0 | 0 |
| ultimatum_responder | human | 60 | 60 | 0 | 0 | 0 | 0 |

### GPT-6.1 Terra

| Decision | Label | Completed | API attempts | Invalid replies | Re-asks | Exclusions | Unfinished |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| dictator | own_model | 60 | 60 | 0 | 0 | 0 | 0 |
| dictator | other_lab | 60 | 60 | 0 | 0 | 0 | 0 |
| dictator | fictional | 60 | 60 | 0 | 0 | 0 | 0 |
| dictator | not_disclosed | 60 | 60 | 0 | 0 | 0 | 0 |
| dictator | human | 60 | 60 | 0 | 0 | 0 | 0 |
| ultimatum_proposer | own_model | 60 | 60 | 0 | 0 | 0 | 0 |
| ultimatum_proposer | other_lab | 60 | 60 | 0 | 0 | 0 | 0 |
| ultimatum_proposer | fictional | 60 | 60 | 0 | 0 | 0 | 0 |
| ultimatum_proposer | not_disclosed | 60 | 60 | 0 | 0 | 0 | 0 |
| ultimatum_proposer | human | 60 | 60 | 0 | 0 | 0 | 0 |
| ultimatum_responder | own_model | 60 | 60 | 0 | 0 | 0 | 0 |
| ultimatum_responder | other_lab | 60 | 60 | 0 | 0 | 0 | 0 |
| ultimatum_responder | fictional | 60 | 60 | 0 | 0 | 0 | 0 |
| ultimatum_responder | not_disclosed | 60 | 60 | 0 | 0 | 0 | 0 |
| ultimatum_responder | human | 60 | 60 | 0 | 0 | 0 | 0 |

### Gemini 4 Hydrogen

| Decision | Label | Completed | API attempts | Invalid replies | Re-asks | Exclusions | Unfinished |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| dictator | own_model | 60 | 60 | 0 | 0 | 0 | 0 |
| dictator | other_lab | 60 | 60 | 0 | 0 | 0 | 0 |
| dictator | fictional | 60 | 60 | 0 | 0 | 0 | 0 |
| dictator | not_disclosed | 60 | 60 | 0 | 0 | 0 | 0 |
| dictator | human | 60 | 60 | 0 | 0 | 0 | 0 |
| ultimatum_proposer | own_model | 60 | 60 | 0 | 0 | 0 | 0 |
| ultimatum_proposer | other_lab | 60 | 60 | 0 | 0 | 0 | 0 |
| ultimatum_proposer | fictional | 60 | 60 | 0 | 0 | 0 | 0 |
| ultimatum_proposer | not_disclosed | 60 | 60 | 0 | 0 | 0 | 0 |
| ultimatum_proposer | human | 60 | 60 | 0 | 0 | 0 | 0 |
| ultimatum_responder | own_model | 60 | 61 | 0 | 0 | 0 | 0 |
| ultimatum_responder | other_lab | 60 | 60 | 0 | 0 | 0 | 0 |
| ultimatum_responder | fictional | 60 | 60 | 0 | 0 | 0 | 0 |
| ultimatum_responder | not_disclosed | 60 | 60 | 0 | 0 | 0 | 0 |
| ultimatum_responder | human | 60 | 60 | 0 | 0 | 0 | 0 |

### Kimi K3.1 Pro

| Decision | Label | Completed | API attempts | Invalid replies | Re-asks | Exclusions | Unfinished |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| dictator | own_model | 60 | 62 | 0 | 0 | 0 | 0 |
| dictator | other_lab | 60 | 60 | 0 | 0 | 0 | 0 |
| dictator | fictional | 60 | 64 | 0 | 0 | 0 | 0 |
| dictator | not_disclosed | 60 | 60 | 0 | 0 | 0 | 0 |
| dictator | human | 60 | 60 | 0 | 0 | 0 | 0 |
| ultimatum_proposer | own_model | 60 | 60 | 0 | 0 | 0 | 0 |
| ultimatum_proposer | other_lab | 60 | 60 | 0 | 0 | 0 | 0 |
| ultimatum_proposer | fictional | 60 | 64 | 0 | 0 | 0 | 0 |
| ultimatum_proposer | not_disclosed | 60 | 60 | 0 | 0 | 0 | 0 |
| ultimatum_proposer | human | 60 | 61 | 0 | 0 | 0 | 0 |
| ultimatum_responder | own_model | 60 | 60 | 0 | 0 | 0 | 0 |
| ultimatum_responder | other_lab | 60 | 60 | 0 | 0 | 0 | 0 |
| ultimatum_responder | fictional | 60 | 60 | 0 | 0 | 0 | 0 |
| ultimatum_responder | not_disclosed | 60 | 60 | 0 | 0 | 0 | 0 |
| ultimatum_responder | human | 60 | 60 | 0 | 0 | 0 | 0 |

## Preserved artifacts and integrity

- `data/study1/main/manifest.jsonl`: original tagged 3,600-draw plan, unchanged.
- `attempts.jsonl`: all 3,613 append-only main attempt records, copied byte-for-byte
  from the completed external log after collection.
- `preflight.json`, `invocation_summary.json`: initial clean-tag/hash verification
  and invocation completion, including the one initially unfinished trial.
- `resume_01_preflight.json`, `resume_01_summary.json`: explicit registered
  resumption scope, budget, clean-tag check, and successful completion.
- `run_summary.json`: aggregate collection completion/timing and totals.
- `collection_counts.csv`: all 60 model × decision × label mechanical counts.
- `collection_audit.json`: record/manifest binding, provenance, concurrency,
  counts/definitions, source integrity, invocation identities, and data hashes.

Attempt-log SHA-256:

```text
2cb8b042908437b2e382dd6021a3df43218e1f276f04e1eed6a1e037abd3d9ac
```

The imported artifacts match their external originals byte-for-byte. Exact
credential scans passed; `.env` remains ignored with permissions 0600 and
`codex_prompts/` remains ignored/untracked. No analysis module was imported by
the mechanical audit. The raw log contains the collected responses for later
reproduction; this report and its counts CSV contain no amount, belief, reason,
or model-behavior summary. All registration digests remain valid, and the
immutable `prereg-study1` tag still resolves to the execution commit above.

Raw data and mechanics are preserved in a separate local collection commit,
keeping the registration tag intact. No new GitHub push is included in this collection
instruction. Analysis waits for the committed Study 2 addendum.
