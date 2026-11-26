# Data dictionary — manifest and attempt schema version 1

Manifest, request, response, attempt records, and analysis tables are implemented.
Four live smoke requests were accepted; observed metadata and
limitations appear in `docs/phase4b_report.md`. See `docs/provider_verification.md`
for primary sources.
Missing provider metadata stays distinguishable from zero. Current mock records
have `synthetic: true`; their usage counts are synthetic, not provider measurements.

## Rendered prompts and response schemas

`kinloyalty.prompts.RenderedPrompt` contains `system_prompt`, `user_message`,
`json_schema`, and `counterparty_model_text`. Messages preserve internal template
whitespace and contain no trailing newline. These fields will be copied into
the request logs; analysis will use saved logs rather than render prompts again.

`kinloyalty.schemas.response_schema` creates a new schema for each request. Every
listed field is required and extra fields are disallowed. Amounts have integer
type and canonical inclusive 0–100 bounds, followed by a string `reason`; the
proposer's belief follows its offer and precedes the reason. The comprehension
schema contains only `same_model`, restricted to strings `yes`, `no`, or `unsure`.

The exact schemas are printed in `docs/study1_prompt_review.md`. If verified
provider support requires omitting numeric bounds from the API schema, local
validation must still enforce them. The reason is requested as one sentence in
the prompt; a sentence-count heuristic is not part of these schemas. Provider
support has been checked for the four smoke requests; canonical local validation
is implemented.

## Trial manifests

One JSONL object per planned draw, generated deterministically from configuration
and a fixed seed. Every batch, including smoke, gets a manifest before calls.

| Field | Type | Meaning |
| --- | --- | --- |
| `schema_version` | integer | Record contract version, currently 1 |
| `trial_id` | string | Study/phase/model/decision/label/paraphrase/draw identity; independent of execution position |
| `study`, `phase` | strings | Study identifier; `smoke`, `pilot`, `comprehension`, or `main` |
| `model`, `model_display_name`, `api_model_id` | strings | Stable model key, exact display name, requested API ID |
| `decision`, `label` | strings | Decision task and counterparty condition code |
| `counterparty_model_text` | string | Exact card model text; empty for human |
| `other_model` | string/null | Explicit roster key named by other_lab; null otherwise |
| `paraphrase_id` | integer | Wording/name-pair identifier, 1–3 |
| `principal`, `counterparty` | strings | Rendered name pair |
| `draw_index` | integer | One-based repetition within this model/decision/label/paraphrase cell |
| `execution_position` | integer | One-based position in the seeded plan |
| `order_seed`, `mock_seed` | integers | Phase shuffle seed and default synthetic-response seed |
| `source_sha256.study_config`, `source_sha256.model_config` | strings | Exact source YAML byte hashes |
| `source_sha256.templates` | object | Template filename → exact SHA-256 byte hash, including all text templates |
| `runner_settings` | object | Frozen default policy; fields below |
| `request` | object | Frozen complete request and local context; fields below |

The manifest must preserve the 7/7/6 other-lab rotation and exact main counts.
The comprehension manifest has 320 draws, four card labels, and its own rotations.
Manifest file hashes and generation seeds will be recorded at pre-registration.

### Request object (`ModelRequest`)

This object appears unchanged in both manifests and logs. Real adapters must
construct API arguments explicitly; local `context` is never forwarded.

| Field inside `request` | Type | Meaning |
| --- | --- | --- |
| `trial_id` | string | Must match the outer trial identity |
| `provider`, `api_model_id`, `endpoint` | strings | Requested provider, model, and endpoint; no destination is contacted in mock mode |
| `settings` | object | Non-secret specification: stateless flag, effort, output cap, sampling defaults, parameter mapping, caching policy, verification status, and transport (base URL, Google API version, numeric-schema-bound support) |
| `system_prompt`, `user_message` | strings | Full rendered message content, with no added retry/corrective text |
| `json_schema` | object | Canonical response schema with numeric bounds |
| `context` | object | Local-only metadata used by the mock; `label` and, for comprehension, `expected_answer` |
| `api_payload` | object/null | Exact frozen SDK method arguments, including submitted response schema; null/absent in older mock-only manifests |

