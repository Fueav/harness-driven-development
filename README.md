# Harness Driven Development

`harness-driven-development` routes repository work through the lightest declared Harness workflow that preserves the repository's contracts, approvals, and release gates.

## Install in Codex

```bash
codex plugin marketplace add Fueav/harness-driven-development
codex plugin add harness-driven-development@fueav-harness-development
```

## Install in Claude Code

```bash
claude plugin marketplace add Fueav/harness-driven-development --scope user
claude plugin install harness-driven-development@fueav-harness-development --scope user
```

## Migrate from v1

Version 2 separates the marketplace identity from the plugin identity. The marketplace cannot be renamed in place, so remove the v1 selector and add the repository again.

For Codex:

```bash
codex plugin remove harness-driven-development@harness-driven-development
codex plugin marketplace remove harness-driven-development
codex plugin marketplace add Fueav/harness-driven-development
codex plugin add harness-driven-development@fueav-harness-development
```

For Claude Code:

```bash
claude plugin uninstall harness-driven-development@harness-driven-development --scope user
claude plugin marketplace remove harness-driven-development --scope user
claude plugin marketplace add Fueav/harness-driven-development --scope user
claude plugin install harness-driven-development@fueav-harness-development --scope user
```

Restart the client or open a new session after migration.

## Upgrade

```bash
codex plugin marketplace upgrade fueav-harness-development
codex plugin add harness-driven-development@fueav-harness-development
claude plugin marketplace update fueav-harness-development
claude plugin update harness-driven-development@fueav-harness-development
```

## Verify a source checkout

```bash
python3 scripts/test_verify_release.py
python3 scripts/verify_release.py
python3 scripts/test_verify_evals.py
python3 scripts/verify_evals.py --repository /path/to/harness-repository
CODEX_PYTHON="${CODEX_PYTHON:-python3}"
CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
"$CODEX_PYTHON" "$CODEX_HOME/skills/.system/plugin-creator/scripts/validate_plugin.py" plugins/harness-driven-development
"$CODEX_PYTHON" "$CODEX_HOME/skills/.system/skill-creator/scripts/quick_validate.py" plugins/harness-driven-development/skills/harness-driven-development
claude plugin validate plugins/harness-driven-development --strict
claude plugin validate . --strict
```

`CODEX_PYTHON` must point to a Python environment with PyYAML for the Codex plugin validator. Eval validation is deterministic and local; external model execution is deliberately not bundled in this repository.

## Roll back to v1

For Codex:

```bash
codex plugin remove harness-driven-development@fueav-harness-development
codex plugin marketplace remove fueav-harness-development
codex plugin marketplace add Fueav/harness-driven-development --ref harness-driven-development--v1.0.0
codex plugin add harness-driven-development@harness-driven-development
```

For Claude Code:

```bash
claude plugin uninstall harness-driven-development@fueav-harness-development --scope user
claude plugin marketplace remove fueav-harness-development --scope user
claude plugin marketplace add Fueav/harness-driven-development@harness-driven-development--v1.0.0 --scope user
claude plugin install harness-driven-development@harness-driven-development --scope user
```

Published tags are immutable.
