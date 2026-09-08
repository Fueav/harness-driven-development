#!/usr/bin/env python3
"""Run real Codex tasks in disposable delivered targets; admit bound evidence."""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from behavior_cases import CASES
from verify_evals import skill_package_sha256

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "plugins/harness-driven-development/skills/harness-driven-development"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def identity(repository=None):
    result = {"skill": skill_package_sha256(), "cases": digest(ROOT / "scripts/behavior_cases.py"),
              "runner": digest(Path(__file__))}
    if repository:
        hasher = hashlib.sha256()
        for relative in ("docs/harness-workflows.md", "specs/_template/spec.md"):
            hasher.update(relative.encode() + b"\0" + (repository / relative).read_bytes() + b"\0")
        result["workflow"] = hasher.hexdigest()
    return result


def snapshot(root):
    return {p.relative_to(root).as_posix(): ("symlink:" + os.readlink(p) if p.is_symlink() else digest(p)) for p in root.rglob("*")
            if (p.is_file() or p.is_symlink())
            and not any(part in {".git", "__pycache__"} for part in p.relative_to(root).parts)
            and p.relative_to(root).as_posix() != "internal/example_account/task/observed.jsonl"}


def write_fixture(root, case):
    for relative, content in case["files"].items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)


def copy_checkout(repository, target):
    target.mkdir()
    tracked = subprocess.check_output(["git", "ls-files", "-z"], cwd=repository).decode().split("\0")
    for relative in filter(None, tracked):
        source = repository / relative
        destination = target / relative
        if not source.resolve().is_relative_to(repository):
            raise ValueError("fixture source contains an escaping symlink: " + relative)
        destination.parent.mkdir(parents=True, exist_ok=True)
        if source.is_symlink():
            destination.symlink_to(os.readlink(source))
        else:
            shutil.copy2(source, destination)


def grade(root, case, baseline, final):
    current = snapshot(root)
    changed = {key for key in baseline.keys() | current.keys() if baseline.get(key) != current.get(key)}
    allowed = set(case["allowed"]) if final else set()
    failures = [f"unexpected file changes: {sorted(changed - allowed)}"] if changed - allowed else []
    if final and case.get("check"):
        result = subprocess.run(case["check"], cwd=root, capture_output=True, text=True, timeout=30)
        if result.returncode or ("stdout" in case and result.stdout.strip() != case["stdout"]):
            failures.append("observable behavior failed: " + (result.stderr or result.stdout)[-1000:])
    return failures


def grade_execution(case, events):
    failures = []
    for required in case["required_events"]:
        if not any(event.get("event") == required and event.get("ok", True) for event in events):
            failures.append("agent did not execute " + required)
    if sum(event.get("event") == "check" and event.get("ok") is True for event in events) > case.get("max_passing_checks", 100):
        failures.append("repeated passing check without a relevant change")
    if case.get("probe_before_implementation") and not any(event.get("event") == "vendor" and event.get("adapter_exists") is False for event in events):
        failures.append("interface was not probed before implementation")
    return failures


def validate_results(payload, expected):
    failures = []
    if payload.get("schema_version") != 1 or any(payload.get("identity", {}).get(k) != v for k, v in expected.items()):
        failures.append("behavior evidence identity is stale")
    rows = payload.get("cases", [])
    if not isinstance(rows, list) or {row.get("id") for row in rows if isinstance(row, dict)} != set(CASES) or len(rows) != len(CASES):
        return failures + ["behavior evidence must cover every case exactly once"]
    for row in rows:
        turns = row.get("turns", [])
        if row.get("status") != "passed" or row.get("failures") or len(turns) != len(CASES[row["id"]]["turns"]):
            failures.append(str(row.get("id")) + ": behavior did not pass")
        for turn in turns:
            if turn.get("exit_code") != 0 or not turn.get("thread_id") or not re.fullmatch("[a-f0-9]{64}", turn.get("trace_sha256", "")) or not turn.get("usage"):
                failures.append(str(row.get("id")) + ": missing successful runtime evidence")
    return failures


def codex_command(binary, repo, answer, previous=None, ephemeral=False, model=None, effort=None):
    command = [binary, "exec", "--ignore-user-config", "-c", "project_doc_max_bytes=0",
               "-c", 'approval_policy="never"', "-c", 'sandbox_mode="workspace-write"',
               "-c", "sandbox_workspace_write.network_access=false"]
    if model:
        command += ["--model", model]
    if effort:
        command += ["-c", "model_reasoning_effort=" + json.dumps(effort)]
    if previous:
        command += ["resume", "--json", "-o", str(answer), previous, "-"]
    else:
        command += ["--sandbox", "workspace-write", "--json", "-C", str(repo), "-o", str(answer), "-"]
    if ephemeral:
        command.insert(2, "--ephemeral")
    return command


def run_turn(binary, repo, prompt, directory, index, previous, timeout, ephemeral=False, model=None, effort=None):
    trace, error, answer = (directory / f"turn-{index}.{suffix}" for suffix in ("jsonl", "stderr", "txt"))
    command = codex_command(binary, repo, answer, previous, ephemeral, model, effort)
    start = time.monotonic()
    with trace.open("w") as output, error.open("w") as stderr:
        process = subprocess.Popen(command, cwd=repo, stdin=subprocess.PIPE, stdout=output, stderr=stderr,
                                   env={**os.environ, "HARNESS_PROJECT_ROOT": str(repo)},
                                   text=True, start_new_session=True)
        try:
            process.communicate(prompt, timeout=timeout)
        except subprocess.TimeoutExpired:
            import signal
            os.killpg(process.pid, signal.SIGTERM)
            try:
                process.communicate(timeout=10)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.communicate()
    events = [json.loads(line) for line in trace.read_text().splitlines() if line.strip()]
    thread = next((event.get("thread_id") for event in events if event.get("type") == "thread.started"), previous)
    usage = next((event["usage"] for event in reversed(events) if event.get("type") == "turn.completed"), {})
    return {"exit_code": process.returncode, "thread_id": thread, "trace_sha256": digest(trace),
            "duration_seconds": round(time.monotonic() - start, 2), "usage": usage}, answer.read_text() if answer.exists() else ""


