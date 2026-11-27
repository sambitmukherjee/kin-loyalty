# Study 2 recorded data

The main collection and pre-registered analysis are complete. The `study2-data`
tag freezes the collection at commit `3b3b85d77c619fcc6fb093a93915e5ef769cbf53`.
All 960 negotiations completed in 8,417 API attempts, including two recovered
API errors. There were no invalid-reply re-asks, exclusions, episode resumptions
or unfinished episodes. Replay verified every attempt and terminal summary.
The [main collection report](../../results/study2/main-collection-report/collection-report.md)
records those checks.

Use the [reproduction guide](../../docs/reproducing_the_paper.md) for setup,
frozen-checkout replay and analysis. The [results index](../../results/study2/README.md)
identifies the saved outputs. For another experiment, start with the
[worked guide](../../docs/running_a_new_experiment.md), which keeps new inputs
and mock logs separate from this collection.

## Collections

| Directory | Contents | Use in the paper |
| --- | --- | --- |
| [main/](main/) | The frozen manifest, turn attempts and 960 terminal episode records. | These supply the pre-registered main analysis. |
| [smoke/](smoke/) | Four ordinary test negotiations and sixteen forced-position probes, completed in 51 calls. | They check request formats and mechanics; they do not enter inference. |
| [pilot/](pilot/) | Eighty pilot episodes, completed in 707 attempts. | They support the blind pilot review and do not enter main inference. |

An episode is one negotiation. A turn is one public message, while an attempt
is one API call, including a failed call or re-ask. A JSONL file stores one JSON
record per line.

| Main collection file | Contents |
| --- | --- |
| [main/manifest.jsonl](main/manifest.jsonl) | The fixed assignments, scenarios, source templates, response schemas and hashes. |
| [main/turns/](main/turns/) | One attempt-log file per ordered buyer–seller model pair. |
| [main/episodes.jsonl](main/episodes.jsonl) | Terminal episode summaries, checked against independent reconstruction from the turn attempts. |
| [main/collection.json](main/collection.json) | The collection scope, manifest binding, version checks and execution authorization. |
| [main/preflight.json](main/preflight.json) | The checks and provenance recorded before collection. |
| [main/run_summary.json](main/run_summary.json) | Mechanical completion counts and log-file sizes. |

The main manifest has sixteen ordered model pairs, twenty shared scenarios per
pair and three disclosure conditions, giving 960 episodes. Its SHA-256 is
`293fecc0f30249e46a794d3d4e1d7d2eacb51e3ad2e13b2113da7067e0a7b814`.
The [addendum](../../preregistration/study2.md) and
[lock inventory](../../preregistration/study2-lock.json) record the frozen plan.

## Registration and execution provenance

Every main turn attempt and terminal episode carries the following fields:

| Field | Revision and meaning |
| --- | --- |
| `registration_git_commit` | `c277054e182eb3a81a475108fa3439e96e869bb0`, the original `prereg-study2` commit. |
| `execution_git_commit` | `4e088670c0cc8386eccf8fff01d93d353a230bda`, the code used for main collection. |
| `git_commit` | The same actual execution revision. |

The main launcher and these extra provenance fields were an approved mechanical
change after registration. The [execution patch report](../../docs/study2_main_execution_patch.md)
explains it. The scientific analysis, prompts, configuration, protocol and
scoring remained unchanged. The data-tag commit identifies the later frozen
snapshot; the execution commit identifies the code that made each call. The
[registration index](../../preregistration/README.md) explains the four study tags.

## Development batches and recovery

Smoke probes use fixed, hand-written transcripts, retained in the
[smoke report](../../docs/study2_phase4_report.md). They have `phase: smoke` and
`is_probe: true`, and their separate terminal records are in
[smoke/probes.jsonl](smoke/probes.jsonl). They are never scored as negotiation
outcomes or included in pilot or main inference. The
[pilot report](../../docs/study2_phase6_report.md) pools disclosure conditions
within each pair.

Before a call, a pending sidecar records its reserved identity and request.
The completed attempt is appended and flushed to disk. On resume, the runner
verifies the saved plan and history, records unresolved calls as interrupted,
and continues unfinished work. Completed episodes and exclusions are retained.
The main collection needed no episode resumptions. The
[data dictionary](../../docs/data_dictionary.md#study-2-persisted-records-version-1)
describes the records, journals and replay checks.

The original live launchers and approvals apply to the original collections.
The public `kinloyalty study2 run` command accepts mocks only; synthetic examples
belong outside these real study directories. Keep credentials and headers out
of manifests, logs and other research artifacts.
