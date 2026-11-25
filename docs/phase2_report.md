# Phase 2 report — 2026-11-25

## Completed work

Implemented the three system/game paraphrases, neutral cards and human blocks,
canonical response schemas, and separate comprehension prompts. The researcher
has authorized drafting; **approval of the prompt text and proposed names remains
pending**. No API calls were made and this phase does not implement the engine.

The proposed new name pairs are Riley/Taylor and Casey/Morgan. Paraphrase 1 keeps
Alex/Jordan and the exact protocol wording. Protected segments are identical
across paraphrases apart from name substitutions.

## Files created or changed

| Path | Work |
| --- | --- |
| `prompts/study1/` | Eighteen plain-text files: three systems, nine game bodies, two counterparty blocks, and four shared JSON instruction files; updated template index |
| `src/kinloyalty/cards.py` | Generic ordered card and counterparty block rendering |
| `src/kinloyalty/prompts.py` | YAML/text loading and exact offline request rendering |
| `src/kinloyalty/schemas.py` | Condition-independent amount/reason and comprehension schemas |
| `src/kinloyalty/review.py` | Deterministic complete prompt-review artifact generation |
| `src/kinloyalty/cli.py` | Offline `review-prompts` command |
| `configs/study1.yaml` | Paths relative to the YAML file; protected block wording moved to text templates without wording changes |
| `docs/study1_prompt_review.md` | Fully rendered prompts and canonical schemas for researcher approval |
| `tests/test_prompts.py`, `tests/test_schemas.py`, `tests/test_review.py` | Exact text/invariant, schema, and review/CLI checks |
| `README.md`, `docs/data_dictionary.md`, `docs/decisions.md` | Updated status, commands, data contract, and decisions |

No dependency changes were required; `pyproject.toml` and `uv.lock` are unchanged.

## Review and verification

Start with [the template index](../prompts/study1/README.md) to compare the
paraphrases. Then read [the complete prompt review](study1_prompt_review.md).
Its focal model is Claude Sonnet 5.5; tests exercise all four model identities.

The review expands the 45 decision × label × paraphrase combinations to 63
examples so every other-lab model name is shown, and adds 18 comprehension
examples. These 81 rendered requests are review examples, not planned paid calls
or a trial manifest. No execution rotation is selected by the renderer.

Run from the project folder:

```sh
.venv/bin/pytest
.venv/bin/kinloyalty review-prompts \
  --config configs/study1.yaml --model claude_sonnet_5_5 \
  --output /private/tmp/kin-loyalty-prompt-review.md
```

Result: **128 offline tests passed**. Checks cover exact paraphrase-1 wording and
card formatting, protected text in every paraphrase, label changes confined to
the model line, schemas identical across models/labels/paraphrases, and the
comprehension check replacing only the dictator JSON instructions. The checked-in
review is tested against regenerated output, including the installed CLI.

Offline wheel and source-distribution builds also passed. The source archive
contains all 18 template files with exact contents and excludes local coding
instructions and secrets. Python syntax/public docstrings and Git tracking rules
were checked as well.

These checks establish text/rendering invariants, not model comprehension or
provider API compatibility. Provider verification and paid batches remain later
approved phases. The repository ignores `codex_prompts/` while versioning the
experiment templates in `prompts/`.

## Open items and next phase

Please approve all prompt text, the canonical schemas, and the Riley/Taylor and
Casey/Morgan name pairs, or specify edits. No other Phase 2 blockers remain.

Phase 3 would build deterministic balanced manifests, the mock client, JSONL
logging, response validation, API-error retry handling, one identical re-ask,
exclusions, and resumable execution, using the mock client only. Before its
implementation, the exact pilot allocation, joint comprehension rotation, and
infrastructure settings must be settled as recorded in the decision log. Phase 3
requires separate permission and has not started.
