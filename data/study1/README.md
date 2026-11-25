# Study 1 data

The approved smoke invocation completed on 2026-11-25: four live requests,
four valid replies, and no retries or re-asks. See `smoke/attempts.jsonl`,
`smoke/run_summary.json`, and `docs/phase4b_report.md`. Every batch has a
deterministic JSONL manifest before execution and an append-only attempt log.

Phase 6 completed 240 pilot and 320 comprehension draws in separate concurrent
batches on 2026-11-25. All were valid; 562 attempts include two recovered API
errors. Each batch has `manifest.jsonl`, `attempts.jsonl`, and `run_summary.json`.
The overall completion is in `phase6_cohort_summary.json`; see
`docs/phase6_report.md` for the floor/variation review flags and metadata caveats.

The approved pre-lock design amendment removed only the final principal-interest
system sentence in each paraphrase. Its fresh pilot and comprehension check
completed on 2026-11-26 in `repilot_20261126/`: 240 and 320 valid draws, exactly
560 attempts, no errors or re-asks. The original data above remain unchanged.
Use `repilot_20261126/comprehension/` as the final-prompt comprehension check for
the eventual registration/paper. See `docs/repilot_20261126_report.md` and the
fixed no-further-floor-prompt-change rule in `docs/decisions.md`.

| Directory | Intended contents | Outcome-analysis eligibility |
| --- | --- | --- |
| `smoke/` | Four completed settings-check draws, one per model | Never |
| `pilot/` | 240 completed pilot draws, kept separate from comprehension | Never |
| `comprehension/` | 320 completed card-recognition draws | Separate comprehension report only |
| `repilot_20261126/pilot/` | 240 revised-prompt pilot draws | Never |
| `repilot_20261126/comprehension/` | 320 fresh final-prompt card-recognition draws | Final comprehension report only |
| `main/` | Frozen manifest, 3,600 valid collected draws, raw attempts, and mechanical counts/audit | Analysis deferred until Study 2 addendum is committed |

Phase 8 generated `main/manifest.jsonl`: 3,600 planned draws, order seed
2026112504, SHA-256
`a583fe4366893e74735f22fc7f1e45ee7e8d136be5e06ad5d770dfcc1225ee55`.
It regenerates byte-identically and contains the final two-sentence system
prompts, schemas, settings, and other-lab rotations. The researcher subsequently
authorized main collection from the clean `prereg-study1` checkout. All 3,600
draws completed valid in 3,613 API attempts: 13 API errors, no invalid replies,
re-asks, exclusions, or unfinished draws. One existing retry-exhausted Kimi draw
was completed through the registered resumption mechanism; no design draw was
added or replaced.

`main/attempts.jsonl` retains all raw attempts. `main/collection_counts.csv`
reports every model × decision × label cell (60 completed valid draws each),
and `main/collection_audit.json` verifies all 3,613 records carry commit
`d4d6ff9c1f7b84bc2b4f90578873f18dbc9fb98a` and clean-code provenance.
Both invocations/preflights are retained, with aggregate `main/run_summary.json`.
The registration inventory remains an immutable snapshot of the pre-collection
state. No outcome analysis or amount/belief summary was computed; analysis waits
until the Study 2 addendum is committed. Simulated verification data remain
outside these real study directories.

Retries and re-asks retain the trial ID and add attempt records. An API-error
attempt is never an exclusion. Detailed fields follow the contract in
`docs/data_dictionary.md`.

Original and revised runs use stable trial IDs within separate manifest-bound
log namespaces. Never combine the two rounds into a single batch or treat pilot
observations as main decisions.

Never put keys, request headers, or `.env` files in these research artifacts.