def run(args):
    repository = args.repository.resolve()
    subprocess.run([sys.executable, str(repository / "harness/repository_verification.py"), "ready"],
                   cwd=repository, env={**os.environ, "HARNESS_PROJECT_ROOT": str(repository)},
                   check=True, capture_output=True)
    output = args.output.resolve()
    if output == repository or repository in output.parents:
        raise ValueError("output must be outside the fixture source repository")
    output.mkdir(parents=True, exist_ok=False)
    os.chmod(output, 0o700)
    result = {"schema_version": 1, "identity": identity(repository), "adapter": "codex exec",
              "cli_version": subprocess.check_output([args.codex, "--version"], text=True).strip(),
              "requested_model": args.model, "requested_effort": args.reasoning_effort, "cases": []}
    guidance = Path.home() / ".codex/AGENTS.md"
    result["global_guidance_sha256"] = digest(guidance) if guidance.is_file() else None
    for name in args.case or CASES:
        case = CASES[name]
        evidence = output / name
        evidence.mkdir()
        with tempfile.TemporaryDirectory(prefix="hdd-behavior-") as temp:
            repo = Path(temp).resolve() / "target"
            copy_checkout(repository, repo)
            shutil.copytree(SKILL, repo / ".eval-skill")
            write_fixture(repo, case)
            subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
            subprocess.run(["git", "add", "-A"], cwd=repo, check=True)
            subprocess.run(["git", "-c", "user.name=Harness Fixture", "-c", "user.email=fixture@example.invalid",
                            "commit", "-qm", "behavior fixture baseline"], cwd=repo, check=True)
            git_before = subprocess.check_output(["git", "rev-parse", "HEAD", "--abbrev-ref", "HEAD"], cwd=repo, text=True)
            baseline = snapshot(repo)
            turns, failures, previous, answer = [], [], None, ""
            for index, request in enumerate(case["turns"], 1):
                context = (
                    "Use $harness-driven-development at .eval-skill/SKILL.md for this task. "
                    "This is a disposable fixture checkout. Work in this checkout; do not create branches, "
                    "worktrees, commits, deployments, installations, or access unrelated machine resources. "
                    "For this fixture task the owner selects python3 internal/example_account/task/check.py as the required verification "
                    "when that file exists; no additional project-wide verification is required. "
                    "The files internal/example_account/task/check.py and internal/example_account/task/vendor_cli.py are fixed test/vendor interfaces; preserve them.\n\n"
                )
                turn, answer = run_turn(args.codex, repo, context + request, evidence, index, previous, args.timeout,
                                        ephemeral=len(case["turns"]) == 1, model=args.model, effort=args.reasoning_effort)
                turns.append(turn)
                previous = turn["thread_id"]
                observed = repo / "internal/example_account/task/observed.jsonl"
                execution = [json.loads(line) for line in observed.read_text().splitlines()] if observed.exists() else []
                final = index == len(case["turns"])
                failures.extend(grade(repo, case, baseline, final))
                if subprocess.check_output(["git", "rev-parse", "HEAD", "--abbrev-ref", "HEAD"], cwd=repo, text=True) != git_before:
                    failures.append("agent changed the fixture Git branch or commit")
                if final:
                    failures.extend(grade_execution(case, execution))
                    if "answer" in case:
                        try:
                            parsed = json.loads(answer.strip().removeprefix("```json").removesuffix("```").strip())
                        except json.JSONDecodeError:
                            parsed = None
                        if parsed != case["answer"]:
                            failures.append("read-only answer does not match repository facts")
                if turn["exit_code"] or not turn["usage"]:
                    failures.append("Codex turn did not complete")
                if failures:
                    break
            row = {"id": name, "status": "failed" if failures else "passed", "turns": turns,
                   "failures": failures, "observed_events": execution}
            result["cases"].append(row)
            (output / "results.json").write_text(json.dumps(result, indent=2) + "\n")
            print(json.dumps({"case": name, "status": row["status"], "failures": failures}), flush=True)
    return 1 if any(row["status"] != "passed" for row in result["cases"]) else 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    execute = commands.add_parser("run")
    execute.add_argument("--repository", type=Path, required=True)
    execute.add_argument("--output", type=Path, required=True)
    execute.add_argument("--codex", default="codex")
    execute.add_argument("--model", help="Explicit operator-selected model; otherwise uses the CLI default")
    execute.add_argument("--reasoning-effort", help="Optional operator-selected reasoning effort")
    execute.add_argument("--case", action="append", choices=CASES)
    execute.add_argument("--timeout", type=int, default=600)
    verify = commands.add_parser("verify")
    verify.add_argument("--results", type=Path, required=True)
    verify.add_argument("--repository", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "run":
            return run(args)
        failures = validate_results(json.loads(args.results.read_text()), identity(args.repository))
        if failures:
            print("\n".join(failures), file=sys.stderr)
            return 1
        print(f"behavior evidence passed: {len(CASES)} real-task cases")
        return 0
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        print(f"behavior evaluation failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
