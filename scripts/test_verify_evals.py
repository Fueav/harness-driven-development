#!/usr/bin/env python3
"""Regression tests for Harness Driven Development eval validation."""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL_FILES = (
    Path("plugins/harness-driven-development/skills/harness-driven-development/SKILL.md"),
    Path("plugins/harness-driven-development/skills/harness-driven-development/agents/openai.yaml"),
    Path("plugins/harness-driven-development/skills/harness-driven-development/references/checklists.md"),
)


def skill_package_sha256(root: Path) -> str:
    digest = hashlib.sha256()
    for relative in SKILL_FILES:
        digest.update(relative.as_posix().encode("utf-8") + b"\0")
        digest.update((root / relative).read_bytes() + b"\0")
    return digest.hexdigest()


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
            "schema_version": 1,
            "skill_package_sha256": skill_package_sha256(checkout),
            "results": [
                {
                    "case_id": case["id"],
                    "workflow_class": case["expected_workflow"],
                    "decision": case["expected_decision"],
                    "active_spec": "specs/module/spec.md" if case["active_spec_required"] else None,
                    "changed_scope": ["declared task scope"],
                    "verification": case.get("verification_contains", ["repository gate"]),
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

    def test_covers_incomplete_delivery_and_upgrade_handoff(self) -> None:
        ids = {
            case["id"]
            for case in json.loads((ROOT / "evals/cases.json").read_text())["cases"]
        }
        self.assertTrue(
            {"incomplete-template-delivery", "template-upgrade-request"}.issubset(ids)
        )

    def test_repository_check_runs_the_readiness_interface(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repository = Path(temp_dir)
            (repository / "docs").mkdir()
            (repository / "AGENTS.md").write_text("docs/harness-workflows.md\n")
            (repository / "docs/harness-workflows.md").write_text(
                "\n".join(sorted({
                    "HARNESS-FOCUSED-CHANGE", "HARNESS-SPEC-FIRST-FEATURE",
                    "HARNESS-VERIFICATION-INCIDENT", "HARNESS-MAINTENANCE",
                })) + "\n"
            )
            result = self.run_validator(ROOT, "--repository", str(repository))
            output = result.stdout + result.stderr
            self.assertNotEqual(result.returncode, 0, output)
            self.assertIn("repository readiness", output.lower())

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

    def test_rejects_stale_skill_package_results(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            checkout = self.copy_checkout(temp_dir)
            payload = self.valid_results(checkout)
            skill = checkout / "plugins/harness-driven-development/skills/harness-driven-development/SKILL.md"
            skill.write_text(skill.read_text() + "\n")
            path = checkout / "results.json"
            path.write_text(json.dumps(payload) + "\n")
            result = self.run_validator(checkout, "--results", str(path))
            output = result.stdout + result.stderr
            self.assertNotEqual(result.returncode, 0, output)
            self.assertIn("stale skill package digest", output)


if __name__ == "__main__":
    unittest.main()
