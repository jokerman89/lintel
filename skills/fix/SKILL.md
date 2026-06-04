---
name: fix
layer: foundation
description: Composite shortcut for hotfix workflow — runs SENSE + BUILD + REVIEW + SHIP, skipping DEFINE/DISCOVER/PLAN/CAPTURE. For known bugs + clear fix path + ship now.
color: cyan
tools: Read, Bash, Grep, Glob
voice: internal
cli_support: [claude-code, codex]
necessity: OPTIONAL
gap_if_skipped: "Operator loses the one-word hotfix shortcut; the identical workflow is still reachable via /li:cycle --mode hotfix, so no capability is lost — only the convenience."
---

You are the FIX composite shortcut — hotfix mode pre-baked.

## What this skill does

Hotfix workflow as a single invocation. Equivalent to:
```
/li:cycle --mode hotfix
```
but with shorter typing. Runs 4 phases (SENSE → BUILD → REVIEW → SHIP), skips the 4 design/plan/capture phases.

## When to use

- Known bug + path to fix is clear
- No design discussion needed (e.g., "null pointer at line 47, add null check")
- Production incident requiring fast ship
- Operator already understands root cause
- Cost expectation: ~5-15k tokens, 10-30 min

## When NOT to use

- New feature work — use `/li:cycle` (full)
- Unclear root cause — use `/li:investigate` first, then `/li:fix`
- Customer-deliverable involved — use `/li:cycle --mode customer-engagement` (the active pack's voice + compliance gates apply)
- Significant architecture change — needs DEFINE + PLAN phases

## Workflow

### Step 1 — Pre-flight

Confirm hotfix mode is appropriate:
- AskUserQuestion (brief): "Hotfix mode skips DEFINE+DISCOVER+PLAN+CAPTURE. Sure root cause is clear and fix path is known? (Y/n)"
- If operator hesitates: suggest `/li:investigate` or `/li:cycle` instead

### Step 2 — Delegate to /li:cycle

```bash
/li:cycle --mode hotfix --from SENSE --to SHIP --skip DEFINE,DISCOVER,PLAN,CAPTURE
```

Mode preset handles:
- audience=solo
- voice_tier=internal
- compliance=minimal (HARD-RULES still enforced per the pack's compliance mode; default advisory)
- Cost expectation pre-set low

### Step 3 — Post-fix

After SHIP DONE, surface:
```
HOTFIX SHIPPED — <commit/PR>

Skipped phases:
  - DEFINE (no design needed for known fix)
  - DISCOVER (no codebase mapping needed)
  - PLAN (single-task work, no breakdown needed)
  - CAPTURE (no durable artifacts to capture)

If this fix reveals a pattern worth capturing (lesson for /li:lessons-promote),
run /li:capture manually now.
```

This is a soft prompt — operator decides if CAPTURE is worth running post-hoc.

## Status protocol

Inherits from /li:cycle. Status reflects underlying cycle outcome.

## Pause-points

- Initial mode-confirmation
- Each underlying phase's pause-points (BUILD's per-task review, SHIP's compliance gates)

## Hop-in support

No — /li-fix is itself a hop-in shortcut. Not nestable.

## Integration

Delegates to `/li:cycle --mode hotfix`. No new behavior beyond that.

## Anti-patterns

- **Using /li-fix for new feature work** — bypass DEFINE/PLAN = guaranteed scope drift
- **Skipping CAPTURE when fix reveals durable lesson** — soft-prompted post-hoc, don't ignore

## Voice tier behavior

`voice: internal`. Inherits cycle's voice_tier per mode (internal for hotfix).
