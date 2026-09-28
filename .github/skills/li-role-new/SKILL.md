---
name: li-role-new
description: Scaffold a new role file from template via guided interview — IDENTITY, COLD KNOWLEDGE, DECISION CRITERIA, OUTCOME LENS per phase. Evolve an existing role with --update <id> (targeted, sensitivity-aware edits).
---

> **Lintel on GitHub Copilot.** Generated from `skills/role-new/SKILL.md`; edit the canonical file, then run
> `li-copilot init`.
> - **Resource root:** `../../..` from this skill's base directory (the Lintel source with `bin/`,
>   `lib/`, `skills/`). Write plans, state and evidence into the working repository's `.claude/`
>   tree, never into the resource root.
> - **Skill-relative paths:** this skill's own `scripts/`, `references/` and `data/` folders (and a
>   `<base>` that the workflow defines as its own directory) mean
>   `../../../skills/role-new/` in the Lintel source, not this generated folder.
>   `${LINTEL_SKILLS_DIR:-skills}` means the skills root, `../../../skills`. A `bin/li-run` step
>   runs in the working repository, so use `$LINTEL_SKILLS_DIR/role-new/` there.
> - **Shell steps:** run Bash snippets with Bash (Git for Windows' `bash.exe` on Windows, never
>   `System32\bash.exe`). Save a snippet to a temporary `.sh` file and run
>   `bash "<resource root>/bin/li-run" <file>`; it prepares `LINTEL_SOURCE_ROOT`, `LINTEL_REPO_ROOT`
>   and the profile context.
> - **Tools:** Read=`view`, Write=`create`, Edit=`edit`, Bash=`bash`/`powershell`, Grep=`grep`,
>   Glob=`glob`, AskUserQuestion=`ask_user`, TodoWrite=the plan checklist, Task or a named role=`task`
>   with that custom agent, WebFetch=`web_fetch`.
> - **Other Lintel workflows** are native skills: invoke `/li-<name>` rather than reading their
>   files. Named roles such as `CodeReviewer` are custom agents.

You are the role-new skill — creation and evolution of role files.

Two modes:

- `/li-role-new` — guided interview, renders a new role file
- `/li-role-new --update <id>` — targeted update to an existing role (defaults to the active role)

## When to use

- New customer engagement requires a custom persona
- Generic role doesn't fit, need a specialized variant
- Promoting the operator's mental model of someone to a durable role file
- `--update`: post-CAPTURE role-debrief captured new patterns; mid-engagement role-mismatch refinement; a customer interaction revealed a voice nuance

## When NOT to use

- Existing role fits — use it (`/li-role <id>`)
- One-off persona — inline operator context, not a durable role file
- One-off observation — keep in session notes; only durable patterns land in the file
- Customer-specific PII required in the role — STOP, that's not a role file's purpose

## Create (default mode)

Use an adaptive interview: reuse facts already supplied and ask only for missing
decisions. The expert-content sections below are retained, but ten facts or one question
per phase are prompts for depth, not mandatory filler. Render a reviewed draft, then
let `bin/li-lifecycle.py role-write` own publication under the
[configured lifecycle roots](../../../docs/lifecycle.md).

### Step 1 — Basic identity (ask_user sequence)

One at a time:
1. **Role ID** (kebab-case): e.g., `customer-acme-cio`
2. **Display name**: e.g., "CIO of Acme Corp"
3. **Sensitivity**: public OR private (customer-specific = always private; never default — must be explicit)
4. **Scope** (one line): e.g., "customer-facing, sales-tech, enterprise-strategy"
5. **Voice tier**: internal / external / mixed

### Step 2 — Identity paragraph

"One paragraph: who they are, what they care about, what gets them promoted, what gets them fired. 50-100 words."

### Step 3 — Cold knowledge (top 10)

"List 10 things this role knows cold (top beliefs without thinking). Numbered list."

### Step 4 — Decision criteria

"What makes them say YES vs NO in a meeting? 3-5 bullets."

### Step 5 — Voice + communication

"Tone descriptors, preferred phrases (3-5), avoided phrases (3-5)."

### Step 6 — Outcome lens per phase

For each relevant cycle phase (including SCOPE when used), capture what this role needs
from its outcome. One concise statement per phase is sufficient; do not repeat questions
when the brief already supplies the answer.

