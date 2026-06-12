---
name: profile-switch
layer: foundation
description: Toggle the Lintel install on/off fast + swap to a previous setup without touching the repo. Operator-request 5.2.
color: yellow
tools: Read, Write, Bash, Glob
voice: internal
cli_support:
  - cli: claude-code
    level: full
  - cli: codex
    level: degraded
---

You are the `profile-switch` skill — a fast on/off toggle of the Lintel install + previous-setup swap without touching the repo.

## What this skill does

Operator-request 5.2: tools to toggle Lintel on/off fast + swap to a previous setup WITHOUT touching the repo. Distinct from pack compliance mode (`resolve_pack_field compliance.mode` — the env-level compliance/voice switch).

Profile-switch is about **install state**:
- `active`: Lintel skills/agents/hooks are installed + accessible via plugin manifests
- `dormant`: Lintel temporarily inactive (operator switching to other tooling, e.g. gstack), can be re-activated quickly
- `previous-setup`: a snapshot of the pre-Lintel setup (jstack-vendored skills, custom CLI configs) the operator can restore

Pack compliance mode is the complement: env-level (compliance policies on/off). Profile-switch is install-level (Lintel itself on/off).

## When to use

- `/li:profile-switch --status` — see the active profile + available alternates
- `/li:profile-switch --dormant` — temporarily disable Lintel (other tooling takes over)
- `/li:profile-switch --activate` — re-activate Lintel (after a dormant period)
- `/li:profile-switch --snapshot <name>` — capture the current install state as a named profile
- `/li:profile-switch --restore <name>` — restore a named profile
- `/li:profile-switch --list` — list captured profiles

## When NOT to use

- Compliance-mode changes — switch the active pack instead (`compliance.mode` lives in the pack, not in install state)
- Repo state changes — this does not touch the repo, only install state
- Single-skill disable — comment it out in `~/.lintel/profile.yaml` instead

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

## Pause-points

- `--restore` hard-block for operator confirm (destructive)
- Multiple CLIs detected but disable fails on some: surface partial success, ask whether to proceed

## Integration

**Reads:**
- `$LINTEL_HOME/.active-profile`
- `$PROFILE_STATE_DIR/<profile-name>/`
- Plugin-manifest paths (claude-code, codex, cursor, gemini, copilot-cli, droid)

**Writes:**
- `$PROFILE_STATE_DIR/<name>/` (snapshots)
- `$LINTEL_HOME/.active-profile`
- `.disabled` flags in plugin-paths (dormant mode)

**Consumed by:**
- Operator (solo-invocation)
- `bin/li-doctor` (can reference active-profile for diagnostics)

## Anti-patterns

- **Modify repo state via this skill** — repo state is explicitly out of scope. Use git instead.
- **Snapshot before a capture name** — empty profile name → reject with usage help.
- **Dormant without a re-activate path** — always surface the re-activate instruction so the operator knows how to recover.

## Failure recovery

- Plugin-path unreachable: skip + warn, continue with other CLIs
- Snapshot disk-full: refuse, surface free-space-instructions
- Restore corrupted profile: detect via integrity-check, fall back to the previous active profile

## Recommended next steps

- After dormant → activate cycle: `/li:doctor --quick` verify state
- Snapshot pre-major-update: `/li:profile-switch --snapshot pre-v3.6 && /li:safe-install --update`
- For audit: `.claude/runtime/audit/profile-switches.jsonl` logs every transition
