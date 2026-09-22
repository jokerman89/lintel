# Engineering modules

Lintel's five engineering modules provide technical depth inside the established
nine-phase lifecycle. They retain their original capabilities and specialist roles,
but their procedures are **agent-owned**, not an implicit shell scheduler.

| Module | Decision expertise | Outputs retained |
|---|---|---|
| [TA](ta-module.md) | invariants, interfaces, topology, scaling and quality attributes | architecture, ADRs, contracts, dependency/NFR evidence |
| [DA](da-module.md) | schemas, queries, migrations, retention and analytics | schema, recovery/validation SQL, partition/lineage and retention |
| [SC](sc-module.md) | threats, auth, secrets and applicable regulatory controls | threat/auth/audit design, control evidence and response runbook |
| [DH](dh-module.md) | deployment, state-compatible recovery, signals/SLOs, cost | cutover/rollback, observability, capacity and on-call plan |
| [TQ](tq-module.md) | requirement assertions, compatibility, performance and recovery | coverage, test matrices, benchmarks, regression/chaos strategy |

The [full engineering pass](full-engineering-pass.md) composes TA -> DA/SC -> DH ->
TQ. DA/SC are parallel-eligible only with the existing approved Swarm profile and
actual safe isolation; otherwise execute serially. No theoretical time saving is
claimed from a diagram.

## Entry and original work

Each module supports `full`, `loop`, or a direct capability/`single --action`.
Full covers its five checkpoints; single preserves the narrow requested operation;
loop requires an explicitly selected saved attempt and changed-input decision.
Do not impose a customer/venture interview on maintenance or a known bounded fix.

The [shared consumer procedure](../../skills/full-engineering-pass/references/domain-handoff.md#module-caller-procedure)
uses accepted `work_context`, `workflow_inspect` and `workflow_resume` for original
artifact paths, task IDs and cycle/profile identity. Source status alone is not
acceptance. Original maps/tasks/handoffs remain authoritative; no parallel backlog
or private package parser is introduced.

Read module skills, roles and method references under `LINTEL_SOURCE_ROOT`.
The target's configuration/artifacts are data, not an executable source fallback.
P07 verifies the actual pinned pack and required policy before use. Explicit
invocation preferences are advice bound into the request; they are not an automatic
read of personal `profile.yaml` or a hidden policy override.

## What the caller owns

The caller selects original leaves, expected domains/checkpoints and immutable P05
QA obligations before observations. It assigns real receiver mode/scope and original
file preimages; records start; uses actual host tools or explicit serial execution;
persists artifacts/logs/results; and externally prepares the final P05 context.
The accepted domain data helper records and verifies only. It cannot perform the
method, infer permission, authenticate an actor or grant release clearance.

Checkpoints are observations, not original task completion. A reviewer reports rather
than repairs; independent acceptance needs actual separate context/corroboration.
MigrationPlanner plans while Migrator retains artifact and exact-authorized execution.
ReleaseEngineer retains planning-only and separately authorized release execution.
No role name or well-formed result grants live-system authority.

## Verification, scoring and continuation

Each module retains six advisory dimensions. A 30-dimension composition view helps
prioritize work, but cannot average away missing or failed mandatory domains.
Unknown applicability, required policy failure, zero/skipped tests or unavailable
browser evidence stay explicit. Grounded optional exclusions do not become failed
mandatory checks, and a skip flag cannot erase a requirement.

Use safe explicit `.claude/runtime/state/domains/<operation>/iNNNN/` record paths.
Keep the original cycle/map and prior-result references in the selected handoff.
Cold resume verifies them and identifies the actual first unmet checkpoint; a
start without result means interrupted. Never replay unknown external effects,
choose the latest report by mtime, replace an old PASS or reset unrelated files.

Old per-module artifacts remain usable history when explicitly selected and verified.
No migration/deletion of them is needed. Main lifecycle remains SENSE -> SCOPE ->
DEFINE -> DISCOVER -> PLAN -> BUILD -> REVIEW -> SHIP -> CAPTURE; resume is a utility.

## Hooks, installation and evidence levels

Domain warn-hooks stay opt-in under ADR-0008. File presence, documented host support
or a configured hook name does not prove registration/execution. Brief Forge/audit
calls are explicit where configured; a persisted event is not independent review.
No hook, global model, personal profile or permission configuration changes here.

Existing shape checks validate metadata/capabilities. The module-consumer tests
exercise real selected-work/profile/data/QA links in synthetic processes. The
separate role-content checks are documentary/illustrative. Native method handoffs
and installed-consumer runs must be identified separately; none is inferred from
a source file, a green grep or a claim that all historical v4.x work is complete.
