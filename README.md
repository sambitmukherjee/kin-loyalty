# kin-loyalty

Does an AI agent give away more of its user's money when a counterparty's agent
card names the agent's own exact model? Study 1 examines this label effect in a
dictator game and in the proposer and responder roles of an ultimatum game.

Study 1 uses fresh, self-contained model calls with hypothetical counterparties.
Study 2 uses buyer/seller negotiations of up to 12 messages, with model-label
cards shown only to buyers. Both main collections and their pre-registered
analyses are complete. The paper is
[Do AI Agents Favor Their Own Kind? Model Labels Shift One-Shot Splits but Not Mandated Negotiation](paper/main.pdf),
by Sambit Mukherjee, Independent Researcher.

The frozen collections are identified by `study1-data` and `study2-data`.
The [registration index](preregistration/README.md) explains these data tags and
the earlier protocol tags, `prereg-study1` and `prereg-study2`.
Saved results and reproduction audits are indexed in the
[Study 1 results README](results/study1/README.md) and the
[Study 2 results README](results/study2/README.md).

Study 2 commands are grouped under `kinloyalty study2`: `manifest`, `run`,
`replay`, `probe-report`, `simulate`, `analyze` and `reproduce`.
The `run` command uses mock responses. Dedicated Python modules handled live
smoke, pilot and main collection. The main launcher is bound to the original
registered manifest and execution commit; it is not a general launcher for new
experiments. The [execution patch report](docs/study2_main_execution_patch.md)
describes this documented post-registration change.

The [Study 2 analysis guide](docs/study2_analysis.md) explains outcome eligibility,
signed concessions, missing outcomes in tested pairs, the interaction's sign
and the generated tables and figures. Reproduction checks saved outcomes against
turn records before calculating results. Smoke tests, pilots and probes are
excluded from main inference; synthetic inputs require `--allow-synthetic`.

## Current status

**Both studies have completed main collection and pre-registered analysis.**
Study 1 collected 3,600 valid decisions. Study 2 completed all 960 negotiations
in 8,417 API attempts, with two recovered API errors, no re-asks or exclusions,
and no unfinished episodes. Its [collection report](results/study2/main-collection-report/collection-report.md)
records the mechanical checks, including exact replay of every terminal summary.
The [Study 2 results report](results/study2/analysis-summary.md) contains the
completed analysis.

For Study 1, the researcher approved the prompt text, response schemas, and Riley/Taylor and Casey/Morgan name pairs. The package
builds balanced, deterministic manifests and executes/resumes them with a mock
client, durable attempt logs, validation, retries, and one identical re-ask.
The `kinloyalty run` command supports **mock execution only**; live Study 1
collection used the provider factory and runner through Python. Four provider
adapters use the official SDKs with documentation-verified mappings and in-memory HTTP tests. The approved
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
$40 offers. **This was the only prompt change for the dictator floor; no further
change was made for that reason.** See the
[re-pilot report](docs/repilot_20261126_report.md) for pooled distributions,
metadata, and offline verification commands. Original artifacts are preserved.
No pilot label-effect comparison was computed. See
[analysis methods and commands](docs/analysis.md). The
[final pre-registration](preregistration/study1.md) includes the full protocol,
prompt/schema appendices, main manifest and exact hashes, final comprehension
result, fixed S1 count rule and paired descriptive comparison, and the pooled
P1 percentile-bootstrap TOST specification. The
[hash inventory](preregistration/study1-lock.json) binds all frozen source and
research artifacts. The `prereg-study1` tag identifies the registration
commit, `d4d6ff9`. The researcher approved its push, and GitHub main and the
annotated tag were verified at that commit before main collection. See the
[Phase 8 preparation report](docs/phase8_report.md).

The authorized main run then collected all 3,600 valid draws in 3,613 API attempts,
including 13 API errors and one registered resumption of an unfinished draw.
Every model × decision × label cell completed 60 valid draws; invalid replies,
re-asks, exclusions, and unfinished draws are zero throughout. Every attempt
records the tagged commit and clean-code provenance. See the
[collection report](docs/study1_main_collection_report.md) and
[complete 60-cell mechanical counts](data/study1/main/collection_counts.csv).
The main analysis was subsequently completed from the `study1-data` tag.
The [Study 1 analysis report](results/study1/analysis_report.md) contains the
results, and the [reproducibility audit](results/study1/reproducibility.json)
records the independent comparison from another checkout.
All bootstrap intervals use empirical ranks without interpolation: 500/9501
for 90% and 250/9751 for 95%, out of the same 10,000 resamples.
Label and adjusted-residual permutations exchange only the two tested labels
within strata. One shared conservative numerical tie tolerance applies to
permutation p-values and bootstrap TOST decisions.

The Study 1 main design used four models, three decisions, five labels, three
paraphrases, and 20 draws per smallest cell: **3,600 planned draws**. Smoke tests,
the 240-draw pilot, and the 320-draw comprehension check are separate batches.
Re-asks and API retries add attempts beyond these counts. The separately
authorized main collection is now complete under that registered plan.

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
was approved on 2026-11-26, before registration. The `prereg-study1` tag preserves
the final registered prompts and protocol.

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
only. The exact 3,600-draw main plan now exists at
`data/study1/main/manifest.jsonl`, generated without API calls and bound by the
registration hashes. Its separately authorized collection is complete; fresh
execution requires its own authorization.

