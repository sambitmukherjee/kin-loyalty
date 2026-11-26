"""Report unscored forced-position probe mechanics with the exact transcript requests."""

import json
from pathlib import Path

from kinloyalty.logs import read_jsonl
from kinloyalty.negotiation.collection import replay_collection, turn_path
from kinloyalty.negotiation.manifest import read_manifest, spec_from_row


def write_probe_report(manifest_path: str | Path, directory: str | Path, output: str | Path) -> None:
    """Write a fresh mechanical probe report; never compute negotiation label effects."""
    replay = replay_collection(manifest_path, directory)
    directory = Path(directory)
    rows = read_manifest(manifest_path)
    terminals = {row['episode_id']: row for row in read_jsonl(directory / 'probes.jsonl')}
    probes = []
    for row in rows:
        if not row['is_probe']:
            continue
        identity = spec_from_row(row).episode_id
        attempts = [record for record in read_jsonl(turn_path(directory, row)) if record['episode_id'] == identity]
        probes.append({'episode_id': identity, 'phase': 'smoke', 'is_probe': True,
                       'model': spec_from_row(row).buyer_model, 'role': row['probe_role'],
                       'message_number': row['probe_position'], 'terminal': terminals.get(identity),
                       'attempt_count': len(attempts), 'initial_turns': row['initial_turns'],
                       'system_prompt': row['probe_request']['system_prompt'],
                       'user_message': row['probe_request']['user_message'],
                       'allowed_actions': row['probe_request']['json_schema']['properties']['action']['enum']})
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('x', encoding='utf-8') as stream:
        json.dump({'synthetic': True, 'inference_eligible': False, 'replay': replay, 'probes': probes}, stream, indent=2)
        stream.write('\n')
