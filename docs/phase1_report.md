# Phase 1 report — 2026-11-25

## Completed work

Initialized a local Git repository on `main` and created the Study 1 repository
skeleton. No remote was configured, no GitHub push was made, and no real model
API calls were made.

| Files or directories | Work |
| --- | --- |
| `.gitignore` | Exclude the entire `codex_prompts/` folder, local secrets, environments, caches, and build products; allow `prompts/` and `.env.example` |
| `pyproject.toml`, `uv.lock`, `.python-version` | Python >=3.11 package, default interpreter 3.11, exact dependency lock, development/test setup |
| `.env.example` | Placeholder names for four provider keys; no real keys |
| `src/kinloyalty/` | Package version, help/version CLI, reserved client and analysis namespaces |
| `configs/models.yaml` | Exact requested four-model roster and draft API settings, explicitly unverified |
| `configs/study1.yaml` | Decisions, labels, protected card data, proposed names, counts, fixed seeds, validation policy, and analysis configuration |
| `prompts/study1/README.md` | Versioned experiment-template location reserved for the next phase |
| `data/study1/` | Batch documentation and empty smoke/pilot/comprehension directories |
| `results/study1/README.md`, `preregistration/README.md` | Output and final-lock outlines without invented data or a premature lock |
| `docs/data_dictionary.md` | Draft manifest, attempt-log, tidy-table, and report field contracts |
| `docs/decisions.md` | Approvals, layout correction, configuration choices, fixed seeds, and open decisions |
| `docs/adding_a_model.md`, `docs/adding_a_game.md` | Extension workflow outlines |
| `README.md`, `LICENSE`, `DATA_LICENSE`, `CITATION.cff` | Project overview, honest quickstart outlines, MIT/CC BY 4.0 terms, provisional citation |
| `tests/test_configuration.py` | Ten offline checks of the configured study protocol |

## Verification

- Installed the locked environment with uv 0.13.10 using local Python 3.11.5.
- `uv run --offline --locked pytest`: **10 passed**. These verify configuration
  invariants; manifest generation, rendering, provider behavior, runner behavior,
  and analysis are not implemented or tested yet.
- Verified CLI `--version` and `--help`, and package/project/citation version
  consistency at 0.1.0.
- Parsed TOML and Python source and checked public package docstrings.
- Built the wheel and source archive offline. Inspected both: neither includes
  `codex_prompts/` or local secrets. The source archive contains the configuration,
  lock file, and versioned experiment-prompt directory.
- Verified Git ignores local instructions and `.env` variants while allowing
  `prompts/study1/` and `.env.example`.

To check the installed environment directly from the project folder:

```sh
.venv/bin/pytest
.venv/bin/kinloyalty --version
git check-ignore -v codex_prompts/study1-coding-agent-prompt.md
git status --short
```

To rebuild on another machine with uv installed:

```sh
uv sync --locked
uv run --offline --locked pytest
uv run --offline --locked kinloyalty --version
```

## Open items and next phase

There are no blocking Phase 1 problems. Provider model/parameter verification is
pending the client phase. Citation authors/publication metadata remain provisional.
Infrastructure retry/concurrency choices, exact joint comprehension rotation, and
TOST/permutation conventions will be proposed before their implementations.

Phase 2 would implement prompt templates, card rendering, and response schemas;
draft paraphrases 2 and 3 using the proposed Riley/Taylor and Casey/Morgan pairs;
and produce fully rendered prompts for every decision × label × paraphrase for
one model. The researcher must approve the text. Phase 2 has not started.
