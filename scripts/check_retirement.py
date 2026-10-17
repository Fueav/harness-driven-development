"""Check retirement and preservation; do not execute the archived plugin."""

from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]
HISTORICAL = "4c1daa9600f10a0d703ae20c34bd994d407ea2b9"
RETIRED = (
    ".agents/plugins", ".claude-plugin", ".codex-plugin", "plugins", "skills",
    "VERSION", "contracts", "scripts/behavior_cases.py",
    "scripts/run_behavior_evals.py", "scripts/test_behavior_evals.py",
    "scripts/test_verify_release.py", "scripts/verify_evals.py",
    "scripts/verify_release.py",
)
ARCHIVES = {
    "evals/behavior-results.json": "evals/behavior-results.json",
    "evals/historical/VERSION": "VERSION",
    "evals/historical/contracts/suite-compatibility.json": "contracts/suite-compatibility.json",
    **{
        f"evals/historical/scripts/{name}.py.txt": f"scripts/{name}.py"
        for name in (
            "behavior_cases", "run_behavior_evals", "test_behavior_evals",
            "test_verify_release", "verify_evals", "verify_release",
        )
    },
}


def main():
    for name in RETIRED:
        if (ROOT / name).exists():
            raise SystemExit(f"Retired entrypoint exists: {name}")
    workflows = {path.name for path in (ROOT / ".github/workflows").iterdir()}
    if workflows != {"retirement.yml"}:
        raise SystemExit(f"Unexpected active workflows: {sorted(workflows)}")
    for archived, original in ARCHIVES.items():
        expected = subprocess.check_output(
            ["git", "show", f"{HISTORICAL}:{original}"], cwd=ROOT
        )
        path = ROOT / archived
        if path.is_symlink() or path.read_bytes() != expected:
            raise SystemExit(f"Historical evidence changed: {archived}")
        if path.stat().st_mode & 0o111:
            raise SystemExit(f"Historical evidence is executable: {archived}")
    print(f"PASS: retired entrypoints absent; {len(ARCHIVES)} historical files preserved")


if __name__ == "__main__":
    main()
