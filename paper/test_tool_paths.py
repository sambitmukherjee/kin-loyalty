"""Check portable executable discovery without invoking external programs."""

import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tool_paths import poppler_tool


class ToolPathsTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name).resolve()
        self.environment = patch.dict(os.environ, {"PATH": ""}, clear=True)
        self.environment.start()

    def tearDown(self):
        self.environment.stop()
        self.temporary.cleanup()

    def executable(self, directory, name="pdftotext"):
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / name
        path.write_text("#!/bin/sh\nexit 0\n")
        path.chmod(0o700)
        return path

    def test_path_lookup(self):
        expected = self.executable(self.root / "standard bin")
        os.environ["PATH"] = str(expected.parent)
        self.assertEqual(poppler_tool("pdftotext"), str(expected))

    def test_directory_override_precedes_path(self):
        fallback = self.executable(self.root / "path")
        expected = self.executable(self.root / "override")
        os.environ.update(PATH=str(fallback.parent), PAPER_POPPLER_BIN=str(expected.parent))
        self.assertEqual(poppler_tool("pdftotext"), str(expected))

    def test_command_override_precedes_directory(self):
        fallback = self.executable(self.root / "group")
        expected = self.executable(self.root / "custom bin", "custom-pdftotext")
        os.environ.update(PAPER_POPPLER_BIN=str(fallback.parent), PDFTOTEXT=str(expected))
        self.assertEqual(poppler_tool("pdftotext"), str(expected))

    def test_relative_directory_override(self):
        expected = self.executable(self.root / "relative")
        os.environ["PAPER_POPPLER_BIN"] = "relative"
        with patch("os.getcwd", return_value=str(self.root)):
            self.assertEqual(poppler_tool("pdftotext"), str(expected))

    def test_relative_command_override(self):
        expected = self.executable(self.root)
        os.environ["PDFTOTEXT"] = "./pdftotext"
        with patch("os.getcwd", return_value=str(self.root)):
            self.assertEqual(poppler_tool("pdftotext"), str(expected))

    def test_bad_explicit_override_does_not_use_path(self):
        fallback = self.executable(self.root / "path")
        os.environ.update(PATH=str(fallback.parent), PDFTOTEXT=str(self.root / "missing"))
        with self.assertRaisesRegex(FileNotFoundError, "PDFTOTEXT"):
            poppler_tool("pdftotext")

    def test_non_executable_file_is_rejected(self):
        candidate = self.root / "pdftotext"
        candidate.write_text("not executable")
        os.environ["PDFTOTEXT"] = str(candidate)
        with self.assertRaises(FileNotFoundError):
            poppler_tool("pdftotext")

    def test_missing_tool_has_installation_guidance(self):
        with self.assertRaisesRegex(FileNotFoundError, "Install Poppler"):
            poppler_tool("pdftotext")

    def test_unknown_tool_is_rejected(self):
        with self.assertRaises(ValueError):
            poppler_tool("unrelated-command")


if __name__ == "__main__":
    unittest.main()
