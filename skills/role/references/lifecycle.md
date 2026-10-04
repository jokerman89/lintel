# Role lifecycle

`role` owns this one procedure for `role`, `role-new` and `roles-list`. Public names
and flags remain unchanged; these are not new helper subcommands. Use the existing
`bin/li-lifecycle` / `bin/li-lifecycle.py` and [configured lifecycle roots](../../../docs/lifecycle.md).
Root flags precede the subcommand; use the explicitly selected source and working
repository, never another checkout or guessed personal store.

Listing/showing/persona discovery are read-only. Create/update publish only a reviewed
role file; set/off change only the selected working-role preference. Framing and audience
are conversational methods, not host activation, independent review or synchronization.
The neutral pack ships no role definitions. Absence is a legitimate empty inventory,
not permission to invent a role or scan a private store.

## Create and update entrypoints

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

Use an adaptive interview: reuse facts already supplied and ask only for missing
decisions. The expert-content sections below are retained, but ten facts or one question
per phase are prompts for depth, not mandatory filler. Render a reviewed draft, then
let `bin/li-lifecycle.py role-write` own publication under the
[configured lifecycle roots](../../../docs/lifecycle.md).

### Step 1 — Basic identity (AskUserQuestion sequence)

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

"Which available Lintel skills/agents fit this role?" Use actual source metadata and host
bindings, including pack-provided methods. Lintel ships skills/agents, not role definitions;
do not invent an unavailable companion.

### Step 9 — Sensitive context (private roles only)

Capture only explicitly authorized, necessary context. Never solicit credentials,
customer PII or unnecessary named-person detail. Private storage is not permission to
collect or publish sensitive data.

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
Activate only if separately requested, via `/li:role <id>`. Do not automatically append
private paths or content to committed/shared evidence.

## --update <id> — evolve an existing role

Targeted edits, not rewrites (wholesale rewrite = re-scaffold via create mode). Sensitivity-aware: private role updates never leak to a public marketplace. Target defaults to the active role (`role_active` in `~/.lintel/profile.yaml`); if none specified and none active, list roles via `/li:roles-list`.

1. **Locate metadata**, then obtain private-body consent before `role-show <id> --deep
   --allow-private` when applicable. Use the resolution below; no implicit private read.
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
     This is a manual/model content review, not an executed automated scanner or
     a waiver of any separately required content-safety control.
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

## List

`/li:roles-list` uses metadata only:

```bash
bash "$LINTEL_SOURCE_ROOT/bin/li-lifecycle" \
  --source "$LINTEL_SOURCE_ROOT" --repo "$LINTEL_REPO_ROOT" role-list
```

Add `--include-private` only for an explicit private-metadata request or session consent.
This does not authorize private body reads; those separately need `--allow-private`.
The helper resolves pack-relative `roles.source` at its defining manifest, then configured
private and public home roles. Preserve duplicate IDs as selected/shadowed rows.

Render the returned `role_id`, `display_name`, `scope`, `audience`, `voice_tier`,
`sensitivity`, `last_updated` when present, origin, selected source and actual active
role. Mark missing metadata unknown rather than guessing. Show all rows, paginating a
large list explicitly. A matching phase/audience may justify a suggestion, never activation.
Link the existing activate, deep-dive and create entrypoints.

Listing never binds a profile, changes preferences or writes a ledger/audit event.
A null reference means an unbound read; malformed metadata/preferences and profile drift
are visible errors, not an empty or healthy inventory.

## Activate and rotate

`/li:role <id>` activates a lightweight lens; `/li:role --rotate <id>` uses the **same
single set operation**, not an off-then-set sequence. Verify the new role before any
preference mutation. Missing role, private-consent refusal, parse or write failure must
retain the previous preference; report that result rather than announcing a transition.

1. Resolve metadata as above. For private context, get explicit consent **before** loading
   the body or passing `--allow-private`. Public-to-private rotation gains sensitive context;
   private-to-public stops applying it but cannot erase previous conversation or notes.
2. Run the actual helper with the authorized ID:

   ```bash
   bash "$LINTEL_SOURCE_ROOT/bin/li-lifecycle" \
     --source "$LINTEL_SOURCE_ROOT" --repo "$LINTEL_REPO_ROOT" role-set "$ROLE_ID"
   ```

   Add `--allow-private` only with that consent. The helper validates first and preserves
   unrelated preference bytes/comments in the configured home's `profile.yaml`.
   Malformed or duplicate-key preferences are refused, never reconstructed from scratch.
   A first real preference change may bootstrap the existing profile lifecycle; if binding
   is outside the task's authority, do not perform that change. Never fabricate a pin.
