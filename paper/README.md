# Build the AAAI-27 workshop paper

The complete paper is available as [main.pdf](main.pdf). It contains the main
paper, references and technical appendices A–H in one 34-page PDF. The main paper
and references occupy five pages; the appendices start on the shared fifth page.
The author is Sambit Mukherjee, Independent Researcher.

This guide explains how to rebuild the manuscript from the saved results. To
reproduce the studies' statistical results first, follow
[Reproducing the paper](../docs/reproducing_the_paper.md). Building the PDF reads
those results; it does not run experiments, fit models or draw new resamples.
No API keys are needed.

## Install the build dependencies

Run the commands below from the repository root, in a checkout of the current
branch. Use a full Git clone with its history and tags: the appendix records the
four frozen study tags, and the optional validators compare the paper with
historical commits. The frozen study tags themselves predate the manuscript.

The build uses the following tools. The versions in the last column were tested
in a disposable checkout on macOS with Apple Silicon; other platforms have not
been tested in this portability check.

| Dependency | What it is used for | Tested version |
| --- | --- | --- |
| Python and the repository's locked packages | Draw Figure 1 and format the saved results and prompt listings. | CPython 3.11.5; packages from `uv.lock` |
| Pandoc | Convert the approved Markdown draft to LaTeX. | 3.7.0.1 |
| TeX distribution with `pdflatex` and `bibtex` | Compile the official AAAI style and author–year bibliography. | TeX Live 2026, pdfTeX 1.40.29 |
| Poppler, including `pdftotext` | Check the saved comprehension figure while formatting appendix tables. | 26.05.0 |
| Bash and Git | Run the build and read the frozen tag metadata. | System commands |

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) and prepare
the repository's Python environment:

```sh
uv sync --locked --python 3.11.5
```

