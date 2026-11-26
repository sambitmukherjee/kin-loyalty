# Adding a game — implementation outline

The engine renders configured templates, builds flat integer/string response
schemas, and executes frozen manifests. Study 1's balance algorithm is separate
from the transport-independent runner, card renderer, clients, and attempt logs.

1. Define the new decision and its outcome fields in a separate study config.
2. Write plain-text templates and a response schema, preserving neutral card and
   identity rendering. Keep person names out of JSON field names.
3. Add a deterministic manifest builder for the new design. The current validator
   supports flat required integer/string fields, bounds, and enums; extend and
   test it explicitly if a new task requires other JSON-schema features.
4. Reuse the clients, card renderer, log format, and runner patterns, keeping
   single-decision assumptions out of the shared components.
5. Add mock-client tests for valid/invalid/truncated replies and resume behavior.
6. Define analyses before observing main outcomes, and obtain any required design,
   prompt, phase, and spending approvals.

Study 2 will add a separate multi-turn negotiation engine later. Do not implement
its bargaining protocol as part of Study 1.

## Study 2 negotiation components

Study 2's offline protocol now lives separately under
`src/kinloyalty/negotiation/`. `state.py` defines scenario/assignment state;
`rules.py` supplies pure `allowed_actions`, `apply_turn`, `exclude_episode`,
`validate_state`, and `score_outcome`. `schemas.py` builds a schema for each
message number, and `validate.py` implements strict reply parsing with Study 2's
explicit non-offer-price exception. Study 1's validator is unchanged.

`requests.py` combines the exact templates, role-relative public transcript,
current mover's private limit, turn schema, and unchanged provider payload
builder. `EpisodeSpec.custom_cards` optionally supplies buyer/seller card text
for engine reuse; leave it unset for the Study 2 buyer-only assignment. Custom
arrangements are marked in local metadata and have no Study 2 analysis here.

`engine.run_episode` executes sequential turns with `NegotiationMockClient`,
scripted responses/errors, or another client declaring mock execution. Its
result contains in-memory attempt records and progress for explicit resumption.
It refuses live clients. Phase 3 now adds frozen `manifest.py` plans,
`runner.py` batch scheduling/journals, independent `history.py` reconstruction,
`collection.py` replay, and marked single-position probe execution/reporting.
Use the additive `kinloyalty study2` command group for manifest, mock run/resume,
replay, and probe-report operations. Existing Study 1 commands are unchanged.
See `docs/study2_phase3_report.md` and the Study 2 sections of
`docs/data_dictionary.md` for the current contracts and checks. Real collection
remains separately gated; these entry points still accept mocks only.
