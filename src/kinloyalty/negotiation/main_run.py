"""Launch/resume the authorized frozen main plan, without changing scientific rules."""

import argparse
import asyncio
import json
from pathlib import Path
import subprocess

from kinloyalty.logs import file_hash
from kinloyalty.negotiation.authorization import (
    MAIN_MANIFEST_SHA256, REGISTRATION_COMMIT, MainAuthorization, ModelDriftError,
)
from kinloyalty.negotiation.config import config_from_snapshot
from kinloyalty.negotiation.manifest import initial_state, read_manifest, spec_from_row
from kinloyalty.negotiation.requests import build_turn_request
from kinloyalty.negotiation.runner import run_manifest
from kinloyalty.negotiation.smoke import create_live_clients
from kinloyalty.provenance import collect_provenance


# The explicitly approved deviation changes execution authorization/provenance
# only. All other registered bytes must remain the registration snapshot.
APPROVED_CHANGED_PATHS = {
    'src/kinloyalty/negotiation/authorization.py', 'src/kinloyalty/negotiation/runner.py',
    'src/kinloyalty/negotiation/history.py', 'src/kinloyalty/negotiation/collection.py',
    'tests/test_study2_registration.py', 'tests/test_study2_analysis.py', 'docs/decisions.md',
}


def verify_main_sources(manifest: str | Path, execution_commit: str) -> tuple[dict, dict]:
    """Verify manifest/addendum/tag and all unchanged registered files before keys/calls."""
    root = Path(__file__).resolve().parents[3]
    provenance = collect_provenance()
    if provenance['git_commit'] != execution_commit or provenance['code_dirty'] is not False:
        raise ValueError('Main collection/resumption requires the same clean committed execution revision.')
    tag = subprocess.check_output(['git', 'rev-parse', 'prereg-study2^{}'], cwd=root, text=True).strip()
    if tag != REGISTRATION_COMMIT:
        raise ValueError('The original registration tag has moved.')
    lock = json.loads((root / 'preregistration/study2-lock.json').read_text())
    registered_lock = subprocess.check_output(['git', 'show', 'prereg-study2:preregistration/study2-lock.json'], cwd=root)
    if registered_lock != (root / 'preregistration/study2-lock.json').read_bytes():
        raise ValueError('The registration snapshot was modified.')
    for relative, digest in lock['hashes_sha256'].items():
        if relative not in APPROVED_CHANGED_PATHS and file_hash(root / relative) != digest:
            raise ValueError(f'Unapproved registered-file change: {relative}.')
    actual = file_hash(manifest)
    addendum = (root / 'preregistration/study2.md').read_text()
    if actual != MAIN_MANIFEST_SHA256 or actual != lock['main_manifest_sha256'] or actual not in addendum:
        raise ValueError('Main manifest SHA-256 differs from the locked addendum; no call made.')
    return lock, provenance


async def run_live_main(manifest: str | Path, directory: str | Path, env_path: str | Path,
                        execution_commit: str) -> dict:
    """Run every unfinished episode, retaining registered retries and stopping on drift."""
    lock, provenance = verify_main_sources(manifest, execution_commit)
    rows = read_manifest(manifest)
    if len(rows) != 960 or any(row['phase'] != 'main' or row['is_probe'] for row in rows):
        raise ValueError('Only the registered 960 natural main episodes are authorized.')
    root = Path(__file__).resolve().parents[3]
    directory = Path(directory)
    if directory.resolve().is_relative_to(root):
        raise ValueError('Collect externally to keep the execution checkout clean throughout the run.')
    config = config_from_snapshot(rows[0]['snapshot'])
    versions = {config.models[key]['api_model_id']: values[0] for key, values in lock['pilot_returned_versions'].items()}
    authorization = MainAuthorization(versions, execution_commit)
    requests = [build_turn_request(config, spec_from_row(row), initial_state(row, config)) for row in rows]
    directory.mkdir(parents=True, exist_ok=True)
    preflight = {'registration_git_commit': REGISTRATION_COMMIT, 'execution_git_commit': execution_commit,
                 'manifest_sha256': MAIN_MANIFEST_SHA256, 'provenance': provenance,
                 'authorization': authorization.contract(MAIN_MANIFEST_SHA256),
                 'ordinary_turn_call_ceiling': 11520,
                 'api_attempts_per_response_opportunity': 4, 'identical_invalid_reasks': 1,
                 'aggregate_attempt_cap': None,
                 'resume_policy': 'Researcher requested resumption until all 960 terminate; stop on model drift/nonretryable error.',
                 'report_policy': 'Collection mechanics only; no outcome statistics or inference.'}
    path = directory / 'preflight.json'
    if path.exists() and json.loads(path.read_text()) != preflight:
        raise ValueError('Resume preflight differs from its original execution contract.')
    if not path.exists():
        path.write_text(json.dumps(preflight, indent=2) + '\n')
    router = create_live_clients(requests, env_path)
    try:
        while True:
            verify_main_sources(manifest, execution_commit)
            summary = await run_manifest(manifest, directory, {model: router for model in config.model_order}, authorization=authorization)
            print(json.dumps({'status': summary['status'], 'episodes_complete': summary['episodes_complete'],
                              'attempts': summary['natural_attempts_used'], 'unfinished': len(summary['unfinished_unit_ids']),
                              'registration_git_commit': REGISTRATION_COMMIT,
                              'execution_git_commit': execution_commit}), flush=True)
            if not summary['unfinished_unit_ids']:
                return summary
            await asyncio.sleep(1)
    finally:
        await router.aclose()


def main() -> None:
    """Expose the approved main launcher without printing SDK errors or outcomes."""
    parser = argparse.ArgumentParser(description='Authorized frozen Study 2 main collection; no analysis.')
    parser.add_argument('--manifest', type=Path, default=Path('data/study2/main/manifest.jsonl'))
    parser.add_argument('--directory', type=Path, required=True)
    parser.add_argument('--env-file', type=Path, default=Path('.env'))
    parser.add_argument('--execution-commit', required=True)
    args = parser.parse_args()
    try:
        asyncio.run(run_live_main(args.manifest, args.directory, args.env_file, args.execution_commit))
    except ModelDriftError:
        print(json.dumps({'status': 'paused_model_drift', 'details': 'Response preserved; researcher review required before continuing.'}))
        raise SystemExit(2) from None
    except Exception as error:
        print(json.dumps({'status': 'main_stopped', 'error_class': type(error).__name__,
                          'details': 'Inspect safe persisted metadata; no automatic settings change.'}))
        raise SystemExit(1) from None


if __name__ == '__main__':
    main()
