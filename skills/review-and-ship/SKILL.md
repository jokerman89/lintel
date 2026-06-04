---
name: review-and-ship
layer: foundation
description: Composite shortcut REVIEW + SHIP + CAPTURE — for when BUILD is done and operator wants to finalize, ship, capture in one chain.
color: cyan
tools: Read, Bash, Grep, Glob
voice: mixed
cli_support: [claude-code, codex]
necessity: OPTIONAL
gap_if_skipped: "Operator loses the REVIEW+SHIP+CAPTURE shortcut for split-session work; the same range is still reachable via /li:cycle --from REVIEW --to CAPTURE, so only the convenience is lost."
---

You are the REVIEW-AND-SHIP composite shortcut.

## What this skill does

Runs REVIEW + SHIP + CAPTURE phases. For when BUILD output is ready and operator wants to ship + capture in one go.

Equivalent to:
```
/li:cycle --from REVIEW --to CAPTURE
```

Closes out a cycle that was previously plan-and-built.

## When to use

- BUILD complete (code shipped to feature branch), ready for review + ship
- Pre-PR finalization
- Composing with `/li-plan-and-build` for split-session work (plan+build session 1, review+ship+capture session 2)
- Cost expectation: ~5-15k tokens, 15-45 min

## When NOT to use

- BUILD not complete — return to BUILD or `/li:cycle --from BUILD`
- Just want review — use `/li:review` standalone
- Just want ship — use `/li:ship` standalone
- Hotfix — use `/li-fix` (skips heavy REVIEW + CAPTURE)

## Workflow

### Step 1 — Pre-flight

Verify:
- BUILD output exists (commits since prior phase start)
- plan.md present and matches current diff scope
- Branch state clean OR operator confirms intentional WIP

### Step 2 — Delegate

```bash
/li:cycle --from REVIEW --to CAPTURE
```

This runs:
- REVIEW (3-stage: spec compliance, code quality, compliance gates)
- SHIP (HARD-RULES, voice + brand gates, PR open / deploy)
- CAPTURE (lessons, ADR, EVOLUTION-LOG, cold-executor trio)

### Step 3 — Post-cycle

After CAPTURE DONE: full cycle summary surfaced per CAPTURE phase output.

## Status protocol

Inherits from /li:cycle. Critical outcomes:
- DONE = shipped + captured cleanly
- DONE_WITH_CONCERNS = shipped but with caveats logged
- BLOCKED at REVIEW = P1 unfixed, loop back to BUILD
- BLOCKED at SHIP = HARD-RULE violation, hard stop

## Pause-points

- REVIEW 3-stage review pauses (between spec compliance / quality / compliance)
- SHIP HARD-RULES re-check + customer-deliverable 4-gate pipeline
- CAPTURE per-lesson and per-ADR draft confirmations

## Hop-in support

n/a — composite shortcut.

## Integration

Delegates to `/li:cycle --from REVIEW --to CAPTURE`.

## Anti-patterns

- **Running on broken BUILD** — review/ship a half-built feature = wasted effort
- **Skipping CAPTURE because "we shipped"** — cold-executor trio + lessons are the durable artifacts
- **Bypassing HARD-RULE re-check at SHIP** — REVIEW passed but pre-ship sanity is mandatory

## Voice tier behavior

`voice: mixed`. SHIP phase surfaces customer-facing artifacts which inherit voice_tier from the active pack (`resolve_pack_field voice.default_tier`; `internal` by default). CAPTURE's release notes follow the same pack voice tier.