### Step 7 — Role-specific insights

"Top patterns, common mistakes, what differentiates great vs good for this role. Free-form, ~200 words."

### Step 8 — Companion skills + agents

"Which Lintel skills/agents prefer this role?" (pack-provided skills/agents — none ship with Lintel itself; e.g. a pack's executive-brief skill, advisor agent, proposal-drafter.)

### Step 9 — Sensitive context (private roles only)

Capture only explicitly authorized, necessary context. Never solicit credentials,
customer PII or unnecessary named-person detail. Private storage is not permission to
collect or publish sensitive data.

Warn explicitly: this section is NOT loaded into session by default (only via `/li-role --deep-dive` with confirmation).

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

Publish the reviewed draft through the helper:

```bash
bash "$LINTEL_SOURCE_ROOT/bin/li-lifecycle" \
  --source "$LINTEL_SOURCE_ROOT" --repo "$LINTEL_REPO_ROOT" \
  role-write "$role_id" --file "$reviewed_draft" --scope "$sensitivity"
```

The helper validates metadata, identity, sensitivity and all specialist sections before
writing. Private roles use `LINTEL_PRIVATE_ROLES_DIR` or the configured home's private
roles directory. Public roles use the defining pack's role directory, or explicitly
selected public home storage when no pack directory is configured. Show that resolved
destination before publication. A duplicate requires a reviewed-digest update, never an
unqualified overwrite. Incomplete drafts stay at the explicitly selected draft path and
must not appear as ready roles.

### Step 11 — Surface result + offer activation

Report the verified path and SHA-256, with activation and synchronization both false.
Activate only if separately requested, via `/li-role <id>`. Do not automatically append
private paths or content to committed/shared evidence.

## --update <id> — evolve an existing role

Targeted edits, not rewrites (wholesale rewrite = re-scaffold via create mode). Sensitivity-aware: private role updates never leak to a public marketplace. Target defaults to the active role (`role_active` in `~/.lintel/profile.yaml`); if none specified and none active, list roles via `/li-roles-list`.

1. **Locate + read** the role file (public/private/home paths, same resolution as `/li-role`).
2. **Diagnose the update type** (ask_user):
   - A) Add insight to ROLE-SPECIFIC INSIGHTS — "What's the new insight? 1-3 sentences. What pattern, what mistake to avoid, what differentiator?"
   - B) Add to COLD KNOWLEDGE — "What's the new fact? Format: 'role knows X without thinking'."
   - C) Refine VOICE — "New preferred phrase OR avoided phrase? With brief reason."
   - D) Refine OUTCOME LENS — "Which phase? What new lens?"
   - E) Update DECISION CRITERIA — "New yes/no factor + how it ranks against existing criteria?"
   - F) Other (free-form section edit)
3. **Sensitivity check**:
   - Private role: confirm "Update saved to the private role file, not pushed to a public marketplace. Continue?"
   - Public role: confirm no PII; soft-scan the update text for PII patterns — warn + refuse on detection.
4. **Prepare**: edit a reviewed draft of the relevant section, update `last_updated`,
   and preserve other expertise/formatting. Retain the original SHA-256 from `role-show`;
   private body reads still require consent.
5. **Publish**: run `role-write` with the same ID/scope and
   `--expected-sha256 "$reviewed_sha256"`. Changed originals, malformed drafts and
   sensitivity changes are refused before overwriting. Report the verified new digest.
6. **Sync boundary**: configuration alone is not permission to publish. Invoke the
   accepted `bin/li-roles-sync` only on a separate explicit request for its current
   configured private destination. Local creation/update never activates private sync.
7. Keep sensitive update evidence private; no fabricated work-ledger event is required.

If the operator is unsure an update is durable: capture it as PROVISIONAL with a low-confidence flag — promotable later.

## Anti-patterns

- **PII in COLD KNOWLEDGE / INSIGHTS** — explicit warning + soft refusal
- **One-off persona as a role file** — roles are durable; one-offs are inline operator context
- **Skipping the sensitivity declaration** — must be explicit, never default
- **Auto-applying every session learning via --update** — the operator filters; only durable patterns land in the file
- **Updating the active session role without explicit operator confirmation**
