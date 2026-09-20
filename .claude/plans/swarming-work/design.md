# Design: first-class swarming work

**Status:** APPROVED by the operator's 2026-09-08 request to deliver the feature through merge.
**Mode:** meta-infra
**Decision record:** originally ADR-0026 on `275a354`; retained and reconciled as
[ADR-0027](../../decisions/0027-first-class-swarming.md). This design remains historical;
current integration authority is the Universal P04 card.

## Vision

A Lintel swarm is one approved initiative, one coordinator, and a dependency-ordered set of
bounded cards. Every worker receives the same Lintel operating discipline plus one card-specific
brief. Workers own disjoint paths and report through separate artifacts; the coordinator alone
advances shared state, integrates changes, and decides what runs next.

Swarming is an opt-in execution profile over PLAN → BUILD → REVIEW. It is not a tenth cycle phase,
a daemon, a distributed queue, or permission for autonomous external actions.

## Constraints

- Preserve the company-neutral spine/pack split.
- Keep the mapped `tasks` artifact authoritative for card text, dependencies, and completion.
- Store durable coordination under `.claude/plans/<initiative>/swarm/`; keep execution churn under
  `.claude/runtime/jobs/<job-id>/swarm/`.
- One coordinator owns shared ledgers, plan checkboxes, generated reducers, commits, and integration.
- Parallel writers need non-overlapping write scopes plus attributable isolation: separate Git
  worktrees/patches or an equivalent host-enforced scoped-write sandbox. Without that evidence,
  writer lanes run sequentially. A conflict blocks integration; it is never silently resolved.
- Correctness must be identical on native, sequenced, and no-subagent hosts. Only concurrency and
  independent-review evidence degrade.
- Agent memory may help but cannot be required to reconstruct work.

## Alternatives

### A — parallelize BUILD in place

Add lane metadata to plan cards and let BUILD fan out directly. This has the smallest diff, but
hides ownership and recovery inside a long plan and makes BUILD both executor and coordination
protocol.

### B — additive swarm contract over the existing work map

Add a `/li:swarm` workflow, a committed swarm charter plus machine-readable coordination map,
per-card briefs/reports/reviews, and a deterministic validator. PLAN and BUILD opt in through an
additive `work.json` pointer. Existing sequential work remains unchanged.

### C — Git worktree federation

Give every card a branch/worktree and reconcile reviewed commits. This gives strong isolation but
turns branch cleanup and merge conflict handling into the normal path and excludes non-Git work.

## Decision

Choose B. Attributable isolation is mandatory for concurrent writers. Git worktrees are one
supported backend, but the contract may also accept isolated patch production or a host-enforced
scoped-write sandbox with equivalent per-lane evidence. Without one of those backends, execution
is sequenced.

## Contract

```text
.claude/plans/<initiative>/
├── work.json
├── spec.md
├── plan.md
├── prompt.md
└── swarm/
    ├── coordination.json
    ├── charter.md
    ├── briefs/<card-id>.md
    ├── reports/<card-id>.md
    └── reviews/<card-id>.md
```

`work.json` gains two optional additive fields: `execution_mode: "swarm"` and `coordination`.
`coordination.json` owns only execution topology: waves, roles, write scopes and artifact paths.
It references card IDs from the authoritative `tasks` artifact and does not copy task prose,
dependencies, status, or acceptance criteria. A worker's permitted artifact set is its declared
`write_scope` plus its own `report` path. Its `review` path is reserved for an independent reviewer;
neither report nor review ownership grants access to another lane or to coordinator reducers.

The validator rejects unsafe paths, duplicate card assignments, missing briefs, unknown modes,
overlapping write scopes inside a wave, missing isolation metadata for parallel writers, and
incomplete report/review evidence at the close gate.

## Lifecycle

```text
approved card → coordinator selects ready wave → Brief Forge assignment → worker executes
→ scope check → worker report → spec review → quality review → serial integration → card DONE
```

Independent lanes may continue if another lane blocks. Scope checks compare each isolated patch or
host-attributed change set to one lane—not the union diff in a shared tree. A breach freezes affected
ownership domains and triggers reconciliation or re-plan. Runtime loss cancels attempts, not
committed and verified work.

## Host degradation

- `native`: dispatch non-conflicting cards concurrently up to the host/operator cap.
- `sequenced`: run the same cards one at a time with the same briefs and evidence.
- `none`: the main agent executes cards serially or emits replayable briefs for manual workers;
  self-review is labelled honestly.

## Non-goals

- Changing ordinary BUILD to swarm by default.
- Translating Claude hooks to every host.
- Automatic Git merge, push, deployment, or production mutation.
- Rewriting the agent fleet or introducing a generic worker persona.
