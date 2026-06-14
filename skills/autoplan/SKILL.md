---
name: autoplan
layer: foundation
description: Use to run a problem statement through the full planning pipeline in one shot — chains the design doc, strategy review, engineering review, and design review end to end. Reach for it when you want a plan taken from raw problem to fully reviewed without driving each review step by hand.
color: purple
tools: Read, Bash, Edit
voice: internal
cli_support: [claude-code]
---

# /autoplan

Orchestrator skill. Chains the full plan pipeline: `/office-hours` (design doc) → `/plan-ceo-review` (scope) → `/plan-eng-review` (arch + tests) → optionally `/plan-design-review` (UI/UX) → optionally `/plan-devex-review` (DX). One invocation, one design + complete review set, ready to ship.

## When to use

- Big feature or initiative — full plan pipeline is appropriate
- Customer-engagement prep where multiple review tiers add value
- New repo / new project — get scaffolded design + reviews in one chain

## When NOT to use

- Trivial fix / refactor — too heavy. Use `/review` then `/ship`.
- Plan already exists — skip `/office-hours`, run individual review skills.
- Ongoing iterative work — chain overhead exceeds value per cycle.

## Inputs

- Optional `--skip <skill>` — skip a specific skill in the chain (e.g., `--skip plan-design-review` for backend-only work)
- Optional `--include-devex` — add `/plan-devex-review` to the chain (default: skip)
- Optional `--mode <full|minimal>` — `full` (default) runs all 4 reviews; `minimal` runs office-hours + plan-eng-review only

## Workflow

1. **Mode + skip decisions** — confirm what's in the chain via AskUserQuestion (one question listing the proposed chain).
2. **Step 1: /office-hours** — runs full skill. Output: design doc at `~/.lintel/projects/<slug>/<user>-<branch>-design-<datetime>.md` with Status: APPROVED.
3. **Auto-detect scope changes** — if office-hours produced a design doc with major product-direction changes, ensure `/plan-ceo-review` is in the chain (override --skip if needed; explicit operator override allowed).
4. **Step 2: /plan-ceo-review** — runs against the design doc. Output: CEO review log entry + verdict.
5. **Step 3: /plan-eng-review** — runs against the design doc. Output: required Eng Review log entry + 17-task implementation list + REPORT appended to design doc.
6. **Step 4: /plan-design-review** (auto-detected: only fires if design doc has UI scope OR `--include-design-review`) — UI/UX review log entry.
7. **Step 5: /plan-devex-review** (only fires if `--include-devex`) — DX review log entry.
8. **Synthesize:** read all review-log entries from this run, render unified REVIEW REPORT in design doc.
9. **Final verdict:** any review NOT CLEARED → autoplan exits "NOT READY"; all CLEARED → "READY TO IMPLEMENT."

## Report format

```
Autoplan Status: <branch>

Chain: office-hours → plan-ceo-review → plan-eng-review → plan-design-review
Mode: full
Skipped: plan-devex-review (default)

Step 1/4 /office-hours: ✓ design doc APPROVED (~/.lintel/projects/lintel/<user>-main-design-20260527-...)
Step 2/4 /plan-ceo-review: ✓ SCOPE LOCKED (3 forcing-questions answered, 5 premises agreed)
Step 3/4 /plan-eng-review: ✓ ENG CLEARED (6 issues resolved, 2 critical gaps encoded as tasks)
Step 4/4 /plan-design-review: ⏸ SKIPPED — no UI scope detected

Final verdict: ✓ READY TO IMPLEMENT
Design doc: <path>
Task list: 17 implementation tasks
Next: begin Phase 1 implementation OR /ship (if work already done)
```

## Compliance integration

- Each chained skill runs its own 5-always-on session-start check at invocation.
- Autoplan aggregates: if ANY chained skill flagged a Layer 2 violation, autoplan exits NOT READY.

## Failure modes

- **`/office-hours` returns "NEEDS_CONTEXT" or "BLOCKED":** chain pauses. Operator addresses, then re-runs autoplan (idempotent — reads existing design doc if present).
- **`/plan-ceo-review` returns REVISE:** chain pauses. Operator updates design doc per CEO findings, then re-runs autoplan.
- **`/plan-eng-review` Exit Plan Mode Gate fails:** chain pauses. Operator fixes the design doc structure (REVIEW REPORT must be last h2).
- **Any chained skill times out:** report which skill, allow operator to re-run that skill standalone, then resume autoplan.

## Idempotency

Autoplan can be re-run safely. Each chained skill detects existing artifacts (design doc, review-log entries) and either:
- Updates them (if invoked with `--rerun`)
- Skips them (default — only fills missing steps)

Operator controls re-run granularity. Default = only fill what's missing.

## Examples

**Full pipeline:**
```
> /autoplan
Chain: office-hours → ceo-review → eng-review → design-review
[runs all 4 in sequence]
✓ READY TO IMPLEMENT
```

**Backend only, skip design-review:**
```
> /autoplan --skip plan-design-review
Chain: office-hours → ceo-review → eng-review
[runs 3]
✓ READY TO IMPLEMENT
```

**Minimal:**
```
> /autoplan --mode minimal
Chain: office-hours → plan-eng-review (CEO + design + DX skipped)
[runs 2]
✓ READY TO IMPLEMENT
```

**Blocked mid-chain:**
```
> /autoplan
Step 2/4 /plan-ceo-review: ✗ REVISE — wedge specificity not established
Chain paused. Update design doc, re-run /autoplan when ready.
```

## See also

- `/office-hours` — design generator (first step of chain)
- `/plan-ceo-review` — step 2
- `/plan-eng-review` — step 3 (the required gate)
- `/plan-design-review` — step 4 (UI scope only)
- `/plan-devex-review` — opt-in step 5
- `/ship` — runs AFTER autoplan completes
