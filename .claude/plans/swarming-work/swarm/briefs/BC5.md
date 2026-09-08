# Agent brief: BC5 — public swarming surface

## Lintel startup

Read `AGENT-INSTRUCTIONS.md`, `scaffolding/01-foundation/CORE-PRINCIPLES.md`, current
`.claude/memory/{MEMORY,working-state,personas}.md`, recent lessons, relevant accepted ADRs, and
`docs/architecture.md`. Resolve the active pack and apply the repository compliance checklist.
This brief narrows your ownership; it does not replace repository authority or safety rules.

## Task

Implement BC5 verbatim from [../../plan.md](../../plan.md) after BC3 is integrated. Explain when,
why, and how Lintel swarms from architecture through day-to-day operation and CLI degradation.

## Inputs

- [../../design.md](../../design.md)
- the final canonical `skills/swarm/SKILL.md`
- `lib/cli-tiers.yaml`
- current README/docs conventions

## Ownership

Write only the BC5 `write_scope` paths in `coordination.json`, plus BC5's own declared `report`
path. Do not write BC5's `review` path. Do not regenerate catalogs/wiki or change versions; those
reducers remain coordinator-owned.

## Acceptance

- A new operator can select, inspect, recover, and close a swarm from the docs alone.
- Docs do not claim concurrency, hooks, independent review, or persistent memory on unsupported hosts.
- Brief Forge's automatic/dormant wording is reconciled with actual activation.
- Nested default handoff policy and unknown-evaluator blocking are proven by executable tests.
- Public prose is company-neutral and English.

## Report

Write `../reports/BC5.md` with changed files, checks, findings, limitations, and reducer links still
needed. Do not mark BC5 complete.