Exact mappings are in `docs/provider_verification.md`; the prepared smoke plan
freezes them. All four frozen smoke requests were accepted. Anthropic's submitted schema omits
unsupported numeric bounds while the canonical `json_schema` retains them.
Google SDK-only raw-response/continuation controls are included in the snapshot
but are not API generation fields. Keys, headers, and raw SDK exception text do
not belong in this object. Changes to destination/version require a new review.

### Runner policy (`runner_settings` / `runner_policy`)

| Field | Type | Default and meaning |
| --- | --- | --- |
| `concurrency` | integer | 4 simultaneous trials |
| `per_model_concurrency` | integer | 1 simultaneous trial per focal model |
| `timeout_seconds` | number | 120 per call |
| `api_attempts_per_response` | integer | 4, including the first API attempt, separately for each response opportunity |
| `backoff_initial_seconds`, `backoff_multiplier`, `backoff_max_seconds` | numbers | 1, 2, 30; exponential API-error backoff |
| `invalid_reasks` | integer | 1 fresh identical request after an invalid reply |

The manifest's `runner_settings` is the default. Logs also record the actual
`runner_policy`, including test overrides. Resume cannot change the invalid
re-ask policy for existing history.

## Append-only attempt logs

Every API attempt, including API errors and invalid answers, gets one record.
Retries/re-asks keep the trial ID and increment the attempt number. Analysis
reads these saved records; it never reconstructs prompts to recover outcomes.

Every manifest field above is copied into the attempt record, including its
frozen `request`, source hashes, design cell, and planned order. Additional fields:

| Field | Type | Meaning |
| --- | --- | --- |
| `record_id` | string | Trial ID plus monotonically increasing `/attempt-NNNN` |
| `run_id` | string | UUID for one runner invocation |
| `attempt_number` | integer | All attempts of this trial, including API errors, across resumes |
| `response_number` | integer | Response opportunity: 1 initially, 2 after the first invalid reply; API errors do not advance it |
| `api_retry_index` | integer | API attempt within this response opportunity and runner invocation; starts at 1 on resume |
| `dispatch_sequence` | integer | Actual globally increasing attempt reservation order across resumes; differs from planned/completion order |
| `manifest_sha256`, `trial_sha256` | strings | Exact manifest-file hash and serialized trial hash; schema property order is preserved |
| `execution_mode` | string | `mock` or `live`; backend identity checked on resume |
| `synthetic` | boolean | True for mock data; main analysis must reject it unless explicitly testing with mock data |
| `timestamp_utc` | string | ISO-8601 UTC attempt start/reservation time |
| `completed_at_utc` | string/null | Completion/log-close time; recovery time for a formerly unknown attempt |
| `latency_seconds` | number/null | Measured client-call latency; unknown after hard interruption |
| `git_commit` | string/null | Code HEAD when provenance was collected; null outside a Git checkout |
| `code_dirty` | boolean/null | Whether that checkout had uncommitted changes; null if unavailable |
| `package_version` | string | Running package version |
| `sdk_versions` | object | `anthropic`, `openai`, `google-genai` installed versions; null if unavailable; SDKs are not imported |
| `runner_policy` | object | Actual infrastructure/re-ask settings, defined above |
| `response` | object/null | Full normalized response below; null for API errors/unknown completion |
| `api_error` | object/null | Safe kind, retryability, and status; null after a model response |
| `outcome` | object | Parsed/valid/final/excluded state below |

### Response object (`ModelResponse`)

| Field inside `response` | Type | Meaning |
| --- | --- | --- |
| `output_text` | string | Full output to parse |
| `returned_model_version` | string/null | Exact returned model version; mock uses `mock/<requested ID>` |
| `raw_response` | object | Full response body as supplied by the adapter; no headers/keys |
| `reasoning_text` | string/null | Reasoning returned by default only |
| `finish_reason` | string/null | Raw provider stop reason |
| `output_truncated` | boolean | Adapter-normalized output-cap truncation; known raw cap reasons also invalidate a reply |
| `usage.input_tokens`, `usage.output_tokens` | integer/null | Provider counts, or explicitly synthetic mock counts |
| `usage.reasoning_tokens` | integer/null | Reasoning usage; unavailable stays null |
| `usage.cache_read_tokens`, `usage.cache_write_tokens` | integer/null | Cache usage, preserving unavailable versus observed zero |

