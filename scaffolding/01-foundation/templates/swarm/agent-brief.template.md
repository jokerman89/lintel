# Agent brief: <task-id> — <short task>

## Lintel startup

Read `AGENT-INSTRUCTIONS.md`, `CORE-PRINCIPLES.md`, current
`.claude/memory/{MEMORY,working-state,personas}.md`, recent lessons, relevant accepted ADRs, and
`docs/architecture.md`. Resolve the active pack and compliance checklist. This brief narrows
ownership; it does not replace repository authority or safety rules.

## Task

Implement `<task-id>` verbatim from the mapped task artifact. Follow the mapped specification and
the initiative swarm charter.

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
findings, limitations, and downstream notes. Do not mark shared plan state complete.
