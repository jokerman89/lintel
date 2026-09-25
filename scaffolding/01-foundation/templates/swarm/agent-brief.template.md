# Agent brief: <package-id> — <short task>

## Lintel startup

Read `AGENT-INSTRUCTIONS.md`, `CORE-PRINCIPLES.md`, current
`.claude/memory/{MEMORY,working-state,personas}.md`, recent lessons, relevant accepted ADRs, and
`docs/architecture.md`. Resolve the active pack and compliance checklist. This brief narrows
ownership; it does not replace repository authority or safety rules.

## Task

Implement `<package-id>` with all unchanged member leaf IDs from the mapped plan/tasks, in their
dependency order. Legacy ungrouped tasks are singleton packages. Follow the mapped specification
and the initiative swarm charter; this brief does not create another backlog.

## Inputs

- `<authoritative input path>`

## Ownership

Write only the lane's `write_scope` paths plus its own declared report path. Do not edit the review
path, shared plan/runtime state, manifests, generated reducers, integration history, or another
lane's paths. Stop and report if the task requires a path outside that scope.

## Acceptance

- `<observable acceptance condition>`

## Report

Write the lane's report from `agent-report.template.md`. List exact changed paths, checks/results,
findings, limitations, and downstream notes. Bind the current attempt/source/result using
`li-swarm.py snapshot` and include acceptance evidence for every member leaf. Do not mark shared
plan state complete, invent a changed file for verification-only work, or author your own review.

Local v2 observations do not grant shared acceptance. The coordinator owns externally prepared
P05 v2 context/QA, the P07 reference and any P09 request; do not write those pointers or synthesize
independent corroboration. Preserve raw reports/results for final external preparation and actual
review. No-domain work uses ordinary P05 QA. A domain result remains non-clearing observation data.