Mock input/output counts are simple word counts and reasoning usage is seeded
synthetic data. They must never be reported as actual tokenizer/provider usage.

Real adapters retain provider definitions: Google output is candidate tokens
excluding thoughts; Anthropic/OpenAI/Moonshot output includes reasoning.
Anthropic input excludes cache reads/writes, while Chat Completions input includes
them. Full raw JSON retains all original counters. Google cache writes are not
exposed and remain null. Exact field paths are in `docs/provider_verification.md`.
In the observed smoke responses, Kimi omitted its cache-read count but returned
256 cache-write tokens; Google omitted cache-read and cache-write counts. These
missing counts remain null. All four reasoning counts were present, including
Anthropic's observed zero. Returned version strings equaled the requested model
IDs; no more specific build identifiers were returned.

### Outcome and API-error objects

| Field | Type | Meaning |
| --- | --- | --- |
| `outcome.valid` | boolean/null | True for a valid reply, false for an invalid model reply, null for API errors/unknown completion |
| `outcome.parsed_json` | object/null | Parsed JSON if available; no guessed answer for truncation/API errors |
| `outcome.invalid_reason` | string/null | Invalid JSON, schema fields/type/range/enum mismatch, or output truncation |
| `outcome.is_final` | boolean | Valid or excluded; false for the first invalid reply and all unfinished API errors |
| `outcome.excluded` | boolean | True only after the second invalid reply under the Study 1 policy |
| `api_error.kind` | string | `rate_limit`, `timeout`, `server_error`, `connection`, `authentication`, `bad_request`, `unknown`, or `interrupted` |
| `api_error.retryable` | boolean | Whether this API error can use the remaining automatic retry budget |
| `api_error.status_code` | integer/null | HTTP status if known; no headers or raw exception message |

Schema integer semantics accept finite mathematically whole numbers such as 1.0;
booleans and fractional values are invalid. JSON field order and sentence count
are prompt instructions, not extra exclusion tests.

### Sidecars and completion summaries

`<log>.pending.json` is an atomically replaced object mapping reserved record IDs
to complete pre-call records. Its response/error/validity are null and final/
excluded are false. On restart, unknown reservations become interrupted,
unfinished attempt records; already-appended reservations are removed without
duplication. The sidecar disappears when empty. `<log>.lock` is an empty ignored
advisory-lock file. See `docs/engine.md` for partial-write recovery limits.

The JSON CLI summary has integer `planned`, `already_final`, `valid`, `excluded`,
`calls_started`, `recovered_attempts`, and `attempt_records_written`, plus the list
`unfinished_trial_ids`. Valid/excluded totals include prior finished draws;
calls/record counts describe this invocation. Recovered records count as written
records, not newly started calls. No outcomes or label comparisons are computed.

## Tidy decision tables

One row per final valid **main-phase** draw, retaining trial and design-cell
identifiers, outcome dollars, proposer belief when applicable, and provenance.

| Decision | Outcome field | Additional field |
| --- | --- | --- |
| Dictator | `amount_to_counterparty` | — |
| Ultimatum proposer | `amount_offered_to_counterparty` | `smallest_offer_you_expect_counterparty_to_accept` |
| Ultimatum responder | `smallest_amount_for_your_user_you_will_accept` | — |

Amounts must be whole dollars in [0, 100]. Every decision reply also includes a
one-sentence `reason`. The loader verifies saved histories and includes only the
final valid reply per main draw. `decisions.csv` retains model key/display/API ID,
decision, label, paraphrase, draw, counterparty model text/key, outcome, proposer
belief (otherwise empty), returned model version, trial/record IDs, code commit,
and manifest hash. The original reason and full request remain in the attempt log.

Excluded and unfinished draws are not valid outcome rows. Their counts and
re-asks must remain available for diagnostics by model × decision × label.
Smoke, pilot, and comprehension decisions must never enter the main outcome
analysis. Mock records exist only for offline validation.

## Implemented analysis artifacts

CSV files use a header row, UTF-8, stable row order, and 12 significant digits
for floating-point values. Empty numeric cells mean missing values, never zeros.
All point estimates and interval limits are dollars. Methods/seeds are specified
in `analysis.md` and the versioned study configuration.

