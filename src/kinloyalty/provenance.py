"""Collect local code/package provenance without importing provider SDKs or reading keys."""

import subprocess
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any

from kinloyalty import __version__


def collect_provenance() -> dict[str, Any]:
    """Report available code revision, dirty state, package and SDK versions."""
    root = Path(__file__).resolve().parents[2]

    def git(*arguments: str) -> str | None:
        try:
            return subprocess.check_output(
                ["git", *arguments], cwd=root, text=True, stderr=subprocess.DEVNULL, timeout=5,
            ).strip()
        except (subprocess.SubprocessError, OSError):
            return None

    sdk_versions: dict[str, str | None] = {}
    for package in ("anthropic", "openai", "google-genai"):
        try:
            sdk_versions[package] = version(package)
        except PackageNotFoundError:
            sdk_versions[package] = None
    status = git("status", "--porcelain")
    return {
        "git_commit": git("rev-parse", "HEAD"), "code_dirty": None if status is None else bool(status),
        "package_version": __version__, "sdk_versions": sdk_versions,
    }
