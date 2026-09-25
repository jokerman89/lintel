---
name: frontend-design-surface
tier: surface-only
event: PreToolUse (Read|Edit|Write on *.tsx|*.jsx|*.svelte|*.vue|*.css|*.scss)
fires_on: frontend-file edits with relevant patterns in ~/.lintel/brand/design-patterns/
override: explicit current LINTEL_HOME/.frontend-design-surface-disabled preference
audit: .claude/runtime/audit/hooks.jsonl
throttle: max 1 surface per file per session (state in ~/.lintel/sessions/<pid>-design-surfaced)
budget: <200ms target for a vault of 1-3 patterns; host timing must be measured
---

# frontend-design-surface

Passive surfacing of relevant design-patterns when operator opens/edits frontend files.

Per v3.7 design doc:
- Reads `~/.lintel/brand/design-patterns/` vault
- Matches against current file extension + (optional) brief-hash from recent runs
- Surfaces 1-line: "Design patterns relevant: X, Y. /li:frontend-design --pattern <name>."
- **Read-only, no blocker** — recommendation surface only.

## What it does

1. When separately registered on a compatible host, handles PreToolUse for
   Read/Edit/Write whose tool target matches frontend file extensions.
2. Reads vault patterns at `~/.lintel/brand/design-patterns/` (index lookup; <200ms for a vault of 1-3).
3. Checks throttle marker (`~/.lintel/sessions/<pid>-design-surfaced` with per-file entries).
4. If not-yet-surfaced this session for this file:
   - Emit 1-line surface
   - Mark file as surfaced (touch marker)
5. Logs to `.claude/runtime/audit/hooks.jsonl`.

## Why surface-only

Frontend-file edits are routine. Hook must not block flow. Surface 1-line recommendation is enough:
- Operator can ignore (most common case)
- Operator can invoke `/li:frontend-design --pattern <name>` if a pattern matches their context

Hard-block would create friction-without-value-for-90%-of-edits.

## Throttle logic

State at `~/.lintel/sessions/<session-id>-design-surfaced` where session-id is `LINTEL_SESSION_ID` env var if set, otherwise PPID. Real Claude Code sessions have stable PPID across tool invocations; test contexts can set `LINTEL_SESSION_ID=test-session-$$` for deterministic throttle-state across `$()` subshells.

File format:
```
path/to/file.tsx
path/to/other.css
```

If current file already in list → skip (no double-surface).
If not → emit + append to list.

This hook does not clean session markers or change host registration.

## Pattern relevance check

Naive v1: match on file-extension (`.tsx` → all patterns referencing tsx-stack).
Better v2 (Phase C+1): match on brief-hash if a recent `/li:frontend-design` run exists.

Pattern-vault format check:
```bash
for dir in "$LINTEL_HOME"/brand/design-patterns/*/; do
  [ -f "$dir/pattern.json" ] || continue
  # Vault entry valid → consider for surfacing
done
```

If vault is empty → silent exit (no surface). MVP.

## Performance budget

- Target: <200ms for vault of 1-3 patterns
- Degrades linearly to vault size — operator-vault > 10 patterns triggers vault-index.json optimization (Phase C+1)
- The budget is a target, not an observed execution claim.

## Override paths

The implementation reads `$LINTEL_HOME/.frontend-design-surface-disabled`.
It does not implement a skill flag or profile-switch dormancy command. Changing
that preference requires the operator's authorized configuration scope.
Expired migration locations are not inspected, copied or deleted. Existing
user data outside the current configured store remains untouched.

## What's NOT in scope

- Auto-applying patterns (operator decides via `/li:frontend-design --pattern <name>`)
- Vault-collision-detection (handled by `/li:frontend-style-extract --overwrite` flag)
- Live preview of pattern (out of hook scope; use `/li:frontend-design-review --baseline`)
