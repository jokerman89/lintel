---
name: da-migration-irreversible-warn
tier: warn-only
event: PreToolUse (Edit|Write on migration files)
fires_on: selected filename has matching SQL text AND no down-file or down-marker hint
audit: .claude/runtime/audit/hooks.jsonl
---

# da-migration-irreversible-warn

An existing optional **filename/regex heuristic**, not migration analysis or a
reversibility proof. It reads the existing file named by the hook input (or manual
path argument); it does not inspect a commit diff or the proposed edit's future
contents. This document does not register or enable the hook on any host.

## What it does

- Selects the supplied path string matching `db/migrations/*`,
  `supabase/migrations/*`, `migrations/*`, `*.up.sql` or `*-up.sql`, or the optional
  comma-separated `data_architecture.migration_glob` field. It does not normalize
  every absolute path into those relative directory patterns.
- Searches existing text case-insensitively for `DROP TABLE`, `DROP COLUMN`,
  `TRUNCATE` and `ALTER COLUMN ... TYPE`. Comments can match; SQL syntax, indirect
  data loss, type narrowing and execution effects are not analyzed.
- Removes `.up.sql`/`-up.sql` from the base and checks the existing candidate names
  `${base}.down.sql`, `${base}-down.sql`, `${base%.sql}.down.sql`, or a line matching
  `^-- ?down|^# ?down`. Presence alone suppresses the warning.
- Matching SQL text **and** no down hint emits WARN and exits zero. Silence,
  including from a missing file or an unmatched filename, is not a passed review.
- The shared text reader treats filenames as literal operands. A grep/read
  failure emits an unavailable-observation warning and keeps the optional hook
  non-blocking; it is not converted to a no-match or recovery result.

## Why warn-only

- Some migrations are deliberately destructive (cleanup after grace window)
- The warning invites review; it does not force or log an acknowledgement.
- A paired down file or marker is not proof of reversibility. Review real recovery,
  retained data, rollback/replay and explicit data-loss acceptance with
  `/li:da single --action migration-plan`.

## Policy and scope

There is no acknowledgement/override option parser. Optional filename data is
explained by the [preference reference](../../../skills/da/references/preferences.md);
a missing optional field is absent advice, while an actual resolver/profile error
keeps its nonzero failure. The lookup is conditional on filename selection, not
a universal profile gate. Required profile/review controls remain owned by their
real callers; this advisory hook never satisfies or bypasses them.

## What's NOT in scope

- Detecting indirect data loss (e.g. column rename that loses precision) — Migrator's analysis
- Auto-generating down-migrations — operator-driven
- Hook activation, SQL execution, automatic repair or new mandatory policy

## Audit format

Only a warning calls the existing `audit_log hooks da_migration_irreversible_warn`
router with string fields `hook`, `tier`, `file`, comma-separated `destructive_ops`
and legacy `has_rollback=false` (meaning no filename/marker hint, not proven
irreversibility). The router owns destination and common metadata. It can fail
advisory writes; no receipt or no warning is not proof that recovery was verified.
