---
name: context-budgetwatch
layer: ms-team
v1_alias: [li-context-tokenwatch]
description: Manual context-bloat check — token + tool-call thresholds, recommendation to /clean or /context-save.
color: yellow
tools: Read, Bash
voice: internal
cli_support: [claude-code]
---

# /context-budgetwatch

Manual trigger for the context-bloat soft-warning system. Reads session token estimate + tool-call count, compares against configured thresholds (default: 50k tokens / 80 tool calls soft, 80k / 130 hard), recommends `/clean` or `/context-save` if approaching limits.

Per A5 decision: this is a HONEST watcher (Claude can't compact mid-session); the skill SURFACES the state + recommends action. It does NOT auto-compact.

## When to use

- Mid-session sense-check: "are we approaching context limits?"
- Long session has been running, want to know if a checkpoint is overdue
- Tool-call-heavy work (lots of file reads, lots of bash) — proactive check
- Pre-large-task: about to do something expensive, want to know runway first

## When NOT to use

- Fresh session — pointless
- Just ran `/context-save` — limits are about to reset on resume anyway
- Inside another skill's workflow — that's the wrong place to trigger this

## Inputs

- Optional `--budget <yaml>` — override default thresholds (default: read from `~/.lintel/config.yaml` watcher section)
- Optional `--quiet` — only emit if a threshold is crossed
- Optional `--mode <soft|hard|both>` — which thresholds to check (default: both)

## Workflow

1. **Read budget.** From `~/.lintel/config.yaml`:
   ```yaml
   watcher:
     soft_token: 50000
     hard_token: 80000
     soft_tool_calls: 80
     hard_tool_calls: 130
   ```
2. **Estimate current state.**
   - Token estimate: read session telemetry if available (`~/.lintel/sessions/<id>/tokens.txt`), else estimate from conversation length heuristic.
   - Tool-call count: read `~/.lintel/sessions/<id>/tool-calls.count` if available, else estimate.
3. **Compare to thresholds.**
   - Below soft: GREEN
   - At/over soft but below hard: YELLOW
   - At/over hard: RED
4. **Recommendation:**
   - GREEN: keep going
   - YELLOW: recommend `/context-save` at next natural pause, OR `/clean` if mid-task
   - RED: STOP — recommend `/context-save` now, fresh session next
5. **Report.**

## Report format

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

## Compliance integration

- Read-only operation. No Layer 2 mutations.
- Watcher thresholds operator-configurable per Layer 4 (power-user) — not load-bearing for compliance, but useful for productivity.
- Audit log not needed (informational only).

## Voice tier note

`voice: internal`. Operational meta-skill, engineering-internal.

## Failure modes

- **Session telemetry unavailable:** fall back to estimate. Mark "ESTIMATED" in output.
- **`~/.lintel/config.yaml` missing watcher section:** use built-in defaults, warn.
- **Hard-threshold crossed:** report RED but skill itself stays read-only. Operator decides next move; auto-compact is dishonest (Claude can't actually compact mid-session).
- **In a CI environment / non-interactive:** print state, exit non-zero on RED to enable CI gating.

## Examples

**Routine check:**
```
> /context-budgetwatch
[62k tokens, 94 tool calls]
YELLOW. Recommend /context-save at next pause.
```

**Hard limit:**
```
> /context-budgetwatch
[82k tokens, 135 tool calls]
RED. STOP — /context-save now, resume in fresh session.
```

**Quiet mode:**
```
> /context-budgetwatch --quiet
[Below thresholds: no output, exit 0]
[Above thresholds: terse warning, exit 1]
```

## See also

- `/clean` — in-session lighter-weight clear
- `/context-save` — checkpoint + clean break for fresh session
- `/context-restore` — resume from checkpoint
- `~/.lintel/config.yaml` — watcher threshold config
- Layer 4 power-user docs — watcher tuning
