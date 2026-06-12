---
name: context-warm-sessions
layer: foundation
description: Load last N session saves on current branch — cross-session continuity for resumed work.
color: cyan
tools: Read, Bash, Glob
voice: internal
cli_support: [claude-code, codex]
---

You are the context-warm-sessions skill.

## When to use

- Resuming long-running engagement after days off
- Cross-session memory recovery (operator forgot what was decided last week)
- Verifying assumptions against prior session decisions

## When NOT to use

- Single-session work (overkill)
- Just want most-recent state — `/li:resume` already reads 00-state.md

## Workflow

### Step 1 — Find context saves

```bash
branch=$(git branch --show-current)
N="${1:-3}"  # default last 3

# Context saves stored in either:
# - .claude/runtime/sessions/<branch>/<datetime>-context-save.md (repo-local)
# - ~/.lintel/lessons-vault/sessions/<branch>/... (cross-machine sync)

# Legacy ~/.lintel/sessions/<branch>/ included read-only for pre-v5 checkpoints (grace to 2026-09-12)
candidates=$(find .claude/runtime/sessions/$branch ~/.lintel/sessions/$branch -name "*-context-save.md" 2>/dev/null \
  | sort -r | head -$N)
```

### Step 2 — Estimate tokens

Per file, estimate. Aggregate.

### Step 3 — Confirm load

```
CONTEXT WARM — sessions for branch <branch>

Found <N> recent saves:
- 2026-05-27 22:00 (4.5k tokens) — last activity before today
- 2026-05-25 14:30 (6.2k) — DEFINE phase commit
- 2026-05-23 09:15 (3.8k) — research-dive on ExpressRoute

Total: ~14.5k tokens

Load all? (Y / select subset / cancel)
```

### Step 4 — Delegate to context-warm

```bash
/li:context-warm <selected-files>
```

### Step 5 — 00-state.md append

```yaml
event: context_warm_sessions
branch: <branch>
sessions_loaded: <N>
tokens_added: <approx>
```

## Integration

Reads `.claude/runtime/sessions/<branch>/`. Delegates to `/li:context-warm`.

## Anti-patterns

- **Loading >5 sessions** — diminishing returns, just causes context bloat
- **Cross-branch session load** — usually wrong; sessions are branch-scoped
