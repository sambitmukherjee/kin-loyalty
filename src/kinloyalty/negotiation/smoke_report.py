"""Report smoke mechanics and exact probe transcripts without hypothesis analyses."""

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

from kinloyalty.logs import file_hash, read_jsonl
from kinloyalty.negotiation.collection import replay_collection, turn_path
from kinloyalty.negotiation.manifest import read_manifest, spec_from_row
from kinloyalty.negotiation.probes import write_probe_report
from kinloyalty.negotiation.config import config_from_snapshot


def write_smoke_report(manifest_path: str | Path, directory: str | Path, output: str | Path) -> dict:
    """Write fresh audit/usage/report files from smoke logs, including partial halted runs."""
    rows = read_manifest(manifest_path)
    if any(row['phase'] != 'smoke' for row in rows):
        raise ValueError('Smoke reports accept smoke data only.')
    directory, output = Path(directory), Path(output)
    if output.exists():
        raise ValueError('Choose a fresh smoke-report output directory.')
    replay = replay_collection(manifest_path, directory)
    output.mkdir(parents=True)
    paths = {row['pair_id']: turn_path(directory, row) for row in rows}
    records = sorted([record for path in paths.values() for record in read_jsonl(path)], key=lambda r: r['dispatch_sequence'])
    responses = [record for record in records if record['response'] is not None]
    contract = json.loads((directory / 'collection.json').read_text()) if (directory / 'collection.json').exists() else {}
    expected = contract.get('expected_versions', {})
    run = json.loads((directory / 'run_summary.json').read_text()) if (directory / 'run_summary.json').exists() else {}
    by_model = defaultdict(list)
    for record in responses:
        by_model[record['model']].append(record)
    models = {}
    config = config_from_snapshot(rows[0]['snapshot'])
    for model in config.model_order:
        calls = by_model[model]
        versions = sorted({str(record['response']['returned_model_version']) for record in calls})
        api_id = config.models[model]['api_model_id']
        def present(field):
            return [record['response']['usage'][field] for record in calls]
        models[model] = {
            'requested_api_id': api_id, 'expected_version': expected.get(api_id), 'returned_versions': versions,
            'responses': len(calls), 'valid_responses': sum(record['validation']['valid'] for record in calls),
            'reasoning_missing': sum(value is None for value in present('reasoning_tokens')),
            'reasoning_values': sorted({value for value in present('reasoning_tokens') if value is not None}),
            'cache_read_missing': sum(value is None for value in present('cache_read_tokens')),
            'cache_write_missing': sum(value is None for value in present('cache_write_tokens')),
            'cache_read_values': sorted({value for value in present('cache_read_tokens') if value is not None}),
            'cache_write_values': sorted({value for value in present('cache_write_tokens') if value is not None}),
            'max_input_tokens': max((value for value in present('input_tokens') if value is not None), default=None),
            'stop_reasons': dict(Counter(str(record['response']['finish_reason']) for record in calls)),
        }
    probes = []
    for row in rows:
        if not row['is_probe']:
            continue
        identity = spec_from_row(row).episode_id
        attempts = [record for record in records if record['episode_id'] == identity]
        received = [record for record in attempts if record['response'] is not None]
        probes.append({'episode_id': identity, 'model': row['spec']['buyer_model'], 'role': row['probe_role'],
                       'message_number': row['probe_position'], 'attempts': len(attempts),
                       'provider_accepted_schema': bool(received),
                       'valid_final_reply': bool(attempts and attempts[-1]['is_final_for_turn'] and not attempts[-1]['excluded']),
                       'observed_actions': [record['validation']['parsed_json'].get('action') for record in received
                                            if record['validation']['parsed_json'] is not None]})
    truncated = [record for record in responses if record['validation']['invalid_reason'] == 'output_truncated']
    drifts = [record for record in records if record.get('model_drift')]
    max_input = max((record['response']['usage']['input_tokens'] for record in responses
                     if record['response']['usage']['input_tokens'] is not None), default=None)
    audit = {'phase': 'smoke', 'execution_mode': contract.get('execution_mode', 'mock'),
             'manifest_sha256': file_hash(manifest_path), 'attempts': len(records),
             'natural_attempts': sum(not record['is_probe'] for record in records),
             'probe_attempts': sum(record['is_probe'] for record in records),
             'api_errors': sum(record['api_error'] is not None for record in records),
             'invalid_responses': sum(not record['validation']['valid'] for record in responses),
             'truncated_responses': len(truncated), 'model_drift_responses': len(drifts),
             'max_input_tokens': max_input, 'models': models, 'probes': probes, 'replay': replay,
             'code_commits': sorted({record['git_commit'] for record in records}),
             'all_calls_from_clean_code': bool(records) and all(record['code_dirty'] is False for record in records),
             'status': run.get('status', 'not_started'),
             'checks': {
                 'all_units_complete': not replay['unfinished_unit_ids'],
                 'all_probe_schemas_accepted': all(probe['provider_accepted_schema'] for probe in probes),
                 'all_probes_valid': all(probe['valid_final_reply'] for probe in probes),
                 'message12_actions_only_accept_or_walk': all(probe['valid_final_reply'] and probe['observed_actions'] and
                    all(isinstance(action, str) and action in {'accept', 'walk_away'} for action in probe['observed_actions'])
                    for probe in probes if probe['message_number'] == 12),
                 'all_responses_valid': bool(responses) and all(record['validation']['valid'] for record in responses),
                 'no_model_drift': not drifts, 'no_truncation': not truncated,
                 'reasoning_counts_present': bool(responses) and all(record['response']['usage']['reasoning_tokens'] is not None for record in responses),
                 'inputs_below_4096': max_input is not None and max_input < 4096,
                 'openai_anthropic_zero_cache': {'openai', 'anthropic'} <= {r['request']['provider'] for r in responses} and all(
                     record['response']['usage']['cache_read_tokens'] == 0 and record['response']['usage']['cache_write_tokens'] == 0
                     for record in responses if record['request']['provider'] in {'openai', 'anthropic'}),
                 'within_approved_budgets': sum(not r['is_probe'] for r in records) <= 384 and sum(r['is_probe'] for r in records) <= 32,
             }}
    (output / 'smoke_audit.json').write_text(json.dumps(audit, indent=2) + '\n', encoding='utf-8')
    fields = ['record_id', 'model', 'role', 'message_number', 'is_probe', 'valid', 'invalid_reason',
              'input_tokens', 'output_tokens', 'reasoning_tokens', 'cache_read_tokens', 'cache_write_tokens', 'finish_reason', 'returned_model_version']
    with (output / 'usage_calls.csv').open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for record in responses:
            writer.writerow({**{key: record[key] for key in fields[:5]}, 'valid': record['validation']['valid'],
                             'invalid_reason': record['validation']['invalid_reason'], **record['response']['usage'],
                             'finish_reason': record['response']['finish_reason'],
                             'returned_model_version': record['response']['returned_model_version']})
    write_probe_report(manifest_path, directory, output / 'probe-report.json')
    lines = ['# Study 2 Phase 4 smoke report', '', f"Status: **{audit['status']}**. Execution: `{audit['execution_mode']}`.", '',
             f"Four natural episodes and sixteen probes were planned. Recorded {audit['natural_attempts']} natural and "
             f"{audit['probe_attempts']} probe attempts; {audit['api_errors']} API errors; {audit['invalid_responses']} invalid responses.",
             f"Replay verified {replay['episodes_verified']} natural episode and {replay['probes_verified']} probe summaries; "
             f"{len(replay['unfinished_unit_ids'])} units remain unfinished.", '',
             'Only mechanical smoke diagnostics are reported. Probes are unscored and ineligible for inference.', '',
             '## Returned model versions', '', '| Model | Expected | Observed | Responses |', '| --- | --- | --- | --- |']
    for model, values in models.items():
        lines.append(f"| `{model}` | `{values['expected_version']}` | `{', '.join(values['returned_versions'])}` | {values['responses']} |")
    lines.extend(['', '## Checks', '', '| Check | Passed |', '| --- | --- |'])
    for name, value in audit['checks'].items():
        lines.append(f'| `{name}` | {value} |')
    lines.extend(['', f"Longest provider-reported input: {max_input} tokens. Missing usage fields remain null, distinct from zero.",
                  'Per-model usage/cache/stop metadata is in `smoke_audit.json`; per-call values are in `usage_calls.csv`.', '',
                  '## Forced-position schema coverage', '', '| Model | Role | Message | Attempts | Schema accepted | Final reply valid |',
                  '| --- | --- | --- | --- | --- | --- |'])
    for probe in probes:
        lines.append(f"| `{probe['model']}` | {probe['role']} | {probe['message_number']} | {probe['attempts']} | {probe['provider_accepted_schema']} | {probe['valid_final_reply']} |")
    lines.extend(['', '## Exact hand-written probe transcripts', '',
                  'The four prefixes below are shared across models. Buyer probes use the not-disclosed seller card; seller probes see no card.',
                  'Full system/user requests for all sixteen probes are preserved in `probe-report.json` and the manifest.'])
    seen = set()
    for row in rows:
        key = (row['probe_role'], row['probe_position'])
        if row['is_probe'] and key not in seen:
            seen.add(key)
            lines.extend(['', f'### {key[0]}, message {key[1]}', '', '```text', row['probe_request']['user_message'], '```'])
    (output / 'smoke-report.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    return audit


def main() -> None:
    """Produce an offline mechanical report from a stopped smoke collection."""
    parser = argparse.ArgumentParser(description='Study 2 smoke mechanics only; no hypothesis analysis or API calls.')
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--directory', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    audit = write_smoke_report(args.manifest, args.directory, args.output)
    print(json.dumps({'status': audit['status'], 'attempts': audit['attempts'], 'checks': audit['checks']}, indent=2))


if __name__ == '__main__':
    main()
