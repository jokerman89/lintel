---
name: jstack-investigate
layer: foundation
description: Hypothesis-driven bug investigation — minimum repro, eliminate variables, root cause.
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

- A failure description, error message, log excerpt, or test name (passed inline or via the latest `/qa-only` report)
- Optional `--scope <file>` — narrow code reading to a specific area
- Optional `--with-codex` — invoke `/codex` mid-investigation for an outside opinion on the hypothesis set

## Workflow

1. **State the observation precisely.** What's the failure? Exact error, exact assertion, exact log line. No paraphrasing.
2. **Minimum repro.** Smallest possible command/test/script that triggers the failure. If you can't reduce it: surface that as a finding.
3. **Hypothesis set.** Generate 3-5 candidate explanations. Rank by probability. Include "no idea yet" if honest.
4. **Variable isolation.** For each hypothesis, design ONE experiment that distinguishes it. Run it. Update the ranking.
5. **Iterate.** Hypotheses survive or fall. New ones spawn from the experiments. Continue until one hypothesis is confirmed via direct evidence (not just elimination).
6. **Root cause statement.** A single sentence: "X happens because Y, observable at Z." Cite file:line.
7. **Fix recommendation.** NOT a fix. A recommendation — operator decides whether to fix here, escalate, or punt.

## Report format

```
Investigation: <one-line failure description>

## Observation
Exact error: <verbatim>
Repro: <minimum command>
First seen: <commit or timestamp>

## Hypotheses (initial)
H1: <hypothesis> — probability: 0.5
H2: <hypothesis> — probability: 0.3
H3: <hypothesis> — probability: 0.2

## Experiments
[E1] Test H1 by <action>. Result: <observation>. Updates: H1 → 0.1, H2 → 0.7
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

## Voice tier note

`voice: internal`. Investigation reports are engineering-internal — direct, technical, no rhetorical flourish.

## Failure modes

- **Cannot reproduce:** name that as a finding. "Cannot reproduce in 50 attempts under conditions X, Y, Z" is data, not failure.
- **No hypotheses survive after N experiments:** generate a new hypothesis set. If still stuck: write up what's been ruled out, escalate to operator with `/codex` for outside opinion.
- **Repro requires production access:** stop, escalate. Per Layer 2: production reads require explicit auth.

## Examples

**Quick win:**
```
> /investigate "refund returns 200 instead of 100"
Observation: tests/billing/test_refund.py:42
Repro: pytest tests/billing/test_refund.py::test_partial_refund -x
H1: amount doubled in serialization (0.6)
H2: refund handler called twice (0.3)
H3: test fixture wrong (0.1)
[E1] Add print at serialize: amount=100 going in, 200 coming out.
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
- `/codex` — for outside-voice hypothesis review
- `/careful` — wrap investigation in extra rigor for prod-impact bugs
- `DebugForensics` subagent — for parallel deeper trace analysis
