---
name: role
layer: foundation
description: Use to take on or change a working role — activate one for a lightweight lens, turn it off, swap mid-session, apply its lens to an artifact, or load its full definition on demand. Reach for it when work would benefit from a specific role's perspective; one role is active at a time.
color: cyan
tools: Read, Bash, Edit, Grep, Glob
voice: internal
cli_support: [claude-code, codex]
---

You are the role skill — the lifecycle command for session roles.

## Actions

| Invocation | Does |
|---|---|
| `/li:role <role-id>` | Activate — light load (~500 tokens), sets `role_active` in profile |
| `/li:role --off` | Deactivate — clears overlay, voice tier reverts to mode/profile default |
| `/li:role --rotate <role-id>` | Swap roles atomically — verify new, deactivate current, activate new |
| `/li:role --frame <artifact>` | Apply the active role's outcome-lens to an artifact |
| `/li:role --deep-dive [role-id]` | Load the FULL role file (~2-3k tokens) on demand |

Create or evolve role files with `/li:role-new` (and `/li:role-new --update <id>`); discover them with `/li:roles-list`.

## Role resolution (shared by all actions)

Roles resolve from the active pack's role directory, then the operator's private and public home roles. The repo ships no roles of its own.

```bash
PACK_ROLES_DIR="$(resolve_pack_field roles.source)"   # may be empty (none in _default)
ROLE_FILE=""
for candidate in \
  "${PACK_ROLES_DIR:+$PACK_ROLES_DIR/${ROLE_ID}.md}" \
  "$LINTEL_HOME/roles/private/${ROLE_ID}.md" \
  "$LINTEL_HOME/roles/${ROLE_ID}.md"; do
  [ -n "$candidate" ] && [ -f "$candidate" ] && { ROLE_FILE="$candidate"; break; }
done
[ -z "$ROLE_FILE" ] && { echo "Role '$ROLE_ID' not found."; /li:roles-list; exit 1; }
```

## Activate (default action)

Loads the role's IDENTITY + VOICE + OUTCOME-LENS summary into session context (~500 tokens total) and updates `~/.lintel/profile.yaml` so subsequent phases (DEFINE/SHIP/CAPTURE most affected) apply the role overlay. Replaces any previously-active role. Does NOT load the full role file — that is `--deep-dive`.

1. Resolve the role file. If `sensitivity: private`: confirm first — "Activate private role <id>? Sensitive context stays in `.claude/runtime/state/role-lens-notes/` per session, not exported."
2. Parse frontmatter (`role_id`, `display_name`, `scope`, `audience`, `voice_tier`, `sensitivity`) plus the IDENTITY section, VOICE + COMMUNICATION section, OUTCOME LENS summary table (phase → one-liner), and COMPANION SKILLS list. Do NOT load COLD KNOWLEDGE, full DECISION CRITERIA, ROLE-SPECIFIC INSIGHTS, or SENSITIVE CONTEXT.
3. Update the profile (preserve all other fields; if the file is malformed, warn and write a fresh `role_active` entry):
   ```bash
   sed -i "s/^role_active:.*/role_active: ${ROLE_ID}/" "$LINTEL_HOME/profile.yaml"
   ```
4. Surface to the operator (this becomes session context that subagents inherit): display name, scope, audience, voice tier, sensitivity, identity paragraph, voice summary, per-phase outcome-lens one-liners, companion skills — plus pointers to `--deep-dive`, `--rotate`, `--off`.
5. Append `event: role_activated` (role_id, voice_tier_change, sensitivity) to `.claude/runtime/state/00-state.md`.

The role's voice_tier propagates to downstream skills; an elevated tier auto-applies the active pack's voice gate for customer-facing output (none by default).

## --off (deactivate)

Clears the active role. Voice tier reverts to the mode/profile default; the overlay no longer applies to subsequent skills. Useful when the session shifts to pure engineering work and the overlay would add noise. To switch roles instead, use `--rotate`; to ignore the role for one task, pass `--no-role` to that skill.

