# AAAI-27 typesetting report — paper and approved appendices

This report records the earlier appendix correction pass. The subsequent
author-approved title update and current PDF checks are recorded in the
[title-change report](title-change-report.md).

## PDF and build

- **34 pages total**, down from 37 before the appendix correction pass.
  The unchanged main text ends on page 4; references end on page 5. The main
  paper plus references remains five pages. Appendices occupy pages 5–34,
  or **30 pages including shared page 5**, down from 33.
- PDFLaTeX, TeX Live 2026 and BibTeX use the official AAAI-27 Author Kit from
  <https://aaai.org/authorkit27/>. All 17 extracted kit files, including the
  style and bibliography style, match the downloaded archive byte for byte.
- US Letter, two columns and PDF 1.7. No margin, font-size, leading or
  float-spacing overrides, forbidden package or manual page break was added.
- **Zero LaTeX errors, overfull boxes or undefined citations/references.**
  All **15 fonts** are embedded Type 1. No Type 3, CID or Identity-H fonts occur.
  Figure lettering remains vector outlines. `font-audit.txt` records pdffonts.
- **1,079,781 bytes**, with 107 appendix tables and eight registered vector figures.
  All 1,959 displayed result cells remain traceable to unchanged saved sources.
- Every appendix page was visually inspected. No split listing, separated
  caption, clipping, overlap or missing glyph was found. Some native float and
  column whitespace remains, especially on prompt pages; the request to remove
  every large gap is not fully met. Ordinary underfull-box messages remain.

For this pass, the draft, main LaTeX source, bibliography and Figure 1 are
byte-identical to commit `76823a6dd130e79f9dafe878b32cfeb1824efa91`.
Extracted PDF text through the final reference is identical; pages 1–4 are also
pixel-identical. Earlier author-approved wording and the Table 1 heading are
unchanged in this pass. The copied prompts, study methods and all scientific
source files remain unchanged. No analysis was run.

`appendix/fix-pass-report.md` records every requested item, old/new location,
fact check and display change, including the remaining layout limitation.
The PDF SHA-256 is `ddb20d79aeb44cb6f9672d92e7d395ca250d72063042114ee66741ddb1a78c46`.

Build command, from the repository root:

```sh
bash paper/build.sh
```

## Approved corrections applied

The author approved the proposed edits on **2026-11-27**, including removal
of Liu (2026) and correction of Jin et al. to Choi et al. The initial instruction
to retain unverified historical Intelligence Index scores was superseded by a
later explicit request to use the supplied November 27 chart and official web
source. The author made the repository public; GitHub visibility was verified
**PUBLIC**. Its public-audit wording is retained. The agent did not change
repository visibility.

`applied-edits.json` records every exact replacement against initial proof
commit `495f4909d8a841eb1bff28969c9ff1abd0e8721e`. Validation reconstructs the
revised draft using only those recorded replacements. `proposed-edits.md`
records the disposition of all ten proposals. No other body prose was changed.

| Item | Saved/computed value | Applied wording or correction |
| --- | --- | --- |
| Mean room for agreement, all 960 episodes | **$222.46875** | Mean **$222.47**. |
| Larger absolute 90% bound | **0.007658102208929781** share units | Used unchanged for the requested dollar calibration. |
| Mean room × bound | **$1.7036884257928472** | **About $1.70 per deal**, explicitly a calibration of the interval. |
| Pooled Study 1 secondary tests | **29** | Threshold **0.05/29 ≈ 0.00172**; the main ultimatum p-values, approximately **0.00010** and **0.00040**, both pass. The non-preregistered caveat is retained. |
| Proposer upper 95% endpoint | **$4.175** | **$4.18**. The separate GPT dictator estimate of $4.17 less is unchanged. |
| Comprehension scope | 240 scored calls; 80 undisclosed calls unscored | All scored calls correct; undisclosed answers unsure and unscored. |

The causal wording about human-counterparty offers was replaced by the approved
sentence describing the adjusted estimate (+$0.08) as a descriptive association.
The approved post-registration mechanical execution/provenance patch is now
explicitly disclosed; analysis, prompts and scoring were unchanged.

Exact arithmetic, source hashes and 43 checked claims/groups remain in
`numeric-audit.json`. Its source-file hashes match the initial proof's audit.
Other reported sample sizes, frequencies, point estimates, intervals and
significance statements match the saved results at their stated precision.
The observed pair-mean range is 0.499779343 to 0.774597271; the two-by-two cell
range is 1.41575299 percentage points. The reported approximations of 0.50–0.77,
at most 1.5 points and about 100 times P2 are consistent with those values.
No statistical tests were added or rerun.

## References

**Sixteen references remain.** Full authors, identifiers and verification URLs
are recorded in `reference-verification.md`. The three dagger-marked references
(Hofstadter, Lakens, Schelling) were verified.

- **Choi attribution applied:** the body now cites **Choi et al. (2025)**
  through BibTeX. The bibliography contains all four verified authors in order:
  Younwoo Choi, Changling Li, Yongjin Yang and Zhijing Jin.
- **Liu removed:** no Liu citation or reference remains in the main paper.
  The earlier source discrepancy is retained only in the audit history.
- **Intelligence Index updated:** Table 1 is labelled **v5.0.2**, with
  **Claude 55, Gemini 54, GPT 51 and Kimi 47**, read from the author-supplied
  November 27, 2026 chart. Only Kimi's number changes (46 → 47). A citation now
  accompanies the benchmark description; the printed reference includes the
  official source URL and observation date. The unmodified chart, its hash and
  selected labels are preserved in `sources/`. This does not retrospectively
  verify the superseded v5.0.1 values or alter the study's model settings.
- Lee's title is verified for **arXiv v1**; the bibliography remains pinned to
  that version.

## Conversion details

- The final Notes for typesetting section is omitted. Export timestamp/handle
  are replaced by the requested author and affiliation. Reference-list editorial
  warnings/daggers are omitted after checking.
- Citations use the kit's author–year style; the pending Jin/Choi attribution
  issue is resolved.
- Figure 1 is drawn directly from the 15 registered contrast rows. The common
  x-axis is −12 to +16 dollars. Model rows are grey; pooled rows use one accent
  colour, bold labels and outlined markers. Panel labels identify the decisions,
  with no overall title inside the figure. The exported chart label supplies
  the unchanged caption.
- The draft's three tabular blocks are retained. The model and mean-surplus
  tables are numbered Tables 1 and 2; the Section 5 design matrix is unnumbered.
  Existing “Models.” and “Mean buyer surplus share” labels supply the captions.
- The repository placeholder uses the project's URL in the kit's resource-links
  block, as the original notes requested. The repository is now public.
- The requested source filename is `main.tex`. The guide's family-name naming
  convention can be handled when preparing a camera-ready source upload.

## AI-tool statement

**No AI-tool-use disclosure paragraph is required by the downloaded kit.** Its
Ethical Statement is explicitly optional and unnumbered. No disclosure prose
was invented or added. Separate AAAI policies retain author responsibility;
this audit does not claim to verify additional workshop-specific declarations.

## Supplement and preservation

`supplementary-material.zip` contains **79 unchanged source artifacts**, plus
a README and checksum manifest: prompt/card sources and configurations, both
pre-registrations and locks, the decision log, full numeric result tables and
the remaining preregistered figures. It is **834,572 bytes**, below 50 MB, and
contains no raw API logs or credentials. It is unchanged from the initial proof.

No study code, data, result file or pre-registration was modified, and no study
analysis was rerun. All revisions and generated audits are confined to
`paper/`. The approved revision and appendices are prepared for a paper-only local commit.
Nothing is pushed.
