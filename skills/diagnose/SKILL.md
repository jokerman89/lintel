---
name: diagnose
layer: foundation
description: Use when something is broken and you don't yet know why — drives a hypothesis-led investigation that builds a minimum repro, eliminates variables, and isolates the root cause. Reach for it for "why is this failing?" before attempting a fix.
color: orange
tools: Read, Bash, Grep, Glob
voice: internal
cli_support: [claude-code, codex, copilot]
---

# /diagnose

The debugging skill. Hypothesis-first, scientific-method approach: state what you observe, propose hypotheses, design a minimum repro, eliminate variables one at a time, name the root cause. No speculation, no guess-fix-rerun loops.

Distinct from `/verify`: that workflow runs applicable checks and reports. This one
zooms in on a selected failure or anomaly and drives it to root cause, preserving
the caller's work and a recoverable record of every experiment.

## When to use

- A test is failing and `/verify` flagged it as product-logic
- Production logs show an anomaly and you need to understand why
- A user-reported bug needs root-cause analysis before a fix design
- A flake is recurring — investigate whether it's actually flake or a real race

## When NOT to use

- The fix is obvious and trivial — just fix it
- You haven't reproduced the issue yet AND can't — use `/verify` first to confirm it's real
- It's a UX issue, not a correctness issue — use `/frontend-design-review` with actual rendered evidence

## Inputs

- A failure description, redacted error/log or test name from the explicitly selected
  QA result; a newer unrelated report is not the source
- Optional `--scope <file>` — narrow code reading to a specific area
- Optional `--cross-check` requests a separate opinion through `/cross-check`.
- Optional `--reviewer <name>` selects an actual available reviewer/client for that
  cross-check; it requires `--cross-check`. No installed CLI/model or permission is assumed.

Invocation: `/diagnose <failure-or-selected-QA-result> [--scope <file>] [--cross-check [--reviewer <name>]]`.
An explicit Codex selection is supported through
`/cross-check --hypothesis <text> --reviewer codex`; the current host is not silently changed.

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
7. **Fix recommendation.** NOT a product fix. Hand the confirmed cause, minimum
   repair and regression check to the authorized builder. Existing implementation
   authority still applies; diagnosis does not itself grant a new write scope.

When `--cross-check` is requested, pass the current hypothesis and its selected
source/experiment evidence to `/cross-check --hypothesis <text>`, retaining any
explicit reviewer choice. Compare actual findings; an unavailable separate context
leaves a manual handoff and an open independent-review requirement.

For mapped/module work use [original-work admission and handoff](../full-engineering-pass/references/domain-handoff.md#module-caller-procedure):
carry original IDs, source/attempt, pinned profile/policy and actual checks. Record
unresolved hypotheses and next discriminating experiment for cold continuation;
do not automatically rerun a side-effecting repro. For standalone unmapped inspection,
use P05's existing snapshot/inspect route with no invented backlog or release clearance.
An independent second opinion is a real separate context, not another heading.

## Owned experiments and recovery

Keep the source read-only. Before any experiment, record the source root, HEAD,
selected staged/unstaged/untracked inputs, owned trial path, safe command, environment
and expected effects. A clean-HEAD trial does not represent the caller's uncommitted
work; use only an explicitly scoped copy/patch when that state matters.

For a regression with verified local good/bad bounds, use
[RegressionDetective's isolated bisection procedure](../../agents/engineering/RegressionDetective.md#isolated-bisection-procedure).
It owns one detached trial, not the caller's checkout. Preserve the bisect log and
exit/reset outcome. Missing history does not authorize fetching, and an unreliable
reproducer does not justify calling the first selected commit the confirmed cause.

An experiment that changes an owned fixture needs its pre-images and attributable
post-images. For authorized in-place recovery, reuse `bin/li-snapshot.py` from the
trusted source with explicit files and a separate store; no second rollback format.
Restore only after its ownership and conflict preflight. Unknown or later user edits
block restore. Never stash, reset, clean or switch the caller's checkout.

After an interrupted experiment, preserve its journal, trial, source/attempt,
original work IDs and pinned profile reference. Check whether an owned process is
still running and inspect actual effects before any continuation. Do not automatically
rerun a repro, reset a different trial or erase a failed result. A bisect reset is
limited to its recorded trial after inspecting that trial's state. A failed reset or
snapshot restore remains a recovery blocker with exact remaining state; cleanup is
separately authorized, not a prerequisite for reporting useful findings.

The diagnosis handoff includes observed commands/exits, redacted evidence, remaining
hypotheses, actual ownership, recovery status and the next discriminating experiment.
No progress label or report heading substitutes for that evidence.

## Report format

```
Diagnosis: <one-line failure description>

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

## Ownership and recovery
Source/attempt: <exact source, selected work and attempt>
Trial: <owned location or not created>
Recovery: <not needed | observed complete | interrupted/blocked with evidence>
Unrun checks and next experiment: <explicit scope>
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
> /diagnose "refund returns 200 instead of 100"
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
> /diagnose "auth flake in CI only"
After 4 experiments: cannot distinguish race vs. network.
Recommendation: enable CI artifact capture (har/trace) on next run, re-investigate.
```

## See also

- `/verify --repair` — bounded, explicitly authorized fixes after the cause is established
- `/cross-check` — an actual available independent reviewer or a retained manual handoff
- For production-impact diagnosis, establish explicit access authority and recovery
  boundaries; a safety label never grants live access.
- `DebugForensics` subagent — for parallel deeper trace analysis
