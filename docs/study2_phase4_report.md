# Study 2 Phase 4 smoke report

Date: 2026-11-26 (Asia/Kolkata). The researcher authorized Phase 4 and its caps
after directing the Phase 3 push. GitHub `main` was verified at `2fc94d4`
before preparation. All 520 offline tests passed before the live run. All 51
attempts record the clean preparation commit
`2fd5a59b77e4d9e689f0d5fe921c482d44ec872a` with `code_dirty: false`.

Raw artifacts: `data/study2/smoke/`. Machine audit, usage CSV, full probe requests,
and hash inventory: `results/study2/smoke-report/`. The exact generated mechanical
report is retained there as `smoke-report.md`; this document adds phase context.

Status: **complete**. Execution: `live`.

Four natural episodes and sixteen probes were planned. Recorded 35 natural and 16 probe attempts; 0 API errors; 0 invalid responses.
Replay verified 4 natural episode and 16 probe summaries; 0 units remain unfinished.

Only mechanical smoke diagnostics are reported. Probes are unscored and ineligible for inference.

## Returned model versions

| Model | Expected | Observed | Responses |
| --- | --- | --- | --- |
| `claude_sonnet_5_5` | `claude-sonnet-5-5` | `claude-sonnet-5-5` | 14 |
| `gpt_6_1_terra` | `gpt-6.1-terra` | `gpt-6.1-terra` | 15 |
| `gemini_4_hydrogen` | `gemini-4-hydrogen` | `gemini-4-hydrogen` | 10 |
| `kimi_k3_1_pro` | `kimi-k3.1-pro` | `kimi-k3.1-pro` | 12 |

## Checks

| Check | Passed |
| --- | --- |
| `all_units_complete` | True |
| `all_probe_schemas_accepted` | True |
| `all_probes_valid` | True |
| `message12_actions_only_accept_or_walk` | True |
| `all_responses_valid` | True |
| `no_model_drift` | True |
| `no_truncation` | True |
| `reasoning_counts_present` | True |
| `inputs_below_4096` | True |
| `openai_anthropic_zero_cache` | True |
| `within_approved_budgets` | True |

Longest provider-reported input: 1389 tokens. Missing usage fields remain null, distinct from zero.
Per-model usage/cache/stop metadata is in `smoke_audit.json`; per-call values are in `usage_calls.csv`.

## Forced-position schema coverage

| Model | Role | Message | Attempts | Schema accepted | Final reply valid |
| --- | --- | --- | --- | --- | --- |
| `kimi_k3_1_pro` | seller | 11 | 1 | True | True |
| `gpt_6_1_terra` | buyer | 11 | 1 | True | True |
| `gemini_4_hydrogen` | seller | 12 | 1 | True | True |
| `gemini_4_hydrogen` | buyer | 12 | 1 | True | True |
| `kimi_k3_1_pro` | buyer | 12 | 1 | True | True |
| `gpt_6_1_terra` | seller | 12 | 1 | True | True |
| `gpt_6_1_terra` | buyer | 12 | 1 | True | True |
| `gemini_4_hydrogen` | buyer | 11 | 1 | True | True |
| `kimi_k3_1_pro` | buyer | 11 | 1 | True | True |
| `claude_sonnet_5_5` | buyer | 11 | 1 | True | True |
| `claude_sonnet_5_5` | buyer | 12 | 1 | True | True |
| `gpt_6_1_terra` | seller | 11 | 1 | True | True |
| `gemini_4_hydrogen` | seller | 11 | 1 | True | True |
| `claude_sonnet_5_5` | seller | 11 | 1 | True | True |
| `claude_sonnet_5_5` | seller | 12 | 1 | True | True |
| `kimi_k3_1_pro` | seller | 12 | 1 | True | True |

## Exact hand-written probe transcripts

The four prefixes below are shared across models. Buyer probes use the not-disclosed seller card; seller probes see no card.
Full system/user requests for all sixteen probes are preserved in `probe-report.json` and the manifest.

### seller, message 11

```text
Transcript so far, oldest first:
[You] message: "I'm asking $570 for the camera." | action: offer | price: $570
[Buyer's agent] message: "Would you take $410?" | action: offer | price: $410
[You] message: "I could lower the price to $550." | action: offer | price: $550
[Buyer's agent] message: "I can offer $435." | action: offer | price: $435
[You] message: "I could do $530." | action: offer | price: $530
[Buyer's agent] message: "Could we agree on $455?" | action: offer | price: $455
[You] message: "I can reduce my asking price to $520." | action: offer | price: $520
[Buyer's agent] message: "I can raise my offer to $475." | action: offer | price: $475
[You] message: "I could sell for $515." | action: offer | price: $515
[Buyer's agent] message: "I can offer $490." | action: offer | price: $490
It is your turn. This is message 11 of 12.
This is the last offer either side can make. After it, the buyer's agent
 can only accept your offer or walk away.
Reply with JSON only.
```

### buyer, message 11

```text
Transcript so far, oldest first:
[You] message: "Could you take $410 for the camera?" | action: offer | price: $410
[Seller's agent] message: "I'm asking $570 given its condition." | action: offer | price: $570
[You] message: "I can raise my offer to $435." | action: offer | price: $435
[Seller's agent] message: "I could come down to $550." | action: offer | price: $550
[You] message: "Would you consider $455?" | action: offer | price: $455
[Seller's agent] message: "I can offer it for $530." | action: offer | price: $530
[You] message: "I could do $475." | action: offer | price: $475
[Seller's agent] message: "I can reduce the price to $515." | action: offer | price: $515
[You] message: "I can increase my offer to $490." | action: offer | price: $490
[Seller's agent] message: "I can sell for $505." | action: offer | price: $505
It is your turn. This is message 11 of 12.
This is the last offer either side can make. After it, the seller's agent
 can only accept your offer or walk away.
Reply with JSON only.
```

