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

The approved Phase 4 smoke uses the dedicated
`python -m kinloyalty.negotiation.smoke` entry point. It permits live smoke
only, reads ignored .env keys without process-environment precedence, requires
clean committed code, persists natural/probe budgets, and halts on returned
version drift after logging the response. `smoke_report.py` reports mechanical
checks and exact probe transcripts from saved logs. See
`docs/study2_phase4_execution_plan.md` and `docs/study2_phase4_report.md`.

The approved Phase 6 pilot uses its separate `kinloyalty.negotiation.pilot`
entry point and blind `pilot_report` module. Current live collection is limited
to explicitly authorized smoke/pilot scopes, not main. The default `study2 run`
CLI remains mock-only. Main inference and reproduction live independently in
`src/kinloyalty/analysis/study2/` and reject smoke/pilot/probes.

Study 2's Phase 8 lock freezes an unexecuted main manifest plus complete
`preregistration/study2.md` and `study2-lock.json`. To verify its registered
sources, byte-identical main generation, every turn-position payload and the
annotated local tag without API keys or analysis, use:

```sh
.venv/bin/python -m kinloyalty.negotiation.registration --require-unrun --tag
```

The `--require-unrun` check is for the lock gate, when the main directory must
contain only its manifest. A future main collection needs separate scope/budget
approval and any post-lock execution glue must be logged as a deviation; the
registration itself never starts that collection. Other researchers should
create new study namespaces/configs and preserve all existing locked artifacts.
