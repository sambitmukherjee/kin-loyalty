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

Study 2 already has a separate multi-turn negotiation engine. Both studies
have completed main collection and analysis. New tasks should preserve their
registered configurations, prompts and artifacts.

## Study 2 negotiation components

Study 2's negotiation protocol lives separately under
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
It refuses live clients. The batch collection components add frozen manifest
plans in `manifest.py`, scheduling and journals in `runner.py`, independent
reconstruction in `history.py`,
`collection.py` replay, and marked single-position probe execution/reporting.
Use the additive `kinloyalty study2` command group for manifest, mock run/resume,
replay, and probe-report operations. Existing Study 1 commands are unchanged.
See `docs/study2_phase3_report.md` and the Study 2 sections of
`docs/data_dictionary.md` for the current contracts and checks. Real collection
remains separately gated; these entry points still accept mocks only.

The original live smoke collection used the dedicated
`python -m kinloyalty.negotiation.smoke` entry point. It permits live smoke
only, reads ignored .env keys without process-environment precedence, requires
clean committed code, persists natural/probe budgets, and halts on returned
version drift after logging the response. `smoke_report.py` reports mechanical
checks and exact probe transcripts from saved logs. See
`docs/study2_phase4_execution_plan.md` and `docs/study2_phase4_report.md`.

The live pilot used the separate `kinloyalty.negotiation.pilot` entry point and
blind `pilot_report` module. The completed 960-episode main collection used
`kinloyalty.negotiation.main_run`, added in the documented
[execution patch](study2_main_execution_patch.md). That launcher accepts only
the original frozen manifest and requires the original clean execution commit.
It is not a general live launcher for another experiment. The public
`kinloyalty study2 run` command remains mock-only. Main inference and reproduction
are implemented separately in `src/kinloyalty/analysis/study2/` and reject smoke,
pilot and probe data.

The `prereg-study2` tag preserves the registration and the main manifest as they
stood before collection. The `study2-data` tag preserves the completed main
collection. The [registration index](../preregistration/README.md) explains the
two snapshots and the later execution patch.

`kinloyalty.negotiation.registration` verifies the original registered source
bytes. Its `--require-unrun` option is a historical registration check that
requires a directory containing only the manifest. That option is appropriate
in the original `prereg-study2` checkout, not in the completed collection.
The verifier also rejects source changes after registration, including the
approved execution patch, so it should be run in the registration checkout.
The [registration preparation report](study2_phase8_report.md) records its
original invocation. Other researchers should use separate configurations and
artifact directories for new studies and preserve all existing frozen inputs.
