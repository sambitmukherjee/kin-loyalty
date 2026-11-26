# Study 2 results

`smoke-report/` contains mechanical diagnostics only:

- `smoke_audit.json`: counts, model-version/schema checks, usage/stop/cache
  availability, clean-code provenance, and replay status.
- `usage_calls.csv`: provider-reported usage for each of the 51 smoke calls.
  Blank counts represent unavailable/null fields, never imputed zeros.
- `probe-report.json`: the sixteen unscored forced-position probes, including
  complete system/user requests and original transcript prefixes.
- `smoke-report.md`: the exact generated mechanical report and four shared
  transcript prefixes.
- `artifacts.sha256.json`: digests of preserved raw/report artifacts and phase
  documentation, excluding the inventory itself.

Raw calls and terminal summaries are under `data/study2/smoke/`. The enriched
phase report is `docs/study2_phase4_report.md`. No smoke/probe data are eligible
for hypothesis analysis. No analysis has been run on real Study 2 or Study 1
main data; Phase 5 writes/tests the analysis using synthetic logs only.
