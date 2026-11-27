"""Redraw registered contrasts only; no fitting, resampling, or new analysis."""
from pathlib import Path
import csv
import hashlib
import json
import os

PAPER = Path(__file__).resolve().parents[1]
os.environ.setdefault('MPLCONFIGDIR', str(PAPER / 'build' / 'matplotlib'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.text import Text
from matplotlib.textpath import TextPath
from matplotlib.patches import PathPatch
from matplotlib.transforms import Affine2D


def outline_text(figure):
    """Keep vector lettering while avoiding the kit-prohibited CID/Identity-H fonts."""
    figure.canvas.draw()
    renderer = figure.canvas.get_renderer()
    width, height = figure.get_size_inches()
    for text in list(figure.findobj(match=Text)):
        if not text.get_visible() or not text.get_text():
            continue
        # Matplotlib's own layout supplies aligned baseline offsets, in display
        # pixels. Paths use the identical font and point size, then map to the
        # figure coordinate system so PDF export can change renderer DPI safely.
        _, lines, _ = text._get_layout(renderer)
        anchor = text.get_transform().transform(text.get_position())
        for line, _, (x, y) in lines:
            path = TextPath((0, 0), line, prop=text.get_fontproperties(), size=text.get_fontsize())
            transform = (Affine2D().scale(1/(72*width), 1/(72*height))
                         .translate((anchor[0]+x)/figure.bbox.width,
                                    (anchor[1]+y)/figure.bbox.height) + figure.transFigure)
            figure.add_artist(PathPatch(path, transform=transform, facecolor=text.get_color(),
                                        edgecolor='none', clip_on=False, zorder=10))
        text.set_visible(False)


def main():
    source = PAPER.parent / 'results/study1/generated/contrasts.csv'
    with source.open() as handle:
        rows = list(csv.DictReader(handle))
    scopes = ['claude_sonnet_5_5', 'gpt_6_1_terra', 'gemini_4_hydrogen', 'kimi_k3_1_pro', 'pooled']
    names = ['Claude Sonnet 5.5', 'GPT-6.1 Terra', 'Gemini 4 Hydrogen', 'Kimi K3.1 Pro', 'Pooled average']
    panels = [('dictator', 'Dictator transfer'), ('ultimatum_proposer', 'Proposer offer'), ('ultimatum_responder', 'Responder minimum')]
    selected = [r for r in rows if r['family'] == 'own_vs_other' and r['outcome'] == 'outcome' and r['method'] == 'unadjusted']
    assert len(selected) == 15
    lookup = {(r['decision'], r['scope']): r for r in selected}
    plt.rcParams.update({'font.family': 'STIXGeneral', 'font.size': 9.5, 'axes.titlesize': 10,
                         'axes.labelsize': 9.5, 'xtick.labelsize': 9, 'ytick.labelsize': 9.5,
                         'pdf.fonttype': 42, 'ps.fonttype': 42, 'axes.spines.top': False,
                         'axes.spines.right': False, 'axes.spines.left': False})
    fig, axes = plt.subplots(1, 3, figsize=(7, 2.2), sharex=True, sharey=True)
    fig.subplots_adjust(left=.205, right=.985, top=.84, bottom=.24, wspace=.20)
    grey, accent = '#666666', '#006B9C'
    for ax, (decision, label) in zip(axes, panels):
        ax.set_title(label, pad=9)
        ax.axvline(0, color='#777777', linestyle=(0, (3, 3)), linewidth=.75, zorder=0)
        for index, scope in enumerate(scopes):
            r = lookup[(decision, scope)]
            assert r['estimable'] == r['interval_available'] == 'True'
            point, low, high = (float(r[key]) for key in ['estimate', 'ci_low', 'ci_high'])
            colour = accent if scope == 'pooled' else grey
            # Plot raw endpoints independently: a constant outcome can have
            # floating-point differences below 1e-12 between its point and CI.
            ax.hlines(index, low, high, color=colour, linewidth=1.5 if scope == 'pooled' else 1.1)
            ax.vlines([low, high], index-.065, index+.065, color=colour, linewidth=.8)
            ax.plot(point, index, 'o', markersize=5.2 if scope == 'pooled' else 4,
                    color=colour, markeredgecolor='#222222' if scope == 'pooled' else colour,
                    markeredgewidth=.5)
            if scope == 'pooled':
                ax.text(high+.65, index, f'{point:+.2f}', va='center', color=accent, fontweight='bold', fontsize=9.5)
        ax.set_xlim(-12, 16)
        ax.set_xticks([-10, 0, 10])
        ax.set_xlabel('Difference ($)', labelpad=4)
        ax.tick_params(axis='y', length=0, pad=7)
    axes[0].set_yticks(range(5), names)
    axes[0].set_ylim(4.55, -.55)
    for label in axes[0].get_yticklabels():
        if label.get_text() == 'Pooled average':
            label.set_fontweight('bold')
    output = PAPER / 'figures' / 'figure1.pdf'
    outline_text(fig)
    fig.savefig(output, metadata={'Title': None, 'Author': None, 'CreationDate': None, 'ModDate': None})
    plt.close(fig)
    (PAPER/'figures/figure1-source.json').write_text(json.dumps({
        'source': 'results/study1/generated/contrasts.csv',
        'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
        'selection': {'family': 'own_vs_other', 'outcome': 'outcome', 'method': 'unadjusted'},
        'contrasts': selected, 'new_analysis': False, 'native_size_inches': [7, 2.2],
        'minimum_label_points': 9, 'x_axis_dollars': [-12, 16],
        'lettering': 'vector outlines from the same STIXGeneral glyphs; no CID/Identity-H or Type 3 fonts'
    }, indent=2) + '\n')


if __name__ == '__main__':
    main()
