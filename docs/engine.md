# Offline experiment engine

The Phase 3 CLI supports mock calls only. Provider SDKs are not imported by the
engine and no keys are read. Every mock record is explicitly synthetic. The
provider names/settings in the frozen requests are the requested, still-unverified
specification, not evidence of a successful provider call.

## Allocation and frozen manifests

`kinloyalty manifest --config configs/study1.yaml --phase <phase> --output <path>`
creates a new JSONL plan. It refuses to overwrite an existing path. Configuration
paths are relative to the study YAML file. All plans are shuffled with the
phase-specific fixed seed before execution positions are assigned.

- **Main:** 3,600 draws, 900/model, 60/model × decision × label, and 20/smallest
  cell. Other-lab names have 7/7/6 counts within each paraphrase. Rotating that
  row across the three paraphrases gives 20 mentions of each name per focal
  model × decision. This plan is tested in temporary files only at this stage.
- **Pilot:** 240 draws. Each model × decision has four draws for each label.
  Start with one draw per paraphrase and add one at
  `(label_index + model_index + decision_index) % 3` (zero-based config order).
  Paraphrase totals within a model × decision are a rotation of 7/7/6. The four
  other-lab names cycle through roster order with a decision-index offset,
  giving 2/1/1 per decision and four mentions/name across its three decisions.
- **Comprehension:** 320 draws, 20/model × card label, no human condition.
  Own-model, fictional, and undisclosed use paraphrase counts 7/7/6. For
  other-lab, rows are paraphrases and columns are the other models in roster
  order: `[[3,2,2],[2,3,2],[2,2,2]]`. Both margins are 7/7/6 and all nine cells
  appear. The researcher explicitly selected these pilot and check allocations.
- **Smoke:** four planned dictator/not-disclosed/paraphrase-1 draws, one/model.
  This phase's demo executes them with the mock client, not the real providers.

Each trial has a stable ID from study, phase, model, decision, label, paraphrase,
and draw index. Changing only the order seed changes order, not these IDs. The
manifest also freezes the complete request, schemas, design metadata, source
hashes, and runner defaults. Local mock context contains labels/expected answers;
it is never part of a system/user message and must never be forwarded by a
provider adapter. Resume does not reload or rerender current source files.

## Validation and the attempt lifecycle

The canonical validator supports the approved flat required integer/string
schemas, enum values, and numeric bounds, with no extra fields. Unsupported
schema features are configuration errors, checked before calls. Malformed JSON,
duplicate keys, non-standard non-finite constants, and schema/range violations
are invalid replies. Output-cap stops (`length`/`max_tokens`) or a client's
normalized truncation flag make even parseable JSON invalid.

Following JSON Schema integer semantics, `1.0` and `1e1` are whole numbers; true,
fractional numbers, strings, and non-finite numbers are not integer outcomes.
Field order and a one-sentence reason are requested in the prompt; the approved
schema does not impose extra order or sentence-count exclusion heuristics.

1. A valid response finishes the draw.
2. The first invalid response gets one fresh, identical request, with no
   corrective message or conversation history.
3. A second invalid response finishes the draw as excluded.
4. A recognized API error has `outcome.valid: null`. It does not consume a model
   response opportunity or cause an exclusion. Retryable errors use exponential
   backoff. Exhausted/non-retryable errors leave the draw unfinished.
5. Resume skips final draws, retries unfinished ones, preserves attempt numbers
   and prior invalid counts, and starts a fresh API-error budget. An invalid
   first reply before an interruption cannot grant a third reply later.

API errors expose categorized kind/status/retryability only; raw exception text
and headers are never logged. Unexpected programming errors are recorded as
interrupted attempts and propagate; the runner stops scheduling new trials and
cancels outstanding tasks. Providers must normalize their errors in adapters.

## Scheduling defaults

The YAML and frozen manifest hold the defaults: four concurrent trials, one per
model, 120-second call timeout, and four API attempts per response opportunity.
Backoff starts at 1 second, multiplies by 2, and caps at 30 seconds: the default
four-attempt sequence waits 1/2/4 seconds. The invalid re-ask is separate.

Initial trials are dispatched in manifest order with global and per-model limits.
A trial holds its permits through its retries/re-ask; a busy model can delay later
dispatches. Retries and concurrent completion naturally interleave. Logs keep
both planned `execution_position` and actual `dispatch_sequence`/timestamps, so
planned order is never misrepresented as response-completion order.

## Durable logging and recovery

`kinloyalty run --manifest <path> --log <path> --client mock` acquires a nonblocking
advisory lock on `<log>.lock` before making any calls. A second writer fails.
Locking uses `fcntl` and is supported on macOS/Linux local filesystems.

Before each call, an atomic fsynced `<log>.pending.json` reserves the attempt
identity, frozen request, counters, and provenance. After completion, the runner
appends and fsyncs exactly one JSONL record, then removes that reservation.
Completed JSONL records are never rewritten. The sidecar is removed when empty;
the empty advisory lock file is ignored by Git.

After a hard process stop, unresolved reservations become one interrupted record
each: response/validity remain unknown, the draw is unfinished, and no answer or
exclusion is invented. A reservation whose record was already appended is cleared
without a duplicate. Unknown external completion can require another attempt;
the log preserves that uncertainty. Tests kill a process during both first-call
and re-ask stages and verify correct recovery.

Before resume, the runner checks the exact manifest digest, each trial/request
binding, counters, saved validation outcomes, backend mode, and terminal states.
A changed plan or inconsistent history is rejected before new calls. A partial
or corrupt JSONL record also stops execution and preserves its original bytes
for deliberate recovery; the runner does not silently delete a damaged tail.

## Summaries and data separation

The CLI reports completion counts, new calls, recovered attempts, and unfinished
trial IDs. It does not compute outcome comparisons, including pilot label effects.
Unfinished work produces a nonzero exit status. Exclusions count as finished
draws and remain available for diagnostics.

Synthetic test/demo logs belong in temporary directories, with `synthetic: true`
and `execution_mode: mock`. Real smoke/pilot/comprehension/main data directories
remain separate. No real batch or main run is authorized by running these demos.
See `docs/data_dictionary.md` for every persisted field.
