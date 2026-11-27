# Reproduce the paper from the recorded responses

This guide recreates the registered analyses for both studies from the saved
model responses. It does not make new model calls or require API keys. The
commands use the original analysis code, configuration and random seeds.
They write new outputs under `scratch/reproduction/`, leaving the committed
data and reference results in place.

Study 1 has 3,600 main decisions and a separate final-prompt comprehension check.
Study 2 has 960 main negotiations. Smoke tests, pilots and forced-position probes
do not enter either main analysis. Reproduction of the paper's typesetting is a
separate step, described under [Paper figures, tables and PDF](#paper-figures-tables-and-pdf).

## 1. Get the repository and required tools

Use Git, [uv](https://docs.astral.sh/uv/getting-started/installation/) and
CPython 3.11.5 for the verified environment. The project accepts Python 3.11 or
later, but the original study environment and this guide's verification used
3.11.5. The dependency versions are fixed in `uv.lock`. The verified uv version
is 0.13.10. The commands below use a macOS or Linux shell; the collection and
replay modules use `fcntl`, so native Windows execution is not supported.

Clone the complete repository, including its history and tags:

```sh
git clone https://github.com/sambitmukherjee/kin-loyalty.git
cd kin-loyalty
uv --version
```

An ordinary clone downloads the required tags. A source ZIP or a shallow clone
does not provide the complete Git history needed by these instructions. If you
already have a clone, start at its root and make sure the four study tags are
available. The [registration index](../preregistration/README.md) explains them.

The first dependency installation needs internet access to download packages.
The later `uv run --offline --locked` commands use the installed dependencies
and cache. The `--locked` option prevents uv from updating the dependency lock.
See [uv's locking documentation](https://docs.astral.sh/uv/concepts/projects/sync/)
for the distinction between installing dependencies and changing the lockfile.

## 2. Create the frozen study checkouts

A Git worktree is another checkout of the same repository in a separate folder.
Each worktree below selects the completed data tag and therefore the analysis
code that was present when that collection was frozen. The data tags predate
the committed main analysis outputs. Those reference outputs are available in
the main checkout's `results/` directory.

Run these commands from the main checkout's root. The destination folders must
not already exist:

```sh
git worktree add worktrees/study1-data study1-data
git worktree add worktrees/study2-data study2-data
git -C worktrees/study1-data rev-parse HEAD
git -C worktrees/study2-data rev-parse HEAD
mkdir -p scratch/reproduction
```

The two printed commit hashes must be:

| Checkout | Expected commit |
| --- | --- |
| `worktrees/study1-data/` | `f7dd0a690a5089b245fff365acf002fcfd7b056a` |
| `worktrees/study2-data/` | `3b3b85d77c619fcc6fb093a93915e5ef769cbf53` |

Stop if either hash differs. The earlier `prereg-study1` and `prereg-study2`
tags preserve the registrations before collection; the data tags include the
recorded responses needed here. Study 2's data tag also contains the documented
[main-execution patch](study2_main_execution_patch.md). That patch left the
registered scientific analysis unchanged.

For a local Matplotlib cache, run this once while still at the main checkout's
root. It keeps the cache outside both frozen worktrees:

```sh
export MPLCONFIGDIR="$(pwd)/scratch/reproduction/matplotlib"
```

## 3. Reproduce Study 1

Enter the Study 1 worktree and install its own environment:

```sh
cd worktrees/study1-data
uv sync --locked --python 3.11.5
uv run --offline --locked python -c 'from pathlib import Path; import kinloyalty; print(kinloyalty.__file__); assert Path(kinloyalty.__file__).resolve().is_relative_to(Path.cwd() / "src")'
git status --short
```

The printed module path must be inside this worktree's `src/kinloyalty/` folder.
The assertion checks that Python is using this checkout. `git status --short`
should print nothing. An environment copied or linked from another checkout can
import that other checkout's code, which is why each study gets its own
`uv sync` installation.

If uv cannot find or download Python 3.11.5, install that interpreter separately
and replace `--python 3.11.5` with its executable path. For example,
`--python /absolute/path/to/python3.11` selects an installed interpreter; check
its patch version with `uv run --offline --locked python --version`.

Now run the analysis:

```sh
uv run --offline --locked kinloyalty reproduce --config configs/study1.yaml \
  --data data/study1/main \
  --comprehension data/study1/repilot_20261126/comprehension \
  --output ../../scratch/reproduction/study1
cd ../..
```

The final `cd` returns to the main checkout's root. The analysis validates the
recorded attempts before calculating results. The separate comprehension input
is required to recreate the paper's comprehension table and plot. It supplies
the final prompts' check, not additional main decisions.

The new `scratch/reproduction/study1/` directory should contain twelve CSV
tables, four figures in both PDF and PNG form, a resampling archive and two
provenance/checksum files. The archive is `resampling_distributions.npz`.
The registered analysis uses 10,000 bootstrap samples and 10,000 permutations.

## 4. Replay and reproduce Study 2

From the main checkout's root, install the Study 2 environment and check its
source path:

```sh
cd worktrees/study2-data
uv sync --locked --python 3.11.5
uv run --offline --locked python -c 'from pathlib import Path; import kinloyalty; print(kinloyalty.__file__); assert Path(kinloyalty.__file__).resolve().is_relative_to(Path.cwd() / "src")'
git status --short
```

The module path must be inside this worktree, and Git should report no changes.
The manifest is the fixed plan saved before collection; it identifies each
episode and its settings. Replay reads that plan and the recorded turns:

```sh
uv run --offline --locked kinloyalty study2 replay \
  --manifest data/study2/main/manifest.jsonl \
  --directory data/study2/main
```

Replay rebuilds each negotiation from its turn records and checks the result
against its saved episode summary. It should report 960 verified episodes,
8,417 verified attempts, zero probes and an empty list of unfinished episodes.
Stop if replay fails or any episode remains unfinished. Reproduction also
performs this check internally, so a separate replay is an early diagnostic.

With replay successful, run the registered analysis:

```sh
uv run --offline --locked kinloyalty study2 reproduce \
  --manifest data/study2/main/manifest.jsonl \
  --directory data/study2/main \
  --output ../../scratch/reproduction/study2
cd ../..
```

The new directory should contain sixteen CSV tables under `tables/`, four
figures in PDF and PNG form under `figures/`, `resamples.npz`, `metadata.json`,
`report.md` and `artifacts.sha256.json`. The fixed analysis uses 10,000 scenario
bootstrap samples and 10,000 permutations. Do not pass `--allow-synthetic` or
change the replication counts for reproduction of the observed study.

Both pipelines require a new output directory. To repeat either run, choose
another output path or move the previous output aside. Keep the reference
outputs in `results/` intact.

## 5. Compare the outputs with the saved results

The repository includes a read-only comparison command. From the main checkout's
root, run it with the Study 1 environment created above:

```sh
worktrees/study1-data/.venv/bin/python docs/verify_reproduction.py \
  --study1 scratch/reproduction/study1 \
  --study2 scratch/reproduction/study2 \
  --report scratch/reproduction/comparison.json
```

The report path must be new. This command checks both directories against
`results/study1/generated/` and `results/study2/main/`. It requires identical CSV
and figure bytes, compares every saved resampling array exactly, including
missing values, and verifies each directory's checksum inventory. It also checks
the recorded parameters, seeds and package versions. A checksum is a file's
digital fingerprint; the inventory lets the command detect changed files.
A successful comparison prints `"matched": true` and exits with status zero.
It does not calculate a new estimate or test.

Provenance files record the code version, input files and software used for a
run. Some differences in these records are expected and are listed separately:

- Study 1 records absolute input paths, which change in another clone. The
  comparison permits different path names only when the input file digests match.
- The recorded Git commit can change when the same analysis is run from another
  checkout. A current-main run can also have a larger package-source inventory
  because it includes Study 2. Existing Study 1 analysis file digests must match.
- `code_dirty` records whether Git saw changes anywhere in the checkout. It can
  include newly written, untracked output files. The saved Study 1 output has
  this flag set to true; the clean-worktree route above writes outside the
  worktree and records false. This changes provenance, while the compared
  scientific files remain identical.
- A provenance file's changed checksum also changes its entry in
  `artifacts.sha256.json`. Each inventory must still match its own files.
- A compressed resampling archive can differ as a file while containing
  identical arrays. The command reports both checks separately.

The comparison requires figure bytes to match and does not automatically excuse
a difference as PDF metadata. If it reports a difference, retain the outputs
and inspect it. Rendering can depend on the software and fonts available on
another system. The validation record describes the platform tested here;
other platforms have not been verified by this documentation pass. Do not
change the analysis or seeds to force a match.

The [documentation reproduction check](reproduction-validation.json) records
the fresh-environment test of these instructions. The original independent
audits remain available for [Study 1](../results/study1/reproducibility.json)
and [Study 2](../results/study2/reproduction-check.json).

## Paper figures, tables and PDF

The analysis commands recreate the scientific outputs. The paper adds its own
layout, drawing and numerical formatting steps. This map identifies the source
of each main-paper element and the appendix plots.

| Paper element | Saved source and generation step |
| --- | --- |
| Main Figure 1, the three contrast panels | `results/study1/generated/contrasts.csv` supplies the unadjusted `own_model` minus `other_lab` rows for each decision and model, plus the pooled rows. `paper/figures/make_figure1.py` draws these estimates and intervals. It does not fit a model. |
| Main Table 1, the four models | `configs/models.yaml` supplies the registered identities. The Intelligence Index scores come from the author-supplied chart preserved in `paper/sources/`, with its source link and checksum. They are external benchmark values, not study analysis outputs. |
| Main Table 2, the two-by-two mean shares | `results/study2/main/tables/actual_kinship_means.csv` supplies the self/cross-pair rows with displayed labels `same` and `other`. The paper prints three decimals and omits the undisclosed baseline rows from this table. |
| Appendix Figures 2–5 | Study 1's `main_distributions`, `responder_distributions`, `s1_coefficients` and `comprehension` plots are generated in `results/study1/generated/`. |
| Appendix Figures 6–9 | Study 2's `main_label_by_actual_kinship`, `deal_rate_and_within_deal_share`, `appendix_buyer_p2` and `appendix_share_distributions` plots are generated in `results/study2/main/figures/`. |
| Appendix result tables | `paper/appendix/build_tables.py` formats the saved tables and metadata. `paper/appendix/number-trace.json` identifies each displayed result cell's source file, row and field. Repeated counts are condensed only after equality checks. |
| Main-text numerical statements | `paper/numeric-audit.json` records the saved sources and rounding checks. `paper/check_numbers.py` recomputes the documented arithmetic checks from those saved results, including the mean room for agreement and the explicitly non-registered Bonferroni remark. |

To redraw main Figure 1 separately, run the following from a disposable current
checkout after creating the study environments above:

```sh
worktrees/study1-data/.venv/bin/python paper/figures/make_figure1.py
```

This writes `paper/figures/figure1.pdf` and its source manifest. It reads the
committed contrast CSV, which the comparison step above checks against the
newly reproduced CSV. The verification run reproduced the vector PDF and source manifest
byte for byte. It does not compile or edit the manuscript.

The appendix uses enlarged lettering in copies of the registered plots; their
data are unchanged. Original and paper-asset checksums are recorded in
[asset-manifest.json](../paper/appendix/asset-manifest.json). The
[appendix source map](../paper/appendix/source-map.md) gives the sources of the
remaining materials and protocol statements.

The paper rounds decimal ties to the nearest even final digit; for example,
4.175 becomes 4.18. The formatter uses Python's Decimal arithmetic. Unadjusted
pooled Study 1 values are recovered as exact multiples of 1/240 dollars before
rounding to cents. The appendix keeps four p-value decimals except for a below-0.05 value
that would otherwise display as 0.0500; that value has six decimals. Per-pair
Study 2 message means have two exact decimals. A final printed digit can
therefore differ from the earlier analysis report's number formatting. The
[appendix correction report](../paper/appendix/fix-pass-report.md) records these
display rules. The numerical source files are preserved unchanged.

The existing PDF is [paper/main.pdf](../paper/main.pdf). Its build command is
`bash paper/build.sh`, and the existing dependencies and asset workflow are
described in [paper/README.md](../paper/README.md). The frozen data checkouts
predate the manuscript, so a PDF build belongs in a separate current checkout.
The analysis steps above do not require PDF build tools. The current paper
build still uses Codex-specific Poppler paths, so its PDF build is not yet
portable to an ordinary installation. This limitation does not affect the
analysis commands or the saved plots.

## Common problems

| Problem | What to check |
| --- | --- |
| An output directory or comparison report already exists. | Choose a new destination or move the earlier output aside. The commands deliberately refuse to overwrite it. |
| An offline uv command cannot find a package. | Run `uv sync --locked --python 3.11.5` with internet access in that worktree first. Keep `uv.lock` unchanged. |
| Python imports another checkout. | Check the printed module path. Use the worktree's own environment, remove an inherited `PYTHONPATH` override and avoid a shared editable installation. |
| The comprehension table or plot is absent. | Include `data/study1/repilot_20261126/comprehension` with `--comprehension`. The original comprehension batch used earlier prompts. |
| Replay or input validation fails. | Check the selected tag, input paths and file integrity. Preserve the files and diagnostic message rather than repairing research logs automatically. |
| Results are labelled simulated. | Check the inputs. The paper uses the real main collections, without `--allow-synthetic`. |
| A Git tag or historical file is missing. | Use a full clone with the required tags. A source archive is insufficient for the frozen-checkout procedure. |
| Figure bytes differ while CSV files match. | Keep the comparison report and compare the rendering environment and figures. The checker does not silently accept unexplained figure differences. |

## Clean up the temporary checkouts

After comparison, return to the main checkout's root. Remove the worktrees with
Git so that its worktree records are also removed:

```sh
git worktree remove worktrees/study1-data
git worktree remove worktrees/study2-data
git status --short
```

The study environments are ignored files within those worktrees and are removed
with them. If Git reports tracked changes, inspect those changes instead of
forcing removal. The reproduction outputs and comparison report remain under
`scratch/reproduction/` for inspection. That directory is ignored by Git and can
be deleted when no longer needed. All tracked files should remain unchanged.
