---
name: frozen-zone-warn
tier: warn-only
event: PreToolUse (Edit | Write)
fires_on: edit to a path matching frozen-zone rules
override: pass --ignore-freeze flag to invoking skill
audit: .claude/runtime/audit/hooks.jsonl
---

# frozen-zone-warn

Warns when an Edit or Write is about to modify a path inside a frozen zone. Frozen zones come from two sources:

1. **Session freezes** (`/code-freeze` skill) — `.claude/runtime/state/code-freeze/<session-id>.yaml`
2. **Permanent freezes** (project CLAUDE.md) — `## Frozen zones` section

## What it does

Reads both sources, builds a glob list of frozen paths, checks the Edit/Write target against the list, emits warning if matched.

## Override

The warning is informational; the actual block happens at the invoking SKILL level (e.g. `/clean` or `/code-freeze` enforce). This hook exists to surface the freeze status when an Edit is about to happen anyway (operator might have forgotten the freeze).

## Why warn-only

- Frozen-zone is operator-set policy; the operator may consciously want to violate
- Block would require complex override mechanism
- Warning + audit-log is the right friction level

## Audit

```jsonl
{"hook": "frozen-zone-warn", "tier": "warn", "ts": "...", "frozen_path": "src/components/landing/", "edit_target": "src/components/landing/Hero.tsx", "source": "session-freeze | project-claude-md"}
```