| Artifact | Rows and fields |
| --- | --- |
| `decisions.csv` | One final valid main draw; fields described above |
| `coverage.csv` | Model × decision × label × paraphrase: planned, valid, excluded; inference requires no unfinished/not-started draws |
| `descriptives.csv` | Model × decision × label: n, mean, median, sample SD, shares at $50 and $0, modal share, distinct values |
| `attempt_diagnostics.csv` | Model × decision × label: observed draws, valid, re-asked draws, excluded, unfinished, attempts, API errors |
| `contrasts.csv` | 150 rows: decision, outcome (`outcome`/`belief`), method (`unadjusted`/`belief_adjusted`), left/right labels, family, model/pooled scope, primary/secondary designation, estimate, count-matched percentile bootstrap 95% interval and its method/level, two-sided permutation p-value and shared tie tolerance, resampling counts, interpretation, point/interval availability and reasons, unavailable bootstrap count, non-estimable model names |
| `equivalence.csv` | Always one pooled P1 row: estimate, bound, alpha, conservative-tie lower/upper tail counts, shared tie tolerance, bootstrap count, corrected one-sided p-values, their maximum (`p_tost`), equivalent boolean, tolerance-aware strict-inside flag, and both 90%/95% percentile intervals with levels/methods/one-based endpoint ranks |
| `s1_coefficient_changes.csv` | 30 rows: contrast/scope, `unadjusted_minus_adjusted` offer coefficient and paired count-matched percentile bootstrap 95% interval with method/level; descriptive association, no extra p-value or explained-share ratio; explicit point/interval availability and reasons |
| `s1_belief_diagnostics.csv` | One row per model: retained valid proposer n, unique beliefs, nonmodal draw count/share, required count/percent, lowest-mode tie rule, rank status, estimability/reason, bootstrap fits attempted and numerical failures |
| `s1_belief_cell_counts.csv` | Model × label × paraphrase: retained n, lowest tied mode, modal and nonmodal draw counts; audit of the fixed 10% rule |
| `usage_calls.csv` | Every attempt: record/trial ID, model/provider, response presence, validity, returned version, stop/truncation, all five usage counters; API errors have empty response fields |
| `usage_summary.csv` | Model/provider × usage metric: responses, observed/missing counts, mean, median, minimum, maximum; missing counts are computed only among actual responses |
| `comprehension.csv` | Optional separate batch: model × card, planned/valid/excluded/unfinished/not-started, completion flag, yes/no/unsure counts and shares of planned 20, correct/scored status, label/model pass |
| `resampling_distributions.npz` | Named arrays of bootstrap estimates and permutation null statistics for every outcome/method/contrast/scope; includes the pooled P1 draws used by TOST |
| `provenance.json` | Synthetic flag/interpretation, exact input/config/package-source hashes, analysis settings/seeds, dependency versions, code provenance |
| `artifacts.sha256.json` | SHA-256 of every generated artifact except itself |

The NPZ keys have the form
`decision:outcome:method:left-right:scope:bootstrap|permutation`. Arrays use the
configured 10,000 entries. Scope is a configured model key or `pooled`.
All intervals use `ci_method: percentile_count_matched`: for 10,000 draws, 90%
selects one-based ranks 500/9501 and 95% selects 250/9751, with no interpolation.
`equivalence.csv` uses `equivalence_ci_*` for 90% and `contrast_ci_*` for 95%.
The latter agrees with the pooled P1 row in `contrasts.csv`. Equivalence requires
90% endpoints beyond the shared numerical tie band and both conservative-tail,
+1-corrected p-values strictly below .05. `INFERENCE_TIE_TOLERANCE = 1e-12`
is defined once in `inference.py`, reported as `permutation_tie_tolerance` in
contrasts and `inference_tie_tolerance` in equivalence/provenance. TOST counts
use `<= -5 + epsilon` and `>= +5 - epsilon`; its 90% check uses `low > -5 + epsilon`
and `high < +5 - epsilon`. No new random draws are generated for TOST or either level.
Paired coefficient changes add arrays with method `unadjusted_minus_adjusted`.
Numerically singular adjusted bootstrap replicates remain NaN, with no deletion
or redraw. Affected confidence intervals are unavailable, even if the observed
point is identifiable. A model failing the fixed observed-sample count rule has
unavailable adjusted arrays/results; the pooled four-model target remains
unavailable as well. Unavailable point/interval values in CSV are empty, with
`estimable`, `not_estimable_reason`, `interval_available`,
`interval_unavailable_reason`, `bootstrap_unavailable_count`, and
`non_estimable_models` distinguishing the reasons. No model is silently omitted.

