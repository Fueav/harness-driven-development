# Harness Driven Development

Daily work uses repository instructions directly. `harness-driven-development` is an optional, explicit-only compatibility entrypoint for existing invocations. It adds no readiness audit or workflow classification.

## Install in Codex

```bash
codex plugin marketplace add Fueav/harness-plugins
codex plugin add harness-driven-development@fueav-harness
```

## Install in Claude Code

```bash
claude plugin marketplace add Fueav/harness-plugins --scope user
claude plugin install harness-driven-development@fueav-harness --scope user
```

Installation is optional for daily work. Template Sync is independently available for explicit source-side delivery.

## Use

Work in the target repository and ask naturally:

```text
Use $harness-driven-development to implement this target-repository task.
```

The skill follows project instructions and relevant checks. Missing or stale delivery records do not block independent work.

## Upgrade

```bash
codex plugin marketplace upgrade fueav-harness
codex plugin add harness-driven-development@fueav-harness
claude plugin marketplace update fueav-harness
claude plugin update harness-driven-development@fueav-harness
```

## Migrate from an older marketplace

Codex:

```bash
codex plugin remove harness-driven-development@harness-driven-development
codex plugin remove harness-driven-development@fueav-harness-development
codex plugin marketplace remove harness-driven-development
codex plugin marketplace remove fueav-harness-development
codex plugin marketplace add Fueav/harness-plugins
codex plugin add harness-driven-development@fueav-harness
```

Claude Code:

```bash
claude plugin uninstall harness-driven-development@fueav-harness-development --scope user
claude plugin marketplace remove harness-driven-development --scope user
claude plugin marketplace remove fueav-harness-development --scope user
claude plugin marketplace add Fueav/harness-plugins --scope user
claude plugin install harness-driven-development@fueav-harness --scope user
```

The per-repository `fueav-harness-development` marketplace remains independently published, but the umbrella path is the supported default onboarding.

## Verify a source checkout

```bash
python3 scripts/test_verify_release.py
python3 scripts/verify_release.py
python3 scripts/test_behavior_evals.py
python3 scripts/run_behavior_evals.py run --repository /path/to/harness-target --output /path/to/new-evidence-directory
CODEX_PYTHON="${CODEX_PYTHON:-python3}"
"$CODEX_PYTHON" "${CODEX_HOME:-$HOME/.codex}/skills/.system/plugin-creator/scripts/validate_plugin.py" plugins/harness-driven-development
"$CODEX_PYTHON" "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" plugins/harness-driven-development/skills/harness-driven-development
claude plugin validate plugins/harness-driven-development --strict
claude plugin validate . --strict
```

After successful real-task evaluation, copy its results.json to evals/behavior-results.json. Release validation checks its Skill/runner/case identity; Scaffold Source suite verification also checks the evaluated workflow identity. Results include trace digests, observations, and usage; this is a regression sample, not a guarantee across future models. See [`docs/CONTRACT.md`](docs/CONTRACT.md).
