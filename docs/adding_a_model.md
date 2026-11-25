# Adding a model — implementation outline

The current phase provides configuration only. Provider adapters and the common
client interface will be implemented after the mock engine.

1. Add a stable key, lab, exact display name, API model ID, provider, and key
   environment-variable name to `configs/models.yaml`.
2. Verify the provider's current official documentation for the intended model,
   endpoint, stateless behavior, low reasoning effort, sampling defaults, output
   schema, output cap, and cache controls. Stop and ask about any mismatch.
3. Implement a short adapter behind the shared client interface. Reuse official
   SDKs; Kimi uses the OpenAI SDK with a verified Moonshot base URL.
4. Map the raw response, returned model version, default reasoning text, stop
   reason, and all token/cache counts without fabricating missing zeros.
5. Add offline request/response fixtures and tests, plus the model to mock runs.
6. Obtain approval before any real smoke calls, state the call count, and record
   results and any design change in `docs/decisions.md`.

Changing the four-model roster for this study is a design change requiring the
researcher's approval. The engine should also support separate fresh experiments
with other rosters through configuration.
