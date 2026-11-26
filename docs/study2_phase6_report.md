# Study 2 Phase 6 — blind pilot report

Date: 2026-11-26 (Asia/Kolkata). **Pilot complete; stop before Phase 7.**

The researcher approved 80 episodes and the 7,680-attempt ceiling, then requested the Phase 5 push. Pushed and independently verified `a91efd59f082ee9cb72ea67d6b7e47d6ebce6eec` before pilot preparation. All 554 offline tests passed in 119.15 seconds. Committed tested preparation as `0872a2f0d0e9225525834b0e1e093b4968f3946d` and executed every real attempt from that clean revision.

## Scope, completion and provenance

- Completed all **80 natural episodes**, five per ordered pair, with no probes or replacements. Exactly **707 API attempts** produced **706 valid replies**. One Kimi seller request at message 3 returned retryable HTTP 429; its ordinary retry succeeded. There was one retry, no invalid-response re-ask, no exclusion, no output truncation, no version drift, and no unfinished or impossible state.
- Budget used: **707/7,680** cumulative natural attempts; **0/0** probes. One uninterrupted invocation sufficed; no external resumption or parameter change was needed.
- Frozen pilot scenario/order seeds: **2026112603/2026112604**. Manifest SHA-256: `9e68d40288fc68621359c254c1d30e60d67684f5a09157748f215e6a08f6278e`. Main scenarios remain undrawn.
- Replayed all 707 attempts and checked all 80 terminal summaries before reporting. Raw artifacts were collected outside the checkout, copied byte-for-byte to `data/study2/pilot/`, and independently replayed there. Re-generated all nine report files from that copy and verified byte-identical output.
- Exact credential-value scans passed without exposing any value. Credentials came only from the ignored checkout `.env`, excluding process environment values. Every call records preparation commit `0872a2f0d0e9225525834b0e1e093b4968f3946d` and `code_dirty: false`.

## Validity and message-position coverage

All **observed** model/turn-class cells are 100% valid, exceeding the required 95%. Received replies, including any re-asks, are the denominator; API errors are separate. The Gemini final-message cell has **zero observations**, a null rate, and a coverage flag. It is not counted as 100% valid.

| Model | Message 1 valid/N | Messages 2–11 valid/N | Message 12 valid/N |
| --- | --- | --- | --- |
| `claude_sonnet_5_5` | 18/18 | 156/156 | 1/1 |
| `gpt_6_1_terra` | 22/22 | 176/176 | 3/3 |
| `gemini_4_hydrogen` | 18/18 | 137/137 | not observed (0) |
| `kimi_k3_1_pro` | 22/22 | 152/152 | 1/1 |

Five episodes attempted and completed message 12: Claude sent one final reply, GPT three, Kimi one, and Gemini none. The Phase 4 forced probes already tested message-11/12 schemas for each model in both roles; those probes are not pooled into pilot validity denominators or analysed as pilot outcomes.

**Only coverage review flag:** `all_model_turn_classes_observed` is false. The report preserves this limitation. No added negotiation or change to the message limit was used to force natural final-turn observations.

## Returned versions and usage

| Model | Expected = every returned string | Responses | Missing reasoning | Missing cache read/write | Max input tokens |
| --- | --- | --- | --- | --- | --- |
| `claude_sonnet_5_5` | `claude-sonnet-5-5` | 175 | 0 | 0/0 | 1514 |
| `gpt_6_1_terra` | `gpt-6.1-terra` | 201 | 0 | 0/0 | 867 |
| `gemini_4_hydrogen` | `gemini-4-hydrogen` | 155 | 0 | 155/155 | 1073 |
| `kimi_k3_1_pro` | `kimi-k3.1-pro` | 175 | 0 | 41/2 | 980 |

All version strings match the locked prior baseline. Reasoning counts are recorded for all 706 replies, including reported zeros. OpenAI and Anthropic cache reads/writes are zero throughout. Google omitted both cache fields in all 155 replies; Kimi omitted cache reads in 41 and cache writes in two of 175 replies. Available Kimi reads were 256/512, and writes 0/253/255/256/512. Every normalized usage record retains both cache fields; unavailable values remain null, distinct from zero, following the established missing-data policy.

Longest provider-counted input: **1,514 tokens**, well below 4,096. All input counts are present, and no reply was cut off at its output cap. Per-call values are in `results/study2/pilot-report/usage_calls.csv`; the audit retains finish reasons and available token values.

## Acceptance-price mismatches

| Actual responding model | Valid acceptances | Mismatching supplied prices |
| --- | --- | --- |
| `claude_sonnet_5_5` | 11 | 0 |
| `gpt_6_1_terra` | 19 | 0 |
| `gemini_4_hydrogen` | 29 | 0 |
| `kimi_k3_1_pro` | 21 | 0 |

Counts pool all labels and pairs; the model/role CSV retains the role. Supplied prices remain in the raw response/parsed reply and terminal acceptance-price JSON, and are ignored when scoring the accepted opposite offer. There is no automatic frequency-based fix threshold.

## Outcomes pooled over all disclosure conditions

All 80 episodes ended in deals, with zero walk-away/final-message impasses or exclusions, and zero buyer/seller mandate violations. This is a descriptive pilot outcome, not a reason to change the design. Overall mean buyer surplus share is 0.6053981082 and median 0.6026315789; retained shares range from 0.4 to 0.9016393443. No disclosure comparison, P2 estimate, confidence interval, or hypothesis test was computed.

