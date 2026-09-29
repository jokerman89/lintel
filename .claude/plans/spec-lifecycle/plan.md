# Spec lifecycle implementation plan

Status: APPROVED by the bounded 2026-09-29 implementation release.
Parent card: `W5-3.spec-lifecycle`; finding `lane-A-07`.
Base: `0baa9a0c6e518dc619668aef03e2889ca599dab8`.
This package implements the existing authority rule, not the larger lean-planning policy.

## Package

| Package ID | Outcome | Leaf IDs | Owner / edit boundary | Dependencies | Review |
|---|---|---|---|---|---|
| SL1 | DRAFT-first native artifacts with observable verification links | T1, T2, T3 | spec lifecycle implementer; scaffolding/01-foundation/templates/plan/spec.template.md, scaffolding/01-foundation/templates/plan/plan.template.md, scaffolding/01-foundation/templates/plan/prompt.template.md, skills/plan/SKILL.md, skills/capture/SKILL.md, tests/unit/planning-consolidation.py, tests/unit/work-artifacts.sh | none | substantive |

## Design

Template statuses describe the selected work; they are not another approval source.
New native scaffolds default DRAFT. PLAN records actual existing approval for the
reviewed scope before reflecting APPROVED in the map and native artifacts.
Do not erase a retained grant or impose native headings on Spec Kit artifacts.

Extend the specification's existing requirements table with observable acceptance
and verification/evidence references. Reuse the plan's original leaf details instead
of making another task list. CAPTURE preserves that contract and distinguishes
planned checks from observations.

## Tasks

### T1 Add artifact and gate regressions

- [ ] Verify newly instantiated artifacts, links and actual gate behavior.
Requirements: R1, R2, R3, R4.
Dependencies: none
Verify: new default/traceability cases fail against old templates; exercise the real
PLAN gate and work-map reader with DRAFT, text-only approval and recorded approval.

### T2 Align the templates and lifecycle

- [ ] Apply the minimal status, traceability and PLAN/CAPTURE changes.
Requirements: R1, R2, R3, R4.
Dependencies: T1
Verify: rendered artifacts carry correct status and observable linked criteria;
original task IDs and existing approval survive, with no schema/authority change.

### T3 Return a verified candidate

- [ ] Run focused checks and local native generation/check.
Requirements: R1, R2, R3, R4.
Dependencies: T2
Verify: record exact commands, outcomes, scope, source hashes and actual own profile
for the existing independent reviewer. No broader W5-3 closure or release claim.

## Profile and review

Establish a new explicit repository-local `spec-lifecycle` profile context from this
worktree's source and requirements. Carry its actual reference/policy unchanged.
Never borrow another worktree's reference or initialize global state.

Implementation: ready for independent source review. All task checkboxes and the
parent card remain open until actual evidence and review satisfy acceptance.

## Implementer evidence

| Leaf | Actual observation |
|---|---|
| T1 | Corrected RED: two methods expose three template defects (spec pre-approved, prompt status absent, requirement verification columns absent). The initial test-extraction error was corrected only in the test helper; both logs are retained. |
| T2 | Spec and prompt now default DRAFT; plan retains its DRAFT default. Requirements carry expected-result and verification/evidence references. PLAN reflects actual selected approval; CAPTURE preserves status rather than granting it. |
| T3 | Final focused run: 20 PASS (15 source-contract checks and five rendered-artifact/gate/mapping cases), 5.013 seconds. Existing work-artifacts shell check PASS. Local native generation/check: 172 managed files verified. |

The behavior cases instantiate the actual templates, execute the existing PLAN
completeness gate's Python block, reject DRAFT maps despite forged approval headings,
preserve recorded approval and original native/Spec Kit IDs, and resolve planned
verification references for both sample requirements. The gate validates recorded
approval state, not human identity; no live agent or approval-conversation claim.

Own reference: context `spec-lifecycle`, generation 1, `_default` 1.0.0,
digest `sha256:740e12dc186e102b1aa954482cd026a7c91412982847b8b810566122f1e97482`.
Actual required-policy result: `required: false`, `status: not_required`,
`source: bundled-neutral`, `version: 1.0.0`, `applicability: not_applicable`.
Roots and reference are local runtime evidence, not transferable approval.

No shared gate/schema, timing/approval floor, governance, version or other package
was changed. Source and generated verification outputs remain uncommitted; final
reducers, independent review and integration are coordinator-owned. Raw logs are
retained under `.claude/runtime/spec-tests/logs/`. No full suite, model, host,
dependency installation or publication was performed.
