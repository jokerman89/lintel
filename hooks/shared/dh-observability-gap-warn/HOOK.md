---
name: dh-observability-gap-warn
tier: warn-only
event: PreToolUse (Edit|Write on new service paths)
fires_on: edit creates or modifies a service entry-point file without observability instrumentation (no metric emission, no trace span, no structured log)
override: pass --ignore-observability-gap flag (operator decision, logged)
audit: ~/.lintel/audit/hooks.jsonl
---

# dh-observability-gap-warn

Surfaces when an edit to a service entry point lacks observability instrumentation. Warning, not block — instrumentation may live elsewhere (middleware, decorators); operator decides.

## What it does

- Detects service entry points (handler files, controller methods, RPC endpoints) via path + content heuristic
- Scans for observability markers (metric emission calls, trace span markers, structured log calls)
- If entry point detected but no instrumentation: WARN

## Why warn-only

- Instrumentation may be added via middleware/decorators (not visible at the entry-point level)
- Operator may be in early-stage scaffolding
- Block would be too aggressive

## Override path

`--ignore-observability-gap "reason"` on the edit. Reason logged.

## Audit format

```jsonl
{"hook":"dh-observability-gap-warn","tier":"warn","ts":"...","file_edited":"src/api/users.go","markers_found":0,"operator":"jokerman"}
```
