# AAAI-27 workshop paper with technical appendices

`main.pdf` typesets `draft.md` with the official AAAI-27 Author Kit, downloaded
from <https://aaai.org/authorkit27/>. `main.tex` is generated from the draft;
the final “Notes for typesetting” section is omitted. The author approved the
recorded corrections on 2026-11-27. Author: Sambit Mukherjee; affiliation:
Independent Researcher. `applied-edits.json` records every approved draft
replacement; `proposed-edits.md` records its disposition.

The approved technical appendices A–H follow the references in the same PDF.
The main text, bibliography and Figure 1 are unchanged from commit `15429f6`.
The main paper and references still occupy five pages. The complete PDF has
37 pages; the appendices occupy pages 5–37, sharing page 5 with the final
references. They explain the registered methods in plain language and include
the complete saved result tables, exact prompt templates and registered figures.

Build from the repository root:

```sh
bash paper/build.sh
```

Requirements: PDFLaTeX and BibTeX (TeX Live 2026 used here), Pandoc, and the
repository's existing Python/Matplotlib environment. The appendix vector assets
are committed, so a normal build need not regenerate them. `PAPER_PYTHON` may select
an equivalent Python environment. A portable TinyTeX installation, if present
under `.toolchain/TinyTeX`, is used locally; no study dependency was changed.
That optional toolchain and build intermediates are ignored by Git.

The official archive is `aaai27-author-kit.zip`; its SHA-256 is
`9406a545d5d213757245eb37118fe652b2fccf64f555aff28b49ebe2a780c960`.
All extracted files under `author-kit/AuthorKit27/`, including `aaai2027.sty`
and `aaai2027.bst`, are unmodified. The build puts local manuscript figures
before kit example figures on the TeX search path.

Figure 1 is drawn by `figures/make_figure1.py` from the existing Study 1
contrast CSV, without fitting or resampling. It is a seven-inch-wide vector
PDF. Nine-point-or-larger lettering is converted to vector outlines to avoid
the kit's prohibited CID/Identity-H and Type 3 fonts.

Re-run requested arithmetic checks with:

```sh
.venv/bin/python paper/check_numbers.py
.venv/bin/python paper/make_supplement.py
```

`numeric-audit.json`, `reference-verification.md`, `conversion-audit.json`,
`validation.json` and `typesetting-report.md` document checks and author
decisions. The supplement ZIP contains the requested unchanged source artifacts,
tables and figures; it excludes raw API logs and credentials.

`appendix/build_tables.py` generates 135 appendix tables from saved results and
metadata, without fitting models or resampling. The appendices preserve 28 exact
prompt-template files and the registered Study 1 card block. Display wrapping
adds line breaks only, with a reversible source map. Eight registered vector
figures have presentation copies with enlarged, outlined lettering; the source
results are unchanged. See `appendix/README.md`, `appendix/source-map.md` and
`appendix/report.md` for the workflow, provenance and final checks.

The manuscript now cites Choi et al. with the full verified author list in
the bibliography. Liu (2026) is removed from both text and references. The
Intelligence Index table now uses v5.0.2 values from the author-supplied chart
of 2026-11-27: Claude 55, Gemini 54, GPT 51 and Kimi 47. The table cites Artificial
Analysis, and the bibliography prints the official source URL and observation
date. `sources/` preserves the supplied chart, its hash and the selected labels
and values. This supersedes the earlier instruction to retain unverified
historical scores. GitHub visibility was verified PUBLIC; the agent did not
change repository visibility. No study files were modified.
