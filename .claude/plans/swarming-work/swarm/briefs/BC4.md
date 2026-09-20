# Agent brief: BC4 — scaffolding and adapters

## Lintel startup

Read `AGENT-INSTRUCTIONS.md`, `scaffolding/01-foundation/CORE-PRINCIPLES.md`, current
`.claude/memory/{MEMORY,working-state,personas}.md`, recent lessons, relevant accepted ADRs, and
`docs/architecture.md`. Resolve the active pack and apply the repository compliance checklist.
This brief narrows your ownership; it does not replace repository authority or safety rules.

## Task

Implement BC4 verbatim from [../../plan.md](../../plan.md) after BC3 is integrated. Propagate the
swarm contract through the session protocol, subagent guide, scaffold, and generated Copilot
surface.

## Inputs

- `scaffolding/01-foundation/SESSION-PROTOCOL.md`
- ADR-0025 and the protocol synchronizer
- `bin/li-copilot.py`
- the final canonical `skills/swarm/SKILL.md`

## Ownership

Write only the BC4 canonical-source `write_scope` paths in `coordination.json`, plus BC4's own
declared `report` path. Do not write BC4's `review` path. Root entry synchronization, generated
Copilot files, inventories, catalogs, manifests, and other reducers remain coordinator-owned.

## Acceptance

- One canonical protocol source is ready for coordinator synchronization.
- New scaffolds receive accurate swarm guidance/templates without local fleet shadowing.
- The Copilot generator declares a native `li-swarm` wrapper and every required source resource.
- `tests/integration/copilot-kit.py` asserts the swarm wrapper and source-resource inventory.
- Generator-focused tests pass; coordinator performs root/consumer regeneration checks after fan-in.

## Report

Write `../reports/BC4.md` with changed/generated files, exact commands, findings, limitations, and
reducer work the coordinator still owns. Do not mark BC4 complete.
