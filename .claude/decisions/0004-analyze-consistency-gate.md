# ADR-0004: Standalone /li:analyze cross-artifact consistency gate

- **Status:** Accepted
- **Date:** 2026-06-10
- **Deciders:** operator (jokerman) + Claude Code session
- **Supersedes:** —
- **Superseded by:** —

## Context

The 2026-06-09 convergent-lessons audit flagged spec-kit's `/analyze` as "the biggest steal":
a read-only, re-runnable cross-artifact consistency check between spec, plan, and tasks. Lintel
already adopted *part* of it — PLAN Step 8 ("Cross-section-analyze, adopted from speckit Analyze
phase", `skills/plan/SKILL.md:156-164`) checks design↔plan coverage at plan time. What Lintel
lacks, verified against the tree on 2026-06-10:

1. **Re-runnability.** Step 8 fires once inside PLAN. Plans get revised (plan-eng-review:
   "after any major plan revision") and BUILD deviates; nothing re-checks consistency after.
2. **The BUILD leg.** Nothing reconciles the finished build against the plan (all tasks
   accounted for; no untasked work shipped) or against the design doc. BUILD's final pass
   (Step 6) runs tests and regression checks only.
3. **A persisted, gateable artifact.** Step 8 emits an ad-hoc gap-list; SHIP cannot gate on it
   and CAPTURE cannot read it.
4. **Authority-doc alignment re-check.** Discover-report ADR constraints are checked at plan
   time only.

Constraint: PLAN Step 8's logic must not be duplicated (shared-schema discipline — define once).

## Decision

We chose a **standalone read-only skill `/li:analyze`** that performs the full three-leg check
(DEFINE↔PLAN, PLAN↔BUILD, authority alignment), persists a severity-classified report to
`.lintel/state/analyze-report.md`, and is *delegated to* by the existing call sites: PLAN Step 8
(plan-time legs) and BUILD's final pass (post-build legs). One implementation, three entry points
(standalone, PLAN, BUILD).

## Alternatives considered

- **Extend PLAN Step 8 + mirror check inline in BUILD**: smaller diff. Rejected because it
  duplicates the check logic in two skills (violates shared-schema discipline), is not
  operator-callable standalone, and still produces no persisted artifact for SHIP.
- **Fold into `/li:plan-eng-review`**: one gate fewer. Rejected because cross-artifact coverage
  is a mechanical check, not the quality-judgment review that skill performs, and the BUILD leg
  does not fit its before-ship timing.
- **Defer**: Step 8 covers the plan-time case today. Rejected by operator 2026-06-10 — the
  BUILD-drift hole is exactly the class of silent failure the v4.11 fail-closed work targets.

## Consequences

- **Positive**: consistency becomes re-checkable at any point in the cycle; BUILD drift gets a
  detection mechanism; SHIP gains a readable verdict artifact; PLAN Step 8 sheds inline logic.
- **Negative / accepted cost**: one more official skill to maintain (catalog 168→169); the
  report is advisory (RED does not hard-block SHIP — pack-driven hard gates can adopt it later);
  the analysis is instruction-driven (agent judgment), not mechanical parsing — findings quality
  depends on the executing model, mitigated by the fixed report schema + severity rubric.
- **Follow-up**: a pack may declare `compliance.hooks` gating on the report verdict; not wired
  by default (the neutral `_default` pack enforces nothing).
