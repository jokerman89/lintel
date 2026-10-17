# Swarm charter: V2 ready-clause continuation

## Intent

The user explicitly requested the remaining Skill review V2 work to run in
parallel. P11A, P11B, P11C and P12 are dependency-ready, have disjoint
source/test scopes and can produce attributable Git-worktree diffs. The mapped
work remains authoritative for leaf text, dependencies, status and acceptance;
this charter owns only coordination.

## Coordinator contract

The MasterCoordinator is the sole writer for shared plan/runtime state,
cross-owner callers, generated reducers, version/release files, commits and
integration. A worker owns only its declared `write_scope` plus its own report.
An independent reviewer owns only the lane review and canonical P05 decision.
Workers never review their own work or edit another lane.
For P11B, `skills/sense/SKILL.md` is a coordinator-owned current caller:
the worker verifies its retained routing behavior read-only, and the coordinator
migrates the exact public help example after fan-in.

## Scheduling

P11A, P11B, P11C and P12 form wave 1. They may run concurrently only in the
declared Git worktrees from the same reviewed base. The coordinator validates
semantic prerequisites and each exact diff before integration. Integration
order is P11A, P11B, P11C, P12. Shared caller migration, resource closure,
catalog/wiki/native generation, versioning and P9 run only after that fan-in.

## Integration barriers

- Validate the work map and coordination before dispatch.
- Preserve original finding IDs and complete accepted owner behavior.
- Reject or quarantine out-of-scope and unattributable changes.
- Require package SPEC then QUALITY review over every member leaf.
- Integrate passing lane changes serially and rerun focused checks after each.
- Regenerate shared outputs only after all producer lanes are integrated.
- Run final integrated REVIEW, profile-bound QA and full verification on one head.

## Coordinator residual continuation 2026-10-17

The original four producer lanes are integrated in the recovered feature branch.
Their source, reports and prior observations remain retained, not replayed or
silently rebound. The active integration branch is now
`jokerman-microsoft-repository-completion`; this is recovery of the same work,
not authority to change the old worktree or publish to main.

P13-P16 in the original plan are coordinator-owned follow-ups on shared templates,
callers, documentation and overlapping oracle files. Execute them sequentially
under the coordinator's exclusive write ownership; they are not new worker lanes.
The original four-lane topology, isolation and acceptance requirements remain.
New source changes need current package and final integrated review/QA; historical
lane or green baseline results do not supply that acceptance.

## Conflict and recovery

An out-of-scope path, overlapping write, missing worktree attribution or review
failure blocks only the affected lane. Preserve its branch and report; narrow,
repair or replay that same brief. Missing runtime state never converts a branch
or chat claim into completed work.

## CLI degradation

If native isolated worktrees cease to be available, replay these exact briefs
sequentially. Do not weaken scope, review, evidence or final integration gates.