Install [Pandoc](https://pandoc.org/installing.html),
[Poppler](https://poppler.freedesktop.org/) and a TeX distribution, and put their
executable directories on `PATH`. For example, Homebrew users can install the
first two with `brew install pandoc poppler`. A full TeX Live installation
supplies the LaTeX packages used here. A smaller
[TinyTeX installation](https://github.com/rstudio/tinytex-releases) also works
once those packages are installed; a missing `.sty` or font error means that the
TeX distribution needs the corresponding package. The build does not download
software or install missing TeX packages automatically.

The official [AAAI-27 Author Kit](https://aaai.org/authorkit27/) is already included.
Its style, bibliography style and other extracted files are unmodified. The
archive [aaai27-author-kit.zip](aaai27-author-kit.zip) has SHA-256
`9406a545d5d213757245eb37118fe652b2fccf64f555aff28b49ebe2a780c960`.
[author-kit-manifest.json](author-kit-manifest.json) records all extracted file
hashes. There is no need to substitute another template.

## Build the PDF

After installing the dependencies, run:

```sh
bash paper/build.sh
```

The output is `paper/main.pdf`. The build regenerates `paper/main.tex`, Figure 1,
appendix materials, tables and their provenance files, then runs PDFLaTeX, BibTeX
and two further PDFLaTeX passes. Compiler output and intermediate files are in
`paper/build/`. The build uses the eight committed appendix figure assets, so it
does not require CairoSVG or the optional validation packages.

Because this command rewrites generated paper files, a separate checkout is
useful when checking reproduction without changing your working copy:

```sh
git clone --no-hardlinks . scratch/paper-build
cd scratch/paper-build
uv sync --locked --python 3.11.5
bash paper/build.sh
```

The local clone starts from committed files. Run it after committing any paper
changes you want to test. Its output is `scratch/paper-build/paper/main.pdf`
relative to the original repository root. The original checkout ignores
`scratch/`.

By default, the build uses `.venv/bin/python` and finds TeX and Pandoc on `PATH`.
If your TeX binaries are not on `PATH`, select their directory explicitly:

```sh
PAPER_TEX_BIN=/absolute/path/to/tex/bin bash paper/build.sh
```

`PAPER_TEX_BIN` is prepended to `PATH` for that invocation. A locally installed
TinyTeX is supported this way, without assuming its location or architecture.
`PAPER_PYTHON=/absolute/path/to/python` can select another interpreter; it must
have the repository's locked dependencies installed. The build respects existing
`TEXMFVAR`, `TEXMFCONFIG` and `TEXMFHOME` settings. Otherwise it keeps those TeX
files under the ignored `paper/.toolchain/` directory.

All paper scripts use the same Poppler lookup. A command-specific variable such
as `PDFTOTEXT` takes precedence, followed by the directory `PAPER_POPPLER_BIN`,
then the ordinary `PATH`. The other supported variables are `PDFFONTS`,
`PDFINFO`, `PDFTOPPM` and `PDFTOCAIRO`. Use absolute paths for overrides, since
some scripts change their working directory. An invalid explicit override stops
the command with an error. For example:

```sh
PAPER_POPPLER_BIN=/absolute/path/to/poppler/bin bash paper/build.sh
```

The build checks its interpreter, required commands and Python imports before
generating manuscript files. If compilation fails later, inspect
`paper/build/pdflatex-first.stdout`, `bibtex.stdout`, `pdflatex-second.stdout` and
`pdflatex-final.stdout`. These logs distinguish missing TeX packages from errors
in the manuscript.

## Validate a rebuilt paper

Validation needs Poppler's `pdffonts`, `pdfinfo` and `pdftoppm` as well as
`pdftotext`. Install the optional Python inspection packages in a separate
environment, so the study environment and its lockfile stay unchanged:

```sh
uv venv paper/.toolchain/tools-venv --python 3.11.5
uv pip install --python paper/.toolchain/tools-venv/bin/python \
  -r paper/validation-requirements.txt
paper/.toolchain/tools-venv/bin/python paper/validate.py
paper/.toolchain/tools-venv/bin/python paper/appendix/validate_appendix.py
paper/.toolchain/tools-venv/bin/python paper/appendix/validate_fixes.py
```

Run these commands after the build, in this order. The first checks the official
kit, embedded fonts, paper size, LaTeX warnings, approved text changes and
numerical input hashes. It renders every page to `paper/build/render/`. The
appendix checks then verify prompt copies, table cells, figures and preservation
of the main text. `validate_fixes.py` also checks the specific appendix
corrections recorded against commit `76823a6`; it is a historical preservation
audit rather than a general validator for a different manuscript.
The appendix audits allow the exact author-approved title replacement recorded
in `applied-edits.json`. They compare the remaining text and page layout without
exempting other content. The [title-change report](title-change-report.md)
records the current title, build checks and comparison with the preceding PDF.

The commands update `paper/validation.json`, `paper/font-audit.txt`,
`paper/author-kit-manifest.json` and the appendix validation reports. Review the
rendered pages as well as the automated checks. Existing native float whitespace
is described in the [appendix correction report](appendix/fix-pass-report.md).

The [portability check](portability-validation.json) records a successful build
and all three validators using ordinary installed tools, without a Codex runtime.
At that revision, all 34 pages matched the committed PDF pixel for pixel at
120 dpi, and extracted text matched exactly. The regenerated tables, prompts and numerical cells were
unchanged. PDF bytes can differ between builds even when text and rendering
match; the published PDF was retained unchanged during that check.
Regenerated provenance files can also record newer documentation hashes;
those are separate from the numerical cell records.

The executable lookup can also be checked without external tools:

```sh
.venv/bin/python -m unittest discover -s paper -p test_tool_paths.py
```

## Figure and appendix sources

[figures/make_figure1.py](figures/make_figure1.py) reads
`results/study1/generated/contrasts.csv` and draws the pre-registered contrasts.
It does not estimate them again. The seven-inch-wide vector figure uses outlined
lettering to meet the kit's font restrictions. A normal build regenerates it.

The [appendix guide](appendix/README.md) explains table provenance, exact prompt
copies and optional regeneration of the eight presentation figures. Those
figures enlarge and outline lettering from the saved registered plots while
preserving their plotted values. Ordinary PDF builds reuse the committed copies.

## Earlier checks and author decisions

These files preserve the manuscript's typesetting and verification history:

- [applied-edits.json](applied-edits.json) and [proposed-edits.md](proposed-edits.md)
  record the author-approved corrections applied to `draft.md`. The final
  typesetting-notes section of that draft is omitted from the paper.
- [numeric-audit.json](numeric-audit.json),
  [reference-verification.md](reference-verification.md),
  [conversion-audit.json](conversion-audit.json) and
  [typesetting-report.md](typesetting-report.md) record the original checks.
- [sources/](sources/) preserves the author-supplied Intelligence Index chart
  and the selected model labels and values.
- [appendix/source-map.md](appendix/source-map.md) identifies the sources of
  explanatory material, while [appendix/report.md](appendix/report.md) and
  [appendix/fix-pass-report.md](appendix/fix-pass-report.md) record the appendix
  work and its limitations.

The optional commands below repeat the arithmetic audit and rebuild the
supplement archive from existing artifacts. They are separate from the PDF
build and write their reports inside `paper/`:

```sh
.venv/bin/python paper/check_numbers.py
.venv/bin/python paper/make_supplement.py
```

The supplement contains the selected source artifacts, tables and figures. It
excludes raw API logs and credentials.
