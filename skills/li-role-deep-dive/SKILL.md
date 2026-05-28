---
name: li-role-deep-dive
layer: foundation
description: Load full role-file content on-demand — COLD KNOWLEDGE, DECISION CRITERIA, INSIGHTS, OUTCOME LENS per phase. For when operator needs role's full expertise.
color: cyan
tools: Read, Bash, Grep, Glob
voice: internal
cli_support: [claude-code, codex]
---

You are the role-deep-dive skill — full role-file load on-demand.

## What this skill does

Loads the COMPLETE role file (~2-3k tokens) into session context: COLD KNOWLEDGE, DECISION CRITERIA, ROLE-SPECIFIC INSIGHTS, OUTCOME LENS per phase, COMPANION SKILLS. Use when role's full expertise is needed for the current task.

Lightweight `/lintel:li-role-activate` loads ~500 tokens; deep-dive loads the rest.

## When to use

- Drafting customer-facing artifact and need role's full voice + insights (e.g., writing proposal in Field CTO voice with their specific cold knowledge)
- Reviewing artifact against role's decision criteria (deep evaluation, not surface check)
- Customer-specific persona context for high-stakes meeting prep
- Operator says "what does Field CTO actually know about <topic>?" — role-specific expertise lookup

## When NOT to use

- Surface-level role overlay (already loaded by role-activate)
- One-off prose tweaks (use voice tier directly)
- When token budget is tight — deep-dive is ~2-3k tokens

## Workflow

### Step 1 — Verify role is activated

```bash
active_role=$(grep '^role_active:' "$LINTEL_HOME/profile.yaml" | awk '{print $2}')
target_role="${1:-$active_role}"

if [ -z "$target_role" ]; then
  echo "No role active and no role-id provided."
  /lintel:li-roles-list
  exit 1
fi
```

### Step 2 — Locate + read full role file

```bash
for candidate in \
  "roles/${target_role}.md" \
  "$LINTEL_HOME/roles/private/${target_role}.md" \
  "$LINTEL_HOME/roles/${target_role}.md"; do
  [ -f "$candidate" ] && { ROLE_FILE="$candidate"; break; }
done

# Read entire file
cat "$ROLE_FILE"
```

### Step 3 — Surface content to session

Inject into context as a structured block. Subagents spawned subsequently inherit this.

For PRIVATE roles: warn operator that sensitive context is now loaded. AskUserQuestion "Confirm deep-dive on private role <id>? Sensitive info will be in session." (Y/n)

If yes: proceed. If no: abort, no load.

### Step 4 — Cost note

Surface token-cost impact:
```
ROLE DEEP-DIVE LOADED: <role-id>

Tokens added: ~<N>k
Context budget: <current> + <added> = <total> / 1M

Sensitive context loaded: <yes — sensitivity=private | no>
Auto-redact in this session: <yes for private | no for public>
```

### Step 5 — 00-state.md append

```yaml
event: role_deep_dive
ts: <timestamp>
role_id: <id>
sensitivity: <public/private>
tokens_added: <approx>
```

## Status protocol

- **DONE** — full role content loaded into session
- **BLOCKED** — role file not found OR sensitivity check failed
- **NEEDS_CONTEXT** — no role active and no ID provided

## Pause-points

- For private roles: confirm before loading sensitive context
- If context budget tight: warn, ask if proceed (cool-down recommendations)

## Hop-in support

YES — invokable mid-task whenever depth needed.

## Integration

**Reads:**
- Role file (full)

**Writes:**
- `.lintel/state/00-state.md` (deep-dive event)

**Triggers:**
- Subagents spawned post-load inherit deep role context

## Anti-patterns

- **Loading deep-dive at session start** — too heavy. Use `/lintel:li-role-activate` for session start.
- **Forgetting to verify sensitivity** for private roles — must confirm with operator
- **Loading multiple deep-dives simultaneously** — sequential, one at a time
- **Caching deep-dive across sessions without consent** — sensitive info should not persist longer than needed

## Failure recovery

- **Role file partially malformed**: load what's parseable, surface gaps
- **Sensitive context but operator on shared machine**: refuse load, recommend role-deactivate first
- **Budget exhausted**: surface, suggest cool-down before retry

## Voice tier behavior

`voice: internal`. Deep-dive output is operator-facing. Role's voice_tier applies to subsequent customer-facing artifacts.
