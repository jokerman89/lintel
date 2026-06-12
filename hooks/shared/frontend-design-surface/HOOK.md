---
name: frontend-design-surface
tier: surface-only
event: PreToolUse (Read|Edit|Write on *.tsx|*.jsx|*.svelte|*.vue|*.css|*.scss)
fires_on: frontend-file edits with relevant patterns in ~/.lintel/brand/design-patterns/
override: pass --no-design-surface flag OR /li:profile-switch --dormant frontend-design-surface
audit: .claude/runtime/audit/hooks.jsonl
throttle: max 1 surface per file per session (state in ~/.lintel/sessions/<pid>-design-surfaced)
budget: <200ms for vault of 1-3 patterns (MVP per /plan-eng-review concern #7)
---

# frontend-design-surface

Passive surfacing of relevant design-patterns when operator opens/edits frontend files.

Per v3.7 design doc:
- Reads `~/.lintel/brand/design-patterns/` vault
- Matches against current file extension + (optional) brief-hash from recent runs
- Surfaces 1-line: "Design patterns relevant: X, Y. /li:frontend-design --pattern <name>."
- **Read-only, no blocker** — recommendation surface only.

## What it does

1. Fires on PreToolUse for Read/Edit/Write when the tool target matches frontend file-extensions.
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

Sessions clean up via existing 120-min stale-removal in preamble logic.

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
- Per /plan-eng-review concern #7: MVP-budget documented + acknowledged

## Override paths

- `--no-design-surface` flag on `/li:frontend-design` (if operator explicitly silent)
- `/li:profile-switch --dormant frontend-design-surface` (existing skill, per-hook dormancy)
- Touch `~/.lintel/.frontend-design-surface-disabled` for session-level silence

## What's NOT in scope

- Auto-applying patterns (operator decides via `/li:frontend-design --pattern <name>`)
- Vault-collision-detection (handled by `/li:frontend-style-extract --overwrite` flag)
- Live preview of pattern (out of hook scope; use `/li:frontend-design-review --baseline`)
