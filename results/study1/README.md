# Study 1 results

The saved-log pipeline generates deterministic CSV tables and matplotlib PDF/PNG
figures, with source/input hashes and saved resampling distributions. Main
collection is complete, but no observed main analyses have been produced.
Analysis is deferred until the Study 2 addendum is committed. Temporary synthetic
verification artifacts stay outside
this directory and the real study data folders.

`kinloyalty reproduce --data data/study1/main --comprehension
data/study1/repilot_20261126/comprehension --output results/study1/generated` will regenerate
everything after that addendum is committed. It requires no API keys and refuses to
overwrite an existing output directory. See `docs/analysis.md` for an offline
mock demonstration and `docs/data_dictionary.md` for each output contract.

Pilot reports are separate and pool all labels. Comprehension reporting uses its
own batch. Neither enters the main decision analysis.

Observed Phase 6 reports are now in `pilot-report/` and `comprehension-report/`.
The pilot report contains pooled distributions and mechanics only. The separate
comprehension table shows all four models passing. Read `docs/phase6_report.md`
for the all-zero dictator floors and constant-offer review flags before any fix
or subsequent live run is considered.

The approved pre-lock system-sentence removal and fresh pilot/check are reported
in `repilot_20261126/pilot-report/` and
`repilot_20261126/comprehension-report/`. All 240 pilot and 320 comprehension
draws were valid in 560 attempts; all four models passed comprehension at 20/20
in every scored condition. Use this final-prompt check for the eventual paper.
The original reports remain historical audit artifacts. Read
`docs/repilot_20261126_report.md` for full pooled distributions, the original
Gemini constant-$40 observation, and the fixed stopping rule. No pilot label
comparisons or main inference were computed.

Main collection mechanics are saved separately at
`data/study1/main/collection_counts.csv` and described in
`docs/study1_main_collection_report.md`. All 3,600 draws completed valid, with
zero invalid replies, re-asks, exclusions, or unfinished draws. These are
collection-status counts only; no outcome summaries or main-analysis artifacts
have been created in this results directory.
