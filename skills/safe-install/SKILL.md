---
name: safe-install
layer: foundation
description: Safe-install wrapper för Lintel — version-before-every-change + uninstall-with-restore + visible-announce backup. Operator-request 5.1.
color: yellow
tools: Read, Write, Bash, Glob
voice: internal
cli_support:
  - cli: claude-code
    level: full
  - cli: codex
    level: degraded
---

You are the `safe-install` skill — operator-protective wrapper runt install/uninstall/update operations.

## What this skill does

Defaults för Lintel install-operations som operator explicit bad om (v3.6 backlog 5.1):

1. **Version-before-every-change** (inte bara at install) — backup current LINTEL_HOME state innan ANY destructive operation
2. **Uninstall with restore** — defaultatt restore latest backup. Currently NO uninstall path (`grep uninstall` = 0 hits i hela repot)
3. **Update-from-repo OR cmd** — operator kan pinpoint update från specific git ref eller live-cmd
4. **Make backup visible** — backup-path announced explicit; ej silent

Bygger på existing backup-pattern (install/install.sh:76 `cp -r "$LINTEL_HOME" "$BACKUP"`). Generaliserar till alla destructive ops.

## When to use

- `/li:safe-install --update` (uppdaterar Lintel från latest main; auto-backup först)
- `/li:safe-install --uninstall` (ren-uninstall + restore latest backup automatically)
- `/li:safe-install --backup-only` (snapshot LINTEL_HOME utan ändring)
- `/li:safe-install --list-backups` (visa available restore points)
- `/li:safe-install --restore <backup-id>` (manual restore till specific snapshot)

## When NOT to use

- First-time install — `install/install.sh` är canonical (denna wrappar för subsequent ops)
- Mid-cycle skill-debug — använd `bin/li-doctor` istället
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

### Step 2 — Backup current state (vid update/uninstall)

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
- Pull latest från config'd Lintel-repo source
- Run install/install.sh in update-mode
- Surface diff-summary av changed files
- If anything fails → auto-restore from backup, surface error

**`uninstall`:**
- Confirm via AskUserQuestion ("Will remove $LINTEL_HOME. Latest backup at <path>. Proceed?")
- Remove $LINTEL_HOME
- Surface "Uninstalled. To restore: /li:safe-install --restore $ts"

**`backup-only`:**
- Just creates backup (Step 2). No state change.

**`list`:**
- ls $BACKUP_ROOT/snapshot-* | format som table
- Most recent first
- Size + date per snapshot

**`restore`:**
- Locate $BACKUP_ROOT/snapshot-<restore_id>
- Confirm via AskUserQuestion ("Will replace current $LINTEL_HOME with snapshot from <date>. Proceed?")
- Remove current $LINTEL_HOME
- `cp -r <backup> $LINTEL_HOME`
- Verify via `bin/li-doctor --quick`

### Step 4 — Backup retention

Default: keep last 5 snapshots. Prune older än 30 dagar.

```bash
cd "$BACKUP_ROOT"
ls -1t snapshot-* | tail -n +6 | xargs -r rm -rf
find . -maxdepth 1 -name 'snapshot-*' -mtime +30 | xargs -r rm -rf
```

Surface "Pruned N old snapshots (kept latest 5 + recent 30 days)."

## Voice tier behavior

`voice: internal`. Operator-internal infrastructure.

## Status protocol

- **DONE** — operation klar, backup visible, retention enforced
- **DONE_WITH_CONCERNS** — operation klar men retention failed eller verify hade warnings
- **BLOCKED** — destination not writable, missing $LINTEL_HOME för restore, etc
- **NEEDS_CONTEXT** — `--restore` utan `<backup-id>`

## Pause-points

- Vid `--uninstall`: hard-block för operator-confirmation (destructive op)
- Vid `--restore`: hard-block för operator-confirmation (replaces current state)
- Vid backup fails mid-update: surface + offer abort

## Hop-in support

YES — solo-invokable för all 5 modes.

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
- `bin/li-update` (could wrap denna instead of doing inline backup) — future-refactor

## Anti-patterns

- **Silent backup** — backup-path MUST be announced till operator. Otherwise "kan inte hitta backup"-pattern återupprepas.
- **No retention enforcement** — backups blir disk-spam. Always prune.
- **Skip confirm på destructive ops** — uninstall + restore är båda one-way. Always confirm.
- **Backup till same disk som live** — for safety, recommend backup-path är på separate disk/path om möjligt.

## Failure recovery

- Update fails → auto-restore latest backup → exit BLOCKED with error
- Restore fails (corrupted backup): fall back till previous snapshot, surface warning
- Disk full → refuse + surface free-space-instructions
