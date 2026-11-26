# Study 2 Phase 4 smoke report

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
