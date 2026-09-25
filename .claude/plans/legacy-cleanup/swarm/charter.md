# Swarm charter: legacy cleanup

## Intent and authority

Six isolated implementation lanes execute the original-ID cards in ../plan.md.
The operator authorized this fan-out and aggregate delivery. All lanes in wave 1
are dependency-independent at their declared write boundaries. The current contract's
frozen-path overlay in ../spec.md has priority over every ordinary scope.

## Coordinator contract

Integration session e9d7470d-278c-4d7a-8a73-e1fd7a108ece alone writes plan/runtime state,
generated reducers, commits and integration history. Workers write only their scope
and own report. No worker edits another worktree, stages/commits, pushes, opens a PR,
authors its review, or creates further descendants.

Each worker sends its actual worktree/branch/base, changed paths, exact checks,
per-leaf outcomes, capability carry-over, limitations and deferred consumers.
Use the report template and li-swarm snapshot for local v2 observations.
Do not invent shared clearance. Coordinator prepares actual P05 context/QA and P07
profile reference; independent actors produce review, with actual host corroboration.

## Scheduling and integration

Maximum six writers, each in its own host-created Git worktree. Shared Git config
is never edited. Narrow tests use synthetic homes/temporary parents (L-037/L-051),
without reusing the denied jq route or installing a refused dependency. No duplicate
full suites. Do not remove a temporary root that backs the shared MSYS mount.

Validate topology before dispatch and exact lane changes before integration.
Preserve isolated results while upstream PR #93 owns its frozen files. After the
explicit green/review/merge handoff, rebase the integration branch onto verified main
before fan-in. Integrate attributable lanes serially; regenerate only afterward.

Two review sessions assess the integrated candidate in order: specification/capability,
then quality/verification. They also provide per-lane findings/evidence; neither fixes
its own findings. No lane or initiative closes without actual required evidence.

## Recovery and honest limits

Missing runtime evidence remains missing; distinct role strings do not prove independence.
An out-of-scope change is preserved and quarantined until reconciled. This worktree is
isolation for attribution, not a security sandbox. Existing failures and real-host
limits remain visible. No archived worktree, reset, history rewrite or cleanup shortcut.
