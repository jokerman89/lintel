# Swarm charter: legacy cleanup

## Intent and authority

Six isolated implementation lanes execute the original-ID cards in ../plan.md.
The operator authorized this fan-out and aggregate delivery. All lanes in wave 1
are dependency-independent at their declared write boundaries. The current contract's
frozen-path overlay in ../spec.md has priority over every ordinary scope.

## Coordinator contract

Integration host/routing session e9c20b62-f877-4242-82cd-b5002d452da8 alone writes plan/runtime state,
generated reducers, commits and integration history. Workers write only their scope
and own report. No worker edits another worktree, stages/commits, pushes, opens a PR,
authors its review, or creates further descendants.

The app workspace separately identifies its project session as
e9d7470d-278c-4d7a-8a73-e1fd7a108ece. This is not the host actor/invocation identity.
Use the host/routing ID for messages, actual profile context and review attribution.

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

## Validation boundary update

The host refused W1's private/session-environment launcher before execution. No
continuation may copy, move, inline, switch tools or borrow another launcher to
recreate the refused action. Source-only checks and existing expressly authorized
read-only swarm metadata commands remain separate observations. Dynamic tests needing
that refused setup remain NOT RUN. Normal committed-repository hosted CI is a separate
required acceptance path and must never load the refused launcher.

The coordinator's earlier, separately accepted map/profile bootstrap is historical
evidence only; it does not transfer permission to a worker. Pre-update documentary red
checks reported by other lanes remain labelled observations, not current acceptance.

## Ownership correction, 2026-09-25

The initial documentation directory scope included a generated showcase HTML file.
The parent identified the overlap before fan-in; the scope now names only its README,
and the generated HTML is explicitly coordinator-owned/frozen. Directory scopes must
be checked against generated-file inventories before dispatch, not only against
obvious catalog/wiki directories. Record this lesson in memory after its freeze lifts.
