---
name: plan-and-build
layer: foundation
description: Composite shortcut PLAN + BUILD — for when DEFINE+DISCOVER are done (have design doc) but PLAN and BUILD still need execution. Skips REVIEW/SHIP/CAPTURE.
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

## When to use

- Design doc APPROVED, ready to break into tasks + execute
- Multi-day work where operator runs PLAN+BUILD this session, REVIEW+SHIP later
- Iterative dogfood — build, dogfood, fix in same iteration before formal REVIEW
- Cost expectation: ~20-40k tokens, 45min - 2 hours (depends on BUILD scope)

## When NOT to use

- No APPROVED design doc — use `/li:cycle` or `/li:define` first
- Ready to ship — use `/li:cycle` (full) or compose with `/li-review-and-ship` after
- Hotfix — use `/li-fix` (skips PLAN's heavy ceremony)
- Just plan, no build — use `/li:plan` standalone

## Workflow

### Step 1 — Pre-flight

Verify:
- APPROVED design doc exists in docs/design/
- Operator on feature branch (not main)
- Context available for PLAN

If missing: surface, suggest `/li:define` first OR `/li:cycle` for full chain.

### Step 2 — Delegate

```bash
/li:cycle --from PLAN --to BUILD --skip CAPTURE
```

Note: only --skip CAPTURE; SENSE still runs (always, cheap) and verifies state.

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
  - spec.md (DRAFT, finalized in CAPTURE)
  - Code commits on current branch
  - build-log.md
```

## Status protocol

Inherits from /li:cycle. Most relevant: BUILD DONE/BLOCKED.

## Pause-points

- PLAN cost-estimate gate + founder approval gate
- Per-task two-stage review during BUILD
- HARD-RULE hooks if the active pack's compliance mode is `hard` (`resolve_pack_field compliance.mode`; advisory by default)

## Hop-in support

n/a — itself is a hop-in composite.

## Integration

Delegates to `/li:cycle --from PLAN --to BUILD`.

## Anti-patterns

- **Skipping REVIEW indefinitely** — fine to defer one cycle, dangerous as habit
- **Treating this as faster /li-cycle** — it just skips review/ship/capture; total cost similar minus those phases
- **Running on main** — same hard rule as BUILD, never on main without consent

## Voice tier behavior

`voice: internal`.
