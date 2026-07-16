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


def validate_declared_skill_path(
    manifest: dict,
    label: str,
    expected: str | list[str],
    errors: list[str],
) -> None:
    declared = manifest.get("skills")
    valid = declared == expected
    require(valid, f"{label} declared Skill path is invalid", errors)
    if not valid:
        return

    relative = declared if isinstance(declared, str) else declared[0]
    declared_root = PLUGIN / relative
    try:
        resolved_root = declared_root.resolve(strict=True)
        resolved_plugin = PLUGIN.resolve(strict=True)
    except OSError:
        errors.append(f"{label} declared Skill path is invalid")
        return

    skill_entry = resolved_root / NAME / "SKILL.md"
    require(
        resolved_root.is_relative_to(resolved_plugin)
        and skill_entry.is_file()
        and skill_entry.resolve().is_relative_to(resolved_plugin),
        f"{label} declared Skill path is invalid",
        errors,
    )


def validate_marketplace_source(source: object, label: str, errors: list[str]) -> None:
    expected = f"./plugins/{NAME}"
    require(source == expected, f"{label} marketplace source is wrong", errors)
    if source != expected:
        return

    source_path = ROOT / expected
    try:
        resolved_root = ROOT.resolve(strict=True)
        resolved_source = source_path.resolve(strict=True)
    except OSError:
        errors.append(f"{label} marketplace source is missing")
        return

    require(
        not source_path.is_symlink()
        and resolved_source.is_relative_to(resolved_root)
        and resolved_source.is_dir(),
        f"{label} marketplace source must stay within repository",
        errors,
    )


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
        f"claude plugin marketplace remove {NAME} --scope user",
        f"claude plugin marketplace add Fueav/{NAME} --scope user",
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

    validate_declared_skill_path(manifests.get("codex_plugin", {}), "Codex plugin", "./skills/", errors)
    validate_declared_skill_path(manifests.get("claude_plugin", {}), "Claude plugin", ["./skills/"], errors)

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
    validate_marketplace_source(codex_source, "Codex", errors)

    claude_entries = manifests.get("claude_marketplace", {}).get("plugins", [])
    claude_entry = next((entry for entry in claude_entries if entry.get("name") == NAME), {})
    claude_source = claude_entry.get("source")
    validate_marketplace_source(claude_source, "Claude", errors)
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
