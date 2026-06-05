---
name: da-migration-irreversible-warn
tier: warn-only
event: PreToolUse (Edit|Write on migration files)
fires_on: migration file lacks a paired down-migration OR contains destructive operations without documented data-loss acceptance
override: pass --ignore-irreversibility flag (operator decision, logged)
audit: ~/.lintel/audit/hooks.jsonl
---

# da-migration-irreversible-warn

Surfaces when a migration commit lacks a rollback path. Warning, not block — destructive migrations exist; the warn prompts operator to acknowledge.

## What it does

- On commit involving files under `db/migrations/`, `supabase/migrations/`, `migrations/`, or matching `pack.data_architecture.migration_glob`:
  - Pairs each up-migration with the corresponding down-migration (heuristic: same prefix, `.down.sql` suffix OR `down: ` section inside the file)
  - Scans up-migration content for destructive operations (`DROP TABLE`, `DROP COLUMN`, `TRUNCATE`, `ALTER COLUMN ... TYPE`, narrowing changes)
- If destructive AND no rollback path: WARN

## Why warn-only

- Some migrations are deliberately destructive (cleanup after grace window)
- The warn forces operator to acknowledge the irreversibility, not block ship
- Block would require operator to invent a fake down-migration; that's worse than honest documentation of irreversibility

## Override path

`--ignore-irreversibility "reason"` on commit. Reason logged. CI can require an explicit override comment in the commit message for irreversible migrations.

## What's NOT in scope

- Detecting indirect data loss (e.g. column rename that loses precision) — Migrator's analysis
- Auto-generating down-migrations — operator-driven
- Hard-blocking destructive migrations (warn-only by design; v4.3+ may add per-pack opt-in block)

## Audit format

```jsonl
{"hook":"da-migration-irreversible-warn","tier":"warn","ts":"...","file":"db/migrations/0042_drop_legacy.sql","destructive_ops":["DROP TABLE","TRUNCATE"],"has_rollback":false,"operator":"<operator>"}
```
