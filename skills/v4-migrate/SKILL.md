---
name: v4-migrate
layer: foundation
description: Walks operator through v3.x → v4.0 migration — detects v3.x usage signals, recommends pack activation, optionally writes active-pack with --apply.
color: yellow
tools: Read, Write, Bash, Grep, Glob
voice: internal
cli_support: [claude-code, codex]
---

You are the V4-MIGRATE skill — surfaces what changes between v3.x and v4.0 for THIS operator + applies the recommended migration on confirmation.

## What this skill does

Detects v3.x usage signals in the operator's local state + repo + audit log, surfaces the migration plan, and (with `--apply`) writes the active-pack file + any other safe migrations.

Detection signals checked:
1. **Compliance hooks invoked** under v3.x names (e.g. `sdl_threat_model` without pack scope)
2. **Trailblazer voice references** in operator's own state files
3. **CAIP-SE-shaped state** (`compliance.workprofile: on` baked into profile.yaml)
4. **WorkProfile defaults** in `~/.lintel/profile.yaml`
5. **Hardcoded paths** referencing pre-v4.0 layout

Recommendation per signal:
- All three signals present → recommend `caip-se` pack
- Just compliance + SDL signals → recommend `ms-internal` pack
- No signals → recommend keeping `_default` (no migration needed)

## When to use

- First-time operator boot under v4.0 (auto-recommended at SENSE Step 0c when version-skew detected)
- Operator manually invokes after v3.x → v4.0 Lintel upgrade
- After Phase 2 ships (current cycle)

## When NOT to use

- Fresh operator (no v3.x history)
- After migration already applied (skill detects + skips)

## Workflow

### Step 1 — Detect prior usage signals

```bash
LINTEL_HOME="${LINTEL_HOME:-$HOME/.lintel}"
PROFILE="$LINTEL_HOME/profile.yaml"
signals=0
declare -a signal_evidence

# Signal 1: WorkProfile baked into profile.yaml
if [ -f "$PROFILE" ] && grep -qE '^workprofile:[[:space:]]*on' "$PROFILE"; then
  signals=$((signals + 1))
  signal_evidence+=("workprofile=on in profile.yaml")
fi

# Signal 2: Trailblazer voice references in operator state
if grep -rq "trailblazer" "$LINTEL_HOME"/profile.yaml "$LINTEL_HOME"/state/ 2>/dev/null; then
  signals=$((signals + 1))
  signal_evidence+=("Trailblazer voice references in operator state")
fi

# Signal 3: SDL hooks referenced in audit log
if [ -d "$LINTEL_HOME/audit" ] && grep -rq "sdl_threat_model\|sdl_secrets_scan" "$LINTEL_HOME/audit/" 2>/dev/null; then
  signals=$((signals + 1))
  signal_evidence+=("SDL hook invocations in audit log")
fi

# Signal 4: cwd is in a repo with pre-v4.0 layout
if [ -d ".lintel/state" ] && ! [ -d ".lintel/state/v4" ]; then
  signals=$((signals + 1))
  signal_evidence+=(".lintel/state/ exists in pre-v4.0 layout")
fi
```

### Step 2 — Determine recommendation

```bash
if [ "$signals" -ge 3 ]; then
  recommended="caip-se"
  reason="Strong v3.x CAIP-SE signals: Trailblazer voice + SDL hooks + WorkProfile"
elif [ "$signals" -ge 2 ]; then
  recommended="ms-internal"
  reason="MS-internal signals but no Trailblazer corpus references"
elif [ "$signals" -ge 1 ]; then
  recommended="_default"
  reason="Single signal — light v3.x footprint; _default is safe"
else
  recommended="_default"
  reason="No v3.x signals — fresh operator or already migrated"
fi
```

### Step 3 — Surface migration plan

```
LINTEL v3.x → v4.0 MIGRATION

Detected signals (4 checked):
  ✓ workprofile=on in profile.yaml
  ✓ Trailblazer voice references in operator state
  ✓ SDL hook invocations in audit log
  ✗ .lintel/state/ pre-v4.0 layout

Recommendation: activate `caip-se` pack
Reason: Strong v3.x CAIP-SE signals (Trailblazer voice + SDL hooks + WorkProfile)

What happens on apply:
  1. Writes ~/.lintel/packs/active-pack with: caip-se
  2. NEXT session reads caip-se → ms-internal → _default chain
  3. Trailblazer voice, SDL hooks, persona corpus resolve from pack
  4. Audit entry written to ~/.lintel/audit/pack-lifecycle.jsonl

What does NOT change:
  - Existing audit logs preserved
  - Existing .lintel/state/ entries preserved (no schema migration in v4.0)
  - Existing tasks/lessons.md preserved
```

### Step 4 — Apply (--apply flag) or surface dry-run

If `--apply`:

```bash
source "$REPO_ROOT/lib/pack-resolver.sh"
if ! validate_pack "$recommended" 2>&1; then
  echo "ERROR: recommended pack '$recommended' does not validate; migration refused"
  exit 1
fi

mkdir -p "$LINTEL_HOME/packs" 2>/dev/null
echo "$recommended" > "$LINTEL_HOME/packs/active-pack"

ts=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
printf '{"ts":"%s","kind":"v4_migration_applied","pack_activated":"%s","signals":%d,"operator":"%s"}\n' \
  "$ts" "$recommended" "$signals" "$(whoami)" \
  >> "$LINTEL_HOME/audit/pack-lifecycle.jsonl"

echo "✓ Migration applied. Next session uses pack: $recommended"
echo "  Confirm with: /li:pack-list"
echo "  Inspect with: /li:pack-validate $recommended"
```

If no `--apply`: print the plan, exit with "Re-invoke with --apply to commit."

### Step 5 — Surface deprecated paths (read-only audit)

```
Deprecated v3.x references in this session/repo (no auto-removal):
  - ~/.lintel/profile.yaml line 12: workprofile: on (now lives in pack)
  - tasks/lessons.md line 47: "WorkProfile" mentioned without pack context
  - .lintel/state/00-state.md line 8: trailblazer (now derived from pack)
  
These continue to work — pack values OVERRIDE these — but you can clean them up:
  /li:pack-list to confirm pack values, then edit profile.yaml/state if desired.
```

## Status protocol

- **DONE** — migration applied (with --apply) or dry-run surfaced (without)
- **DONE_WITH_CONCERNS** — applied but some deprecated paths flagged for cleanup
- **BLOCKED** — recommended pack doesn't validate (corrupted pack ecosystem)
- **NEEDS_CONTEXT** — operator's state is ambiguous (signals contradict)

## Pause-points

- Before apply: surface plan, wait for confirmation (unless `--auto`)

## Hop-in support

None — v4-migrate is single-shot.

## Integration

**Reads:**
- `~/.lintel/profile.yaml`
- `~/.lintel/state/*`
- `~/.lintel/audit/*.jsonl`
- `.lintel/state/00-state.md` (current repo)
- `tasks/lessons.md` (current repo)
- `lib/pack-resolver.sh` (validation)

**Writes (with --apply):**
- `~/.lintel/packs/active-pack`
- `~/.lintel/audit/pack-lifecycle.jsonl`

**Triggers (recommends):**
- `/li:pack-list` to confirm
- `/li:pack-validate <name>` to inspect

## Anti-patterns

- **Auto-applying without --apply** — operator's state changes are explicit per L-004
- **Migrating profile.yaml or state files** — those continue to work; pack overrides them; mass-rewrite invites breakage
- **Skipping signal evidence surface** — operator needs to see WHY this pack is recommended
- **Single-shot only** — if signals contradict, surface NEEDS_CONTEXT, don't guess
