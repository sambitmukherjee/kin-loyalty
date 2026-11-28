# Author-approved title update — 2026-11-28

The paper's title is now:

**Do AI Agents Favor Their Own Kind? Model Labels Shift Ultimatum Choices but Have Little Effect on Negotiation**

The author approved the subtitle replacement and requested an update throughout
the paper and repository, a PDF rebuild and a local commit without a push.
The Markdown draft, generated LaTeX, PDF, main README and preferred citation
now use the same title. The exact replacement and approval are recorded in
[applied-edits.json](applied-edits.json).

The PDF was rebuilt with `bash paper/build.sh`, using the unmodified official
AAAI-27 kit and PDFLaTeX. It remains **34 pages**, with a two-line title.
There are no LaTeX errors, overfull boxes or undefined references/citations;
all 15 Type 1 fonts are embedded. The PDF is **1,079,784 bytes**.

Compared with commit `c6cef9a21f0af7575f4cf9f1263540d1ec885813`, pages 2–34 render pixel for pixel
identically at 120 dpi. Page 1 is also identical outside the title. Extracted
text from the entire PDF is unchanged apart from the approved title, and the
first page was visually inspected. The manuscript body, bibliography, figures,
107 appendix tables and all 1,959 traced numerical cells are unchanged.

All three paper validators passed. The appendix preservation checks now permit
only the exact title edit in the approval record. Their image exception covers
only the title's bounding rectangle with two points of padding; negative checks confirmed that unexpected titles
and changes elsewhere remain detectable. The normal table build also refreshed
two older documentation hashes in `number-trace.json`; its numerical records
and generated table text are unchanged.

Study code, configuration, prompts, data, results, methods and frozen tags were
preserved. No analysis or model calls were run. Earlier report and audit
versions are preserved in Git history; the current paper validation files
describe the updated PDF. The detailed checks are in
[title-change-validation.json](title-change-validation.json).

PDF SHA-256: `7a93e15896031bbb01716d5a1f07d2b809c9ffee21b39218dc2502b5362d13b1`.
