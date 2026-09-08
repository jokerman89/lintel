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
  - hooks/shared/_input.sh
  - hooks/shared/_patterns.sh
  - bin/_context.sh
  - bin/_jobs.sh
  - bin/li-review-log
  - bin/li-review-read
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

Completion integrates the accepted Copilot source/target and Spec Kit work-map contracts from
main `e9911fc`. Review helpers now keep source code separate from target state. Context naming
adds a canonical-repository hash; repository-local older files remain discoverable, while shared
legacy files require ownership evidence or an explicitly selected path. No checkpoint is deleted.
The shared jobs registry uses a directory lock around atomic replacement; timeout or read/write
failure preserves the previous view. Job files remain authoritative. A stale lock requires
confirming its writer has stopped before removal; it is never stolen automatically.

Git gate collection now inspects full selected source ancestry without local tracking exclusions
or replacement objects. Read errors and unsupported/dynamic commands block recognized mutations.
Split unsupported chains into literal commands; the existing audited override remains explicit.
This changes permissive failure behavior to the existing ADR-0013 intent. It introduces no remote
reads, cutoff, cache, new hook registration or platform enforcement claim.
Shared scanner failures now propagate to callers: block hooks stop and warning hooks preserve
their warning-only behavior. Successful scans with no matches retain the existing empty result.

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
with this one. Its installer and adapter fixes are integrated from main and verified as part
of the combined tree; authorship remains in their original commits.
