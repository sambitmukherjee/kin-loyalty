# Study 1 data

The approved smoke invocation completed on 2026-11-25: four live requests,
four valid replies, and no retries or re-asks. See `smoke/attempts.jsonl`,
`smoke/run_summary.json`, and `docs/phase4b_report.md`. Every batch has a
deterministic JSONL manifest before execution and an append-only attempt log.

| Directory | Intended contents | Outcome-analysis eligibility |
| --- | --- | --- |
| `smoke/` | Four completed settings-check draws, one per model | Never |
| `pilot/` | 240 planned pilot draws, kept separate from comprehension | Never |
| `comprehension/` | 320 planned card-recognition draws | Separate comprehension report only |
| `main/` | Main-run manifest at lock; 3,600 planned decisions executed only later | Main decisions only |

The main directory will be created when the main manifest is generated. No main
run is authorized as part of this project phase plan. Simulated test data will
be generated under pytest temporary directories and must not be represented as
observed main data.

Retries and re-asks retain the trial ID and add attempt records. An API-error
attempt is never an exclusion. Detailed fields follow the contract in
`docs/data_dictionary.md`.

Never put keys, request headers, or `.env` files in these research artifacts.
