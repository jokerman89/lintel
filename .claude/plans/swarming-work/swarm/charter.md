# Swarm charter: first-class swarming work

## Intent

Dogfood the proposed Lintel swarm contract while building it. The authoritative cards and
dependencies remain in [../plan.md](../plan.md); this file owns coordination only.

## Coordinator contract

The root agent is the sole writer for shared plan/runtime state, generated reducers, commits, and
integration. Workers receive one card and own only the paths declared in `coordination.json`.

Worker scope is the lane's `write_scope` plus that lane's own `report` path. The report exception
is explicit and validated; it does not grant access to the lane's `review` path. An independent
reviewer may write only the reviewed lane's `review` path. Workers never author their own review
evidence.

## Scheduling

Run waves in numeric order after checking the authoritative dependencies. Within a wave, dispatch
writer lanes concurrently only when their scopes are disjoint and each change set is attributable
through an isolated worktree/patch or host-enforced scoped sandbox. Otherwise sequence the same
lanes. Never exceed `max_parallel`. Reviews may fan out read-only after implementation fan-in.

## Integration barriers

- Core schema and validator land before workflow consumers.
- Workflow integration lands before scaffolding/adapters and public documentation finalize.
- Generated surfaces, synchronized entry files, catalogs, inventories, and manifests are
  coordinator-owned reducers after producer lanes finish.
- Final review and the full suite run on the reconciled feature branch.

## Conflict and recovery

A path outside a lane's attributable patch or an overlapping edit blocks that lane. Preserve the
diff, stop the affected closure, and either serialize, narrow ownership, or re-run in an isolated
worktree. A union diff from shared concurrent writers is not acceptable attribution evidence.
Runtime loss cancels attempts only; reconstruct from committed artifacts, Git, and evidence.

## CLI degradation

Native hosts may run safe lanes concurrently. Sequenced/no-subagent hosts run the same lanes in
order. Correctness, evidence, and authority boundaries do not degrade; only concurrency and the
claim of independent review do.
