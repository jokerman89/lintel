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
| `/li:role --audience [name]` | List or load an explicitly selected audience persona for this conversation without changing role/profile state |
| `/li:role --clear-audience` | Stop applying the audience overlay to future responses; persisted data and prior conversation remain |

Create or evolve role files with `/li:role-new` (and `/li:role-new --update <id>`); discover them with `/li:roles-list`.

## Audience context without a profile change

`--audience` is a conversational lens, separate from the persistent working role.
Resolve allowed sources through the existing source-owned helper:

```bash
bash "$LINTEL_SOURCE_ROOT/bin/li-lifecycle" \
  --source "$LINTEL_SOURCE_ROOT" --repo "$LINTEL_REPO_ROOT" persona-sources
```

This preserves verified profile selection and anchors relative pack persona sources
at their defining manifest. List available names and concise purpose before loading
an unselected persona. Read only the selected, authorized definition from the returned
sources, including `.claude/memory/personas.md` or `docs/personas` where declared.
Do not search another checkout or private home to manufacture a missing result.

Apply its responsibilities, concerns, communication preferences, decision criteria and
pitfalls to the requested task. Ask if its voice conflicts with required policy.
Missing names stay missing; list actual choices rather than inventing a persona.
Keep customer/private context out of public artifacts and pass only an explicitly
authorized summary to a delegate. No automatic inheritance or independent review is
implied. `--clear-audience` ends future use of the overlay but cannot erase conversation
content; neither action edits profile files, packs, durable memory or host settings.

## Role resolution (shared by all actions)

Roles resolve through the actual helper, from the active pack's role directory, then
configured private roles and public home roles. The repo ships no roles of its own.
Relative pack paths are anchored to their defining manifest, not the current directory.
Follow [lifecycle paths](../../docs/lifecycle.md); no guessed home or private sync.

```bash
bash "$LINTEL_SOURCE_ROOT/bin/li-lifecycle" \
  --source "$LINTEL_SOURCE_ROOT" --repo "$LINTEL_REPO_ROOT" role-list
```

## Activate (default action)

Loads the role's IDENTITY + VOICE + OUTCOME-LENS summary into session context (~500 tokens total) and updates `~/.lintel/profile.yaml` so subsequent phases (DEFINE/SHIP/CAPTURE most affected) apply the role overlay. Replaces any previously-active role. Does NOT load the full role file — that is `--deep-dive`.

1. Resolve the role file. If `sensitivity: private`: confirm first — "Activate private role <id>? Sensitive context stays in `.claude/runtime/state/role-lens-notes/` per session, not exported."
2. Parse frontmatter (`role_id`, `display_name`, `scope`, `audience`, `voice_tier`, `sensitivity`) plus the IDENTITY section, VOICE + COMMUNICATION section, OUTCOME LENS summary table (phase → one-liner), and COMPANION SKILLS list. Do NOT load COLD KNOWLEDGE, full DECISION CRITERIA, ROLE-SPECIFIC INSIGHTS, or SENSITIVE CONTEXT.
3. Call the owned helper. Add `--allow-private` only after consent to load that private
   context. It validates the selected role and preserves unrelated preference bytes.
   A malformed or duplicate-key profile is refused, never rewritten from scratch:
   ```bash
   bash "$LINTEL_SOURCE_ROOT/bin/li-lifecycle" \
     --source "$LINTEL_SOURCE_ROOT" --repo "$LINTEL_REPO_ROOT" role-set "$ROLE_ID"
   ```
4. Surface the returned lightweight summary: display name, scope, audience, voice tier,
   sensitivity, identity, communication, outcome-lens and companion skills. Include
   `--deep-dive`, `--rotate`, `--off`. Pass only needed, authorized context to delegated
   work; neither discovery nor automatic inheritance is guaranteed by this command.
5. Retain the actual result in task evidence if needed; do not invent a ledger event schema.

The role's voice_tier propagates to downstream skills; an elevated tier auto-applies the active pack's voice gate for customer-facing output (none by default).

## --off (deactivate)

Clears the active role. Voice tier reverts to the mode/profile default; the overlay no longer applies to subsequent skills. Useful when the session shifts to pure engineering work and the overlay would add noise. To switch roles instead, use `--rotate`; to ignore the role for one task, pass `--no-role` to that skill.

