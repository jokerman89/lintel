# ADR-0017: the eval-harness — decide prompt changes on evidence, not intuition

**Status:** Accepted-direction, build staged (2026-06-13)
**Implements:** battletest H1/H5 + the cli-issues-craft synthesis (the recurring "real unlock")

## Context

Every workstream and persona keeps landing on the same gap: Lintel has no way to MEASURE whether
a prompt/skill change helps. The tests assert documentation, not behavior; the cost estimator is
uncalibrated; "generically better" prompt edits can hurt a specific skill (2026 evidence). The
house-style (ADR-0014) is applied with judgment because there is no eval to settle it.

## Decision

Build a lightweight eval-harness: 20-50 real tasks per critical skill (drawn from actual
failures), each with an unambiguous pass/fail verifier (string match → grep → code grader →
fresh-context LLM judge), positive AND negative cases. Run on every skill diff in CI; grow the
set over time. Provider-agnostic (the harness must run across Lintel's CLIs, not just Claude).

## Consequences (when built)

- Every craft rule in ADR-0014, every reinvention, every subtraction becomes evidence-backed.
- It is the foundation the rest should stand on — which is why it keeps recurring. Staged as its
  own cycle because it's the highest-design-leverage item and deserves a focused build, not a
  rushed bolt-on.
- Until it exists, the house-style is the best-evidence default and the behavior tests
  (security-controls-fire, session-leaves-traces) are the behavior-over-prose beachhead.
