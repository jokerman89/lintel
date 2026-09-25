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
source_root="${LINTEL_SOURCE_ROOT:?Set the trusted Lintel source root}"
source "$source_root/bin/_context.sh"
branch=$(_context_branch)
N="${1:-3}"  # default last 3
case "$N" in [1-5]) ;; *) echo 'Choose 1–5 sessions.' >&2; exit 1 ;; esac
# Shared legacy checkpoints must belong to the selected repository. Filter
# ownership before choosing the newest N, just as context-restore does.
candidates=$(context_list "$branch") || exit 1
candidates=$(printf '%s\n' "$candidates" | sed -n "1,${N}p")
```

### Step 2 — Estimate tokens

For each candidate call `context_checkpoint "$path"` with a quoted path to get the bounded
size/digest manifest. It uses the same ownership reader as restore, even for legacy saves
outside the repository. Empty interrupted reservations and foreign/unattributed saves are
not candidates. Do not bypass the reader with a raw home-directory glob.

Aggregate source-byte estimates only; active capacity/usage is unknown unless the current
host reports it. Show actual paths, source root/ownership and any missing/changed candidate.

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

Follow `/li:context-warm` admission and host-read steps for the selected checkpoint manifests.
Use the validated `context_checkpoint` path for owned legacy sources; the general repo
selector deliberately refuses out-of-root paths. Loading notes is not restoring source
bytes or authority. Load referenced project files only through a bounded `context_select`
preview, not automatically from every historical "Files touched" line.

### Step 5 — 00-state.md append

```yaml
event: context_warm_sessions
branch: <branch>
sessions_loaded: <N>
estimated_input_tokens: <source-byte estimate, not measured active usage>
```

## Integration

Reads `.claude/runtime/sessions/<branch>/`. Delegates to `/li:context-warm`.

## Anti-patterns

- **Loading >5 sessions** — diminishing returns, just causes context bloat
- **Cross-branch session load** — usually wrong; sessions are branch-scoped
