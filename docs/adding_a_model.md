# Use another model or add a provider

Start with the [worked new-experiment guide](running_a_new_experiment.md) to
create separate configurations and prompts and check the complete workflow with
mocks. The registered roster in `configs/models.yaml` belongs to the completed
studies. Put a new roster in your own experiment; preserve the original file.

There are two different tasks here. Another model on an existing provider may
work with an existing adapter, after its request requirements have been checked.
A new provider, API origin or request format needs implementation work. Neither
case is established by changing an API model ID alone.

## Understand the model configuration

A study configuration selects its roster through `models_file`, resolved
relative to the study YAML file. Each model has a stable local key, such as
`claude_sonnet_5_5`, and the following information:

| Field | How the existing code uses it |
| --- | --- |
| `lab` and `display_name` | These appear in prompt identities and agent cards. Study 1 also uses labs to identify other-lab counterparties. |
| `api_model_id` | This is the requested provider model ID and is recorded separately from the returned version string. |
| `provider` | This selects the payload builder and provider adapter: `anthropic`, `openai`, `google` or `moonshot`. |
| `endpoint` | This records the intended endpoint. The adapter implements the actual SDK call; editing this text does not switch APIs. |
| `transport` | The origin and, for Google, API version are checked against the adapter's supported values. `numeric_schema_bounds` controls whether numeric bounds are included in the submitted schema. |
| `requested_parameters` and `caching` | These describe the registered mappings. They are not arbitrary SDK keyword arguments; the payload builder defines what is actually sent. |
| `api_key_env` | This records the credential name. The generic factory's actual lookup is fixed by `KEY_NAMES`; changing this field alone does not redirect credential loading. |

Roster-wide defaults supply the output cap and reasoning effort. The current
payload builder requires stateless requests with provider-default sampling.
It also accepts only the existing verification-status values. A copied
`smoke_verified` value describes a past check, not new evidence that a changed
request is accepted. See the [historical provider verification](provider_verification.md)
for the original mappings and their source dates.

## Use a model on a supported provider

1. Copy the roster into the new experiment and point the copied study
   configuration at it. Choose a stable local key and accurate display name,
   lab and requested API model ID. For negotiations, `model_order` must contain
   every model key exactly once.
2. Check the intended model's current official documentation. Confirm the API,
   supported reasoning settings, structured-output schema, output cap, sampling
   behavior and caching controls. Compare those requirements with
   [clients/payloads.py](../src/kinloyalty/clients/payloads.py) and the adapter,
   rather than assuming compatibility with an earlier model on the same service.
3. Regenerate the prompt review and manifest. Inspect the exact `api_payload`
   and canonical `json_schema`. They are distinct: an adapter may submit a
   supported subset of schema constraints while local validation retains the
   complete contract. The original Anthropic requests omitted numeric bounds
   only from the submitted schema. A new model needs its own documented reason
   for such a mapping.
4. Recheck allocation and analysis assumptions. Study 1's default design uses
   four models from four labs, three paraphrases and fixed other-lab balance.
   Its analysis figures use four model panels. A different roster size or lab
   structure can require code and count changes. Study 2 supports an explicit
   roster order, but counts, name rotation, contrasts, figures and reporting
   assumptions still need review for that roster.
5. Exercise the new requests with mocks and offline provider fixtures. Then
   plan a small live smoke batch with an explicit call budget and the new
   study's expected-version policy. Include every response-schema form the
   model will receive. Make any required research, prompt or spending approvals
   part of the new study's own record.

The [worked guide's live-collection section](running_a_new_experiment.md#6-live-collection-interfaces-and-their-limits)
explains the Python interfaces. The public `run` commands remain mock-only,
and the original Study 2 live launchers are not general-purpose launchers for a
replacement roster.

## Implement a different provider or request format

The client interface is defined in [clients/base.py](../src/kinloyalty/clients/base.py).
It consists of `execution_mode`, asynchronous `complete(request)` and
`aclose()`. A client receives a frozen `ModelRequest` and returns a normalized
`ModelResponse`, or raises a categorized `ClientError`.

The main implementation points are:

| Component | Work needed for another provider |
| --- | --- |
| [Payload construction](../src/kinloyalty/clients/payloads.py) | Add the actual SDK argument mapping and supported origin/version checks. Freeze the arguments in `request.api_payload` and verify them before sending. |
| [Provider factory](../src/kinloyalty/clients/factory.py) | Register the adapter constructor and credential-name mapping. Add any SDK dependency to the new experiment's dependency specification and lockfile. |
| [Adapter modules](../src/kinloyalty/clients/) | Implement one self-contained request, response normalization, safe error categorization and resource cleanup. The existing adapters show how runner-level retries are kept separate from SDK retries. |
| [Response normalization](../src/kinloyalty/clients/response_data.py) | Preserve response text, raw body, returned model version, reasoning text if supplied, finish reason, truncation and token/cache counts. Leave unavailable counts null. |
| [Offline provider tests](../tests/test_provider_clients.py) | Use fake credentials and in-memory HTTP transports to inspect serialized requests and normalized responses without contacting a provider. |
| New experiment launcher | Supply collection budgets, version checks and durable resumption appropriate to that study. A new provider may also need a dedicated negotiation client factory. |

Use the official SDK where suitable and record the version used by the new
experiment. Never send `request.context`: it is local metadata, not another
provider message. Keep credentials, headers and raw exception strings out of
persisted records. Normalize errors with safe kind, retryability and status
metadata so the runner can distinguish an API failure from an invalid reply.

Test valid replies, invalid JSON, truncation, unavailable usage, retryable errors
and non-retryable errors. Check that one runner attempt corresponds to one
provider call, that stateless requests have the intended messages, and that
canonical local validation is still applied after any provider-schema mapping.
A mock fixture proves these mechanics; a live smoke check establishes whether
the actual service accepts the request at that time. Neither replaces reviewing
the scientific design.

## Record the new collection

Keep requested model IDs and returned version strings separately. A returned
string is evidence about the API response, not an immutable identifier of model
weights. Record the code revision, frozen request and manifest hashes, package
versions, smoke observations and any changes made before the new main run.

The original [Study 1 smoke report](phase4b_report.md) and
[Study 2 smoke report](study2_phase4_report.md) show the kinds of mechanical
observations retained, including missing token counters. They are historical
examples rather than a current guarantee for a new model or service.
