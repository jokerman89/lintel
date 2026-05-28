---
name: role-rotate
layer: foundation
description: Swap active role mid-session — deactivate current, activate new. Preserves session memory but shifts overlay.
color: cyan
tools: Read, Bash, Edit, Glob
voice: internal
cli_support: [claude-code, codex]
---

You are the role-rotate skill.

## What this skill does

Atomically swaps active role: deactivates current + activates new. Useful when operator changes facets mid-session (e.g., started with Field CTO frame for customer-pitch, now needs Engineering Manager frame for handoff planning).

Session memory preserved (lessons, context, artifacts). Only the role-overlay changes.

## When to use

- Mid-session role shift (one engagement, multiple personas)
- Customer-engagement with multiple stakeholders (rotate as you address each)
- Different cycle phases benefit from different role lenses (e.g., DEFINE with Field CTO, REVIEW with SecurityAuditor-flavored Compliance Officer)

## When NOT to use

- First role activation — use `/li:role-activate` directly
- Deactivating without replacement — use `/li:role-deactivate`
- Loading multiple roles simultaneously — not supported (rotate, don't multi-load)

## Workflow

### Step 1 — Read current state

```bash
current_role=$(grep '^role_active:' "$LINTEL_HOME/profile.yaml" | awk '{print $2}')
new_role="$1"
```

If no current role active: surface info, suggest `/li:role-activate` directly.

### Step 2 — Compare roles

Both should exist (verify new role file before deactivating current):

```bash
# Check new role exists
new_role_file=""
for candidate in \
  "roles/${new_role}.md" \
  "$LINTEL_HOME/roles/private/${new_role}.md" \
  "$LINTEL_HOME/roles/${new_role}.md"; do
  [ -f "$candidate" ] && { new_role_file="$candidate"; break; }
done

if [ -z "$new_role_file" ]; then
  echo "New role '$new_role' not found. Current role '$current_role' kept active."
  /li:roles-list
  exit 1
fi
```

### Step 3 — Sensitivity transition

If current = public AND new = private: warn that session is gaining sensitive context, ask confirm.

If current = private AND new = public: surface that sensitive context will be DROPPED from context (or persisted in role-lens-notes file for current session record).

### Step 4 — Deactivate current

```bash
# Mark deactivation
echo "role_deactivated: $current_role at $(date)" >> .lintel/state/00-state.md
```

Don't clear cached deep-dive context if operator wants both available — but mark current as inactive.

### Step 5 — Activate new

Delegate to `/li:role-activate <new-role>`. Loads lightweight context for new role.

### Step 6 — Surface transition

```
ROLE ROTATED: <current-role> → <new-role>

Previous overlay: deactivated
New overlay: <new-role> activated (lightweight)

Session memory preserved:
- Lessons applied this session: <count>
- Artifacts referenced: <count>
- Context budget: <unchanged>

If you need deep-dive on new role: /li:role-deep-dive <new-role>
```

### Step 7 — 00-state.md append

```yaml
event: role_rotated
ts: <timestamp>
from: <current-role>
to: <new-role>
sensitivity_shift: <none | gained | dropped>
```

## Status protocol

- **DONE** — rotation complete, new role active
- **BLOCKED** — new role file missing, current role kept
- **NEEDS_CONTEXT** — operator didn't specify new role-id

## Pause-points

- Sensitivity transition (gaining private OR dropping private)

## Hop-in support

YES — invokable anytime mid-session.

## Integration

Delegates to `/li:role-activate` after deactivating current. Reads + writes `~/.lintel/profile.yaml`.

## Anti-patterns

- **Rotating without verifying new role exists** — could leave session role-less
- **Frequent rotations (>3 per session)** — context jitter, confuses subagents
- **Cross-contaminating private role context after rotation** — verify sensitive content doesn't bleed into new role's outputs

## Voice tier behavior

`voice: internal`.