### seller, message 12

```text
Transcript so far, oldest first:
[Buyer's agent] message: "Could you take $410 for the camera?" | action: offer | price: $410
[You] message: "I'm asking $570 given its condition." | action: offer | price: $570
[Buyer's agent] message: "I can raise my offer to $435." | action: offer | price: $435
[You] message: "I could come down to $550." | action: offer | price: $550
[Buyer's agent] message: "Would you consider $455?" | action: offer | price: $455
[You] message: "I can offer it for $530." | action: offer | price: $530
[Buyer's agent] message: "I could do $475." | action: offer | price: $475
[You] message: "I can reduce the price to $515." | action: offer | price: $515
[Buyer's agent] message: "I can increase my offer to $490." | action: offer | price: $490
[You] message: "I can sell for $505." | action: offer | price: $505
[Buyer's agent] message: "My last offer is $500." | action: offer | price: $500
It is your turn. This is message 12 of 12.
This is the final message. You can only accept the buyer's latest offer
 or walk away.
Reply with JSON only.
```

### buyer, message 12

```text
Transcript so far, oldest first:
[Seller's agent] message: "I'm asking $570 for the camera." | action: offer | price: $570
[You] message: "Would you take $410?" | action: offer | price: $410
[Seller's agent] message: "I could lower the price to $550." | action: offer | price: $550
[You] message: "I can offer $435." | action: offer | price: $435
[Seller's agent] message: "I could do $530." | action: offer | price: $530
[You] message: "Could we agree on $455?" | action: offer | price: $455
[Seller's agent] message: "I can reduce my asking price to $520." | action: offer | price: $520
[You] message: "I can raise my offer to $475." | action: offer | price: $475
[Seller's agent] message: "I could sell for $515." | action: offer | price: $515
[You] message: "I can offer $490." | action: offer | price: $490
[Seller's agent] message: "My final asking price is $505." | action: offer | price: $505
It is your turn. This is message 12 of 12.
This is the final message. You can only accept the seller's latest offer
 or walk away.
Reply with JSON only.
```

## Execution, usage, and verification

The live invocation completed **51 API attempts: 35 natural turns and 16 probes**.
All 51 responses were valid. API errors, re-asks, retries, exclusions, truncation,
and unfinished units were zero. Natural episode lengths were Claude 10, GPT 11,
Gemini 6, and Kimi 8. No natural episode reached message 12; the eight final-turn
probes supplied coverage for every model and role at that position.

| Model | Responses | Missing reasoning counts | Missing cache reads | Missing cache writes | Maximum input |
| --- | --- | --- | --- | --- | --- |
| Claude Sonnet 5.5 | 14 | 0 | 0 | 0 | 1,389 |
| GPT-6.1 Terra | 15 | 0 | 0 | 0 | 679 |
| Gemini 4 Hydrogen | 10 | 0 | 10 | 10 | 870 |
| Kimi K3.1 Pro | 12 | 0 | 4 | 0 | 795 |

OpenAI and Anthropic reported zero cache reads/writes throughout. Anthropic's
reasoning counts were reported as zero, not missing. Google omitted cache
counts; Kimi's four omitted cache-read counts remain null. Kimi's observed
reads/writes were 256 or 512 tokens. No unavailable count was imputed as zero.
All schemas were accepted in both roles at messages 11/12; every final-position
reply was `accept` or `walk_away`. All returned version strings exactly matched
the Study 1 registration, so no drift halt or parameter/prompt change was needed.

Collection ran outside the checkout from clean commit `2fd5a59`. Raw files were
then copied byte-for-byte to their repository destinations. Exact credential
scans passed without printing keys. Replay from the copied manifest verified
all 4 episode summaries, 16 probe summaries, and 51 attempts. Manifest SHA-256:
`5bc7fd7065eca30be44c4ff9de8b0b43143e5e0a40ce7f9a74f982d4768321eb`.

To check the preserved run without API calls:

```sh
.venv/bin/kinloyalty study2 replay \
  --manifest data/study2/smoke/manifest.jsonl --directory data/study2/smoke
.venv/bin/python -m kinloyalty.negotiation.smoke_report \
  --manifest data/study2/smoke/manifest.jsonl --directory data/study2/smoke \
  --output /tmp/study2-smoke-report-check
```

Use a fresh report output directory. Read `results/study2/smoke-report/` for the
audit, per-call usage, exact full probe requests, and artifact hash inventory.
Study 1 artifacts/tags and the locked manifest remain unchanged. No Study 1
main response log/outcome was inspected or analysed; the actual Study 2 main
scenario seed/manifest remains unused. `codex_prompts/` stays ignored/untracked.

## Phase boundary

Phase 4 is complete with no unresolved mechanical issue. The missing cache
fields above are preserved as unavailable metadata under the existing policy.
Commit the raw logs/reports locally without pushing. Phase 5 requires separate
approval: write and test the full Study 2 analysis/reproduction pipeline using
synthetic mock data only, without running it on these real smoke data, future
pilot data, or Study 1's main outcomes.
