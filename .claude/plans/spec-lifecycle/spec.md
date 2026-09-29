# Truthful native specification lifecycle

Status: APPROVED for the bounded implementation released on 2026-09-29.
Parent card: `W5-3.spec-lifecycle`. Original finding: V2 `lane-A-07`.
Base: `0baa9a0c6e518dc619668aef03e2889ca599dab8`.

## Requirements

| ID | Requirement | Observable acceptance |
|---|---|---|
| R1 | New unapproved native artifacts start DRAFT | Files instantiated from the actual spec, plan and prompt templates have DRAFT status. Copying a template does not assert approval or skip the selected-work check. |
| R2 | Approval reflects existing authority | The actual PLAN completeness gate rejects a DRAFT work map even if artifact headings claim APPROVED. A recorded approved scope remains usable without changing original task IDs, rewriting artifacts or asking for the same grant. |
| R3 | Requirements name observable verification | A rendered specification carries an observable expected result and concrete verification/evidence references linked to original leaf IDs; planned checks are not represented as executed evidence. |
| R4 | PLAN/CAPTURE and external authority stay consistent | PLAN owns approval/finalization; CAPTURE preserves the actual selected status and records observations rather than approving drafts. Spec Kit original artifacts/tasks remain authoritative. |

## Scope and limits

Edit only the spec template and necessary plan/prompt status joins, PLAN/CAPTURE,
and the existing planning-consolidation/work-artifact tests. Use the existing work
map and completeness gate; no approval engine, schema, timing rule, approval floor,
governance or other remediation changes.

Tests instantiate real templates and execute the existing gate/reader in owned
fixtures. They do not authenticate a conversational grant or prove live model
obedience. The existing host/operator authority boundary remains unchanged.

Local native generation/check is verification only; final version and generated
integration remain coordinator-owned. No publication, full suite, new actor, model,
dependency, install or live-host run is authorized.
