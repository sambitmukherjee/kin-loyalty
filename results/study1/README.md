# Study 1 saved results

[generated/](generated/) contains the completed pre-registered main analysis.
For a guided account of the results, read [analysis_report.md](analysis_report.md).
To recreate them, follow [Reproduce the paper](../../docs/reproducing_the_paper.md)
for setup, the frozen checkout, fresh output paths and comparison with these
reference files. No model calls or API keys are needed.

## Main outputs

P1 is the own-model minus other-lab contrast in dictator transfers. Its pooled
estimate gives the four models equal weight. The other tables retain the
registered secondary comparisons and diagnostics.

| File or group | What it provides |
| --- | --- |
| [generated/contrasts.csv](generated/contrasts.csv) | P1 and the secondary contrasts, with estimates, intervals and permutation p-values. It also supplies the estimates redrawn in main-paper Figure 1. |
| [generated/equivalence.csv](generated/equivalence.csv) | The pooled primary equivalence test and its interval. |
| [generated/descriptives.csv](generated/descriptives.csv), [decisions.csv](generated/decisions.csv) and [coverage.csv](generated/coverage.csv) | Descriptive summaries, valid decision rows and planned/valid/excluded counts for every main cell. |
| [generated/s1_coefficient_changes.csv](generated/s1_coefficient_changes.csv), [belief diagnostics](generated/s1_belief_diagnostics.csv) and [belief cell counts](generated/s1_belief_cell_counts.csv) | The descriptive belief-adjusted comparison and its estimability checks. |
| [generated/comprehension.csv](generated/comprehension.csv) | The separate final-prompt comprehension check. |
| [generated/attempt_diagnostics.csv](generated/attempt_diagnostics.csv), [usage calls](generated/usage_calls.csv) and [usage summary](generated/usage_summary.csv) | Collection diagnostics and reported token/cache usage. |
| [generated/resampling_distributions.npz](generated/resampling_distributions.npz) | The saved bootstrap and permutation arrays. |
| [generated/provenance.json](generated/provenance.json) and [artifact hashes](generated/artifacts.sha256.json) | Analysis settings, seeds, software/input provenance and checksums of the generated files. |

Four figures are saved in both PDF and PNG form: the
[main decision distributions](generated/main_distributions.pdf),
[responder distributions](generated/responder_distributions.pdf),
[S1 coefficient comparison](generated/s1_coefficients.pdf) and
[comprehension table](generated/comprehension.pdf). The
[paper-artifact map](../../docs/reproducing_the_paper.md#paper-figures-tables-and-pdf)
explains their relationship to the main figure and appendix figures. These
scientific outputs are separate from compiling the manuscript PDF.

## Original analysis and reproduction evidence

These outputs were generated on 2026-11-27 from `study1-data`, commit
`f7dd0a690a5089b245fff365acf002fcfd7b056a`. Its registered analysis,
configuration and prompts match `prereg-study1`
(`d4d6ff9c1f7b84bc2b4f90578873f18dbc9fb98a`) exactly.
The [registration index](../../preregistration/README.md) explains both tags.

The original command was run inside the frozen data checkout. Its destination
was new at that time; for another reproduction, use the guide's fresh scratch
paths rather than the existing reference directory below:

```sh
uv run --offline --locked kinloyalty reproduce --config configs/study1.yaml \
  --data data/study1/main \
  --comprehension data/study1/repilot_20261126/comprehension \
  --output results/study1/generated
```

The original [independent reproduction audit](reproducibility.json) used the
then-current main commit `3b3b85d77c619fcc6fb093a93915e5ef769cbf53`. Every numeric
table, figure and saved resampling array/archive matched byte for byte. Only
provenance and its checksum entry differed, as the audit explains. The later
[documentation verification](../../docs/reproduction-validation.json) checked
the fresh-environment procedure now described in the reproduction guide.

## Earlier reports and further reading

[pilot-report/](pilot-report/), [comprehension-report/](comprehension-report/)
and [repilot_20261126/](repilot_20261126/) retain separate historical pilot and
check reports. They are not additional main-analysis outputs. The
[data index](../../data/study1/README.md) identifies the input batches and the
final comprehension check. The [methods guide](../../docs/analysis.md) explains
eligibility and inference; the [documentation index](../../docs/README.md)
provides the wider navigation.
