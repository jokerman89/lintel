# Swarm charter: <initiative>

## Intent

State why this initiative benefits from swarming. The mapped task artifact remains authoritative
for card text, dependencies, status, and acceptance; this charter owns coordination behavior only.

## Coordinator contract

One coordinator is the sole writer for shared plan/runtime state, generated reducers, commits, and
integration. A worker owns only its declared `write_scope` plus its own report. An independent
reviewer owns only the reviewed lane's review artifact. Workers never author their own review.

## Scheduling

Run waves in numeric order after checking dependencies in the mapped task artifact. Concurrent
writers require disjoint scopes and attributable isolation (`git-worktree`, `isolated-patch`, or
`host-scoped-write`). Otherwise sequence the same briefs. Never exceed `max_parallel`.

## Integration barriers

- Validate topology before dispatch.
- Validate each attributable change set before integration.
- Integrate lanes serially and let the coordinator regenerate shared outputs.
- Require per-lane spec and quality review before a dependent wave.
- Run final REVIEW and the full suite on the reconciled integration branch.

## Conflict and recovery

An out-of-scope path, overlap, or unattributable shared-tree diff blocks the affected lane. Preserve
the diff and either narrow ownership, serialize, or repeat the lane in isolation. Reconstruct a
lost attempt from committed maps, briefs, reports, reviews, and Git; do not invent evidence.

## CLI degradation

Native hosts may run isolated lanes concurrently. Sequenced and no-subagent hosts replay the same
briefs serially. Correctness and evidence stay fixed; only concurrency and independent-review claims
may degrade to what the host actually proves.
