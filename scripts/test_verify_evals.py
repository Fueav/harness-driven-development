#!/usr/bin/env python3
"""Regression tests for Harness Driven Development eval validation."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class EvalContractTests(unittest.TestCase):
    def run_validator(self, checkout: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "scripts/verify_evals.py", *args],
            cwd=checkout,
            capture_output=True,
            text=True,
            check=False,
        )

    def copy_checkout(self, temp_dir: str) -> Path:
        checkout = Path(temp_dir) / "checkout"
        shutil.copytree(ROOT, checkout, ignore=shutil.ignore_patterns(".git", "__pycache__"))
        return checkout

    def valid_results(self, checkout: Path) -> dict:
        cases = json.loads((checkout / "evals/cases.json").read_text())["cases"]
        return {
            "results": [
                {
                    "case_id": case["id"],
                    "workflow_class": case["expected_workflow"],
                    "decision": case["expected_decision"],
                    "active_spec": "specs/module/spec.md" if case["active_spec_required"] else None,
                    "changed_scope": ["declared task scope"],
                    "verification": ["repository gate"],
                    "residual_risk": ["none identified"],
                    "reason": case.get("reason_contains", "repository contract"),
                }
                for case in cases
            ]
        }

    def test_accepts_complete_results(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            checkout = self.copy_checkout(temp_dir)
            path = checkout / "results.json"
            path.write_text(json.dumps(self.valid_results(checkout)) + "\n")
            result = self.run_validator(checkout, "--results", str(path))
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_rejects_wrong_route(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            checkout = self.copy_checkout(temp_dir)
            payload = self.valid_results(checkout)
            payload["results"][0]["workflow_class"] = "HARNESS-MAINTENANCE"
            path = checkout / "results.json"
            path.write_text(json.dumps(payload) + "\n")
            result = self.run_validator(checkout, "--results", str(path))
            output = result.stdout + result.stderr
            self.assertNotEqual(result.returncode, 0, output)
            self.assertIn("wrong workflow class", output)

    def test_rejects_missing_active_spec(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            checkout = self.copy_checkout(temp_dir)
            payload = self.valid_results(checkout)
            target = next(item for item in payload["results"] if item["case_id"] == "api-semantic-change")
            target["active_spec"] = None
            path = checkout / "results.json"
            path.write_text(json.dumps(payload) + "\n")
            result = self.run_validator(checkout, "--results", str(path))
            output = result.stdout + result.stderr
            self.assertNotEqual(result.returncode, 0, output)
            self.assertIn("active_spec is required", output)

    def test_rejects_missing_stop_reason(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            checkout = self.copy_checkout(temp_dir)
            payload = self.valid_results(checkout)
            target = next(item for item in payload["results"] if item["case_id"] == "failed-gate")
            target["reason"] = "cannot proceed"
            path = checkout / "results.json"
            path.write_text(json.dumps(payload) + "\n")
            result = self.run_validator(checkout, "--results", str(path))
            output = result.stdout + result.stderr
            self.assertNotEqual(result.returncode, 0, output)
            self.assertIn("expected stop cause", output)


if __name__ == "__main__":
    unittest.main()