1. Read `role_active` from `~/.lintel/profile.yaml`. If empty/null: "No role active. Nothing to deactivate." — stop.
2. Preserve existing private notes. Any new save or deletion needs its own explicit
   path/scope; deactivation does not erase sensitive conversation history.
3. Run `role-off` through `bin/li-lifecycle.py` with the same source/target roots. The
   verified preference change persists; existing private notes are preserved unless
   their exact deletion was separately authorized.
4. Report `previous_role`, `active_role`, and whether it changed.

## --rotate <role-id>

Atomically swaps the active role: deactivate current + activate new. Session memory (lessons, context, artifacts) is preserved — only the role overlay changes. For a first activation use the default action directly.

1. **Verify the new role file exists BEFORE deactivating the current one** (resolution above). If missing: "New role '<id>' not found. Current role '<current>' kept active." — list roles, stop.
2. Sensitivity transition gates:
   - public → private: warn the session is gaining sensitive context, confirm.
   - private → public: surface that sensitive context is dropped from the overlay (persisted in role-lens-notes for the session record).
3. Run one `role-set <new-id>` operation. Do not deactivate first: lookup, sensitivity,
   parsing or write failure must retain the previous preference.
4. Surface the verified transition, preserved session memory and deep-dive pointer.

## --frame <artifact>

Applies the active role's lens to an artifact (design doc, proposal, plan, PR description, customer email) and surfaces what the role would notice. Requires an active role and an existing artifact path — otherwise stop and say so. Operates at the SURFACE level using the ~500-token activation context; for high-stakes artifacts, `--deep-dive` first, then frame. Frame is broader than a voice gate: decision criteria + cold knowledge + voice.

1. Read the artifact and apply the actually loaded voice/outcome lens. If decision
   criteria or cold knowledge are needed, request the bounded deep dive first rather
   than inventing unseen expertise. Apply the current phase's lens where relevant.
2. Surface findings: strengths (what the role would respond to), gaps (with recommended additions), voice misalignment (phrase-level), decision-criteria fit (met / partial / not met), and suggested edits prioritized P1-P3 with file:line.
3. Private role: findings are operator-internal — write them to `.claude/runtime/state/role-lens-notes-<ts>.md` (gitignored) instead of inline-editing, and never propagate role-specific insights into the artifact unless the operator explicitly accepts each suggestion.
4. Operator decides edits (gate): apply all P1+P2 / P1 only / selectively per edit / findings only. Never blanket-overwrite the artifact with the role's voice. If edits applied: re-frame to verify alignment.
5. Record actual findings/edits in the selected work evidence; framing is not an independent review.

Voice deviation: findings are operator-internal (`internal`); applied artifact edits inherit the role's voice_tier.

## --deep-dive [role-id]

Loads the COMPLETE role file (~2-3k tokens): COLD KNOWLEDGE, DECISION CRITERIA, ROLE-SPECIFIC INSIGHTS, full OUTCOME LENS, COMPANION SKILLS. Use when the role's full expertise is needed (customer-facing drafting in the role's voice, deep evaluation against its criteria, "what does <role> actually know about X?"). Defaults to the active role when no id is given; if none active and none given, list roles and stop.

1. Inspect metadata; obtain private-context consent before loading a private body.
2. Run `role-show <id> --deep` through the helper; add `--allow-private` only with that consent.
3. Load the returned full definition for the requested purpose. Explicitly scope any
   delegated handoff instead of promising automatic subagent inheritance.
4. Surface host-reported token cost when available, otherwise label an estimate or unknown.
   Do not claim cooling erases already supplied conversation content.

## Anti-patterns

- **Multi-loading roles** — one role active at a time; rotate, don't multi-load. Frequent rotations (>3 per session) cause context jitter and confuse subagents.
- **Auto-activating without an operator command** — the operator opts in explicitly.
- **Cross-contaminating private role context into public artifacts** — strict separation; per-edit approval only. Deactivation does not scrub conversation history — surface that.
- **Loading the full role file outside `--deep-dive`** — light by default; deep knowledge on-demand.
- **Caching deep-dive content across sessions without consent** — sensitive info should not persist longer than needed.
