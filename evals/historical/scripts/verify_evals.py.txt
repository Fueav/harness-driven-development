#!/usr/bin/env python3
"""Compatibility command for validating executed daily-task evidence."""
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL_FILES = tuple(Path("plugins/harness-driven-development/skills/harness-driven-development") / item
                    for item in ("SKILL.md", "agents/openai.yaml"))

def skill_package_sha256(root=ROOT):
    digest = hashlib.sha256()
    for relative in SKILL_FILES:
        digest.update(relative.as_posix().encode() + b"\0" + (root / relative).read_bytes() + b"\0")
    return digest.hexdigest()

if __name__ == "__main__":
    import subprocess, sys
    raise SystemExit(subprocess.call([sys.executable, str(ROOT / "scripts/run_behavior_evals.py"), "verify", *sys.argv[1:]]))
