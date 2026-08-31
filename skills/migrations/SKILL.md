---
name: migrations
layer: foundation
description: Surface pending v4.x migrations at SENSE. Sister to /li:status. Read-only — surfaces operator-callsites still on deprecated shape with grace-window remaining. Per v4.0 Chapter 4 §5.6.
color: yellow
tools: Read, Bash, Glob, Grep
voice: internal
cli_support:
  - cli: claude-code
    level: full
  - cli: codex
    level: full
---

You are the `migrations` skill — pending-migration surfacer (v4.0 Phase 1).

## When to use

- Session-start (auto-invoked by SENSE Step 0c if any migration window is active)
- Standalone: "what migrations are pending?" → `/li:migrations`
- Before invoking a workflow that touches deprecated paths

## When NOT to use

- For ad-hoc renaming questions — use `/li:catalog` or `git grep`
- To actually perform the migration — that's PR work, not surfacing

## Inputs

No required args. Optional `--all` to include CLOSED migrations (last 30 days).

## Workflow

### Step 1 — Read tracker

```bash
TRACKER="$(pwd)/docs/migrations/_INDEX.md"
[ -f "$TRACKER" ] || { echo "_No active migrations._"; exit 0; }
```

### Step 2 — Parse active entries

Each migration file under `docs/migrations/<date>-<slug>.md` declares grace + removal in its frontmatter. The `_INDEX.md` is the catalog. Read both.

For each ACTIVE migration (grace_until > today):
- Grep operator's repo for deprecated callsites
- Compute days remaining in grace window
- Surface 1-line summary

### Step 3 — Surface verdict

```
LINTEL MIGRATIONS — <N> active
══════════════════════════════════════════════════════════════════

⚠ <slug> — grace until <date> (<N> days remaining)
   Old shape: <pattern>
   Detected in: <files>
   Action: <one-line>

⚠ <slug-2> — grace until <date> (<N> days)
   ...

(Run `/li:migrations <slug>` for full migration guide)
```

If no active migrations: `_No pending migrations._`

If operator has zero callsites on any active migration: list still appears but with `   No callsites in current cwd — safe to ignore`.

### Step 4 — Audit (optional)

```bash
source "$(dirname "$0")/../../bin/_audit.sh"
audit_log migration surfaced "active_count=$active_count"
```

## Integration

**Reads:**
- `docs/migrations/_INDEX.md` (catalog)
- `docs/migrations/<date>-<slug>.md` (per-migration detail)

**Writes:**
- `~/.lintel/audit/migration.jsonl` (surface events, optional)

**Consumed by:**
- `/li:sense` Step 0c (auto-invocation)
- Operator standalone

## Anti-patterns

- **Auto-migrating code** — this skill is read-only by design. Migration is operator-driven.
- **Surfacing CLOSED migrations** — wastes operator attention. Use `--all` flag if needed.
- **Hard-blocking on detected callsite** — surface ONLY. Operator decides timing.

## Failure recovery

- Tracker missing: `_No pending migrations._` (silent OK)
- Malformed entry: skip that entry, surface others, log warning
- Grep timeout: cap at 5s, surface partial result

## Recommended next steps after invocation

- Per surfaced migration: read `docs/migrations/<slug>.md` for full migration guide + rollback procedure
- After completing migration: file PR removing operator's old callsites
- After grace expires + removal lands: `/li:migrations` no longer surfaces that entry

## See also

- `/li:status` (sister — what's open right now)
- `docs/migrations/_INDEX.md` (tracker)
- `docs/concepts/meta-infra-discipline.md` (Gate M3 enforcement context)
