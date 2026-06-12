---
name: role-new
layer: foundation
description: Scaffold a new role file from template via guided interview — IDENTITY, COLD KNOWLEDGE, DECISION CRITERIA, OUTCOME LENS per phase. Evolve an existing role with --update <id> (targeted, sensitivity-aware edits).
color: cyan
tools: Read, Bash, Edit, Write
voice: internal
cli_support: [claude-code, codex]
---

You are the role-new skill — creation and evolution of role files.

Two modes:

- `/li:role-new` — guided interview, renders a new role file
- `/li:role-new --update <id>` — targeted update to an existing role (defaults to the active role)

## When to use

- New customer engagement requires a custom persona
- Generic role doesn't fit, need a specialized variant
- Promoting the operator's mental model of someone to a durable role file
- `--update`: post-CAPTURE role-debrief captured new patterns; mid-engagement role-mismatch refinement; a customer interaction revealed a voice nuance

## When NOT to use

- Existing role fits — use it (`/li:role <id>`)
- One-off persona — inline operator context, not a durable role file
- One-off observation — keep in session notes; only durable patterns land in the file
- Customer-specific PII required in the role — STOP, that's not a role file's purpose

## Create (default mode)

Operator answers guided questions; the skill renders a structured role file into the active pack's role directory (`resolve_pack_field roles.source`) for public roles, or `~/.lintel/roles/private/<id>.md` for private ones.

### Step 1 — Basic identity (AskUserQuestion sequence)

One at a time:
1. **Role ID** (kebab-case): e.g., `customer-acme-cio`
2. **Display name**: e.g., "CIO of Acme Corp"
3. **Sensitivity**: public OR private (customer-specific = always private; never default — must be explicit)
4. **Scope** (one line): e.g., "customer-facing, sales-tech, enterprise-strategy"
5. **Voice tier**: internal / trailblazer / mixed

### Step 2 — Identity paragraph

"One paragraph: who they are, what they care about, what gets them promoted, what gets them fired. 50-100 words."

### Step 3 — Cold knowledge (top 10)

"List 10 things this role knows cold (top beliefs without thinking). Numbered list."

### Step 4 — Decision criteria

"What makes them say YES vs NO in a meeting? 3-5 bullets."

### Step 5 — Voice + communication

"Tone descriptors, preferred phrases (3-5), avoided phrases (3-5)."

### Step 6 — Outcome lens per phase

For each cycle phase (SENSE, DEFINE, DISCOVER, PLAN, BUILD, REVIEW, SHIP, CAPTURE): "What does <role-name> want from <PHASE>? One line." — 8 questions, batchable.

### Step 7 — Role-specific insights

"Top patterns, common mistakes, what differentiates great vs good for this role. Free-form, ~200 words."

### Step 8 — Companion skills + agents

"Which Lintel skills/agents prefer this role?" (pack-provided skills/agents — none ship with Lintel itself; e.g. a pack's executive-brief skill, advisor agent, proposal-drafter.)

### Step 9 — Sensitive context (private roles only)

"Sensitive context — customer-internal info, specific projects, named people. Stays in the private role file only, NEVER ships to a public marketplace."

Warn explicitly: this section is NOT loaded into session by default (only via `/li:role --deep-dive` with confirmation).

### Step 10 — Render + save

```yaml
---
role_id: <id>
display_name: <name>
scope: <scope>
audience: <inferred from scope>
voice_tier: <tier>
sensitivity: <public/private>
last_updated: <today>
applies_to_phases: [<inferred>]
companion_agents: [<list>]
---

# IDENTITY
<paragraph>

# COLD KNOWLEDGE (top 10)
1. ...

# DECISION CRITERIA
- ...

# VOICE + COMMUNICATION
- Tone: <descriptors>
- Preferred phrases: [...]
- Avoided phrases: [...]
- Energy: <descriptor>

# OUTCOME LENS (per cycle phase)
- SENSE: <line>
- ... (one line per phase through CAPTURE)

# ROLE-SPECIFIC INSIGHTS
<free-form>

# COMPANION SKILLS
- ...

# SENSITIVE CONTEXT (private roles only)
<free-form or omitted>
```

Save location:

```bash
if sensitivity == public:
  PACK_ROLES_DIR="$(resolve_pack_field roles.source)"
  if [ -z "$PACK_ROLES_DIR" ]; then
    echo "No pack role directory configured (roles.source is null in _default)."
    echo "Activate a pack that provides roles, or save this role as private."
    exit 1
  fi
  target="$PACK_ROLES_DIR/<id>.md"; mkdir -p "$PACK_ROLES_DIR"
else:
  target="$LINTEL_HOME/roles/private/<id>.md"; mkdir -p "$LINTEL_HOME/roles/private"
```

Duplicate role-id: ask overwrite / rename / cancel. If the operator abandons mid-interview: save the partial role to `~/.lintel/roles/draft/<id>-draft.md` and prompt to resume next session.

### Step 11 — Surface result + offer activation

"ROLE CREATED: <display-name> at <path>. Activate now?" — if yes: `/li:role <id>`. Append `event: role_created` (role_id, sensitivity, path) to `.claude/runtime/state/00-state.md`.

## --update <id> — evolve an existing role

Targeted edits, not rewrites (wholesale rewrite = re-scaffold via create mode). Sensitivity-aware: private role updates never leak to a public marketplace. Target defaults to the active role (`role_active` in `~/.lintel/profile.yaml`); if none specified and none active, list roles via `/li:roles-list`.

1. **Locate + read** the role file (public/private/home paths, same resolution as `/li:role`).
2. **Diagnose the update type** (AskUserQuestion):
   - A) Add insight to ROLE-SPECIFIC INSIGHTS — "What's the new insight? 1-3 sentences. What pattern, what mistake to avoid, what differentiator?"
   - B) Add to COLD KNOWLEDGE — "What's the new fact? Format: 'role knows X without thinking'."
   - C) Refine VOICE — "New preferred phrase OR avoided phrase? With brief reason."
   - D) Refine OUTCOME LENS — "Which phase? What new lens?"
   - E) Update DECISION CRITERIA — "New yes/no factor + how it ranks against existing criteria?"
   - F) Other (free-form section edit)
3. **Sensitivity check**:
   - Private role: confirm "Update saved to the private role file, not pushed to a public marketplace. Continue?"
   - Public role: confirm no PII; soft-scan the update text for PII patterns — warn + refuse on detection.
4. **Apply**: append to the relevant section, update the `last_updated:` frontmatter field, preserve formatting. For C also update the VOICE + COMMUNICATION block.
5. **Verify integrity**: re-read; frontmatter must still parse (`head -1` is `---`). If corrupt: revert the edit (git or backup), surface the error.
6. **Sync**: if the role is private and `bin/li-roles-sync` is configured, push to the operator's private repo. If the push fails: surface, retain the local change, retry later.
7. Append `event: role_updated` (role_id, update_type, section_updated, sensitivity) to 00-state.

If the operator is unsure an update is durable: capture it as PROVISIONAL with a low-confidence flag — promotable later.

## Anti-patterns

- **PII in COLD KNOWLEDGE / INSIGHTS** — explicit warning + soft refusal
- **One-off persona as a role file** — roles are durable; one-offs are inline operator context
- **Skipping the sensitivity declaration** — must be explicit, never default
- **Auto-applying every session learning via --update** — the operator filters; only durable patterns land in the file
- **Updating the active session role without explicit operator confirmation**