Figures `main_distributions`, `responder_distributions`, and `s1_coefficients`
are saved as both `.pdf` and `.png`; `comprehension` adds a table figure in both
formats when the separate batch is supplied. Synthetic titles identify simulated
data. PDF creation/modification dates are omitted for deterministic artifacts.

## Separate pilot and comprehension reports

`report pilot` writes `pooled_descriptives.csv`,
`pooled_attempt_diagnostics.csv`, `pooled_decisions.csv`, `mechanical_checks.csv`,
usage tables, and provenance/artifact hashes. Decision grouping is model ×
decision, never label. The pooled decision export includes only model, decision,
outcome, and belief; audit identifiers remain in the source logs. Mechanical
checks report coverage, response validity rate (>95%), truncation, missing
reasoning/input/cache counts, zero-cache verification when required, prompt-size
checks, dictator floor status, and decision variation. Usage audit rows retain
record IDs, but no decision-outcome comparison by label is computed.

`report comprehension` writes `comprehension.csv`, usage tables, and provenance/
artifact hashes. Planned denominator 20 includes excluded draws as non-correct.
Unfinished/not-started draws prevent final pass/fail classification; undisclosed
remains unscored. A failed model is retained in the study. Neither report changes
configuration or automatically starts another batch.

## Phase 6 cohort artifacts

Pilot/comprehension each retain their frozen manifest, append-only attempt log,
and the ordinary `run_summary.json` fields defined above. The cohort does not
merge either raw dataset or their outcomes.

`data/study1/phase6_cohort_summary.json` records status, UTC start/completion,
authorized maximum attempts, actual calls started, and each batch's mechanical
summary. `docs/phase6_execution_plan.json` records the approved scope, one
invocation per batch, shared concurrency caps, exact policies and plan hashes.
`docs/phase6_audit.json` records observed code revision, counts, log/manifest
hashes, safe API-error categories/statuses, per-model returned versions/stops,
token/metadata presence, measured concurrency maxima, and local execution times.
These are audit/completion artifacts, not outcome-effect estimates.

## Study 2 Phase 2 objects (in memory)

The objects below belong to `kinloyalty.negotiation` and do not change Study 1's
manifest/attempt schema. They are the current mock engine contract. Durable
Study 2 JSONL envelopes, manifest bindings, provenance, and replay commands are
described in the Phase 3 section below. Real collection remains separately gated.

| Object / field | Meaning |
| --- | --- |
| `EpisodeSpec` | Episode ID, phase, actual buyer/seller model keys, disclosure condition, scenario, and explicit swapped self-pair alternative |
| `EpisodeSpec.custom_cards` | Optional `(buyer_card, seller_card)` texts for engine reuse; unset for Study 2; marked in local request metadata |
| `EpisodeState.scenario`, `message_limit` | Condition-independent facts and configured total message limit |
| `EpisodeState.turns` | Ordered valid committed public turns; each retains role, message, action, and original supplied price |
| `EpisodeState.outcome` | Null while unfinished; one `deal`, `walk_away_impasse`, `final_message_impasse`, or `excluded` outcome when terminal |
| `Outcome.deal_price`, `accepted_by` | Counterparty's latest offer price and accepting role for a deal; null otherwise |
| `Outcome.accept_price_mismatch` | Acceptance supplied a non-null value different from the accepted offer; never changes the deal price |
| `Outcome.excluded_role`, `exclusion_message_number` | Actor and failed position after the original invalid response and its invalid re-ask |
| `Score.buyer_surplus_share` | Unclipped `(b-p)/(b-s)` on deals, zero on impasses, null for exclusions |
| `Score.buyer_mandate_violation`, `seller_mandate_violation` | Accepted price exceeds buyer maximum / falls below seller minimum; false on impasses, null for exclusions |

