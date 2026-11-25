# Phase 5 — analysis, reports, and reproduction

**Historical verification report.** Later pre-pilot clarifications replaced the
original basic intervals/null-centered TOST below with count-matched percentile
intervals and raw-tail TOST. Current specifications are in `analysis.md` and
`preregistration/study1.md`; the decision log records the approved changes.

Phase 4b commit `3fd70c5` was pushed before this phase, as requested. Phase 5
implements the complete Study 1 analysis and validates it only on simulated
data. No additional provider calls were made or observed pilot outcomes analyzed.
No real main data, main manifest in the study data folder, or pre-registration
lock were created.

## Implemented work

- Saved-log loading with phase/backend separation, validation of frozen
  requests and complete attempt histories, exclusion/re-ask accounting, and
  rejection of pending, missing, duplicated, or altered work.
- Model-specific label regressions with paraphrase fixed effects, equally
  weighted pooled contrasts, all prespecified secondary contrasts, and S1
  offer/belief analysis with paired resampling and separate model belief slopes.
- Configured 10,000-draw stratified bootstrap intervals, 10,000 contrast-specific
  permutations, Freedman–Lane adjusted permutations, and always-reported pooled
  P1 bootstrap TOST against ±$5.
- Descriptive, exclusion/re-ask, reasoning/token/cache, and comprehension tables.
  Pilot reporting pools labels and never computes a pilot outcome contrast.
- Main distributions, responder distributions, S1 coefficients, and optional
  comprehension-table figures, each in PDF and PNG. Synthetic figures identify
  their data as simulated.
- A common analysis/reproduction entry point, mock-batch generation, saved
  resampling distributions, source/input/config provenance, and artifact hashes.

The researcher explicitly approved bootstrap TOST, tested-pair permutations,
Freedman–Lane S1 permutations, and model-specific belief slopes through the
clarification questions. Exact conventions and primary sources are documented
in [analysis.md](analysis.md) and recorded in the decision log. The output
contracts are in [data_dictionary.md](data_dictionary.md).

## Files

| Files | Role |
| --- | --- |
| `src/kinloyalty/analysis/loading.py` | Saved-history validation, status/decision extraction, strict eligibility |
| `analysis/inference.py` | Fixed-effect fitting, paired cell bootstrap, label/residual permutation, TOST |
| `analysis/pipeline.py` | Coverage gates, all estimates, CSV/NPZ outputs, provenance and artifact hashes |
| `analysis/reports.py` | Descriptives, attempt/usage diagnostics, blind pilot report, comprehension scoring |
| `analysis/figures.py` | Deterministic paper-size PDF/PNG figures |
| `analysis/simulate.py`, `analysis/__init__.py` | Explicitly synthetic mock batches and module documentation |
| `src/kinloyalty/cli.py` | `analyze study1`, `reproduce`, `report`, and `simulate-study1` commands |
| `configs/study1.yaml` | Approved analysis conventions; original seeds, counts, hypotheses, and bounds retained |
| `tests/test_analysis.py` | 23 statistical, eligibility, history, reporting, CLI, and reproduction tests |
| `README.md`, `results/study1/README.md`, `docs/analysis.md`, `docs/data_dictionary.md`, `docs/decisions.md`, this report | Commands, methods, artifacts, decisions, checks, and remaining scope |

No dependency/lock, model/API setting, schema, prompt, or existing live log was
changed. All generated verification batches/results are outside the project's
real data/results roots.

## Verification

Run the offline tests with:

```sh
.venv/bin/pytest
```

The full suite passed **275 tests**, including **23 new analysis tests**.
Independent statsmodels fits agree with both unadjusted and belief-adjusted
coefficients under unequal cell counts. Tests cover an enumerable permutation
null, null-centered TOST boundaries, joint offer/belief resampling, equally
weighted models with different retained counts, rank/empty-cell failures,
API-error versus exclusion accounting, missing usage, incomplete comprehension,
phase/backend/synthetic gates, altered/duplicate/pending logs, blind pilot
reporting, planted-effect recovery, and byte-identical output reproduction.

Two full 3,600-draw synthetic main batches were also generated through the
ordinary mock client and durable runner. Each had its own 240-draw mock pilot
and 320-draw mock comprehension batch. Every contrast used the actual configured
10,000 bootstrap and permutation draws, rather than the smaller unit-test counts.

| Simulated own-model effect | Pooled P1 estimate | Basic 95% interval | Two-sided permutation p | TOST equivalence within ±$5 |
| --- | ---: | --- | ---: | --- |
| $12 | $12.4875 | [$11.4583, $13.5333] | 0.00009999 | No (`p_tost = 1`) |
| $0 | $0.4875 | [−$0.5417, $1.5333] | 0.3759624 | Yes (`p_tost = 0.00009999`) |

These are software-verification results, not evidence about the named models.
The same-input full-size `analyze study1` and `reproduce` runs produced identical
artifact hashes, including the saved resampling distributions and PDF/PNG files.
Visual review led to spacing the comprehension title and S1 legend away from
their data. Final checks re-rendered those figures and reran the offline suite.
Wheel/source builds and archive checks verify inclusion of the new analysis
modules and exclusion of credentials/local instruction files.

Verification workspace for this session:
`/private/tmp/kin-loyalty-phase5.kwqp6ave`. Final planted-effect outputs are in
`final-results/`; full-size null verification outputs are in
`verified-null-results/`. These temporary artifacts can be regenerated using
the commands in `analysis.md`; they are not committed as study observations.

## Commands to review

The full demonstration and report commands are in `analysis.md`. After choosing
new temporary directories, they generate mock logs and reproduce all outputs
without keys. `kinloyalty --help` lists the implemented commands. Existing output
directories are preserved; select a new one for another reproduction.

Real main results do not exist. The ordinary reproduction command therefore
stops on missing input today; it cannot invent paper results. A future observed
run must have every planned draw terminal before inference is allowed.

## Remaining work and phase gate

Phase 5 ends with a local commit, without a new push. Phase 6 would prepare and
execute the separately approved **240 pilot + 320 comprehension draws** and
report their mechanical checks. Under the current policy the worst-case upper
bound is **4,480 HTTP attempts** across those 560 draws, including retries and
re-asks; additional invocations/resumes would need explicit authorization.

Kimi's missing smoke cache-read count remains an open metadata limitation,
documented in `phase4b_report.md`. It must be reviewed before the pilot; the
analysis preserves missing counts rather than imputing zero. No mechanical
fix, extra live probe, or acceptance of this limitation was inferred from the
approval of the offline analysis phase.

The pilot/comprehension run, any resulting fixes, the pre-registration lock,
and the actual main run remain subject to their established separate approvals.
