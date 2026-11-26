# Study 2 analysis and reproduction

The pipeline lives in `src/kinloyalty/analysis/study2/`. It does not invoke Study
1 analysis, read credentials, or make model calls. During Phase 5, all execution
and numerical verification use explicit synthetic mock logs. Real smoke, pilot,
and probe data are ineligible for inference. The researcher approved the
clarifications below on 2026-11-26; they are preserved in `docs/decisions.md` and
the unlocked draft `preregistration/study2.md`.

## Reproduce independently

Create a fresh synthetic collection using independent fixture seeds, then replay
and reproduce every table and figure with the production replication counts:

```sh
.venv/bin/kinloyalty study2 simulate --output /private/tmp/study2-synthetic-example
.venv/bin/kinloyalty study2 reproduce \
  --manifest /private/tmp/study2-synthetic-example/manifest.jsonl \
  --directory /private/tmp/study2-synthetic-example/collection \
  --output /private/tmp/study2-synthetic-results --allow-synthetic
```

Choose fresh paths. Synthetic generation uses the actual Study 2 engine,
append-only logs, frozen requests and replay, with mock clients only. The default
fixture plants a buyer final-offer increase of 0.20 zone units for the same-model
label, producing a P2 surplus-share contrast of −0.20. These numbers are test
inputs and expected synthetic results, not empirical findings. Mock token counts
are explicitly synthetic fixture values, not measured provider usage.

`analyze` and `reproduce` are aliases for the same replay-first pipeline. Main
analysis later uses the same arguments without `--allow-synthetic`. No actual
main manifest has been generated in Phase 5. The collection runner still permits
live smoke only; read-only replay understands future explicitly approved
pilot/main contracts so future main inference can use the same verification
path. This reader support does not enable or authorize live execution.

`--resamples N` is available only with explicitly opted-in synthetic input for
shorter tests; it is rejected for real input. Default analysis uses the frozen
config's 10,000 bootstraps and 10,000 permutations. The output directory must be
fresh, outside the input collection and protected study/mechanical-report paths.
No raw input or existing result is overwritten. The loader refuses unfinished
collections, pending calls, active writers, probes, wrong phases/modes, changed
bindings, corrupt logs, or summaries inconsistent with the replayed replies.

## Outcomes and eligibility

All outcomes omit excluded episodes. Impasses have zero primary surplus share,
zero deal indicator, and zero mandate-violation flags. Primary share is
`(b-p)/(b-s)` for deals, with no clipping, including values below zero or above
one. Deal-only share and messages to agreement are undefined for impasses.
These two secondary outcomes condition on agreement, which disclosure can affect;
their contrasts are not unconditional effects on the same population.

The first buyer offer x gives position `(b-x)/(b-s)`; an episode without a buyer
offer is undefined. The buyer's average concession is the mean of
`(x_(j+1)-x_j)/(b-s)` between consecutive offers made by the buyer agent itself.
Seller offers and acceptance prices never enter this sequence. Positive values
mean raising an offer, negative values mean lowering it. There is no truncation.
Fewer than two buyer offers makes the concession outcome undefined. Eligible
counts, exclusions, and undefined non-excluded counts are reported for every
outcome per original disclosure condition and per displayed label in
`tables/outcome_eligibility.csv`.

Buyer violation means a deal above b, including the buyer's own offer being
accepted. Seller violation means a deal below s. Unaccepted offers outside a
limit are not violations. Counts and rates are reported by original condition
and buyer model, with non-excluded episode denominators (impasses contribute zero).

## Regression, permutations, and bootstrap

The primary OLS specification is
`surplus_share ~ C(pair_id) + buyer_opens + card_says_same + card_says_other`.
The baseline is not disclosed (`none`). The primary P2 contrast is same minus
other. It uses all non-excluded episodes, without scenario fixed effects. The
implementation eliminates pair intercepts algebraically and is checked against
independent statsmodels fits. Secondary outcome fits use this same specification
and all episodes eligible for their particular outcome.

Each permutation independently swaps or keeps only the two compared labels
within a pair-and-scenario stratum. Both tested episodes must have that outcome
available; otherwise that tested pair is held fixed. All eligible singleton rows
remain in OLS. The third condition is irrelevant: an excluded `none` episode
does not block a complete same/other pair. This rule applies to primary,
secondary, buyer-specific, and disclosure-baseline tests. Every permutation test
reports planned, complete, incomplete, singleton, and neither-eligible strata,
plus the numbers of fixed tested and third-label rows. Incomplete is singleton
plus neither eligible. No imputation, replacement, or complete-case-stratum
filtering changes the point-estimation sample.

Matched rows have identical pair and opener controls, so exchanging their labels
is exactly equivalent to exchanging their outcomes in the fixed design. The
implementation reuses the OLS projection for each exchange; independent explicit
label-refit tests verify the resulting statistic. Two-sided p-values use
`(1 + count(abs(T_perm) >= abs(T_obs) - 1e-12))/(10000+1)`.

