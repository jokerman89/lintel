---
name: code-unfreeze
layer: foundation
v1_alias: [li-unfreeze]
description: Remove a path from session freeze — other skills can write to it again.
color: blue
tools: Read, Edit, Bash
voice: internal
cli_support: [claude-code, codex]
---

# /code-unfreeze

Reverses `/code-freeze`. Removes paths from the session freeze metadata file, allowing other Lintel skills to write to them again. Logged to audit.

## When to use

- Done with the focused-scope work that motivated the freeze — open the area back up
- Freeze was added by mistake or applied too broadly
- Project freeze (loaded from CLAUDE.md frozen-zones) needs a temporary override — unfreeze for one operation, then re-freeze

## When NOT to use

- Trying to bypass Layer 2 compliance — that's not what freeze controls; Layer 2 always overrides
- Cleaning up old session state — freeze is session-scoped, expires automatically when session ends

## Inputs

- Required: one or more paths (must match an existing freeze entry)
- Optional `--all` — clear all freezes for this session
- Optional `--reason <text>` — why you're unfreezing (logged to audit)

## Workflow

1. **Resolve paths.** Canonicalize.
2. **Read session freeze file.** `.claude/runtime/state/code-freeze/<session-id>.yaml`.
3. **Match.** Exact-match required (no glob expansion at unfreeze time — too easy to over-unfreeze by accident).
4. **Remove matched entries.** Write the updated freeze file.
5. **Audit log.** Append to `.claude/runtime/audit/code-freeze.jsonl` with operation: unfreeze.
6. **Report remaining freeze state.**

## Report format

```
Unfreeze: src/components/landing/

Removed. Reason logged: "ready to coordinate landing + portal nav change"

Currently frozen this session:
- supabase/migrations/       (reason: migration churn risk)
```

## Compliance integration

- Unfreezing a CLAUDE.md frozen-zone path: WARN explicitly that this is a TEMPORARY runtime override and the static rule still applies — re-freeze when done.
- Audit log retains the unfreeze event even after session ends.

## Failure modes

- **Path not in current freeze:** report it wasn't frozen (no-op). Do not error.
- **`--all` invoked but freeze file is empty:** report no-op, exit cleanly.
- **Session file corrupted:** report + offer to reset (operator confirms).
- **Operator unfreezes a CLAUDE.md frozen-zone path without `--reason`:** require the reason — this is a deliberate override of project policy and deserves a trail.

## Examples

**Remove one:**
```
> /code-unfreeze src/components/landing/ --reason "ready to land nav change"
✓ Unfrozen. 1 path remains frozen.
```

**Clear all:**
```
> /code-unfreeze --all --reason "session pivot, opening everything"
✓ All freezes cleared this session.
```

**Path wasn't frozen:**
```
> /code-unfreeze src/lib/dlxClient.ts
⚠ Not in freeze list. No-op.
```

## See also

- `/code-freeze` — add to session freeze
- `/help` — shows current freeze state
- Project CLAUDE.md frozen-zones — permanent rules, distinct from session freeze