See [engine behavior and recovery](docs/engine.md) and the
[implemented log dictionary](docs/data_dictionary.md). Locking uses `fcntl` on
macOS/Linux. A partially written JSONL record causes execution to stop while
preserving its bytes for recovery.

## Quickstart A: reproduce the paper

The reproduction command reads saved main logs and a separate comprehension
batch, then regenerates CSV tables, PDF/PNG figures, resampling distributions,
provenance, and artifact hashes without API keys:

```sh
uv run --offline --locked kinloyalty reproduce --config configs/study1.yaml \
  --data data/study1/main \
  --comprehension data/study1/repilot_20261126/comprehension \
  --output scratch/study1-reproduce
```

Run from the repository root after installing the locked dependencies. The
output directory must not already exist. This command rejects smoke, pilot and
comprehension decisions as main outcomes, requires every main draw to be
terminal, and keeps the separate comprehension batch out of outcome inference.
`kinloyalty analyze study1` runs the same pipeline with the same arguments.

Study 2 reproduction reads its frozen manifest and collection:

```sh
uv run --offline --locked kinloyalty study2 reproduce \
  --manifest data/study2/main/manifest.jsonl \
  --directory data/study2/main \
  --output scratch/study2-reproduce
```

This output directory must also be new. The saved results remain in
`results/study1/generated/` and `results/study2/main/`. Their READMEs record the
original frozen-checkout commands and independent reproduction checks.
These analysis commands do not rebuild the paper PDF; its existing build
instructions are in [paper/README.md](paper/README.md).

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

1. Make separate copies of the model and study YAML files and prompt templates
   for the new experiment. Preserve the configurations and prompts used by the
   registered studies.
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
Live Study 1 batches use the provider factory and runner or cohort coordinator
through Python. Study 2 has dedicated live smoke, pilot and main modules, each
with its own collection checks. The main module accepts only the original
registered study. The public `run` commands use mocks. Pilot reports pool all
labels; comprehension reports apply the separate pass rule.

## Repository layout

| Path | Purpose |
| --- | --- |
| `configs/models.yaml` | Model roster and settings accepted in four live smoke requests; metadata caveats in the report |
| `configs/study1.yaml` | Design, conditions, names, counts, fixed seeds, and analysis settings |
| `prompts/study1/` | Versioned system/game templates, protected blocks and shared JSON instructions |
| `src/kinloyalty/` | Prompts/schemas, manifests, clients, validation, logging, runner, saved-log analysis, CLI |
| `data/study1/` | Separate smoke/pilot/check batches, frozen main plan, and completed main collection with mechanical counts |
| `results/study1/` | Completed main analysis, reproduction audit and separate historical pilot/check reports |
| `configs/study2.yaml`, `prompts/study2/` | Registered negotiation design and exact prompt templates |
| `data/study2/` | Separate smoke/probe, pilot and completed main collections |
| `results/study2/` | Completed main analysis, reproduction audit and separate collection reports |
| `paper/` | Manuscript, compiled PDF, figures, appendices and build instructions |
| `preregistration/` | Both final registrations, their hash inventories and an index of frozen tags |
| `docs/data_dictionary.md` | Attempt-log and implemented analysis-table contracts |
| `docs/decisions.md` | Dated decisions, approvals, and later deviations |
| `docs/study1_prompt_review.md` | Fully rendered final prompts and schemas across all paraphrases |
| `docs/engine.md` | Allocation rules, retries/re-asks, concurrency, and durable resume |
| `docs/provider_verification.md` | Official sources, exact API mappings, normalization, and prepared smoke scope |
| `docs/phase4b_report.md` | Observed smoke metadata, limitations, artifact hashes, and offline inspection commands |
| `docs/analysis.md` | Eligibility, approved methods, resampling conventions, reports, and reproduction |
| `docs/phase6_report.md` | Observed pilot/comprehension results, pooled distributions, mechanical checks, and review flags |
| `docs/phase8_report.md` | Historical Study 1 registration preparation and verification report |
| `docs/study1_main_collection_report.md` | Main completion/validation counts and tagged provenance; no outcome summaries |
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
- The original collections used researcher approvals and recorded call budgets.
  Their decisions and deviations are preserved in `docs/decisions.md`. New
  experiments need their own collection plans and any applicable approvals.

The historical phase reports describe development and registration before main
collection. Their statements about work still to come refer to the date of each
report. Current collection and analysis status is recorded above and in the
data and results READMEs.

## Licenses and citation

Code uses the MIT license in `LICENSE`. Study data and logs use CC BY 4.0 as
described in `DATA_LICENSE`, subject to third-party rights.
[CITATION.cff](CITATION.cff) names Sambit Mukherjee and records the public repository and accompanying manuscript. The manuscript is listed as unpublished;
no DOI or publication venue is claimed. Record the repository commit or frozen
data tag used when citing a particular version.
