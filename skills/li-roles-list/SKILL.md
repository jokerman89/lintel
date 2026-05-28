---
name: li-roles-list
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
- Public roles in repo (`roles/*.md`)
- Public roles in user home (`~/.lintel/roles/*.md`)
- Private roles in user home (`~/.lintel/roles/private/*.md`)

Surfaces a table for selection.

## When to use

- Operator unsure which role-id to activate
- After install, exploring available roles
- Audit: which private roles operator has

## When NOT to use

- Already know the role-id — use `/lintel:li-role-activate <id>` directly

## Workflow

### Step 1 — Collect role files

```bash
roles=()
# Public in repo
for f in roles/*.md 2>/dev/null; do [ -f "$f" ] && roles+=("$f"); done
# Public in home
for f in "$LINTEL_HOME"/roles/*.md 2>/dev/null; do [ -f "$f" ] && roles+=("$f"); done
# Private in home
for f in "$LINTEL_HOME"/roles/private/*.md 2>/dev/null; do [ -f "$f" ] && roles+=("$f"); done
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
| field-cto | Field CTO | customer-facing, sales-tech | trailblazer | public | 2026-05-28 |
| solution-architect | Solution Architect | enterprise IT, security-conscious | mixed | public | 2026-05-28 |
| engineering-manager | Engineering Manager | process, team coordination | internal | public | 2026-05-28 |
| customer-acme-cio | CIO of Acme Corp | <scope> | trailblazer | private | 2026-05-20 |

Currently active: <role-id or null>

To activate: /lintel:li-role-activate <id>
To deep-dive: /lintel:li-role-deep-dive <id>
To create new role: /lintel:li-role-new <id>
```

### Step 4 — Auto-suggest if cycle phase implies role fit

If cycle is mid-DEFINE for customer-engagement mode, surface: "Recommended for current phase: field-cto (matches customer-facing audience)."

### Step 5 — 00-state.md append (light, optional)

```yaml
event: roles_listed
ts: <timestamp>
role_count: <N>
```

## Status protocol

- **DONE** — list surfaced
- **DONE_WITH_CONCERNS** — list partial (some role files malformed)
- **BLOCKED** — no role directories exist

## Pause-points

None.

## Hop-in support

YES — pure information query, anytime.

## Integration

**Reads:**
- `roles/*.md`
- `~/.lintel/roles/*.md` (public)
- `~/.lintel/roles/private/*.md`
- `~/.lintel/profile.yaml` (active role)

**Writes:**
- Optional `.lintel/state/00-state.md` event

## Anti-patterns

- **Loading full role content** — frontmatter only
- **Showing private roles to operators on shared machines without confirmation** — privacy-aware (though operator chose to list them)
- **Truncating list silently** — show all, paginate only if huge (>20 roles)

## Voice tier behavior

`voice: internal`.
