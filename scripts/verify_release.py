#!/usr/bin/env python3
"""Verify the cross-client Harness plugin release contract."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NAME = "harness-driven-development"
MARKETPLACE_NAME = "fueav-harness-development"
PLUGIN = ROOT / "plugins" / NAME
SKILL = PLUGIN / "skills" / NAME


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text())
    except FileNotFoundError:
        raise ValueError(f"missing {path.relative_to(ROOT)}") from None
    except json.JSONDecodeError as error:
        raise ValueError(f"invalid JSON in {path.relative_to(ROOT)}: {error}") from None


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def main() -> int:
    errors: list[str] = []
    version_path = ROOT / "VERSION"
    version = version_path.read_text().strip() if version_path.exists() else ""
    require(bool(re.fullmatch(r"\d+\.\d+\.\d+", version)), "VERSION must be strict semver", errors)

    readme_path = ROOT / "README.md"
    readme_text = readme_path.read_text() if readme_path.exists() else ""
    for command in (
        f"codex plugin marketplace add Fueav/{NAME}",
        f"codex plugin add {NAME}@{MARKETPLACE_NAME}",
        f"codex plugin remove {NAME}@{NAME}",
        f"codex plugin marketplace remove {NAME}",
        f"codex plugin marketplace upgrade {MARKETPLACE_NAME}",
        f"claude plugin update {NAME}@{MARKETPLACE_NAME}",
    ):
        require(command in readme_text, f"README must document: {command}", errors)

    paths = {
        "codex_plugin": PLUGIN / ".codex-plugin" / "plugin.json",
        "claude_plugin": PLUGIN / ".claude-plugin" / "plugin.json",
        "codex_marketplace": ROOT / ".agents" / "plugins" / "marketplace.json",
        "claude_marketplace": ROOT / ".claude-plugin" / "marketplace.json",
    }
    manifests: dict[str, dict] = {}
    for key, path in paths.items():
        try:
            manifests[key] = load_json(path)
        except ValueError as error:
            errors.append(str(error))

    for key in ("codex_plugin", "claude_plugin"):
        manifest = manifests.get(key, {})
        require(manifest.get("name") == NAME, f"{key} name must be {NAME}", errors)
        require(manifest.get("version") == version, f"{key} version must equal VERSION", errors)

    require(
        manifests.get("codex_plugin", {}).get("skills") == "./skills/",
        "Codex plugin must load ./skills/",
        errors,
    )
    require(
        manifests.get("claude_plugin", {}).get("skills") == ["./skills/"],
        "Claude plugin must load ./skills/",
        errors,
    )

    codex_entries = manifests.get("codex_marketplace", {}).get("plugins", [])
    codex_marketplace_name = manifests.get("codex_marketplace", {}).get("name")
    claude_marketplace_name = manifests.get("claude_marketplace", {}).get("name")
    require(
        codex_marketplace_name == MARKETPLACE_NAME,
        f"Codex marketplace name must be {MARKETPLACE_NAME}",
        errors,
    )
    require(
        claude_marketplace_name == MARKETPLACE_NAME,
        f"Claude marketplace name must be {MARKETPLACE_NAME}",
        errors,
    )
    require(
        codex_marketplace_name != NAME and claude_marketplace_name != NAME,
        "marketplace name must differ from plugin name",
        errors,
    )
    codex_entry = next((entry for entry in codex_entries if entry.get("name") == NAME), {})
    codex_source = codex_entry.get("source", {}).get("path")
    require(
        codex_source == f"./plugins/{NAME}",
        "Codex marketplace must point to the shared plugin directory",
        errors,
    )
    if codex_source:
        codex_plugin = (ROOT / codex_source).resolve()
        require(codex_plugin == PLUGIN.resolve(), "Codex marketplace source resolves incorrectly", errors)
        require(
            (codex_plugin / "skills" / NAME / "SKILL.md").is_file(),
            "Codex marketplace Skill entrypoint is missing",
            errors,
        )

    claude_entries = manifests.get("claude_marketplace", {}).get("plugins", [])
    claude_entry = next((entry for entry in claude_entries if entry.get("name") == NAME), {})
    claude_source = claude_entry.get("source")
    require(
        claude_source == f"./plugins/{NAME}",
        "Claude marketplace must point to the shared plugin directory",
        errors,
    )
    if claude_source:
        claude_plugin = (ROOT / claude_source).resolve()
        require(claude_plugin == PLUGIN.resolve(), "Claude marketplace source resolves incorrectly", errors)
        require(
            (claude_plugin / "skills" / NAME / "SKILL.md").is_file(),
            "Claude marketplace Skill entrypoint is missing",
            errors,
        )
    require(claude_entry.get("version") == version, "Claude marketplace version must equal VERSION", errors)

    skill_path = SKILL / "SKILL.md"
    if skill_path.exists():
        skill_text = skill_path.read_text()
        require(len(skill_text.splitlines()) <= 60, "SKILL.md exceeds 60 lines", errors)
        require(f"name: {NAME}" in skill_text, "SKILL.md name is incorrect", errors)
    else:
        errors.append("missing shared SKILL.md")

    old_references = {
        "code-review-checklist.md",
        "implementation-plan-template.md",
        "prd-audit-checklist.md",
        "release-closeout-checklist.md",
        "specification-template.md",
    }
    references = SKILL / "references"
    present_old = sorted(path.name for path in references.glob("*.md") if path.name in old_references)
    require(not present_old, f"legacy duplicate references remain: {', '.join(present_old)}", errors)

    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1

    print(f"release contract ok: {NAME} {version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
