# Study 2 saved results

[main/](main/) contains the completed pre-registered main analysis. Read
[analysis-summary.md](analysis-summary.md) for results in the registered order.
To recreate them, follow [Reproduce the paper](../../docs/reproducing_the_paper.md)
for setup, frozen-checkout replay, fresh output paths and comparison with these
reference files. No model calls or API keys are needed.

## Main outputs

P2 compares the buyer's surplus share when the card says the same model with
its share when the card says a different model. Displayed labels describe what
the buyer was told; actual kinship describes whether the two agents really use
the same model. These are distinct groupings in the saved outputs.

| File or group | What it provides |
| --- | --- |
| [main/tables/contrasts.csv](main/tables/contrasts.csv) | Primary P2 and secondary contrasts, intervals, permutation p-values and complete/incomplete tested-pair stratum counts. |
| [main/metadata.json](main/metadata.json) | The primary equivalence test and pair-cluster robustness check, together with frozen settings, seeds, replay and software/input provenance. |
| [outcome eligibility](main/tables/outcome_eligibility.csv), [episodes](main/tables/episodes.csv) and [scenario index](main/tables/scenario_index.csv) | Eligible counts, analysed episode rows and the scenario units used for resampling. |
| [pair/condition descriptives](main/tables/pair_condition_descriptives.csv), [pooled descriptives](main/tables/pooled_descriptives.csv) and [displayed-label descriptives](main/tables/displayed_label_descriptives.csv) | Summaries under the original assignments and the labels shown to buyers. |
| [actual-kinship means](main/tables/actual_kinship_means.csv) and [deal/share means](main/tables/price_and_deal_means.csv) | The grouped descriptive means used in the figures. The first file also supplies main-paper Table 2. |
| [mandates by condition](main/tables/mandates_by_condition.csv) and [mandates by buyer](main/tables/mandates_by_buyer.csv) | Recorded private-limit violations. |
| [usage calls](main/tables/usage_calls.csv), [usage summary](main/tables/usage_summary.csv), [cache summary](main/tables/provider_cache_summary.csv), [response lengths](main/tables/message_lengths.csv) and [public-message lengths](main/tables/public_message_lengths.csv) | Provider usage, cache metadata and message-size diagnostics. |
| [main/resamples.npz](main/resamples.npz) | Saved bootstrap scenario indices, estimates and permutation statistics, including unavailable draws. |
| [main/report.md](main/report.md) and [artifact hashes](main/artifacts.sha256.json) | The generated report and checksums of all generated artifacts. |

The four figures, each saved as PDF and PNG, show
[displayed labels and actual kinship](main/figures/main_label_by_actual_kinship.pdf),
[deal rate and within-deal share](main/figures/deal_rate_and_within_deal_share.pdf),
[buyer-specific P2](main/figures/appendix_buyer_p2.pdf) and
[surplus-share distributions](main/figures/appendix_share_distributions.pdf).
The [paper-artifact map](../../docs/reproducing_the_paper.md#paper-figures-tables-and-pdf)
identifies the presentation copies used in the appendix. Analysis output and
manuscript compilation are separate steps.

## Original analysis and reproduction evidence

These outputs were generated on 2026-11-27 from `study2-data`, commit
`3b3b85d77c619fcc6fb093a93915e5ef769cbf53`. Replay verified all 960 episodes and
8,417 attempts before inference.

The original command below ran inside that frozen checkout, with its source
first on `PYTHONPATH` and the locked dependencies available. Its destination
was new at that time. For another reproduction, use the guide's separate
scratch destination rather than the existing reference directory:

```sh
.venv/bin/kinloyalty study2 reproduce \
  --manifest data/study2/main/manifest.jsonl \
  --directory data/study2/main \
  --output results/study2/main
```

The scientific analysis, configuration, prompts, dependencies, protocol and
scoring match `prereg-study2` (`c277054e182eb3a81a475108fa3439e96e869bb0`).
The full tag difference includes the approved main-execution and dual-provenance
patch `4e088670c0cc8386eccf8fff01d93d353a230bda`, as well as data. The
[registration index](../../preregistration/README.md),
[execution patch report](../../docs/study2_main_execution_patch.md) and
[decision log](../../docs/decisions.md) explain the deviation, which is also
reported in the paper. No analysis code, parameters or seeds changed.

The original [independent reproduction audit](reproduction-check.json) used
then-current main commit `78aac6a5125c293b2a9f66f50b3f061624c7da80`. All sixteen
numeric tables, eight figure files, `resamples.npz` and `report.md` matched byte
for byte. Only the execution commit recorded in `metadata.json` and its
checksum entry differed. The later
[documentation verification](../../docs/reproduction-validation.json) checked
the fresh-environment procedure in the current reproduction guide.

## Earlier reports and further reading

[smoke-report/](smoke-report/), [pilot-report/](pilot-report/) and
[main-collection-report/](main-collection-report/) retain collection and review
reports separately from the analysis outputs. Smoke, pilot and probe data never
enter main inference. The [data index](../../data/study2/README.md) explains the
collections and provenance fields. The [methods guide](../../docs/study2_analysis.md)
explains outcomes, eligibility and inference; the
[documentation index](../../docs/README.md) provides the wider navigation.
