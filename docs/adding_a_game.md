# Adapt an existing task or implement another game

The [worked new-experiment guide](running_a_new_experiment.md) demonstrates both
engines with separate configurations, copied prompts, mock responses, resumption
and analysis. It is the starting point for another experiment that retains an
existing task. This guide explains the implementation boundaries when the task
itself changes.

The registered configurations, prompts, logs, results and registrations describe
the completed studies. New tasks belong in a separate experiment directory or
fork, with their own source files and records.

## Choose the appropriate engine

| Engine | Existing task | Useful components |
| --- | --- | --- |
| Study 1 single-decision engine | A fresh, self-contained model request produces one decision. The current games are dictator, ultimatum proposer and ultimatum responder. | Template and card rendering, response schemas, balanced manifests, provider clients, validation, durable attempt logs and retry/resume behavior. |
| Study 2 negotiation engine | Two roles alternate public messages until agreement, walk-away or the message limit. | Private role prompts, transcript rendering, action schemas, explicit state transitions, per-pair attempt logs and independent outcome replay. |

A new scenario description can often reuse an engine. A different response
structure, information flow or rule for agreement usually needs code. Passing a
new task name in YAML does not create those behaviors.

## Adapt wording within an existing task

Copy the study configuration, model roster and prompt folder, as in the worked
guide. Change the copies and preserve the placeholders used by the renderer.
Inspect the resulting messages for each condition and role before freezing a
new manifest. For negotiations, inspect late messages as well as openings,
because the allowed actions change at the end.

If the game, fields, allocation and target of estimation remain the same, the
existing analysis may still be suitable. That is a scientific judgment to make
before main collection, not something established by successful execution. The mock
clients use local rules and supplied metadata; they do not interpret the edited
natural-language instructions. A successful mock run checks the machinery,
not whether a model understands a new scenario.

## Implement a different single-decision task

Study 1's runner operates on frozen requests, but its planning and analysis
layers implement the original design. The main points to examine are:

| Component | What a new task must define |
| --- | --- |
| [prompts.py](../src/kinloyalty/prompts.py) and the new templates | How identities, person names, conditions and task text form complete messages. Some task-specific template and field conventions are implemented in code. |
| [schemas.py](../src/kinloyalty/schemas.py) | The required response fields and their types, bounds and allowed values. The current builder supports flat integer/string fields for the configured outcomes and beliefs. |
| [validate.py](../src/kinloyalty/validate.py) | Parsing and local validity rules, including any schema features the new task needs. The current validator rejects unsupported features rather than silently ignoring them. |
| [manifest.py](../src/kinloyalty/manifest.py) | A deterministic allocation, stable trial identities, expected counts and complete frozen requests. The original other-lab and comprehension allocation rules are not arbitrary design builders. |
| [clients/mock.py](../src/kinloyalty/clients/mock.py) | Valid synthetic decisions and explicit failure cases for the new fields. A mock must not be mistaken for a scientific agent. |
| [analysis/](../src/kinloyalty/analysis/) | Eligible outcomes, coverage requirements, hypotheses, estimands, uncertainty calculations and figures appropriate to the new task. |

For example, adding an integer outcome field can reuse part of the schema
builder, but it does not automatically add an analysis for that outcome. The
existing analysis expects the original decision and label conventions; its
figures explicitly use the original games and four-model layout. A new decision
name, label set, continuous response, nested JSON or different roster size needs
checks beyond editing a template.

The transport-independent [runner](../src/kinloyalty/runner.py) and
[provider clients](../src/kinloyalty/clients/) can often be reused. Preserve the
separation between invalid responses and API errors, and retain exact request
content in the logs. Define any new exclusion or re-ask rules explicitly instead
of letting parsing accidents decide which observations survive.

## Implement a different negotiation task

Negotiation components live in
[src/kinloyalty/negotiation/](../src/kinloyalty/negotiation/). They separate task
state from provider calls and from durable collection:

| Component | Responsibility |
| --- | --- |
| `config.py`, `scenarios.py`, `manifest.py` | Validate the design, generate scenario facts and assignments, and freeze their source snapshot. |
| `cards.py`, `prompts.py`, `transcript.py`, `requests.py` | Control what each role sees, render the public history and construct the current request. |
| `state.py`, `rules.py` | Define the episode state, legal actions, turn order, terminal conditions and outcome calculation. |
| `schemas.py`, `validate.py` | Define and validate the reply structure for each message position. |
| `engine.py` | Execute sequential turns, re-asks and retries while keeping resumable episode progress. |
| `runner.py`, `journal.py` | Schedule episodes, persist attempts and pending calls, and resume a stopped collection. |
| `history.py`, `collection.py` | Reconstruct progress and outcomes from attempts and verify saved episode summaries. |
| [analysis/study2/](../src/kinloyalty/analysis/study2/) | Load eligible completed collections and implement the original outcomes, matched comparisons and figures. |

The loader checks several original choices explicitly: the three disclosure
conditions, the Alex/Jordan role names, ordered pairs including self-pairs,
shared scenarios and the configured allocation rules. It validates that model
order and expected counts agree. Some quantities, such as items and scenario
replication counts, are configurable, but their relationship to prompts, probes,
outcomes and analysis still needs review. A larger message limit also needs
suitable late-message review fixtures; the original hand-written transcripts
have a finite length.

Information flow is part of the design. The original buyer sees a seller card,
and each role sees only its own private limit. `EpisodeSpec.custom_cards` can
supply optional card text for each role at the lower request/engine level.
It is not a CLI option or a ready-made new condition with matching analysis.
Changing who sees a card, allowing simultaneous messages, adding roles or
changing the meaning of acceptance requires coordinated request, state, rule,
replay and analysis changes.

The current rules treat an `accept` as accepting the counterparty's latest
standing offer. A supplied price on a non-offer reply is recorded and ignored;
a mismatched accept price is flagged. If a new task defines those actions
differently, its validator and replay logic must implement that definition
together. Reusing the old action names alone does not preserve the intended
meaning.

`engine.run_episode` is useful for in-memory tests and uses mocks by default.
It is not a durable live batch launcher. The existing live smoke, pilot and main
launchers and authorization classes encode the original study's collection
scopes. A different live study needs its own launcher, authorization and replay
support; see the [live-interface discussion](running_a_new_experiment.md#6-live-collection-interfaces-and-their-limits).
Do not reuse an original approval as authorization for another experiment.

## Verify the new task before main collection

Begin with hand-written cases whose correct outcomes are known. Check a valid
reply, an invalid reply followed by a valid re-ask, two invalid replies, a
truncated response, retryable and non-retryable API errors, and resumption after
an interruption. Negotiation cases should also cover each terminal state and
role, late-message action restrictions, private-information separation and
replay of the saved outcome. Include the new task's own boundary cases.

Use separate synthetic destinations and retain explicit synthetic markers.
[The existing tests](../tests/) use in-memory transports and block socket
connections; they show how to exercise these paths without paid calls. Add
tests for the behavior that changes rather than assuming the original test
suite covers a new protocol.

Define the new analysis before collecting its main outcomes. A changed game may
need a different estimand, unit of randomization, handling of missing outcomes
or resampling scheme. The existing P1/P2 labels and inference commands refer to
the paper's designs. Retain the new code revision, source templates, dependency
lock, frozen plan, response logs and any documented departures with the new
experiment, so another reader can reconstruct its results.
