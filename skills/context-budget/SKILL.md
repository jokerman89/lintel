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

### Step 2.5 — Apply 500k soft + 750k hard cap (v3.6 cohort 3 items 2.1+2.2+2.3+3.3)

Mode-aware caps per design-doc D-3a + D-3c (initial defaults, operator-overridable):

```yaml
mode_envelopes:
  hotfix:              { soft: 200k, hard: 300k }
  customer-engagement: { soft: 500k, hard: 750k }
  research-dive:       { soft: 750k, hard: 900k }
  demo-prep:           { soft: 300k, hard: 450k }
  internal-tool:       { soft: 400k, hard: 600k }
```

Workflow:
1. Read current mode from `~/.lintel/profile.yaml` (default: customer-engagement)
2. Look up `soft` + `hard` cap for mode
3. Compute current payload (loaded files + warming-projected-loads from queue)
4. Surface verdict:
   - `payload < soft` → **green pass** (proceed silently)
   - `soft <= payload < hard` → **friction warning** ("near cap, consider --skip-warming-X")
   - `payload >= hard` → **hard block** ("exceeds cap, reduce before handoff")

**Synthetic vs real warming distinction (2.3):**
- Synthetic warming (operator-written brief, agent-assigned context): cheap, doesn't count toward cap
- Real warming (loading actual files via `/li:context-warm-*`): costs, counts against cap

Hard block only triggers on real-warming-driven payload growth.

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
