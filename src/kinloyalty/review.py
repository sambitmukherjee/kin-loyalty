"""Generate a deterministic human-review document containing complete rendered prompts."""

import json
from pathlib import Path

from kinloyalty.prompts import PromptLibrary, render_prompt
from kinloyalty.schemas import response_schema


def build_prompt_review(library: PromptLibrary, *, model: str) -> str:
    """Show every decision/check cell and every other-lab card variant for one model."""
    if model not in library.models:
        raise ValueError(f"Unknown model: {model}")
    self_model = library.models[model]
    other_count = sum(value["lab"] != self_model["lab"] for value in library.models.values())
    paraphrases = len(library.study["paraphrases"])
    decision_cells = paraphrases * len(library.study["decisions"]) * len(library.study["labels"])
    decision_examples = paraphrases * len(library.study["decisions"]) * sum(
        other_count if label == "other_lab" else 1 for label in library.study["labels"]
    )
    check_examples = paraphrases * sum(
        other_count if label == "other_lab" else 1 for label in library.study["comprehension"]["labels"]
    )
    sections = [
        "# Study 1 prompt review — DRAFT, awaiting researcher approval",
        (
            f"Focal model: **{self_model['display_name']} ({self_model['lab']})**. "
            "This document contains rendered examples, not calls or observations. "
            "Headings and commentary are for review only and are never sent to a model."
        ),
        (
            f"All {decision_cells} decision × label × paraphrase combinations are shown. Each "
            f"other_lab combination includes all {other_count} eligible named models, giving "
            f"{decision_examples} complete decision prompts. The separate comprehension section "
            f"contains {check_examples} complete prompts, including its other_lab variants. "
            "These are coverage examples, not a trial manifest or a rotation schedule."
        ),
        (
            "Paraphrase 1 reproduces the protocol wording. Paraphrases 2 and 3 "
            "and their name pairs are proposals. The first system sentence, card "
            "block, human sentence, and task-specific reply instructions are "
            "protected across paraphrases apart from name substitution. "
            "Messages below have no trailing newline."
        ),
        "## Name pairs",
    ]
    name_table = ["| Paraphrase | Principal | Counterparty | Status |", "| --- | --- | --- | --- |"]
    for entry in library.study["paraphrases"]:
        name_table.append(
            f"| {entry['id']} | {entry['principal']} | {entry['counterparty']} | "
            f"{entry['name_status']} |"
        )
    sections.append("\n".join(name_table))
    sections.extend([
        "## Canonical response schemas",
        (
            "Schemas are identical across labels, models, and paraphrases for a "
            "given task. All fields are required; additional fields are disallowed. "
            "The canonical numeric range is 0–100. If a provider's verified API "
            "cannot accept numeric bounds, only its submitted schema may omit "
            "them; local validation must retain the bounds. One-sentence reasons "
            "are requested in the prompt; no sentence-count heuristic is added here."
        ),
    ])
    decisions = [*library.study["decisions"], "comprehension"]
    for decision in decisions:
        schema = json.dumps(response_schema(decision, library.study), ensure_ascii=False, indent=2)
        sections.extend([f"### Schema: {decision}", f"```json\n{schema}\n```"])

    for task_group, tasks in (
        ("Decision prompts", list(library.study["decisions"])),
        ("Separate comprehension prompts", ["comprehension"]),
    ):
        sections.append(f"## {task_group}")
        for entry in library.study["paraphrases"]:
            for decision in tasks:
                labels = (
                    library.study["comprehension"]["labels"]
                    if decision == "comprehension" else library.study["labels"]
                )
                for label in labels:
                    others = (
                        [key for key, value in library.models.items() if value["lab"] != self_model["lab"]]
                        if label == "other_lab" else [None]
                    )
                    for other in others:
                        prompt = render_prompt(
                            library, model=model, decision=decision, label=label,
                            paraphrase=entry["id"], other_model=other,
                        )
                        title = f"p{entry['id']} / {decision} / {label}"
                        if other is not None:
                            title += f" / {library.models[other]['display_name']}"
                        sections.extend([
                            f"### {title}",
                            "System message:",
                            f"```text\n{prompt.system_prompt}\n```",
                            "User message:",
                            f"```text\n{prompt.user_message}\n```",
                        ])
    return "\n\n".join(sections) + "\n"


def write_prompt_review(library: PromptLibrary, path: str | Path, *, model: str) -> None:
    """Write the fully rendered review artifact without contacting any provider."""
    content = build_prompt_review(library, model=model)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
