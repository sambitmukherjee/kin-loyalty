# Appendix correction pass

Baseline: `76823a6dd130e79f9dafe878b32cfeb1824efa91`. The main paper and references extract identically to the baseline PDF. Pages 1–4 also render pixel-identically. The main paper plus references remains **five pages**, with references ending on shared page 5.

The complete PDF changed from **37 to 34 pages**. The appendices changed from **33 to 30 pages**, including shared page 5. There are **107 appendix tables**, down from 135, and **1,959 traced result cells**. The PDF is **1,079,781 bytes**.

PDF SHA-256: `ddb20d79aeb44cb6f9672d92e7d395ca250d72063042114ee66741ddb1a78c46`.

## Fixes and locations

Locations name the original appendix/subsection or original table/listing. Every table mapping, including removed tables, is also recorded in `fix-locations.json`. All table, figure and listing references in the paper use LaTeX cross-references.

| Item | Original location | Revised location and change |
| --- | --- | --- |
| A1 | F, Study 1 pilots | p. 16. Removed the calendar date from the amendment sentence. |
| A2 | E, Study 2 outcome/regression | p. 15. Named the undisclosed card as the reference category. |
| A3 | E opening | p. 14. Expanded sign conventions to transfers, offers, responder minimums, stated expectations and buyer share; the paragraph precedes this subsection. |
| A4 | D, Transcript/action rules | p. 11. Replaced the local-rule wording with the registered rule and the verified zero-mismatch statement. |
| A5 | E, Numerical tolerance/reporting | p. 16. Defined the 29-test Bonferroni family explicitly. |
| B1 | F, Study 2 after lock | p. 18. Used the requested two-paragraph explanation of execution, provenance, drift, attempts and resumption. |
| B2 | F, Smoke checks/blind pilot | p. 17. Explained smoke tests and forced-position probes, rate limiting and missing cache fields; used the verified Gemini wording and a figure cross-reference. |
| B3 | F, Study 1 pilots/after lock | p. 17. Applied all four replacements about the design change, separately stored pilot results, recovery and registration push. |
| B4 | D, Role prompts | p. 11. Explained single-pass placeholder substitution. |
| B5 | C, Comprehension/design | p. 11. Spelled out the wording/name allocation and the three joint-allocation rows. |
| B6 | B, Settings and old Tables 4–5 | p. 7. Removed the opening filler sentence; clarified Moonshot SDK/address and historical settings; expanded OpenAI/Gemini caching cells and prose. Settings remain Tables 3–6, before this subsection. |
| B7 | E, Bootstrap and S1 adjustment | p. 15. Applied the requested plain-language Freedman–Lane and count-matched-rank explanations. |
| B8 | H opening | p. 27. Stated that all 960 main episodes were rebuilt from turns and checked against their summaries. |
| B9 | G/H figure introductions | p. 19. Named the asset manifest, unchanged plotted data and larger lettering; used figure references throughout G and H. |
| C1 | Old Table 37, Terra p-value | p. 19. Applied the four-decimal rule with the six-decimal exception; the exact cell is listed below. |
| C2 | G/H introductions | p. 18. Added the minimum-permutation-p explanation to both introductions. |
| C3 | Old Tables 34, 38, 46 and 51 | p. 18. Used Decimal and round-half-to-even with exact unadjusted pooled lattice values; stated the scope and rule in G. |
| C4 | Old Tables 124, 127, 130 and 133 | p. 31. Displayed all 48 per-pair Length means to two exact decimals. |
| C5 | Old Tables 72–83 | p. 26. Ordered all 12 tables as Own model, Other lab, Fictional, Undisclosed, Human. |
| D1 | C/D inline literals, old pp. 10/12 | p. 11. Preserved literal spaces, straight apostrophes and complete agent labels; all 68 inline-literal occurrences match the PDF. |
| D2 | Old Listings 8, 11, 15, 22, 27, 31 and 37 | p. 8. Made all 37 listings native unbreakable ruled floats; long JSON reply listings span both columns. Full listing locations are listed below. |
| D3 | C wrapping explanation and old Listing 37 | p. 11. Marked automatic soft wraps with a grey arrow; retained source bytes and hard breaks; the transcript format spans both columns and price: $X stays on one line. |
| D4 | B model IDs and Gemini endpoint | p. 7. Kept model IDs unbroken and moved full API addresses to their own unbroken lines above the settings tables. |
| E1 | A opening | p. 5. Deleted the two reviewer/workflow notes before Frozen versions. |
| E2 | A/E/F, defensive phrasing | p. 17. Removed or rewrote the specified denials while retaining causal and scoring qualifications that prevent real misreadings. |
| E3 | C/D listing lead-ins | p. 8. Removed the three system and nine decision-body repetitions; one sentence per wording points to its listings; card insertion is explained in the C paragraph. |
| E4 | A/F/G/H workflow terms | p. 18. Replaced the specified workflow vocabulary and checked every requested leftover phrase in the PDF. |
| E5 | All Saved result/Saved value headings | p. 27. Changed these headings to Value throughout the tables. |
| E6 | Pilot, contrast and coefficient-change captions | p. 24. Moved the specified boilerplate into section introductions; retained the special pooled-P1 note. |
| F1 | Old Tables 105–112 | p. 30. Table 102 (p. 32) combines eight outcomes; build assertions verify equality across all six condition/label groups for every outcome. |
| F2 | Old Tables 113–116 | p. 30. Table 103 (p. 32) contains all 14 permutation tests. |
| F3 | Old Tables 117–123 | p. 31. Table 104 (p. 34) has all three original conditions and four buyer models; n is explicitly defined as retained episodes. |
| F4 | Old Tables 125/126/128/129/131/132/134/135 | p. 31. Replaced eight count tables with a generated sentence whose 48 identical cells are asserted in code. Retained the four share/Length tables. |
| F5 | Old Tables 84–87 | p. 27. Removed the four duplicate tables after verifying all 16 model/card count rows against the registered Figure 5; the text points to that figure. |

