# kin-loyalty

Does an AI agent give away more of its user's money when a counterparty's agent
card names the agent's own exact model? Study 1 examines this label effect in a
dictator game and in the proposer and responder roles of an ultimatum game.

The unit of observation is a fresh, self-contained model call. Counterparties
are hypothetical. Study 2 will examine negotiation later; its implementation is
outside the current scope.

## Current status

**Phase 1: repository skeleton.** The package currently exposes help and version
information only. There are no provider clients, experiment prompts, manifests,
runner, API calls, analysis results, or locked pre-registration yet. Model IDs
and API settings in the configuration are the requested specification and have
not been verified against current provider documentation.

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

## Quickstart A: reproduce the paper

This workflow will be implemented before the pre-registration lock. It will read
saved logs and regenerate tables and PDF/PNG figures without API keys. There are
no paper data or reproduction commands available in this skeleton.

The planned entry point is `kinloyalty reproduce`. Analysis will reject pilot,
smoke, and comprehension decisions as input to the main outcome analysis. A
separate report will summarize the comprehension check.

## Quickstart B: run a new experiment

This workflow will be implemented in subsequent approved phases:

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

The planned CLI will include `smoke`, `manifest`, `run`, `report`, `analyze`, and
`reproduce`. These commands are **not implemented yet**.

## Repository layout

| Path | Purpose |
| --- | --- |
| `configs/models.yaml` | Requested model roster and provider settings; verification pending |
| `configs/study1.yaml` | Design, conditions, names, counts, fixed seeds, and analysis settings |
| `prompts/study1/` | Versioned experiment templates, to be drafted in Phase 2 |
| `src/kinloyalty/` | Package, with reserved client and analysis modules |
| `data/study1/` | Separate smoke, pilot, and comprehension batches; main data added later |
| `results/study1/` | Generated tables and figures, once implemented |
| `preregistration/` | Reserved for the final Study 1 pre-registration |
| `docs/data_dictionary.md` | Draft attempt-log and analysis-table contracts |
| `docs/decisions.md` | Dated decisions, approvals, and later deviations |
| `tests/` | Offline configuration checks; behavioral tests added with implementation |
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
