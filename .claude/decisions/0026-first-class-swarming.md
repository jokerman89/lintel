# ADR-0026: First-class swarming as an opt-in execution profile

**Status:** Accepted — 2026-09-08

## Context

Lintel already supports bounded subagent delegation, dependency-ordered build cards, Brief Forge
handoffs, work maps, independent review, and CLI capability tiers. Those pieces do not yet form one
portable swarming contract. BUILD describes one fresh implementer at a time, the work map cannot
point to execution topology, and no deterministic gate proves that concurrent writers had disjoint,
attributable ownership. Operators therefore have to reconstruct coordination from chat history and
host-specific behavior.

The requested capability must cover the complete harness: planning, execution, review, recovery,
scaffolding, supported client adapters, public documentation, tests, and delivery. It must preserve
Lintel's company-neutral spine/pack split and its existing nine-phase cycle.

## Decision

Add swarming as an explicit, opt-in execution profile over PLAN, BUILD, and REVIEW. It is not a
tenth phase and ordinary BUILD remains sequential when no swarm pointer is present.

The mapped task artifact remains authoritative for card text, dependencies, status, and acceptance.
Schema-version-1 `work.json` may add `execution_mode: "swarm"` and a repository-relative
`coordination` pointer. The coordination document owns only execution topology: waves, roles,
write scopes, isolation backends, and brief/report/review paths.

Every swarm has one coordinator. The coordinator alone writes shared plan/runtime state, generated
reducers, commits, and integration history. A worker may write its declared `write_scope` plus its
own report; an independent reviewer may write only the lane's review artifact. Concurrent writers
must use attributable isolation through separate Git worktrees, isolated patches, or an equivalent
host-enforced scoped-write sandbox. If such evidence is unavailable, writers are sequenced.

Add a standard-library validator and read-only CLI gates for validation, ready-wave calculation,
per-change-set scope checking, status, and close evidence. The CLI never executes artifact content,
spawns agents, mutates shared state, pushes, or merges. Brief Forge remains the handoff envelope;
swarming does not invent another message protocol.

Native, sequenced, and no-subagent hosts consume the same committed artifacts. Native hosts may
fan out isolated lanes, sequenced hosts replay them serially, and no-subagent hosts let the main
agent execute or export the briefs. Claims of concurrency and independent review must match the
evidence actually produced.

## Alternatives

1. **Parallelize BUILD prose in place.** This is smaller, but hides recovery and ownership inside a
   long plan and cannot mechanically reject unsafe concurrency.
2. **Add an additive coordination contract over the existing work map.** This preserves current
   authority, supports deterministic gates, and is removable without migration. Selected.
3. **Make a Git-worktree scheduler or work-map v2.** This offers strong isolation but over-couples
   the first version to Git, duplicates task authority, and turns Lintel into a runtime scheduler.

## Invariants

- Swarming is selected explicitly; absence of swarm fields preserves existing behavior.
- One task ID has one authoritative definition and at most one execution lane.
- Shared ledgers and generated outputs have one coordinator writer.
- Parallel writers have disjoint scopes and attributable per-lane evidence.
- Dependency and review gates are preserved across every host capability tier.
- External mutations still require the authority that would be required without swarming.

## Consequences and verification

Lintel gains a reusable swarm skill, committed templates, validator/CLI, workflow integration,
session-protocol rules, scaffold support, generated adapter support, and operator documentation.
The additional artifacts are required only for opted-in initiatives. The main costs are a larger
planning surface and explicit fan-in/review work.

Verification must cover backward-compatible work maps, unsafe paths, duplicate lanes, same-wave
overlap, missing isolation, per-lane scope including report/review ownership, incomplete evidence,
sequential degradation, generated drift, fresh scaffolds, and the integrated full suite. Final
review always runs on the reconciled branch rather than isolated lane trees.

## Migration and rollback

No migration is required because all work-map additions and swarm artifacts are optional. Existing
initiatives and clients continue on sequential BUILD.

Before publication, revert the feature commits in reverse order and abandon ignored runtime swarm
attempts. After publication, ship any rollback under a new patch version; never reuse a released
version. Preserved lane branches/worktrees must remain until their changes are either integrated or
explicitly accounted for.

## Non-goals

- A daemon, database, distributed queue, MCP server, or generic agent runtime.
- A universal host API for spawning, Git integration, deployment, or production actions.
- Translating Claude hooks to every client.
- Rewriting the existing agent fleet or making swarming the default.
