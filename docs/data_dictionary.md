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
| `contrasts.csv` | 150 rows: decision, outcome (`outcome`/`belief`), method (`unadjusted`/`belief_adjusted`), left/right labels, family, model/pooled scope, primary/secondary designation, estimate, basic bootstrap 95% interval, two-sided permutation p-value, resampling counts, interpretation, point/interval availability and reasons, unavailable bootstrap count, non-estimable model names |
| `equivalence.csv` | Always one pooled P1 row: estimate, bound, lower/upper one-sided p-values, their maximum (`p_tost`), equivalent boolean, 90% basic interval and its level |
| `s1_coefficient_changes.csv` | 30 rows: contrast/scope, `unadjusted_minus_adjusted` offer coefficient and paired bootstrap 95% interval; descriptive association, no extra p-value or explained-share ratio; explicit point/interval availability and reasons |
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
