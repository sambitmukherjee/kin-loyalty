# Technical appendices

The author approved the A–H outline and confirmed that the workshop permits
technical appendices after the references in the same PDF on 2026-11-27.
The appendices use the unchanged AAAI-27 style. They contain no manual page or
column breaks. The existing main text, bibliography and Figure 1 are preserved
from commit `15429f6`, apart from the later author-requested Table 1 heading
“Artificial Analysis Intelligence Index v5.0.2”.

`appendices.tex` contains the explanatory prose. Each method starts with its
purpose and an intuitive description, then specifies the registered procedure.
Result tables are split into manageable groups with units, directions and
missing-value conventions stated in words. No results were selected by p-value.

The subsequent author-requested prose revision describes the registered analysis
and study procedures rather than instructing the reader. It changes no main
text, copied prompt, command, formula, seed, result cell or statistical method.
The revision is checked against the original appendix commit `8e9f829` in
`validation.json`.

From the repository root, `bash paper/build.sh` regenerates the appendix
materials and tables, then compiles the complete paper with PDFLaTeX and BibTeX.
All work and temporary files remain inside `paper/`.

- `build_tables.py` reads saved result CSVs and the saved Study 2 metadata for
  TOST and cluster-robust inference. It also reads the registered provider
  configuration and Git tag metadata. It formats values; it fits no model and
  performs no resampling. `number-trace.json` records the original cell behind
  every displayed numerical result and the input hashes.
- `build_materials.py` prepares source listings and figure inclusions.
- `prompts/` contains exact copies of all 28 registered text-template files,
  plus the Study 1 card-construction block copied from the registration.
- `wrap_prompts.py` prepares byte-identical source copies in `display/`.
  `prompt-wrapping.json` retains original spaces, hard breaks and final newlines.
  The listings package wraps long lines automatically; grey arrows mark only
  visual continuations and are not prompt text. All 37 listings are unbreakable
  native floats; the two long JSON instructions and transcript format span both
  columns.
- `figures/` contains presentation copies of the eight registered vector PDFs.
  The saved originals use kit-forbidden CID/Identity-H fonts and 6–8 point
  labels. `prepare_assets.py` converts glyphs to vector outlines and enlarges
  lettering; it never re-estimates a plotted value or changes data geometry.
  The small S1 legend is enlarged as a unit. The duplicate Study 2 kinship
  legends become one shared enlarged legend below the panels. Its caption
  discloses that relocation. Source and presentation hashes are recorded in
  `asset-manifest.json`. The copies contain no fonts or raster images.
- `validate_appendix.py` checks exact source copies, reversible wrapping,
  numerical cell provenance, main-text preservation, figure fonts and source
  hashes. Run it with a Python environment providing `pypdf`, `pdfplumber`
  and Pillow, after `paper/validate.py` has rendered the pages.

The committed vector copies allow normal builds without regenerating assets.
To regenerate those presentation copies, use `prepare_assets.py` with
CairoSVG 2.8.2, the dependencies in `asset-requirements.txt`, Cairo and Poppler's
`pdftocairo` and `pdffonts`. The verified local build used the bundled Python
3.12 runtime and installed only these paper-build dependencies under the ignored
`paper/.toolchain/appendix-python/`. The study Python environment and `uv.lock`
were not modified. See `source-map.md` for prose sources and `validation.json`
for the final checks.

The correction pass against commit `76823a6` is documented in
`fix-pass-report.md`, with old/new locations in `fix-locations.json`. The PDF
has 34 pages: five main/reference pages and 30 appendix pages including shared
page 5. The 107 generated appendix tables contain 1,959 traced result cells.
`verify_fix_facts.py` checks the requested saved-file facts on every table build.
`validate_fixes.py` checks exact main PDF text, pages 1–4 rendering, all inline
literals, table hashes, leftover phrases and display changes. It uses the
committed baseline-location map and Git baseline, so it does not require an old
build directory. `build_fix_report.py` writes the itemized report after validation.

Values use Decimal round-half-to-even; unadjusted pooled Study 1 cells are
recovered on their exact 1/240 lattice, and per-pair Length means on their 1/20
lattice. Belief-adjusted coefficients use their exported decimal values. One
borderline p-value has six decimals; all 48 Length means have two. Identical
eligibility, strata, mandate and completion tables were condensed with build
assertions. The duplicate comprehension tables were checked against the registered
figure before removal. Some native float/column whitespace remains; the report
records this limitation without claiming that G6 is fully satisfied.