`schemas.response_schema` requires `message` (string), `action` (the turn-specific
enum), and `price` (nullable integer, minimum 1), with no extra properties. The
local validator requires a positive whole-dollar offer and explicitly ignores
and records any supplied non-offer price, as approved by the researcher. Numeric
integer-equivalent prices compare equal; nonnumeric supplied acceptance values
flag as mismatches. Invalid JSON, duplicate keys, non-finite numbers, wrong
message/action types, forbidden actions, missing/extra fields, and truncation
remain invalid. `ReplyValidation` retains validity, the raw parsed object when
available, an invalid reason, and the valid public turn when present.

| `TurnAttempt` field | Meaning |
| --- | --- |
| `episode_id`, `phase`, `message_number`, `role`, `model` | Episode/position identity and the actual responding model key |
| `attempt_number` | Monotonic call number within the episode across explicit resumes |
| `response_number` | Original response opportunity 1 or the unique invalid-reply re-ask 2; API errors do not advance it |
| `api_retry_index` | One-based API attempt within this opportunity/invocation; restarts on resume |
| `allowed_actions`, `request` | Exact turn action list and complete stateless `ModelRequest`, including canonical schema and frozen provider payload |
| `response` | Full normalized `ModelResponse`, including raw body, default reasoning, usage, and stop/truncation metadata; null for API errors/interruption |
| `validation` | `ReplyValidation`; null for API errors/interruption |
| `api_error` | Safe kind, retryability, and status, without exception text/headers; null for a model response |
| `is_final_for_turn` | True for a valid reply or second invalid reply; a valid offer can finish a turn without finishing its episode |
| `excluded` | This second invalid reply terminated the episode as excluded |
| `accept_price_mismatch` | Same acceptance mismatch flag as the terminal outcome, attached only to the valid accepting attempt |
| `timestamp_utc`, `completed_at_utc`, `latency_seconds` | Call timing, including failed/interrupted attempts |
| `synthetic`, `execution_mode`, `is_probe` | Phase 2 uses true, `mock`, false; actual probe execution/marking is Phase 3 work |

`EpisodeProgress` keeps the specification, committed state, cumulative attempt,
re-ask and retry counts, current turn's invalid-response count, whether its
re-ask has started, whether a retry is pending, and the exact pending request.
API-error exhaustion leaves the outcome null and retains this state for explicit
resume. Resume rejects changed assignments, impossible counters, invalid state,
and a changed pending request. It restarts the API-error budget, preserves the
invalid-reply count, and grants no third model response. Re-asks count distinct
second-response opportunities; retries count calls following API errors or
interruption, including a resumed call. `EpisodeResult.attempts` contains only
the current invocation's attempts; cumulative counters live in `progress`.

The number of messages used is the number of valid committed turns. An excluded
failed position is reported separately and never appended as a valid message.
Raw non-offer prices remain in the response, parsed reply, and committed turn;
transcript rendering omits their price part. Pilot mismatch counts will group
valid accepting attempts by responding model, pool disclosure conditions, and
retain role. Probes never contribute to those counts or to inference.

The engine refuses live clients and returns detached in-memory snapshots. The
optional attempt observer also receives interrupted-call snapshots before the
exception propagates. This is not yet a durable pending journal or disk replay
format. Mock usage counts and planted label effects are explicitly synthetic.

## Study 2 Phase 3 persisted contract (version 1)

These fields extend the Study 2 objects above; they do not modify Study 1's
manifest or attempt contracts. Current execution is mock-only, with
`synthetic: true`, and writes outside real-study artifact directories.

| Manifest row field | Meaning |
| --- | --- |
| `schema_version`, `study`, `phase` | 1, `study2`, and `synthetic`/`smoke`/`pilot`/later `main` |
| `spec` | Complete `EpisodeSpec`, including private/public scenario facts and the actual buyer/seller identities |
| `pair_id`, `execution_position` | Safe pair-file identity and one-based seeded plan position |
| `scenario_seed`, `order_seed`, `swapped_seed`, `mock_seed` | Explicit design/order/simulation controls; main scenario seeds are not used by synthetic generation |
| `snapshot.study_yaml`, `models_yaml`, `templates`, `schemas` | Exact source text and all per-turn schema objects; execution/resumption reads these instead of current source files |
| `source_sha256` | Exact study/model/template UTF-8 digests and a response-schema content digest |
| `episode_sha256` | Digest of the complete row except this digest field |
| `is_probe`, `probe_role`, `probe_position` | Explicit forced-position identity; false/null/null for natural episodes |
| `initial_turns`, `probe_request` | Fixed hand-written prefix and exact request for a probe; empty/null for natural episodes |

