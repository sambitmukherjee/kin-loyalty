# Author-approved edits — applied

The author approved the proposed edits on 2026-11-27, with explicit instructions
to remove Liu (2026), retain the unverified Intelligence Index scores, and
correct Jin et al. to Choi et al. The author also made the repository public.
`applied-edits.json` records every exact replacement against the initial proof
commit; `numeric-audit.json` retains the computations and source hashes.

| Original proposal | Final disposition |
| --- | --- |
| 1. Room for agreement | Applied: mean **$222.47** over all 960 negotiations, and a larger-absolute-bound calibration of **about $1.70 per deal**. Exact values are $222.46875 and $1.7036884257928472; the saved 90% bound is 0.007658102208929781. |
| 2. Bonferroni check | Applied: **29** pooled secondary permutation tests, **0.05/29 ≈ 0.00172**, with p ≈ 0.00010 and 0.00040. Both pass; the non-preregistered caveat is retained. No tests were added or rerun. |
| 3. Proposer interval rounding | Applied: the upper endpoint **$4.175** is reported as **$4.18**. The separate GPT dictator estimate of $4.17 less is unchanged. |
| 4. Comprehension scope | Applied: all 240 scored calls were correct; the 80 undisclosed answers were unsure and unscored. |
| 5. Public availability | Resolved by the author making the repository public. GitHub reports **PUBLIC**. The original public-audit wording is retained; the proposed alternative availability sentence is unnecessary and was not inserted. The agent did not change visibility. |
| 6. Jin → Choi | Applied through the kit's author–year citation style. The full verified author list is Younwoo Choi, Changling Li, Yongjin Yang and Zhijing Jin. |
| 7. Liu title discrepancy | Superseded by the author's explicit instruction: **remove Liu (2026) from the main text and bibliography**. No substitute paper was inserted. |
| 8. Historical Intelligence Index | Scores **55, 54, 51 and 46** and the historical v5.0.1 description remain unchanged and **unverified**, at the author's explicit instruction. Lee's reference remains pinned to verified arXiv v1. |
| 9. Mechanical deviation | Applied: the paper discloses the approved post-registration execution/provenance patch and states that analysis, prompts and scoring were unchanged. |
| 10. Descriptive S1 language | Applied: the adjusted offer contrast is described as near zero (+$0.08), with an explicit descriptive, noncausal interpretation. |

No substantive cuts were made. Study code, data, results and preregistrations
were not modified. Final page count and rendering checks are recorded in
`typesetting-report.md` and `validation.json`.
