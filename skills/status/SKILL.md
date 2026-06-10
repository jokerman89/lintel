---
name: status
layer: foundation
description: Show what's open right now — alias for /li:jobs list. Single command for "where am I in flight?".
color: yellow
tools: Read, Bash
voice: internal
cli_support:
  - cli: claude-code
    level: full
  - cli: codex
    level: full
---

You are the `status` skill — quick read of in-flight Lintel jobs (v3.8 Feature 1).

## What this skill does

Reads `~/.lintel/jobs/_active.md` (regenerated from each job.yaml on state change) and surfaces it. Equivalent to `/li:jobs list` but kept as a separate command because operators reach for "status" more naturally than "jobs list".

## When to use

- "Where am I right now?" — start of any session, or after a long break
- After invoking a workflow_root skill — verify the job spawned
- After `/li:jobs abort` or `branch` — verify the action landed
- Before opening a new cycle — check if a previous one is still open

## When NOT to use

- For task-level progress within a phase (read the phase's own audit log)
- For external system status (Azure, MS portal, etc.)

## Inputs

No required args. Optional `--all` to include archived jobs in output.

## Workflow

```bash
ACTIVE="$HOME/.lintel/jobs/_active.md"
ARCHIVE="$HOME/.lintel/jobs/_archive"

if [ -f "$ACTIVE" ]; then
  cat "$ACTIVE"
else
  echo "_No active jobs._ (Run /li:cycle or /li:plan to start one.)"
fi

if [ "${1:-}" = "--all" ] && [ -d "$ARCHIVE" ]; then
  echo ""
  echo "## Recently archived (last 7 days)"
  find "$ARCHIVE" -maxdepth 3 -name "job.yaml" -mtime -7 -print 2>/dev/null | \
    head -10 | \
    while read -r f; do
      d=$(dirname "$f")
      id=$(grep '^job_id:' "$f" | awk '{print $2}')
      status=$(grep '^status:' "$f" | awk '{print $2}')
      archived_at=$(grep '^archived_at:' "$f" | awk '{print $2}')
      echo "- $id ($status, $archived_at)"
    done
fi
```

## Voice tier behavior

`voice: internal`. Operator-only diagnostic.

## Status protocol

- **DONE** — output printed
- **NEEDS_CONTEXT** — `_active.md` malformed (rare; user should run `/li:jobs list` to regenerate)

## Hop-in support

YES — always solo-invocable. Most-used Lintel command in the wild.

## Integration

**Reads:**
- `~/.lintel/jobs/_active.md`
- `~/.lintel/jobs/_archive/` (with `--all`)

**Writes:**
- nothing

**Calls into:**
- nothing (pure read)

## Anti-patterns

- Don't pipe to grep/jq — `_active.md` is human-readable markdown
- Don't poll in a loop — file is regenerated on state change, not periodically

## See also

- `/li:jobs` (the controller)
- `/li:resume` (the recovery mechanic)
- `docs/concepts/jobs-system.md`

## Cycle-position footer

Close your report with the shared position footer. Outside an active cycle it renders the thin
ambient line; inside one it shows the operator's position + next step:

```bash
source "$LINTEL_REPO_ROOT/lib/cycle-footer.sh"   # fallback: "$(git rev-parse --show-toplevel)/lib/cycle-footer.sh"
render_cycle_footer                               # auto: thin when no cycle, full/--compact when in one
```

See [ADR-0003](../../docs/adr/0003-cycle-position-footer.md).