Each row below pools every disclosure condition within its pair. The full CSV additionally gives denominators, impasse/exclusion counts, extrema, retries/re-asks and mandate rates.

| Buyer → seller pair | Deals / completed | Mean share | Median share | Mean messages | Buyer/seller violations |
| --- | --- | --- | --- | --- | --- |
| `claude_sonnet_5_5__claude_sonnet_5_5` | 5/5 | 0.628422 | 0.656250 | 8.8 | 0/0 |
| `claude_sonnet_5_5__gemini_4_hydrogen` | 5/5 | 0.687720 | 0.692308 | 8.4 | 0/0 |
| `claude_sonnet_5_5__gpt_6_1_terra` | 5/5 | 0.545077 | 0.511364 | 10.6 | 0/0 |
| `claude_sonnet_5_5__kimi_k3_1_pro` | 5/5 | 0.590421 | 0.619048 | 9.0 | 0/0 |
| `gemini_4_hydrogen__claude_sonnet_5_5` | 5/5 | 0.557529 | 0.564103 | 7.4 | 0/0 |
| `gemini_4_hydrogen__gemini_4_hydrogen` | 5/5 | 0.622955 | 0.619048 | 6.6 | 0/0 |
| `gemini_4_hydrogen__gpt_6_1_terra` | 5/5 | 0.499422 | 0.484848 | 7.4 | 0/0 |
| `gemini_4_hydrogen__kimi_k3_1_pro` | 5/5 | 0.514873 | 0.509804 | 7.2 | 0/0 |
| `gpt_6_1_terra__claude_sonnet_5_5` | 5/5 | 0.644146 | 0.650000 | 10.8 | 0/0 |
| `gpt_6_1_terra__gemini_4_hydrogen` | 5/5 | 0.780630 | 0.758621 | 9.8 | 0/0 |
| `gpt_6_1_terra__gpt_6_1_terra` | 5/5 | 0.528340 | 0.527273 | 11.2 | 0/0 |
| `gpt_6_1_terra__kimi_k3_1_pro` | 5/5 | 0.625164 | 0.645714 | 10.4 | 0/0 |
| `kimi_k3_1_pro__claude_sonnet_5_5` | 5/5 | 0.600015 | 0.605263 | 8.4 | 0/0 |
| `kimi_k3_1_pro__gemini_4_hydrogen` | 5/5 | 0.691363 | 0.653061 | 7.2 | 0/0 |
| `kimi_k3_1_pro__gpt_6_1_terra` | 5/5 | 0.558631 | 0.511628 | 8.8 | 0/0 |
| `kimi_k3_1_pro__kimi_k3_1_pro` | 5/5 | 0.611662 | 0.628571 | 9.2 | 0/0 |

Episode lengths (valid messages; no invalid replies included):

| Messages | Episodes |
| --- | --- |
| 6 | 4 |
| 7 | 18 |
| 8 | 14 |
| 9 | 17 |
| 10 | 11 |
| 11 | 11 |
| 12 | 5 |

Mean length: **8.825 messages**. Five episodes reached message 12. Pair-specific length distributions are in `pair_episode_lengths.csv`.

## Artifacts and checks

- `data/study2/pilot/manifest.jsonl`, `collection.json`, `preflight.json`, `episodes.jsonl`, `run_summary.json`, and sixteen `turns/*.jsonl` files: 21 raw/provenance files copied unchanged. Maximum pair-log size is 530,821 bytes, below 50 MB.
- `results/study2/pilot-report/`: audit JSON, generated blind Markdown, pair-pooled outcomes/lengths, validity by model/class and role, mismatch counts by actual model and role, and per-call usage. Nine generated report files reproduce byte-for-byte.
- `results/study2/pilot-report/artifacts.sha256.json`: complete raw/report/phase-document digest inventory (excluding itself).
- Preparation and tests: `docs/study2_phase6_execution_plan.md` and `tests/test_study2_pilot.py`. All 554 offline tests passed before paid execution; no source code changed during or after collection.

```sh
.venv/bin/kinloyalty study2 replay \
  --manifest data/study2/pilot/manifest.jsonl --directory data/study2/pilot
.venv/bin/python -m kinloyalty.negotiation.pilot_report \
  --manifest data/study2/pilot/manifest.jsonl --directory data/study2/pilot \
  --output /private/tmp/study2-pilot-report-check
```

Choose a fresh report directory. These commands make no model calls. Do not run the inference pipeline on this pilot; its loader continues to reject pilot input.

## Phase 7 review and limits

No mechanical fix is proposed from the observed run. The remaining review item is accepting Gemini’s unobserved natural message-12 cell as a coverage limitation, with the earlier forced-position schema probes as separate mechanical evidence. No additional API call or prompt/protocol change is proposed without researcher approval. Missing provider cache counts remain documented rather than imputed.

No scientific setting, prompt/card/schema, provider adapter, Phase 5 analysis code, or addendum definition changed during this pilot. No Study 1 outcome log was read or analysed, no Study 1 artifact or immutable tag moved, and its locked manifest hash remains preserved. No actual Study 2 main manifest, registration tag/lock, main run, or Phase 6 push was performed. `codex_prompts/` remains ignored and untracked.

Commit Phase 6 locally and stop for approval before Phase 7. Any subsequent mechanical change must be explained and approved, logged with its reason, and re-piloted where affected. The final addendum lock is a later separate phase.
