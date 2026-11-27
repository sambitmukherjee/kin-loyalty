# Study 2 preregistered analysis

`main/` contains unchanged outputs produced on 2026-11-27 from annotated tag
`study2-data`, commit `3b3b85d77c619fcc6fb093a93915e5ef769cbf53`.
The replay verified all 960 episodes and 8,417 attempts before inference.

Run inside that frozen checkout, with its source first on `PYTHONPATH` and the
existing locked dependency environment:

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
documented in `docs/decisions.md`. Retain that mechanical deviation in the paper.
No analysis code, parameters or seeds changed for this analysis.

Independent reproduction from main commit
`78aac6a5125c293b2a9f66f50b3f061624c7da80`, writing to
`scratch/study2-reproduce/`, matched all 16 numeric CSV tables, all eight figure
files, `resamples.npz` and `report.md` byte-for-byte. Only the execution commit
in `metadata.json` and its artifact-inventory digest differed.
See [reproduction-check.json](reproduction-check.json).

The complete ordered results are in [analysis-summary.md](analysis-summary.md).
Exact numeric tables and the unmodified generated report are under `main/`.
Earlier smoke, pilot and main-collection reports remain separate; smoke/pilot
and probes are ineligible for inference. Study 1 artifacts were not changed.
