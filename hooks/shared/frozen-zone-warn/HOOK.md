---
name: frozen-zone-warn
tier: warn-only
event: PreToolUse (Edit | Write)
fires_on: edit target matching a legacy session freeze entry or a project CLAUDE.md "Frozen zones" bullet
override: none — the hook only warns; the edit proceeds unchanged
audit: .claude/runtime/audit/hooks.jsonl (repo-scoped; resolved by bin/_audit.sh)
---

# frozen-zone-warn

Opt-in and warn-only. When an Edit or Write targets a frozen path, the hook prints a warning
and records one `frozen_zone_warn` finding. It never blocks, and nothing enforces a freeze.

## What it reads

The hook reads exactly two sources:

1. **Legacy session freeze file:** `$LINTEL_HOME/freeze/${LINTEL_SESSION_ID:-default}.yaml`. Each
   `- path: <prefix>` entry is a **prefix** match against the edit target.
2. **Project `CLAUDE.md`:** the current directory's `CLAUDE.md` section whose heading starts with
   `Frozen zones`. Each bullet's first path-like token is a **substring** match against the edit
   target.

It does not read the advisory metadata that `/li:code-freeze` records under
`.claude/runtime/state/code-freeze/<session-id>.yaml`, and it builds no glob list. That metadata
is a cooperative reminder for BUILD and review; this hook is a separate, dormant legacy reader.

## What it does not do

- No enforcement: `/clean`, `/li:code-freeze` and other skills do not block on this hook's result,
  and no filesystem or host write lock is installed.
- No automatic registration: it ships inert and runs only after an operator activates it.
- No override flag: there is nothing to override because the edit is never stopped.

## Message

A match prints the frozen path and its source, then names an explicitly authorized `/li:code-freeze --lift` for removing an
advisory freeze that is no longer wanted. The warning is informational.

## Audit

One record per match, written through the shared advisory writer (a failed write only warns):

```jsonl
{"ts":"...","kind":"frozen_zone_warn","operator":"...","cycle_id":"...","hook":"frozen-zone-warn","tier":"warn","frozen_path":"src/components/landing/","edit_target":"src/components/landing/Hero.tsx","source":"session-freeze | project-claude-md"}
```

A record shows that the hook matched and warned. It is not proof that the edit was prevented.
