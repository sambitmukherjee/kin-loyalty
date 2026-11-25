"""Load Study 1 text and render a decision or separate comprehension request offline."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from kinloyalty.cards import render_counterparty_block
from kinloyalty.schemas import response_schema


@dataclass(frozen=True)
class PromptLibrary:
    """Hold the study configuration, model roster, and resolved template directory."""

    study: dict[str, Any]
    models: dict[str, dict[str, Any]]
    template_directory: Path


@dataclass(frozen=True)
class RenderedPrompt:
    """Keep exact messages, the canonical response schema, and the card model text."""

    system_prompt: str
    user_message: str
    json_schema: dict[str, Any]
    counterparty_model_text: str


def load_prompt_library(config_path: str | Path) -> PromptLibrary:
    """Load YAML, resolving file/directory paths relative to the study YAML file."""
    config_path = Path(config_path).resolve()
    study = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    models_path = config_path.parent / study["models_file"]
    roster = yaml.safe_load(models_path.read_text(encoding="utf-8"))
    return PromptLibrary(
        study=study,
        models=roster["models"],
        template_directory=(config_path.parent / study["prompt_directory"]).resolve(),
    )


def _read_template(library: PromptLibrary, filename: str) -> str:
    # Remove only the file terminator, preserving all internal prompt whitespace.
    return (library.template_directory / filename).read_text(encoding="utf-8").removesuffix("\n")


def _counterparty_model_text(
    library: PromptLibrary, model: str, label: str, other_model: str | None
) -> str:
    condition = library.study["labels"][label]
    if label != "other_lab" and other_model is not None:
        raise ValueError("Specify other_model only for the other_lab condition.")
    if "model_text" in condition:
        return condition["model_text"]
    source = condition["model_source"]
    if source == "focal_model":
        named_model = library.models[model]
    elif source == "other_three_models":
        if other_model is None or other_model not in library.models:
            raise ValueError("other_lab requires an explicit model key from the roster.")
        named_model = library.models[other_model]
        if named_model["lab"] == library.models[model]["lab"]:
            raise ValueError("other_lab must name a model from another lab.")
    else:
        raise ValueError(f"Unknown model source: {source}")
    return f"{named_model['display_name']} ({named_model['lab']})"


def render_prompt(
    library: PromptLibrary,
    *,
    model: str,
    decision: str,
    label: str,
    paraphrase: int,
    other_model: str | None = None,
) -> RenderedPrompt:
    """Render one specified design cell without sampling, keys, or provider calls.

    The other_lab model must be supplied explicitly by the caller, so rendering
    cannot silently choose a rotation. Comprehension uses the dictator body and
    replaces its decision instructions; it never asks for a monetary choice.
    """
    if model not in library.models:
        raise ValueError(f"Unknown model: {model}")
    if label not in library.study["labels"]:
        raise ValueError(f"Unknown label: {label}")
    if decision not in library.study["decisions"] and decision != "comprehension":
        raise ValueError(f"Unknown decision: {decision}")
    if decision == "comprehension" and label not in library.study["comprehension"]["labels"]:
        raise ValueError("Comprehension checks require a card condition; human is excluded.")
    name_pair = next(
        (entry for entry in library.study["paraphrases"] if entry["id"] == paraphrase), None
    )
    if name_pair is None:
        raise ValueError(f"Unknown paraphrase: {paraphrase}")

    model_text = _counterparty_model_text(library, model, label, other_model)
    block = render_counterparty_block(
        library.study["card"]["fields"],
        counterparty=name_pair["counterparty"],
        model_text=model_text,
        agent_template=_read_template(library, "counterparty_agent.txt"),
        human_template=_read_template(library, "counterparty_human.txt"),
        human=label == "human",
    )
    self_model = library.models[model]
    values = {
        "SELF_EXACT_MODEL": self_model["display_name"],
        "SELF_LAB": self_model["lab"],
        "PRINCIPAL": name_pair["principal"],
        "COUNTERPARTY": name_pair["counterparty"],
        "COUNTERPARTY_BLOCK": block,
    }
    body_decision = "dictator" if decision == "comprehension" else decision
    body = _read_template(library, f"{body_decision}_{paraphrase}.txt").format_map(values)
    # JSON instructions are literal text, so their braces are never interpolated.
    instructions = _read_template(library, f"reply_{decision}.txt")
    return RenderedPrompt(
        system_prompt=_read_template(library, f"system_{paraphrase}.txt").format_map(values),
        user_message=f"{body}\n\n{instructions}",
        json_schema=response_schema(decision, library.study),
        counterparty_model_text=model_text,
    )
