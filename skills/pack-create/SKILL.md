---
name: pack-create
layer: foundation
description: Scaffolds a new Lintel pack — copies _default pack.yaml as starting point, optionally sets extends parent, validates result.
color: green
tools: Read, Write, Edit, Bash
voice: internal
cli_support: [claude-code, codex]
---

You are the PACK-CREATE skill — scaffolds a new pack in `<repo>/packs/<name>/` or `~/.lintel/packs/<name>/`.

## What this skill does

Creates a new pack directory + manifest. Three modes:

- **Blank pack:** starts from `packs/_default/pack.yaml` skeleton (every field declared with neutral value)
- **Extending pack:** starts from `packs/_default/pack.yaml` + sets `extends: <parent-name>` (validates parent exists)
- **Cloned pack:** copies an existing pack as a starting point (operator edits per their needs)

## When to use

- Operator wants a new pack for a fresh customer/team/domain
- Sister pack to an existing pack (extends: shared parent)
- Forking an existing pack for an isolated experiment

## When NOT to use

- Tweaking an existing pack — just edit `packs/<name>/pack.yaml` directly
- One-off override for a single workflow — use `--mode` on `/li:cycle` instead

## Workflow

### Step 1 — Resolve target location

```bash
LINTEL_HOME="${LINTEL_HOME:-$HOME/.lintel}"
REPO_PACKS="$(git rev-parse --show-toplevel 2>/dev/null)/packs"
HOME_PACKS="$LINTEL_HOME/packs"

# Operator chooses scope: repo (shared via git) or home (personal)
# Default: repo if invoked inside a git repo with packs/ dir; else home
```

If operator didn't specify `--scope repo|home`: ask once.

### Step 2 — Validate name + check existing

```bash
# Name must be kebab-case, filesystem-safe, not already taken
name="${1:?usage: /li:pack-create <name> [--extends <parent>]}"
echo "$name" | grep -qE '^[a-z][a-z0-9-]*$' || { echo "ERROR: name must be kebab-case"; exit 1; }
[ -d "$REPO_PACKS/$name" ] || [ -d "$HOME_PACKS/$name" ] && { echo "ERROR: pack '$name' already exists"; exit 1; }
```

### Step 3 — Resolve template

```bash
template="$REPO_PACKS/_default/pack.yaml"
[ -f "$template" ] || { echo "ERROR: _default pack missing"; exit 1; }
```

If `--from <existing-pack>`: use that pack's manifest as template instead.

### Step 4 — Validate parent (if --extends)

```bash
if [ -n "$extends" ]; then
  source "$REPO_ROOT/lib/pack-resolver.sh"
  if ! validate_pack "$extends" 2>/dev/null; then
    echo "ERROR: parent pack '$extends' does not exist or fails validation"
    exit 1
  fi
fi
```

### Step 5 — Write manifest

```bash
mkdir -p "$target_dir/$name"
cp "$template" "$target_dir/$name/pack.yaml"

# Replace name: line
sed -i.bak "s/^name: .*/name: $name/" "$target_dir/$name/pack.yaml"
rm -f "$target_dir/$name/pack.yaml.bak"

# Add extends: if requested
if [ -n "$extends" ]; then
  # Insert after `version:` line
  awk -v ext="$extends" '
    /^version:/ { print; print "extends: " ext; next }
    { print }
  ' "$target_dir/$name/pack.yaml" > "$target_dir/$name/pack.yaml.tmp"
  mv "$target_dir/$name/pack.yaml.tmp" "$target_dir/$name/pack.yaml"
fi
```

### Step 6 — Validate result

```bash
source "$REPO_ROOT/lib/pack-resolver.sh"
if validate_pack "$name" 2>&1; then
  echo "✓ Pack '$name' created at $target_dir/$name/"
else
  echo "WARN: pack created but validation failed — review pack.yaml"
fi
```

### Step 7 — Audit + surface next steps

```bash
ts=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
printf '{"ts":"%s","kind":"pack_created","name":"%s","extends":"%s","scope":"%s","operator":"%s"}\n' \
  "$ts" "$name" "${extends:-none}" "$scope" "$(whoami)" \
  >> "$LINTEL_HOME/audit/pack-lifecycle.jsonl"
```

Surface:
- Path to new pack
- "Activate with: `/li:pack-switch $name`"
- "List all packs: `/li:pack-list`"

## Status protocol

- **DONE** — pack created and validates
- **DONE_WITH_CONCERNS** — pack created but validation warned
- **BLOCKED** — name collision, invalid parent, or write-permission error
- **NEEDS_CONTEXT** — operator didn't specify scope and we're outside a repo

## Pause-points

- Step 1 if scope ambiguous: ask `repo` or `home`
- After Step 6 if validation fails: surface, ask to retry or abandon

## Hop-in support

None — pack-create is single-shot.

## Integration

**Reads:**
- `packs/_default/pack.yaml` (template)
- `lib/pack-resolver.sh` (validation)

**Writes:**
- `<scope>/packs/<name>/pack.yaml`
- `~/.lintel/audit/pack-lifecycle.jsonl`

**Triggers (recommends):**
- `/li:pack-switch <name>` to activate the new pack
- `/li:pack-list` to confirm

## Anti-patterns

- **Creating a pack to override one field** — edit `pack.yaml` of an existing pack instead
- **Not validating extends parent** — broken extends silently degrades to _default at runtime
- **Auto-activating after create** — operator decides when to switch (avoids surprise behavior changes mid-session)
