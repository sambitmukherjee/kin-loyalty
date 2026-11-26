"""Reproduce Study 2 alone: validate replay, compute tables, and draw all figures."""

import hashlib
import importlib.metadata
import json
from pathlib import Path

import numpy as np
import pandas as pd

from kinloyalty.analysis.study2.core import analyze_core
from kinloyalty.analysis.study2.loading import check_input_paths, load_data
from kinloyalty.analysis.study2.reports import bootstrap_group_means, diagnostic_tables
from kinloyalty.logs import file_hash
from kinloyalty.negotiation.runner import check_destination
from kinloyalty.provenance import collect_provenance


def _input_hashes(manifest: Path, directory: Path) -> dict[str, str]:
    files = {'manifest.jsonl': manifest, 'episodes.jsonl': directory / 'episodes.jsonl'}
    for name in ('probes.jsonl', 'collection.json'):
        path = directory / name
        if path.exists():
            files[name] = path
    files.update({f'turns/{path.name}': path for path in sorted((directory / 'turns').glob('*.jsonl'))})
    return {name: file_hash(path) for name, path in files.items()}


def _code_hashes() -> dict[str, str]:
    root = Path(__file__).resolve().parents[4]
    files = [*sorted((root / 'src/kinloyalty/analysis/study2').glob('*.py')),
             *sorted((root / 'src/kinloyalty/negotiation').glob('*.py')),
             root / 'src/kinloyalty/analysis/inference.py', root / 'src/kinloyalty/logs.py']
    return {str(path.relative_to(root)): file_hash(path) for path in files}


