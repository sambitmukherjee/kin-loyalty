# Study 1 data

There are no experiment logs yet. Each batch will have a deterministic JSONL
manifest before execution and an append-only JSONL attempt log.

| Directory | Intended contents | Outcome-analysis eligibility |
| --- | --- | --- |
| `smoke/` | Four planned settings-check draws, one per model | Never |
| `pilot/` | 240 planned pilot draws, kept separate from comprehension | Never |
| `comprehension/` | 320 planned card-recognition draws | Separate comprehension report only |
| `main/` | Main-run manifest at lock; 3,600 planned decisions executed only later | Main decisions only |

The main directory will be created when the main manifest is generated. No main
run is authorized as part of this project phase plan. Simulated test data will
be generated under pytest temporary directories and must not be represented as
observed main data.

Retries and re-asks retain the trial ID and add attempt records. An API-error
attempt is never an exclusion. Detailed fields will follow the contract in
`docs/data_dictionary.md`.

Never put keys, request headers, or `.env` files in these research artifacts.
