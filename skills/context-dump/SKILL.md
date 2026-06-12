---
name: context-dump
layer: foundation
description: Read prior session's context-save output and inject into current session. Cross-session memory recovery.
color: cyan
tools: Read, Bash, Glob
voice: internal
cli_support: [claude-code, codex]
---

You are the context-dump skill.

## What this skill does

Reads a specific prior session's `/li:context-save` output and dumps it into current session. Useful when operator knows exactly which session's state to recover.

## When to use

- Operator references a specific session ("the one from last Tuesday")
- Recovering after laptop crash / session loss
- Cherry-picking specific decision context from a known prior session

## When NOT to use

- Don't know which session — use `/li:context-warm-sessions <N>` instead (loads last N)
- Just want most-recent state — `/li:resume` handles that
- Loading entire session history — too heavy; use `/li:context-warm-sessions` with limit

## Workflow

### Step 1 — Identify session

```bash
session_id="$1"  # e.g., "2026-05-27-2200" or just date
branch="${2:-$(git branch --show-current)}"

# Find matching context-save
# Legacy ~/.lintel/sessions/<branch>/ included read-only for pre-v5 checkpoints (grace to 2026-09-12)
candidates=$(find .claude/runtime/sessions/$branch ~/.lintel/sessions/$branch -name "*${session_id}*" -name "*-context-save.md" 2>/dev/null)

if [ -z "$candidates" ]; then
  echo "No session matched '$session_id' on branch '$branch'"
  # List recent sessions
  /li:context-warm-sessions --list
  exit 1
fi

# If multiple matches, pick most-specific or ask
```

### Step 2 — Read + estimate

```bash
file_size=$(wc -c < "$candidates")
est_tokens=$((file_size / 4))
```

### Step 3 — Surface preview

```
CONTEXT DUMP — <session-id>

File: <path>
Size: <chars> (~<tokens>k)
Date: <ts>
Branch: <branch>
Last skill invoked: <from frontmatter if present>

Excerpt (first 30 lines):
[show preview]

Load full? (Y / cancel)
```

### Step 4 — Delegate to context-warm

```bash
/li:context-warm "<full-path>"
```

### Step 5 — 00-state.md append

```yaml
event: context_dump
source_session: <id>
tokens_added: <approx>
```

## Status protocol

- DONE / BLOCKED (no match)

## Hop-in support

YES.

## Integration

Reads `.claude/runtime/sessions/<branch>/`. Delegates to `/li:context-warm`.

## Anti-patterns

- **Dumping ancient sessions** (>90 days): stale assumptions, surface age warning
- **Dumping multiple sessions back-to-back**: use `/li:context-warm-sessions` for that pattern

## Voice tier behavior

`voice: internal`.
