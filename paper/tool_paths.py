"""Find Poppler commands in an ordinary installation or an explicit override."""

import argparse
import os
from pathlib import Path
import shutil


POPPLER_TOOLS = ("pdftotext", "pdffonts", "pdfinfo", "pdftoppm", "pdftocairo")


def poppler_tool(name):
    """Resolve one executable without assuming a platform or an app installation.

    A command-specific variable, such as PDFTOTEXT, takes precedence over
    PAPER_POPPLER_BIN. Otherwise the command is found on PATH. An invalid
    explicit override is an error rather than a reason to use another copy.
    """
    if name not in POPPLER_TOOLS:
        raise ValueError(f"Unknown Poppler command: {name}.")
    override = os.environ.get(name.upper())
    directory = os.environ.get("PAPER_POPPLER_BIN")
    if override:
        candidate = str(Path(override).expanduser())
        if "/" in override:
            candidate = str(Path(candidate).absolute())
        setting = name.upper()
    elif directory:
        candidate = str(Path(directory).expanduser().resolve() / name)
        setting = "PAPER_POPPLER_BIN"
    else:
        candidate = name
        setting = "PATH"
    found = shutil.which(candidate)
    if found:
        return found
    raise FileNotFoundError(
        f"Cannot find executable {name!r} using {setting}. Install Poppler and "
        f"put its bin directory on PATH, set PAPER_POPPLER_BIN, or set "
        f"{name.upper()} to the executable's full path. See paper/README.md."
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("commands", choices=POPPLER_TOOLS, nargs="+")
    args = parser.parse_args()
    try:
        for name in args.commands:
            print(f"{name}: {poppler_tool(name)}")
    except FileNotFoundError as error:
        parser.exit(1, f"{error}\n")


if __name__ == "__main__":
    main()
