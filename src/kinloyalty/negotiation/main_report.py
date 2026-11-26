"""Report main collection mechanics only, with an explicit non-outcome field whitelist."""

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path

from kinloyalty.logs import file_hash, read_jsonl
from kinloyalty.negotiation.authorization import MAIN_MANIFEST_SHA256, REGISTRATION_COMMIT
from kinloyalty.negotiation.collection import load_histories, replay_collection, turn_path
from kinloyalty.negotiation.manifest import read_manifest


def write_main_report(manifest: str | Path, directory: str | Path, output: str | Path) -> dict:
    """Replay and report completion/exclusion/re-ask/error/resumption counts, never outcomes."""
    rows = read_manifest(manifest)
    if len(rows) != 960 or any(row['phase'] != 'main' or row['is_probe'] for row in rows) or file_hash(manifest) != MAIN_MANIFEST_SHA256:
        raise ValueError('Collection report requires the exact registered main manifest.')
    directory, output = Path(directory), Path(output)
    if output.exists() or output.resolve().is_relative_to(directory.resolve()):
        raise ValueError('Choose a fresh report directory separate from source logs.')
    replay = replay_collection(manifest, directory)
    contract = json.loads((directory / 'collection.json').read_text())
    paths = {row['pair_id']: turn_path(directory, row) for row in rows}
    histories, progress = load_histories(rows, {pair: read_jsonl(path) for pair, path in paths.items()},
                                          MAIN_MANIFEST_SHA256, execution_mode='live')
    episodes = read_jsonl(directory / 'episodes.jsonl')
    terminal_ids = {record['episode_id'] for record in episodes}
    all_attempts = [record for history in histories.values() for record in history]
    for record in [*all_attempts, *episodes]:
        if (record.get('registration_git_commit') != REGISTRATION_COMMIT or
                record.get('execution_git_commit') != contract['execution_git_commit'] or
                record.get('git_commit') != contract['execution_git_commit']):
            raise ValueError('Every turn and episode record must contain both truthful code hashes.')
    groups = defaultdict(list)
    for row in rows:
        groups[(row['pair_id'], row['spec']['condition'])].append(row['spec']['episode_id'])
    cells = []
    for (pair, condition), identities in sorted(groups.items()):
        attempts = [record for identity in identities for record in histories[identity]]
        resumed = [max(len({record['run_id'] for record in histories[identity]}) - 1, 0) for identity in identities]
        cells.append({'pair_id': pair, 'condition': condition, 'planned': len(identities),
                      'completed': sum(identity in terminal_ids for identity in identities),
                      'exclusions': sum(any(record['excluded'] for record in histories[identity]) for identity in identities),
                      'reasks': sum(progress[identity].reasks for identity in identities),
                      'api_errors': sum(record['api_error'] is not None for record in attempts),
                      'api_retries': sum(progress[identity].retries for identity in identities),
                      'resumptions': sum(resumed), 'resumed_episodes': sum(value > 0 for value in resumed),
                      'attempts': len(attempts), 'unfinished': sum(identity not in terminal_ids for identity in identities)})
    sizes = {str(path.relative_to(directory)): path.stat().st_size for path in paths.values() if path.exists()}
    if (directory / 'episodes.jsonl').exists():
        sizes['episodes.jsonl'] = (directory / 'episodes.jsonl').stat().st_size
    largest = max(sizes, key=sizes.get, default=None)
    report = {'study': 'study2', 'phase': 'main', 'report_scope': 'collection_mechanics_only',
              'registration_git_commit': REGISTRATION_COMMIT, 'execution_git_commit': contract['execution_git_commit'],
              'manifest_sha256': MAIN_MANIFEST_SHA256, 'planned': 960, 'completed': len(episodes),
              **{field: sum(row[field] for row in cells) for field in ('exclusions', 'reasks', 'api_errors', 'api_retries', 'resumptions', 'resumed_episodes', 'attempts', 'unfinished')},
              'collection_invocations_with_attempts': len({record['run_id'] for record in all_attempts}),
              'unfinished_episode_ids': replay['unfinished_unit_ids'], 'per_pair_condition': cells,
              'both_hashes_on_every_turn_and_episode': True, 'replay': replay,
              'model_drift_responses': sum(bool(record.get('model_drift')) for record in all_attempts),
              'api_error_kinds': dict(Counter(record['api_error']['kind'] for record in all_attempts if record['api_error'])),
              'largest_log_file': largest, 'largest_log_bytes': sizes.get(largest, 0),
              'inference_run': False, 'outcome_statistics_reported': False}
    output.mkdir(parents=True)
    (output / 'collection-report.json').write_text(json.dumps(report, indent=2) + '\n')
    lines = ['# Study 2 main collection report', '',
             'Scope: collection mechanics only. No outcome statistics or analysis.', '',
             f"Completed **{report['completed']}/960** episodes in **{report['attempts']}** API attempts.",
             f"Exclusions: {report['exclusions']}; re-asks: {report['reasks']}; API errors: {report['api_errors']}; API retries: {report['api_retries']}.",
             f"Episode resumptions: {report['resumptions']} across {report['resumed_episodes']} episodes; collection invocations with attempts: {report['collection_invocations_with_attempts']}.", '',
             f"Registration commit: `{REGISTRATION_COMMIT}`.", f"Actual execution commit: `{contract['execution_git_commit']}`.",
             'Both hashes are present and checked on every turn and episode record; git_commit denotes the actual execution revision.',
             f"Manifest SHA-256: `{MAIN_MANIFEST_SHA256}`.",
             f"Replay verified {replay['attempts_verified']} attempts and {replay['episodes_verified']} terminal summaries exactly.",
             f"Largest log: `{largest}`, {report['largest_log_bytes']} bytes.", '',
             '| Pair | Condition | Complete/planned | Exclusions | Re-asks | API errors | Resumptions | Unfinished |',
             '| --- | --- | --- | --- | --- | --- | --- | --- |']
    for row in cells:
        lines.append(f"| `{row['pair_id']}` | `{row['condition']}` | {row['completed']}/{row['planned']} | {row['exclusions']} | {row['reasks']} | {row['api_errors']} | {row['resumptions']} | {row['unfinished']} |")
    lines.extend(['', 'Resumptions count additional invocations that actually attempted an already-started episode, derived from distinct run_id values; API retries within one invocation are separate.',
                  f"API error/recovery kinds: {report['api_error_kinds']}. Interrupted reservations represent unknown responses, not inferred negotiating choices.",
                  f"Unfinished episode IDs: {replay['unfinished_unit_ids']}.",
                  f"Model-version drift responses: {report['model_drift_responses']}.",
                  'The replay recomputes terminal records internally for validation; their substantive values are not reported here.'])
    (output / 'collection-report.md').write_text('\n'.join(lines) + '\n')
    return report


def main() -> None:
    """Write only mechanical completion reports, without credentials or API calls."""
    parser = argparse.ArgumentParser(description='Study 2 main collection status only; no outcome analysis.')
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--directory', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    report = write_main_report(args.manifest, args.directory, args.output)
    print(json.dumps({key: report[key] for key in ('completed', 'planned', 'attempts', 'exclusions', 'reasks', 'api_errors', 'resumptions', 'unfinished')}))


if __name__ == '__main__':
    main()
