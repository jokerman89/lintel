---
name: context-snapshot
layer: foundation
description: Save current context state to disk — operator-named snapshot for later resume via /li:context-dump.
color: cyan
tools: Read, Bash, Write
voice: internal
cli_support: [claude-code, codex]
---

You are the context-snapshot skill.

## What this skill does

Saves current session state to `~/.lintel/sessions/<branch>/<datetime>-snapshot-<name>.md`. Different from `/li:context-save` (which writes canonical end-of-session save) — snapshot is operator-named mid-session preservation.

## When to use

- Mid-cycle "save point" before risky operation
- Branching exploration: snapshot baseline, try approach A, restore if needed
- Pre-deep-dive: snapshot before loading heavy context, can revert

## When NOT to use

- End of session (use `/li:context-save` — canonical save)
- Just want to commit code (use git WIP commit)

## Workflow

### Step 1 — Capture state

```bash
name="${1:-mid-session}"
branch=$(git branch --show-current)
ts=$(date +%Y%m%d-%H%M%S)
snap_path="$LINTEL_HOME/sessions/$branch/${ts}-snapshot-${name}.md"

mkdir -p "$LINTEL_HOME/sessions/$branch"
```

### Step 2 — Write snapshot

Structure:
```yaml
---
snapshot_name: <name>
branch: <branch>
ts: <timestamp>
operator: <whoami>
cycle_id: <if active>
phase: <current phase if cycle active>
---

# Snapshot: <name>

## Active state
- WorkProfile: <on/off>
- Mode: <preset>
- Role: <active id or null>
- Voice tier: <effective>
- Azure focus: <on/off>

## Context budget at snapshot
- Tokens used: <approx>
- Loaded files (last warm): <list>

## Open todos
[Read TodoWrite state if available]

## Recent commits
$(git log --oneline -5)

## 00-state.md snapshot
[Copy current .lintel/state/00-state.md content]

## Operator note
[Optional: prompt operator for note]
```

### Step 3 — Confirm + write

```bash
echo "Snapshot saved: $snap_path"
echo "Restore later: /li:context-dump $(basename $snap_path)"
```

### Step 4 — 00-state.md append

```yaml
event: context_snapshot
name: <name>
path: <snap_path>
ts: <timestamp>
```

## Status protocol

- DONE / BLOCKED (write permission)

## Hop-in support

YES.

## Integration

Reads cwd state. Writes `~/.lintel/sessions/<branch>/`.

## Anti-patterns

- **Snapshot without name** — make names mnemonic ("before-azure-deep-dive" beats "save1")
- **Frequent snapshots** — 3-5 per session max, beyond that get lost

## Voice tier behavior

`voice: internal`.
