---
name: context-warm-adrs
layer: foundation
description: Load topic-relevant ADRs into context — design constraints + prior decisions surfaced for current work.
color: cyan
tools: Read, Bash, Grep, Glob
voice: internal
cli_support: [claude-code, codex]
---

You are the context-warm-adrs skill.

## What this skill does

Scans `.claude/decisions/*.md` for ADRs matching a topic. Loads relevant ones into session context. ADRs are durable architecture constraints — knowing them prevents re-deriving or contradicting prior decisions.

## When to use

- Pre-PLAN when wedge touches area with prior ADRs
- DEFINE phase if operator suspects related prior decision
- Cross-repo ADR scan (sometimes via `bin/li-lessons-sync`-style remote)

## When NOT to use

- No ADR directory exists (skip silently)
- ADRs already loaded by SENSE (already in context)

## Workflow

### Step 1 — Scan ADRs by topic match

```bash
topic="$1"

# Find ADRs with topic in title or body
matched_adrs=$(grep -rli "$topic" .claude/decisions/*.md 2>/dev/null)

# Per match, extract metadata
for adr in $matched_adrs; do
  num=$(basename "$adr" | sed 's/^\([0-9]*\)-.*/\1/')
  title=$(grep '^# ' "$adr" | head -1 | sed 's/^# //')
  status=$(grep -i '^status:' "$adr" | head -1)
  ts=$(grep -i '^date:' "$adr" | head -1)
done
```

### Step 2 — Filter by status

Operator can flag:
- `--accepted-only`: just Accepted ADRs
- `--include-deprecated`: include Deprecated/Superseded
- Default: Accepted + Proposed

### Step 3 — Surface candidate list

```
ADRs MATCHING "<topic>":

| # | Title | Status | Date | Tokens (est) |
|---|---|---|---|---|
| 0042 | <title> | Accepted | 2026-04 | 1.2k |
| 0058 | <title> | Proposed | 2026-05 | 0.8k |
| 0023 | <title> | Deprecated | 2025-11 | 0.5k |

Total est: <X>k tokens

Load all? (Y / accepted only / select subset / cancel)
```

### Step 4 — Delegate to context-warm

```bash
/li:context-warm <selected-adrs>
```

### Step 5 — 00-state.md append

```yaml
event: context_warm_adrs
topic: <topic>
adrs_loaded: <N>
tokens_added: <approx>
```

## Status protocol

- DONE / BLOCKED (no .claude/decisions/ dir or no matches)

## Hop-in support

YES.

## Integration

Reads `.claude/decisions/*.md`. Delegates to `/li:context-warm`.

## Anti-patterns

- **Loading ALL ADRs ever** — filter by topic
- **Loading deprecated without note** — surface explicitly that ADR is deprecated

## Voice tier behavior

`voice: internal`.
