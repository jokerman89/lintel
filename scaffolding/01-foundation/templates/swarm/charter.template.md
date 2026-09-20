# Swarm charter: <initiative>

## Intent

State why this initiative benefits from swarming. The mapped task artifact remains authoritative
for leaf text, dependencies, status and acceptance; the mapped plan owns package membership and
aggregate review depth. This charter owns coordination behavior only.

## Coordinator contract

One coordinator is the sole writer for shared plan/runtime state, generated reducers, commits, and
integration. A worker owns only its declared `write_scope` plus its own report. An independent
reviewer owns only the reviewed lane's review artifact. Workers never author their own review.
List project-generated/shared outputs in `coordinator_paths`; handoff paths may not alias them or
mapped authority, directly or through an ancestor or filesystem alias.

## Scheduling

Run waves in numeric order after checking dependencies in the mapped task artifact. Concurrent
writers require disjoint scopes and attributable isolation (`git-worktree`, `isolated-patch`, or
`host-scoped-write`). Otherwise sequence the same briefs. Never exceed `max_parallel`.

## Integration barriers

- Validate topology before dispatch.
- Validate each attributable change set before integration.
- Integrate lanes serially and let the coordinator regenerate shared outputs.
- Require package spec and quality review covering every member leaf before a dependent wave.
- Check worker and reviewer attribution separately and bind review to the exact attempt/report/result.
- Run final REVIEW and the full suite on the reconciled integration branch.

## Conflict and recovery

An out-of-scope path, overlap, or unattributable shared-tree diff blocks the affected lane. Preserve
the diff and either narrow ownership, serialize, or repeat the lane in isolation. Reconstruct a
lost attempt from committed maps, briefs, reports, reviews, and Git; do not invent evidence.

## CLI degradation

Native hosts may run isolated lanes concurrently. Sequenced and no-subagent hosts replay the same
briefs serially. Correctness and evidence stay fixed; only concurrency and independent-review claims
may degrade to what the host actually proves.
Export structured briefs and `review-input` on a no-subagent host. Substantive independent review
stays open until a real reviewer acts. An explicitly mechanical package may record coordinator
review, never relabel that as independent. Shared final binding remains an integration gate.
