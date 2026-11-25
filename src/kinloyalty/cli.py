"""Expose package information until experiment commands are implemented."""

import argparse

from kinloyalty import __version__


def main() -> None:
    """Display the available command help or the installed package version."""
    parser = argparse.ArgumentParser(
        prog="kinloyalty",
        description=(
            "Study 1 repository skeleton. Experiment and analysis commands "
            "will be added in subsequent approved phases."
        ),
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.parse_args()
    parser.print_help()
