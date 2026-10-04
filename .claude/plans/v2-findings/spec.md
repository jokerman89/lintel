# Spec: complete the original V2 findings

**Status:** APPROVED for concrete corrections compatible with the constraints below.
Architectural alternatives and experiments remain unapproved until specifically resolved.
**Authority:** the operator's 2026-10-03 instruction to finish the original findings
with working repository changes, not another report or a selected-subset closeout.
**Plan:** [plan.md](plan.md).
**Work map:** [work.json](work.json).
**Base:** `f9796bb8b3fbcdab3e235f30401933ea1b2f3162`.

## Architecture overview

This continues Skill review v2. The original inventory contains 84 findings and
165 reviewed skill/agent items. The finding IDs, claims and adjudications remain
the requirements source; previous implementation packages are evidence, not a
replacement inventory. Their successful acceptance remains historical evidence
for their exact scope.

Preserve the company-neutral spine, existing public capabilities, source/target
separation, owned paths, required profile checks, content-bound review and actual
host permissions. Correct source methods, their consumers and regression tests
together. Share existing methods rather than creating a second runtime or policy
engine. Regenerate native resources from canonical source, never manually.

## Requirements

| ID | Requirement | Observable acceptance | Verification |
|---|---|---|---|
| COMPLETE | Account for all 84 original findings without dropping partial claims. | Each original ID has a current disposition and a cited implementation, contrary evidence, specific decision or exact hold. No subset marks the programme complete. | Exact inventory comparison plus independent claim-to-source review. |
| SOURCE | Implement every ready concrete correction. | Original symptoms no longer occur; useful behavior and authority boundaries survive. | A discriminating regression and affected existing checks for each coherent package. |
| OWNERSHIP | Default inspection never changes supplied artifacts or silently selects another output. | Report-only artifact QA; explicit repair writes a distinct authorized copy or reports a refusal. | QA-source contract and owned-file refusal/preservation fixtures. |
| TRUTH | Advertise only implemented operations and observed guarantees. | No nonexistent flag, hook, role or personal-home fallback is needed by a mandatory step. Missing required observations remain unverified. | Trace named operations to real consumers and negative fixtures. |
| METHOD | Consolidate duplicate procedures without losing capability or evidence. | One method owner, explicit callers, retained original data and documented compatibility. | Caller/dependency closure and source-preservation checks. |
| ACCEPTANCE | Deliver only the reviewed, verified aggregate. | Current generated resources, applicable local checks and hosted CI, independent review and existing SHIP gates pass for that exact result. | Existing repository runners and review/evidence tools. |

The original private inputs are identified by content, not a copied private
history dump: `all-findings.json` SHA-256
`2e1f1086ec041b5017a88a20b7a5c6238683b9ade8fc648ac29e9e40e8342e0f`,
`all-items.json`
`5677e8c45ebec98cc320999f1ed598f2c1a5fd06a09f7c4980608e9ce58bd595`,
and `adjudications.json`
`e62ade101fb001b13ab5a8ff2f9d70a1c3b35f5d3356aac14a3dddb4c5884a7a`.

## Constraints and specific decisions

No change to an accepted architecture decision is implicit in a code correction.
ADR-0026 explicitly retains short leaves; removing that rule needs an explicit
superseding decision. Retiring capabilities, changing pack inheritance or adding
dependencies likewise requires a precise preservation/design decision. These
questions do not block unrelated corrections.

The earlier native-hook and ADR-drafting host refusals apply only to those exact
workflows. Do not retry, reword or assign them elsewhere. No credential inspection,
new external destination, destructive worktree cleanup, policy bypass or historical
evidence rewrite is authorized.

Model efficacy and comparative productivity are separate from source correctness.
Do not invent a model benchmark, empirical benefit or all-client enforcement.

## Profile impact

Use a fresh, explicit context for this owned target and its bundled neutral pack.
No private pack, customer data, live infrastructure or company policy is selected.
The actual profile reference and policy result are recorded at runtime before
BUILD; absent or drifted required policy is not a neutral success.
