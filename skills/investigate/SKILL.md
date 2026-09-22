---
name: investigate
layer: foundation
description: Use when something is broken and you don't yet know why — drives a hypothesis-led investigation that builds a minimum repro, eliminates variables, and isolates the root cause. Reach for it for "why is this failing?" before attempting a fix.
color: orange
tools: Read, Bash, Grep, Glob
voice: internal
cli_support: [claude-code, codex]
---

# /investigate

The debugging skill. Hypothesis-first, scientific-method approach: state what you observe, propose hypotheses, design a minimum repro, eliminate variables one at a time, name the root cause. No speculation, no guess-fix-rerun loops.

Distinct from `/qa --no-fix`: that one runs the suite and reports. This one zooms in on a single failure or anomaly and drives it to root cause.

## When to use

- A test is failing and `/qa` flagged it as product-logic
- Production logs show an anomaly and you need to understand why
- A user-reported bug needs root-cause analysis before a fix design
- A flake is recurring — investigate whether it's actually flake or a real race

## When NOT to use

- The fix is obvious and trivial — just fix it
- You haven't reproduced the issue yet AND can't — use `/qa-only` first to confirm it's real
- It's a UX issue, not a correctness issue — use `/design-review` or `/qa` with browser

## Inputs

- A failure description, redacted error/log or test name from the explicitly selected
  QA result; a newer unrelated report is not the source
- Optional `--scope <file>` — narrow code reading to a specific area
- Optional `--with-codex` retains the explicit outside-review request; inspect the
  actual available authorized tool first. No installed CLI/model or permission is assumed.

## Workflow

1. **State the observation precisely.** Exact assertion/error and relevant redacted
   log evidence; mark redactions rather than reproducing secrets/customer data.
2. **Minimum repro.** Use an inspected command in an owned synthetic target; preserve
   source, staged/dirty/untracked inputs and exact environment. Read-only investigation
   does not authorize live access or mutations just because a shell exists.
3. **Hypothesis set.** Rank plausible explanations by evidence; do not invent
   numerical probabilities without a calibration basis.
4. **Variable isolation.** For each hypothesis, design ONE experiment that distinguishes it. Run it. Update the ranking.
5. **Iterate.** Hypotheses survive or fall. New ones spawn from the experiments. Continue until one hypothesis is confirmed via direct evidence (not just elimination).
6. **Root cause statement.** A single sentence: "X happens because Y, observable at Z." Cite file:line.
7. **Fix recommendation.** NOT a fix. A recommendation — operator decides whether to fix here, escalate, or punt.

For mapped/module work use [original-work admission and handoff](../full-engineering-pass/references/domain-handoff.md#module-caller-procedure):
carry original IDs, source/attempt, pinned profile/policy and actual checks. Record
unresolved hypotheses and next discriminating experiment for cold continuation;
do not automatically rerun a side-effecting repro. For standalone unmapped inspection,
use P05's existing snapshot/inspect route with no invented backlog or release clearance.
An independent second opinion is a real separate context, not another heading.

## Report format

```
Investigation: <one-line failure description>

## Observation
Exact error: <verbatim>
Repro: <minimum command>
First seen: <commit or timestamp>

## Hypotheses (initial)
H1: <hypothesis> — strongest current evidence: <source>
H2: <hypothesis> — plausible, untested: <discriminating case>
H3: <hypothesis> — unresolved: <missing observation>

## Experiments
[E1] Test H1 by <authorized experiment>. Result: <actual observation/exit>.
[E2] Test H2 by <action>. Result: <observation>. CONFIRMED.

## Root cause
src/lib/dlxClient.ts:87 — fetch retries don't reset the AbortController, so the second attempt cancels itself.

## Fix recommendation
Minimal fix: reset controller in the retry path (5-line change).
Risk: low. No callers depend on the canceled-second-attempt behavior.
Recommend: fix here, add regression test.
```

## Compliance integration

- Read-only mode. No code mutation in this skill. If investigation reveals a sec-issue (e.g. token in logs): surface as Layer 2 sanitization concern, do NOT fix in this skill.
- If repro requires customer-data: STOP. Use synthetic data, or escalate to operator for sanitized fixture.

## Failure modes

- **Cannot reproduce:** name that as a finding. "Cannot reproduce in 50 attempts under conditions X, Y, Z" is data, not failure.
- **No hypotheses survive:** preserve evidence and request an available independent
  reviewer/operator, not automatic external-CLI execution.
- **Repro requires production access:** stop, escalate. Per Layer 2: production reads require explicit auth.

## Examples

**Quick win:**
```
> /investigate "refund returns 200 instead of 100"
Observation: tests/billing/test_refund.py:42
Repro: pytest tests/billing/test_refund.py::test_partial_refund -x
H1: amount doubled in serialization (test directly)
H2: refund handler called twice (check call evidence)
H3: test fixture wrong (inspect isolated fixture)
[E1] In an explicitly authorized disposable trial, observe amount=100 in and 200 out.
ROOT CAUSE: src/lib/billing.ts:34 — `* 2` left over from a debug session.
```

**Stuck:**
```
> /investigate "auth flake in CI only"
After 4 experiments: cannot distinguish race vs. network.
Recommendation: enable CI artifact capture (har/trace) on next run, re-investigate.
```

## See also

- `/qa` — when fix is auto-applicable
- Actual available independent reviewer — `/codex` only when explicitly available/authorized
- `/careful` — wrap investigation in extra rigor for prod-impact bugs
- `DebugForensics` subagent — for parallel deeper trace analysis