## Verification results

- **A4:** all eight Study 2 model/role rows report zero acceptance-price mismatches. The episode and per-call tables also contain only false mismatch flags.
- **A5:** the divisor counts exactly 29 pooled secondary Study 1 permutation tests: 17 unadjusted outcomes, 6 stated-belief contrasts and 6 belief-adjusted offers. It excludes the primary dictator contrast, all model-specific tests and all Study 2 tests.
- **B1:** the runner compares returned and expected model strings and halts dispatch on a difference. The locked pilot strings equal the requested API IDs. The approved launcher requires completion of all 960 episodes, preserves four attempts per response opportunity and has no aggregate attempt cap. Its frozen execution revision is `4e088670c0cc8386eccf8fff01d93d353a230bda`.
- **B2:** 35 pilot episodes involved Gemini; their maximum length was 11 messages. Thus no episode involving Gemini reached message 12. This is stronger than merely saying Gemini was never the final mover. The pilot had the recorded one Kimi HTTP 429 retry and no model-string change.
- **B4:** `render_template` uses one `re.sub` pass over the original template. Its callback inserts message text without rescanning the replacement.
- **B5:** the configured wording and other-name margins are both 7/7/6, with rows (3,2,2), (2,3,2), (2,2,2).
- **F1–F5:** equality/count assertions and the registered-figure comparison run during table generation and fail if the conditions cease to hold. Their source rows are retained in the generated-statement trace.

### P-value display change

Exactly one cell changed: Table 37 (p. 20), GPT-6.1 Terra, proposer other-lab minus undisclosed. CSV row 63 has raw p = 0.0499950005; its display changed from 0.0500 to **0.049995**. All appendix p-value fields were checked by the shared formatter.

### Exact cent ties

The rule is **round half to even**. Unadjusted pooled Study 1 estimates and their bootstrap endpoints are recovered as integer/240 values within the CSV export precision, then formatted with Decimal. The lattice claim is deliberately scoped to unadjusted contrasts: belief-adjusted regression coefficients are not generally multiples of 1/240. Other values use their exact exported decimal strings. Per-pair Length means are recovered at denominator 20.

**No existing displayed cent value changes under this rule.** The preceding appendix already displayed the verified ties using the same half-even direction. Exact lattice recovery now makes that choice explicit and reproducible. The main paper remains unchanged at $4.18, and Appendix G remains $4.18. All twelve cent-tie fields checked are listed here; this includes the five cells specifically identified in the request.

