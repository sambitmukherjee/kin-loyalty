"""Expose isolated Study 2 planning, mock collection, replay, and probe reporting."""

import argparse
import asyncio
import json
from collections.abc import Sequence
from pathlib import Path

from kinloyalty.negotiation.collection import replay_collection
from kinloyalty.negotiation.config import config_from_snapshot
from kinloyalty.negotiation.manifest import build_manifest, read_manifest, write_manifest
from kinloyalty.negotiation.mock import NegotiationMockClient
from kinloyalty.negotiation.probes import write_probe_report
from kinloyalty.negotiation.runner import run_manifest


def main(argv: Sequence[str] | None = None) -> None:
    """Run Study 2 commands without reading credentials or invoking Study 1 analysis."""
    parser = argparse.ArgumentParser(prog='kinloyalty study2', description='Offline Study 2 tools; execution uses mocks only.')
    commands = parser.add_subparsers(dest='command', required=True)
    manifest = commands.add_parser('manifest', help='Freeze a new self-contained episode/probe plan.')
    manifest.add_argument('--config', type=Path, default=Path('configs/study2.yaml'))
    manifest.add_argument('--phase', choices=('synthetic', 'smoke', 'pilot'), required=True)
    manifest.add_argument('--scenario-seed', type=int)
    manifest.add_argument('--order-seed', type=int)
    manifest.add_argument('--swapped-seed', type=int)
    manifest.add_argument('--output', type=Path, required=True)
    run = commands.add_parser('run', help='Run/resume with synthetic responses and durable journals.')
    run.add_argument('--client', choices=('mock',), required=True)
    run.add_argument('--mock-seed', type=int)
    run.add_argument('--label-effect', type=float, default=0.0)
    replay = commands.add_parser('replay', help='Verify outcomes and probe records from saved attempts.')
    report = commands.add_parser('probe-report', help='Write probe mechanics and exact transcript requests.')
    report.add_argument('--output', type=Path, required=True)
    for command in (run, replay, report):
        command.add_argument('--manifest', type=Path, required=True)
        command.add_argument('--directory', type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == 'manifest':
            rows = build_manifest(args.config, args.phase, scenario_seed=args.scenario_seed,
                                  order_seed=args.order_seed, swapped_seed=args.swapped_seed)
            write_manifest(rows, args.output)
            print(f'Wrote {len(rows)} Study 2 units to {args.output}; no model calls made.')
        elif args.command == 'run':
            rows = read_manifest(args.manifest)
            config = config_from_snapshot(rows[0]['snapshot'])
            seed = rows[0]['mock_seed'] if args.mock_seed is None else args.mock_seed
            clients = {model: NegotiationMockClient(seed=seed, label_effect=args.label_effect) for model in config.model_order}
            summary = asyncio.run(run_manifest(args.manifest, args.directory, clients))
            print(json.dumps(summary, indent=2))
            if summary['unfinished_unit_ids']:
                raise SystemExit(1)
        elif args.command == 'replay':
            summary = replay_collection(args.manifest, args.directory)
            print(json.dumps(summary, indent=2))
            if summary['unfinished_unit_ids']:
                raise SystemExit(1)
        else:
            write_probe_report(args.manifest, args.directory, args.output)
            print(f'Wrote unscored probe mechanics to {args.output}.')
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.error(str(error))


if __name__ == '__main__':
    main()
