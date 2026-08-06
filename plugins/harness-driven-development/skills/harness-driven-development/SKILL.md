---
name: harness-driven-development
description: Use for daily work inside a fully delivered Harness target repository.
---

# Harness Driven Development

Use this Skill as the target's daily router, not as a second repository methodology.

## Start

1. From the target root, run `harness/repository_verification.py ready` before routing. If it is missing or fails, stop and report that Template Delivery is incomplete; direct a scaffold maintainer to start an explicit delivery from the canonical Scaffold Source.
2. If the request itself is a cold start or template upgrade, stop before mutation with the same handoff. Never invoke or install Harness Template Sync.
3. Read the nearest `AGENTS.md`, child instructions, and the repository's Harness workflow document.
4. Separate semantic novelty from approval, protected paths, deployment, or security; those controls alone never require a Specification.
5. Select the lightest declared workflow. Use Focused for an exact correction, including approved dev config; use Spec-first only for new semantics or unresolved contract ambiguity.
6. Select proportional verification; reuse same-SHA evidence only through `harnessctl evidence verify`.
7. Follow repository artifacts, tests, approvals, gates, branch rules, and runbooks. Load `references/checklists.md` only for the active phase.

Target Harness maintenance is normal daily work and uses its declared maintenance workflow.

## Stop Conditions

Stop on ambiguous high-risk semantics, missing approval or authority, conflicting sources, failed gates, incomplete Template Delivery, or unrelated changes that would be overwritten or staged.

## Evidence Contract

Name the selected workflow, changed scope, exact verification, authorized Git or deployment actions completed, and residual risk.
