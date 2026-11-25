"""Expose offline planning, mock execution, log-based analysis, and reproduction."""

import argparse
import asyncio
import json
from collections.abc import Sequence
from dataclasses import asdict
from pathlib import Path

from kinloyalty import __version__


def main(argv: Sequence[str] | None = None) -> None:
    """Run a selected offline command; no CLI command contacts a model provider."""
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
    analyze = commands.add_parser("analyze", help="Analyze validated saved main-run logs.")
    analyze.add_argument("study", choices=("study1",))
    reproduce = commands.add_parser("reproduce", help="Recreate Study 1 tables and figures from saved logs.")
    for command in (analyze, reproduce):
        command.add_argument("--config", type=Path, default=Path("configs/study1.yaml"))
        command.add_argument("--data", type=Path, nargs="+", default=[Path("data/study1/main")])
        command.add_argument("--comprehension", type=Path, nargs="+")
        command.add_argument("--output", type=Path, default=Path("results/study1/generated"))
        command.add_argument("--allow-synthetic", action="store_true")
    report = commands.add_parser("report", help="Report blind pilot mechanics or comprehension checks.")
    report.add_argument("phase", choices=("pilot", "comprehension"))
    report.add_argument("--config", type=Path, default=Path("configs/study1.yaml"))
    report.add_argument("--data", type=Path, nargs="+", required=True)
    report.add_argument("--output", type=Path, required=True)
    report.add_argument("--allow-synthetic", action="store_true")
    simulate = commands.add_parser("simulate-study1", help="Generate three explicitly synthetic verification batches.")
    simulate.add_argument("--config", type=Path, default=Path("configs/study1.yaml"))
    simulate.add_argument("--directory", type=Path, required=True)
    simulate.add_argument("--own-model-effect", type=int, default=12)
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
    elif args.command in {"analyze", "reproduce"}:
        from kinloyalty.analysis.pipeline import analyze_study1

        try:
            output = analyze_study1(args.config, args.data, args.output,
                                    allow_synthetic=args.allow_synthetic,
                                    comprehension_paths=args.comprehension)
        except (OSError, ValueError, KeyError) as error:
            parser.error(str(error))
        print(f"Wrote saved-log analysis to {output}; no API calls made.")
    elif args.command == "report":
        from kinloyalty.analysis.pipeline import report_batch

        try:
            output = report_batch(args.config, args.data, args.output,
                                  phase=args.phase, allow_synthetic=args.allow_synthetic)
        except (OSError, ValueError, KeyError) as error:
            parser.error(str(error))
        print(f"Wrote {args.phase} report to {output}; no API calls made.")
    elif args.command == "simulate-study1":
        from kinloyalty.analysis.simulate import simulate_study1

        try:
            output = asyncio.run(simulate_study1(args.config, args.directory,
                                               own_model_effect=args.own_model_effect))
        except (OSError, ValueError, KeyError) as error:
            parser.error(str(error))
        print(f"Wrote explicitly synthetic batches to {output}; no API calls made.")
    else:
        parser.print_help()
