---
slug: enterprise-value-review
date: 2026-09-08
cycle_id: enterprise-value-review
affected_paths:
  - lib/pack-resolver.sh
  - lib/orientator-routing.sh
  - lib/scale-estimator.sh
  - hooks/shared/session-digest/run.sh
  - skills/plan/SKILL.md
  - skills/pack-create/SKILL.md
  - skills/pack-validate/SKILL.md
  - skills/scope/SKILL.md
  - skills/build/SKILL.md
  - scaffolding/01-foundation/templates/plan/plan.template.md
risk_class: medium
breaking_change: false
---

# Structure impact: enterprise value review

## Intent and compatibility

Restore existing pack inheritance, missing-field fallback, risk classification and planning
contracts; make applicable pack requirements traceable to task acceptance and evidence.
The runtime fixes follow ADR-0008 and ADR-0018. The operator additionally selected hybrid
execution: short leaves with bounded package execution/review, recorded in ADR-0026.
No new pack schema, policy engine, implicit enterprise control or dormant activation is introduced.

Numeric token-prior callers retain their interface; provenance is additive. Plain and quoted
scalars, supported inline/block lists and inherited required blocks gain consistent treatment.
Malformed required fields and broken ancestry are rejected under the documented validation
contract. Existing invalid-active-pack fallback remains; stronger fail-closed activation is an
explicit unresolved architectural decision, not hidden in this correction.

## Verification and migration

Run existing pack/scale checks, new synthetic enterprise integration cases, shape and unit suites,
then independent review. Record actual results in the audit and plan review. No customer data,
personal installation or production mutation is required. Confirm the installed plugin version
and effective pack on the next session after release; do not clear current session identity silently.

## Rollback and integration

Revert this feature branch's atomic commits through a new reviewed change. No data migration is
needed. The concurrent Copilot branch has overlapping skill/template/resolver edits; reconcile
those file-level changes explicitly before combining the branches. Never replace its working tree
with this one. Its installer and adapter fixes are separate work and are not credited here.
