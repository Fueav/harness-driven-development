# Harness Driven Development

`harness-driven-development` is the only plugin target developers need for normal work in a fully delivered Harness repository. It verifies the target-local handoff first, then routes product work, incidents, maintenance, releases, and deployments through the lightest declared workflow.

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

Target developers install only this plugin. Scaffold maintainers additionally install Harness Template Sync, but the two plugins remain independently released and never call or install one another.

## Use

Work in the target repository and ask naturally:

```text
Use $harness-driven-development to implement this target-repository task.
```

The Skill reads applicable repository instructions, then runs `harness/repository_verification.py ready` before routing. Missing or failed readiness, or a request for template cold start or upgrade, stops target mutation and hands off to a scaffold maintainer at the canonical Scaffold Source. It never invokes Harness Template Sync.

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
python3 scripts/test_verify_evals.py && python3 scripts/test_behavior_evals.py
python3 scripts/run_behavior_evals.py run --repository /path/to/delivered-harness-target --output /path/to/new-evidence-directory
CODEX_PYTHON="${CODEX_PYTHON:-python3}"
CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
"$CODEX_PYTHON" "$CODEX_HOME/skills/.system/plugin-creator/scripts/validate_plugin.py" plugins/harness-driven-development
"$CODEX_PYTHON" "$CODEX_HOME/skills/.system/skill-creator/scripts/quick_validate.py" plugins/harness-driven-development/skills/harness-driven-development
claude plugin validate plugins/harness-driven-development --strict
claude plugin validate . --strict
```

After successful real-task evaluation, copy its results.json to evals/behavior-results.json. Release validation checks its Skill/runner/case identity; Scaffold Source suite verification also checks the evaluated workflow identity. Results include trace digests, observations, and usage; this is a regression sample, not a guarantee across future models. See [`docs/CONTRACT.md`](docs/CONTRACT.md).

## Roll back to v2

Use the immutable `harness-driven-development--v2.1.0` tag through the standalone repository marketplace if the v3 readiness contract is not yet available. Published tags are immutable.
