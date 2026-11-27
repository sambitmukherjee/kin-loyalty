# AAAI-27 workshop paper — proof awaiting author approval

`main.pdf` typesets `draft.md` with the official AAAI-27 Author Kit, downloaded
from <https://aaai.org/authorkit27/>. `main.tex` is generated from the draft;
the final “Notes for typesetting” section is omitted. The prose and numeric
claims have not been corrected or cut. Author: Sambit Mukherjee; affiliation:
Independent Researcher. Proposed corrections are in `proposed-edits.md`.

Build from the repository root:

```sh
bash paper/build.sh
```

Requirements: PDFLaTeX and BibTeX (TeX Live 2026 used here), Pandoc, and the
repository's existing Python/Matplotlib environment. `PAPER_PYTHON` may select
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
`validation.json` and `typesetting-report.md` document checks and unresolved
items. The supplement ZIP contains the requested unchanged source artifacts,
tables and figures; it excludes raw API logs and credentials.

The proof keeps the draft's literal “Jin et al.” citation pending approval,
although its full verified Choi/Li/Yang/Jin author list is in the bibliography.
Liu's supplied title and the unverified historical benchmark scores also remain
provisional. Do not treat this proof as the author-approved final version.
