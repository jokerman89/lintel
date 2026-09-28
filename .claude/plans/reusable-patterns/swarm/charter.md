# Swarm charter: reusable patterns

## Intent

The operator explicitly opted into swarm execution. The initiative has three dependency-independent
domains after P1: core pins/lifecycle/sharing, pack provenance and launcher, and workflow/visual
consumers. The mapped plan.md leaf items remain authoritative for leaf text, dependencies, status and
acceptance; the "Swarm execution packages" table owns package membership and review depth. This
charter owns coordination behavior only. ADR-0027 and ADR-0028 govern; nothing here is a second backlog.

## Chronology (recorded honestly)

- P0/P1 (package P0P1) were implemented by the integration session and reviewed by an independent
  reviewer session, coordinated by the host parent session. They were not dispatched through
  `li-swarm.py wave`/`brief` or Brief Forge.
- The PACK and WF lanes were launched by the parent from the reviewed R2 head `ae9d6df7` as separate
  host worktree sessions, again host-coordinated rather than through native `li-swarm` dispatch.
- This charter, coordination.json and the swarm fields of work.json were added afterwards
  (2026-09-28) to bring the running initiative under the existing validators. They record the
  approved topology and ownership. They are not a retroactive claim that the earlier dispatch was
  natively validated, and no brief envelope, QA or corroboration receipt is backfilled.

## Coordinator contract

The integration session is the coordinator and the sole writer for shared plan/runtime state,
generated reducers, commits on the integration branch and integration. It also implements the
CORE lane in its own worktree, which is attributable by its own commits. A worker owns only its
declared `write_scope` plus its own report. An independent reviewer owns only the reviewed lane's
review artifact. Workers never author their own review. Coordinator-owned outputs are listed in
`coordinator_paths`. The parent host session owns dispatch of nested sessions and commissions
independent review.

## Scheduling

All three lanes are wave 1 after P0P1, with disjoint scopes and `git-worktree` isolation, bounded
by `max_parallel: 3`. Cross-lane acceptance (V09, V11, the launcher-backed parts of V05/V12)
stays pending join and is verified on the integrated branch. INT (P6) is coordinator-only and
serial after all lanes are integrated and reviewed.

## Integration barriers

- Run `li-work-artifacts.py` and `li-swarm.py validate` before any further dispatch or join.
- Before each serial join, derive the lane's exact attributable changed paths from its own base and
  head, and run `li-swarm.py check-scope --actor worker`. A failure blocks the lane.
- Integrate with ordinary merges or cherry-picks, never rebase, reset or amend. Run focused checks
  after each join, then regenerate shared reducers from source.
- A substantive package needs spec review and quality review by a separately attributable reviewer
  covering every member leaf.
- The final integrated freeze uses the ADR-0028 shared v2 context, QA derived from acceptance, an
  independent review and a log-backed ship check. Historical narrative reviews are not current
  clearance.

## Conflict and recovery

An out-of-scope path, overlap or unattributable diff blocks the affected lane. Preserve the diff and
narrow ownership, serialize, or repeat the lane. Reconstruct from committed maps, briefs, reports,
reviews and Git; never invent evidence.

## CLI degradation

The host provides separate app-native worktree sessions for isolation. If attribution cannot be shown
for a lane, replay its brief serially. Independent review stays open until a real reviewer acts.