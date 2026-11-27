# Study 2 data

The main collection and pre-registered analysis are complete. The `study2-data`
tag freezes the collection at commit `3b3b85d77c619fcc6fb093a93915e5ef769cbf53`.
All 960 episodes completed in 8,417 API attempts. Two API errors were recovered;
there were no invalid-reply re-asks, exclusions, resumptions or unfinished episodes.
Replay checked all 8,417 attempts and reconstructed all 960 terminal summaries.
The [main collection report](../../results/study2/main-collection-report/collection-report.md)
records these mechanical checks. The [results README](../../results/study2/README.md)
indexes the completed analysis and independent reproduction audit.

| Directory | Contents | Use in the paper |
| --- | --- | --- |
| [smoke/](smoke/) | Four ordinary test negotiations and sixteen forced-position probes, completed in 51 calls. | These check request formats and pipeline operation; they do not enter inference. |
| [pilot/](pilot/) | Eighty completed pilot episodes, recorded in 707 attempts. | These support the blind pilot review; they do not enter main inference. |
| [main/](main/) | The frozen manifest, turn attempts and 960 terminal episode records. | These supply the pre-registered main analysis. |

## Files and provenance

Each collection has a `manifest.jsonl` containing its fixed assignments, source
text, schemas and hashes. Attempts are stored in `turns/<buyer>__<seller>.jsonl`.
The `episodes.jsonl` file contains terminal summaries for ordinary episodes.
Only the smoke collection has `probes.jsonl`; probes are marked separately and
have no outcome scores. `collection.json` records the collection scope and
checks, and `run_summary.json` records mechanical completion information.

The main manifest contains 960 episodes: sixteen ordered buyer–seller pairs,
three disclosure conditions and twenty scenarios per pair. Its SHA-256 is
`293fecc0f30249e46a794d3d4e1d7d2eacb51e3ad2e13b2113da7067e0a7b814`.
The [addendum](../../preregistration/study2.md) and
[lock inventory](../../preregistration/study2-lock.json) record the frozen plan.

Every main turn and terminal episode records:

- `registration_git_commit`: `c277054e182eb3a81a475108fa3439e96e869bb0`, the original `prereg-study2` commit.
- `execution_git_commit`: `4e088670c0cc8386eccf8fff01d93d353a230bda`, the code used for main collection.
- `git_commit`: the same actual execution revision.

The main launcher and these extra provenance fields were an approved mechanical
change after registration. The [execution patch report](../../docs/study2_main_execution_patch.md)
explains the deviation. The scientific analysis, prompts, configuration,
protocol and scoring remained unchanged. The data-tag commit identifies the
later frozen snapshot; it is distinct from the execution commit in each record.

## Logging and recovery

Every call is recorded before dispatch and its completed record is appended and
flushed to disk. Pending sidecars preserve unresolved calls after interruption;
advisory `.lock` files are local and ignored by Git. Resume verifies the saved
plan and histories, records calls with unknown completion as interrupted, and
continues unfinished episodes. Completed episodes and exclusions are not replaced.
Damaged log tails are preserved for explicit recovery. The main run needed no
episode resumptions.

Smoke probes use fixed, hand-written transcripts. Their attempts retain
`phase: smoke` and `is_probe: true`, including any permitted re-ask. They never
enter the pilot or main analysis. The smoke report preserves the exact transcripts.
Pilot outcome summaries pool disclosure conditions within each pair.

The public `kinloyalty study2 run` command accepts mocks only and rejects real
study destinations. Dedicated live modules handled the original smoke, pilot
and main collections. The main launcher accepts only the registered manifest
and requires its original clean execution commit. New experiments need separate
configurations and collection arrangements. Synthetic examples belong outside
these real study directories. Credentials and request headers must never be
stored in research artifacts. The [data dictionary](../../docs/data_dictionary.md)
describes the record fields.
