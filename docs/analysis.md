# Study 1 analysis and reproduction

All commands below run locally without model API calls, SDK imports, or API-key
reads. Outcomes come from saved logs, never from re-rendered prompts. The
analysis is implemented before the pilot and pre-registration lock.

## Eligibility and histories

`analyze study1` and `reproduce` accept only `study1` / `main` attempt records.
They reject smoke, pilot, and comprehension decisions, even when synthetic input
is enabled. Comprehension records are accepted only as a separate optional batch
for the comprehension table. Real and synthetic batches cannot be combined.

The loader validates frozen trial/request hashes, stable IDs, attempts, dispatch
identities, response opportunities, validation outcomes, final/excluded states,
and backend flags. Duplicate or conflicting attempts, mixed phases, altered
answers, corrupt JSONL, pending reservations, and unknown model identities fail.
Input folders select `*attempts*.jsonl`; arbitrary log filenames can be passed
explicitly. Multiple non-overlapping log files can be supplied.

Main inference requires every configured draw to have a terminal record. API
failures left unfinished must be resumed first. Only final valid replies enter
outcome tables. Excluded draws remain in coverage and diagnostics; they are never
imputed as zero. Empty label × paraphrase cells or non-identifiable adjusted
regressions fail explicitly instead of dropping a model or changing its weight.

Synthetic data require `--allow-synthetic`. All output provenance and figure
titles then identify them as simulated. Simulation directories must be outside
the configured real study data/results roots. No real main manifest is created
by testing the analysis.

## Estimation

For each model and outcome, ordinary least squares uses all five label
indicators plus paraphrase indicators (one omitted reference paraphrase). This
is equivalent to an intercept with reference-label coding. A contrast is the
difference between the relevant fitted label coefficients. Unequal retained
cell counts after exclusions use the actual regression, not raw mean differences.

The pooled estimate is the arithmetic mean of the four model estimates. Its
weight remains one quarter per model even when exclusions differ. No cluster
standard errors across models or random-effects meta-analysis are used.

The six distinct contrasts are own-model minus other-lab, other-lab minus
fictional, each of own-model/other-lab/fictional minus undisclosed, and human
minus undisclosed (S2). These apply to dictator transfers, proposer offers,
responder minimums, and proposer beliefs. Only the pooled dictator own-minus-other
test is primary P1; per-model tests and all other comparisons are secondary.
There is no multiplicity correction.

For S1, paired offers and beliefs enter a regression with label and paraphrase
controls. The researcher approved model-specific belief slopes; the workflow averages the
four adjusted contrasts equally. Before/after coefficients and their paired
bootstrap change are reported. Coefficient changes are descriptive associations;
they are not causal mediation estimates. The change table has no additional
hypothesis test. The adjusted coefficients themselves have intervals and
permutation p-values.

## Bootstrap intervals and equivalence

The bootstrap uses **10,000** draws with the configured fixed seed. Within each
model × label × paraphrase cell, observations are resampled with replacement at
the original retained cell size. Offer/belief pairs stay together. Regression
coefficients are refitted for each draw, including the belief slope. Independent
model streams are combined by averaging estimates at the same bootstrap index.

The interval convention is the basic (reverse-error) bootstrap. For observed
estimate `d` and bootstrap errors `e = d_boot - d`, its 95% interval is
`[d - quantile(e, .975), d - quantile(e, .025)]`. This matches the basic interval
definition in the [SciPy bootstrap documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.bootstrap.html).

