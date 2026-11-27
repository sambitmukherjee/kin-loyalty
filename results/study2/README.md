# Study 2 preregistered analysis

`main/` contains unchanged outputs produced on 2026-11-27 from annotated tag
`study2-data`, commit `3b3b85d77c619fcc6fb093a93915e5ef769cbf53`.
The replay verified all 960 episodes and 8,417 attempts before inference.

The original command below was run inside that frozen checkout, with its source
first on `PYTHONPATH` and the locked dependencies available. Its output directory
was new at that time:

```sh
.venv/bin/kinloyalty study2 reproduce \
  --manifest data/study2/main/manifest.jsonl \
  --directory data/study2/main \
  --output results/study2/main
```

The scientific analysis, configuration, prompts, dependencies, protocol and
scoring match `prereg-study2` (`c277054e182eb3a81a475108fa3439e96e869bb0`).
The full tag diff is **not data-only**: it includes the already approved main
execution/dual-provenance patch `4e088670c0cc8386eccf8fff01d93d353a230bda`,
documented in [the decision log](../../docs/decisions.md) and
[the execution patch report](../../docs/study2_main_execution_patch.md). The
paper reports this mechanical deviation.
No analysis code, parameters or seeds changed for this analysis.

Independent reproduction from the then-current main commit
`78aac6a5125c293b2a9f66f50b3f061624c7da80`, writing to
`scratch/study2-reproduce/`, matched all 16 numeric CSV tables, all eight figure
files, `resamples.npz` and `report.md` byte-for-byte. Only the execution commit
in `metadata.json` and its artifact-inventory digest differed.
See [reproduction-check.json](reproduction-check.json).

The complete ordered results are in [analysis-summary.md](analysis-summary.md).
Exact numeric tables and the unmodified generated report are under `main/`.
Earlier smoke, pilot and main-collection reports remain separate; smoke/pilot
and probes are ineligible for inference. Study 1 artifacts were not changed.

For another reproduction from the repository root, use the same manifest and
collection with `--output scratch/study2-reproduce`. The output path must not
already exist. The committed `main/` directory is the saved reference output.
The [main README](../../README.md#quickstart-a-reproduce-the-paper) gives the
current starting commands; the [analysis guide](../../docs/study2_analysis.md)
explains replay, outcomes and inference.