Bootstrap the 20 planned scenarios with replacement separately within each pair,
carrying the three episode slots together. Excluded or undefined rows stay
unavailable; no scenario is replaced because an outcome is missing. A single
shared array of scenario draws supports the primary CI, TOST, all secondary CIs,
and descriptive figure intervals. Buyer-specific fits use the four relevant
pairs from those same draws. Rank-deficient nuisance coefficients are allowed
when the requested contrast is identifiable. Non-estimable contrasts are marked
unavailable. Failed bootstrap estimates remain NaN in the saved array; no failed
draw is dropped or redrawn. If any requested draw is unavailable, that contrast's
interval (and primary TOST) is unavailable, with failure counts reported.

Bootstrap intervals select count-matched order statistics without interpolation:
95% ranks 250/9,751; 90% ranks 500/9,501. RNG streams are derived deterministically
from the frozen bootstrap/permutation seeds, sorted pair/scenario identities,
and test keys. The shared conservative numerical tolerance is 1e-12.

The primary bootstrap TOST is always attempted using the primary contrast's same
bootstrap estimates: lower tail `T_boot <= -0.05 + 1e-12`, upper tail
`T_boot >= 0.05 - 1e-12`, each with the add-one correction. Report both one-sided
p-values, their maximum, the 90% interval and ranks, and strict containment.
Equivalence requires both p-values below 0.05 and the 90% interval strictly
inside the bounds with conservative tolerance. It is not conditional on the
primary difference test being nonsignificant.

The specified statsmodels OLS contrast with pair-cluster covariance is reported
only as a robustness check, alongside its SE, statistic, p-value, interval, and
cluster count. Sixteen clusters are not the basis for primary inference.

## Secondary analyses and figures

Report secondary tests without multiplicity correction: four buyer-specific P2
contrasts, same versus none and other versus none, and seven secondary outcome
contrasts (deal-only share, deal rate, messages to agreement, first buyer offer,
average buyer concession, and buyer/seller mandate violations).

The interaction regression adds both card indicators × actual self-pair terms;
pair fixed effects absorb actual self-pair status itself. Its contrast is
`(same-other in self-pairs) - (same-other in cross-pairs)`, the difference of the
two interaction coefficients. A positive estimate means a more positive label
contrast in actual self-pairs. Output labels state this sign convention. Report
the scenario-bootstrap interval only, without a permutation test. The actual
kinship × displayed-label mean table is descriptive, without a test.

All figures use the existing matplotlib fonts, dimensions, colors, 220-dpi PNG,
and PDF conventions. They are:

- Main: displayed same/other × actual copy/different model mean shares, with
  scenario-bootstrap 95% intervals and a not-disclosed baseline for each actual
  group.
- Figure 2: deal rate and within-deal share side by side, grouped by displayed
  `same`, `other`, `none` in that order.
- Appendix: buyer-specific P2 estimates with 95% intervals; surplus-share
  distributions by original disclosure condition.

Synthetic figures are marked SIMULATED. Values are never restricted to [0,1].
Unavailable point estimates/intervals are marked explicitly. Descriptive usage
reports retain missing token fields as missing, distinct from zero, and summarize
reasoning counts per model/role, provider caches, maximum input tokens, and
public-message character lengths. No semantic coding of messages is performed.

## Output contract and verification

- `report.md`: result overview, interpretation limits, and approved conventions.
- `metadata.json`: methods/seeds, TOST, robustness check, replay counts, frozen
  manifest and input hashes, current code hashes, Git/package provenance.
- `tables/contrasts.csv`: primary/secondary estimates, 95% intervals, permutation
  p-values where specified, eligibility and incomplete-stratum counts.
- `tables/outcome_eligibility.csv`: per-outcome condition/displayed-label counts.
- Other CSVs: replay-verified numerical episodes, scenario index, pair/condition
  and pooled descriptives, mandate/usage/length tables, figure means and CIs.
- `resamples.npz`: shared zero-based scenario draw indices and every bootstrap/
  permutation statistic, including unavailable estimates. The column-to-scenario
  mapping is `tables/scenario_index.csv`.
- `figures/`: four figures, each PDF and PNG.
- `artifacts.sha256.json`: hashes of every result file except the inventory itself.

Within an unchanged code/environment/input snapshot, two fresh reproduce runs
produce byte-identical result artifacts, including PDF/PNG and NPZ. Provenance
and package versions remain visible when a different environment is used.

```sh
.venv/bin/python -m pytest -q tests/test_study2_analysis.py tests/test_study2_inference.py
.venv/bin/python -m pytest -q
```

Tests use synthetic data only and block network sockets. They independently
verify OLS, bootstrap row-refits, tested-pair swaps with missing outcomes, signed
concessions, interaction sign, full mock replay, planted/null/reversed/boundary
fixtures, and byte-identical CLI reproduction. Study 1's locked manifest hash
and existing tests remain part of the preservation checks.
