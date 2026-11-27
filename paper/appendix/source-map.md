# Appendix source map

This map identifies the source of explanatory prose and protocol numbers.
Result-table cell values have the more detailed machine-readable trace in
`number-trace.json`; prompt bytes and display wrapping have separate manifests.
The prose explains the registered procedures in new wording without adding an
analysis or changing a method. It does not infer a causal mechanism from the
results.

| Appendix | Sources and scope |
| --- | --- |
| A | Git targets and annotations for `prereg-study1`, `study1-data`, `prereg-study2`, `study2-data`; `.python-version`; `uv.lock`; reproduction commands in `preregistration/study1.md` and `preregistration/study2.md`; existing audits in `results/study1/reproducibility.json`, `results/study2/reproduction-check.json` and their results READMEs. Dates distinguish commit creation from tag annotation and remote publication. |
| B | `configs/models.yaml`; Study 1 registration Section 2; Study 2 registration Section 2; returned strings in `results/study1/generated/decisions.csv` and `results/study2/main/tables/usage_calls.csv`; both `usage_summary.csv` files. Requested caching is distinguished from observed and missing usage. |
| C | All `prompts/study1/*.txt`; `prompts/study1/README.md`; `configs/study1.yaml`; Study 1 registration Sections 3–6 and Appendix A. The card-construction block is copied exactly from its Section 3 fence. All wordings, name pairs, allocation counts and comprehension rules are fixed sources. |
| D | All `prompts/study2/*.txt`; `configs/study2.yaml`; Study 2 registration Sections 3–5; `src/kinloyalty/negotiation/transcript.py` and `prompts.py` for literal rendering confirmation. Items and prices in the displayed table are read from `results/study2/main/tables/episodes.csv`. |
| E | Study 1 registration Section 7, including the detailed TOST, permutation, S1 and numerical-tolerance subsections; Study 2 registration Section 7; `docs/analysis.md` and `docs/study2_analysis.md`. No methods or seeds are changed. The methods describe approximate resampling inference and retain its registered interpretation limits. |
| F | `docs/decisions.md`; Study 1 registration Section 5; Study 2 registration Sections 8–9; `docs/phase6_report.md`, `docs/repilot_20261126_report.md`, `docs/study2_phase4_report.md`, `docs/study2_phase6_report.md`, `docs/study2_phase7_report.md`, `docs/study2_main_execution_patch.md`; `results/study2/README.md`. Blind summaries are copied from saved pilot CSVs and never compare disclosure conditions. The only actual post-Study-2-lock code amendment recorded in the decision log is the explicitly approved execution/dual-provenance extension, not a scientific change. Registered Study 1 retry/resumption is identified separately from an amendment. |
| G | Every row of `results/study1/generated/contrasts.csv`; `equivalence.csv`, `s1_coefficient_changes.csv`, `s1_belief_diagnostics.csv`, `s1_belief_cell_counts.csv`, `descriptives.csv`, `comprehension.csv`; all four registered PDF figures. The pooled primary row and secondary rows are distinguished; no results are selected for significance. |
| H | Every row of `results/study2/main/tables/contrasts.csv`; saved TOST and robustness outputs in `metadata.json`; `outcome_eligibility.csv`, both mandate tables, `pair_condition_descriptives.csv`, `pooled_descriptives.csv`, `actual_kinship_means.csv`; all four registered PDF figures. Every permutation test has complete and incomplete stratum counts with the one/neither split. |

All referenced study files remain unchanged. The figure treatment changes only
presentation: the source data geometry and saved estimates are preserved.
Study reproducibility claims refer to the existing recorded checks, with their
provenance-metadata exceptions, rather than a new execution of either analysis.


The appendix correction pass is checked against commit `76823a6`. Its factual
checks and sources are recorded in `fix-verifications.json`; every item and its
old/new location appears in `fix-pass-report.md` and `fix-locations.json`.
Comprehension CSV counts were compared with the registered figure before the
four duplicate tables were removed. Repeated Study 2 counts were condensed
only after equality assertions, whose rows are retained under generated
statements in `number-trace.json`. Numeric formatting uses Decimal half-even;
the exact 1/240 claim applies only to unadjusted pooled Study 1 contrasts and
endpoints, not belief-adjusted regression coefficients. Per-pair message means
use their exact denominator of 20. No result calculation was rerun.
