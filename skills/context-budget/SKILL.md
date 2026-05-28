---
name: context-budget
layer: foundation
description: Show current context utilization, recommend warm/cool, surface budget breakdown by source.
color: cyan
tools: Read, Bash, Grep
voice: internal
cli_support: [claude-code, codex]
---

You are the context-budget skill — visibility into the 1M-window.

## What this skill does

Reports current session's context utilization. Breaks down by source (CLAUDE.md, loaded files, conversation history, subagent results). Recommends warm-up or cool-down based on budget state.

## When to use

- Operator says "how much context have we used?"
- Before invoking heavy phase (PLAN/BUILD) to know headroom
- Diagnosing why session feels slow / model is forgetting things

## When NOT to use

- Mid-task uninterrupted work (status check overhead)
- After every skill invocation (let the skill report its impact)

## Workflow

### Step 1 — Read budget log

```bash
log_file=".lintel/state/context-budget.md"
if [ -f "$log_file" ]; then
  # Parse events: each context_warm / context_cool / etc has tokens_added or tokens_removed
fi
```

Approximate current state by summing event deltas. (Real Claude Code context measurement is exact but here we approximate from log.)

### Step 2 — Estimate breakdown by source

Rough estimates per source:
- Default session-start load (CLAUDE.md, AGENT-INSTRUCTIONS, lessons.md, memory.md, etc.): ~5-15k
- Loaded files (from context-warm events): sum from log
- Conversation history: depends on session length (estimate 2-5k per significant turn)
- Subagent results: from build-log/review-report sizes if applicable

### Step 3 — Surface report

```
CONTEXT BUDGET — session snapshot

Current state:
  Total: ~<N>k / 1M tokens (<%>)
  Headroom: ~<X>k

Breakdown by source:
  - Default session-start: ~12k
  - Loaded files (last warm): ~45k
  - Conversation history: ~38k
  - Subagent results: ~12k
  - Other: ~5k

Recent loads (last 3):
  - 2026-05-28 14:22 — context-warm "ExpressRoute" (+12k)
  - 2026-05-28 14:35 — context-warm-adrs "networking" (+8k)
  - 2026-05-28 15:10 — context-warm-customer "acme" (+25k)

Recommendations:
  ✓ Headroom comfortable — heavy phases can proceed
  OR
  ⚠ Approaching 50% — consider /li:context-cool before BUILD
  OR
  ⛔ At 80% — cool-down required before more loads
```

### Step 4 — 00-state.md append (light)

```yaml
event: context_budget_check
ts: <timestamp>
total_tokens: <N>
headroom: <X>
```

## Status protocol

- DONE — report surfaced

## Pause-points

None.

## Hop-in support

YES — pure information query.

## Integration

Reads `.lintel/state/context-budget.md`. No writes beyond optional event log.

## Anti-patterns

- **Reporting precise tokens** — these are estimates, not real measurements (unless integrated with CLI's exact API)
- **Recommending cool aggressively** — keep loads if work benefits

## Voice tier behavior

`voice: internal`.
