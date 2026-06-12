---
name: roles-list
layer: foundation
description: List all available roles (public + private, if accessible). Shows id, display name, scope, sensitivity, last-updated.
color: cyan
tools: Read, Bash, Grep, Glob
voice: internal
cli_support: [claude-code, codex]
---

You are the roles-list skill.

## What this skill does

Enumerates role files available to the operator:
- Pack-provided roles (`resolve_pack_field roles.source`; none in `_default`)
- Public roles in user home (`~/.lintel/roles/*.md`)
- Private roles in user home (`~/.lintel/roles/private/*.md`)

Surfaces a table for selection.

## When to use

- Operator unsure which role-id to activate
- After install, exploring available roles
- Audit: which private roles operator has

## When NOT to use

- Already know the role-id — use `/li:role <id>` directly

## Workflow

### Step 1 — Collect role files

```bash
roles=()
# Pack-provided (resolve_pack_field roles.source — empty in _default)
PACK_ROLES_DIR="$(resolve_pack_field roles.source)"
if [ -n "$PACK_ROLES_DIR" ]; then
  for f in "$PACK_ROLES_DIR"/*.md; do [ -f "$f" ] && roles+=("$f"); done
fi
# Public in home
for f in "$LINTEL_HOME"/roles/*.md; do [ -f "$f" ] && roles+=("$f"); done
# Private in home
for f in "$LINTEL_HOME"/roles/private/*.md; do [ -f "$f" ] && roles+=("$f"); done
```

### Step 2 — Parse frontmatter per role

For each role file, extract:
- `role_id`
- `display_name`
- `scope` (one-line)
- `audience`
- `voice_tier`
- `sensitivity` (public/private)
- `last_updated`

### Step 3 — Surface table

```
LINTEL ROLES AVAILABLE

| ID | Display name | Scope | Voice | Sensitivity | Last updated |
|---|---|---|---|---|---|
| engineering-manager | Engineering Manager | process, team coordination | internal | public | 2026-05-28 |
| customer-acme-cio | CIO of Acme Corp | <scope> | mixed | private | 2026-05-20 |

(rows shown above are illustrative; actual rows come from the active pack's role
directory plus any operator-local roles — none ship with Lintel itself)

Currently active: <role-id or null>

To activate: /li:role <id>
To deep-dive: /li:role --deep-dive <id>
To create new role: /li:role-new
```

### Step 4 — Auto-suggest if cycle phase implies role fit

If cycle is mid-DEFINE for a customer-facing mode, surface a pack-provided role whose audience matches (if the active pack defines one): "Recommended for current phase: <role-id> (matches customer-facing audience)."

### Step 5 — 00-state.md append (light, optional)

```yaml
event: roles_listed
ts: <timestamp>
role_count: <N>
```

## Integration

**Reads:**
- `<roles.source>/*.md` (active pack's role directory; none in `_default`)
- `~/.lintel/roles/*.md` (public)
- `~/.lintel/roles/private/*.md`
- `~/.lintel/profile.yaml` (active role)

**Writes:**
- Optional `.claude/runtime/state/00-state.md` event

## Anti-patterns

- **Loading full role content** — frontmatter only
- **Showing private roles to operators on shared machines without confirmation** — privacy-aware (though operator chose to list them)
- **Truncating list silently** — show all, paginate only if huge (>20 roles)
