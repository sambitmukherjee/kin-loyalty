# kin-loyalty

Does an AI agent give away more of its user's money when a counterparty's agent
card names the agent's own exact model? Study 1 examines this label effect in a
dictator game and in the proposer and responder roles of an ultimatum game.

The unit of observation is a fresh, self-contained model call. Counterparties
are hypothetical. Study 2 will examine negotiation later; its implementation is
outside the current scope.

## Current status

**Phase 3: offline experiment engine.** The researcher has approved the prompt
text, response schemas, and Riley/Taylor and Casey/Morgan name pairs. The package
builds balanced, deterministic manifests and executes/resumes them with a mock
client, durable attempt logs, validation, retries, and one identical re-ask.
The CLI supports **mock execution only**. No real provider clients or model API
calls, analysis results, or locked pre-registration exist yet. Model IDs and API
settings remain unverified until the provider-client phase.

The planned main design has four models, three decisions, five labels, three
paraphrases, and 20 draws per smallest cell: **3,600 planned draws**. Smoke tests,
the 240-draw pilot, and the 320-draw comprehension check are separate batches.
Re-asks and API retries add attempts beyond these counts. The main run is outside
the current authorization.

## Set up the development environment

Use Python 3.11 or later and [uv](https://docs.astral.sh/uv/). The project pins
Python 3.11 as the default interpreter and exact dependencies in `uv.lock`.

```sh
uv sync --locked
uv run --locked kinloyalty --version
uv run --locked pytest
```

The development dependency group includes pytest and is installed by default.
Tests do not need API keys or network access once dependencies are installed.

If you already have a supported interpreter, select it explicitly:

```sh
uv sync --locked --python /absolute/path/to/python3.11
```

## Inspect the approved prompts

Read [the complete rendered review](docs/study1_prompt_review.md) for Claude
Sonnet 5.5. It contains all 45 decision/label/paraphrase combinations, expanded to
63 decision examples to include every other-lab card, plus 18 separate
comprehension examples. These are examples for text approval, not a trial manifest.
The canonical response schemas appear at the beginning.

The [template index](prompts/study1/README.md) links to each plain-text source for
comparing the paraphrases. To regenerate the review without keys or API calls:

```sh
uv run --offline --locked kinloyalty review-prompts \
  --config configs/study1.yaml --model claude_sonnet_5_5 \
  --output docs/study1_prompt_review.md
```

`--model` accepts any model key in `configs/models.yaml`. Configuration file and
directory paths are resolved relative to the study YAML file; CLI input/output
paths are relative to the working directory unless supplied as absolute paths.
Prompt approval was recorded on 2026-11-25; it does not lock the pre-registration.

## Try the offline engine

Create a fresh directory for these synthetic examples, outside the study's real
data directories. This executes four mock calls and makes no network requests:

```sh
kinloyalty_demo_dir="$(mktemp -d /private/tmp/kin-loyalty-demo.XXXXXX)"
uv run --offline --locked kinloyalty manifest --phase smoke \
  --output "$kinloyalty_demo_dir/manifest.jsonl"
uv run --offline --locked kinloyalty run --client mock \
  --manifest "$kinloyalty_demo_dir/manifest.jsonl" \
  --log "$kinloyalty_demo_dir/attempts.jsonl"
```

Repeat the `run` command to verify resume: it reports four already-final draws
and zero new calls. Every mock record has `synthetic: true`; mock token counts
are synthetic, not provider measurements. Manifests refuse to overwrite an
existing file. The runner reads frozen requests from the manifest, without
reloading current prompts or configuration.

`manifest` also supports `pilot`, `comprehension`, and `main`. These build plans
only. The main manifest has been checked in temporary tests; the pre-registration
manifest is created at the final lock, and the real main run remains out of scope.

See [engine behavior and recovery](docs/engine.md) and the
[implemented log dictionary](docs/data_dictionary.md). Locking uses `fcntl` on
macOS/Linux. A partially written JSONL record causes execution to stop while
preserving its bytes for recovery.

## Quickstart A: reproduce the paper

This workflow will be implemented before the pre-registration lock. It will read
saved logs and regenerate tables and PDF/PNG figures without API keys. There are
no paper data or reproduction commands available in this skeleton.

The planned entry point is `kinloyalty reproduce`. Analysis will reject pilot,
smoke, and comprehension decisions as input to the main outcome analysis. A
separate report will summarize the comprehension check.

## Quickstart B: run a new experiment

The offline planning/execution steps are implemented; real provider integration
will follow in its approved phase:

1. Edit the readable model and study YAML files in `configs/` and the experiment
   templates in `prompts/study1/`.
2. Verify each model's endpoint and request parameters against its provider's
   current official documentation. Obtain approval for all prompt text.
3. Create a local `.env` from `.env.example` and fill in the required keys. The
   runner's key loading will be implemented with the provider clients. Keys and
   request headers must never appear in logs.
4. Generate and inspect a deterministic trial manifest before any batch. Run the
   approved batch through the manifest-based runner, resuming by trial ID.
5. Retain the append-only attempt logs and reproduce outputs from those logs.

Available commands are `review-prompts`, `manifest`, and mock-only `run`.
Real `smoke`, reporting, analysis, and reproduction commands are not implemented
yet. No command in the current package makes paid model calls.

## Repository layout

| Path | Purpose |
| --- | --- |
| `configs/models.yaml` | Requested model roster and provider settings; verification pending |
| `configs/study1.yaml` | Design, conditions, names, counts, fixed seeds, and analysis settings |
| `prompts/study1/` | Versioned system/game templates, protected blocks and shared JSON instructions |
| `src/kinloyalty/` | Prompt/schema tools, manifests, mock client, validation, logging, runner, CLI |
| `data/study1/` | Separate smoke, pilot, and comprehension batches; main data added later |
| `results/study1/` | Generated tables and figures, once implemented |
| `preregistration/` | Reserved for the final Study 1 pre-registration |
| `docs/data_dictionary.md` | Draft attempt-log and analysis-table contracts |
| `docs/decisions.md` | Dated decisions, approvals, and later deviations |
| `docs/study1_prompt_review.md` | Fully rendered draft prompts and schemas for approval |
| `docs/engine.md` | Allocation rules, retries/re-asks, concurrency, and durable resume |
| `tests/` | Offline protocol, manifest, validation, logging/resume, and CLI checks; socket connections blocked |
| `codex_prompts/` | Local coding-agent instructions; always Git-ignored |

`prompts/` and `codex_prompts/` have different purposes. Experiment templates are
versioned. The local coding-agent instruction folder and `.env` files must never
be staged or force-added. Raw study logs are intended to be versioned research
artifacts and are not ignored.

## Research and working rules

- P1 tests dictator transfers to `own_model` versus `other_lab`; its pooled
  estimate gives each of the four models equal weight.
- All difference tests are two-sided. The pooled P1 equivalence test uses the
  configurable ±$5 bound; exact TOST conventions await analysis-phase approval.
- Pilot decision summaries pool over labels. No pilot label-effect comparisons
  are computed, and pilot decisions never enter the main analysis.
- An invalid reply gets one identical fresh re-ask. Two invalid replies exclude
  the draw. Exhausted API errors remain unfinished and resumable.
- Each phase ends with a report, local commit, and approval before the next.
  Real API batches require explicit approval and a stated call count. No GitHub
  pushes occur without permission.

The refined phase order is repository skeleton → prompts/cards → mock engine →
provider documentation/clients → approved smoke test → mock-tested analysis →
approved pilot/comprehension → approved fixes → pre-registration lock. The final
lock includes a main manifest and hashes, a local commit and tag, and a separately
approved push. It does not execute the main study.

## Licenses and citation

Code uses the MIT license in `LICENSE`. Study data and logs use CC BY 4.0 as
described in `DATA_LICENSE`, subject to third-party rights. `CITATION.cff`
contains provisional repository metadata; named authors, the public repository,
and publication details will be added when confirmed.
