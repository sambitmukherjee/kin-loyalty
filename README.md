# kin-loyalty

Does an AI agent give away more of its user's money when a counterparty's agent
card names the agent's own exact model? Study 1 examines this label effect in a
dictator game and in the proposer and responder roles of an ultimatum game.

The unit of observation is a fresh, self-contained model call. Counterparties
are hypothetical. Study 2 will examine negotiation later; its implementation is
outside the current scope.

## Current status

**Approved pre-lock design amendment and re-pilot complete.** The researcher has approved the prompt
text, response schemas, and Riley/Taylor and Casey/Morgan name pairs. The package
builds balanced, deterministic manifests and executes/resumes them with a mock
client, durable attempt logs, validation, retries, and one identical re-ask.
The CLI supports **mock execution only**. Four provider adapters use the official
SDKs with documentation-verified mappings and in-memory HTTP tests. The approved
smoke invocation made exactly four API attempts, with no retries or re-asks.
Input sizes were 233–539 tokens; no response hit the output cap. Kimi omitted
its cache-read count (retained as null) and reported 256 cache-write tokens.
See the [smoke report and metadata limitations](docs/phase4b_report.md) and
[provider verification and sources](docs/provider_verification.md).
The [original Phase 6 pilot](docs/phase6_report.md) found all-zero dictator
transfers for OpenAI/Gemini and constant Gemini proposer offers. On 2026-11-26,
the researcher explicitly approved a design change before the lock: remove only
the final principal-interest sentence from all three system paraphrases, used
by every decision and comprehension. No other scientific input changed.
The fresh 240-draw pilot and 320-draw comprehension check completed in exactly
560 API attempts, all valid, without errors or re-asks. All four models passed
every scored comprehension condition at 20/20. No model had an all-zero dictator
floor; Sonnet and Gemini transferred $50 in all 20 dictator draws each. Gemini
proposer offers varied; no change was made in response to its original constant
$40 offers. **This is the only prompt change for the dictator floor; no further
change will be made for that reason.** See the
[re-pilot report](docs/repilot_20261126_report.md) for pooled distributions,
metadata, and offline verification commands. Original artifacts are preserved.
No pilot label-effect comparison was computed, and pre-registration remains
unlocked. See [analysis methods and commands](docs/analysis.md).
The [unlocked pre-registration draft](preregistration/study1.md) records the
researcher's fixed S1 count rule and paired descriptive comparison, plus the
pooled P1 percentile-bootstrap TOST specification.
All bootstrap intervals use empirical ranks without interpolation: 500/9501
for 90% and 250/9751 for 95%, out of the same 10,000 resamples.
Label and adjusted-residual permutations exchange only the two tested labels
within strata. One shared conservative numerical tie tolerance applies to
permutation p-values and bootstrap TOST decisions.

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
Initial prompt approval was recorded on 2026-11-25; the system-sentence removal
was explicitly approved on 2026-11-26. Neither locks the pre-registration.

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

The reproduction command reads saved main logs and a separate comprehension
batch, then regenerates CSV tables, PDF/PNG figures, resampling distributions,
provenance, and artifact hashes without API keys:

```sh
kinloyalty reproduce --data data/study1/main \
  --comprehension data/study1/repilot_20261126/comprehension --output results/study1/generated
```

Real main data do not exist yet, so this command currently stops with a missing
input error. It rejects smoke/pilot/comprehension decisions as main outcomes,
requires every main draw to be terminal, and refuses to overwrite outputs.
`kinloyalty analyze study1` runs the same pipeline with the same arguments.

For an entirely offline demonstration, use new temporary paths:

```sh
kinloyalty simulate-study1 --directory /private/tmp/kin-loyalty-analysis-demo \
  --own-model-effect 12
kinloyalty reproduce --data /private/tmp/kin-loyalty-analysis-demo/main \
  --comprehension /private/tmp/kin-loyalty-analysis-demo/comprehension \
  --output /private/tmp/kin-loyalty-analysis-demo-results --allow-synthetic
```

This generates explicitly synthetic main/pilot/comprehension logs through the
mock client and runner. The output labels them simulated. Synthetic batches are
kept outside the configured real study data/results roots. See [the methods,
eligibility rules, and inference conventions](docs/analysis.md).

## Quickstart B: run a new experiment

Planning, execution, and the four provider adapters are implemented. Every real
batch still requires its own approval:

1. Edit the readable model and study YAML files in `configs/` and the experiment
   templates in `prompts/study1/`.
2. Verify each model's endpoint and request parameters against its provider's
   current official documentation. Obtain approval for all prompt text.
3. After real-call approval, create a local `.env` from `.env.example` and fill
   in the required keys. The provider factory loads these with process-environment
   precedence. Keys and request headers must never appear in logs.
4. Generate and inspect a deterministic trial manifest before any batch. Run the
   approved batch through the manifest-based runner, resuming by trial ID.
5. Retain the append-only attempt logs and reproduce outputs from those logs.

Available commands are `review-prompts`, `manifest`, mock-only `run`,
`simulate-study1`, `analyze study1`, `reproduce`, and `report pilot|comprehension`.
Real batch execution is available programmatically through the provider factory
and runner/cohort coordinator after approval; it is not exposed by the CLI yet. Pilot reports pool
all labels; comprehension reports apply the separate pass rule. No CLI command
makes paid calls.

## Repository layout

| Path | Purpose |
| --- | --- |
| `configs/models.yaml` | Model roster and settings accepted in four live smoke requests; metadata caveats in the report |
| `configs/study1.yaml` | Design, conditions, names, counts, fixed seeds, and analysis settings |
| `prompts/study1/` | Versioned system/game templates, protected blocks and shared JSON instructions |
| `src/kinloyalty/` | Prompts/schemas, manifests, clients, validation, logging, runner, saved-log analysis, CLI |
| `data/study1/` | Separate smoke, pilot, and comprehension batches; main data added later |
| `results/study1/` | Generated tables and figures, once implemented |
| `preregistration/` | Reserved for the final Study 1 pre-registration |
| `docs/data_dictionary.md` | Attempt-log and implemented analysis-table contracts |
| `docs/decisions.md` | Dated decisions, approvals, and later deviations |
| `docs/study1_prompt_review.md` | Fully rendered draft prompts and schemas for approval |
| `docs/engine.md` | Allocation rules, retries/re-asks, concurrency, and durable resume |
| `docs/provider_verification.md` | Official sources, exact API mappings, normalization, and prepared smoke scope |
| `docs/phase4b_report.md` | Observed smoke metadata, limitations, artifact hashes, and offline inspection commands |
| `docs/analysis.md` | Eligibility, approved methods, resampling conventions, reports, and reproduction |
| `docs/phase6_report.md` | Observed pilot/comprehension results, pooled distributions, mechanical checks, and review flags |
| `tests/` | Offline protocol, manifest, validation, logging/resume, and CLI checks; socket connections blocked |
| `codex_prompts/` | Local coding-agent instructions; always Git-ignored |

`prompts/` and `codex_prompts/` have different purposes. Experiment templates are
versioned. The local coding-agent instruction folder and `.env` files must never
be staged or force-added. Raw study logs are intended to be versioned research
artifacts and are not ignored.

## Research and working rules

- P1 tests dictator transfers to `own_model` versus `other_lab`; its pooled
  estimate gives each of the four models equal weight.
- All difference tests are two-sided. Pooled P1 equivalence always uses bootstrap
  TOST against configurable ±$5 bounds. The researcher approved tested-pair
  permutations, Freedman–Lane adjusted tests, and model-specific S1 belief slopes.
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
