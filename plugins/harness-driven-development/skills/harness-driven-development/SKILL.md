---
name: harness-driven-development
description: Use for daily work inside a fully delivered Harness target repository.
---

# Harness Driven Development

Use this Skill as the target's daily router, not as a second repository methodology.

## Start

1. Read the nearest `AGENTS.md` and applicable child instructions. From the target root, run `harness/repository_verification.py ready` before routing. If missing or failing, report that Template Delivery is incomplete and direct a scaffold maintainer to explicit delivery from the canonical Scaffold Source.
2. If the request itself is a cold start or template upgrade, stop before mutation with the same handoff. Never invoke or install Harness Template Sync.
3. After readiness, consult the repository workflow document; load further authority only for the active decision.
4. Separate semantic novelty from permissions. Select the lightest declared workflow: Focused for exact corrections including approved dev config, Spec-first for new semantics or unresolved contracts, maintenance for target Harness upkeep.
5. Follow the repository's outcome tracking, recovery, and verification contract across turns. Reuse same-SHA release evidence only through `harnessctl evidence verify`. Load `references/checklists.md` only for the active phase.

## Stop Conditions

Failed gates block promotion; repair change-caused failures within authorization. Stop the affected action for missing authority, unresolved high-risk contracts, incomplete delivery, or unrelated work that would be overwritten.

## Evidence Contract

Name the workflow, completed outcome, changed scope, verification, authorized Git/deployment actions completed, and residual risk.
