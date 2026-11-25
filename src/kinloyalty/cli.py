"""Expose offline prompt review, frozen manifests, and mock-only execution."""

import argparse
import asyncio
import json
from collections.abc import Sequence
from dataclasses import asdict
from pathlib import Path

from kinloyalty import __version__


def main(argv: Sequence[str] | None = None) -> None:
    """Display package information or write an offline prompt-review artifact."""
    parser = argparse.ArgumentParser(
        prog="kinloyalty",
        description="Study 1 tools. Execution currently supports the offline mock client only.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    commands = parser.add_subparsers(dest="command")
    review = commands.add_parser("review-prompts", help="Write complete rendered prompts for review.")
    review.add_argument("--config", type=Path, default=Path("configs/study1.yaml"))
    review.add_argument("--model", required=True, help="Focal model key in the configured roster.")
    review.add_argument("--output", type=Path, default=Path("docs/study1_prompt_review.md"))
    manifest = commands.add_parser("manifest", help="Freeze a deterministic, balanced trial plan.")
    manifest.add_argument("--config", type=Path, default=Path("configs/study1.yaml"))
    manifest.add_argument("--phase", choices=("smoke", "pilot", "comprehension", "main"), required=True)
    manifest.add_argument("--output", type=Path, required=True)
    run = commands.add_parser("run", help="Execute or resume a manifest with mock responses only.")
    run.add_argument("--manifest", type=Path, required=True)
    run.add_argument("--log", type=Path, required=True)
    run.add_argument("--client", choices=("mock",), required=True)
    run.add_argument("--mock-seed", type=int, default=None)
    args = parser.parse_args(argv)
    if args.command == "review-prompts":
        from kinloyalty.prompts import load_prompt_library
        from kinloyalty.review import write_prompt_review

        try:
            library = load_prompt_library(args.config)
            write_prompt_review(library, args.output, model=args.model)
        except (OSError, ValueError, KeyError) as error:
            parser.error(str(error))
        print(f"Wrote prompt review to {args.output}")
    elif args.command == "manifest":
        from kinloyalty.manifest import build_manifest, write_manifest

        try:
            trials = build_manifest(args.config, args.phase)
            write_manifest(trials, args.output)
        except (OSError, ValueError, KeyError) as error:
            parser.error(str(error))
        print(f"Wrote {len(trials)} planned trials to {args.output}; no calls made.")
    elif args.command == "run":
        from kinloyalty.clients.mock import MockClient
        from kinloyalty.manifest import read_manifest
        from kinloyalty.runner import run_manifest

        try:
            trials = read_manifest(args.manifest)
            seed = trials[0]["mock_seed"] if args.mock_seed is None else args.mock_seed
            summary = asyncio.run(run_manifest(args.manifest, args.log, MockClient(seed=seed)))
        except (OSError, ValueError, KeyError) as error:
            parser.error(str(error))
        print(json.dumps(asdict(summary), indent=2))
        if summary.unfinished_trial_ids:
            raise SystemExit(1)
    else:
        parser.print_help()
