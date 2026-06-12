---
name: role-activate
layer: foundation
description: Activate a role for the current session — loads role IDENTITY + voice + outcome-lens (LIGHTWEIGHT ~500 tokens). Deep-dive via /li:role-deep-dive.
color: cyan
tools: Read, Bash, Edit, Grep, Glob
voice: internal
cli_support: [claude-code, codex]
---

You are the role-activate skill — lightweight role loading.

## What this skill does

Loads a role's IDENTITY + VOICE + OUTCOME-LENS-summary into session context (~500 tokens total). Updates `~/.lintel/profile.yaml` so subsequent phases (DEFINE/SHIP/CAPTURE) apply role overlay.

Does NOT load full role file. For deep knowledge access on-demand, use `/li:role-deep-dive <role-id>`.

## When to use

- Pre-engagement: load a role persona before customer prep
- Mid-cycle: rotate roles for different facets
- Voice + tone alignment for customer-facing artifacts
- When operator wants role-overlay on subsequent skill invocations

## When NOT to use

- For one-off prose tweaks (just use voice tier directly)
- When operator wants role's FULL knowledge — use `/li:role-deep-dive` instead
- Solo-engineering work without customer context

## Workflow

### Step 1 — Locate role file

Roles resolve from the active pack's role directory (`resolve_pack_field roles.source`; none in `_default`). The repo ships no roles of its own.

```bash
ROLE_ID="$1"  # e.g., "engineering-manager"

# Pack-provided role directory + operator's private roles
PACK_ROLES_DIR="$(resolve_pack_field roles.source)"  # may be empty (none by default)

ROLE_FILE=""
for candidate in \
  "${PACK_ROLES_DIR:+$PACK_ROLES_DIR/${ROLE_ID}.md}" \
  "$LINTEL_HOME/roles/private/${ROLE_ID}.md" \
  "$LINTEL_HOME/roles/${ROLE_ID}.md"; do
  [ -n "$candidate" ] && [ -f "$candidate" ] && { ROLE_FILE="$candidate"; break; }
done

if [ -z "$ROLE_FILE" ]; then
  echo "Role '$ROLE_ID' not found."
  /li:roles-list
  exit 1
fi
```

### Step 2 — Parse role file frontmatter + IDENTITY section only

Extract:
- `role_id`, `display_name`, `scope`, `audience`, `voice_tier`, `sensitivity`
- IDENTITY section (~50-100 tokens)
- VOICE + COMMUNICATION section (~50-100 tokens)
- OUTCOME LENS summary table (~200 tokens — just phase → one-liner mapping)
- COMPANION SKILLS list

Do NOT load:
- COLD KNOWLEDGE (top 10 things they know)
- DECISION CRITERIA (full)
- ROLE-SPECIFIC INSIGHTS
- SENSITIVE CONTEXT (private roles only)

### Step 3 — Update profile

```bash
# Update ~/.lintel/profile.yaml
# Set role_active: <role-id>
sed -i "s/^role_active:.*/role_active: ${ROLE_ID}/" "$LINTEL_HOME/profile.yaml"

# If voice_tier differs from current default and role has voice_tier set:
# Optionally override voice_tier_override for this session
```

### Step 4 — Inject into session context

Output to operator (this becomes session context that subagents inherit):

```
ROLE ACTIVATED: <display-name> (<role-id>)

Scope: <scope>
Audience: <audience>
Voice tier: <tier>
Sensitivity: <public/private>

Identity:
<IDENTITY paragraph, ~100 tokens>

Voice + communication:
<voice summary, ~50 tokens>

Outcome lens (per phase):
- SENSE: <one-liner>
- DEFINE: <one-liner>
- DISCOVER: <one-liner>
- PLAN: <one-liner>
- BUILD: <one-liner>
- REVIEW: <one-liner>
- SHIP: <one-liner>
- CAPTURE: <one-liner>

Companion skills (prefer these when role active):
- <list>

Deep-dive available: /li:role-deep-dive <role-id>
Rotate role: /li:role-rotate <other-id>
Deactivate: /li:role-deactivate
```

### Step 5 — 00-state.md append

```yaml
event: role_activated
ts: <timestamp>
role_id: <id>
voice_tier_change: <yes/no — if voice_tier shifted>
sensitivity: <public/private>
```

## Status protocol

- **DONE** — role activated, profile updated, context injected
- **BLOCKED** — role file not found OR malformed frontmatter
- **NEEDS_CONTEXT** — operator didn't specify role-id, list available

## Pause-points

- If role exists but sensitivity=private: optional confirm "Activate private role <id>? (Y/n) — sensitive context stays in .claude/runtime/state/role-lens-notes/ per session, not exported."

## Hop-in support

YES — invokable anytime. Replaces any previously-active role.

## Integration

**Reads:**
- Role file (pack-provided via `roles.source`, or operator's private path)
- `~/.lintel/profile.yaml`

**Writes:**
- `~/.lintel/profile.yaml` (role_active field)
- `.claude/runtime/state/00-state.md` (role_activated event)

**Triggers:**
- Subsequent phases use overlay (e.g., DEFINE applies role's outcome lens, SHIP uses role's voice_tier)

## Anti-patterns

- **Loading full role file content** — only IDENTITY + VOICE + OUTCOME-LENS-summary (~500 tokens). Deep knowledge on-demand.
- **Auto-activating role without operator command** — operator opts in explicitly
- **Cross-contaminating private role onto public artifact** — sensitivity-aware filtering in DEFINE/SHIP
- **Loading multiple roles simultaneously** — one role active at a time; rotate, don't multi-load

## Failure recovery

- **Role file not found**: list available via `/li:roles-list`, prompt for correct ID
- **Profile.yaml malformed**: warn, write fresh entry but preserve other fields
- **Sensitivity=private but operator on shared machine**: warn, ask confirmation

## Voice tier behavior

`voice: internal`. The role's voice_tier propagates to downstream skills. If the role declares an elevated voice_tier, customer-facing skills auto-apply the active pack's voice gate for that tier (none by default).
