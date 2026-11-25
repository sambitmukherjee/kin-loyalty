# Phase 4a report — 2026-11-25

## Completed work

Pushed Phase 3 commit `a356aed` before starting this phase, as requested. Reviewed
current official provider documentation and implemented the four SDK adapters.
All specified model IDs/settings are documented; live acceptance is still pending.
No provider/model API calls were made, and no real keys were read by the tests.

The [verification report](provider_verification.md) records exact parameter and
usage mappings, official sources, and the locked SDK versions. Anthropic's
unsupported numeric bounds use the fallback already allowed by the protocol:
its submitted schema omits bounds, while approved wording and canonical local
validation keep the 0–100 restriction. No prompt/model/sampling substitution was
made. The 18 approved experimental text files are unchanged.

Manifests now freeze exact SDK method arguments as well as canonical schemas.
No local condition/answer metadata is forwarded. SDK retries and Google's
automatic continuation/function calling are disabled so the runner owns each
attempt. Full JSON response bodies are retained without headers. Default returned
reasoning and missing-vs-zero token fields are preserved.

## Files created or changed

| Files | Work |
| --- | --- |
| `clients/anthropic.py`, `openai.py`, `google.py`, `moonshot.py` under `src/kinloyalty/` | Four official-SDK adapters with explicit reviewed endpoints and safe error translation |
| `clients/payloads.py`, `response_data.py`, `factory.py` | Frozen argument mapping, body normalization, credential loader, provider routing/resource cleanup |
| `clients/base.py`, `mock.py`, `__init__.py` | Optional API snapshot, shared cleanup contract, current status |
| `src/kinloyalty/manifest.py` | Freeze verified transport/settings and SDK argument snapshots |
| `configs/models.yaml`, `.env.example` | Documentation-verified metadata, exact transport settings, credential guidance |
| `tests/test_provider_clients.py`, configuration test | Official-SDK in-memory HTTP and credential tests, verification status |
| `data/study1/smoke/manifest.jsonl` | Four prepared real-smoke requests; generation only |
| `docs/smoke_request_review.md`, `provider_verification.md` | Concrete request review and primary-source evidence |
| README, engine/data/model guides, decision log | Updated capabilities, field definitions, approvals, and pending live scope |

No dependency or lock-file changes were needed. No smoke logs, main manifest,
main observations, or pre-registration lock were produced. The public CLI still
supports mock execution only.

## Checks

The SDK tests use in-memory HTTP transports with fake credentials and blocked
socket connections. They exercise all four tasks/providers, low-effort/cap/schema
serialization, default sampling, cache controls, raw-body fidelity, default
reasoning, usage/version capture, safe HTTP/transport failures, no hidden SDK
retries, frozen-payload guards, `.env` handling, and runner-controlled retries.
No real endpoint is used to obtain these results.

Run from the project folder:

```sh
.venv/bin/pytest
.venv/bin/pytest tests/test_provider_clients.py
```

Final result: **252 offline tests passed**, including **54 provider-specific
tests**. Offline wheel/source builds and archive checks passed. The smoke plan
regenerates identically, its review matches every frozen argument and SHA-256,
and syntax/public docstrings, unchanged prompts, and Git ignore rules passed.

## Prepared approval and remaining work

Inspect [the four actual SDK requests](smoke_request_review.md) and the committed
manifest. Phase 4b would load local keys, execute this manifest once through the
provider factory/runner, and report parse success, returned versions, token/cache
fields, prompt sizes, stop reasons, and any documented-vs-live differences.

The scope is **4 planned calls, at most 32 HTTP attempts in one invocation** under
the existing API-error retries and identical re-ask policy. No account top-up or
automatic extra invocation is included. Keys should be supplied locally via
`.env`/environment variables, never in chat. Phase 4b needs explicit approval and
has not started. Phase 4a ends with a local commit, not a push.
