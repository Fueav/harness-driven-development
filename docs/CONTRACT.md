# Harness Driven Development Contract

Status: v3.0 release contract

## Decision

Harness Driven Development is the only Skill needed for normal work inside a delivered Target Repository. It routes product changes, incidents, reviews, refactors, releases, deployments, and target Harness maintenance through the lightest repository-declared workflow after the target proves its Repository Contract is ready.

It does not cold-start or upgrade a repository. Harness Template Sync is an independent one-shot delivery peer that a scaffold maintainer invokes from the exact canonical Scaffold Source root. The plugins never contain, install, invoke, or coordinate one another.

## Entry contract

Before reading task-routing policy, run target-local `harness/repository_verification.py ready` from the repository root.

- Success proves a supported suite contract, required files and executables, schema versions, current scaffold record, semantic path resolutions, managed symlinks, and retired-path absence.
- A missing command or any failure stops routing. Report the exact readiness error and ask a scaffold maintainer to initiate an explicit Template Delivery from the canonical Scaffold Source.
- A cold-start or template-upgrade request made inside the target also stops before mutation with the same handoff. Do not invoke Harness Template Sync on the user's behalf.

Readiness is target-local and does not need the template checkout or either plugin. It protects the delivery-to-daily-work seam without introducing a runtime package dependency.

## Daily routing

After readiness:

1. Read nearest `AGENTS.md`, child instructions, the repository Harness workflow document, and task-relevant authority.
2. Separate semantic novelty from approval, protected paths, security, deployment, or file type. Those independent controls do not choose the workflow.
3. Select the lightest declared workflow. New or intentionally changed semantics and unresolved contract ambiguity use the repository's Spec-first route; exact restoration and behavior-preserving work use its focused route.
4. Follow target tests, gates, approvals, branch rules, runbooks, and deployment authority. Harness maintenance remains target work and uses the declared maintenance route.
5. Close out with the selected workflow, changed scope, exact verification, Git/deployment actions actually authorized and completed, and residual risk.

Repository artifacts own project facts. The Skill contains routing and stop conditions, not a second methodology or copied target policy.

## Distribution

This repository independently publishes one plugin with its own semver, tags, GitHub releases, evals, and per-repository marketplaces. It declares supported handoff versions in `contracts/suite-compatibility.json`. The recommended target-developer onboarding uses the `fueav-harness` umbrella marketplace but installs only this plugin.
