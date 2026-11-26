"""Verify the Study 2 registration and main plan offline, without collecting data."""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess

from kinloyalty.clients.payloads import frozen_api_payload
from kinloyalty.logs import content_hash, file_hash, json_line
from kinloyalty.negotiation.config import config_from_snapshot
from kinloyalty.negotiation.manifest import build_manifest, initial_state, read_manifest, spec_from_row
from kinloyalty.negotiation.requests import build_turn_request
from kinloyalty.negotiation.rules import apply_turn, next_role
from kinloyalty.negotiation.transcript import TranscriptTurn


def verify_hashes(hashes: dict[str, str], root: Path) -> None:
    """Check exact bytes while restricting inventory paths to the checkout."""
    for relative, digest in hashes.items():
        path = (root / relative).resolve()
        if Path(relative).is_absolute() or not path.is_relative_to(root.resolve()):
            raise ValueError('Registration inventory path must stay inside the checkout.')
        if file_hash(path) != digest:
            raise ValueError(f'Registration digest mismatch: {relative}.')


def verify_request_shapes(rows: list[dict]) -> int:
    """Check all planned turn positions using temporary offers, never API replies.

    These prefixes are shape fixtures, not observed negotiations or data. No
    outcome is generated, and no fixture is saved under the main data directory.
    """
    config = config_from_snapshot(rows[0]['snapshot'])
    count = 0
    def check_sampling(value):
        if isinstance(value, dict):
            if {'temperature', 'top_p', 'top_k'} & value.keys():
                raise ValueError('Registered payload overrides provider-default sampling.')
            for child in value.values():
                check_sampling(child)
        elif isinstance(value, list):
            for child in value:
                check_sampling(child)
    for row in rows:
        spec = spec_from_row(row)
        state = initial_state(row, config)
        for number in range(1, config.message_limit + 1):
            request = build_turn_request(config, spec, state)
            payload = frozen_api_payload(request, request.provider)
            check_sampling(payload)
            if request.context['message_number'] != number or request.settings['reasoning_effort'] != 'low' or request.settings['max_output_tokens'] != 8192:
                raise ValueError('Registered turn position or API settings differ.')
            count += 1
            if number < config.message_limit:
                state = apply_turn(state, TranscriptTurn(next_role(state), 'Offline shape fixture; not observed data.',
                                                         'offer', spec.scenario.reference_price))
    return count


def verify_registration(path: str | Path = 'preregistration/study2-lock.json', *,
                        require_unrun: bool = False, check_tag: bool = False) -> dict:
    """Validate locked sources, deterministic manifest, payloads, and optional local tag."""
    root = Path(__file__).resolve().parents[3]
    path = Path(path).resolve()
    lock = json.loads(path.read_text(encoding='utf-8'))
    if lock['schema_version'] != 1 or lock['study'] != 'study2' or lock['git_tag'] != 'prereg-study2':
        raise ValueError('Expected the Study 2 registration snapshot.')
    verify_hashes(lock['hashes_sha256'], root)
    manifest = root / lock['main_manifest']
    rows = read_manifest(manifest)
    if len(rows) != 960 or any(row['phase'] != 'main' or row['is_probe'] for row in rows):
        raise ValueError('Registered main plan must have exactly 960 natural main episodes.')
    rebuilt = ''.join(map(json_line, build_manifest(root / 'configs/study2.yaml', 'main', allow_main=True))).encode()
    if rebuilt != manifest.read_bytes() or hashlib.sha256(rebuilt).hexdigest() != lock['main_manifest_sha256']:
        raise ValueError('Main manifest does not regenerate byte-identically.')
    config = config_from_snapshot(rows[0]['snapshot'])
    if (config.study['seeds'] != lock['seeds'] or content_hash(config.schemas) != content_hash(lock['canonical_schemas'])
            or config.study['analysis'] != lock['analysis_settings']):
        raise ValueError('Registered seeds, schemas, or analysis settings differ from the frozen manifest.')
    if require_unrun and any(entry.name != 'manifest.jsonl' for entry in manifest.parent.iterdir()):
        raise ValueError('Phase 8 requires a main directory containing only its manifest.')
    positions = verify_request_shapes(rows)
    tag_target = None
    if check_tag:
        tag = lock['git_tag']
        def git(*args):
            return subprocess.check_output(['git', *args], cwd=root, stderr=subprocess.DEVNULL)
        if git('cat-file', '-t', f'refs/tags/{tag}').strip() != b'tag':
            raise ValueError('The registration requires an annotated local tag.')
        tag_target = git('rev-parse', f'{tag}^{{}}').decode().strip()
        for relative, digest in {**lock['hashes_sha256'], str(path.relative_to(root)): file_hash(path)}.items():
            if hashlib.sha256(git('show', f'{tag}:{relative}')).hexdigest() != digest:
                raise ValueError(f'Local tag does not contain the registered bytes: {relative}.')
    return {'study': 'study2', 'registered_files_verified': len(lock['hashes_sha256']),
            'main_manifest_sha256': lock['main_manifest_sha256'], 'episodes': len(rows),
            'scenarios': len({row['spec']['scenario']['scenario_id'] for row in rows}),
            'pairs': len({row['pair_id'] for row in rows}), 'request_positions_validated': positions,
            'main_directory_unrun_required': require_unrun, 'annotated_tag_target': tag_target,
            'api_calls_made': 0}


def main() -> None:
    """Expose a credential-free lock check, with no analysis or collection command."""
    parser = argparse.ArgumentParser(description='Verify Study 2 registration offline; never run collection or inference.')
    parser.add_argument('--lock', type=Path, default=Path('preregistration/study2-lock.json'))
    parser.add_argument('--require-unrun', action='store_true')
    parser.add_argument('--tag', action='store_true')
    args = parser.parse_args()
    print(json.dumps(verify_registration(args.lock, require_unrun=args.require_unrun, check_tag=args.tag), indent=2))


if __name__ == '__main__':
    main()
