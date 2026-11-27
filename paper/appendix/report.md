# Technical appendix build report

The approved appendices A–H follow the references in the same PDF. The latest
correction pass is described item by item in `fix-pass-report.md`, including
original and revised locations, all requested checks and the remaining spacing
limitation. No study analysis or model API call was run.

## Pages and preservation

The PDF has **34 pages**, down from 37, and is **1,079,781 bytes**. Main text ends
on page 4 and references on page 5, exactly as before. The main paper plus
references remains five pages. Appendices occupy pages 5–34: **30 pages
including shared page 5**, down from 33.

Baseline: `76823a6dd130e79f9dafe878b32cfeb1824efa91`. The draft, main LaTeX source,
bibliography and Figure 1 are byte-identical to that commit. Extracted PDF text
through the final reference is identical; pages 1–4 also render pixel-identically.
The main paper's previous author-approved corrections and Table 1 heading are
preserved. Nothing outside `paper/` was changed.

PDF SHA-256: `ddb20d79aeb44cb6f9672d92e7d395ca250d72063042114ee66741ddb1a78c46`.

## Materials and numeric provenance

`build_tables.py` generates **107 appendix tables**, down from 135, and traces
**1,959 result cells** in `number-trace.json`. The requested eligibility, strata
and mandate tables were merged; identical completion counts became an asserted,
generated sentence. Duplicate comprehension tables were checked against the
registered figure before removal. Source rows and count assertions remain in
the trace. No value was selected or omitted because of its p-value.

All 28 registered prompt-template files and the registered card block are
preserved byte for byte. The 29 listing inputs are now exact source copies.
`prompt-wrapping.json` records original lines and the automatic wrapping
convention. A grey arrow marks visual continuations only; it is not source text.
All 37 listings retain their captions and complete contents in native floats.
Listings 24, 25 and 37 span both columns. Every one of the 68 inline literals
checked against extracted PDF text retains its source spelling and spaces.

The eight vector figures and `asset-manifest.json` are unchanged. The earlier
kit-compliant enlargement and outlining of lettering preserves plotted data;
no figure was reanalysed. All result source checksums continue to match.

Numeric presentation uses Decimal round-half-to-even. Exact unadjusted pooled
Study 1 cells are recovered at denominator 240; belief-adjusted coefficients
use their exported decimal values. All twelve verified cent ties retain their
previous displays, including $4.18. One p-value changes from 0.0500 to 0.049995.
All 48 per-pair Length means now have two exact decimals, at denominator 20.
`formatting-changes.json` records all 49 changed display strings.

## Format and checks

The official AAAI-27 style and bibliography style remain unmodified, as do all
17 extracted kit files. No forbidden package, manual page break, smaller type,
margin adjustment or float-spacing override was added. The build has zero LaTeX
errors, overfull boxes and undefined citations/references. All 15 fonts are
embedded Type 1; none is Type 3, CID or Identity-H. The PDF has no raster images.

The build and all three validators passed: `paper/validate.py`,
`appendix/validate_appendix.py` and `appendix/validate_fixes.py`. Every appendix
page was inspected as an image. No split listing, separated caption, clipping,
overlap, missing glyph or unreadable figure label was found. Some native float
and column gaps remain, particularly on prompt pages. **G6's request to remove
every large empty gap is not fully met.** Ordinary underfull-box messages remain.
The itemized correction report explains the retained kit layout.

Factual verifications, source-cell traces, table/listing location mappings and
PDF-specific checks are committed beside this report. `fix-baseline-locations.json`
records original locations without depending on an ignored old build directory.
The study code, configurations, prompts, data, results, pre-registrations and
protected tags are unchanged. The local commit includes only `paper/`; nothing
is pushed.
