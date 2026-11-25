# Study 1 results

The saved-log pipeline generates deterministic CSV tables and matplotlib PDF/PNG
figures, with source/input hashes and saved resampling distributions. No observed
main results exist yet. Temporary synthetic verification artifacts stay outside
this directory and the real study data folders.

`kinloyalty reproduce --data data/study1/main --comprehension
data/study1/comprehension --output results/study1/generated` will regenerate
everything when those logs exist. It requires no API keys and refuses to
overwrite an existing output directory. See `docs/analysis.md` for an offline
mock demonstration and `docs/data_dictionary.md` for each output contract.

Pilot reports are separate and pool all labels. Comprehension reporting uses its
own batch. Neither enters the main decision analysis.

Observed Phase 6 reports are now in `pilot-report/` and `comprehension-report/`.
The pilot report contains pooled distributions and mechanics only. The separate
comprehension table shows all four models passing. Read `docs/phase6_report.md`
for the all-zero dictator floors and constant-offer review flags before any fix
or subsequent live run is considered.
