# Study 1 pre-registration — unlocked draft

**Status:** This is an incomplete, unlocked draft. The researcher requested that
the S1 specification, its fixed estimability rule, and the pooled P1 bootstrap
TOST specification be recorded before the pilot on 2026-11-25. The remaining protocol, pilot/comprehension results, final
prompt/manifest hashes, and analysis commit references will be completed at the
pre-registration phase. No `prereg-study1` tag or registration push has occurred.

## Pooled P1 bootstrap TOST

The P1 estimand is the equally weighted mean of the four model-specific
dictator own-model-minus-other-lab contrasts with paraphrase fixed effects.
Always perform equivalence testing against −$5 and +$5, independently of the
two-sided difference test's result.

Use exactly the same 10,000 stratified bootstrap estimates used for the P1
confidence interval: resample draws within each model × label × paraphrase
cell, refit the model-specific regressions, and average the four model estimates
with equal quarter-weights at every bootstrap index. Use the existing fixed
bootstrap seed, `2026112505`, and its existing named model streams. Do not make
a separate bootstrap run or assign TOST another seed.

For the bootstrap estimates `d_boot`, calculate:

```text
p_lower = (1 + count(d_boot <= -5)) / 10001
p_upper = (1 + count(d_boot >= +5)) / 10001
p_TOST = max(p_lower, p_upper)
equivalent = (p_lower < 0.05) and (p_upper < 0.05)
```

Both boundary comparisons are inclusive. The decision uses strict p < .05 for
each one-sided test. The +1 correction prevents zero p-values. Report both
one-sided p-values and their maximum. These are percentile-bootstrap tail
areas of the estimates themselves, not tails of null-centered or reflected
bootstrap errors. This replaces the earlier null-centered TOST convention.

Sort those same 10,000 bootstrap estimates in ascending order. The 90%
percentile interval uses the **500th and 9,501st** estimates, with no
interpolation. Equivalence requires this interval to lie **strictly** inside
−$5 and +$5: if either endpoint equals its bound exactly, equivalence is not
declared. These count-matched ranks give the same decision as the corrected
one-sided p-values above, including values exactly on a bound.

Report the 95% percentile interval alongside it, using the **250th and 9,751st**
sorted estimates. Use this same no-interpolation percentile convention for
**every bootstrap interval in the analysis**: per-model and pooled primary and
secondary contrasts, S1 adjusted contrasts, and paired coefficient changes.
This replaces the earlier basic 95% intervals as well as the earlier basic 90%
TOST interval. Confidence levels, bootstrap draws/seeds, regression estimates,
and the primary two-sided permutation test remain unchanged.

For smaller synthetic-test counts `B`, the rank convention generalizes as
follows: for interval level `1-2a`, find the largest integer `k` such that
`(k+1)/(B+1) < a`; use one-based ranks `k+1` and `B-k`. Production inference uses
10,000 resamples and the specific ranks above. Record tail counts, p-values,
levels, endpoint ranks, and interval methods in the equivalence output. Sorting
must preserve the original shared bootstrap order for paired calculations.

## S1: descriptive comparison of offers and stated beliefs

For each of the four models separately, fit the proposer's offer on indicators
for all five counterparty labels, paraphrase fixed effects, and the stated
smallest offer the counterparty is expected to accept. Each model has its own
belief slope. The adjusted contrast is the fitted own-model label coefficient
minus the other-lab label coefficient. The pooled adjusted contrast is the
arithmetic mean of the four model-specific contrasts, with weight one quarter
per model.

Fit the unadjusted offer regression on the same retained valid proposer draws,
with the same label indicators and paraphrase fixed effects, omitting only the
belief term. Compare its own-model-minus-other-lab contrast with the adjusted
contrast on this same model-specific basis. Regress the stated belief itself on
the same label indicators and paraphrase fixed effects and report its label
contrast per model and the equally weighted four-model average. Other
prespecified secondary label contrasts use the same specifications.

