# Study 2 Phase 7 — mechanical review, no fixes

Date: 2026-11-26 (Asia/Kolkata). **Phase 7 complete; stop before Phase 8.**

After the Phase 6 report and the explanation that Gemini never sent a natural
message-12 reply, the researcher instructed: "Push the Phase 6 commits. Then
proceed to Phase 7." This follows the proposed no-fix review while retaining
that coverage limitation. Both Phase 6 commits (`0872a2f` and `46d1496`) were
pushed, and the remote `main` tip was independently verified at `46d1496` before
recording this review.

## Decision

Retain the existing protocol, prompts/cards, schemas, validation, retry rules,
output cap, provider parameters and analysis unchanged. **No mechanical fix,
additional API call, or re-pilot is needed.** Outcome levels played no role in
this decision, and no disclosure comparison or hypothesis test was computed.

| Review item | Evidence | Disposition |
| --- | --- | --- |
| Gemini natural final-message coverage | Zero pilot replies sent by Gemini at message 12; validity rate remains null | Retain as an explicit coverage limitation, without declaring a pilot final-turn validity pass |
| Gemini schema acceptance | The existing Phase 4 buyer/seller probes at messages 11 and 12 each received a valid reply; both message-12 replies used an allowed final action | Separate mechanical evidence only; do not add probes to pilot denominators or infer a natural final-turn validity rate |
| Reply validity, truncation and completion | All 706 received pilot replies valid; all 80 summaries match turn replay; no truncation, exclusion, impossible state or unfinished episode | No parser, schema, prompt, cap, or protocol fix |
| API retry behavior | One Kimi HTTP 429 recovered under the existing approved retry policy | No retry, concurrency, endpoint or model change |
| Acceptance-price semantics | Zero mismatching supplied acceptance prices for every responding model; raw supplied prices retained and ignored | No misunderstanding-based prompt fix proposed; no automatic frequency threshold |
| Usage metadata | Reasoning/input counts present for every received reply; maximum input 1,514 tokens; OpenAI/Anthropic cache counts zero | No output or request-parameter change |
| Provider cache omissions | Google/Kimi omitted some cache values; unavailable values are retained as null, distinct from zero | Keep the existing approved missing-data policy and report the limitation; no imputation or adapter change |
| Returned model versions | Every response matches the prior baseline | No substitution or model-version change |

The unobserved Gemini cell does not demonstrate a failure or establish a
validity rate. The forced probes establish acceptance/validity of those fixed
requests, not behavior in unseen natural final-turn negotiations. Existing smoke
and pilot raw records, reports and denominators remain unchanged.

## Files updated

- `docs/decisions.md`: researcher authorization, verified Phase 6 push,
  review dispositions, and explicit record that there were no post-pilot fixes.
- `preregistration/study2.md`: an unlocked mechanical-review note preserving
  the Gemini and missing-cache limitations; the three approved analysis
  definitions remain unchanged. This does not finalize or lock the addendum.
- This report and the README status. No source code, scientific configuration,
  prompt/card/schema, provider adapter, or raw/report data was changed.

## Verification

- Re-verified every digest in the 32-file Phase 6 artifact inventory.
- Independently replayed all 707 attempts and all 80 pilot episode summaries;
  zero probes/unfinished units, and the same frozen pilot manifest SHA-256
  `9e68d40288fc68621359c254c1d30e60d67684f5a09157748f215e6a08f6278e`.
- Checked only the prior mechanical smoke-probe audit for Gemini's four
  model/role/position cases. No probe inference, pooled pilot/probe rate, or new
  paid request was performed.
- Re-verified the locked Study 1 manifest hash in memory and immutable Study 1
  tags; frozen scientific source/config/prompt/analysis/client files and both
  smoke/pilot artifact sets remain unchanged. No Study 1 outcome log was read
  or analysed. `codex_prompts/` remains ignored and untracked.
- This is a documentation-only phase. The existing 554-test offline result
  applies to the unchanged runtime; no new tests or repeat full-suite run were
  needed. Reviewed the diff and checked whitespace before the local commit.

## Next gate

Phase 8 needs separate researcher approval under Section 10 of the supplied
coding prompt. It would draw and validate the actual 960-episode main manifest
for the first time, finish `preregistration/study2.md` with the complete
protocol/prompts/hashes, pilot versions and review limitations, approved analysis
and its code revision, reproduction command, and deviations policy, then commit
and create the annotated `prereg-study2` tag. Push the commit/tag only with
explicit permission. **Do not start the main run.** No actual main manifest,
registration lock/tag, Phase 7 push, or main API call was made in Phase 7.
