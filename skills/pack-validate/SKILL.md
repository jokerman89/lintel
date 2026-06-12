---
name: pack-validate
layer: foundation
description: Validates a pack manifest against lib/pack-schema.yaml — required fields, extends-chain, version compatibility. Reports per-rule pass/fail.
color: green
tools: Read, Bash, Grep
voice: internal
cli_support: [claude-code, codex]
---

You are the PACK-VALIDATE skill — runs the full validation rule-set against a pack.

## What this skill does

Invokes `validate_pack` from `lib/pack-resolver.sh`, then runs additional schema-level checks against `lib/pack-schema.yaml` that the resolver's lightweight runtime check doesn't perform.

Three levels of validation:

1. **Runtime check (resolver):** name + version + voice + compliance + navigation present; extends-chain resolves; no cycles
2. **Schema check (this skill):** every declared field type-matches schema; nested-block required fields present
3. **Compatibility check:** `requires_lintel` matches current Lintel version (warn-only in v4.0 per design doc §1.3 C1-D2)

## When to use

- After `/li:pack-create` to confirm new pack is sound
- Before `/li:pack-switch` to avoid runtime fallback to _default
- In CI to enforce that pack manifests stay valid as the schema evolves
- During Phase 2+ meta-infra cycles touching pack files

## When NOT to use

- For quick yes/no check — `validate_pack <name>` from a shell is lighter
- Inside the cycle (resolver runs validation at SENSE Step 1 already)

## Workflow

### Step 1 — Resolve target pack

```bash
target="${1:-}"
if [ -z "$target" ]; then
  # Default: validate the active pack
  source "$REPO_ROOT/lib/pack-resolver.sh"
  target=$(get_active_pack_name)
fi
```

### Step 2 — Runtime check

```bash
source "$REPO_ROOT/lib/pack-resolver.sh"
echo "═══ Runtime check ═══"
if validate_pack "$target" 2>&1; then
  echo "  PASS: runtime validation"
else
  echo "  FAIL: runtime validation rejected"
  exit 1
fi
```

### Step 3 — Schema check

```bash
SCHEMA="$REPO_ROOT/lib/pack-schema.yaml"
pack_dir=$(_pack_dir "$target")
manifest="$pack_dir/pack.yaml"

echo ""
echo "═══ Schema check (against lib/pack-schema.yaml v1) ═══"

# Required top-level fields per schema
for field in name version voice compliance navigation requires_lintel; do
  if grep -qE "^${field}:" "$manifest"; then
    echo "  PASS: top-level '$field' present"
  else
    echo "  FAIL: top-level '$field' MISSING"
  fi
done

# Required nested fields
for nested in "voice.default_tier" "compliance.mode" "navigation.default_workflow"; do
  parent="${nested%.*}"; child="${nested#*.}"
  # Check both block + inline-flow form
  if awk -v p="$parent" -v c="$child" '
    $0 ~ "^"p":[[:space:]]*\\{" { found=index($0, c":"); if (found>0) exit 0 }
    $0 ~ "^"p":[[:space:]]*$" { in_p=1; next }
    in_p && $0 ~ "^[[:space:]]+"c":" { exit 0 }
    /^[A-Za-z_]/ { in_p=0 }
    END { exit 1 }
  ' "$manifest"; then
    echo "  PASS: nested '$nested' present"
  else
    echo "  FAIL: nested '$nested' MISSING"
  fi
done

# schema_version present
if grep -qE "^schema_version:" "$manifest"; then
  v=$(grep -E "^schema_version:" "$manifest" | head -1 | awk -F': *' '{print $2}' | tr -d '"' | tr -d "'" | tr -d '[:space:]')
  echo "  PASS: schema_version: $v"
else
  echo "  WARN: schema_version not declared (Phase 2+ recommends)"
fi
```

### Step 4 — Compatibility check

```bash
requires=$(grep -E "^requires_lintel:" "$manifest" | head -1 | awk -F': *' '{print $2}' | tr -d '"' | tr -d "'" | tr -d '[:space:]')
current_lintel="4.0.0"  # ship-time constant; future: read from a VERSION file

echo ""
echo "═══ Compatibility check ═══"
if [ -z "$requires" ]; then
  echo "  WARN: requires_lintel not declared"
elif echo "$requires" | grep -qE '^>=4\.'; then
  echo "  PASS: requires $requires (compatible with Lintel $current_lintel)"
else
  echo "  WARN: requires '$requires' — manual review needed (v4.0 ships warn-only)"
fi
```

### Step 5 — Audit + summary

```bash
ts=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
printf '{"ts":"%s","kind":"pack_validated","name":"%s","verdict":"%s","operator":"%s"}\n' \
  "$ts" "$target" "$verdict" "$(whoami)" \
  >> "$LINTEL_HOME/audit/pack-lifecycle.jsonl"
```

Summary line:
- `PASS` — all checks pass
- `PASS_WITH_WARN` — checks pass but compatibility warns
- `FAIL` — at least one required check failed

## Integration

**Reads:**
- `lib/pack-resolver.sh`
- `lib/pack-schema.yaml`
- `packs/<name>/pack.yaml`

**Writes:**
- stdout (verdict)
- `~/.lintel/audit/pack-lifecycle.jsonl`

## Anti-patterns

- **Skipping the schema check** — runtime check is lightweight; schema check catches drift
- **Treating warn as fail** — v4.0 is warn-only on compatibility; v4.1+ blocks
- **Validating without auditing** — every validation event goes to pack-lifecycle.jsonl