| Table | Source CSV row/field | Exact tie | Display |
| --- | --- | --- | --- |
| Table 29 (p. 19) | 11 / estimate | -0.625 | -0.62 |
| Table 29 (p. 19) | 11 / ci_low | -3.125 | -3.12 |
| Table 29 (p. 19) | 11 / ci_high | 1.875 | 1.88 |
| Table 30 (p. 19) | 16 / estimate | 1.875 | 1.88 |
| Table 30 (p. 19) | 16 / ci_low | -0.625 | -0.62 |
| Table 30 (p. 19) | 16 / ci_high | 4.375 | 4.38 |
| Table 34 (p. 19) | 36 / ci_high | 4.175 | 4.18 |
| Table 38 (p. 20) | 76 / estimate | -0.475 | -0.48 |
| Table 38 (p. 20) | 76 / ci_low | -1.425 | -1.42 |
| Table 44 (p. 22) | 116 / ci_low | -1.625 | -1.62 |
| Table 46 (p. 22) | 126 / ci_low | -1.225 | -1.22 |
| Table 51 (p. 24) | 151 / estimate | -4.825 | -4.82 |

### Every Length display change

All 48 display strings changed from one to two decimal places, including added trailing zeroes. No underlying mean changed. The original tables 124, 127, 130 and 133 are now Table 105 (p. 34), Table 106 (p. 34), Table 107 (p. 34), Table 108 (p. 34).

| Buyer | Seller | Original condition | Before | After |
| --- | --- | --- | --- | --- |
| Sonnet | Sonnet | not_disclosed | 9.2 | 9.25 |
| Sonnet | Sonnet | true | 9.1 | 9.10 |
| Sonnet | Sonnet | swapped | 9.3 | 9.30 |
| Sonnet | Terra | not_disclosed | 10.7 | 10.70 |
| Sonnet | Terra | true | 10.6 | 10.55 |
| Sonnet | Terra | swapped | 10.4 | 10.45 |
| Sonnet | Hydrogen | not_disclosed | 7.8 | 7.85 |
| Sonnet | Hydrogen | true | 8.1 | 8.05 |
| Sonnet | Hydrogen | swapped | 7.6 | 7.60 |
| Sonnet | Kimi | not_disclosed | 8.8 | 8.85 |
| Sonnet | Kimi | true | 8.6 | 8.60 |
| Sonnet | Kimi | swapped | 8.8 | 8.80 |
| Terra | Sonnet | not_disclosed | 10.8 | 10.75 |
| Terra | Sonnet | true | 10.8 | 10.85 |
| Terra | Sonnet | swapped | 10.8 | 10.80 |
| Terra | Terra | not_disclosed | 10.9 | 10.95 |
| Terra | Terra | true | 11.3 | 11.30 |
| Terra | Terra | swapped | 10.9 | 10.90 |
| Terra | Hydrogen | not_disclosed | 9.7 | 9.70 |
| Terra | Hydrogen | true | 9.5 | 9.50 |
| Terra | Hydrogen | swapped | 9.8 | 9.85 |
| Terra | Kimi | not_disclosed | 9.8 | 9.80 |
| Terra | Kimi | true | 10.2 | 10.15 |
| Terra | Kimi | swapped | 10.1 | 10.05 |
| Hydrogen | Sonnet | not_disclosed | 7.2 | 7.15 |
| Hydrogen | Sonnet | true | 7.3 | 7.30 |
| Hydrogen | Sonnet | swapped | 7.4 | 7.40 |
| Hydrogen | Terra | not_disclosed | 7.8 | 7.85 |
| Hydrogen | Terra | true | 8.0 | 8.00 |
| Hydrogen | Terra | swapped | 8.2 | 8.20 |
| Hydrogen | Hydrogen | not_disclosed | 6.3 | 6.35 |
| Hydrogen | Hydrogen | true | 6.6 | 6.60 |
| Hydrogen | Hydrogen | swapped | 6.6 | 6.60 |
| Hydrogen | Kimi | not_disclosed | 7.2 | 7.15 |
| Hydrogen | Kimi | true | 6.8 | 6.80 |
| Hydrogen | Kimi | swapped | 7.0 | 6.95 |
| Kimi | Sonnet | not_disclosed | 8.3 | 8.35 |
| Kimi | Sonnet | true | 8.2 | 8.20 |
| Kimi | Sonnet | swapped | 8.6 | 8.60 |
| Kimi | Terra | not_disclosed | 9.2 | 9.25 |
| Kimi | Terra | true | 9.7 | 9.70 |
| Kimi | Terra | swapped | 9.5 | 9.50 |
| Kimi | Hydrogen | not_disclosed | 7.5 | 7.45 |
| Kimi | Hydrogen | true | 7.3 | 7.35 |
| Kimi | Hydrogen | swapped | 7.5 | 7.55 |
| Kimi | Kimi | not_disclosed | 8.0 | 7.95 |
| Kimi | Kimi | true | 8.5 | 8.50 |
| Kimi | Kimi | swapped | 8.3 | 8.30 |