The paired offer and belief fields come from the same response. The fields are
`amount_offered_to_counterparty` and
`smallest_offer_you_expect_counterparty_to_accept`. Only final valid main-phase
replies are used. Excluded draws are reported and never imputed as zero; missing
or unfinished main work must be completed before inference. Pilot decisions do
not enter these regressions.

### Confidence intervals and coefficient change

Use 10,000 bootstrap resamples with the fixed bootstrap seed in
`configs/study1.yaml`. Within each model × label × paraphrase cell, resample
retained draws with replacement at their observed cell size. Keep the offer and
belief together as a pair. Refit both the adjusted and unadjusted regressions
on every shared resample. Average the four model-specific estimates with equal
weights at each bootstrap index for pooled inference.

Report count-matched percentile bootstrap 95% intervals for both offer contrasts,
using the 250th and 9,751st sorted estimates without interpolation. Define the
descriptive coefficient change as **unadjusted minus adjusted** and calculate
its interval from the paired difference on every bootstrap resample. Do not
subtract separate confidence limits or treat the two estimates as independent.
Report belief contrasts with the same fixed-effect, cell-bootstrap, and
equal-weight conventions. No "share of the effect explained" ratio is reported.

Adjusted-contrast p-values use the previously specified two-sided
Freedman–Lane residual permutation within model × paraphrase strata, retaining
label/paraphrase/belief nuisance structure. Unadjusted and belief contrasts use
tested-pair label permutations within these strata. Each uses 10,000
permutations, the configured fixed seed, absolute-statistic tails, and the
randomized +1 correction. The coefficient-change table is descriptive and
introduces no extra hypothesis test.

### Fixed belief-variation rule

**This rule is fixed before the pilot and will not be adjusted after inspecting
pilot data.** For a model's retained valid proposer draws, identify the most
common stated belief separately within every label × paraphrase cell. If
multiple values tie for most common, choose the lowest value.

Count draws whose belief differs from their own cell's selected mode. Flag that
model's belief-adjusted S1 contrast as **not estimable** if this count is fewer
than 10% of its retained valid proposer draws. With 300 valid draws, fewer than
30 fails and exactly 30 passes. More generally, the minimum is `ceil(N/10)` for
`N` retained valid draws; excluded/invalid replies cannot supply a stated belief.
The diagnostic output reports `N`, the required count, actual nonmodal count,
share, and each cell's mode/counts. This is a count rule; no SD cutoff is used.

Retain the flagged model's unadjusted offer and belief contrasts. Report its
adjusted contrast, coefficient change, and their inferential quantities as
unavailable, with an explicit reason. Do not silently drop the model. If any
model's adjusted contrast is not estimable, the equally weighted **four-model**
adjusted contrast and coefficient change are also not estimable. Do not replace
them with averages over three models. Other estimable model-specific adjusted
contrasts remain reported.

Numerical rank checks remain safeguards for regression fitting. The practical
count rule is applied to the observed model sample, not used to filter or redraw
bootstrap samples. If an observed contrast is estimable but an adjusted
bootstrap fit is numerically singular, preserve that replicate as unavailable
and count it. Do not discard it, redraw until a fit succeeds, or calculate an
interval from a reduced set of bootstrap replicates. Mark the affected model's
and pooled paired-bootstrap intervals unavailable. An identifiable observed
point estimate and its valid permutation p-value can still be reported.

### Interpretation

The stated belief is measured after the counterparty card is shown and may
itself be affected by the label. Conditioning on it provides a **descriptive
decomposition**, not a causal mediation analysis or an identified share of the
label effect caused by beliefs. Comments, table labels, and figure captions use
descriptive language. A coefficient change can be negative and does not by
itself identify a mechanism.

The S1 implementation is in `src/kinloyalty/analysis/inference.py` and
`src/kinloyalty/analysis/pipeline.py`. Complete method conventions and saved-log
reproduction commands are in `docs/analysis.md`. The final pre-registration will
identify the exact analysis commit and artifact hashes after the approved pilot
and any approved mechanical fixes, while retaining this fixed variation rule.
