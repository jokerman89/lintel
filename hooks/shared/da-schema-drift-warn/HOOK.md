---
name: da-schema-drift-warn
tier: warn-only
event: PreToolUse (Edit|Write on schema-ADR-claimed files)
fires_on: edit to a file path listed in any schema-flavored ADR's "decisions:" block, OR to a migration file referenced by an ADR
override: pass --ignore-schema-drift flag (operator decision, logged)
audit: .claude/runtime/audit/hooks.jsonl
---

# da-schema-drift-warn

Surfaces when an Edit/Write hits a schema file or migration covered by a prior schema-ADR. Warning, not block — schema evolution is normal; the warn prompts operator to update the ADR or document the divergence.

## What it does

- Scans `.lintel/decisions/`, `docs/decisions/`, `.claude/decisions/` for ADRs whose `decisions:` block references the edited file OR a migration file path inside the same schema directory
- Filters to schema-flavored ADRs (heuristic: ADR title or content references "schema", "migration", "data model", "column", "table")
- If match: WARN with ADR id + decision summary

## Why warn-only

Schema decisions evolve. The warn prompts the operator to either: (a) update the ADR, (b) deliberately diverge (audit-logged), or (c) reconsider the edit. Block would be too aggressive for routine schema work.

## Override path

`--ignore-schema-drift "reason"` on the edit. Reason logged to audit. CI can inspect override frequency per file.

## What's NOT in scope

- Detecting indirect schema impact (downstream consumers — that's `/li:da data-contract-collision`)
- Blocking the edit (warn only)
- Auto-updating the ADR

## Audit format

```jsonl
{"hook":"da-schema-drift-warn","tier":"warn","ts":"...","file_edited":"db/migrations/0042_user_schema.sql","adr_id":"ADR-014","adr_decision":"User schema versioning","operator":"<operator>"}
```
