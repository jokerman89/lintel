# Spec: Universal capability and evidence integration

**Status:** APPROVED
**Authority:** operator request of 2026-09-20 and the preserved
[MasterSession mandate](../universal-quality-audit/master-session-prompt.md).
**Plan:** [plan.md](plan.md)
**Baseline:** `28061e434be455ca02f135b73244eaf4f73f3a69`

## Outcome and authority

Implement all A01-A26 outcomes from the
[audited action list](../../engineering/audits/2026-09-20-universal-quality/action-plan.md).
That list supplies the discriminating acceptance cases; it is not a second task ledger.
The implementation task source is this directory's plan.md, selected by work.json.
The audit's completed checklist never establishes implementation completion.

Preserve useful functionality, specialist methods, familiar entry points, tests and
historical evidence. No file-count reduction target applies. Preserve all 76 Swarming
delta paths and its Git ancestry, reconciling rather than replacing current main.
ADR-0026's short leaves, package execution and independent substantive review remain.

The existing local feature branch is the integration branch. Only MasterSession merges,
updates common state, assigns ADR numbers and regenerates common outputs. Each writer
uses a separately verified worktree. Overlapping ownership runs sequentially.

## Architecture

Keep the current harness, path layout, canonical skills and small mechanical helpers.
Do not introduce a scheduler, daemon, universal execution engine or competing backlog.
Host adapters translate neutral operations using actual session tools and permissions.
Capabilities distinguish vendor documentation, shipped adapter and observed execution.
No missing reviewer may be represented by role-playing independence.

The following interfaces must have one authoritative representation, consumed by both
producers and readers, with integration tests at their boundaries:

| Interface | Required semantics | Owner |
|---|---|---|
| Review/control result | Mandatory versus advisory, applicability, pass/fail/unverified/error; mandatory unknown/error/failure blocks | P05 |
| Review identity | Selected work map, package/leaf coverage, acceptance/source identity, exact base/result including selected dirty/new files, attempt and independent actor | P05; P04 consumes during final reconciliation |
| Host operations | Question, plan, tools, browser, delegation, isolation, memory and hooks; explicit fallback and observation level | P06 |
| Effective profile | Explicit source precedence, content identity across calls/resume, required-policy failure distinct from neutral first use | P07 |
| Work identity | Original spec/plan/tasks/prompt and stable leaf IDs; no initiative guessing by mtime | P08 |
| Domain result | Work/profile/revision reference, decisions, checks and handoff; not a second backlog | P09 |
| Design result | One contract from brief through renderer/review, including valid no-animation/no-shader choices | P11 |
| Audit event | Common producer/consumer schema, observation provenance, minimal non-sensitive content | P08 |
| Swarm ownership | Coordinator, worker and reviewer scopes, protected/generated outputs and attributable evidence | P04 |

## Requirements and coverage

Every A-ID retains the full acceptance criterion in the audited action list.
Its implementation leaves and accountable owner are recorded in plan.md.

| Requirement | Actions |
|---|---|
| R01 Safe literal input, owned recovery and trusted code source | A01, A04, A12, A25 |
| R02 No false clearance; independent review binds delivered content | A02, A03, A23 |
| R03 Universal host operations without reducing existing client value | A05, A06, A16, A19 |
| R04 Stable, observable company profile and compatible pack schema | A07, A20, A24 |
| R05 One work map across routing, execution, review and recovery | A08, A10, A11, A13 |
| R06 Concrete domain and role expertise, retained use cases | A09, A17, A18, A19 |
| R07 Runnable design/browser/document chains with honest boundaries | A14, A15, A16 |
| R08 Dormant mechanisms stay opt-in; payloads are checked before output | A21 |
| R09 Complete Swarming preservation with native/serial/manual modes | A22 |
| R10 Private sync uses only an explicit, current destination | A26 |
| R11 Measured evidence, preserved behavior and final integrated review | All; A23, A24 |

## Verification and preservation

For each leaf record the original defect, changed behavior, preserved behavior, exact
command/scenario, outcome and limitation. Add discriminating negative tests, not just
prose assertions. Reproduce on isolated fixtures; never run an unsafe recipe against
personal state. Keep existing useful tests. Validate generated files from their source.

Review runs after a package's code stops changing and names the exact reviewed revision.
A reviewer does not repair their findings. A repair invalidates affected evidence and
returns to review. Integrated review is separate from package reviews.

Final delivery needs the stable combined tree, relevant tests, strict suite, fresh
consumer installation, current-main comparison, CI and independent final review.
Actual client/model acceptance is separate from local/structural tests. Untested clients
stay unverified, not "complete" through a blanket support statement. No fabricated ROI,
usage, duration, coverage percentage or independent actor is acceptable.

## Permission boundaries

Repository edits, feature commits, bounded local tests and delegated work are authorized.
Delivery is a feature branch and PR to `jokerman89/lintel` main, not a new repository.
Only the `jokerman89` GitHub identity is authorized. Previously rejected credentials must
not be used even for read-only GitHub calls, cleanup or PR creation. The earlier abandoned
private-repository operation is not part of this initiative.

On 2026-09-21 the operator explicitly authorized completing this initiative through
a reviewed feature PR and merge to `main`, then cleaning up its completed owned work.
This applies to the approved A01-A26 delivery batch only, after required verification,
independent review and CI; it is not standing default-branch authority or permission
to bypass branch rules. Preserve Swarming ancestry, historical reports, verified
backups and any unmerged work during scoped cleanup. No broad deletion or personal
profile cleanup is authorized.

The operator separately authorized GitHub login as `jokerman89`; the CLI credential
selected specifically for that account was verified through `/user` during the
2026-09-22 continuation.
Authenticated repository reads confirm `main` is still `28061e4`, push permission
and merge-commit support. Clear rejected injected tokens and select the verified
identity explicitly for authenticated operations; never assume another tool's actor.
No release/tag, new repository, production/deployment action, private synchronization,
hook activation, other credential/policy change or paid benchmark follows implicitly.

## Decisions

The operator selected preservation-first Universal improvement over removal or a new
runtime. Reserve ADR-0027 for the reconciled Swarming decision, ADR-0028 for the Universal
operation/evidence contract, and ADR-0029 for required-profile behavior. Workers must not
reuse these numbers for unrelated decisions. Accepted historic ADRs are preserved and
explicitly superseded only in the applicable scope.

Material unavoidable value loss or a genuine strategic conflict returns to the operator
with concrete alternatives. Ordinary corrections within these acceptance criteria do not
require repeating approval.
