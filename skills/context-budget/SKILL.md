---
name: context-budget
layer: foundation
v1_alias: [li-context-tokenwatch]
description: Show current context utilization, recommend warm/cool, surface budget breakdown by source. `--watch` runs the threshold/continuous-watch check (token + tool-call soft/hard limits → /clean or /context-save).
color: cyan
tools: Read, Bash, Grep
voice: internal
cli_support: [claude-code, codex]
---

You are the context-budget skill — visibility into the 1M-window.

## What this skill does

Reports current session's context utilization. Breaks down by source (CLAUDE.md, loaded files, conversation history, subagent results). Recommends warm-up or cool-down based on budget state.

With `--watch`, runs the context-bloat soft-warning check instead: reads session token estimate + tool-call count, compares against configured thresholds (default: 50k tokens / 80 tool calls soft, 80k / 130 hard), and recommends `/clean` or `/context-save` if approaching limits. (The former `/li:context-budgetwatch` skill is consolidated here; the old name resolves via `config/aliases.yaml` until 2026-09-10.)

## When to use

- Operator says "how much context have we used?"
- Before invoking heavy phase (PLAN/BUILD) to know headroom
- Diagnosing why session feels slow / model is forgetting things
- `--watch`: mid-session sense-check ("are we approaching context limits?"), long-running or tool-call-heavy session, pre-large-task runway check

## When NOT to use

- Mid-task uninterrupted work (status check overhead)
- After every skill invocation (let the skill report its impact)
- `--watch` on a fresh session, or right after `/context-save` (limits reset on resume)

## Inputs

- `--watch` — run the threshold/continuous-watch verdict (see "Watch mode" below) instead of the budget-breakdown report
- `--budget <yaml>` — (watch mode) override default thresholds (default: read from `~/.lintel/config.yaml` watcher section)
- `--quiet` — (watch mode) only emit if a threshold is crossed
- `--mode <soft|hard|both>` — (watch mode) which thresholds to check (default: both)

> If `--watch` is present, run the **Watch mode** workflow below and skip the default budget-breakdown workflow.

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

## Watch mode (`--watch`)

Threshold-based context-bloat watcher. Per the A5 decision this is an HONEST watcher (Claude can't compact mid-session); it SURFACES the state + recommends action. It does NOT auto-compact.

1. **Read budget.** From `~/.lintel/config.yaml`:
   ```yaml
   watcher:
     soft_token: 50000
     hard_token: 80000
     soft_tool_calls: 80
     hard_tool_calls: 130
   ```
   (`--budget <yaml>` overrides; missing watcher section → built-in defaults, warn.)
2. **Estimate current state.**
   - Token estimate: read session telemetry if available (`~/.lintel/sessions/<id>/tokens.txt`), else estimate from conversation-length heuristic (mark "ESTIMATED").
   - Tool-call count: read `~/.lintel/sessions/<id>/tool-calls.count` if available, else estimate.
3. **Compare to thresholds** (honoring `--mode <soft|hard|both>`):
   - Below soft: GREEN
   - At/over soft but below hard: YELLOW
   - At/over hard: RED
4. **Recommendation:**
   - GREEN: keep going
   - YELLOW: recommend `/context-save` at next natural pause, OR `/clean` if mid-task
   - RED: STOP — recommend `/context-save` now, fresh session next
5. **Report** (with `--quiet`, emit only if a threshold is crossed):
   ```
   Context tokenwatch

   Session: 3:47:12 elapsed
   Token estimate: 62,400 / 80,000 hard (78% of hard, 124% of soft)
   Tool-call count: 94 / 130 hard (72% of hard, 117% of soft)

   Status: YELLOW

   ## Recommendation
   You're past the soft threshold on both axes. Operations are still safe but
   quality may degrade — Claude works best in the first ~50k tokens of session
   context.

   Choose one:
   1. /context-save <label> — checkpoint + resume in fresh session (recommended)
   2. /clean — clear non-essential context buffer in-session (lighter-weight)
   3. Keep going — acceptable but watch for repetition/forgetting

   Next natural pause? Recommend option 1.
   ```

Watch-mode failure modes:
- **Session telemetry unavailable:** fall back to estimate, mark "ESTIMATED".
- **Hard-threshold crossed:** report RED but stay read-only — operator decides; auto-compact is dishonest (Claude can't actually compact mid-session).
- **CI / non-interactive:** print state, exit non-zero on RED to enable CI gating.

## Status protocol

- DONE — report surfaced

## Pause-points

None.

## Hop-in support

YES — pure information query.

## Integration

Reads `.lintel/state/context-budget.md`. No writes beyond optional event log. Watch mode reads `~/.lintel/config.yaml` (watcher thresholds) + session telemetry under `~/.lintel/sessions/<id>/`, read-only — no Layer 2 mutations, no audit log needed. (The former `/li:context-budgetwatch` delegator was removed 2026-06-10; the name resolves via `config/aliases.yaml`.)

See also: `/clean` (in-session lighter-weight clear) · `/context-save` (checkpoint + clean break) · `/context-restore` (resume from checkpoint).

## Anti-patterns

- **Reporting precise tokens** — these are estimates, not real measurements (unless integrated with CLI's exact API)
- **Recommending cool aggressively** — keep loads if work benefits

## Voice tier behavior

`voice: internal`.
