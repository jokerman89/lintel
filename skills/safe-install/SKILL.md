---
name: safe-install
layer: foundation
description: Safe-install wrapper for Lintel — version-before-every-change + uninstall-with-restore + visible-announce backup. Operator-request 5.1.
color: yellow
tools: Read, Write, Bash, Glob
voice: internal
cli_support:
  - cli: claude-code
    level: full
  - cli: codex
    level: degraded
---

You are the `safe-install` skill — an operator-protective wrapper around install/uninstall/update operations.

## What this skill does

Defaults for Lintel install operations that the operator explicitly asked for (v3.6 backlog 5.1):

1. **Version-before-every-change** (not just at install) — back up the current LINTEL_HOME state before ANY destructive operation
2. **Uninstall with restore** — default to restoring the latest backup. Currently NO uninstall path (`grep uninstall` = 0 hits in the whole repo)
3. **Update-from-repo OR cmd** — the operator can pinpoint an update from a specific git ref or a live cmd
4. **Make backup visible** — backup path announced explicitly; not silent

Builds on the existing backup pattern (install/install.sh:76 `cp -r "$LINTEL_HOME" "$BACKUP"`). Generalizes it to all destructive ops.

## When to use

- `/li:safe-install --update` (updates Lintel from latest main; auto-backup first)
- `/li:safe-install --uninstall` (clean uninstall + restore latest backup automatically)
- `/li:safe-install --backup-only` (snapshot LINTEL_HOME without changing anything)
- `/li:safe-install --list-backups` (show available restore points)
- `/li:safe-install --restore <backup-id>` (manual restore to a specific snapshot)

## When NOT to use

- First-time install — `install/install.sh` is canonical (this wraps subsequent ops)
- Mid-cycle skill debug — use `bin/li-doctor` instead
- Reading current state — `bin/li-doctor --quick`

## Workflow

### Step 1 — Detect operation mode

```bash
case "${1:-}" in
  --update)        op="update" ;;
  --uninstall)     op="uninstall" ;;
  --backup-only)   op="backup" ;;
  --list-backups)  op="list" ;;
  --restore)       op="restore"; restore_id="${2:?need backup id}" ;;
  *)               echo "Usage: /li:safe-install [--update|--uninstall|--backup-only|--list-backups|--restore <id>]"; exit 2 ;;
esac
```

### Step 2 — Backup current state (on update/uninstall)

```bash
LINTEL_HOME="${LINTEL_HOME:-$HOME/.lintel}"
BACKUP_ROOT="${LINTEL_HOME}.backups"
mkdir -p "$BACKUP_ROOT"

if [ "$op" = "update" ] || [ "$op" = "uninstall" ] || [ "$op" = "backup" ]; then
  ts=$(date +%Y%m%d-%H%M%S)
  backup_path="$BACKUP_ROOT/snapshot-$ts"
  cp -r "$LINTEL_HOME" "$backup_path"

  # VISIBLE ANNOUNCE
  echo "📦 Backup created: $backup_path"
  echo "   ($(du -sh "$backup_path" | awk '{print $1}'))"
  echo "   To restore: /li:safe-install --restore $ts"
  echo ""
fi
```

### Step 3 — Execute operation

**`update`:**
- Pull latest from the configured Lintel-repo source
- Run install/install.sh in update-mode
- Surface a diff summary of changed files
- If anything fails → auto-restore from backup, surface the error

**`uninstall`:**
- Confirm via AskUserQuestion ("Will remove $LINTEL_HOME. Latest backup at <path>. Proceed?")
- Remove $LINTEL_HOME
- Surface "Uninstalled. To restore: /li:safe-install --restore $ts"

**`backup-only`:**
- Just creates backup (Step 2). No state change.

**`list`:**
- ls $BACKUP_ROOT/snapshot-* | format as a table
- Most recent first
- Size + date per snapshot

**`restore`:**
- Locate $BACKUP_ROOT/snapshot-<restore_id>
- Confirm via AskUserQuestion ("Will replace current $LINTEL_HOME with snapshot from <date>. Proceed?")
- Remove current $LINTEL_HOME
- `cp -r <backup> $LINTEL_HOME`
- Verify via `bin/li-doctor --quick`

### Step 4 — Backup retention

Default: keep the last 5 snapshots. Prune those older than 30 days.

```bash
cd "$BACKUP_ROOT"
ls -1t snapshot-* | tail -n +6 | xargs -r rm -rf
find . -maxdepth 1 -name 'snapshot-*' -mtime +30 | xargs -r rm -rf
```

Surface "Pruned N old snapshots (kept latest 5 + recent 30 days)."

## Voice tier behavior

`voice: internal`. Operator-internal infrastructure.

## Status protocol

- **DONE** — operation complete, backup visible, retention enforced
- **DONE_WITH_CONCERNS** — operation complete but retention failed or verify had warnings
- **BLOCKED** — destination not writable, missing $LINTEL_HOME for restore, etc
- **NEEDS_CONTEXT** — `--restore` without a `<backup-id>`

## Pause-points

- On `--uninstall`: hard-block for operator confirmation (destructive op)
- On `--restore`: hard-block for operator confirmation (replaces current state)
- If backup fails mid-update: surface + offer abort

## Hop-in support

YES — solo-invokable for all 5 modes.

## Integration

**Reads:**
- `$LINTEL_HOME` (snapshot source)
- `$BACKUP_ROOT` (restore source)
- `install/install.sh` (for update mode, called as subprocess)

**Writes:**
- `$BACKUP_ROOT/snapshot-<ts>/` (backup target)
- `$LINTEL_HOME` (modified by underlying operation)

**Consumed by:**
- Operator (manual invocation)
- `bin/li-update` (could wrap this instead of doing inline backup) — future refactor

## Anti-patterns

- **Silent backup** — the backup path MUST be announced to the operator. Otherwise the "can't find the backup" pattern recurs.
- **No retention enforcement** — backups become disk spam. Always prune.
- **Skip confirm on destructive ops** — uninstall + restore are both one-way. Always confirm.
- **Backup to the same disk as live** — for safety, recommend the backup path be on a separate disk/path if possible.

## Failure recovery

- Update fails → auto-restore latest backup → exit BLOCKED with error
- Restore fails (corrupted backup): fall back to the previous snapshot, surface a warning
- Disk full → refuse + surface free-space-instructions
