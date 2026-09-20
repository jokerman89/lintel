# Agent brief: BC2 — swarm contract and deterministic gates

## Lintel startup

Read `AGENT-INSTRUCTIONS.md`, `scaffolding/01-foundation/CORE-PRINCIPLES.md`, current
`.claude/memory/{MEMORY,working-state,personas}.md`, recent lessons, relevant accepted ADRs, and
`docs/architecture.md`. Resolve the active pack and apply the repository compliance checklist.
This brief narrows your ownership; it does not replace repository authority or safety rules.

## Task

Implement BC2 verbatim from [../../plan.md](../../plan.md), using [../../spec.md](../../spec.md)
and [../charter.md](../charter.md). Create the shared schema, stdlib validator/CLI, templates, and
focused unit tests.

## Inputs

- `bin/li-work-artifacts.py`
- `skills/spec-kit/references/work-map.md`
- `lib/envelope-schema.yaml`
- `scaffolding/01-foundation/templates/plan/`

## Ownership

Write only the BC2 `write_scope` paths in `coordination.json`, plus BC2's own declared `report`
path. Do not write BC2's `review` path. Do not edit work.json, plan checkboxes, runtime state,
manifests, generated files, or another lane's paths.

## Acceptance

- Old work-map fixtures remain valid.
- Unsafe paths, duplicate task IDs, missing briefs, same-wave scope overlap, out-of-scope changed
  paths, and incomplete close evidence fail closed.
- The current initiative's coordination map validates.
- Code is Python standard-library only and does not execute artifact content.

## Report

Write `../reports/BC2.md` from the agent-report template with changed files, checks, findings,
limitations, and handoff notes. Do not mark BC2 complete.