## Listing locations

Listing numbers are retained. Each caption and complete body is in one float. Listings 24, 25 and 37 span both columns. Original hard line breaks are retained; only automatic continuations receive the grey arrow. All 29 source/template blocks reconstruct byte for byte.

| Listing | Original page | New page | Source label |
| --- | --- | --- | --- |
| 1 | 5 | 5 | lst:tag-prereg-study1 |
| 2 | 5 | 5 | lst:tag-study1-data |
| 3 | 5 | 5 | lst:tag-prereg-study2 |
| 4 | 5 | 5 | lst:tag-study2-data |
| 5 | 5 | 5 | lst:install |
| 6 | 6 | 6 | lst:reproduce-study1 |
| 7 | 6 | 6 | lst:reproduce-study2 |
| 8 | 8 | 8 | lst:study1-system-1 |
| 9 | 8 | 8 | lst:study1-dictator-1 |
| 10 | 8 | 8 | lst:study1-ultimatum-proposer-1 |
| 11 | 8 | 9 | lst:study1-ultimatum-responder-1 |
| 12 | 9 | 9 | lst:study1-system-2 |
| 13 | 9 | 9 | lst:study1-dictator-2 |
| 14 | 9 | 9 | lst:study1-ultimatum-proposer-2 |
| 15 | 9 | 9 | lst:study1-ultimatum-responder-2 |
| 16 | 9 | 10 | lst:study1-system-3 |
| 17 | 9 | 10 | lst:study1-dictator-3 |
| 18 | 9 | 10 | lst:study1-ultimatum-proposer-3 |
| 19 | 10 | 10 | lst:study1-ultimatum-responder-3 |
| 20 | 10 | 10 | lst:study1-card |
| 21 | 10 | 10 | lst:study1-counterparty-agent |
| 22 | 10 | 11 | lst:study1-counterparty-human |
| 23 | 10 | 11 | lst:study1-reply-dictator |
| 24 | 10 | 12 | lst:study1-reply-ultimatum-proposer |
| 25 | 10 | 12 | lst:study1-reply-ultimatum-responder |
| 26 | 10 | 12 | lst:study1-comprehension |
| 27 | 11 | 12 | lst:study2-buyer-system |
| 28 | 11 | 12 | lst:study2-seller-system |
| 29 | 11 | 12 | lst:study2-counterparty-with-card |
| 30 | 11 | 13 | lst:study2-agent-card |
| 31 | 11 | 13 | lst:study2-counterparty-without-card |
| 32 | 12 | 13 | lst:study2-turn |
| 33 | 12 | 13 | lst:study2-opening |
| 34 | 12 | 13 | lst:study2-transcript-heading |
| 35 | 12 | 13 | lst:study2-last-offer |
| 36 | 12 | 13 | lst:study2-final-message |
| 37 | 12 | 14 | lst:transcript-format |

## Build, preservation and remaining limitation

- PDFLaTeX and BibTeX build passed, with zero errors, zero overfull boxes and zero undefined references/citations. All 15 fonts are embedded Type 1; no Type 3, CID or Identity-H fonts occur. Ordinary underfull-box messages remain.
- The official kit files and the eight appendix figure assets are unchanged. No forbidden package, page-break command, smaller type, margin change or float-spacing override was added.
- Main PDF text through the last reference is identical to the previous PDF; the main source, draft, bibliography and Figure 1 are byte-identical. Study code, prompts, configurations, logs, results, pre-registrations and protected tags were not modified.
- All requested leftover phrases are absent. All 68 inline-literal occurrences match, including spaces and apostrophes. Listing 37 keeps the complete price: $X phrase on one line.
- Every appendix page was inspected as an image. No split listing, separated caption, clipped table/figure, overlap or missing glyph was found.
- **G6 spacing limitation:** some native float/column gaps remain, especially on prompt-only and final float pages. The requirement to eliminate every large gap is not fully met. Trials with larger grouped floats and unbreakable inline boxes worsened the layout; the final version retains ruled floats and the kit spacing. No manual page breaks or spacing overrides were used to conceal the remaining white space.
- **C3 wording qualification:** the 1/240 statement applies to unadjusted pooled contrasts and endpoints, not belief-adjusted regression coefficients. No fact check contradicted the other requested replacements.

The full machine checks are in `fix-verifications.json`, `fix-pass-validation.json`, `number-trace.json`, `formatting-changes.json`, `fix-locations.json` and the two general validation files. No analysis or model API call was run. The correction pass is for a paper-only local commit; nothing is pushed.
