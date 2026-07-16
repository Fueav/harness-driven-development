---
name: harness-driven-development
description: Use for PRDs, behavior changes, release-sensitive fixes, incidents, refactors, or deployments in repositories that declare Harness workflows or release gates.
---

# Harness Driven Development

Use this skill as a router, not as a second repository methodology.

## Start

1. Read the nearest `AGENTS.md` and child instructions.
2. Read the repository's Harness workflow document, normally `docs/harness-workflows.md`.
3. Select the lightest declared workflow that preserves the repository's contract, approvals, and release safety.
4. When drafting a Specification, delete unfilled template sections and keep only repository-specific facts.
5. Before maintaining prompts, skills, or Harness docs, find and merge duplicate definitions.
6. Follow the repository's artifacts, tests, approval rules, and release gates; use `references/checklists.md` only for the current review or closeout phase.

Repository instructions, approved specifications, API/schema contracts, runbooks, and tests define project facts. Do not restate their rules in skill-generated artifacts.

## Stop Conditions

Stop and report when:

- target behavior is ambiguous and choosing would change product, API, auth, money, data, security, or rollout semantics;
- required human approval or deployment authority is missing;
- authoritative sources conflict;
- required tests or gates fail;
- unrelated local changes would have to be overwritten, staged, or force-merged.

## Evidence Contract

The final handoff names the repository-selected workflow, changed scope, verification results, and residual risk.
