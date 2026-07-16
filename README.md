# Harness Driven Development

`harness-driven-development` routes repository work through the lightest declared Harness workflow that preserves the repository's contracts, approvals, and release gates.

## Install in Codex

```bash
codex plugin marketplace add Fueav/harness-driven-development
codex plugin add harness-driven-development@fueav-harness-development
```

## Install in Claude Code

```bash
claude plugin marketplace add Fueav/harness-driven-development
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
claude plugin marketplace remove harness-driven-development
claude plugin marketplace add Fueav/harness-driven-development
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
```

## Roll back to v1

Remove the v2 plugin and marketplace, then add `Fueav/harness-driven-development` with `--ref harness-driven-development--v1.0.0` in Codex or the equivalent pinned marketplace source in Claude Code. Published tags are immutable.
