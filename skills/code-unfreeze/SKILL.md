---
name: code-unfreeze
layer: foundation
v1_alias: [li-unfreeze]
description: Remove explicitly selected advisory freeze metadata without changing host permissions, project policy or release authority.
color: blue
tools: Read, Edit, Bash
voice: internal
cli_support: [claude-code, codex]
---

# /code-unfreeze

Reverses `/code-freeze` metadata, not host or project controls. Exact removal from
the selected session/cycle file is advisory and does not grant permission to write.
No filesystem lock or universal skill refusal was installed.

## When to use

- Done with the focused-scope work that motivated the freeze — open the area back up
- Freeze was added by mistake or applied too broadly
- A runtime reminder is no longer needed; changing a static project rule requires
  separate explicit authority, not this command

## When NOT to use

- Trying to bypass Layer 2 compliance — that's not what freeze controls; Layer 2 always overrides
- Automatic cleanup or expiry — no timer/watcher is implemented

## Inputs

- Required: one or more paths (must match an existing freeze entry)
- Optional `--all` — clear all freezes for this session
- Optional `--reason <text>` — why you're unfreezing (logged to audit)

## Workflow

1. **Resolve paths.** Canonicalize.
2. **Read session freeze file.** `.claude/runtime/state/code-freeze/<session-id>.yaml`.
3. **Match.** Exact-match required (no glob expansion at unfreeze time — too easy to over-unfreeze by accident).
4. **Remove matched entries.** Preserve all unmatched entries and verify the exact
   selected file's new contents before reporting success.
5. **Audit observation.** Use the existing writer once per removed path:
   `audit_log code-freeze unfreeze "path=<path>" "reason=<reason>"`; the event is not
   verification of host permission or project-policy override.
6. **Report remaining freeze state.**

## Report format

```
Unfreeze: src/components/landing/

Removed. Reason logged: "ready to coordinate landing + portal nav change"

Currently frozen this session:
- supabase/migrations/       (reason: migration churn risk)
```

## Compliance integration

- Removing a reminder for a project frozen-zone path is **not** a temporary override.
  The static rule and required permission still apply.
- Audit log retains the unfreeze event even after session ends.

## Failure modes

- **Path not in current freeze:** report it wasn't frozen (no-op). Do not error.
- **`--all` invoked but freeze file is empty:** report no-op, exit cleanly.
- **Session file corrupted:** retain the file and report unknown scope; no empty
  success-shaped replacement.
- **Operator requests a project-policy exception:** refer to its actual authority
  boundary. A local reason field or unfreeze event cannot grant it.

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
- `/code-freeze --list` — shows the recorded advisory freeze state
- Project CLAUDE.md frozen-zones — permanent rules, distinct from session freeze
