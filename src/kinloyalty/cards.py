"""Render neutral agent cards and human counterparty blocks from supplied text."""

from collections.abc import Sequence


def render_agent_card(
    fields: Sequence[Sequence[str]], *, counterparty: str, model_text: str
) -> str:
    """Fill ordered card fields, preserving the protocol's two-space indentation."""
    values = {"COUNTERPARTY": counterparty, "COUNTERPARTY_MODEL_TEXT": model_text}
    return "\n".join(f"  {name}: {value.format_map(values)}" for name, value in fields)


def render_counterparty_block(
    fields: Sequence[Sequence[str]],
    *,
    counterparty: str,
    model_text: str,
    agent_template: str,
    human_template: str,
    human: bool = False,
) -> str:
    """Combine supplied templates and fields without adding ratings or other cues."""
    if human:
        if model_text:
            raise ValueError("A human counterparty must have empty model text.")
        return human_template.format_map({"COUNTERPARTY": counterparty})
    card = render_agent_card(fields, counterparty=counterparty, model_text=model_text)
    return agent_template.format_map({"COUNTERPARTY": counterparty, "AGENT_CARD": card})
