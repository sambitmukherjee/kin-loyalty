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
| `main/` | Main-run manifest at lock; 3,600 planned decisions executed only later | Main decisions only |

The main directory will be created when the main manifest is generated. No main
run is authorized as part of this project phase plan. Simulated test data will
be generated under pytest temporary directories and must not be represented as
observed main data.

Retries and re-asks retain the trial ID and add attempt records. An API-error
attempt is never an exclusion. Detailed fields follow the contract in
`docs/data_dictionary.md`.

Original and revised runs use stable trial IDs within separate manifest-bound
log namespaces. Never combine the two rounds into a single batch or treat pilot
observations as main decisions.

Never put keys, request headers, or `.env` files in these research artifacts.
