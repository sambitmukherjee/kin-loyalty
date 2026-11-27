# AAAI-27 typesetting report — author-review proof

## PDF and build

- **Five pages total.** Main text ends on page 4; References begin on page 4
  and continue onto page 5. This fits approximately four content pages plus
  references. **No cuts are needed and none were made.**
- Compiled with **pdflatex**, TeX Live 2026, and BibTeX using the official
  AAAI-27 Author Kit from <https://aaai.org/authorkit27/>. All 17 extracted kit
  files, including `aaai2027.sty` and `aaai2027.bst`, match the downloaded ZIP
  byte-for-byte. See `author-kit-manifest.json`.
- US Letter, two columns, PDF 1.7. No margin, font, leading or float-spacing
  overrides; no forbidden package. The card uses the kit's nine-point
  monospace size. Table columns use ordinary paragraph alignment without
  shrinking the font or intercolumn spacing.
- **Zero LaTeX errors, zero overfull boxes, zero undefined citations.**
- `pdffonts` confirms all **eight** remaining fonts are embedded. No Type 3,
  CID or Identity-H font remains. Figure lettering is vector outlines,
  preserving the original glyph shapes and point sizes. `font-audit.txt`
  retains the command's output.
- All five rendered pages were visually inspected, along with a greyscale
  rendering of Figure 1: no overlaps, clipped text, unreadable labels or
  missing glyphs were found.

Build command, from the repository root:

```sh
bash paper/build.sh
```

## Requested computations and proposed edits

The draft's body prose and numbers remain unchanged. Exact checks, source hashes
and 43 checked claims/groups are in `numeric-audit.json`. The following edits
are proposed for author approval; full replacement wording is in
`proposed-edits.md`.

| Item | Saved/computed value | Proposed action |
| --- | --- | --- |
| Mean room for agreement, all 960 episodes | **$222.46875** | Replace the estimated $220 with a stated mean of **$222.47**. |
| Larger absolute 90% bound | **0.007658102208929781** share units | Retain the existing rounded interval; use this exact bound for the requested dollar calibration. |
| Mean room × bound | **$1.7036884257928472** | Replace the rough $2 calibration with **about $1.70**, worded as a calibration of the interval rather than a newly fitted dollar-effect interval. |
| Pooled Study 1 secondary tests | **29** | State the count and **0.05/29 = 0.00172413793103448** threshold. Both main ultimatum p-values, **0.0000999900009999** and **0.000399960004**, pass. Retain the post hoc/non-preregistered caveat. |
| Proposer upper 95% endpoint | **$4.175** | Propose **$4.18**, replacing $4.17. |
| Comprehension scope | 240 scored calls; 80 undisclosed calls unscored | Replace “every card” with the three scored cards; disclose the unscored “unsure” responses. |

Other reported sample sizes, frequencies, point estimates, intervals and
significance statements match the saved results at their stated precision.
The observed pair-mean range is 0.499779343 to 0.774597271; the two-by-two cell
range is 1.41575299 percentage points. The reported approximations of 0.50–0.77,
at most 1.5 points and about 100 times P2 are consistent with those values.

Two additional author-review issues are recorded without editing the paper:
the GitHub repository is currently **PRIVATE**, contrary to the current public-
audit claim; and the already approved post-registration execution/provenance
patch should be explicitly disclosed in the paper as required by the decision
log. The stronger causal wording “fully explained” in S1 also exceeds the
registered descriptive interpretation. See proposals 5, 9 and 10.

## References

All 17 draft references were checked. The three dagger-marked references
(Hofstadter, Lakens, Schelling) were verified. Full authors, identifiers and
verification URLs are recorded in `reference-verification.md`.

- **Jin attribution:** the correct ordered authors are **Younwoo Choi,
  Changling Li, Yongjin Yang and Zhijing Jin**. The full list is in the BibTeX
  entry. The original literal body citation is retained pending approval to
  replace “Jin et al.” with **“Choi et al.”**
- **Liu title mismatch:** arXiv:2607.02814 is titled
  “SovereignNegotiation-Bench: Evaluating User-Owned Personal Agents In
  Delegated Bargaining Under Privacy, Consent, Evidence, And Institutional
  Pressure,” not the supplied “Faithful Delegates?” title. The supplied title
  remains provisional; the author must approve the corrected title or identify
  the intended different source.
- **Historical Intelligence Index:** the v5.0.1 mid-November scores
  **55/54/51/46 remain unverified**. The current site is v5.0.2. No replacement
  scores were inferred. A dated screenshot/export or archived source is needed.
- Lee's draft title is correct for **arXiv v1**, not the retitled latest
  version. The bibliography pins v1.

## Conversion details

- Removed the final Notes for typesetting section. Export timestamp/handle
  were replaced by the requested author and affiliation. The reference-list
  editorial warning/daggers are not paper prose and were omitted after checking.
- Converted the existing citations to the kit's author–year style, with the
  one deliberately literal pending Jin/Choi correction noted above.
- Redrew Figure 1 directly from the 15 registered contrast rows. The common
  x-axis is −12 to +16 dollars. Model rows are grey; pooled rows use one accent
  colour, bold labels and outlined markers. There is no overall figure title;
  panel labels identify the decisions. The only supplied caption was the
  exported embedded-chart label; its wording is retained in the caption.
- The draft actually contains **three tabular blocks**. The requested model
  table and mean-surplus table are numbered Tables 1 and 2. The Section 5 design
  matrix is retained as an **unnumbered** block, so no design text is cut.
  Existing “Models.” and “Mean buyer surplus share” labels supply the table
  captions rather than invented caption sentences.
- The repository placeholder was replaced by the supplied project's URL in
  the kit's resource-links block, as the notes request. Its private visibility
  is an unresolved availability issue, not something changed by typesetting.
- The source is named `main.tex` as explicitly requested. The guide's general
  family-name naming convention can be handled when preparing an actual
  camera-ready source upload.

## AI-tool statement

**No AI-tool-use disclosure paragraph is required by the downloaded kit.** Its
Ethical Statement is explicitly optional and unnumbered. No disclosure prose
was invented or added. Separate AAAI author policies retain author
responsibility and restrict AI authorship; any additional workshop-specific
declaration must be checked against that workshop's instructions.

## Supplement and preservation

`supplementary-material.zip` contains **79 unchanged source artifacts**, plus
a README and checksum manifest: all prompt/card sources and configurations,
both pre-registrations and locks, the decision log, full numeric result tables,
and the remaining preregistered figures. It is **834,572 bytes**, below 50 MB.
It contains no raw API logs or credentials.

No study code, source data, result file or pre-registration was modified, and
no study analysis was rerun. All work and generated audits are confined to
`paper/`. This proof and its proposed edits are prepared for a paper-only local
commit. Nothing is pushed. Author approval is required before applying the
proposals and rebuilding the final version.
