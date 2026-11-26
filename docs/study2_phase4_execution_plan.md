# Study 2 Phase 4 live smoke execution plan

Date: 2026-11-26 (Asia/Kolkata).

The researcher approved the proposed Phase 4 caps and instructed that Phase 3
be pushed first. Phase 3 commit `2fc94d4576d4aeb565ea8f78a05dd7d201404433`
was pushed and its exact remote branch tip verified before this preparation.

## Authorized scope and fixed inputs

- Four natural self-pair negotiations under `not_disclosed`, one per model.
- Sixteen forced-position probes: each model, buyer/seller role, message 11/12.
  Buyer probes use the not-disclosed card; sellers see no card.
- At most 48 ordinary natural turns and 16 ordinary probe calls before any
  re-asks/retries. Natural attempts have a hard cap of 384; probes retain their
  approved hard cap of 32. The combined ceiling is 416, across resumptions.
- Exactly one identical invalid-response re-ask; four API attempts per response
  opportunity, existing 120-second timeout, and 1/2/4-second backoffs. SDK hidden
  retries remain disabled. Exclusions are counted, not replaced.
- Freeze the existing Study 2 scientific configuration, exact prompts/card text,
  all per-turn schemas, and hand-written probe prefixes. No prompt or API-setting
  substitution is part of this phase.

The externally saved 20-unit manifest has SHA-256:
`5bc7fd7065eca30be44c4ff9de8b0b43143e5e0a40ce7f9a74f982d4768321eb`.
The same manifest will be copied byte-for-byte to `data/study2/smoke/manifest.jsonl`
after collection. Actual output is initially outside the checkout so every call
can record a clean committed code revision.

The prior returned versions are read only from Study 1's locked registration:

| Requested model | Required prior returned string |
| --- | --- |
| `claude-sonnet-5-5` | `claude-sonnet-5-5` |
| `gpt-6.1-terra` | `gpt-6.1-terra` |
| `gemini-4-hydrogen` | `gemini-4-hydrogen` |
| `kimi-k3.1-pro` | `kimi-k3.1-pro` |

## Preparation and live controls

Reuse all four existing provider adapters unchanged. Load credentials only from
this checkout's ignored `.env`, explicitly excluding process environment values;
never print/store keys or headers. Source configuration's Phase 1 administrative
`natural_execution_approved: false` flag is preserved as historical source text;
the dated researcher authorization in `preflight.json` and `collection.json`
supersedes it for this smoke run only. It does not authorize pilot/main calls.

`SmokeAuthorization` binds mode, manifest, expected versions, and both budgets.
The saved contract cannot be silently replaced on resume. Counts include API
errors and uncertain interrupted reservations. Live entry points reject other
phases, mixed modes, dirty/uncommitted code, and protected Study 1 destinations.
Default Study 2 CLI execution remains mock-only. No shared client change is
needed or made.

Each response is saved before the returned-version check can halt dispatch.
Any changed or missing returned string sets `model_drift`, stops queued calls,
and raises a safe halt. In-flight calls are cancelled and logged as interrupted
if their response is unknown. Prior logged drift prevents a new invocation
from making further calls without researcher review. Pure logging/replay/report
work continues to preserve and explain the observed evidence.

Commit and test this preparation first. The dedicated live command is
`python -m kinloyalty.negotiation.smoke`, with the frozen external manifest,
external output directory, and ignored `.env` path. Its console progress contains
model/role/message/version metadata only. After execution, use the offline
`kinloyalty.negotiation.smoke_report` module for audit JSON, per-call usage CSV,
probe requests/transcripts, and a Markdown mechanical report.

Preparation verification: all **520 offline tests passed** in 70.81 seconds,
including eight new live-mode/authorization/report tests using synthetic replies
and no network. Required .env credentials were present for all four providers;
their values were not printed or stored. The locked Study 1 manifest and Phase 1
prompt-review digests are checked again before committing this preparation.

## Review and stopping boundary

Check schema acceptance for all model/role/position probes, message-12 action
restrictions, exact version matches, validity/truncation, usage/reasoning/cache
presence, prompt length below 4,096 provider-counted tokens, budget use, and replay
agreement. Do not impute missing counts as zero. Probe outcomes stay unscored and
ineligible for analysis. Include every fixed transcript prefix in the report.

Stop and report on drift, incompatible requests, exhausted budgets, or other
unresolved mechanical problems. Do not silently change API settings, model IDs,
schemas, or prompt wording. Commit raw smoke artifacts/report after collection;
push only with permission. Phase 5 (analysis on mock data) is a separate gate.
No Study 1 response log/outcome is read, and no actual Study 2 main scenario or
manifest is generated.
