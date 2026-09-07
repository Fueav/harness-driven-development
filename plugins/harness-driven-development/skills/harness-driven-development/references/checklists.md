# Harness Checklists

Load only the section needed for the current phase.

## Requirement Audit

- Resolve only missing decisions that change the requested result, compatibility, ownership, or authority. Use the relevant contract and evidence; routine assumptions need no audit checklist.

## Review

- Lead with reachable defects caused by the change, their trigger, impact, and evidence. Inspect related compatibility, money, concurrency, or operational invariants only where the change can affect them.
- Distinguish verified failures from hypotheses; report material gaps and a ready, needs fixes, or blocked verdict.

## Closeout

- Compare the actual outcome with the request. Finish remaining authorized validation and change-caused fixes before handoff; follow the repository's profiles and branch rules.
- If deployment was requested, prove target lineage, deployed revision, and changed behavior with the documented smoke checks. Git integration alone proves no deployment.
- Report exact evidence and any remaining blocked operation; keep unrelated files out of commits.