def reproduce(manifest: str | Path, directory: str | Path, output: str | Path, *,
              allow_synthetic: bool = False, resamples: int | None = None) -> dict:
    """Write a fresh deterministic result directory from immutable eligible logs.

    No credentials or clients are loaded. Both analyze and reproduce use this
    same replay-first path. Production uses the frozen 10,000-replication values;
    overrides are explicitly restricted to synthetic verification.
    """
    manifest, directory, output = Path(manifest), Path(directory), Path(output)
    check_input_paths(manifest, directory)
    check_destination(output, live=False)
    root = Path(__file__).resolve().parents[4]
    protected_reports = [root / f'results/study2/{phase}-report' for phase in ('smoke', 'pilot')]
    if output.resolve().is_relative_to(directory.resolve()) or any(output.resolve().is_relative_to(path) for path in protected_reports):
        raise ValueError('Analysis output must be separate from input and mechanical-report directories.')
    if output.exists():
        raise ValueError('Choose a fresh result directory; existing results are never overwritten.')
    data = load_data(manifest, directory, allow_synthetic=allow_synthetic)
    inputs = _input_hashes(manifest, directory)
    metadata, tables, arrays = analyze_core(data, resamples=resamples)
    tables.update(diagnostic_tables(data))
    draws = arrays['bootstrap_scenario_indices']
    kinship, samples = bootstrap_group_means(data.episodes, data.scenarios, draws,
                                           outcome='surplus_share', group_by=['self_pair', 'card_says'])
    tables['actual_kinship_means'] = kinship
    arrays.update({f'kinship_{key}': values for key, values in samples.items()})
    cards = []
    for outcome in ('deal', 'within_deal_share'):
        means, samples = bootstrap_group_means(data.episodes, data.scenarios, draws, outcome=outcome, group_by=['card_says'])
        cards.append(means)
        arrays.update({f'card_{key}': values for key, values in samples.items()})
    tables['price_and_deal_means'] = pd.concat(cards, ignore_index=True)
    tables['episodes'] = data.episodes
    tables['scenario_index'] = data.scenarios.assign(bootstrap_column=range(len(data.scenarios)))
    metadata.update(input_sha256=inputs, code_sha256=_code_hashes(), provenance=collect_provenance(),
                    packages={name: importlib.metadata.version(name) for name in ('numpy', 'pandas', 'scipy', 'statsmodels', 'matplotlib')},
                    figure2_grouping='card_says: same, other, none',
                    interaction_sign='(same - other in self-pairs) - (same - other in cross-pairs)',
                    concession_sign='positive when a buyer raises its own offer; signed and unclipped',
                    outcome_eligibility_table='tables/outcome_eligibility.csv',
                    results_status='SIMULATED VERIFICATION ONLY' if data.synthetic else 'MAIN STUDY')
    if inputs != _input_hashes(manifest, directory):
        raise ValueError('Input artifacts changed during reproduction; no results written.')
    output.mkdir(parents=True)
    (output / 'tables').mkdir()
    (output / 'figures').mkdir()
    for name, table in tables.items():
        table.to_csv(output / 'tables' / f'{name}.csv', index=False, float_format='%.17g', lineterminator='\n')
    np.savez_compressed(output / 'resamples.npz', **arrays)
    (output / 'metadata.json').write_text(json.dumps(metadata, indent=2, sort_keys=True, allow_nan=False) + '\n', encoding='utf-8')
    from kinloyalty.analysis.study2.figures import draw_buyer_estimates, draw_distributions, draw_main, draw_price_and_deals
    draw_main(kinship, output / 'figures', synthetic=data.synthetic)
    draw_price_and_deals(tables['price_and_deal_means'], output / 'figures', group_column='card_says',
                        order=['same', 'other', 'none'], synthetic=data.synthetic)
    draw_buyer_estimates(tables['contrasts'], data.config.models, output / 'figures', synthetic=data.synthetic)
    draw_distributions(data.episodes, output / 'figures', group_column='condition',
                       order=['not_disclosed', 'true', 'swapped'], synthetic=data.synthetic)
    p2 = tables['contrasts'].loc[tables['contrasts'].test.eq('p2')].iloc[0]
    report = (
        '# Study 2 results\n\n' + metadata['results_status'] + '\n\n'
        f'All {data.replay["episodes_verified"]} episode summaries verified against saved turn attempts.\n\n'
        f'Primary same-label minus other-label share: {p2.estimate}; 95% interval [{p2.ci_low}, {p2.ci_high}]; '
        f'two-sided permutation p={p2.permutation_p_value}.\n\n'
        f'Bootstrap TOST: {json.dumps(metadata["tost"], sort_keys=True)}\n\n'
        'Primary inference uses scenario bootstraps and matched-label permutations. '
        'Pair-cluster standard errors are a robustness check only (16 clusters).\n\n'
        'Secondary tests have no multiplicity correction. Deal-only share and messages to agreement '
        'condition on agreement, which the card can itself affect. Concessions use only consecutive own buyer offers; '
        'acceptance is not an offer. Positive means raising the offer; negative values and all other outcomes are unclipped. '
        'See outcome_eligibility.csv for eligible episodes per original condition and displayed label.\n\n'
        'Every permutation test reports complete and incomplete tested-pair strata. Incomplete pairs stay fixed; '
        'eligible singleton rows remain in OLS/bootstrap. Missing third-condition outcomes never prevent a complete tested-pair swap.\n\n'
        'The secondary interaction is (same minus other in self-pairs) minus (same minus other in cross-pairs), '
        'adjusted for pair and opener; it has a bootstrap interval only, with no permutation test. '
        'The actual-kinship mean table is descriptive, without a test. Figure 2 groups by displayed same/other/none.\n\n'
        'metadata.json records frozen seeds, methods, replay, package versions, code/input hashes, and provenance. '
        'resamples.npz preserves every bootstrap scenario index, estimate, and permutation statistic, including unavailable draws. '
        'Failed draws are never dropped or redrawn; affected intervals/TOST are unavailable.\n'
    )
    (output / 'report.md').write_text(report, encoding='utf-8')
    inventory = {str(path.relative_to(output)): hashlib.sha256(path.read_bytes()).hexdigest()
                 for path in sorted(output.rglob('*')) if path.is_file()}
    (output / 'artifacts.sha256.json').write_text(json.dumps(inventory, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    return {'output': str(output), 'synthetic': data.synthetic, 'episodes_verified': data.replay['episodes_verified'],
            'tests_reported': len(tables['contrasts']), 'bootstrap_resamples': metadata['bootstrap_resamples'],
            'permutation_resamples': metadata['permutation_resamples'], 'primary_estimate': p2.estimate,
            'artifacts': len(inventory)}
