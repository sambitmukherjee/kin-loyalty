"""Draw deterministic paper-size matplotlib figures from validated tidy tables."""

from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


LABEL_TEXT = {"own_model": "Own model", "other_lab": "Other lab", "fictional": "Fictional",
              "not_disclosed": "Undisclosed", "human": "Human"}


def _save(figure: plt.Figure, output: Path, name: str, formats: list[str]) -> None:
    for extension in formats:
        metadata = {"CreationDate": None, "ModDate": None} if extension == "pdf" else {"Software": "kin-loyalty"}
        figure.savefig(output / f"{name}.{extension}", dpi=220, metadata=metadata)
    plt.close(figure)


def _distribution(axis: plt.Axes, frame: pd.DataFrame, labels: list[str], *, offset: float, color: str, width: float) -> None:
    for index, label in enumerate(labels):
        values = frame.loc[frame.label == label, "outcome"].to_numpy()
        if len(values) < 2 or np.ptp(values) == 0:
            axis.plot([index + offset], [values[0]], marker="_", color=color, markersize=12)
            continue
        violin = axis.violinplot([values], positions=[index + offset], widths=width,
                                 showmedians=True, showextrema=True)
        for body in violin["bodies"]:
            body.set_facecolor(color)
            body.set_alpha(.55)
        for key in ("cmedians", "cmins", "cmaxes", "cbars"):
            violin[key].set_color(color)


def create_figures(frame: pd.DataFrame, estimates: pd.DataFrame, comprehension: pd.DataFrame | None,
                   study: dict[str, Any], roster: dict[str, Any], output: Path, *, synthetic: bool) -> None:
    """Save main distributions, S1 coefficients, responder distributions, and check table."""
    labels, models = list(study["labels"]), list(roster)
    formats = study["analysis"]["figure_formats"]
    prefix = "SIMULATED — " if synthetic else ""
    with plt.rc_context({"font.size": 7, "axes.titlesize": 8, "pdf.fonttype": 42}):
        fig, axes = plt.subplots(2, 2, figsize=(7.2, 5.1), layout="constrained")
        for model, axis in zip(models, axes.flat, strict=True):
            subset = frame[frame.model == model]
            _distribution(axis, subset[subset.decision == "dictator"], labels, offset=-.16, color="#2166ac", width=.29)
            _distribution(axis, subset[subset.decision == "ultimatum_proposer"], labels, offset=.16, color="#b35806", width=.29)
            axis.set(title=roster[model]["display_name"], ylabel="Dollars to counterparty", ylim=(-2, 102),
                     xticks=range(len(labels)), xticklabels=[LABEL_TEXT[label] for label in labels])
            axis.tick_params(axis="x", rotation=20)
            axis.grid(axis="y", alpha=.2)
        p1 = estimates[estimates.designation == "primary_P1"].iloc[0]
        fig.suptitle(f"{prefix}Dictator (blue) and proposer (orange) distributions\nPooled P1: ${p1.estimate:.2f} [{p1.ci_low:.2f}, {p1.ci_high:.2f}], two-sided p={p1.permutation_p:.4g}")
        _save(fig, output, "main_distributions", formats)

        fig, axes = plt.subplots(2, 2, figsize=(7.2, 5), layout="constrained")
        for model, axis in zip(models, axes.flat, strict=True):
            _distribution(axis, frame[(frame.model == model) & (frame.decision == "ultimatum_responder")], labels, offset=0, color="#2166ac", width=.65)
            axis.set(title=roster[model]["display_name"], ylabel="Minimum dollars for principal", ylim=(-2, 102),
                     xticks=range(len(labels)), xticklabels=[LABEL_TEXT[label] for label in labels])
            axis.tick_params(axis="x", rotation=20)
            axis.grid(axis="y", alpha=.2)
        fig.suptitle(prefix + "Ultimatum responder distributions")
        _save(fig, output, "responder_distributions", formats)

        fig, axis = plt.subplots(figsize=(7.2, 3.4), layout="constrained")
        scopes = [*models, "pooled"]
        unavailable_point = False
        unavailable_interval = False
        for offset, outcome, method, color, label in (
            (-.2, "outcome", "unadjusted", "#2166ac", "Offer"),
            (0, "outcome", "belief_adjusted", "#b35806", "Offer, belief adjusted"),
            (.2, "belief", "unadjusted", "#1b7837", "Stated belief"),
        ):
            subset = estimates[(estimates.decision == "ultimatum_proposer") & (estimates.family == "own_vs_other")
                               & (estimates.outcome == outcome) & (estimates.method == method)].set_index("scope").loc[scopes]
            positions = np.arange(len(scopes)) + offset
            axis.vlines(positions, subset.ci_low, subset.ci_high, color=color)
            axis.scatter(positions, subset.estimate, color=color, label=label, s=10)
            for position, row in zip(positions, subset.itertuples(), strict=True):
                if not row.estimable:
                    axis.text(position, .025, "NE", color=color, ha="center", transform=axis.get_xaxis_transform(), fontsize=6)
                    unavailable_point = True
                elif not row.interval_available:
                    axis.annotate("*", (position, row.estimate), xytext=(3, 2), textcoords="offset points", color=color)
                    unavailable_interval = True
        axis.axhline(0, color="gray", linewidth=.7)
        axis.set(xticks=range(len(scopes)), xticklabels=[roster[model]["display_name"] for model in models] + ["Pooled"],
                 ylabel="Own-model minus other-lab dollars")
        notes = (["NE: adjusted contrast not estimable"] if unavailable_point else [])
        if unavailable_interval:
            notes.append("*: bootstrap interval unavailable")
        title = prefix + "S1 descriptive comparison: offers and beliefs"
        axis.set_title(title + ("\n" + "; ".join(notes) if notes else ""), pad=29)
        axis.legend(loc="lower center", bbox_to_anchor=(.5, 1.01), ncol=3, frameon=False, fontsize=6)
        _save(fig, output, "s1_coefficients", formats)

        if comprehension is not None:
            fig, axis = plt.subplots(figsize=(7.2, 4.9), layout="constrained")
            axis.axis("off")
            table_rows = [[roster[row.model]["display_name"], LABEL_TEXT[row.label],
                           str(row.n_yes), str(row.n_no), str(row.n_unsure),
                           "unscored" if not row.scored else "incomplete" if row.label_pass is None else "pass" if row.label_pass else "fail"]
                          for row in comprehension.itertuples()]
            table = axis.table(cellText=table_rows, colLabels=["Model", "Card", "Yes", "No", "Unsure", "Rule"],
                               cellLoc="center", bbox=[0, 0, 1, .94], colWidths=[.24, .18, .1, .1, .1, .18])
            table.auto_set_font_size(False)
            table.set_fontsize(7)
            axis.text(.5, .98, "Planned denominator: 20 per card", transform=axis.transAxes,
                      ha="center", va="top", fontsize=7)
            fig.suptitle(prefix + "Comprehension check", fontsize=8)
            _save(fig, output, "comprehension", formats)
