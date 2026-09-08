# ADR-0026: short leaves with package execution and review

**Status:** Accepted
**Date:** 2026-09-08
**Decider:** operator, explicitly selected the hybrid option during the enterprise value review
**Supersedes:** the per-leaf dispatch/review portions of `docs/concepts/planner-as-module.md` and `skills/build/SKILL.md`; the short-leaf constraint remains

## Context

Lintel used a fresh implementer and two review stages per small task. Short leaves preserve
traceability, but repeating context setup and review around related changes can cost more
than it adds. Enterprise work also needs clear ownership, integrated verification and
evidence that company requirements changed the delivered result.

## Decision

Keep 2–5 minute leaf tasks with stable IDs, dependencies and acceptance criteria. Group
related leaves into a bounded work package with one outcome, write owner and compatible
edit/risk boundary. One implementer executes the leaves in dependency order; one spec
review and one quality review cover the package, every leaf and their integration.

Select review depth from aggregate package complexity. Substantive packages require
independent review; a coordinator can review a mechanical package inline. Self-review does
not replace independent review. Separate incompatible ownership, approval or rollback
boundaries. Missing evidence or a blocked leaf keeps the package open.

Packages run sequentially by default. Existing leaf IDs/statuses remain authoritative;
package IDs annotate plans and evidence without a new scheduler or job-state schema.
Legacy plans without grouping behave as singleton packages. Existing authorization,
cost-estimate, compliance and PLAN approval requirements remain in force.

## Alternatives

1. Keep a fresh implementer/review per leaf: strongest isolation, highest repeated setup cost.
2. Replace short leaves with risk-sized tasks: fewer records, but loses the existing short-task
   handoff discipline and needs broader calibration.
3. **Hybrid (chosen):** preserve leaf traceability while sharing execution context and review
   for coherent outcomes. Requires explicit ownership and full leaf coverage.

## Consequences and evidence

The intended benefit is less repeated context and review overhead with unchanged acceptance
coverage. This is not yet a measured productivity claim. Synthetic behavior tests cover
helper changes; independent scenario review assesses the workflow instructions. A pilot
must compare measured usage, rework, defects and cold-session recovery per accepted outcome.

Relevant sources: `docs/enterprise-profile-value.md`, `docs/concepts/agent-dispatch-rules.md`,
ADR-0008 (behavior evidence), ADR-0021 (staged model eval harness).
