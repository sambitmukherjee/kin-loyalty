"""Verify the researcher reviews exactly the text produced by the prompt renderer."""

import subprocess
import sys
from pathlib import Path

import pytest

from kinloyalty.prompts import load_prompt_library
from kinloyalty.review import build_prompt_review


ROOT = Path(__file__).resolve().parents[1]


def test_review_is_current_and_covers_every_variant() -> None:
    """Keep the checked-in artifact synchronized with the configured templates."""
    library = load_prompt_library(ROOT / "configs/study1.yaml")
    actual = build_prompt_review(library, model="claude_sonnet_5_5")
    assert actual == (ROOT / "docs/study1_prompt_review.md").read_text(encoding="utf-8")
    assert actual.count("### p") == 81
    decision_section, check_section = actual.split("## Separate comprehension prompts")
    assert decision_section.count("### p") == 63
    assert check_section.count("### p") == 18
    assert "/ human" not in check_section
    assert "All 45 decision × label × paraphrase combinations" in actual
    assert "| --- | --- | --- | --- |\n| 1 | Alex | Jordan |" in actual
    for other in ("GPT-6.1 Terra", "Gemini 4 Hydrogen", "Kimi K3.1 Pro"):
        assert actual.count(f"/ other_lab / {other}\n") == 12
    with pytest.raises(ValueError, match="Unknown model"):
        build_prompt_review(library, model="missing")


def test_offline_cli_reproduces_review_from_another_directory(tmp_path: Path) -> None:
    """Exercise the installed entry point without API keys or any provider call."""
    output = tmp_path / "review.md"
    executable = Path(sys.executable).parent / "kinloyalty"
    result = subprocess.run(
        [str(executable), "review-prompts", "--config", str(ROOT / "configs/study1.yaml"),
         "--model", "claude_sonnet_5_5", "--output", str(output)],
        cwd=tmp_path, text=True, capture_output=True, check=True,
    )
    assert "Wrote draft prompt review" in result.stdout
    assert output.read_bytes() == (ROOT / "docs/study1_prompt_review.md").read_bytes()
