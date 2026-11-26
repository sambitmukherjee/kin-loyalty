# Study 2 addendum — UNLOCKED DRAFT

This is an **unlocked, incomplete draft**, started on 2026-11-26 to preserve
researcher-approved analysis definitions before the pilot. It does not authorize
collection or constitute the Phase 8 registration. Hypotheses and P2's estimand
remain those in [Study 1's registration](study1.md); they are not changed here.
The final protocol, source hashes, pilot/version report, analysis commit, main
manifest/hash, and complete prompt appendix will be added at the Phase 8 gate.
No actual Study 2 main scenarios have been drawn, and no registration tag exists.

## Approved analysis clarifications — 2026-11-26

All three definitions below were explicitly confirmed by the researcher on
2026-11-26 and are also recorded in `docs/decisions.md`.

### Signed buyer concessions and eligibility

For successive offers `x_j` and `x_(j+1)` made by the buyer's agent itself,
the concession is `(x_(j+1) - x_j) / (b - s)`. Average these consecutive-offer
concessions within the episode. An acceptance of the seller's offer is not a
buyer offer, regardless of a supplied acceptance price. A raised buyer offer
is positive and a lowered buyer offer is negative. Keep the sign and do not
truncate any value. With fewer than two buyer offers, this outcome is undefined
and that episode is omitted from this outcome's analysis. Exclusions are
unavailable for every outcome. Report eligible episodes per disclosure condition
(also report eligibility by the displayed label for interpretation).

### Missing outcomes in permutations and the scenario bootstrap

For each outcome and contrast, keep every eligible episode in the OLS point
estimate and in the scenario bootstrap. Resample planned scenarios within each
pair, carrying all three episode slots together; unavailable outcomes stay
unavailable and scenarios are not replaced. For the permutation test, independently
swap or keep the two tested labels **only** in pair-and-scenario strata where
both compared episodes have that outcome available. Hold incomplete tested pairs
fixed, keeping any eligible singleton in the regression. The third episode's
availability is irrelevant: a missing `none` episode does not stop a complete
`same`/`other` pair from swapping. This also applies to primary-outcome exclusions
and to disclosure-baseline tests (`same`/`none` or `other`/`none`). Report complete
and incomplete strata for every permutation test, splitting incomplete strata
into one eligible tested episode and neither eligible. This is the researcher's
explicit interpretation of the coding prompt's Section 6.3 exclusion sentence.

### Displayed-label figure and adjusted interaction

Figure 2 groups episodes by what the card says, in the order `same`, `other`,
`none`, and shows the deal rate and within-deal surplus share side by side.
Within-deal share conditions on agreement, which the card can itself affect.

The secondary interaction uses the surplus-share regression with pair fixed
effects, the buyer-opens indicator, both card indicators, and both card ×
self-pair interactions. Actual self-pair status is absorbed by pair fixed effects.
Report `(same - other in self-pairs) - (same - other in cross-pairs)`, which is
the difference of the two card × self-pair coefficients. A positive value means
a more positive same-minus-other label effect in actual self-pairs. State this
sign convention in outputs. Report its scenario-bootstrap 95% interval only,
with **no permutation test**. The actual-kinship two-by-two mean table remains
descriptive, without a test.

## Post-pilot mechanical review — 2026-11-26 (still unlocked)

The researcher authorized Phase 7 after the blind pilot report and the
explanation of Gemini's unobserved natural final-message cell. The review
retains the existing protocol, prompts/cards, schemas, validation, output cap,
retry rules, provider parameters, and analysis. **No post-pilot mechanical fix
was made, and no additional API call or re-pilot was performed.** See
`docs/study2_phase7_report.md` and the dated entry in `docs/decisions.md`.

Gemini sent no natural pilot reply at message 12. Its validity rate for that
cell remains undefined, not a pass or failure. Existing forced-position smoke
probes separately verified schema acceptance and valid replies at messages
11/12 for Gemini in both roles. These probes do not enter pilot denominators
or inference and do not estimate a natural final-turn validity rate. Retain
this coverage limitation in the final addendum. Preserve omitted provider cache
counts as null under the approved policy; they remain distinct from zero.

This note records the review only. Final protocol/source hashes, pilot version
table, analysis revision, actual main manifest and its hash, full prompt
appendix, and registration lock/tag still require the Phase 8 gate.
