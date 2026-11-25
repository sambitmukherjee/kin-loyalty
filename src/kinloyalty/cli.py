"""Expose package information and offline prompt-review generation."""

import argparse
from collections.abc import Sequence
from pathlib import Path

from kinloyalty import __version__


def main(argv: Sequence[str] | None = None) -> None:
    """Display package information or write an offline prompt-review artifact."""
    parser = argparse.ArgumentParser(
        prog="kinloyalty",
        description="Study 1 tools. Prompt review is offline; experiment commands are not implemented yet.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    commands = parser.add_subparsers(dest="command")
    review = commands.add_parser("review-prompts", help="Write complete rendered prompts for review.")
    review.add_argument("--config", type=Path, default=Path("configs/study1.yaml"))
    review.add_argument("--model", required=True, help="Focal model key in the configured roster.")
    review.add_argument("--output", type=Path, default=Path("docs/study1_prompt_review.md"))
    args = parser.parse_args(argv)
    if args.command == "review-prompts":
        from kinloyalty.prompts import load_prompt_library
        from kinloyalty.review import write_prompt_review

        try:
            library = load_prompt_library(args.config)
            write_prompt_review(library, args.output, model=args.model)
        except (OSError, ValueError, KeyError) as error:
            parser.error(str(error))
        print(f"Wrote draft prompt review to {args.output}")
    else:
        parser.print_help()
