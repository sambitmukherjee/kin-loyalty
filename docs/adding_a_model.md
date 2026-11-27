# Adding a model — implementation outline

The common asynchronous interface, mock engine, and four provider adapters are
implemented. All four registered models completed both main studies. The
[original smoke report](phase4b_report.md) records the initial request checks,
including the missing Kimi cache-read count. The main collection reports and
[results READMEs](../README.md#current-status) record the completed studies.
Provider settings in this repository describe the registered experiments; a
new experiment needs its own checks against current provider documentation.

1. Create a separate model configuration for the new experiment. Add a stable
   key, lab, exact display name, API model ID, provider and credential name there.
   Preserve the original `configs/models.yaml` used by both registered studies.
2. Verify the provider's current official documentation for the intended model,
   endpoint, stateless behavior, low reasoning effort, sampling defaults, output
   schema, output cap, and cache controls. Stop and ask about any mismatch.
3. Reuse an existing provider adapter when it supports the new request. A new
   provider needs an adapter behind `clients/base.py`'s `ModelClient` interface
   and registration in the provider factory. Reuse official SDKs; the registered
   Kimi requests used the OpenAI SDK with Moonshot's base URL.
   Never forward `request.context` to a provider or include keys/headers in logs.
   Freeze exact arguments as `request.api_payload`; keep the canonical local
   schema intact if a submitted provider schema needs the permitted bound fallback.
4. Map the raw response, returned model version, default reasoning text, stop
   reason/truncation, and all token/cache counts without fabricating missing
   zeros. Normalize errors as safe `ClientError` metadata without raw exception
   strings. Establish exact request-setting mappings before freezing real plans.
5. Add offline request/response fixtures and tests, plus the model to mock runs.
6. Obtain approval before any real smoke calls, state the call count, and record
   results and any design change in `docs/decisions.md`.

The registered studies retain their original four-model roster. A new roster
belongs to a separate experiment. Changing the model count can also require
changes to allocation counts, comprehension balance and analysis assumptions;
adding an entry to a YAML file alone does not guarantee a valid design.
