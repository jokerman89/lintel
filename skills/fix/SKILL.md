---
name: fix
layer: foundation
description: Use for a known bug with a clear fix path that needs to ship now — runs the abbreviated SENSE, BUILD, REVIEW, SHIP path and skips design, discovery, and planning. The hotfix shortcut; reach for it when the diagnosis is already done and only the fix remains.
color: cyan
tools: Read, Bash, Grep, Glob
voice: internal
cli_support: [claude-code, codex]
hop_in: no
necessity: OPTIONAL
gap_if_skipped: "Operator loses the one-word hotfix shortcut; the identical workflow is still reachable via /li:cycle --mode hotfix, so no capability is lost — only the convenience."
---

You are the FIX composite shortcut — hotfix mode pre-baked. Not nestable — /li:fix is itself the hop-in shortcut.

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

## Integration

Delegates to `/li:cycle --mode hotfix`. No new behavior beyond that.

## Anti-patterns

- **Using /li-fix for new feature work** — bypass DEFINE/PLAN = guaranteed scope drift
- **Skipping CAPTURE when fix reveals durable lesson** — soft-prompted post-hoc, don't ignore
