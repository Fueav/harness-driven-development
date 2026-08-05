---
name: harness-driven-development
description: Use for PRDs, behavior changes, release-sensitive fixes, incidents, refactors, or deployments in repositories that declare Harness workflows or release gates.
---

# Harness Driven Development

Use this skill as a router, not as a second repository methodology.

## Start

1. Read the nearest `AGENTS.md` and child instructions.
2. Read the repository's Harness workflow document, usually `docs/harness-workflows.md`.
3. Separate semantic novelty from approval, protected paths, deployment, or security; those controls alone never require a Specification.
4. Select the lightest declared workflow. Use Focused for an exact correction, including approved dev config; use Spec-first only for new semantics or unresolved contract ambiguity.
5. Select verification: run changed-path gates, one full release for a final SHA when required, then `harnessctl evidence verify` for reuse.
6. Keep Specifications repository-specific and remove unfilled template sections. Before Harness maintenance, merge duplicate definitions.
7. Follow repository artifacts, tests, approvals, release gates, and runbooks; load `references/checklists.md` only for that phase.

Repository instructions, approved specifications, contracts, runbooks, and tests define project facts. Do not restate them in generated artifacts.

## Stop Conditions

Stop and report when:

- target behavior is ambiguous and choosing would change product, API, auth, money, data, security, or rollout semantics;
- required human approval or deployment authority is missing;
- authoritative sources conflict;
- required tests or gates fail;
- unrelated local changes would have to be overwritten, staged, or force-merged.

## Evidence Contract

The final handoff names the repository-selected workflow, changed scope, verification results, and residual risk.
