"""Draw Study 2 paper figures from derived numerical tables, without reading logs."""

from pathlib import Path

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


LABELS = {'none': 'Not disclosed', 'same': 'Says same model', 'other': 'Says different model',
          'not_disclosed': 'Not disclosed', 'true': 'Truthful disclosure', 'swapped': 'Swapped disclosure'}
BLUE, ORANGE = '#2166ac', '#b35806'


def _save(figure: plt.Figure, output: Path, name: str) -> None:
    for extension in ('pdf', 'png'):
        metadata = {'CreationDate': None, 'ModDate': None} if extension == 'pdf' else {'Software': 'kin-loyalty'}
        figure.savefig(output / f'{name}.{extension}', dpi=220, metadata=metadata)
    plt.close(figure)


def _point(axis: plt.Axes, position: float, row, *, color: str) -> None:
    if pd.isna(row.estimate):
        axis.text(position, .03, 'NE', ha='center', transform=axis.get_xaxis_transform())
        return
    axis.scatter([position], [row.estimate], color=color, s=19, zorder=3)
    if row.interval_available:
        axis.vlines(position, row.ci_low, row.ci_high, color=color, linewidth=1.4)
        axis.plot([position - .04, position + .04], [row.ci_low, row.ci_low], color=color, linewidth=.8)
        axis.plot([position - .04, position + .04], [row.ci_high, row.ci_high], color=color, linewidth=.8)
    else:
        axis.annotate('*', (position, row.estimate), xytext=(4, 2), textcoords='offset points', color=color)


def draw_main(means: pd.DataFrame, output: Path, *, synthetic: bool) -> None:
    """Display the actual-copy × stated-label table with each actual group's ND baseline."""
    prefix = 'SIMULATED — ' if synthetic else ''
    with plt.rc_context({'font.size': 7, 'axes.titlesize': 8, 'pdf.fonttype': 42}):
        figure, axes = plt.subplots(2, 1, figsize=(7.2, 5.1), sharex=True, layout='constrained')
        for actual, axis in zip((True, False), axes, strict=True):
            group = means.loc[means.self_pair.eq(actual)]
            baseline = group.loc[group.card_says.eq('none')].iloc[0]
            if pd.notna(baseline.estimate):
                axis.axhline(baseline.estimate, color='gray', linestyle='--', linewidth=.9, label='Not-disclosed mean')
                if baseline.interval_available:
                    axis.axhspan(baseline.ci_low, baseline.ci_high, color='gray', alpha=.12, label='Not-disclosed 95% CI')
            for index, (label, color) in enumerate((('same', BLUE), ('other', ORANGE))):
                _point(axis, index, group.loc[group.card_says.eq(label)].iloc[0], color=color)
            axis.set(title='Actually faces a copy' if actual else 'Actually faces a different model',
                     ylabel='Mean buyer surplus share', xlim=(-.5, 1.5))
            axis.grid(axis='y', alpha=.2)
            axis.legend(loc='best', frameon=False, fontsize=6)
        axes[-1].set(xticks=[0, 1], xticklabels=[LABELS['same'], LABELS['other']])
        figure.suptitle(prefix + 'Buyer surplus by displayed label and actual kinship\nScenario-bootstrap 95% intervals; * interval unavailable; NE not estimable')
        _save(figure, output, 'main_label_by_actual_kinship')


def draw_price_and_deals(means: pd.DataFrame, output: Path, *, group_column: str, order: list[str], synthetic: bool) -> None:
    """Plot an explicitly supplied grouping; the caller controls its scientific definition."""
    prefix = 'SIMULATED — ' if synthetic else ''
    with plt.rc_context({'font.size': 7, 'axes.titlesize': 8, 'pdf.fonttype': 42}):
        figure, axes = plt.subplots(1, 2, figsize=(7.2, 3.4), layout='constrained')
        for outcome, title, axis, color in zip(('deal', 'within_deal_share'), ('Deal rate', 'Surplus share among deals'), axes, (BLUE, ORANGE), strict=True):
            for index, label in enumerate(order):
                row = means.loc[means.outcome.eq(outcome) & means[group_column].eq(label)].iloc[0]
                _point(axis, index, row, color=color)
            axis.set(title=title, xticks=range(len(order)), xticklabels=[LABELS[label] for label in order])
            axis.tick_params(axis='x', rotation=15)
            axis.grid(axis='y', alpha=.2)
        figure.suptitle(prefix + 'Price and agreement\n95% scenario-bootstrap intervals; deal-only share conditions on a post-treatment outcome')
        _save(figure, output, 'deal_rate_and_within_deal_share')


def draw_buyer_estimates(contrasts: pd.DataFrame, roster: dict, output: Path, *, synthetic: bool) -> None:
    """Show secondary buyer-specific P2 estimates using the configured model order."""
    prefix = 'SIMULATED — ' if synthetic else ''
    with plt.rc_context({'font.size': 7, 'axes.titlesize': 8, 'pdf.fonttype': 42}):
        figure, axis = plt.subplots(figsize=(7.2, 3.4), layout='constrained')
        for index, model in enumerate(roster):
            row = contrasts.loc[contrasts.buyer_model.eq(model)].iloc[0]
            _point(axis, index, row, color=BLUE)
        axis.axhline(0, color='gray', linewidth=.7)
        axis.set(xticks=range(len(roster)), xticklabels=[row['display_name'] for row in roster.values()],
                 ylabel='Same-label minus other-label share',
                 title=prefix + 'Secondary: P2 by buyer model\n95% scenario-bootstrap intervals; * interval unavailable; NE not estimable')
        axis.grid(axis='y', alpha=.2)
        _save(figure, output, 'appendix_buyer_p2')


def draw_distributions(episodes: pd.DataFrame, output: Path, *, group_column: str, order: list[str], synthetic: bool) -> None:
    """Plot unbounded retained shares, including impasse zeros and mandate violations."""
    prefix = 'SIMULATED — ' if synthetic else ''
    values = episodes.loc[~episodes.excluded, 'surplus_share'].to_numpy(float)
    bins = np.histogram_bin_edges(values, bins=25) if len(values) else np.linspace(-.1, 1.1, 26)
    with plt.rc_context({'font.size': 7, 'axes.titlesize': 8, 'pdf.fonttype': 42}):
        figure, axes = plt.subplots(1, len(order), figsize=(7.2, 3.1), sharex=True, sharey=True, layout='constrained')
        for label, axis in zip(order, np.atleast_1d(axes), strict=True):
            group = episodes.loc[~episodes.excluded & episodes[group_column].eq(label)]
            axis.hist(group.surplus_share, bins=bins, color=BLUE, alpha=.75)
            axis.set(title=LABELS[label], xlabel='Buyer surplus share')
            axis.grid(axis='y', alpha=.2)
        np.atleast_1d(axes)[0].set_ylabel('Episodes')
        figure.suptitle(prefix + 'Surplus share distributions (including impasses)')
        _save(figure, output, 'appendix_share_distributions')