Pooled P1 TOST is **always** calculated at the configured bound ±$5, regardless
of the difference-test result. The researcher approved null-centered bootstrap
TOST using the same 10,000 stratified draws. The lower null is `d <= -5`, with
upper-tail probability of `e >= d + 5`; the upper null is `d >= 5`, with lower-tail
probability of `e <= d - 5`. Both use `(1 + tail_count)/(B + 1)`. Equivalence
requires both one-sided p-values below .05. The maximum is reported as `p_tost`.
The accompanying basic 90% interval is reported separately from the 95% contrast
interval. These are approximate bootstrap tests; no t-test approximation or
four-model degrees of freedom are inserted. [TOSTER's bootstrap reference](https://aaroncaldwell.us/TOSTERpkg/reference/boot_t_TOST.html)
describes the method family and matching interval conventions; TOSTER is not a
dependency or an assertion of numerical equivalence to its implementation.

## Permutation tests

Every test uses **10,000** random permutations and the configured fixed seed.
The researcher approved permuting only the two tested labels within each
model × paraphrase stratum, preserving both label counts and leaving the other
labels fixed. The full regression is refitted, retaining other-label and
paraphrase controls. Permuting outcome assignments within the tested pair is
algebraically equivalent here because the fixed-design cross-product is unchanged.

For belief-adjusted S1, the approved method is Freedman–Lane: merge the tested
label columns under their equality null, retain all other labels, paraphrases,
and belief as nuisance regressors, fit that reduced model, permute its residuals
within model × paraphrase, add the reduced fitted values, and refit the full
model. Estimated nuisance residuals make this an approximate permutation method.
The procedure follows [Winkler et al. (2014)](https://pmc.ncbi.nlm.nih.gov/articles/PMC4010955/).

Pooled null statistics average the four independently permuted model estimates.
All p-values are two-sided, using `|T_perm| >= |T_observed|`, with a `1e-12`
comparison tolerance for floating-point ties. The randomized-test correction is
`(1 + extreme_count)/(R + 1)`; p-values cannot be zero. The correction is also
documented by [SciPy](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.permutation_test.html).
We explicitly use absolute-statistic tails, rather than SciPy's default
twice-the-smaller-tail convention. Label permutations test exchangeability of
the two conditions within each stratum; they do not generalize to other models.

All RNG streams derive from SHA-256 of the configured seed and named analysis,
model, contrast, and method. Trial rows are sorted by stable IDs. Output does not
depend on completion order or Python's randomized hash. Bootstrap/permutation
draws are saved in `resampling_distributions.npz` for audit.

## Commands

When real main and comprehension logs exist, one command regenerates the tables,
figures, provenance, and artifact hashes:

```sh
kinloyalty reproduce --config configs/study1.yaml \
  --data data/study1/main --comprehension data/study1/comprehension \
  --output results/study1/generated
```

`kinloyalty analyze study1` accepts the same arguments and runs the same pipeline.
Output directories must be new; existing artifacts are never overwritten. If no
comprehension input is supplied, that table/figure is omitted. Main logs and the
comprehension batch are never merged into one outcome dataset.

For an offline demonstration, choose a new temporary path:

```sh
kinloyalty simulate-study1 --directory /private/tmp/kin-loyalty-demo \
  --own-model-effect 12
kinloyalty reproduce --data /private/tmp/kin-loyalty-demo/main \
  --comprehension /private/tmp/kin-loyalty-demo/comprehension \
  --output /private/tmp/kin-loyalty-demo-results --allow-synthetic
```

The mock client adds $12 to own-model numeric outcomes without clipping in this
demonstration's range. It generates 3,600 synthetic main draws, 240 pilot draws,
and 320 comprehension draws through the ordinary manifest/runner/log interfaces.
Their model versions and usage are synthetic. They are not observations about
the named models and are never stored in the project's real data folders.

Pilot/comprehension reports are separate commands:

```sh
kinloyalty report pilot --data data/study1/pilot --output results/study1/pilot-report
kinloyalty report comprehension --data data/study1/comprehension \
  --output results/study1/comprehension-report
```

Pilot decision distributions and exclusion/re-ask diagnostics pool all labels
within model × decision. No pilot outcome contrast is computed. Comprehension
answer shares use the planned denominator of 20; excluded/unfinished/missing
draws cannot become correct answers. A scored label passes with at least 18
correct once all planned draws are terminal. Undisclosed is reported unscored.
Model pass requires every scored label to pass; failed models remain in all
analyses. Incomplete checks are explicitly unscored until completed.

## Artifacts and verification

The main workflow writes 150 contrast rows: 120 unadjusted rows across four
outcomes and 30 belief-adjusted offer rows. See `data_dictionary.md` for all CSV
contracts. Four matplotlib figures are saved as PDF and PNG when comprehension
input is available. Main and responder figures show distributions per model;
the main figure annotates pooled P1. S1 shows own-minus-other offers, adjusted
offers, and beliefs with intervals. PDF date metadata is disabled.

`provenance.json` records input/config/source hashes, settings, seeds, dependency
versions, synthetic status, and code provenance. `artifacts.sha256.json` hashes
every output except itself. Tests check independent OLS agreement, an enumerable
permutation null, TOST boundaries, pair preservation, exclusions, eligibility,
pilot blinding, planted-effect recovery, and byte-identical reproduction.
