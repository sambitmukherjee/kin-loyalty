# kin-loyalty

Does an AI agent give away more of its user's money when the counterparty's
agent card says that both agents use the same model? This repository contains the code,
prompts, pre-registrations, recorded responses and completed analyses for two
studies of that question.

**Paper:** [Do AI Agents Favor Their Own Kind? Model Labels Shift One-Shot Splits but Not Mandated Negotiation](paper/main.pdf),
by Sambit Mukherjee, Independent Researcher. The PDF includes the technical
appendices after the references.

## Start here

| Your goal | Guide |
| --- | --- |
| Recreate the paper's results, tables and figures from the recorded responses. | [Reproduce the paper](docs/reproducing_the_paper.md), including frozen code, setup, output comparison and the map from results to paper elements. No API keys or new model calls are needed. |
| Develop and run an experiment of your own. | [Run a new experiment](docs/running_a_new_experiment.md), with worked mock examples, request inspection, logs, resumption, analysis and the limits of the live interfaces. |

For manuscript compilation, see the [paper build guide](paper/README.md).
For methods and other supporting material, see the [documentation index](docs/README.md).

## The two studies

Both main collections and their pre-registered analyses are complete. The four
models are Claude Sonnet 5.5, GPT-6.1 Terra, Gemini 4 Hydrogen and Kimi K3.1 Pro.
An agent card is a description of the counterparty's agent, including a line
that names its underlying model or says that it is not disclosed.

| Study | Design and completed main data | Browse the artifacts |
| --- | --- | --- |
| Study 1: single decisions | 3,600 valid decisions across dictator transfers, ultimatum proposer offers and ultimatum responder minimums. Each call is self-contained; counterparties are hypothetical. | [Data](data/study1/README.md), [prompts](prompts/study1/README.md), [results](results/study1/README.md), [protocol](preregistration/study1.md). |
| Study 2: negotiations | 960 buyer–seller negotiations, with up to 12 public messages. Only buyers see a seller card. Truthful and swapped cards separate what the buyer is told from the seller model it actually faces. | [Data](data/study2/README.md), [prompts](prompts/study2/README.md), [results](results/study2/README.md), [addendum](preregistration/study2.md). |

Smoke tests, pilots and schema probes are separate development batches. They do
not enter main outcome inference. Study 1's final comprehension check is a
separate input used to reproduce its comprehension table and plot.

## Set up a current checkout

