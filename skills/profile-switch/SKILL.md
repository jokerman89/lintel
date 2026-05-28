---
name: profile-switch
layer: foundation
description: Toggle Lintel install on/off fast + swap till previous setup utan att röra repot. Operator-request 5.2.
color: yellow
tools: Read, Write, Bash, Glob
voice: internal
cli_support:
  - cli: claude-code
    level: full
  - cli: codex
    level: degraded
---

You are the `profile-switch` skill — fast on/off toggle av Lintel-install + previous-setup-swap utan repo-touch.

## What this skill does

Operator-request 5.2: tools för toggle Lintel on/off fast + swap till previous setup UTAN att röra repot. Distinkt från WorkProfile (env-level compliance/voice/telemetry-switch).

Profile-switch handlar om **install-state**:
- `active`: Lintel-skills/agents/hooks är installed + accessible via plugin manifests
- `dormant`: Lintel temporarily inactive (operator switching till annan tooling t.ex. gstack), kan re-aktiveras snabbt
- `previous-setup`: snapshot av pre-Lintel setup (jstack-vendored skills, custom CLI configs) som operator kan restore

WorkProfile är complement: env-level (compliance-policies on/off). Profile-switch är install-level (Lintel itself on/off).

## When to use

- `/li:profile-switch --status` — see active profile + available alternates
- `/li:profile-switch --dormant` — temporarily disable Lintel (other tooling tar over)
- `/li:profile-switch --activate` — re-activate Lintel (after dormant period)
- `/li:profile-switch --snapshot <name>` — capture current install-state som named profile
- `/li:profile-switch --restore <name>` — restore named profile
- `/li:profile-switch --list` — list captured profiles

## When NOT to use

- WorkProfile changes — use `/li:workprofile-toggle` istället (compliance on/off)
- Repo state changes — denna rör inte repot, bara install-state
- Single-skill disable — kommentera ut i `~/.lintel/profile.yaml` istället

## Workflow

### Step 1 — Locate profile-state directory

```bash
LINTEL_HOME="${LINTEL_HOME:-$HOME/.lintel}"
PROFILE_STATE_DIR="${LINTEL_HOME}/profile-states"
mkdir -p "$PROFILE_STATE_DIR"

ACTIVE_PROFILE_FILE="${LINTEL_HOME}/.active-profile"
```

### Step 2 — Execute mode

**`--status`:**
- Read `.active-profile` file → display "Active profile: <name>"
- List available profiles from `$PROFILE_STATE_DIR/`
- For each profile, show capture-date + size

**`--dormant`:**
1. Snapshot current state: `cp -r <plugin-manifests-paths> $PROFILE_STATE_DIR/_pre-dormant/`
2. Disable plugins:
   - claude-code: `~/.claude/plugins/li/.disabled` flag
   - codex: similar disable-flag
   - cursor / gemini / copilot: equivalent per plugin
3. Mark `.active-profile` as `dormant`
4. Surface: "Lintel dormant. Re-activate via /li:profile-switch --activate"

**`--activate`:**
1. Remove `.disabled` flags from plugins
2. Restore active profile pre-dormant
3. Mark `.active-profile` accordingly
4. Surface "Lintel active."

**`--snapshot <name>`:**
1. Cp plugin-manifests + LINTEL_HOME-config-state till `$PROFILE_STATE_DIR/<name>/`
2. Record metadata: capture-date, operator, summary-of-state
3. Surface "Profile '<name>' captured."

**`--restore <name>`:**
1. Confirm via AskUserQuestion (destructive — overwrites current state)
2. Cp `$PROFILE_STATE_DIR/<name>/*` back till plugin paths + config
3. Update `.active-profile` till `<name>`
4. Surface "Profile '<name>' restored. Verify via /li:doctor."

**`--list`:**
- Table-format: name | captured | size | active?

## Voice tier behavior

`voice: internal`. Operator-internal install-management.

## Status protocol

- **DONE** — operation klar, profile-state-fil uppdaterad
- **DONE_WITH_CONCERNS** — operation klar men plugin disable/enable partial (some CLI plugins unreachable)
- **BLOCKED** — `$PROFILE_STATE_DIR` permissions deny write, eller named profile not found
- **NEEDS_CONTEXT** — `--snapshot` / `--restore` utan `<name>` arg

## Pause-points

- `--restore` hard-block för operator-confirm (destructive)
- Multiple CLIs detected men disable fails på some: surface partial-success, ask if proceed

## Hop-in support

YES — solo-invokable för all 6 modes.

## Integration

**Reads:**
- `$LINTEL_HOME/.active-profile`
- `$PROFILE_STATE_DIR/<profile-name>/`
- Plugin-manifest paths (claude-code, codex, cursor, gemini, copilot-cli, droid)

**Writes:**
- `$PROFILE_STATE_DIR/<name>/` (snapshots)
- `$LINTEL_HOME/.active-profile`
- `.disabled`-flags i plugin-paths (dormant mode)

**Consumed by:**
- Operator (solo-invocation)
- `bin/li-doctor` (kan reference active-profile för diagnostic)

## Anti-patterns

- **Modify repo-state via denna skill** — repo-state är explicit out-of-scope. Use git instead.
- **Snapshot innan capture-name** — empty profile-name → reject med usage-help.
- **Dormant utan re-activate-path** — always surface re-activate-instruction so operator knows how to recover.

## Failure recovery

- Plugin-path unreachable: skip + warn, continue with other CLIs
- Snapshot disk-full: refuse, surface free-space-instructions
- Restore corrupted profile: detect via integrity-check, fall back till previous active profile

## Recommended next steps

- After dormant → activate cycle: `/li:doctor --quick` verify state
- Snapshot pre-major-update: `/li:profile-switch --snapshot pre-v3.6 && /li:safe-install --update`
- For audit: `~/.lintel/audit/profile-switches.jsonl` logs every transition
