---
name: da-retention-violation-warn
tier: warn-only
event: PreToolUse (Edit|Write on data-access code)
fires_on: edit to a file that reads data classified as retention-bound, without honoring retention filter (e.g. WHERE deleted_at IS NULL, WHERE archived_at IS NULL)
override: pass --ignore-retention flag (operator decision, logged)
audit: .claude/runtime/audit/hooks.jsonl
---

# da-retention-violation-warn

Surfaces when an edit touches data-access code reading a retention-bound table without retention filtering. Warning, not block — operator may have legitimate analytics or admin reasons.

## What it does

- Reads `.claude/runtime/state/da/retention-policy.md` (if present) for tables with retention windows
- Detects data-access patterns in the edited file (SELECT / find / repository methods)
- For each access against a retention-bound table: checks for retention filters (deleted_at, archived_at, retained_until, expires_at)
- If access without filter: WARN

## Why warn-only

- Admin tooling legitimately reads soft-deleted data
- Analytics queries against historical data may intentionally span retention boundaries
- Block would be too aggressive for routine work

## Override path

`--ignore-retention "reason"` on the edit. Reason logged. CI can flag PRs with repeated overrides to the same file as candidates for explicit "admin-only" mark.

## What's NOT in scope

- Detecting indirect retention violations (an admin path that exposes deleted data to a customer-facing view)
- Auto-injecting retention filters
- Hard-blocking access (warn-only)

## Audit format

```jsonl
{"hook":"da-retention-violation-warn","tier":"warn","ts":"...","file_edited":"src/users/repository.ts","table":"users","retention_window_days":90,"missing_filter":"deleted_at","operator":"<operator>"}
```
