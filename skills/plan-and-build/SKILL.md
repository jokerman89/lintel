---
name: plan-and-build
layer: foundation
description: Use to compose canonical PLAN and BUILD for an approved design or selected work map, retaining original tasks, package reviews and authority while deferring integrated REVIEW, SHIP and CAPTURE.
color: cyan
tools: Read, Bash, Grep, Glob
voice: internal
cli_support: [claude-code, codex]
necessity: OPTIONAL
gap_if_skipped: "Operator loses the PLAN+BUILD shortcut for split-session work; the same range is still reachable via /li:cycle --from PLAN --to BUILD, so only the convenience is lost."
---

You are the PLAN-AND-BUILD composite shortcut.

## What this skill does

Runs PLAN + BUILD phases. Skips DEFINE (design assumed done), DISCOVER (context assumed established), REVIEW/SHIP/CAPTURE (caller invokes separately).

Equivalent to:
```
/li:cycle --from PLAN --to BUILD
```

For incremental development where operator wants to plan + execute but defer review/ship.
This defers the integrated REVIEW phase, not BUILD's required package spec/quality
reviews. Follow [work-map.md](../spec-kit/references/work-map.md) and
[task-relevant intake](../define/references/intake.md); `bin/li-work-artifacts.py`
and `workflow_resume` keep artifact/status/profile selection identical to direct
PLAN/BUILD. A mapped Spec Kit plan does not need a new native checklist.

## When to use

- Design doc APPROVED, ready to break into tasks + execute
- Multi-day work where operator runs PLAN+BUILD this session, REVIEW+SHIP later
- Iterative dogfood — build, dogfood, fix in same iteration before formal REVIEW
- Cost expectation: ~20-40k tokens, 45min - 2 hours (depends on BUILD scope)

## When NOT to use

- No APPROVED design doc — use `/li:cycle` or `/li:define` first
- Ready to ship — use `/li:cycle` (full) or compose with `/li:review-and-ship` after
- Hotfix — use `/li:fix` (skips PLAN's heavy ceremony)
- Just plan, no build — use `/li:plan` standalone

## Workflow

### Step 1 — Pre-flight

Verify:
- An explicitly selected approved design or approved mapped spec/plan/tasks exists
- Operator on feature branch (not main)
- Context available for PLAN

If missing: surface, suggest `/li:define` first OR `/li:cycle` for full chain.

### Step 2 — Delegate

```bash
/li:cycle --from PLAN --to BUILD
```

Read startup context once. Do not add another SENSE phase outside this range,
restart the cycle identity, repeat answered approval questions or manufacture a
separate alias status.

### Step 3 — Post-build

After BUILD DONE, surface:
```
PLAN + BUILD COMPLETE

Phases done: PLAN ✓ BUILD ✓
Phases deferred: REVIEW, SHIP, CAPTURE

To finish cycle later:
  /li:resume → picks up at REVIEW
  OR
  /li:review-and-ship → composite for the rest

Artifacts:
  - plan.md (APPROVED)
  - Original mapped spec/plan/tasks/prompt and their actual approval/evidence status
  - Code commits on current branch
  - build-log.md
```

## Pause-points

- PLAN cost-estimate gate + founder approval gate
- Per-package two-stage review during BUILD, covering each original leaf
- HARD-RULE hooks if the active pack's compliance mode is `hard` (`resolve_pack_field compliance.mode`; advisory by default)

## Integration

Delegates to `/li:cycle --from PLAN --to BUILD`.

## Anti-patterns

- **Skipping REVIEW indefinitely** — fine to defer one cycle, dangerous as habit
- **Treating this as faster /li:cycle** — it just skips review/ship/capture; total cost similar minus those phases
- **Running on main** — same hard rule as BUILD, never on main without consent
