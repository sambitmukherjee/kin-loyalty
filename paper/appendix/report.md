# Technical appendix build report

The author approved the A–H outline and confirmed workshop permission for
technical appendices in the same PDF on 2026-11-27. All requested sections and
materials are included. Nothing was omitted, and no new study analysis was run.

## Pages and file size

The complete PDF has **37 pages** and is **1,067,368 bytes**, about 1.07 MB.
The main text ends on page 4, and the references occupy parts of pages 4 and 5.
The main paper and references therefore remain five pages. Appendix A begins
immediately after the last reference on page 5; appendices A–H occupy pages 5–37,
or **33 pages including the shared reference page**. They add 32 pages to the
original five-page PDF. There are no manual page or column breaks.

PDF SHA-256:
`d88f3717dd5ef22cf4c884548eac8774afa89baaa7a222587e1c2d4f7c2c317a`.

## Content and provenance

The methods begin with their purpose and an intuitive account, followed by the
precise registered procedure. Result tables state units, contrast directions,
eligibility rules and missing-value conventions in full sentences. Secondary
results are retained regardless of their p-values.

`build_tables.py` produces **135 appendix tables**. `number-trace.json` traces
all **2,471 numerical/result cells** to saved files, rows and fields, with raw
values, displayed precision and input checksums. The script only reads and
formats existing outputs; it does not fit regressions, draw bootstrap samples
or run permutations. Protocol statements, commands and dates are traced in
`source-map.md`, the generated metadata and the material manifests.

The prompt source folder preserves **28 exact text-template files**, plus the
Study 1 card-construction block copied exactly from the registration. All 29
listing blocks have a reversible display-line map. Wrapping inserts newlines
only and retains every original character, space and source newline. Appendices
C and D explain this convention. The original files remain available alongside
their wrapped display copies.

All **eight registered appendix figures** are included as vector presentation
copies. Original result files remain unchanged. The saved PDFs used 6–8 point
labels and CID/Identity-H fonts, which the kit forbids. The copies outline the
lettering and enlarge it without changing data or plot geometry. The smallest
conservatively calculated displayed label is above nine points. The small S1
legend is enlarged as a unit. The Study 2 kinship plot uses one shared enlarged
baseline legend below its panels instead of two duplicated legends; its caption
explicitly states this presentation change. These copies contain no raster
images or embedded fonts.

## Preservation and format

The baseline main-paper commit is
`15429f61d532905722aff7979876107843479c02`. The draft, bibliography and main
Figure 1 are byte-identical to that commit. The main document body through its
bibliography is also byte-identical. Pages 1–4 render pixel-identically. On page
5, every existing reference character retains its text, font size and horizontal
position. Native TeX vertical glue moves those reference lines by at most
4.015 points as the appendix content follows. No spacing override was used.

All 17 extracted official AAAI-27 kit files match the downloaded archive.
The style and bibliography style remain unmodified. The PDF uses US Letter,
native two-column layout, ten-point tables and the kit-permitted nine-point
monospace listings. Listing headers are left-aligned between rules. No forbidden
package, manual page break, margin change or global font/spacing override is
introduced.

The study code, configuration, prompts, logs, results, pre-registrations and
protected Git tags were not modified. All edits and generated files are within
`paper/`. Additional asset-conversion dependencies were installed only under
the ignored paper toolchain; the study environment and `uv.lock` are unchanged.

## Checks

The complete build uses `bash paper/build.sh` with PDFLaTeX and BibTeX.
`paper/validate.py` and `appendix/validate_appendix.py` passed on the final PDF.
The compilation has **zero errors, zero overfull boxes and zero undefined
citations**. Ordinary underfull-box messages remain. All **13 document fonts
are embedded Type 1**; no Type 3, CID or Identity-H font is present. Poppler
reports no raster images in the complete PDF.

All 37 final rendered pages were visually inspected, including every prompt,
table, figure, legend and section transition. No clipping, overlapping text,
missing glyph or unreadable figure label was found. Exact-source, reversible
wrapping, numerical-cell and input-checksum checks passed. The final machine
checks are recorded in the two `validation.json` files and `font-audit.txt`.

The changes are authorized for a local commit on main. Nothing is pushed.
