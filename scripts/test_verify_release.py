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
PLUGIN_MANIFESTS = (
    (Path("plugins/harness-driven-development/.codex-plugin/plugin.json"), "./missing/"),
    (Path("plugins/harness-driven-development/.claude-plugin/plugin.json"), ["./missing/"]),
)


class ReleaseValidatorTests(unittest.TestCase):
    def run_validator(self, checkout: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "scripts/verify_release.py"],
            cwd=checkout,
            capture_output=True,
            text=True,
            check=False,
        )

    def copy_checkout(self, temp_dir: str) -> Path:
        checkout = Path(temp_dir) / "checkout"
        shutil.copytree(ROOT, checkout, ignore=shutil.ignore_patterns(".git", "__pycache__"))
        return checkout

    def test_rejects_marketplace_name_equal_to_plugin_name(self) -> None:
        for relative_path in MARKETPLACES:
            with self.subTest(relative_path=relative_path), tempfile.TemporaryDirectory() as temp_dir:
                checkout = self.copy_checkout(temp_dir)
                path = checkout / relative_path
                document = json.loads(path.read_text())
                document["name"] = NAME
                path.write_text(json.dumps(document, indent=2) + "\n")

                result = self.run_validator(checkout)
                output = result.stdout + result.stderr
                self.assertNotEqual(result.returncode, 0, output)
                self.assertIn("marketplace name must differ from plugin name", output)

    def test_rejects_plugin_directory_symlink_outside_repository(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            checkout = self.copy_checkout(temp_dir)
            plugin = checkout / "plugins" / NAME
            external_plugin = Path(temp_dir) / "external-plugin"
            shutil.move(plugin, external_plugin)
            plugin.symlink_to(external_plugin, target_is_directory=True)

            result = self.run_validator(checkout)
            output = result.stdout + result.stderr
            self.assertNotEqual(result.returncode, 0, output)
            self.assertIn("marketplace source must stay within repository", output)

    def test_rejects_invalid_declared_skills_path(self) -> None:
        for relative_path, invalid_skills in PLUGIN_MANIFESTS:
            with self.subTest(relative_path=relative_path), tempfile.TemporaryDirectory() as temp_dir:
                checkout = self.copy_checkout(temp_dir)
                path = checkout / relative_path
                document = json.loads(path.read_text())
                document["skills"] = invalid_skills
                path.write_text(json.dumps(document, indent=2) + "\n")

                result = self.run_validator(checkout)
                output = result.stdout + result.stderr
                self.assertNotEqual(result.returncode, 0, output)
                self.assertIn("declared Skill path is invalid", output)


if __name__ == "__main__":
    unittest.main()
