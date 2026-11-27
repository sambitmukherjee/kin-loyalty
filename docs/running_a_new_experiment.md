# Run a new experiment with the existing engines

This guide takes you through two offline examples: a single-decision experiment
using the Study 1 engine, and a negotiation experiment using the Study 2 engine.
You will copy configurations and prompts, inspect the requests, collect mock
responses, resume saved work and produce analysis tables and figures. No part of
the worked examples contacts a model provider or needs API keys.

A **manifest** is the fixed list of planned decisions or negotiations saved
before collection. An **attempt** is one call made while carrying out that plan.
A negotiation is an **episode**, which can contain several messages and more
than one attempt at a message. The logs retain unsuccessful attempts as well as
valid responses, so a final result can be traced back to what happened.
JSONL is a text-file format with one JSON record per line.

These engines implement the paper's particular designs. They provide useful
components for another experiment, but they are not a general experiment editor.
The examples keep the original games, model roster, conditions and allocation.
They change only copied file locations, demonstration wording, random seeds and
the demonstration's resampling count. Later sections explain where a different
design needs programming.

If your goal is to recreate the paper's findings, use
[Reproduce the paper](reproducing_the_paper.md) instead. That guide uses the frozen
code, data and original analysis settings.

## 1. Prepare a separate example

Use a current checkout with its Git history, a macOS or Linux shell, uv and
Python 3.11.5. The collection engines use `fcntl` for file locks, so native
Windows execution is not supported. The [reproduction setup](reproducing_the_paper.md#1-get-the-repository-and-required-tools)
explains installation. Run every command in this guide from the repository root:

```sh
uv sync --locked --python 3.11.5
uv run --offline --locked kinloyalty --version
```

The first installation may need internet access to download dependencies. The
remaining worked commands use the installed environment and make no network
requests. Their files go under `scratch/new-experiment-demo/`, which Git ignores.
Choose a different new directory if you have already run this example, and use
that path consistently throughout the commands.

The following command copies both configurations, the model roster and both
prompt folders. It resolves their paths within the example, replaces the copied
seeds with distinct demonstration seeds, and adds an identifying sentence to the
copied system prompts. It also removes Study 1's old prompt-approval note from
the copy. It does not change any registered file:

```sh
uv run --offline --locked python - <<'PY'
from pathlib import Path
import shutil
import yaml

example = Path('scratch/new-experiment-demo')
example.mkdir(parents=True, exist_ok=False)
(example / 'configs').mkdir()
shutil.copy2('configs/models.yaml', example / 'configs/models.yaml')
for study in ('study1', 'study2'):
    shutil.copytree(Path('prompts') / study, example / 'prompts' / study)
    config = yaml.safe_load((Path('configs') / f'{study}.yaml').read_text())
    config.update(
        models_file='models.yaml', prompt_directory=f'../prompts/{study}',
        data_directory=f'../data/{study}', results_directory=f'../results/{study}',
        status='offline_example',
    )
    config.pop('prompt_approval', None)
    config['seeds'] = {name: seed + 100_000 for name, seed in config['seeds'].items()}
    if study == 'study1':
        config['analysis']['bootstrap_resamples'] = 200
        config['analysis']['permutation_resamples'] = 200
    (example / 'configs' / f'{study}.yaml').write_text(
        yaml.safe_dump(config, sort_keys=False)
    )
    names = ('system_1.txt', 'system_2.txt', 'system_3.txt') if study == 'study1' else (
        'buyer_system.txt', 'seller_system.txt'
    )
    for name in names:
        path = example / 'prompts' / study / name
        path.write_text('This is an offline demonstration.\n' + path.read_text())
print(f'Created {example}')
PY
```

The original model roster is copied unchanged. Its verification dates describe
the original studies; they do not establish that a new model or request works
now. The copied `study` values also remain `study1` and `study2`, because they
select the existing engines. A directory name identifies this separate example;
changing a study identifier alone does not implement a new experiment.

Paths inside a study YAML file are relative to that file. CLI input and output
paths are relative to your shell's working directory. Source templates contain
placeholders that the engine fills when it constructs a request. Edit the
copies when developing another wording, then review the complete rendered text.

## 2. Inspect and run single-decision requests

First generate a human-readable review. It expands the copied templates into
complete messages and response schemas for the selected focal model, across
all configured decisions, labels and paraphrases:

```sh
uv run --offline --locked kinloyalty review-prompts \
  --config scratch/new-experiment-demo/configs/study1.yaml \
  --model claude_sonnet_5_5 \
  --output scratch/new-experiment-demo/study1-prompt-review.md
uv run --offline --locked kinloyalty manifest \
  --config scratch/new-experiment-demo/configs/study1.yaml --phase smoke \
  --output scratch/new-experiment-demo/runs/study1-smoke/manifest.jsonl
```

The review concerns one focal model; repeat it with the other configured model
keys when preparing a real study. A response schema specifies the required
fields and their permitted types and values. The smoke manifest contains four
requests, one per model. Creating a manifest makes no calls and refuses to
overwrite an existing file.

The next command saves the first frozen request as readable JSON. Open that
file and inspect the system prompt, user message, response schema and
`api_payload`, which contains the arguments prepared for the provider SDK:

```sh
uv run --offline --locked python - <<'PY'
from pathlib import Path
import json
from kinloyalty.manifest import read_manifest

example = Path('scratch/new-experiment-demo')
rows = read_manifest(example / 'runs/study1-smoke/manifest.jsonl')
output = example / 'study1-first-request.json'
output.write_text(json.dumps(rows[0]['request'], indent=2) + '\n')
print(f'{len(rows)} planned requests; inspect {output}')
PY
```

The SDK is the provider's Python client library. `context` in that JSON is local
metadata used by the mock engine. Provider adapters do not send it. The prompts
and `api_payload` contain no credentials.
A readable review helps check wording; the manifest shows the exact request
that execution will use.

Run the four mock requests, then run the same command again:

```sh
uv run --offline --locked kinloyalty run --client mock \
  --manifest scratch/new-experiment-demo/runs/study1-smoke/manifest.jsonl \
  --log scratch/new-experiment-demo/runs/study1-smoke/attempts.jsonl
uv run --offline --locked kinloyalty run --client mock \
  --manifest scratch/new-experiment-demo/runs/study1-smoke/manifest.jsonl \
  --log scratch/new-experiment-demo/runs/study1-smoke/attempts.jsonl
```

The first invocation reports four valid decisions and four calls. The second
reports `already_final: 4` and `calls_started: 0`. It reads the saved records and
skips completed work. Each JSONL line in `attempts.jsonl` is one attempt, marked
`synthetic: true` and `execution_mode: mock`. Mock token counts and returned
version strings are synthetic too.

### Resume an unfinished mock decision

To see recovery of unfinished work, the following optional example injects one
synthetic connection error into a separate log. The error is marked
non-retryable so the first invocation stops that decision immediately; it is
not a real connection failure. The other three decisions complete normally:

```sh
uv run --offline --locked python - <<'PY'
import asyncio
from dataclasses import asdict
from pathlib import Path
from kinloyalty.clients.base import ClientError
from kinloyalty.clients.mock import MockClient
from kinloyalty.manifest import read_manifest
from kinloyalty.runner import run_manifest

example = Path('scratch/new-experiment-demo')
manifest = example / 'runs/study1-smoke/manifest.jsonl'
rows = read_manifest(manifest)
client = MockClient(seed=rows[0]['mock_seed'], scripts={
    rows[0]['trial_id']: [ClientError('connection', retryable=False)]
})
summary = asyncio.run(run_manifest(
    manifest, example / 'runs/study1-recovery/attempts.jsonl', client
))
assert len(summary.unfinished_trial_ids) == 1
print(asdict(summary))
PY
uv run --offline --locked kinloyalty run --client mock \
  --manifest scratch/new-experiment-demo/runs/study1-smoke/manifest.jsonl \
  --log scratch/new-experiment-demo/runs/study1-recovery/attempts.jsonl
```

The resumed invocation skips three completed decisions and makes one new call.
All four decisions are then valid. The log retains the failed attempt, followed
by the successful attempt for that decision. For a real non-retryable error,
resolve its cause before resuming.

An invalid model reply and an API error have different consequences. Under the
existing rules, one invalid reply gets one identical fresh re-ask; two invalid
replies exclude the decision. API errors do not consume those response
opportunities. Exhausted errors leave work unfinished. Resume preserves earlier
invalid replies and attempt counters; it does not grant another re-ask. See
[engine behavior and recovery](engine.md) for retry budgets and pending records.

## 3. Produce single-decision analysis outputs from synthetic data

Four smoke decisions are too few for the existing main analysis, which requires
all planned main cells to be terminal. The simulator below creates separate
main, pilot and comprehension batches through the mock runner. With the copied
design, their sizes are 3,600, 240 and 320 decisions:

```sh
uv run --offline --locked kinloyalty simulate-study1 \
  --config scratch/new-experiment-demo/configs/study1.yaml \
  --directory scratch/new-experiment-demo/runs/study1-simulated \
  --own-model-effect 12
uv run --offline --locked kinloyalty reproduce \
  --config scratch/new-experiment-demo/configs/study1.yaml \
  --data scratch/new-experiment-demo/runs/study1-simulated/main \
  --comprehension scratch/new-experiment-demo/runs/study1-simulated/comprehension \
  --output scratch/new-experiment-demo/analysis/study1 --allow-synthetic
```

`--own-model-effect 12` deliberately shifts the mock's own-model numeric answers;
it is not a response to the edited wording or a finding about any model. The
analysis reads only the simulated main decisions and the separate comprehension
batch. Pilot decisions stay out of main inference.

Inspect `analysis/study1/contrasts.csv`, `equivalence.csv`, `coverage.csv`, the
PDF/PNG figures and `provenance.json` under the example directory. The analysis
also saves `resampling_distributions.npz` and an artifact hash inventory. Outputs
are marked synthetic. This demonstration uses 200 bootstrap and permutation repetitions
from its copied configuration, rather than the paper's 10,000. That smaller
count makes a mechanics check quicker; it is not a recommended scientific
analysis setting. The [Study 1 analysis guide](analysis.md) explains the methods,
coverage requirements and other output files.

## 4. Inspect, run and replay negotiations

The negotiation engine freezes the configuration, templates, scenarios and
schemas in the manifest. It constructs each later request from that snapshot
and the saved public transcript. Each role receives only its own private limit.
A prompt review uses fixed illustrative transcripts so you can inspect the
opening and late-message instructions without collecting responses:

```sh
uv run --offline --locked python -m kinloyalty.negotiation.review \
  --config scratch/new-experiment-demo/configs/study2.yaml \
  --output scratch/new-experiment-demo/study2-prompt-review.md
uv run --offline --locked kinloyalty study2 manifest \
  --config scratch/new-experiment-demo/configs/study2.yaml --phase synthetic \
  --scenario-seed 83101 --order-seed 83102 --swapped-seed 83103 \
  --output scratch/new-experiment-demo/runs/study2-mock/manifest.jsonl
```

This synthetic plan contains 960 episodes: 16 ordered model pairs, 20 scenarios
per pair and three disclosure conditions. It contains no probes. Synthetic
plans require explicit scenario, order and swapped-name seeds distinct from the
configured main seeds. The mock's own seed is already frozen from the copied
configuration.

Save one opening request for inspection before executing the plan:

```sh
uv run --offline --locked python - <<'PY'
from dataclasses import asdict
from pathlib import Path
import json
from kinloyalty.negotiation.config import config_from_snapshot
from kinloyalty.negotiation.manifest import initial_state, read_manifest, spec_from_row
from kinloyalty.negotiation.requests import build_turn_request

example = Path('scratch/new-experiment-demo')
rows = read_manifest(example / 'runs/study2-mock/manifest.jsonl')
config = config_from_snapshot(rows[0]['snapshot'])
request = build_turn_request(config, spec_from_row(rows[0]), initial_state(rows[0], config))
output = example / 'study2-first-request.json'
output.write_text(json.dumps(asdict(request), indent=2) + '\n')
print(f'{len(rows)} planned episodes; inspect {output}')
PY
uv run --offline --locked kinloyalty study2 run --client mock \
  --manifest scratch/new-experiment-demo/runs/study2-mock/manifest.jsonl \
  --directory scratch/new-experiment-demo/runs/study2-mock/collection
uv run --offline --locked kinloyalty study2 run --client mock \
  --manifest scratch/new-experiment-demo/runs/study2-mock/manifest.jsonl \
  --directory scratch/new-experiment-demo/runs/study2-mock/collection
uv run --offline --locked kinloyalty study2 replay \
  --manifest scratch/new-experiment-demo/runs/study2-mock/manifest.jsonl \
  --directory scratch/new-experiment-demo/runs/study2-mock/collection
```

The first run completes 960 episodes. Repeating it reports `already_final: 960`
and `new_calls: 0`. Replay independently reconstructs each episode from its
attempts and compares that reconstruction with the saved summary. It should
report `episodes_verified: 960` and an empty `unfinished_unit_ids` list. Replay
makes no new responses and does not repair pending attempts; resume the runner
first if pending work needs recovery.

For an interrupted negotiation, rerun the same execution command with the same
manifest and collection directory. It reconstructs the saved progress before
continuing the unfinished message or episode. Earlier invalid replies still
count toward the re-ask limit.

In the collection directory, `turns/` contains one attempt-log file per ordered
model pair. `episodes.jsonl` contains completed episode summaries, and
`run_summary.json` records collection mechanics. Attempts preserve the full
request, raw response, validation and API-error metadata; a valid message
advances the transcript. Rejected responses do not become public messages.
[The data dictionary](data_dictionary.md#study-2-persisted-records-version-1)
explains the fields and pending journals.

Now analyse those synthetic logs, writing to a new directory:

```sh
uv run --offline --locked kinloyalty study2 reproduce \
  --manifest scratch/new-experiment-demo/runs/study2-mock/manifest.jsonl \
  --directory scratch/new-experiment-demo/runs/study2-mock/collection \
  --output scratch/new-experiment-demo/analysis/study2 \
  --allow-synthetic --resamples 200
```

The command replays the collection before analysis. It produces `tables/`,
`figures/`, `metadata.json`, `resamples.npz`, `report.md` and a hash inventory.
The report is labelled `SIMULATED VERIFICATION ONLY`. The `--resamples` override
is accepted only for explicit synthetic verification; real analysis uses the
manifest's frozen settings. Smoke, pilot and probe records are never eligible
for this main-analysis pipeline. The [Study 2 analysis guide](study2_analysis.md)
explains the available outcomes, missing values and output tables.

All examples stay in `scratch/new-experiment-demo/`. The
[worked-example verification](new-experiment-validation.json) records their
completion and resume checks. You can retain that directory for inspection or
remove it when you are finished. The repository's real study files are separate.

## 5. Move from an example to a new research design

For a real project, keep versioned configurations, prompt sources and launcher
code in a separate experiment directory or fork, rather than leaving them only
in ignored `scratch/`. Save the manifest, exact code revision, dependency lock
and collection logs with that experiment. Keep credentials local. The frozen
registrations and existing artifacts should continue to identify the original
studies.

Decide the hypotheses, design, eligibility rules and inference before collecting
the new main data. A wording or model change can change the scientific question
even when the existing code can run it. The following distinctions help identify
how much implementation work is needed:

| Proposed change | Existing support and further work |
| --- | --- |
| Change wording while retaining the same game, fields and design | Copy templates, preserve their placeholders, regenerate the review and manifest, and check the resulting requests. Mock responses check mechanics, not how a model understands the new text. |
| Change an API model ID on a supported provider | Review its actual request requirements and test the adapter. Recheck roster balance and model names in cards; a YAML entry alone does not establish compatibility. See [adding a model](adding_a_model.md). |
| Change model count, labels, paraphrases or allocation | Reconcile manifest allocation, expected counts, comprehension checks, contrasts and figures. Existing balance checks can reject unsupported combinations. |
| Add an outcome or a different game | Implement the corresponding schema, validation, mock behavior, manifest and analysis support. See [adding a game](adding_a_game.md). |
| Change negotiation conditions, roles, information flow or action rules | Extend the negotiation configuration, request/state/rule/replay code and analysis together. Several original-study choices are validated explicitly. |
| Run another live negotiation study | Implement a launcher and collection authorization for that study. The original live main launcher accepts only its registered manifest. |

Configuration fields are not a promise that every value is implemented. For
example, the negotiation loader requires the original three conditions and
Alex/Jordan roles, while the provider payload builder requires stateless calls
with provider-default sampling. Changing descriptive YAML metadata does not
rewrite these checks or the provider's wire-format arguments.

## 6. Live collection interfaces and their limits

The public `kinloyalty run` and `kinloyalty study2 run` commands accept only
`--client mock`. There is no `--client live` option. The public Study 2 manifest
command offers `synthetic`, `smoke` and `pilot`, rather than a general main-run
builder. A new live main negotiation collection needs its own planning and launch code.
The following interfaces exist in the Python package:

| Interface | What it provides |
| --- | --- |
| `clients.factory.create_provider_clients(requests, env_path=...)` | Checks frozen provider arguments, loads credentials and constructs a provider router; construction itself makes no model calls. |
| `runner.run_manifest(manifest_path, log_path, client)` | Executes or resumes Study 1 requests using a supplied mock or live client, with durable attempt logs and the frozen retry policy. |
| `cohort.run_cohort(batches, client)` | Runs separate Study 1 batches under shared concurrency limits, retaining separate logs and stopping the cohort on a non-retryable API error. |
| `negotiation.runner.run_manifest(manifest_path, directory, clients, authorization=...)` | Runs negotiation collections; live calls require one of the explicit authorization types and clean committed code. Existing types encode the original study's scopes. |
| `negotiation.engine.run_episode(...)` | Runs a single episode in memory with mock clients by default. Lower-level live execution is not a durable collection launcher. |

For Study 1, the essential transport wiring is shown below. This is an
illustration for a new launcher, not part of the offline worked example. Calling
`run_manifest` with this live router makes paid requests:

```python
from dataclasses import asdict
from kinloyalty.clients.base import ModelRequest
from kinloyalty.clients.factory import create_provider_clients
from kinloyalty.manifest import read_manifest
from kinloyalty.runner import run_manifest

async def collect(manifest_path, log_path, env_path):
    rows = read_manifest(manifest_path)
    requests = [ModelRequest(**row['request']) for row in rows]
    client = create_provider_clients(requests, env_path=env_path)
    try:
        return asdict(await run_manifest(manifest_path, log_path, client))
    finally:
        await client.aclose()
```

This wiring supplies retries and durable logs, but the Study 1 runner does not
provide a cumulative spending cap or an automatic model-version drift stop.
Those checks, the new study's expected returned versions, and its collection
plan belong in the new launcher. Count retry and re-ask attempts in its budget.
Keep the same manifest, code revision and logs when resuming; changing a frozen
request requires a new plan and collection, not editing the old manifest.

The generic provider factory reads the standard credential names in
[.env.example](../.env.example), with nonempty process-environment values taking
precedence over the specified `.env` file. Its mapping is in `factory.KEY_NAMES`;
changing only a model's `api_key_env` metadata does not change that mapping.
Credentials and request headers must never be copied into manifests or logs.

Study 2's dedicated `negotiation.smoke`, `negotiation.pilot` and
`negotiation.main_run` modules launched the original live batches. They use the
checkout's ignored `.env` only, without process-environment precedence. The
smoke and pilot launchers embed original budgets and prior-version checks. The
main launcher checks the exact registered manifest hash and original
registration, and binds every resumption to its recorded execution revision.
They are historical collection tools, not launchers for a different study.
Changing an old approval field or passing a new configuration does not create a
new live-collection contract.

A new live negotiation experiment therefore needs its own reviewed launcher,
authorization, expected versions, attempt budget and replay/analysis support for
that contract. Preserve the existing scopes. Check every intended provider's
current official documentation, then run a small, explicitly planned smoke
collection using the new requests. Include opening and late-message schemas
for each role when the protocol changes what actions are allowed. The
[provider verification report](provider_verification.md) is historical evidence
for the original requests, not a current guarantee for a new model.

## Common problems

| Symptom | Explanation and next step |
| --- | --- |
| A manifest, simulation or result destination already exists. | Use a fresh path. These commands refuse to replace existing artifacts. The execution commands, in contrast, reuse their existing manifest and logs to resume. |
| Edited templates do not change a resumed request. | Requests come from the frozen manifest or snapshot. Build a new plan and use new logs for the edited experiment. |
| A new configuration fails a balance or identity check. | Reconcile the design with the implemented allocation and analysis. Do not remove a check merely to make an unsupported design run. |
| Main analysis refuses smoke, pilot or probe data. | Use a completed main design or the explicit synthetic example. Keep development batches separate from main inference. |
| Synthetic analysis is refused. | Pass `--allow-synthetic` for mock data only. Do not relabel synthetic records as live. |
| Replay finds pending work, damaged JSONL or a mismatched episode. | Stop collection, retain the original files and inspect the history. Resume can recover valid pending journals; it does not silently repair corrupt or conflicting records. |
| Two writers try to use the same logs. | Stop the second writer. The engines use advisory locks to prevent concurrent writers; do not remove a lock to bypass an active collection. |
