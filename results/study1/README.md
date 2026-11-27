# Study 1 pre-registered analysis

Generated on 2026-11-27 from tag **`study1-data`**, commit
`f7dd0a690a5089b245fff365acf002fcfd7b056a`. Its registered analysis/configuration/prompts
match `prereg-study1` (`d4d6ff9c1f7b84bc2b4f90578873f18dbc9fb98a`) exactly.
The frozen outputs are copied unchanged under `generated/`.

Command run inside `worktrees/study1-data/`:

```sh
uv run --offline --locked kinloyalty reproduce --config configs/study1.yaml \
  --data data/study1/main \
  --comprehension data/study1/repilot_20261126/comprehension \
  --output results/study1/generated
```

See [the ordered results report](analysis_report.md) and
[the reproducibility audit](reproducibility.json). The current-main reproduction
(commit `3b3b85d77c619fcc6fb093a93915e5ef769cbf53`) wrote to
`scratch/study1-reproduce/`: every numeric table, saved resampling array/archive,
and figure is byte-identical. Only provenance and its hash entry differ.
Code, parameters, and seeds are unchanged; Study 2 data/analysis are untouched.
The other subdirectories retain historical blind pilot/check reports.
