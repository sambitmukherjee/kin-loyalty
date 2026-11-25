# Data dictionary — draft contract

This is a Phase 1 outline, not an implemented schema. Concrete types, provider
field mappings, nullability, and schema versioning will be finalized before the
runner is implemented. Missing provider metadata must remain distinguishable
from an observed zero; unsupported required fields must be reported.

## Trial manifests

One JSONL object per planned draw, generated deterministically from configuration
and a fixed seed. Every batch, including smoke, gets a manifest before calls.

| Planned field | Meaning |
| --- | --- |
| `trial_id` | Stable identity built from study, phase, cell, and draw index |
| `study`, `phase` | Study identifier and `smoke`, `pilot`, `comprehension`, or `main` |
| `model`, `model_display_name`, `api_model_id` | Stable model key, exact display name, requested API ID |
| `decision`, `label` | Decision task and counterparty condition code |
| `counterparty_model_text` | Exact model-line text; empty for a human |
| `paraphrase_id` | Wording/name-pair identifier, 1–3 |
| `principal`, `counterparty` | Rendered name pair |
| `draw_index` | One-based repetition within the smallest decision cell |
| `execution_position` | Position in the seeded, interleaved order |

The manifest must preserve the 7/7/6 other-lab rotation and exact main counts.
The comprehension manifest has 320 draws, four card labels, and its own rotations.
Manifest file hashes and generation seeds will be recorded at pre-registration.

## Append-only attempt logs

Every API attempt, including API errors and invalid answers, gets one record.
Retries/re-asks keep the trial ID and increment the attempt number. Analysis
reads these saved records; it never reconstructs prompts to recover outcomes.

| Planned field/group | Meaning |
| --- | --- |
| `record_id`, `trial_id`, `attempt_number`, `study`, `phase` | Record identity and linkage to a planned draw |
| Design-cell fields | Model, decision, label, counterparty model text, paraphrase, names, draw index |
| `timestamp_utc` | Attempt timestamp in UTC |
| `git_commit`, `package_version`, `sdk_versions` | Code and environment provenance |
| `provider`, `api_model_id`, `endpoint` | Request destination without headers or keys |
| `request_settings` | All non-secret request parameters |
| `system_prompt`, `user_message`, `json_schema` | Full rendered request text and response contract |
| `returned_model_version` | Exact version string returned by the provider |
| `raw_response` | Full response body; never request headers or credentials |
| `output_text`, `reasoning_text` | Output and any reasoning returned by default |
| `finish_reason` | Provider stop reason; identifies output-cap truncation |
| `usage.input_tokens`, `usage.output_tokens` | Provider-reported token counts |
| `usage.reasoning_tokens` | Provider-reported reasoning tokens; missing is not zero |
| `usage.cache_read_tokens`, `usage.cache_write_tokens` | Cache usage, preserving unavailable versus zero |
| `latency_seconds` | Attempt latency |
| `parsed_json`, `valid`, `invalid_reason` | Validated response and validation outcome |
| `is_final`, `excluded` | Whether the trial is finished and whether two invalid replies excluded it |
| `api_error` | Sanitized error details without credentials/headers |

The runner must distinguish successful completion, an excluded draw, and an
unfinished draw after API retries. An unfinished draw is eligible for resume.
Error/redaction handling and restart durability will be specified and tested in
the engine phase.

## Tidy decision tables

One row per final valid **main-phase** draw, retaining trial and design-cell
identifiers, outcome dollars, proposer belief when applicable, and provenance.

| Decision | Outcome field | Additional field |
| --- | --- | --- |
| Dictator | `amount_to_counterparty` | — |
| Ultimatum proposer | `amount_offered_to_counterparty` | `smallest_offer_you_expect_counterparty_to_accept` |
| Ultimatum responder | `smallest_amount_for_your_user_you_will_accept` | — |

Amounts must be whole dollars in [0, 100]. Every decision reply also includes a
one-sentence `reason`. Exact schema checks belong to the prompt/validation phases.

Excluded and unfinished draws are not valid outcome rows. Their counts and
re-asks must remain available for diagnostics by model × decision × label.
Smoke, pilot, and comprehension decisions must never enter the main outcome
analysis. Mock records exist only for offline validation.

## Reports and generated tables

- Main descriptives: n, mean, median, standard deviation, share at $50, share at
  $0, and modal share by model × decision × label.
- Estimates: named contrast, model or pooled scope, estimate, bootstrap interval,
  two-sided permutation p-value, and secondary/primary designation.
- Equivalence: configurable ±$5 bound, both one-sided tests, and pooled result;
  the exact TOST method requires approval in the analysis phase.
- S1: belief contrasts and offer contrasts with and without the belief control.
- Attempt diagnostics: re-asks, exclusions, unfinished draws, reasoning usage,
  cached usage, and truncation.
- Pilot: parse/mechanical diagnostics and outcome distributions by model and
  decision, pooled over labels; no label-effect calculations.
- Comprehension: answer shares by model × card label, scored counts, and pass/fail
  using at least 18 of 20 correct for each scored label. Undisclosed is unscored.

Exact output filenames, table columns, and types will be documented alongside
the implemented analysis. Figures will be saved as PDF and PNG.
