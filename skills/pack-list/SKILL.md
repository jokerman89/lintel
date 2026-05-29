---
name: pack-list
layer: foundation
description: Lists every pack discoverable in ~/.lintel/packs/ and repo packs/ — shows name, extends, voice tier, compliance mode, active flag.
color: green
tools: Read, Bash, Glob
voice: internal
cli_support: [claude-code, codex]
---

You are the PACK-LIST skill — surfaces every pack available on this machine.

## What this skill does

Walks `~/.lintel/packs/` + `<repo>/packs/`, parses each pack.yaml, prints a table:

```
PACK              ACTIVE  EXTENDS       VOICE       COMPLIANCE  REQUIRES
_default                                internal    advisory    >=4.0.0
ms-internal               (none)        mixed       hard        >=4.0.0
caip-se           *       ms-internal   trailblazer hard        >=4.0.0
foo-customer              caip-se       trailblazer hard        >=4.0.0
```

`*` marks the active pack.

## When to use

- Operator forgot which packs exist
- Before `/li:pack-switch` to confirm target
- Before `/li:pack-create` to avoid name collision
- After `/li:v4-migrate` to confirm caip-se is present

## When NOT to use

- Mid-cycle (no need; the cached pack is what matters)
- For pack-content introspection — read the pack.yaml directly

## Workflow

### Step 1 — Discover pack directories

```bash
LINTEL_HOME="${LINTEL_HOME:-$HOME/.lintel}"
REPO_PACKS="$(git rev-parse --show-toplevel 2>/dev/null)/packs"
HOME_PACKS="$LINTEL_HOME/packs"

packs=()
for base in "$HOME_PACKS" "$REPO_PACKS"; do
  [ -d "$base" ] || continue
  while IFS= read -r d; do
    [ -f "$d/pack.yaml" ] && packs+=("$(basename "$d"):$base")
  done < <(find "$base" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | sort)
done
```

### Step 2 — Read active pack

```bash
ACTIVE_FILE="$LINTEL_HOME/packs/active-pack"
active="_default"
[ -f "$ACTIVE_FILE" ] && active=$(head -1 "$ACTIVE_FILE" | tr -d '[:space:]')
```

### Step 3 — Parse each pack + emit table

For each pack, extract:
- `name`
- `extends` (or `(none)`)
- `voice.default_tier`
- `compliance.mode`
- `requires_lintel`

Emit aligned table to stdout. Mark active pack with `*`.

### Step 4 — Validation indicator (optional, --validate)

If `--validate` flag: invoke `validate_pack` per row, print `OK` or `FAIL` in extra column.

```bash
if [ "$VALIDATE" = "1" ]; then
  source "$REPO_ROOT/lib/pack-resolver.sh"
  for row in "${packs[@]}"; do
    name="${row%%:*}"
    if validate_pack "$name" 2>/dev/null; then
      echo "  $name: VALID"
    else
      echo "  $name: INVALID — run /li:pack-validate $name for details"
    fi
  done
fi
```

### Step 5 — Surface counts + footer

```
Total: 4 packs (1 active)
Sources: ~/.lintel/packs (2), <repo>/packs (2)
```

Footer:
- "Switch active: `/li:pack-switch <name>`"
- "Create new: `/li:pack-create <name>`"
- "Validate all: `/li:pack-list --validate`"

## Status protocol

- **DONE** — listing surfaced
- **DONE_WITH_CONCERNS** — listing surfaced, one or more packs failed validation (only when --validate)
- **BLOCKED** — neither home nor repo packs dir exists (shouldn't happen since _default ships)

## Pause-points

None — pack-list is single-shot read-only.

## Hop-in support

None.

## Integration

**Reads:**
- `~/.lintel/packs/<name>/pack.yaml` for every pack
- `<repo>/packs/<name>/pack.yaml` for every pack
- `~/.lintel/packs/active-pack`
- Optionally `lib/pack-resolver.sh` (--validate mode)

**Writes:**
- stdout only — no state mutation

## Anti-patterns

- **Hardcoding pack list** — always re-discover (operators add packs frequently)
- **Hiding home-packs** — both scopes count; surface both
- **Suppressing pack collisions** — if `~/.lintel/packs/foo` AND `<repo>/packs/foo` both exist, flag it (home wins per resolver order)
