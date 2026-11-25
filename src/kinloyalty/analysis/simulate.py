"""Create explicitly synthetic verification batches through the ordinary mock runner."""

import asyncio
import json
from dataclasses import asdict
from pathlib import Path

from kinloyalty.clients.mock import MockClient
from kinloyalty.manifest import build_manifest, write_manifest
from kinloyalty.analysis.pipeline import load_analysis_config
from kinloyalty.runner import run_manifest


async def simulate_study1(config: str | Path, directory: str | Path, *, own_model_effect: int = 12) -> Path:
    """Generate mock main/pilot/check logs outside the configured real data/results roots."""
    config, directory = Path(config).resolve(), Path(directory).resolve()
    study, _ = load_analysis_config(config)
    for key in ("data_directory", "results_directory"):
        reserved = (config.parent / study[key]).resolve()
        if directory == reserved or reserved in directory.parents:
            raise ValueError("Synthetic verification batches must stay outside real study data/results roots.")
    if directory.exists():
        raise ValueError("Simulation directory already exists; choose a new path.")
    directory.mkdir(parents=True)
    summaries = {}
    for phase in ("main", "pilot", "comprehension"):
        manifest = directory / phase / "manifest.jsonl"
        write_manifest(build_manifest(config, phase), manifest)
        client = MockClient(seed=study["seeds"]["mock"], own_model_effect=own_model_effect)
        summary = await run_manifest(manifest, directory / phase / "attempts.jsonl", client)
        summaries[phase] = asdict(summary)
    (directory / "simulation.json").write_text(json.dumps({"synthetic": True, "own_model_effect": own_model_effect,
                                                         "summaries": summaries}, indent=2) + "\n")
    return directory
