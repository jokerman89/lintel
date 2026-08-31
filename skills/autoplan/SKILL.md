---
name: autoplan
layer: foundation
description: Use to run a problem statement through the full planning pipeline in one shot — chains the design doc, strategy review, engineering review, and design review end to end. Reach for it when you want a plan taken from raw problem to fully reviewed without driving each review step by hand.
color: purple
tools: Read, Bash, Edit
voice: internal
necessity: OPTIONAL
gap_if_skipped: "The same pipeline is reachable by hand (/li:office-hours → /li:plan-ceo-review → /li:plan-eng-review → …); without autoplan the operator drives each review step manually and synthesizes the verdicts."
cli_support:
  - cli: claude-code
    level: full
---

# /li:autoplan

Orchestrator skill. Chains the full plan pipeline: `/li:office-hours` (design doc) → `/li:plan-ceo-review` (scope) → `/li:plan-eng-review` (arch + tests) → optionally `/li:plan-design-review` (UI/UX) → optionally `/li:plan-devex-review` (DX). One invocation, one design + complete review set, ready to ship.

## When to use

- Big feature or initiative — full plan pipeline is appropriate
- Customer-engagement prep where multiple review tiers add value
- New repo / new project — get scaffolded design + reviews in one chain

## When NOT to use

- Trivial fix / refactor — too heavy. Use `/li:fix`, or `/li:review` then `/li:ship`.
- Plan already exists — skip `/li:office-hours`, run individual review skills.
- Ongoing iterative work — chain overhead exceeds value per cycle.

## Inputs

- Optional `--skip <skill>` — skip a specific skill in the chain (e.g., `--skip plan-design-review` for backend-only work)
- Optional `--include-devex` — add `/li:plan-devex-review` to the chain (default: skip)
- Optional `--mode <full|minimal>` — `full` (default) runs all 4 reviews; `minimal` runs office-hours + plan-eng-review only

## Workflow

1. **Mode + skip decisions** — confirm what's in the chain via AskUserQuestion (one question listing the proposed chain).
2. **Step 1: /li:office-hours** — runs full skill. Output: design doc at `.claude/engineering/design-archive/<slug>-design.md` with Status: APPROVED.
3. **Auto-detect scope changes** — if office-hours produced a design doc with major product-direction changes, ensure `/li:plan-ceo-review` is in the chain (override --skip if needed; explicit operator override allowed).
4. **Step 2: /li:plan-ceo-review** — runs against the design doc. Output: CEO review log entry + verdict.
5. **Step 3: /li:plan-eng-review** — runs against the design doc. Output: required Eng Review log entry + implementation task list + REPORT appended to design doc.
6. **Step 4: /li:plan-design-review** (auto-detected: only fires if design doc has UI scope OR `--include-design-review`) — UI/UX review log entry.
7. **Step 5: /li:plan-devex-review** (only fires if `--include-devex`) — DX review log entry.
8. **Synthesize:** read all review-log entries from this run, render unified REVIEW REPORT in design doc.
9. **Final verdict:** any review NOT CLEARED → autoplan exits "NOT READY"; all CLEARED → "READY TO IMPLEMENT."

## Report format

```
Autoplan Status: <branch>

Chain: office-hours → plan-ceo-review → plan-eng-review → plan-design-review
Mode: full
Skipped: plan-devex-review (default)

Step 1/4 /li:office-hours: ✓ design doc APPROVED (.claude/engineering/design-archive/<slug>-design.md)
Step 2/4 /li:plan-ceo-review: ✓ SCOPE LOCKED (3 forcing-questions answered, 5 premises agreed)
Step 3/4 /li:plan-eng-review: ✓ ENG CLEARED (6 issues resolved, 2 critical gaps encoded as tasks)
Step 4/4 /li:plan-design-review: ⏸ SKIPPED — no UI scope detected

Final verdict: ✓ READY TO IMPLEMENT
Design doc: <path>
Task list: <N> implementation tasks
Next: begin Phase 1 implementation OR /li:ship (if work already done)
```

## Compliance integration

- Each chained skill applies the active pack's compliance gates at invocation (`resolve_pack_field compliance.hooks`; none in the neutral `_default` pack).
- Autoplan aggregates: if ANY chained skill flagged a pack compliance gate, autoplan exits NOT READY.

## Failure modes

- **`/li:office-hours` returns "NEEDS_CONTEXT" or "BLOCKED":** chain pauses. Operator addresses, then re-runs autoplan (idempotent — reads existing design doc if present).
- **`/li:plan-ceo-review` returns REVISE:** chain pauses. Operator updates design doc per CEO findings, then re-runs autoplan.
- **`/li:plan-eng-review` Exit Plan Mode Gate fails:** chain pauses. Operator fixes the design doc structure (REVIEW REPORT must be last h2).
- **Any chained skill times out:** report which skill, allow operator to re-run that skill standalone, then resume autoplan.

## Idempotency

Autoplan can be re-run safely. Each chained skill detects existing artifacts (design doc, review-log entries) and either:
- Updates them (if invoked with `--rerun`)
- Skips them (default — only fills missing steps)

Operator controls re-run granularity. Default = only fill what's missing.

## Examples

**Full pipeline:**
```
> /li:autoplan
Chain: office-hours → ceo-review → eng-review → design-review
[runs all 4 in sequence]
✓ READY TO IMPLEMENT
```

**Backend only, skip design-review:**
```
> /li:autoplan --skip plan-design-review
Chain: office-hours → ceo-review → eng-review
[runs 3]
✓ READY TO IMPLEMENT
```

**Minimal:**
```
> /li:autoplan --mode minimal
Chain: office-hours → plan-eng-review (CEO + design + DX skipped)
[runs 2]
✓ READY TO IMPLEMENT
```

**Blocked mid-chain:**
```
> /li:autoplan
Step 2/4 /li:plan-ceo-review: ✗ REVISE — wedge specificity not established
Chain paused. Update design doc, re-run /li:autoplan when ready.
```

## See also

- `/li:office-hours` — design generator (first step of chain)
- `/li:plan-ceo-review` — step 2
- `/li:plan-eng-review` — step 3 (the required gate)
- `/li:plan-design-review` — step 4 (UI scope only)
- `/li:plan-devex-review` — opt-in step 5
- `/li:ship` — runs AFTER autoplan completes
