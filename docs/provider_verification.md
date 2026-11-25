# Provider verification — 2026-11-25

**Documentation verified; four live smoke requests accepted on 2026-11-25.**
The offline HTTP tests use in-memory transports and fake credentials. The separate,
explicitly approved live invocation is recorded in `data/study1/smoke/attempts.jsonl`.
See [the smoke report](phase4b_report.md) for observed metadata and limitations.
Test fixture version strings remain synthetic; they are not smoke observations.

## Verified request mappings

All calls are fresh, self-contained requests. No temperature/top-p/top-k,
conversation IDs, tools, or extra thinking-visibility switches are sent.

| Model ID | Endpoint | Low effort | Output cap | JSON output | Caching |
| --- | --- | --- | --- | --- | --- |
| `claude-sonnet-5-5` | Messages | `output_config.effort: low` | `max_tokens: 8192` | `output_config.format`, JSON schema | Omit all `cache_control` |
| `gpt-6.1-terra` | Chat Completions | `reasoning_effort: low` | `max_completion_tokens: 8192` | `response_format`, strict JSON schema | Explicit-only cache mode, no breakpoints |
| `gemini-4-hydrogen` | Developer API `generateContent`, v1beta | `thinking_config.thinking_level: low` | `max_output_tokens: 8192` | JSON MIME type and `response_json_schema` | Implicit only; keep provider-counted input below 4,096 |
| `kimi-k3.1-pro` | OpenAI-compatible Chat Completions | `reasoning_effort: low` | `max_completion_tokens: 8192` | `response_format`, strict JSON schema | Automatic defaults, no override |

Locked SDK versions: Anthropic 2.14.0, OpenAI 3.59.0 (also Moonshot), Google Gen AI
3.6.1. Documentation confirms all four IDs and requested settings. No model or
effort was substituted. All caps include reasoning according to provider rules.

### Anthropic evidence

