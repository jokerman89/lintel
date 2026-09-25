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

### Step 1 — Call the source-owned inventory

```bash
bash "$LINTEL_SOURCE_ROOT/bin/li-lifecycle" \
  --source "$LINTEL_SOURCE_ROOT" --repo "$LINTEL_REPO_ROOT" role-list
```

Follow [lifecycle paths](../../docs/lifecycle.md). Add `--include-private` only when
the operator requested private metadata or approves it for this session. The helper
reads bounded frontmatter only, resolves pack-relative paths through field provenance,
preserves duplicate IDs as shadowed rows and never binds a profile or changes preferences.

### Step 2 — Display metadata per role

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

### Step 5 — Preserve read-only behavior

Do not write an event or a guessed active role to the work ledger. A null profile
reference is an unbound read; malformed metadata/preferences or profile drift remain
visible errors, not an empty or healthy inventory.

## Integration

**Reads:**
- `<roles.source>/*.md` (active pack's role directory; none in `_default`)
- `~/.lintel/roles/*.md` (public)
- `~/.lintel/roles/private/*.md`
- `~/.lintel/profile.yaml` (active role)

**Writes:**
- stdout only; no preference, ledger or private synchronization mutation

## Anti-patterns

- **Loading full role content** — frontmatter only
- **Showing private roles to operators on shared machines without confirmation** — privacy-aware (though operator chose to list them)
- **Truncating list silently** — show all, paginate only if huge (>20 roles)
