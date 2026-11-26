# Study 2 Phase 6 blind pilot report

Execution: `live`; status: **complete**. 80/80 episodes complete; 707/7680 attempts; 1 API errors; 0 invalid responses.

All outcome summaries pool disclosure conditions within pair. No disclosure comparisons or hypothesis tests were computed.

## Mechanical checks

| Check | Passed |
| --- | --- |
| `all_80_episodes_complete` | True |
| `replay_matches_and_no_impossible_states` | True |
| `observed_model_turn_class_validity_above_95_percent` | True |
| `all_model_turn_classes_observed` | False |
| `no_truncation` | True |
| `no_model_drift` | True |
| `reasoning_counts_present` | True |
| `all_input_counts_present_and_below_4096` | True |
| `openai_anthropic_zero_cache` | True |
| `within_approved_budget` | True |

Zero-response model/turn cells are not observed, not 100% valid; they remain separate coverage flags.
Validity denominators are received responses (including re-asks); API failures are counted separately.

## Validity per model and turn class

| Model | Turn class | Valid / responses | Rate | Status |
| --- | --- | --- | --- | --- |
| `claude_sonnet_5_5` | first | 18/18 | 1.0 | pass |
| `claude_sonnet_5_5` | middle | 156/156 | 1.0 | pass |
| `claude_sonnet_5_5` | final | 1/1 | 1.0 | pass |
| `gpt_6_1_terra` | first | 22/22 | 1.0 | pass |
| `gpt_6_1_terra` | middle | 176/176 | 1.0 | pass |
| `gpt_6_1_terra` | final | 3/3 | 1.0 | pass |
| `gemini_4_hydrogen` | first | 18/18 | 1.0 | pass |
| `gemini_4_hydrogen` | middle | 137/137 | 1.0 | pass |
| `gemini_4_hydrogen` | final | 0/0 | None | not_observed |
| `kimi_k3_1_pro` | first | 22/22 | 1.0 | pass |
| `kimi_k3_1_pro` | middle | 152/152 | 1.0 | pass |
| `kimi_k3_1_pro` | final | 1/1 | 1.0 | pass |

## Pooled outcomes

```json
{
  "planned": 80,
  "completed": 80,
  "unfinished": 0,
  "deals": 80,
  "walk_away_impasses": 0,
  "final_message_impasses": 0,
  "exclusions": 0,
  "retained": 80,
  "deal_rate": 1.0,
  "mean_surplus_share": 0.6053981082403139,
  "median_surplus_share": 0.6026315789473684,
  "min_surplus_share": 0.4,
  "max_surplus_share": 0.9016393442622951,
  "mean_messages_used": 8.825,
  "reasks": 0,
  "retries": 1,
  "buyer_mandate_violations": 0,
  "seller_mandate_violations": 0,
  "buyer_violation_rate_retained": 0.0,
  "seller_violation_rate_retained": 0.0,
  "episodes_attempting_message12": 5,
  "episodes_completing_message12": 5
}
```

Mandate rates use non-excluded episodes, including impasse zeros. Surplus shares are unclipped; exclusions are not impasses.
Pair-pooled distributions and length counts are in `pair_pooled_outcomes.csv` and `pair_episode_lengths.csv`.

## Acceptance-price mismatches

| Responding model | Valid acceptances | Mismatching supplied prices |
| --- | --- | --- |
| `claude_sonnet_5_5` | 11 | 0 |
| `gpt_6_1_terra` | 19 | 0 |
| `gemini_4_hydrogen` | 29 | 0 |
| `kimi_k3_1_pro` | 21 | 0 |

These counts pool all labels and pairs. Role breakdowns are retained in the audit/CSV. An accept is valid at the latest opposite offer; its supplied price is recorded and ignored. There is no automatic frequency-based fix threshold; interpretation belongs to the researcher.

## Versions and usage

| Model | Expected | Returned | Responses | Missing reasoning | Missing cache read/write |
| --- | --- | --- | --- | --- | --- |
| `claude_sonnet_5_5` | `claude-sonnet-5-5` | `['claude-sonnet-5-5']` | 175 | 0 | 0/0 |
| `gpt_6_1_terra` | `gpt-6.1-terra` | `['gpt-6.1-terra']` | 201 | 0 | 0/0 |
| `gemini_4_hydrogen` | `gemini-4-hydrogen` | `['gemini-4-hydrogen']` | 155 | 0 | 155/155 |
| `kimi_k3_1_pro` | `kimi-k3.1-pro` | `['kimi-k3.1-pro']` | 175 | 0 | 41/2 |

Longest provider-counted prompt: 1514 tokens. Missing usage stays null, distinct from zero. Cache omissions are reported without imputation; complete per-call usage is in `usage_calls.csv`.

## Episode lengths

```json
{
  "6": 4,
  "7": 18,
  "8": 14,
  "9": 17,
  "10": 11,
  "11": 11,
  "12": 5
}
```

Episodes attempting message 12: 5; completing it: 5.

## Review boundary

Flags: ['all_model_turn_classes_observed'].
Unfinished identities: [].
No settings or prompts were changed based on outcomes. Only mechanical fixes may be proposed, and each requires researcher approval before implementation. Pilot data never enter main inference.