3. Load only the returned IDENTITY, VOICE + COMMUNICATION, OUTCOME LENS and COMPANION
   SKILLS summary (roughly 500 tokens, not a measured size). Do not load COLD KNOWLEDGE,
   full DECISION CRITERIA, ROLE-SPECIFIC INSIGHTS or SENSITIVE CONTEXT until deep-dive.
4. Report the actual previous/active role, changed flag, display name, scope, audience,
   voice and sensitivity; offer `--deep-dive`, `--rotate`, `--off`. Keep session memory
   and artifacts intact. No automatic saving of private notes or delegate inheritance
   is performed. Pass only explicitly authorized, needed context to delegated work.

Apply the role's voice within required policy and the configured voice-gate method,
without claiming that a role preference registers or executes a host hook.

## Off

`/li:role --off` calls the same source-owned helper:

```bash
bash "$LINTEL_SOURCE_ROOT/bin/li-lifecycle" \
  --source "$LINTEL_SOURCE_ROOT" --repo "$LINTEL_REPO_ROOT" role-off
```

Report `previous_role`, `active_role` and `changed`. With no active role, this is a no-op.
Otherwise stop applying the overlay; voice returns to mode/profile defaults. Preserve
all private notes and history. New saves/deletions require their own explicit path/scope;
off is not cleanup, synchronization or erasure of sensitive conversation content.

## Deep dive

`/li:role --deep-dive [id]` defaults to the actual active role. If none is active and no
ID was supplied, list the real choices and stop. Inspect metadata and obtain private-body
consent first, then:

```bash
bash "$LINTEL_SOURCE_ROOT/bin/li-lifecycle" \
  --source "$LINTEL_SOURCE_ROOT" --repo "$LINTEL_REPO_ROOT" role-show "$ROLE_ID" --deep
```

Add `--allow-private` only with consent. Load the returned complete expertise for this
purpose: COLD KNOWLEDGE, DECISION CRITERIA, ROLE-SPECIFIC INSIGHTS, full OUTCOME LENS,
COMPANION SKILLS and authorized SENSITIVE CONTEXT. Report observed token use if available,
otherwise an estimate/unknown (the historical 2–3k estimate is not telemetry).
This read does not set the working role. Do not cache or pass private content to another
session without consent; cooling cannot remove content already sent to the host.

## Frame

`/li:role --frame <artifact>` requires an active role and an existing authorized artifact.
Use the lightweight voice/outcome lens actually loaded. If the analysis needs cold
knowledge or deeper decision criteria, request deep-dive first, rather than inventing
unseen expertise. For high-stakes framing, surface that limitation before proceeding.

Report strengths, gaps, phrase-level voice misalignment, decision-criteria fit
(met/partial/not met) and P1–P3 suggested edits with file:line. Private-role findings stay
operator-internal, never inline-edited into a public artifact. If a private report is
requested, choose an explicitly owned private path, such as the configured session's
`role-lens-notes/`; do not claim notes were saved automatically.

The operator selects P1+P2, P1 only, individual suggestions or findings-only. Each private
insight needs explicit acceptance before propagation. Do not blanket-overwrite the
artifact. Re-frame actual accepted edits, preserving source voice obligations.
Framing is self-review, not an independent acceptance record.

## Audience

`/li:role --audience [name]` is a lens for the **current conversation**, separate from
persistent role/profile state. Resolve approved sources through:

```bash
bash "$LINTEL_SOURCE_ROOT/bin/li-lifecycle" \
  --source "$LINTEL_SOURCE_ROOT" --repo "$LINTEL_REPO_ROOT" persona-sources
```

The helper preserves verified profile selection and anchors inherited persona paths to
their defining manifest. List names and concise purpose before an unselected load.
Read only the selected authorized definition from the returned sources, including
`.claude/memory/personas.md` or `docs/personas` when present. Never search another checkout
or private home to manufacture a missing name.

Apply responsibilities, concerns, communication preferences, decision criteria and
pitfalls to the requested task. Resolve a voice/required-policy conflict explicitly.
Keep customer/private content out of public artifacts; only an authorized summary may
enter a handoff. No automatic inheritance or independent review is implied.
`--clear-audience` ends future overlay use; it cannot erase prior conversation. Neither
action edits packs, preferences, durable memory or host settings.

## Safeguards

- **PII in COLD KNOWLEDGE / INSIGHTS** — explicit warning + soft refusal
- **One-off persona as a role file** — roles are durable; one-offs are inline operator context
- **Skipping the sensitivity declaration** — must be explicit, never default
- **Auto-applying every session learning via --update** — the operator filters; only durable patterns land in the file
- **Updating the active session role without explicit operator confirmation**
- One working role at a time; rotate rather than stacking lenses. Avoid needless
  rotations and repeated loading; no fixed rotation count is a measured quality limit.
