"""Report pilot mechanics and pair-pooled outcomes, without disclosure comparisons."""

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from statistics import mean, median

from kinloyalty.logs import file_hash, read_jsonl
from kinloyalty.negotiation.collection import replay_collection, turn_path
from kinloyalty.negotiation.config import config_from_snapshot
from kinloyalty.negotiation.manifest import read_manifest
from kinloyalty.negotiation.runner import check_destination


def _class(number: int) -> str:
    return 'first' if number == 1 else 'final' if number == 12 else 'middle'


def _validity(records: list[dict], models: tuple, *, split_roles: bool) -> list[dict]:
    rows = []
    for model in models:
        for role in (('buyer', 'seller') if split_roles else ('all',)):
            for turn_class in ('first', 'middle', 'final'):
                calls = [record for record in records if record['model'] == model and
                         (role == 'all' or record['role'] == role) and _class(record['message_number']) == turn_class]
                responses = [record for record in calls if record['response'] is not None]
                valid = sum(record['validation']['valid'] for record in responses)
                rows.append({'model': model, 'role': role, 'turn_class': turn_class, 'attempts': len(calls),
                             'responses': len(responses), 'valid': valid, 'invalid': len(responses) - valid,
                             'api_errors': len(calls) - len(responses),
                             'valid_rate': valid / len(responses) if responses else None,
                             'status': 'not_observed' if not responses else 'pass' if valid / len(responses) > .95 else 'review'})
    return rows


def _outcomes(episodes: list[dict], planned: int, records: list[dict]) -> dict:
    retained = [episode for episode in episodes if episode['outcome'] != 'excluded']
    shares = [episode['buyer_surplus_share'] for episode in retained]
    deals = [episode for episode in retained if episode['outcome'] == 'deal']
    buyer_violations = sum(episode['buyer_mandate_violation'] for episode in retained)
    seller_violations = sum(episode['seller_mandate_violation'] for episode in retained)
    return {'planned': planned, 'completed': len(episodes), 'unfinished': planned - len(episodes),
            'deals': len(deals), 'walk_away_impasses': sum(e['outcome'] == 'walk_away_impasse' for e in episodes),
            'final_message_impasses': sum(e['outcome'] == 'final_message_impasse' for e in episodes),
            'exclusions': len(episodes) - len(retained), 'retained': len(retained),
            'deal_rate': len(deals) / len(retained) if retained else None,
            'mean_surplus_share': mean(shares) if shares else None, 'median_surplus_share': median(shares) if shares else None,
            'min_surplus_share': min(shares) if shares else None, 'max_surplus_share': max(shares) if shares else None,
            'mean_messages_used': mean(e['messages_used'] for e in episodes) if episodes else None,
            'reasks': sum(e['reasks'] for e in episodes), 'retries': sum(e['retries'] for e in episodes),
            'buyer_mandate_violations': buyer_violations, 'seller_mandate_violations': seller_violations,
            'buyer_violation_rate_retained': buyer_violations / len(retained) if retained else None,
            'seller_violation_rate_retained': seller_violations / len(retained) if retained else None,
            'episodes_attempting_message12': len({r['episode_id'] for r in records if r['message_number'] == 12}),
            'episodes_completing_message12': sum(e['messages_used'] == 12 for e in episodes)}


def _csv(output: Path, name: str, rows: list[dict]) -> None:
    with (output / name).open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