Use Git, [uv](https://docs.astral.sh/uv/getting-started/installation/) and Python.
The project accepts Python 3.11 or later; the verified reproduction environment
uses CPython 3.11.5 and the exact dependencies in `uv.lock`. Collection and replay
use `fcntl` file locks, so the examples require macOS or Linux rather than
native Windows.

```sh
git clone https://github.com/sambitmukherjee/kin-loyalty.git
cd kin-loyalty
uv sync --locked --python 3.11.5
uv run --offline --locked kinloyalty --version
```

Use a full clone with its history and tags. The first installation may need
internet access to download Python and packages. Once dependencies are installed,
the offline commands use that environment and cache. `--locked` prevents uv
from changing the dependency lockfile.

This current-checkout environment is for examples and development. The
reproduction guide installs a separate environment in each frozen study
checkout, so Python imports the intended analysis code.

## Reproduce the paper

Follow the [complete reproduction guide](docs/reproducing_the_paper.md). It takes
you through selecting the frozen data tags, checking the imported code, replaying
Study 2, running both registered analyses and comparing every output with the
saved reference files. New outputs go under ignored `scratch/` directories;
the committed `results/` directories remain the references.

The saved outputs are indexed in the [Study 1 results guide](results/study1/README.md)
and [Study 2 results guide](results/study2/README.md). Each guide explains the
files, original analysis command and reproduction evidence. The reproduction
guide also maps the paper's figures and tables to their source files and
explains its display rounding.

Analysis and PDF compilation are separate steps. The [paper build guide](paper/README.md)
explains TeX, Pandoc and Poppler setup, the build command, optional PDF checks
and figure-asset regeneration. These tools are not required to reproduce the
analysis tables and plots.

## Run your own experiment

Start with the [worked new-experiment guide](docs/running_a_new_experiment.md).
It copies configurations and prompts into a separate example directory, freezes
planned requests in a manifest, collects mock responses and analyses the saved
logs. A manifest is the fixed list of planned decisions or negotiations saved
before collection. The examples demonstrate both engines and keep synthetic
outputs explicitly marked.

For a quick installation check, the following commands use the registered
Study 1 settings to make four mock requests in a fresh directory. They do not
contact a model provider. Run them from the repository root after setup:

```sh
uv run --offline --locked kinloyalty manifest \
  --config configs/study1.yaml --phase smoke \
  --output scratch/readme-demo/manifest.jsonl
uv run --offline --locked kinloyalty run --client mock \
  --manifest scratch/readme-demo/manifest.jsonl \
  --log scratch/readme-demo/attempts.jsonl
uv run --offline --locked kinloyalty run --client mock \
  --manifest scratch/readme-demo/manifest.jsonl \
  --log scratch/readme-demo/attempts.jsonl
```

The first execution completes four decisions. The second reports four already
finished decisions and zero new calls. If the example manifest already exists,
choose another new directory. For a new research design, use the copied inputs
in the worked guide rather than editing the registered files.

The public `kinloyalty run` and `kinloyalty study2 run` commands accept mocks
only. Live Study 1 collection uses Python interfaces. Study 2's original live
launchers encode its original collection scopes, and its main launcher accepts
only the registered manifest. A different live negotiation experiment requires
additional planning and launch code. The worked guide explains these boundaries,
credential handling and the checks needed for a new collection.

For changes beyond wording, read [adding a model or provider](docs/adding_a_model.md)
and [adapting or adding a game](docs/adding_a_game.md). They distinguish supported
configuration changes from changes requiring implementation and new analysis.

## Frozen versions and research history

| Tag | What it identifies |
| --- | --- |
| `prereg-study1` | Study 1's protocol, code, prompts and main manifest before main collection. |
| `study1-data` | Study 1's completed collection and the code present when it was frozen. |
| `prereg-study2` | Study 2's addendum, code, prompts and main manifest before main collection. |
| `study2-data` | Study 2's completed collection and the code present when it was frozen. |

The [registration index](preregistration/README.md) records all four commit
hashes. The data tags predate the saved main analysis outputs, which are
committed on `main`. Reproduction uses the code and data from the data tags.

Study 2 needed an approved mechanical patch after registration to launch the
main run and record both registration and execution revisions. It preserved
the registered scientific analysis, prompts, settings, protocol and scoring.
The tag difference therefore includes that patch as well as data. See the
[execution patch report](docs/study2_main_execution_patch.md) and
[decision log](docs/decisions.md).

Historical phase reports describe the state at the time they were written.
Their references to pending collections or approvals do not describe the
current project status. The data and results guides index the completed work.

## Repository map

| Location | What you will find |
| --- | --- |
| [docs/](docs/README.md) | Reproduction and new-experiment guides, methods, engine details and historical reports. |
| [configs/](configs/) | The registered study designs, model identities, provider settings and fixed seeds. |
| [prompts/](prompts/) | The versioned experiment templates, indexed separately for each study. |
| [src/kinloyalty/](src/kinloyalty/) | Planning, provider clients, validation, collection, replay, analysis and command interfaces. |
| [data/](data/) | Recorded requests and responses, with main and development batches kept separate. |
| [results/](results/) | Saved analysis tables, figures, reports and reproduction audits. |
| [preregistration/](preregistration/README.md) | Registered protocols, hash inventories and frozen-version information. |
| [paper/](paper/README.md) | Manuscript sources, complete PDF, figures, appendices and build instructions. |
| [tests/](tests/) | Offline checks of requests, rules, validation, logging, recovery and analysis. |

`scratch/` and `worktrees/` are ignored local work areas. `.env` files hold local
credentials and must not be committed. `codex_prompts/` contains local coding-agent
instructions and also remains ignored and untracked; it is separate from the
versioned experiment templates in `prompts/`.

## Common problems

| Problem | Where to look |
| --- | --- |
| A result directory or manifest already exists. | Choose a fresh destination. Execution reuses its existing manifest and logs when resuming; generation and analysis refuse to overwrite artifacts. |
| An offline command cannot find a dependency. | Complete `uv sync --locked --python 3.11.5` with internet access in the intended checkout first. |
| Reproduction imports code from another checkout or produces different files. | Follow the source-path checks and comparison instructions in the [reproduction guide](docs/reproducing_the_paper.md#common-problems). |
| Logs are unfinished or replay fails. | Preserve the files and inspect the diagnostic. The [engine guide](docs/engine.md) and [data dictionary](docs/data_dictionary.md) explain recovery and record checks. |
| A new model or design does not work by editing YAML alone. | Consult the [model guide](docs/adding_a_model.md), [game guide](docs/adding_a_game.md) and [live-interface limits](docs/running_a_new_experiment.md#6-live-collection-interfaces-and-their-limits). |

For development, `uv run --offline --locked pytest` runs the existing test suite.
Its tests block socket connections and use fake provider credentials; they do
not require real API keys.

## Licenses and citation

Code uses the [MIT license](LICENSE). Study data and logs use
[CC BY 4.0](DATA_LICENSE), subject to third-party rights. [CITATION.cff](CITATION.cff)
records Sambit Mukherjee and the accompanying manuscript, which is listed as
unpublished without a claimed venue or DOI. Cite the manuscript when discussing
the findings, and record the repository commit or frozen data tag used.
