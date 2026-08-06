#!/usr/bin/env python3
"""Validate Harness Driven Development eval cases and optional results."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVALS = ROOT / "evals"
WORKFLOWS = {
    "HARNESS-FOCUSED-CHANGE",
    "HARNESS-SPEC-FIRST-FEATURE",
    "HARNESS-VERIFICATION-INCIDENT",
    "HARNESS-MAINTENANCE",
}
SKILL_FILES = (
    Path("plugins/harness-driven-development/skills/harness-driven-development/SKILL.md"),
    Path("plugins/harness-driven-development/skills/harness-driven-development/agents/openai.yaml"),
    Path("plugins/harness-driven-development/skills/harness-driven-development/references/checklists.md"),
)


def load(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def skill_package_sha256(root: Path = ROOT) -> str:
    digest = hashlib.sha256()
    for relative in SKILL_FILES:
        digest.update(relative.as_posix().encode("utf-8") + b"\0")
        digest.update((root / relative).read_bytes() + b"\0")
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path)
    parser.add_argument("--repository", type=Path)
    args = parser.parse_args()
    errors: list[str] = []
    manifest = load(EVALS / "cases.json")
    if not isinstance(manifest, dict) or set(manifest) != {"schema_version", "cases"}:
        errors.append("cases.json has an invalid contract")
        cases: list[dict] = []
    else:
        cases = manifest.get("cases", [])
        if manifest.get("schema_version") != 1 or not isinstance(cases, list):
            errors.append("cases.json must use schema version 1 and a cases array")
            cases = []
    ids: set[str] = set()
    expected_by_id: dict[str, dict] = {}
    required_case_fields = {
        "id", "scenario", "expected_workflow", "expected_decision", "active_spec_required"
    }
    for index, case in enumerate(cases):
        if not isinstance(case, dict) or not required_case_fields.issubset(case):
            errors.append(f"cases[{index}] is incomplete")
            continue
        case_id = case["id"]
        if not isinstance(case_id, str) or case_id in ids:
            errors.append(f"cases[{index}] has invalid or duplicate id")
            continue
        ids.add(case_id)
        expected_by_id[case_id] = case
        if case["expected_workflow"] is not None and case["expected_workflow"] not in WORKFLOWS:
            errors.append(f"{case_id}: expected workflow is invalid")
        if case["expected_workflow"] is None and case["expected_decision"] != "stop":
            errors.append(f"{case_id}: a missing workflow must stop")
        if case["expected_decision"] not in {"continue", "stop"}:
            errors.append(f"{case_id}: expected decision is invalid")
        if not isinstance(case["scenario"], str) or not case["scenario"].strip():
            errors.append(f"{case_id}: scenario must be non-empty")
        if not isinstance(case["active_spec_required"], bool):
            errors.append(f"{case_id}: active_spec_required must be boolean")
        phrases = case.get("verification_contains", [])
        if not isinstance(phrases, list) or any(not isinstance(item, str) or not item for item in phrases):
            errors.append(f"{case_id}: verification_contains must be strings")

    schema = load(EVALS / "result.schema.json")
    if not isinstance(schema, dict) or schema.get("type") != "object":
        errors.append("result schema is invalid")

    if args.repository:
        repository = args.repository.resolve()
        readiness = repository / "harness/repository_verification.py"
        if not readiness.is_file() or readiness.is_symlink():
            errors.append("repository readiness interface is missing")
        else:
            runtime = os.environ.copy()
            runtime["HARNESS_PROJECT_ROOT"] = str(repository)
            result = subprocess.run(
                [sys.executable, "-I", "-B", "-S", str(readiness), "ready"],
                cwd=repository, env=runtime, capture_output=True, text=True, check=False,
            )
            if result.returncode:
                errors.append("repository readiness failed: " + (result.stderr.strip() or "unknown error"))
        for relative in ("AGENTS.md", "docs/harness-workflows.md"):
            path = repository / relative
            if not path.is_file():
                errors.append(f"repository contract is missing {relative}")
        workflow_doc = repository / "docs/harness-workflows.md"
        if workflow_doc.is_file():
            text = workflow_doc.read_text(encoding="utf-8")
            for workflow in WORKFLOWS:
                if workflow not in text:
                    errors.append(f"repository workflow document is missing {workflow}")

    if args.results:
        try:
            payload = load(args.results)
        except (OSError, json.JSONDecodeError) as error:
            errors.append(f"cannot load eval results: {error}")
            payload = {}
        expected_payload_fields = {"schema_version", "skill_package_sha256", "results"}
        if not isinstance(payload, dict) or set(payload) != expected_payload_fields:
            errors.append("result payload has an invalid contract")
            results: list[dict] = []
        else:
            if payload.get("schema_version") != 1:
                errors.append("result payload has an invalid schema version")
            if payload.get("skill_package_sha256") != skill_package_sha256():
                errors.append("result payload has a stale skill package digest")
            results = payload.get("results", [])
            if not isinstance(results, list):
                errors.append("results must be an array")
                results = []
        by_id: dict[str, dict] = {}
        for result in results:
            if not isinstance(result, dict):
                errors.append("every result must be an object")
                continue
            case_id = result.get("case_id")
            if not isinstance(case_id, str) or case_id in by_id:
                errors.append("results contain an invalid or duplicate case_id")
                continue
            by_id[case_id] = result
        if set(by_id) != ids:
            errors.append("results must cover every eval case exactly once")
        required_result_fields = {
            "case_id", "workflow_class", "decision", "active_spec", "changed_scope",
            "verification", "residual_risk", "reason",
        }
        for case_id in sorted(ids & set(by_id)):
            result = by_id[case_id]
            expected = expected_by_id[case_id]
            if set(result) != required_result_fields:
                errors.append(f"{case_id}: result fields do not match the schema contract")
                continue
            if result["workflow_class"] != expected["expected_workflow"]:
                errors.append(f"{case_id}: wrong workflow class")
            if result["decision"] != expected["expected_decision"]:
                errors.append(f"{case_id}: wrong decision")
            active_spec = result["active_spec"]
            if expected["active_spec_required"] and not isinstance(active_spec, str):
                errors.append(f"{case_id}: active_spec is required")
            if not expected["active_spec_required"] and active_spec is not None:
                errors.append(f"{case_id}: active_spec must be absent")
            reason = result["reason"]
            phrase = expected.get("reason_contains")
            if not isinstance(reason, str) or (phrase and phrase.lower() not in reason.lower()):
                errors.append(f"{case_id}: reason does not identify the expected stop cause")
            for field in ("changed_scope", "verification", "residual_risk"):
                value = result[field]
                if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
                    errors.append(f"{case_id}: {field} must be an array of strings")
            if not result["verification"]:
                errors.append(f"{case_id}: verification handoff is empty")
            verification_text = " ".join(result["verification"]).lower()
            for phrase in expected.get("verification_contains", []):
                if phrase.lower() not in verification_text:
                    errors.append(f"{case_id}: verification is missing {phrase!r}")

    for error in sorted(set(errors)):
        print(f"FAIL: {error}", file=sys.stderr)
    if errors:
        return 1
    print(f"eval contract ok: {len(cases)} cases")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
