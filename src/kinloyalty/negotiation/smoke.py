"""Execute the approved live smoke plan using existing clients and .env-only keys."""

import argparse
import asyncio
import json
import subprocess
from dataclasses import asdict
from pathlib import Path

from kinloyalty.clients.base import ModelRequest
from kinloyalty.clients.factory import ProviderClients, load_api_keys
from kinloyalty.clients.payloads import frozen_api_payload
from kinloyalty.negotiation.authorization import ModelDriftError, SmokeAuthorization, study1_versions
from kinloyalty.negotiation.config import config_from_snapshot
from kinloyalty.negotiation.manifest import initial_state, read_manifest, spec_from_row
from kinloyalty.negotiation.requests import build_turn_request
from kinloyalty.negotiation.runner import check_destination, run_manifest
from kinloyalty.provenance import collect_provenance


def create_live_clients(requests: list[ModelRequest], env_path: str | Path) -> ProviderClients:
    """Read ignored .env only, constructing the unchanged adapters without API calls."""
    from kinloyalty.clients.anthropic import AnthropicClient
    from kinloyalty.clients.google import GoogleClient
    from kinloyalty.clients.moonshot import MoonshotClient
    from kinloyalty.clients.openai import OpenAIClient

    env_path = Path(env_path).resolve()
    root = Path(__file__).resolve().parents[3]
    ignored = subprocess.run(['git', 'check-ignore', '--quiet', str(env_path)], cwd=root, capture_output=True)
    if env_path != root / '.env' or ignored.returncode != 0:
        raise ValueError('Real keys must come only from this checkout\'s ignored .env file.')
    for request in requests:
        frozen_api_payload(request, request.provider)
    providers = list(dict.fromkeys(request.provider for request in requests))
    keys = load_api_keys(providers, env_path, environ={})
    constructors = {'anthropic': AnthropicClient, 'openai': OpenAIClient,
                    'google': GoogleClient, 'moonshot': MoonshotClient}
    class ObservedClients(ProviderClients):
        async def complete(self, request):
            response = await super().complete(request)
            print(json.dumps({'model': request.api_model_id, 'message_number': request.context['message_number'],
                              'role': request.context['role'], 'returned_model': response.returned_model_version}), flush=True)
            return response
    return ObservedClients({provider: constructors[provider](api_key=keys[provider]) for provider in providers})


async def run_live_smoke(manifest_path: str | Path, directory: str | Path, env_path: str | Path) -> dict:
    """Run only the approved smoke phase, close SDKs, and retain budget/drift evidence."""
    rows = read_manifest(manifest_path)
    if any(row['phase'] != 'smoke' for row in rows):
        raise ValueError('Live entry point accepts only the approved smoke manifest.')
    provenance = collect_provenance()
    if provenance['code_dirty'] is not False:
        raise ValueError('Commit live smoke code before making any real provider call.')
    config = config_from_snapshot(rows[0]['snapshot'])
    requests = [build_turn_request(config, spec_from_row(row), initial_state(row, config)) for row in rows]
    root = Path(__file__).resolve().parents[3]
    authorization = SmokeAuthorization(study1_versions(root / 'preregistration/study1.md'))
    directory = Path(directory)
    check_destination(directory, live=True)
    directory.mkdir(parents=True, exist_ok=True)
    preflight = {'authorization': asdict(authorization), 'provenance': provenance,
                 'planned_natural_episodes': 4, 'planned_probes': 16,
                 'ordinary_call_ceiling': 64, 'total_attempt_cap': 416,
                 'credential_source': 'ignored .env only; process values excluded',
                 'scientific_config_approval_note': 'Phase 1 administrative flag is superseded by this dated researcher authorization.'}
    path = directory / 'preflight.json'
    if not path.exists():
        path.write_text(json.dumps(preflight, indent=2) + '\n', encoding='utf-8')
    router = create_live_clients(requests, env_path)
    clients = {model: router for model in config.model_order}
    try:
        return await run_manifest(manifest_path, directory, clients, authorization=authorization)
    finally:
        await router.aclose()


def main() -> None:
    """Expose the explicitly authorized live smoke entry point, with safe diagnostics."""
    parser = argparse.ArgumentParser(description='Approved Study 2 smoke only: 384 natural + 32 probe attempts maximum.')
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--directory', type=Path, required=True)
    parser.add_argument('--env-file', type=Path, default=Path('.env'))
    args = parser.parse_args()
    try:
        summary = asyncio.run(run_live_smoke(args.manifest, args.directory, args.env_file))
        print(json.dumps(summary, indent=2))
        if summary['unfinished_unit_ids']:
            raise SystemExit(1)
    except ModelDriftError:
        print('Smoke stopped on model-version drift; inspect the saved response and run summary.')
        raise SystemExit(2) from None
    except Exception as error:
        # Never print arbitrary SDK exception text or request/header representations.
        print(json.dumps({'status': 'smoke_stopped', 'error_class': type(error).__name__,
                          'details': 'Inspect safe persisted attempt metadata; no automatic substitution made.'}))
        raise SystemExit(1) from None


if __name__ == '__main__':
    main()