The [model page](https://platform.claude.com/docs/en/models/sonnet-5-5/overview)
confirms the ID/output capacity. The [Messages reference](https://platform.claude.com/docs/en/api/messages/create)
defines output configuration, stop reasons, and usage. The [effort guide](https://platform.claude.com/docs/en/build-with-claude/effort)
confirms low effort and default adaptive thinking; no thinking override is added.
[Caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)
is opt-in through `cache_control`.

The [structured-output guide](https://platform.claude.com/docs/en/build-with-claude/structured-outputs)
excludes numeric bounds. Only the submitted Anthropic schema omits minimum and
maximum. The approved 0–100 prompt wording and canonical local validator retain
them. This is the fallback explicitly permitted in protocol Section 2.2, not a
new design choice. No SDK schema helper adds wording to the prompt.

### OpenAI evidence

The [model page](https://developers.openai.com/api/docs/models/gpt-6.1-terra)
confirms identity/low effort. The [Chat Completions reference](https://developers.openai.com/api/reference/resources/chat/subresources/completions/methods/create)
specifies the cap, strict schema, storage default, and counters. The
[schema guide](https://developers.openai.com/api/docs/guides/structured-outputs)
supports bounds for this non-fine-tuned model.
[Caching](https://developers.openai.com/api/docs/guides/prompt-caching) documents
that explicit mode without breakpoints does not use prompt caching. We use
system/user messages and `store: false` (its default); Responses is not used.

### Google evidence

Google's prior URLs redirect to official AI Studio documentation. The
[Hydrogen page](https://aistudio.google.com/docs/models/gemini-4-hydrogen),
[generateContent thinking guide](https://aistudio.google.com/docs/thinking?generate-content=true),
and [structured-output guide](https://aistudio.google.com/docs/structured-output?generate-content=true)
confirm identity, low effort, cap behavior, and numeric-schema support.
The [cache guide](https://aistudio.google.com/docs/caching) sets Hydrogen's
implicit threshold at 4,096. The [API reference](https://aistudio.google.com/api-reference/generate-content)
defines version, stop, and usage fields.

The [long-decode guide](https://aistudio.google.com/docs/long-decode?generate-content=true)
describes SDK continuation. Automatic continuation and function calling are
disabled so one runner attempt sends one request. No `include_thoughts` switch
is sent. The SDK raw-body option retains JSON without recording response headers.
The locked SDK uses native `thinking_level: LOW` inside `thinkingConfig`;
[ProtoJSON accepts native and camelCase field names](https://protobuf.dev/programming-guides/json/#field-names-as-json-keys).
Dictionary and typed-config serialization were checked without a live call.

### Moonshot/Kimi evidence

Moonshot's former docs redirect to its official Kimi platform. The
[model list](https://platform.kimi.ai/docs/models) and
[model guide](https://platform.kimi.ai/docs/guide/kimi-k3-1-pro-quickstart) confirm
the ID and `https://api.moonshot.ai/v1` origin. The
[parameter reference](https://platform.kimi.ai/docs/api/models-overview.md)
specifies low effort and fixed sampling defaults; these sampling fields are omitted.
The [Chat reference](https://platform.kimi.ai/docs/api/chat.md) defines the cap,
reasoning content, stop reasons, and counters. The
[response_format guide](https://platform.kimi.ai/docs/guide/response_format)
supports strict schemas; its official validator lists
[numeric keywords](https://github.com/MoonshotAI/walle/blob/main/model.go) and
[range validation](https://github.com/MoonshotAI/walle/blob/main/keyword_validators.go).
No validator dependency was added.
The [cache guide](https://platform.kimi.ai/docs/guide/context-caching) documents
automatic default 5-minute writes and separate read/write counters; no TTL or
caching override is sent.

## Response normalization

| Provider | Version / stop | Input / output / reasoning | Cache read / write |
| --- | --- | --- | --- |
| Anthropic | `model`, `stop_reason` | `usage.input_tokens`, `output_tokens`, `output_tokens_details.thinking_tokens` | `usage.cache_read_input_tokens`, `cache_creation_input_tokens` |
| OpenAI/Moonshot | `model`, first choice `finish_reason` | `usage.prompt_tokens`, `completion_tokens`, `completion_tokens_details.reasoning_tokens` | `usage.prompt_tokens_details.cached_tokens`, `cache_write_tokens` |
| Google | `modelVersion`, first candidate `finishReason` | `usageMetadata.promptTokenCount`, `candidatesTokenCount`, `thoughtsTokenCount` | `usageMetadata.cachedContentTokenCount`; writes unavailable/null |

Provider definitions are retained. Google output excludes thoughts; the other
output totals include reasoning. Anthropic input excludes cache reads/writes,
while Chat input includes them. Raw JSON retains every original breakdown.
Missing fields remain null, never inferred as zero; required missing metadata
must be reported in the smoke test.

Anthropic/OpenAI SDK retries are zero; Google attempts are one. The runner owns
all retries/re-asks. Errors retain category/status/retryability without raw text
or headers. Exact SDK arguments are frozen in `request.api_payload`, separately
from the canonical `json_schema`; local `context` is never forwarded.

## Live smoke outcome

`data/study1/smoke/manifest.jsonl` has the original four frozen requests, also
shown in `docs/smoke_request_review.md`. One approved programmatic invocation
used the provider factory and existing runner with local keys: four valid replies,
four attempts, no retries/re-asks, and no cap stops. The CLI stays mock-only.

Observed inputs were 233–539 tokens, below 4,096 for all four. All reasoning
counters were present. OpenAI/Anthropic cache reads and writes were zero. Kimi
reported 256 cache-write tokens but omitted its cache-read count; Google omitted
cache counts. Missing fields remain null. Returned versions matched the requested
model IDs without more specific build suffixes. These observations do not prove
behavior across other tasks, repeated calls, or future versions. In particular,
the missing Kimi cache-read metadata needs researcher review before the pilot.

Authorization was **4 planned draws**, at most **32 HTTP attempts in one
invocation**. Only four attempts were used. No further real calls, account
top-ups, or subsequent phases are authorized by this completed invocation.