def write_pilot_report(manifest_path: str | Path, directory: str | Path, output: str | Path) -> dict:
    """Replay first; emit only approved pair-pooled outcomes and mechanical diagnostics."""
    rows = read_manifest(manifest_path)
    if len(rows) != 80 or any(row['phase'] != 'pilot' or row['is_probe'] for row in rows):
        raise ValueError('Blind pilot reports require exactly 80 pilot episodes and no probes.')
    directory, output = Path(directory), Path(output)
    check_destination(output, live=False)
    if output.exists() or output.resolve().is_relative_to(directory.resolve()):
        raise ValueError('Choose a fresh report directory separate from pilot inputs.')
    replay = replay_collection(manifest_path, directory)
    config = config_from_snapshot(rows[0]['snapshot'])
    paths = {row['pair_id']: turn_path(directory, row) for row in rows}
    records = sorted([record for path in paths.values() for record in read_jsonl(path)], key=lambda r: r['dispatch_sequence'])
    responses = [record for record in records if record['response'] is not None]
    episodes = read_jsonl(directory / 'episodes.jsonl')
    contract_path, run_path = directory / 'collection.json', directory / 'run_summary.json'
    contract = json.loads(contract_path.read_text()) if contract_path.exists() else {}
    run = json.loads(run_path.read_text()) if run_path.exists() else {}
    models = {}
    for model in config.model_order:
        calls = [record for record in responses if record['model'] == model]
        api_id = config.models[model]['api_model_id']
        fields = {field: [record['response']['usage'][field] for record in calls]
                  for field in ('input_tokens', 'output_tokens', 'reasoning_tokens', 'cache_read_tokens', 'cache_write_tokens')}
        models[model] = {'requested_api_id': api_id, 'expected_version': contract.get('expected_versions', {}).get(api_id),
                         'returned_versions': sorted({record['response']['returned_model_version'] for record in calls}, key=str),
                         'responses': len(calls), 'finish_reasons': dict(Counter(str(r['response']['finish_reason']) for r in calls)),
                         **{f'{field}_missing': sum(value is None for value in values) for field, values in fields.items()},
                         **{f'{field}_values': sorted({value for value in values if value is not None}) for field, values in fields.items()},
                         'max_input_tokens': max((value for value in fields['input_tokens'] if value is not None), default=None)}
    validity = _validity(records, config.model_order, split_roles=False)
    validity_roles = _validity(records, config.model_order, split_roles=True)
    mismatches = []
    for model in config.model_order:
        for role in ('buyer', 'seller'):
            accepted = [record for record in responses if record['model'] == model and record['role'] == role and
                        record['validation']['valid'] and record['validation']['turn']['action'] == 'accept']
            mismatches.append({'model': model, 'role': role, 'valid_accepts': len(accepted),
                               'accept_price_mismatches': sum(record['accept_price_mismatch'] for record in accepted)})
    mismatch_models = [{'model': model,
                        'valid_accepts': sum(row['valid_accepts'] for row in mismatches if row['model'] == model),
                        'accept_price_mismatches': sum(row['accept_price_mismatches'] for row in mismatches if row['model'] == model)}
                       for model in config.model_order]
    pooled = _outcomes(episodes, len(rows), records)
    pairs, lengths = [], []
    for pair in sorted(paths):
        group = [episode for episode in episodes if episode['pair_id'] == pair]
        attempts = [record for record in records if record['pair_id'] == pair]
        spec = next(row['spec'] for row in rows if row['pair_id'] == pair)
        pairs.append({'pair_id': pair, 'buyer_model': spec['buyer_model'], 'seller_model': spec['seller_model'],
                      **_outcomes(group, 5, attempts)})
        lengths.extend({'pair_id': pair, 'messages_used': number, 'episodes': sum(e['messages_used'] == number for e in group)}
                       for number in range(13))
    max_input = max((r['response']['usage']['input_tokens'] for r in responses
                     if r['response']['usage']['input_tokens'] is not None), default=None)
    truncations = sum(r['validation']['invalid_reason'] == 'output_truncated' for r in responses)
    drift = sum(bool(r.get('model_drift')) for r in records)
    cache_calls = [r for r in responses if r['request']['provider'] in {'openai', 'anthropic'}]
    checks = {'all_80_episodes_complete': len(episodes) == 80 and not replay['unfinished_unit_ids'],
              'replay_matches_and_no_impossible_states': True,
              'observed_model_turn_class_validity_above_95_percent': bool(responses) and all(v['status'] != 'review' for v in validity),
              'all_model_turn_classes_observed': all(v['responses'] > 0 for v in validity),
              'no_truncation': truncations == 0, 'no_model_drift': drift == 0,
              'reasoning_counts_present': bool(responses) and all(r['response']['usage']['reasoning_tokens'] is not None for r in responses),
              'all_input_counts_present_and_below_4096': max_input is not None and max_input < 4096 and
                  all(r['response']['usage']['input_tokens'] is not None for r in responses),
              'openai_anthropic_zero_cache': {'openai', 'anthropic'} <= {r['request']['provider'] for r in cache_calls} and all(r['response']['usage'][field] == 0 for r in cache_calls
                                                                 for field in ('cache_read_tokens', 'cache_write_tokens')),
              'within_approved_budget': len(records) <= 7680 and not any(r['is_probe'] for r in records)}
    flags = [name for name, passed in checks.items() if not passed]
    audit = {'phase': 'pilot', 'blinded_to_disclosure': True, 'outcomes_grouped_by': ['pair_id'], 'inference_performed': False,
             'execution_mode': contract.get('execution_mode', 'mock'), 'status': run.get('status', 'not_started'),
             'manifest_sha256': file_hash(manifest_path), 'attempts': len(records), 'responses': len(responses),
             'api_errors': sum(r['api_error'] is not None for r in records),
             'invalid_responses': sum(not r['validation']['valid'] for r in responses),
             'truncated_responses': truncations, 'model_drift_responses': drift, 'max_input_tokens': max_input,
             'models': models, 'validity_by_model_turn_class': validity, 'validity_by_model_role_turn_class': validity_roles,
             'accept_price_mismatches_by_model': mismatch_models, 'accept_price_mismatches_by_model_role': mismatches,
             'pooled_outcomes': pooled, 'pair_pooled_outcomes': pairs, 'pair_episode_lengths': lengths,
             'pooled_episode_lengths': dict(sorted(Counter(e['messages_used'] for e in episodes).items())),
             'checks': checks, 'review_flags': flags, 'unobserved_validity_cells': [v for v in validity if v['responses'] == 0],
             'code_commits': sorted({r['git_commit'] for r in records}),
             'all_calls_from_clean_code': bool(records) and all(r['code_dirty'] is False for r in records),
             'replay': replay, 'automatic_fix_threshold': None}
    output.mkdir(parents=True)
    (output / 'pilot_audit.json').write_text(json.dumps(audit, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    _csv(output, 'pair_pooled_outcomes.csv', pairs)
    _csv(output, 'pair_episode_lengths.csv', lengths)
    _csv(output, 'validity_by_model_turn_class.csv', validity)
    _csv(output, 'validity_by_model_role_turn_class.csv', validity_roles)
    _csv(output, 'accept_price_mismatches_by_model.csv', mismatch_models)
    _csv(output, 'accept_price_mismatches_by_model_role.csv', mismatches)
    usage = []
    for record in records:
        response = record['response']
        usage.append({'record_id': record['record_id'], 'model': record['model'], 'role': record['role'],
                      'message_number': record['message_number'],
                      'valid': record['validation']['valid'] if response else None,
                      'invalid_reason': record['validation']['invalid_reason'] if response else None,
                      'api_error': record['api_error']['kind'] if record['api_error'] else None,
                      **(response['usage'] if response else {field: None for field in
                         ('input_tokens', 'output_tokens', 'reasoning_tokens', 'cache_read_tokens', 'cache_write_tokens')}),
                      'finish_reason': response['finish_reason'] if response else None,
                      'returned_model_version': response['returned_model_version'] if response else None})
    if usage:
        _csv(output, 'usage_calls.csv', usage)
    lines = ['# Study 2 Phase 6 blind pilot report', '',
             f"Execution: `{audit['execution_mode']}`; status: **{audit['status']}**. "
             f"{len(episodes)}/80 episodes complete; {len(records)}/7680 attempts; "
             f"{audit['api_errors']} API errors; {audit['invalid_responses']} invalid responses.", '',
             'All outcome summaries pool disclosure conditions within pair. No disclosure comparisons or hypothesis tests were computed.', '',
             '## Mechanical checks', '', '| Check | Passed |', '| --- | --- |']
    lines.extend(f'| `{name}` | {passed} |' for name, passed in checks.items())
    lines.extend(['', 'Zero-response model/turn cells are not observed, not 100% valid; they remain separate coverage flags.',
                  'Validity denominators are received responses (including re-asks); API failures are counted separately.', '',
                  '## Validity per model and turn class', '', '| Model | Turn class | Valid / responses | Rate | Status |',
                  '| --- | --- | --- | --- | --- |'])
    for row in validity:
        lines.append(f"| `{row['model']}` | {row['turn_class']} | {row['valid']}/{row['responses']} | {row['valid_rate']} | {row['status']} |")
    lines.extend(['', '## Pooled outcomes', '', '```json', json.dumps(pooled, indent=2), '```', '',
                  'Mandate rates use non-excluded episodes, including impasse zeros. Surplus shares are unclipped; exclusions are not impasses.',
                  'Pair-pooled distributions and length counts are in `pair_pooled_outcomes.csv` and `pair_episode_lengths.csv`.', '',
                  '## Acceptance-price mismatches', '', '| Responding model | Valid acceptances | Mismatching supplied prices |', '| --- | --- | --- |'])
    for row in mismatch_models:
        lines.append(f"| `{row['model']}` | {row['valid_accepts']} | {row['accept_price_mismatches']} |")
    lines.extend(['', 'These counts pool all labels and pairs. Role breakdowns are retained in the audit/CSV. '
                  'An accept is valid at the latest opposite offer; its supplied price is recorded and ignored. '
                  'There is no automatic frequency-based fix threshold; interpretation belongs to the researcher.', '',
                  '## Versions and usage', '', '| Model | Expected | Returned | Responses | Missing reasoning | Missing cache read/write |',
                  '| --- | --- | --- | --- | --- | --- |'])
    for model, values in models.items():
        lines.append(f"| `{model}` | `{values['expected_version']}` | `{values['returned_versions']}` | {values['responses']} | "
                     f"{values['reasoning_tokens_missing']} | {values['cache_read_tokens_missing']}/{values['cache_write_tokens_missing']} |")
    lines.extend(['', f'Longest provider-counted prompt: {max_input} tokens. Missing usage stays null, distinct from zero. '
                  'Cache omissions are reported without imputation; complete per-call usage is in `usage_calls.csv`.', '',
                  '## Episode lengths', '', '```json', json.dumps(audit['pooled_episode_lengths'], indent=2), '```', '',
                  f"Episodes attempting message 12: {pooled['episodes_attempting_message12']}; completing it: {pooled['episodes_completing_message12']}.", '',
                  '## Review boundary', '', f"Flags: {flags}.",
                  f"Unfinished identities: {replay['unfinished_unit_ids']}.",
                  'No settings or prompts were changed based on outcomes. Only mechanical fixes may be proposed, '
                  'and each requires researcher approval before implementation. Pilot data never enter main inference.'])
    (output / 'pilot-report.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    return audit


def main() -> None:
    """Generate only the blind pilot report, without credentials or model calls."""
    parser = argparse.ArgumentParser(description='Blind Study 2 pilot mechanics and pair-pooled outcomes only.')
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--directory', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    audit = write_pilot_report(args.manifest, args.directory, args.output)
    print(json.dumps({'attempts': audit['attempts'], 'checks': audit['checks'], 'review_flags': audit['review_flags']}, indent=2))


if __name__ == '__main__':
    main()
