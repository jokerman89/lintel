---
name: context-cool
layer: foundation
description: Selectively drop context from session — free budget for further warming. Operator picks what to keep.
color: cyan
tools: Read, Bash, Grep
voice: internal
cli_support: [claude-code, codex]
---

You are the context-cool skill — selective context dropping.

## What this skill does

In Claude Code, context isn't directly mutable mid-session — it's append-only. So "cooling" here means: signal to subsequent skills/agents to IGNORE specific loaded content + clean up budget tracking + recommend session-restart if true reduction needed.

For real budget reduction: operator can `/li:context-snapshot` then restart session, then `/li:context-dump` selectively.

## When to use

- Budget tight, need to free for new heavy load
- Specific loaded files no longer relevant (different phase shifted scope)
- Operator wants to declutter conversation context

## When NOT to use

- True early-session (let context grow organically)
- Mid-task (interruption cost > benefit)

## Workflow

### Step 1 — Surface what's loaded

Read `.claude/runtime/state/context-budget.md` to see what was warmed:

```
CURRENTLY LOADED (from context-warm events):

| Source | Files | Tokens (est) | Last accessed |
|---|---|---|---|
| context-warm "ExpressRoute" | 8 files | 12k | 30 min ago |
| context-warm-adrs "networking" | 5 ADRs | 8k | 45 min ago |
| context-warm-customer "acme" | 18 files | 25k | 1 hour ago |

Total warmed: 45k tokens
```

### Step 2 — Operator selects what to drop

AskUserQuestion:
- A) Mark all customer-acme files as IGNORE
- B) Mark all ADR loads as IGNORE  
- C) Keep highest-relevance subset (operator-driven)
- D) Restart session (true cool — operator does manually)

### Step 3 — Apply marker

For selected items, add to `.claude/runtime/state/context-ignore.md`:
```yaml
- source: context-warm "ExpressRoute"
  files: [...]
  ignore_from: <timestamp>
  reason: <operator note or "scope shift">
```

Subsequent skills/agents reading the IGNORE list will downweight or skip these in their reasoning.

(Note: Claude Code's actual context isn't trimmed; this is a coordination signal only.)

### Step 4 — Surface result + recommendation

```
CONTEXT COOL — applied

Marked for IGNORE: <N> file(s)
Effective budget freed: ~<X>k (when subagents respect IGNORE)

True budget reduction requires session restart:
  1. /li:context-snapshot
  2. Restart session
  3. /li:context-dump <snapshot>
  4. /li:context-warm (only what's still needed)
```

### Step 5 — 00-state.md append

```yaml
event: context_cool
ts: <timestamp>
items_marked: <N>
```

## Status protocol

- DONE — markers applied
- DONE_WITH_CONCERNS — markers don't actually reduce context in Claude Code; surface caveat

## Hop-in support

YES.

## Integration

Reads `.claude/runtime/state/context-budget.md`. Writes `.claude/runtime/state/context-ignore.md` for coordination.

## Anti-patterns

- **Treating "cool" as true budget reduction** — it's coordination, not memory cleanup
- **Cooling too aggressively** — operator loses access if they need files later (would need re-warm)

## Voice tier behavior

`voice: internal`.
