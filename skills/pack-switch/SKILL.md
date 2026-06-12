---
name: pack-switch
layer: foundation
description: Switches the active pack — writes ~/.lintel/packs/active-pack, validates the target, audits the switch.
color: green
tools: Read, Write, Bash
voice: internal
cli_support: [claude-code, codex]
---

You are the PACK-SWITCH skill — switches which pack the operator's cycles read from.

## What this skill does

Writes `~/.lintel/packs/active-pack` to the new pack name. The next session picks up the new pack; the current session keeps its cached pack (per pack-resolver semantics in [pack-resolver.md](../../docs/concepts/pack-resolver.md)).

## When to use

- Operator moves from one customer/team domain to another
- Operator wants to test a newly created pack
- After running `/li:v4-migrate` (which recommends pack-switch as the final step)

## When NOT to use

- Mid-cycle — switch takes effect at NEXT session; the current cycle ignores
- One-off override for a single workflow — use `--mode` or `--pack <name>` flags

## Workflow

### Step 1 — Resolve target pack

```bash
target="${1:?usage: /li:pack-switch <pack-name>}"
source "$REPO_ROOT/lib/pack-resolver.sh"

if ! validate_pack "$target" 2>&1; then
  echo "ERROR: pack '$target' does not validate; switch refused"
  echo "Hint: /li:pack-list to see valid packs"
  exit 1
fi
```

### Step 2 — Read current active

```bash
LINTEL_HOME="${LINTEL_HOME:-$HOME/.lintel}"
ACTIVE_FILE="$LINTEL_HOME/packs/active-pack"
mkdir -p "$LINTEL_HOME/packs" 2>/dev/null

current="_default"
[ -f "$ACTIVE_FILE" ] && current=$(head -1 "$ACTIVE_FILE" | tr -d '[:space:]')
```

### Step 3 — Confirm switch (when target differs)

If `current == target`: no-op, surface "already active" and exit DONE.

Otherwise surface diff:

```
Pack switch:
  Current: <current>
  Target:  <target>

  Effective at: next session (current session keeps cached pack)
  Operator's workflows after switch: <target>'s defaults
  
  Proceed? [Y/n]
```

### Step 4 — Write active-pack file + audit

```bash
echo "$target" > "$ACTIVE_FILE"

ts=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
printf '{"ts":"%s","kind":"pack_switched","from":"%s","to":"%s","operator":"%s"}\n' \
  "$ts" "$current" "$target" "$(whoami)" \
  >> "$LINTEL_HOME/audit/pack-lifecycle.jsonl"

echo "✓ Active pack: $target (next session)"
```

### Step 5 — Surface effective changes

Read both packs and surface fields that differ:

```
Effective field changes (next session):
  voice.default_tier: <old> → <new>
  compliance.mode:    <old> → <new>
  navigation.default_workflow: <old> → <new>
  (etc.)
```

Operator sees what changes before living with the new pack.

## Pause-points

- Step 3: confirm switch when current ≠ target (skipped with `--auto`)

## Integration

**Reads:**
- `lib/pack-resolver.sh` (validation)
- `~/.lintel/packs/<target>/pack.yaml` (field-diff)
- `~/.lintel/packs/<current>/pack.yaml` (field-diff)

**Writes:**
- `~/.lintel/packs/active-pack`
- `~/.lintel/audit/pack-lifecycle.jsonl`

## Anti-patterns

- **Skipping field-diff surface** — operator deserves to see what changes
- **Switching mid-cycle and expecting current session to update** — per resolver semantics, cache survives until next session
- **Auto-switching after `/li:pack-create`** — operator decides

## Mid-session override

If the operator REALLY wants the current session to pick up the new pack:

```bash
# Run clear_pack_cache from a shell that sources lib/pack-resolver.sh
source $REPO_ROOT/lib/pack-resolver.sh && clear_pack_cache
```

This is documented but not automated — explicit override per L-004.
