---
name: role-deactivate
layer: foundation
description: Remove active role from session — clears overlay, voice tier reverts to mode/profile default.
color: cyan
tools: Read, Bash, Edit
voice: internal
cli_support: [claude-code, codex]
---

You are the role-deactivate skill.

## What this skill does

Clears active role. Voice tier reverts to mode/profile default. Useful when session shifts to pure engineering work and role overlay would add noise.

## When to use

- After customer-facing work ends, before deep engineering work
- When role-overlay is producing more noise than value
- Pre-shipping internal-only artifact where role's voice would mismatch

## When NOT to use

- Want to switch to different role — use `/li:role-rotate`
- Want to keep role but ignore for one task — pass `--no-role` flag to that skill instead

## Workflow

### Step 1 — Verify role active

```bash
current_role=$(grep '^role_active:' "$LINTEL_HOME/profile.yaml" | awk '{print $2}')
if [ -z "$current_role" ] || [ "$current_role" = "null" ]; then
  echo "No role active. Nothing to deactivate."
  exit 0
fi
```

### Step 2 — Sensitivity handling

If current role is private:
- AskUserQuestion: "Deactivating private role <id>. Save current session's role-lens-notes? (Y/n)"
- If Y: ensure `.lintel/state/role-lens-notes-<ts>.md` is preserved
- If N: clear notes

### Step 3 — Clear active role in profile

```bash
sed -i "s/^role_active:.*/role_active: null/" "$LINTEL_HOME/profile.yaml"
```

### Step 4 — Surface deactivation

```
ROLE DEACTIVATED: <previous-role-id>

Voice tier reverted to: <mode_default OR profile.voice_tier_default>
Role-overlay no longer applied to subsequent skills.

To re-activate same role: /li:role-activate <id>
To activate different role: /li:role-activate <other>
```

### Step 5 — 00-state.md append

```yaml
event: role_deactivated
ts: <timestamp>
role_id: <previous-role>
sensitivity: <public/private>
notes_preserved: <yes/no>
```

## Status protocol

- **DONE** — deactivated, profile updated
- **BLOCKED** — no role active
- **DONE_WITH_CONCERNS** — private role deactivated but sensitive context may still be in conversation history

## Pause-points

- Sensitivity handling for private roles

## Hop-in support

YES — anytime.

## Integration

Reads + writes `~/.lintel/profile.yaml`. Optionally preserves `.lintel/state/role-lens-notes-*.md`.

## Anti-patterns

- **Deactivating private role without addressing context-history sensitivity** — surface explicitly
- **Forgetting deactivation persists across sessions** — operator's next session starts with `role_active: null`

## Voice tier behavior

`voice: internal`.
