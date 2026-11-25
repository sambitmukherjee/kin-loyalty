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
imputed as zero. Empty label × paraphrase cells fail explicitly. Unavailable
belief-adjusted regressions are flagged in the outputs, retaining every model
and the four-model pooled target as described below.

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
bootstrap change (unadjusted minus adjusted) are reported. Coefficient changes are descriptive associations;
they are not causal mediation estimates. The change table has no additional
hypothesis test. The adjusted coefficients themselves have intervals and
permutation p-values.

The adjusted/unadjusted offer regressions use the same retained draws and the
same bootstrap indexes. The coefficient-change interval comes from the paired
difference on each resample. No explained-share ratio is calculated: such a
ratio is unstable when the unadjusted contrast is near zero. Stated beliefs are
measured after the card, so the adjustment does not identify causal mediation.

### Fixed count-based S1 estimability rule

Before the pilot, the researcher fixed this rule: choose each label × paraphrase
cell's modal belief, breaking modal ties by the lowest value; count retained
valid proposer draws differing from their own cell's mode. If fewer than 10%
are nonmodal, flag that model's adjusted contrast as not estimable. Exactly
30/300 passes; fewer than 30/300 fails. For `N` retained valid draws, the minimum
is `ceil(N/10)`. No SD cutoff is used, and this rule will not be tuned after the
pilot. `s1_belief_diagnostics.csv` records every model's count/denominator and
status; `s1_belief_cell_counts.csv` records the cell modes and counts.

Unavailable adjusted point estimates, intervals, and p-values remain empty with
explicit status/reason columns. Their unadjusted and belief analyses remain
available. A four-model adjusted average is unavailable if any model is not
estimable; no three-model average is substituted. Plots retain each model's
position and identify unavailable adjusted contrasts with `NE`.

For models passing the observed-sample rule, both regressions are fitted on
every paired bootstrap resample without applying the practical count cutoff
again. Numerically singular adjusted resamples remain NaN in the saved arrays
and are counted. They are never removed or redrawn; if any are unavailable, the
affected model and pooled paired-bootstrap intervals are unavailable. Observed
identifiable points and their valid permutation tests remain available. Plots
mark a point with an unavailable interval using `*`.

The same specification is recorded in the unlocked `preregistration/study1.md`.

## Bootstrap intervals and equivalence

The bootstrap uses **10,000** draws with the configured fixed seed. Within each
model × label × paraphrase cell, observations are resampled with replacement at
the original retained cell size. Offer/belief pairs stay together. Regression
coefficients are refitted for each draw, including the belief slope. Independent
model streams are combined by averaging estimates at the same bootstrap index.

Every bootstrap interval uses **count-matched empirical percentile endpoints**,
with no interpolation, centering, or reflection. Sort the same 10,000 bootstrap
estimates in ascending order:

- 90% interval: the **500th and 9,501st** estimates.
- 95% interval: the **250th and 9,751st** estimates.

This applies to model-specific and pooled primary/secondary contrasts, adjusted
S1 contrasts, and the paired unadjusted-minus-adjusted coefficient change.
It replaces all earlier basic intervals. The [SciPy bootstrap documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.bootstrap.html)
distinguishes percentile intervals from basic intervals; this project fixes the
finite-sample endpoint ranks explicitly rather than using interpolation.

For test configurations using `B` resamples, let `a = (1-confidence)/2` and take
the largest integer `k` satisfying `(k+1)/(B+1) < a`. Use the `(k+1)`th and
`(B-k)`th sorted estimates (one-based). Exact rational arithmetic defines the
strict rank boundary. Too few resamples to supply such a rank cause an error.
Sorting uses a copy so the shared bootstrap indexes remain intact.

Pooled P1 TOST is **always** calculated at the configured bound ±$5, regardless
of the difference-test result. The researcher specified percentile-bootstrap
tail probabilities using the same 10,000 stratified estimates already used for
the P1 confidence interval. No second bootstrap or new seed is used:

```text
epsilon = INFERENCE_TIE_TOLERANCE = 1e-12
p_lower = (1 + count(d_boot <= -5 + epsilon)) / 10001
p_upper = (1 + count(d_boot >= +5 - epsilon)) / 10001
p_tost = max(p_lower, p_upper)
equivalent = (p_lower < .05) and (p_upper < .05)
```

Both comparisons include numerical ties in the conservative direction, and
the p-value decisions are strictly below .05. Counts use the bootstrap estimates
directly, without centering or reflection. This replaces the
earlier null-centered/basic-interval TOST convention before the pilot.

A 90% percentile interval is reported alongside the 95% percentile interval in
`equivalence.csv`, with both endpoint ranks and method metadata. The researcher
selected the count-matched ranks above so the corrected p-value rule agrees
with the 90% interval lying **strictly** inside ±$5 after the same conservative
tie convention: its lower endpoint must exceed `-5 + epsilon` and its upper
endpoint must be below `+5 - epsilon`. Endpoints within epsilon of a bound fail
equivalence. Ordinary interpolated percentiles can
disagree with corrected p-values at the cutoff; [NumPy documents these
interpolation conventions](https://numpy.org/doc/stable/reference/generated/numpy.quantile.html).
The primary two-sided permutation test is unchanged. Bootstrap inference remains
approximate; no t-test approximation or four-model degrees of freedom is used.

## Permutation tests

Every test uses **10,000** random permutations and the configured fixed seed.
The researcher approved permuting only the two tested labels within each
model × paraphrase stratum, preserving both label counts and leaving the other
labels fixed. The full regression is refitted, retaining other-label and
paraphrase controls. Permuting outcome assignments within the tested pair is
algebraically equivalent here because the fixed-design cross-product is unchanged.

For belief-adjusted S1, the approved method is Freedman–Lane: merge the tested
label columns under their equality null, retain all other labels, paraphrases,
and belief as nuisance regressors, fit that reduced model, and permute its
residuals within model × paraphrase **among the two compared labels only**.
Residuals belonging to all other labels stay fixed. Add the reduced fitted
values and refit the full model. Its fixed design permits caching the OLS
projection, which is algebraically equivalent to repeated full refits and is
tested against independent statsmodels regressions. Estimated nuisance residuals
make this an approximate permutation method.
The procedure follows [Winkler et al. (2014)](https://pmc.ncbi.nlm.nih.gov/articles/PMC4010955/).

For pooled replicate `j`, every stratum of all four models is permuted and the
four per-model contrasts from that same replicate are averaged equally.
Per-model RNG streams are independent; their output arrays are aligned by
replicate index. The procedure never averages per-model p-values.
All permutation p-values are two-sided, using
`|T_perm| >= |T_observed| - INFERENCE_TIE_TOLERANCE`. The randomized-test correction is
`(1 + extreme_count)/(R + 1)`; p-values cannot be zero. The correction is also
documented by [SciPy](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.permutation_test.html).
We explicitly use absolute-statistic tails, rather than SciPy's default
twice-the-smaller-tail convention. Label permutations test exchangeability of
the two conditions within each stratum; they do not generalize to other models.

`INFERENCE_TIE_TOLERANCE = 1e-12` is defined once in `inference.py`. The same
absolute tolerance applies conservatively to permutation counts, bootstrap
TOST counts, and the 90% interval's strict-inside check. Tied values always count
against significance/equivalence. It does not change the strict `p < .05` rule,
interval ranks, or any bootstrap draw. The output provenance and relevant tables
record the constant. No permutation distribution or p-value is computed for
the S1 unadjusted-minus-adjusted coefficient change; only its paired interval
is reported.

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
