# Adding a model — implementation outline

The common asynchronous interface, mock engine, and four provider adapters are
implemented. All four current models accepted their live smoke requests; see
`phase4b_report.md` for observed metadata and the missing Kimi cache-read count.

1. Add a stable key, lab, exact display name, API model ID, provider, and key
   environment-variable name to `configs/models.yaml`.
2. Verify the provider's current official documentation for the intended model,
   endpoint, stateless behavior, low reasoning effort, sampling defaults, output
   schema, output cap, and cache controls. Stop and ask about any mismatch.
3. Implement a short adapter behind `clients/base.py`'s `ModelClient` interface.
   Reuse official SDKs; Kimi uses the OpenAI SDK with a verified Moonshot base URL.
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

Changing the four-model roster for this study is a design change requiring the
researcher's approval. The engine should also support separate fresh experiments
with other rosters through configuration.