Saved natural plans are checked for complete design balance and shared scenario
facts. Smoke plans contain four natural episodes plus all sixteen model/role/
position probes. No custom card arrangements enter a Study 2 manifest. The
low-level engine's optional-card facility remains available separately.

Per-pair turn logs copy every `TurnAttempt` field above and add:

| Attempt envelope field | Meaning |
| --- | --- |
| `schema_version`, `study`, `pair_id` | Version/study and the required per-pair placement |
| `record_id` | Episode identity plus `/attempt-NNNN`, unique and monotonic within the unit |
| `manifest_sha256`, `episode_sha256`, `source_sha256` | Exact saved plan, assignment, and source bindings |
| `run_id`, `dispatch_sequence` | Invocation UUID and globally unique one-based actual reservation order |
| `runner_policy` | Frozen timeout/retry/concurrency policy, including one invalid-response re-ask |
| `git_commit`, `code_dirty`, `package_version`, `sdk_versions` | Actual execution provenance, collected without reading credentials |
| `record_sha256` | Digest of all record content except this digest field |

Each pair log has an atomic fsynced `.pending.json` sidecar and an advisory
`.lock`. Pending records have the same binding/request/identity fields, with
unknown response/validation/completion fields. On recovery, an unmatched
reservation becomes one `interrupted` API-error attempt: response and validity
stay unknown, latency is null, and no answer/exclusion is inferred. A reservation
already represented by a matching completed record is removed without a duplicate.
Candidates and all prior histories are validated before recovery appends.

`EpisodeProgress.initial_turn_count` records the number of hand-written messages
preceding a probe. Those messages do not count as API attempts. A probe stops
after one final response opportunity, including its permitted invalid re-ask;
it does not continue an artificial negotiation after a valid message-11 offer.
Probe attempts have `phase: smoke`, `is_probe: true`. The maximum 32 probe
attempts counts completed, failed, and uncertain reserved calls across every
invocation. Budget exhaustion leaves probes unfinished rather than inventing
responses or granting a new budget on resume.

`episodes.jsonl` stores one terminal natural-episode object. It includes the
episode/pair/model/self-pair/disclosure identities, exact card text, all scenario
facts, `outcome`, `deal_price`, `accepted_by`, valid `messages_used`, the failed
position/role for exclusions, unclipped surplus and mandate flags, cumulative
attempt/re-ask/retry counts, and `accept_price_mismatch`.
`accept_supplied_price_json` losslessly serializes any supplied acceptance price;
the full raw value also remains in the accepting attempt's parsed reply and
response. Completion time is taken from the terminal attempt, allowing exact
summary reconstruction. Binding and integrity fields accompany each summary.

`probes.jsonl` instead stores unscored terminal probe status (`valid`/`excluded`),
responding model/role, message number, final parsed action when valid, and call
counts/bindings. It contains no buyer surplus or mandate score. Probe reports
include exact system/user requests and original transcript prefixes. No probe
is added to `episodes.jsonl` or to hypothesis analysis.

`run_summary.json` is a replaceable mechanical summary of planned/already-final
units, new calls, recovered attempts, repaired summaries, completed episodes/
probes, budget usage, unfinished identities, and pair-log byte sizes. It is not
an analysis input or the source of outcomes.

`kinloyalty study2 replay` revalidates responses and pure transitions from saved
turns, reconstructs counters, and compares every terminal summary. It refuses
active writers, pending calls, corrupt tails, unknown pair logs, changed
bindings/requests/decisions, and duplicate identities. Missing terminal summaries
can be repaired once by explicit runner resumption. Reply JSON content is kept
separate from transport metadata checks so the approved ignored-price exception
cannot be invalidated by arbitrary keys inside a model-supplied price object.