1. Read `role_active` from `~/.lintel/profile.yaml`. If empty/null: "No role active. Nothing to deactivate." — stop.
2. If the role is private: ask "Save current session's role-lens-notes?" — preserve `.claude/runtime/state/role-lens-notes-<ts>.md` on yes, clear on no. Surface that sensitive context may still be in conversation history.
3. `sed -i "s/^role_active:.*/role_active: null/" "$LINTEL_HOME/profile.yaml"` — deactivation persists across sessions (the next session starts role-less).
4. Append `event: role_deactivated` (role_id, sensitivity, notes_preserved) to 00-state.

## --rotate <role-id>

Atomically swaps the active role: deactivate current + activate new. Session memory (lessons, context, artifacts) is preserved — only the role overlay changes. For a first activation use the default action directly.

1. **Verify the new role file exists BEFORE deactivating the current one** (resolution above). If missing: "New role '<id>' not found. Current role '<current>' kept active." — list roles, stop.
2. Sensitivity transition gates:
   - public → private: warn the session is gaining sensitive context, confirm.
   - private → public: surface that sensitive context is dropped from the overlay (persisted in role-lens-notes for the session record).
3. Mark the current role deactivated in 00-state, then run the default activate action for the new role (lightweight load).
4. Surface the transition (`<from> → <to>`, session memory preserved, deep-dive pointer) and append `event: role_rotated` (from, to, sensitivity_shift: none | gained | dropped).

## --frame <artifact>

Applies the active role's lens to an artifact (design doc, proposal, plan, PR description, customer email) and surfaces what the role would notice. Requires an active role and an existing artifact path — otherwise stop and say so. Operates at the SURFACE level using the ~500-token activation context; for high-stakes artifacts, `--deep-dive` first, then frame. Frame is broader than a voice gate: decision criteria + cold knowledge + voice.

1. Read the artifact. Apply the role's DECISION CRITERIA (does the artifact serve them?), COLD KNOWLEDGE (does it match what the role knows?), VOICE preferences, and the OUTCOME LENS for the current phase if a cycle is in progress.
2. Surface findings: strengths (what the role would respond to), gaps (with recommended additions), voice misalignment (phrase-level), decision-criteria fit (met / partial / not met), and suggested edits prioritized P1-P3 with file:line.
3. Private role: findings are operator-internal — write them to `.claude/runtime/state/role-lens-notes-<ts>.md` (gitignored) instead of inline-editing, and never propagate role-specific insights into the artifact unless the operator explicitly accepts each suggestion.
4. Operator decides edits (gate): apply all P1+P2 / P1 only / selectively per edit / findings only. Never blanket-overwrite the artifact with the role's voice. If edits applied: re-frame to verify alignment.
5. Append `event: role_frame` (role_id, artifact_path, findings per priority, edits_applied) to 00-state.

Voice deviation: findings are operator-internal (`internal`); applied artifact edits inherit the role's voice_tier.

## --deep-dive [role-id]

Loads the COMPLETE role file (~2-3k tokens): COLD KNOWLEDGE, DECISION CRITERIA, ROLE-SPECIFIC INSIGHTS, full OUTCOME LENS, COMPANION SKILLS. Use when the role's full expertise is needed (customer-facing drafting in the role's voice, deep evaluation against its criteria, "what does <role> actually know about X?"). Defaults to the active role when no id is given; if none active and none given, list roles and stop.

1. Resolve and read the full role file.
2. Private role gate: confirm "Deep-dive on private role <id>? Sensitive info will be in session." — abort on no.
3. Inject as a structured block — subagents spawned afterwards inherit it.
4. **Surface the token cost**: tokens added, context budget before/after. If the budget is tight: warn and suggest cool-down before retrying. Do NOT deep-dive at session start — lightweight activation is the session-start path.
5. Append `event: role_deep_dive` (role_id, sensitivity, tokens_added) to 00-state.

## Anti-patterns

- **Multi-loading roles** — one role active at a time; rotate, don't multi-load. Frequent rotations (>3 per session) cause context jitter and confuse subagents.
- **Auto-activating without an operator command** — the operator opts in explicitly.
- **Cross-contaminating private role context into public artifacts** — strict separation; per-edit approval only. Deactivation does not scrub conversation history — surface that.
- **Loading the full role file outside `--deep-dive`** — light by default; deep knowledge on-demand.
- **Caching deep-dive content across sessions without consent** — sensitive info should not persist longer than needed.
