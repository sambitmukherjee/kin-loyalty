# Study 1 recorded data

The main collection and pre-registered analysis are complete. The `study1-data`
tag freezes 3,600 valid main decisions at commit
`f7dd0a690a5089b245fff365acf002fcfd7b056a`. To reproduce the paper, use
[main/](main/) together with the separate final-prompt comprehension batch in
[repilot_20261126/comprehension/](repilot_20261126/comprehension/).

Follow the [reproduction guide](../../docs/reproducing_the_paper.md) for setup,
frozen checkouts and commands. The [results index](../../results/study1/README.md)
identifies the saved tables and figures. For your own experiment, use the
[worked guide](../../docs/running_a_new_experiment.md) and separate inputs and
output directories.

## Main collection files

Each JSONL file contains one JSON record per line. The manifest is the plan
saved before collection; the attempt log records every call, including API
errors. A decision can therefore have more than one attempt.

| File | Contents |
| --- | --- |
| [main/manifest.jsonl](main/manifest.jsonl) | The 3,600 planned decisions, exact requests, response schemas, settings and source hashes. |
| [main/attempts.jsonl](main/attempts.jsonl) | All 3,613 API attempts, including 13 errors and the subsequent valid replies. |
| [main/collection_counts.csv](main/collection_counts.csv) | Completion counts for each model × decision × label cell; each has 60 valid decisions. |
| [main/collection_audit.json](main/collection_audit.json) | Checks of all attempt records, including the registration commit and clean-code provenance. |
| [main/run_summary.json](main/run_summary.json) | Aggregate collection mechanics across the initial invocation and one registered resumption. |
| [main/preflight.json](main/preflight.json) and [main/resume_01_preflight.json](main/resume_01_preflight.json) | The checks recorded before those two invocations. |

The main run had no invalid replies, re-asks, exclusions or unfinished decisions.
One retry-exhausted decision was completed through resumption; no planned
decision was added or replaced. The [collection report](../../docs/study1_main_collection_report.md)
provides the full account.

The manifest SHA-256 is
`a583fe4366893e74735f22fc7f1e45ee7e8d136be5e06ad5d770dfcc1225ee55`.
It contains the final two-sentence system prompts and the registered other-lab
allocation. Main attempts record the `prereg-study1` execution commit,
`d4d6ff9c1f7b84bc2b4f90578873f18dbc9fb98a`. The later `study1-data` commit
identifies the frozen collection snapshot. The
[registration index](../../preregistration/README.md) explains both tags and
links the protocol and hash inventory.

## Separate development and comprehension batches

| Directory | Contents and role |
| --- | --- |
| [smoke/](smoke/) | Four completed provider-settings checks, one per model. They do not enter main inference. |
| [pilot/](pilot/) | The original 240-decision pilot, using the earlier prompts. These observations do not enter main inference. |
| [comprehension/](comprehension/) | The original 320 card-recognition checks. These used the earlier prompts and are not the paper's final comprehension input. |
| [repilot_20261126/pilot/](repilot_20261126/pilot/) | A fresh 240-decision pilot after the approved pre-registration prompt amendment. It does not enter main inference. |
| [repilot_20261126/comprehension/](repilot_20261126/comprehension/) | The 320 final-prompt checks used for the paper's separate comprehension table and plot. They are not additional main decisions. |

Each batch retains its own manifest, attempt log and completion summary. The
[original pilot report](../../docs/phase6_report.md),
[re-pilot report](../../docs/repilot_20261126_report.md) and
[decision log](../../docs/decisions.md) explain the prompt amendment and reviews.
The earlier records remain intact. Trial IDs can recur in separate batches,
so keep each batch with its own manifest and log; do not combine the two rounds.

Retries and re-asks retain the decision's trial ID and add attempt records.
API errors are separate from invalid model replies and do not by themselves
exclude a decision. The [engine guide](../../docs/engine.md) explains recovery,
and the [data dictionary](../../docs/data_dictionary.md) defines the fields.
Credentials, headers and `.env` files do not belong in these research artifacts.
