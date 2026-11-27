# Proposed edits — not applied

The proof preserves the supplied body wording and numbers. Full exact values,
source hashes and the other verified claims are in `numeric-audit.json`.

## Requested computations

1. **Room for agreement.** Across all 960 main Study 2 episodes, the arithmetic
   mean of Alex's maximum minus Jordan's minimum is **$222.46875**. The larger
   absolute bound of the saved 90% interval is **0.007658102208929781** share
   units. Their product is **$1.7036884257928472**. These are arithmetic checks
   of existing results, not a new fitted monetary-effect interval.

   Proposed replacement for the sentence fragment:

   > with a mean of $222.47 of room for agreement, the larger absolute 90%
   > interval bound corresponds to about $1.70 per deal.

   This replaces “with about $220 of room in a typical negotiation, any effect
   is below about $2 per deal.” The original approximations are conservative;
   the requested replacement makes their calculation explicit.

2. **Bonferroni remark.** There are **29 pooled secondary permutation tests**
   in Study 1: rows with `scope=pooled`, `designation=secondary` and an available
   permutation p-value. This includes adjusted offers and belief outcomes;
   it excludes primary P1, model-specific tests and bootstrap-only coefficient
   changes. The corrected threshold is **0.05/29 = 0.00172413793103448**.
   The own-minus-other proposer and responder p-values are respectively
   **0.0000999900009999** and **0.000399960004**. **Both remain significant.**

   Proposed replacement for the final Bonferroni sentence:

   > Both main ultimatum results remain significant at the corrected threshold
   > of 0.05/29 ≈ 0.00172 (p ≈ 0.00010 and 0.00040), although this check was not
   > part of our pre-registration.

   The underlying 29 saved rows are copied in
   `bonferroni-pooled-secondary.csv`; no tests were added or rerun.

## Numeric or scope corrections

3. **Proposer interval rounding.** The saved upper 95% endpoint is **$4.175**.
   Proposed: “95% CI $1.85 to **$4.18**” instead of “$1.85 to $4.17.”
   The latter is a binary-floating-point formatting artifact. Other exact
   half-cent values in the notes, −0.625 and 3.125, round to −0.62 and 3.12
   under decimal ties-to-even; the exact values are retained in the audit.

4. **Comprehension scope.** The 320 calls comprise 240 scored calls and 80
   undisclosed calls. All models scored 20/20 on each of own-model, other-lab
   and fictional cards. All undisclosed answers were “unsure” and unscored.

   Proposed replacement for “every model answered correctly in all 20 calls
   for every card”:

   > every model answered correctly in all 20 calls for each of the three
   > scored cards; “not disclosed” answers were unsure and unscored.

5. **Public availability.** GitHub reports `sambitmukherjee/kin-loyalty` as
   **PRIVATE**. The claim that every logged call is public is not currently
   verifiable and conflicts with the current repository visibility. No
   visibility setting was changed. Either authorize a separate public release,
   or approve a corresponding availability statement. A text-only alternative
   is “An auditable protocol, with prompts, pre-registrations and result tables
   provided in the supplementary material.” This alternative does not claim
   that raw API logs are included in the supplement.

## Reference corrections / unresolved source

6. **Jin → Choi.** Proposed body citation: “Choi et al. (2025)” rather than
   “Jin et al. (2025).” Full verified author order: Younwoo Choi, Changling Li,
   Yongjin Yang, Zhijing Jin. The explicitly requested full author list is in
   `references.bib`; the original literal body citation remains pending approval.

7. **Liu title.** The supplied arXiv identifier has the title recorded in
   `reference-verification.md`, not “Faithful Delegates? Benchmarking the
   Fiduciary Duties of LLM Negotiating Agents.” Approve the verified title or
   provide the intended source; the draft title remains in this proof.

8. **Historical benchmark.** Provide an archived mid-November 2026 Artificial
   Analysis v5.0.1 source for scores 55, 54, 51 and 46, or approve a change to
   that reference/table. The live index is now v5.0.2. No scores were guessed
   or replaced. Lee's stated title was verified specifically in arXiv v1 and
   the bibliography is pinned to that version.

## Other author-review items; not silently edited

9. **Recorded mechanical deviation.** The post-registration Study 2 execution/
   dual-provenance patch was previously approved and logged. The registration
   requires reporting it in the paper; the draft does not explicitly do so.
   Proposed sentence for Pre-registration:

   > After registration, an approved mechanical patch enabled the Study 2 main
   > run and recorded both registration and execution commits; the analysis,
   > prompts and scoring were unchanged.

10. **Descriptive S1 language.** “The lower offers are fully explained by lower
    expectations” is stronger than the registered descriptive interpretation.
    The adjusted estimate is +$0.0830, 95% interval −$0.6993 to +$0.8522,
    p=0.80292. Proposed: “After controlling for stated expectations, the offer
    contrast is near zero (+$0.08); this is a descriptive association, not a
    causal explanation.” This is an interpretation concern, not a numerical
    mismatch. No sentence was changed.

No substantive cuts have been made. Page count and conversion details are
recorded in `typesetting-report.md` after visual inspection.
