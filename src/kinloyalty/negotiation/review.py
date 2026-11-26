"""Write deterministic full-prompt review examples from hand-written fixtures."""

import argparse
import os
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from kinloyalty.logs import file_hash
from kinloyalty.negotiation import Role
from kinloyalty.negotiation.config import Study2Config, load_config
from kinloyalty.negotiation.prompts import render_turn_prompt
from kinloyalty.negotiation.scenarios import Scenario, pair_id
from kinloyalty.negotiation.transcript import TranscriptTurn, other_role


@dataclass(frozen=True)
class FixedPositions:
    """Hold illustrative facts and hand-written prefixes, never main-run draws."""

    facts: dict[str, Any]
    transcripts: dict[str, tuple[TranscriptTurn, ...]]
    source: Path

    def position(
        self, config: Study2Config, *, buyer_model: str, seller_model: str,
        role: Role, message_number: int,
    ) -> tuple[Scenario, tuple[TranscriptTurn, ...]]:
        """Select the opener and live prefix that place the requested role on turn."""
        if not 1 <= message_number <= config.message_limit:
            raise ValueError("Requested position is outside the message limit.")
        opener = role if message_number % 2 else other_role(role)
        prefix = self.transcripts[opener][:message_number - 1]
        if len(prefix) != message_number - 1:
            raise ValueError("The fixed transcript is too short for this position.")
        pair = pair_id(config, buyer_model, seller_model)
        return Scenario(
            scenario_id=f"study2:fixture:{pair}:{opener}_opens", pair_id=pair,
            opener=opener, **self.facts,
        ), prefix


def load_fixed_positions(config: Study2Config) -> FixedPositions:
    """Read fixed review/probe prefixes and reject non-offer or non-alternating histories."""
    source = config.template_directory / config.study["smoke"]["probes"]["transcript_file"]
    data = yaml.safe_load(source.read_text(encoding="utf-8"))
    if data["schema_version"] != 1 or set(data["transcripts"]) != {"buyer", "seller"}:
        raise ValueError("Expected fixed transcript schema version 1 with both openers.")
    transcripts = {}
    for opener, rows in data["transcripts"].items():
        turns = tuple(TranscriptTurn(**row) for row in rows)
        for index, turn in enumerate(turns):
            expected = opener if index % 2 == 0 else other_role(opener)
            if turn.role != expected or turn.action != "offer":
                raise ValueError("Fixed transcript prefixes must alternate offers.")
        transcripts[opener] = turns
    return FixedPositions(data["scenario"], transcripts, source)


def render_prompt_review(config: Study2Config) -> str:
    """Return complete opening/late requests for one self-pair and one cross-pair."""
    positions = load_fixed_positions(config)
    order = config.model_order
    cross_seller = order[-1] if len(order) > 2 else order[0]
    pairs = [("self-pair", order[0], order[0]), ("cross-pair", order[1], cross_seller)]
    numbers = tuple(dict.fromkeys((1, 2, config.message_limit - 1, config.message_limit)))
    example_count = len(pairs) * len(config.study["conditions"]) * 2 * len(numbers)
    number_text = ", ".join(map(str, numbers))
    lines = [
        "# Study 2 fully rendered prompt review", "",
        "Generated offline from fixed hand-written scenarios and transcripts. No main-run",
        "scenario seed was used, no API call was made, and no reply schema is defined here.",
        f"This file contains {example_count} complete system/user requests: two pairs, three conditions,",
        f"two roles, and messages {number_text}. Each position uses its appropriate opener;",
        "these are illustrative positions rather than one episode per group.", "",
        "Private limits and assignment metadata below are for researcher review only;",
        "they are not extra content sent to either agent. Fixed transcript text is shared",
        "across models/conditions and is also available for the approved smoke probes.", "",
        "## Source SHA-256", "", "| Source | SHA-256 |", "| --- | --- |",
    ]
    sources = [config.path, config.model_path, *sorted(config.template_directory.glob("*.txt")), positions.source]
    for source in sources:
        label = Path(os.path.relpath(source, config.path.parent.parent)).as_posix()
        lines.append(f"| `{label}` | `{file_hash(source)}` |")
    for pair_kind, buyer, seller in pairs:
        for condition in config.study["conditions"]:
            alternative = order[1] if pair_kind == "self-pair" and condition == "swapped" else None
            for role in ("buyer", "seller"):
                for number in numbers:
                    scenario, prefix = positions.position(
                        config, buyer_model=buyer, seller_model=seller, role=role, message_number=number,
                    )
                    prompt = render_turn_prompt(
                        config, buyer_model=buyer, seller_model=seller, condition=condition,
                        role=role, scenario=scenario, transcript=prefix, swapped_model=alternative,
                    )
                    lines.extend([
                        "", f"## {pair_kind} / {condition} / {role} / message {number}", "",
                        f"Buyer: `{buyer}`; seller: `{seller}`; card says: `{prompt.disclosure.card_says}`.",
                        f"Displayed seller model: `{prompt.disclosure.model_text}` (buyer sees it only).",
                        f"Fixture: {scenario.item}; P=${scenario.reference_price}; s=${scenario.seller_min}; "
                        f"b=${scenario.buyer_max}; opener={scenario.opener}.", "",
                        "System prompt:", "", "```text", prompt.system_prompt, "```", "",
                        "Single user message:", "", "```text", prompt.user_message, "```",
                    ])
    return "\n".join(lines) + "\n"


def write_prompt_review(config: Study2Config, output: str | Path) -> None:
    """Write a new review file, refusing to overwrite any existing artifact."""
    content = render_prompt_review(config)
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8") as stream:
        stream.write(content)


def main(argv: Sequence[str] | None = None) -> None:
    """Generate review examples offline without extending the shared Study 1 CLI."""
    parser = argparse.ArgumentParser(description="Write full Study 2 prompt review examples; no API calls.")
    parser.add_argument("--config", type=Path, default=Path("configs/study2.yaml"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        write_prompt_review(load_config(args.config), args.output)
    except (OSError, ValueError, KeyError) as error:
        parser.error(str(error))
    print(f"Wrote Study 2 prompt review to {args.output}; no calls made.")


if __name__ == "__main__":
    main()
