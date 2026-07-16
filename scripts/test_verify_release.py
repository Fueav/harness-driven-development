#!/usr/bin/env python3
"""Regression tests for the Harness Driven Development release validator."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NAME = "harness-driven-development"
MARKETPLACES = (
    Path(".agents/plugins/marketplace.json"),
    Path(".claude-plugin/marketplace.json"),
)


class ReleaseValidatorTests(unittest.TestCase):
    def test_rejects_marketplace_name_equal_to_plugin_name(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            checkout = Path(temp_dir) / "checkout"
            shutil.copytree(ROOT, checkout, ignore=shutil.ignore_patterns(".git", "__pycache__"))
            for relative_path in MARKETPLACES:
                path = checkout / relative_path
                document = json.loads(path.read_text())
                document["name"] = NAME
                path.write_text(json.dumps(document, indent=2) + "\n")

            result = subprocess.run(
                [sys.executable, "scripts/verify_release.py"],
                cwd=checkout,
                capture_output=True,
                text=True,
                check=False,
            )

            output = result.stdout + result.stderr
            self.assertNotEqual(result.returncode, 0, output)
            self.assertIn("marketplace name must differ from plugin name", output)


if __name__ == "__main__":
    unittest.main()
