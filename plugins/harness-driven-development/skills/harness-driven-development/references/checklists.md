# Harness Checklists

Load only the section needed for the current phase.

## Requirement Audit

- Identify the user or operator workflow, target baseline, governing contract, ownership, permissions, data lifecycle, compatibility, and operational impact.
- Resolve high-risk gaps for empty/error/retry/timeout/duplicate/partial-failure states before drafting a behavior-changing contract.
- Separate covered facts, missing decisions, conflicts, low-risk assumptions, and the evidence that will prove the change.

## Review

- Lead with defects: behavioral regressions, broken contracts, hidden product decisions, missing tests, and operational risk.
- Check public API/auth/identity compatibility, exact numeric types, additive migration safety, projection/cache consistency, retries/concurrency/idempotency, and performance-sensitive paths when relevant.
- Confirm primary, edge, and compatibility paths are tested and docs match final behavior.
- Confirm no unrelated files, generated artifacts, or scratch notes are staged.
- Report findings by severity, open questions, verification gaps, residual risk, and a verdict of ready, needs fixes, or blocked.

## Closeout

- Inspect status and diff; stage only task files.
- Run focused verification and the repository's required Harness/release gate with fresh output.
- Commit, push, merge, or deploy only within the user's authorization and repository branch rules.
- For deployment, verify target lineage and deployed revision, then run documented health and behavior smoke checks.
- Report artifact path when applicable, branch/commit actions actually completed, commands and results, deployment evidence, and residual risk.
