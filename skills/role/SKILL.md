---
name: role
layer: foundation
description: Use to take on or change a working role — activate one for a lightweight lens, turn it off, swap mid-session, apply its lens to an artifact, or load its full definition on demand. Reach for it when work would benefit from a specific role's perspective; one role is active at a time.
color: cyan
tools: Read, Bash, Edit, Grep, Glob
voice: internal
cli_support: [claude-code, codex, copilot]
---

The role skill owns the [shared role lifecycle](references/lifecycle.md) used by
this entry, `role-new` and `roles-list`. Read its selected procedure before acting.

## Actions

| Invocation | Does |
|---|---|
| `/li:role <role-id>` | Activate — light load (~500 tokens), sets `role_active` in profile |
| `/li:role --off` | Deactivate — clears overlay, voice tier reverts to mode/profile default |
| `/li:role --rotate <role-id>` | One validated set; failure retains the previous selection |
| `/li:role --frame <artifact>` | Apply the active role's outcome-lens to an artifact |
| `/li:role --deep-dive [role-id]` | Load the FULL role file (~2-3k tokens) on demand |
| `/li:role --audience [name]` | List or load an explicitly selected audience persona for this conversation without changing role/profile state |
| `/li:role --clear-audience` | Stop applying the audience overlay to future responses; persisted data and prior conversation remain |

Create or evolve role files with `/li:role-new` (and `/li:role-new --update <id>`); discover them with `/li:roles-list`.

## Method and authority

The shared lifecycle owns resolution, private consent, the real CLI invocations,
create/update interview, expected-digest conflict handling, listing, activation,
failure-safe rotation, off, framing, deep-dive and audience context. No additional
role parser or selector belongs here.

One working role is active at a time. A role file is not an installed agent or a
grant of host authority. Audience changes remain conversation-only, while persistent
set/off and role publication need the scope stated in that method.
