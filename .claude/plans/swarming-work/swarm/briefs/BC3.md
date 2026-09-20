# Agent brief: BC3 — workflow integration

## Lintel startup

Read `AGENT-INSTRUCTIONS.md`, `scaffolding/01-foundation/CORE-PRINCIPLES.md`, current
`.claude/memory/{MEMORY,working-state,personas}.md`, recent lessons, relevant accepted ADRs, and
`docs/architecture.md`. Resolve the active pack and apply the repository compliance checklist.
This brief narrows your ownership; it does not replace repository authority or safety rules.

## Task

Implement BC3 verbatim from [../../plan.md](../../plan.md). Add the canonical `/li:swarm` workflow
and connect PLAN, BUILD, REVIEW, RESUME, CAPTURE, CYCLE, the work-map contract, and the existing
parallel engineering pass.

## Inputs

- BC2's validated schema/CLI and templates
- [../../spec.md](../../spec.md)
- [../charter.md](../charter.md)
- `docs/concepts/agent-dispatch-rules.md`

## Ownership

Write only the BC3 `write_scope` paths in `coordination.json`, plus BC3's own declared `report`
path. Do not write BC3's `review` path. The task artifact remains authoritative. Do not edit
session protocol, docs, manifests, generated adapters, shared plan state, or runtime ledgers.

## Acceptance

- No coordination pointer means legacy sequential BUILD.
- Swarm mode dispatches only a dependency-ready, ownership-safe wave.
- Every worker assignment uses Brief Forge explicitly or records an audited unavailable/bypass path.
- Per-card spec/quality review and final integrated review are both required.
- Sequenced/no-subagent fallback preserves the artifact and evidence contract.

## Report

Write `../reports/BC3.md` with changed files, checks, findings, limitations, and downstream
generator/documentation notes. Do not mark BC3 complete.
