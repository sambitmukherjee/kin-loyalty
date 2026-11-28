# Technical appendix materials and figures

Appendices A–H follow the references in the same [paper PDF](../main.pdf).
They explain the registered methods and include the saved result tables, exact
prompt templates and registered figures. The full PDF has 34 pages; the
appendices occupy pages 5–34 and share page 5 with the final references.

For dependencies and the complete PDF build, start with the
[paper build guide](../README.md). From the repository root,
`bash paper/build.sh` regenerates the appendix materials and tables before
compiling the paper. A normal build reuses the committed figure assets.

## How the appendix is assembled

[appendices.tex](appendices.tex) contains the explanatory prose. Each method
starts with its purpose and an intuitive description, followed by the registered
procedure. The prose describes what was done; copied prompts and commands keep
their original wording. The author approved technical appendices in the same
PDF, and the official AAAI-27 style remains unchanged.

The material is prepared in several steps:

- [build_materials.py](build_materials.py) prepares source-listing inclusions,
  item descriptions and saved-figure inclusions. It also copies the registered
  Study 1 card-construction block into the prompt materials.
- [prompts/](prompts/) contains exact copies of all 28 registered text-template
  files, plus that card-construction block. These are source templates; variable
  placeholders remain visible.
- [wrap_prompts.py](wrap_prompts.py) prepares byte-identical display copies in
  `display/`. [prompt-wrapping.json](prompt-wrapping.json) records original
  spaces, hard breaks and final newlines. LaTeX wraps long lines visually, with
  grey arrows marking continuations. The arrows are not prompt text. The 37
  listings use native LaTeX floats; the longest listings span both columns.
- [build_tables.py](build_tables.py) formats the saved result CSVs and Study 2
  inference metadata, together with registered configuration and Git tag
  metadata. It does not fit models, resample or call an API.
  [number-trace.json](number-trace.json) identifies the original source cell for
  every displayed numerical result and records input hashes. The current
  appendix has 107 generated tables containing 1,959 traced result cells.

The tables state units, contrast directions and missing-value conventions. They
use Decimal round-half-to-even. Unadjusted pooled Study 1 values are recovered
as exact multiples of 1/240 before display rounding, and per-pair Study 2 message
means as multiples of 1/20. Belief-adjusted coefficients use their exported
values. One borderline p-value has six decimals, and all 48 per-pair message
means have two. [verify_fix_facts.py](verify_fix_facts.py) checks the saved-file
facts on every table build. No result was selected by its p-value.

The [source map](source-map.md) identifies the registrations, protocol files and
saved outputs behind each appendix. The full CSVs in `results/` retain more
precision than the printed tables.

## Optional regeneration of the figure assets

The eight PDFs in [figures/](figures/) are presentation copies of registered
plots in `results/study1/generated/` and `results/study2/main/figures/`. Their
sources use CID/Identity-H fonts and small lettering. The presentation copies
have outlined, enlarged lettering, with no embedded fonts or raster images.
[asset-manifest.json](asset-manifest.json) records both source and copy hashes.

[prepare_assets.py](prepare_assets.py) regenerates these copies. It leaves plot
paths and data geometry unchanged, enlarges the small Study 1 S1 legend as a
unit, and replaces duplicate Study 2 kinship legends with one enlarged legend
below the panels. The paper caption states the latter change. The script also
refreshes the exact copies of the 28 prompt-template files.

This conversion is separate from the ordinary PDF build. To run it, install
[Cairo](https://www.cairographics.org/) and Poppler, including `pdftocairo` and
`pdffonts`, through your system package manager. Then install the pinned
[CairoSVG dependencies](https://cairosvg.org/documentation/) in the optional
paper-tool environment. From the repository root:

```sh
uv venv paper/.toolchain/tools-venv --python 3.11.5
uv pip install --python paper/.toolchain/tools-venv/bin/python \
  -r paper/validation-requirements.txt \
  -r paper/appendix/asset-requirements.txt
paper/.toolchain/tools-venv/bin/python paper/appendix/prepare_assets.py
bash paper/build.sh
```

If the tool environment already exists, reuse it and run the install command
onward. These packages are kept out of the study environment and `uv.lock`.
The script imports CairoSVG normally and uses the common
[Poppler lookup](../README.md#build-the-pdf); it does not need an app-provided
Python runtime or library directory. If Cairo is installed in a nonstandard
location, configure the system library loader for that installation. On macOS,
for example:

```sh
DYLD_FALLBACK_LIBRARY_PATH=/absolute/path/to/cairo/lib \
  paper/.toolchain/tools-venv/bin/python paper/appendix/prepare_assets.py
```

Regeneration overwrites the eight copies and their manifest. Use a disposable
checkout to check this step while preserving the published assets. The
[portability check](../portability-validation.json) used CairoSVG 2.8.2, Cairo
1.18.6 and Poppler 26.05.0. All eight regenerated figures matched the committed
figures pixel for pixel at 160 dpi. Their PDF bytes differed, so compare their
rendering and source hashes as well as their file hashes. All published assets
were retained unchanged after that check.

## Validation and earlier correction reports

Follow the validation commands in the [paper build guide](../README.md#validate-a-rebuilt-paper),
after compiling the PDF. `validate_appendix.py` checks source copies, reversible
prompt wrapping, numerical provenance, figure fonts and preservation of the main
text. It needs the rendered pages produced by `paper/validate.py`, plus the
optional `pypdf`, `pdfplumber` and Pillow packages. Both validators write audit
files; they do not run the study analysis.

[validate_fixes.py](validate_fixes.py) additionally checks the appendix correction
pass against commit `76823a6`. It verifies main/reference PDF text apart from
the recorded, author-approved title update. It checks page 1 outside that title
and exact rendering of pages 2–4, inline literals, generated table hashes and
the requested display changes. It uses the committed location map and Git history rather than
an old build directory. [build_fix_report.py](build_fix_report.py) can rebuild the
itemized historical report after those checks.

[report.md](report.md) and [validation.json](validation.json) record the original
appendix work. The subsequent prose revision is checked against commit
`8e9f829`; it changed no main text, copied prompt, command, formula, seed or
statistical method. The later correction pass is documented in
[fix-pass-report.md](fix-pass-report.md), with old and new locations in
[fix-locations.json](fix-locations.json). Some native float and column whitespace
remains, as that report explains.
