"""Run the approved 80-episode pilot with unchanged providers and .env-only keys."""

import argparse
import asyncio
import json
from dataclasses import asdict
from pathlib import Path

from kinloyalty.negotiation.authorization import ModelDriftError, PilotAuthorization, study1_versions
from kinloyalty.negotiation.config import config_from_snapshot
from kinloyalty.negotiation.manifest import initial_state, read_manifest, spec_from_row
from kinloyalty.negotiation.requests import build_turn_request
from kinloyalty.negotiation.runner import check_destination, run_manifest
from kinloyalty.negotiation.smoke import create_live_clients
from kinloyalty.provenance import collect_provenance


async def run_live_pilot(manifest_path: str | Path, directory: str | Path, env_path: str | Path) -> dict:
    """Collect only the approved pilot; no inference or disclosure comparisons."""
    rows = read_manifest(manifest_path)
    if len(rows) != 80 or any(row['phase'] != 'pilot' or row['is_probe'] for row in rows):
        raise ValueError('Live pilot accepts only the approved 80 natural episode plan.')
    provenance = collect_provenance()
    if provenance['code_dirty'] is not False or not provenance['git_commit']:
        raise ValueError('Commit live pilot preparation before any real call.')
    config = config_from_snapshot(rows[0]['snapshot'])
    requests = [build_turn_request(config, spec_from_row(row), initial_state(row, config)) for row in rows]
    root = Path(__file__).resolve().parents[3]
    authorization = PilotAuthorization(study1_versions(root / 'preregistration/study1.md'))
    directory = Path(directory)
    check_destination(directory, live=True, phase='pilot')
    directory.mkdir(parents=True, exist_ok=True)
    preflight = {'authorization': asdict(authorization), 'provenance': provenance,
                 'planned_natural_episodes': 80, 'planned_probes': 0,
                 'ordinary_call_ceiling': 960, 'total_attempt_cap': 7680,
                 'credential_source': 'ignored .env only; process values excluded',
                 'report_policy': 'Outcomes per pair pooled over all disclosures; no condition comparisons or inference.'}
    path = directory / 'preflight.json'
    if not path.exists():
        path.write_text(json.dumps(preflight, indent=2) + '\n', encoding='utf-8')
    router = create_live_clients(requests, env_path)
    try:
        return await run_manifest(manifest_path, directory, {model: router for model in config.model_order}, authorization=authorization)
    finally:
        await router.aclose()


def main() -> None:
    """Expose only the approved pilot; print safe progress/errors without SDK text."""
    parser = argparse.ArgumentParser(description='Approved 80-episode Study 2 pilot only; 7680 attempts, no probes.')
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--directory', type=Path, required=True)
    parser.add_argument('--env-file', type=Path, default=Path('.env'))
    args = parser.parse_args()
    try:
        summary = asyncio.run(run_live_pilot(args.manifest, args.directory, args.env_file))
        print(json.dumps(summary, indent=2))
        if summary['unfinished_unit_ids']:
            raise SystemExit(1)
    except ModelDriftError:
        print('Pilot stopped on model-version drift; response preserved, no automatic substitution.')
        raise SystemExit(2) from None
    except Exception as error:
        print(json.dumps({'status': 'pilot_stopped', 'error_class': type(error).__name__,
                          'details': 'Inspect safe saved metadata; no settings were changed.'}))
        raise SystemExit(1) from None


if __name__ == '__main__':
    main()
