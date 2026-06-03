#!/usr/bin/env bash
# lib/pack-resolver.sh — Lintel PackResolver (v4.0 Phase 1)
#
# Critical-path interface used by 30+ skills. Reads identity-bound state
# from the active pack with explicit failure semantics + per-session cache.
#
# Per v4.0 design doc §2.4:
# - Parse pack.yaml once at SENSE Step 1 (cached for cycle lifetime)
# - Hard-fail SENSE on parse-error
# - Refuse activation on extends: cycle
# - Reject load on missing required field
# - Fall back to _default on internal bug + warn
# - Cached value immutable for current cycle (mid-cycle pack-switch deferred)
#
# Usage (sourced by skills):
#   source "$(dirname "$0")/../../lib/pack-resolver.sh"
#   voice_tier=$(resolve_pack_field voice.default_tier)
#   compliance_mode=$(resolve_pack_field compliance.mode)
#   workflow=$(resolve_pack_field navigation.default_workflow)

set -uo pipefail

LINTEL_HOME="${LINTEL_HOME:-$HOME/.lintel}"
LINTEL_REPO_ROOT="${LINTEL_REPO_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." 2>/dev/null && pwd)}"
LINTEL_PACKS_DIR="${LINTEL_PACKS_DIR:-$LINTEL_HOME/packs}"
LINTEL_ACTIVE_PACK_FILE="${LINTEL_ACTIVE_PACK_FILE:-$LINTEL_PACKS_DIR/active-pack}"
LINTEL_AUDIT_DIR="${LINTEL_AUDIT_DIR:-$LINTEL_HOME/audit}"

# Per-session cache (lives at ~/.lintel/sessions/<id>-pack-cache.yaml)
LINTEL_SESSION_ID="${LINTEL_SESSION_ID:-${PPID:-$$}}"
PACK_CACHE_FILE="${LINTEL_HOME}/sessions/${LINTEL_SESSION_ID}-pack-cache.yaml"

mkdir -p "$LINTEL_AUDIT_DIR" "${LINTEL_HOME}/sessions" 2>/dev/null || true

# Unified audit writer (resolved via repo-root). Idempotent source.
command -v audit_log >/dev/null 2>&1 || source "${LINTEL_REPO_ROOT}/bin/_audit.sh"

# ─── Internal logging ──────────────────────────────────────────────────────
_resolver_audit() {
  local kind msg
  kind="${1:-info}"
  msg="${2:-}"
  audit_log "pack-resolver" "pack_resolver_${kind}" "msg=$msg"
}

_resolver_warn() {
  echo "[lintel/pack-resolver] WARN: $1" >&2
  _resolver_audit warn "$1"
}

_resolver_fail() {
  echo "[lintel/pack-resolver] FAIL: $1" >&2
  _resolver_audit fail "$1"
}

# ─── Active pack discovery ─────────────────────────────────────────────────
get_active_pack_name() {
  # Reads ~/.lintel/packs/active-pack (single-line file)
  if [ -f "$LINTEL_ACTIVE_PACK_FILE" ]; then
    local name
    name=$(head -1 "$LINTEL_ACTIVE_PACK_FILE" 2>/dev/null | tr -d '[:space:]')
    if [ -n "$name" ]; then
      printf '%s' "$name"
      return 0
    fi
  fi
  printf '_default'
  return 0
}

# Resolve a pack's directory — checks ~/.lintel/packs/<name>/ first, then repo packs/<name>/
_pack_dir() {
  local name="$1"
  local home_path="$LINTEL_PACKS_DIR/$name"
  local repo_path="$LINTEL_REPO_ROOT/packs/$name"
  if [ -d "$home_path" ]; then
    printf '%s' "$home_path"
  elif [ -d "$repo_path" ]; then
    printf '%s' "$repo_path"
  else
    return 1
  fi
}

# ─── Pack validation (called at SENSE Step 1) ──────────────────────────────
validate_pack() {
  # Args: <pack-name>
  # Returns: 0 if valid; 1 if reject (with audit + stderr message)
  local name="${1:-_default}"
  local pack_dir
  pack_dir=$(_pack_dir "$name") || { _resolver_fail "pack not found: $name"; return 1; }
  local manifest="$pack_dir/pack.yaml"

  # Failure mode 1: file missing
  if [ ! -f "$manifest" ]; then
    _resolver_fail "pack.yaml missing for pack=$name (looked at $manifest)"
    return 1
  fi

  # Failure mode 2: required fields absent
  for required in "^name:" "^version:" "^voice:" "^compliance:" "^navigation:"; do
    if ! grep -qE "$required" "$manifest"; then
      _resolver_fail "pack=$name missing required top-level: ${required#^}"
      return 1
    fi
  done

  # Failure mode 3: extends: cycle (depth-limited shallow check)
  local visited=":$name:"
  local current="$name"
  local depth=0
  while [ "$depth" -lt 10 ]; do
    local pack_dir_cur
    pack_dir_cur=$(_pack_dir "$current") || break
    local ext
    ext=$(grep -E '^extends:' "$pack_dir_cur/pack.yaml" 2>/dev/null | head -1 | awk '{print $2}')
    [ -z "$ext" ] && break
    case "$visited" in
      *:"$ext":*)
        _resolver_fail "pack=$name extends: cycle detected at $ext (chain: ${visited//:/, })"
        return 1
        ;;
    esac
    visited="${visited}${ext}:"
    current="$ext"
    depth=$((depth + 1))
  done

  return 0
}

# ─── Inheritance chain resolution (extends: walk) ──────────────────────────
# Returns space-separated chain ordered root → leaf, e.g. "ms-internal caip-se".
# Does NOT auto-prepend _default — _default is the resolver's fallback layer
# for missing fields, not an explicit extends target.
_resolve_extends_chain() {
  local name="$1"
  local chain="$name"
  local current="$name"
  local depth=0
  while [ "$depth" -lt 10 ]; do
    local pack_dir
    pack_dir=$(_pack_dir "$current") || break
    local ext
    ext=$(grep -E '^extends:' "$pack_dir/pack.yaml" 2>/dev/null | head -1 | awk '{print $2}')
    [ -z "$ext" ] && break
    # Prepend parent (walk leaf → root, reverse implicit through prepend)
    chain="$ext $chain"
    current="$ext"
    depth=$((depth + 1))
  done
  printf '%s' "$chain"
}

# Merge an extends-chain into the session cache. Top-level keys from later
# packs in the chain override earlier ones (child overrides parent).
# Per design doc §1.3: nested blocks REPLACE wholesale, not deep-merge.
_merge_packs_into_cache() {
  local chain="$1"      # space-separated, root → leaf
  local out="$PACK_CACHE_FILE"
  : > "$out"

  # Each top-level key gets the LAST occurrence in the chain.
  # Strategy: collect all manifests, then for each top-level key the child's
  # version replaces the parent's. We process in order root → leaf, and for
  # each manifest we overwrite the same top-level keys in $out.

  for name in $chain; do
    local pack_dir
    pack_dir=$(_pack_dir "$name") 2>/dev/null || continue
    local manifest="$pack_dir/pack.yaml"
    [ -f "$manifest" ] || continue

    # Extract this manifest's top-level keys
    local keys
    keys=$(grep -E '^[A-Za-z_][A-Za-z_0-9]*:' "$manifest" | awk -F: '{print $1}' | sort -u)

    # For each key in this manifest, remove the corresponding block from $out
    for key in $keys; do
      [ -z "$key" ] && continue
      awk -v key="$key" '
        BEGIN { skip=0 }
        $0 ~ "^"key":" { skip=1; next }
        skip && /^[A-Za-z_]/ { skip=0 }
        !skip { print }
      ' "$out" > "$out.tmp2" 2>/dev/null && mv "$out.tmp2" "$out"
    done

    # Append this manifest's content to $out (skipping comments/blanks for clean cache)
    cat "$manifest" >> "$out"
    printf '\n' >> "$out"
  done
}

# ─── Cache management ──────────────────────────────────────────────────────
_prime_cache_for_session() {
  # Reads active pack, validates, copies merged manifest to cache.
  # Run once per session. Subsequent resolve_pack_field calls hit cache.
  if [ -f "$PACK_CACHE_FILE" ]; then
    return 0  # already primed
  fi

  local name
  name=$(get_active_pack_name)

  if ! validate_pack "$name"; then
    # Failure mode 4: internal bug or invalid active pack → fall back to _default
    _resolver_warn "active pack '$name' invalid; falling back to _default"
    name="_default"
    if ! validate_pack "$name"; then
      _resolver_fail "_default pack ALSO invalid — repo is broken"
      return 1
    fi
  fi

  # Resolve extends: chain (parent → child order)
  local chain
  chain=$(_resolve_extends_chain "$name")

  # Count chain length (whitespace-separated tokens)
  local chain_count
  # shellcheck disable=SC2086
  chain_count=$(printf '%s' "$chain" | awk '{print NF}')

  if [ "${chain_count:-1}" -le 1 ]; then
    # No inheritance — single pack, simple copy
    local pack_dir
    pack_dir=$(_pack_dir "$name")
    cp "$pack_dir/pack.yaml" "$PACK_CACHE_FILE" 2>/dev/null || {
      _resolver_fail "could not cache pack.yaml to $PACK_CACHE_FILE"
      return 1
    }
  else
    # Inheritance — merge chain into cache
    _merge_packs_into_cache "$chain" || {
      _resolver_fail "merge of extends chain '$chain' failed"
      return 1
    }
  fi

  _resolver_audit cache_primed "pack=$name chain=$chain session=$LINTEL_SESSION_ID"
  return 0
}

# ─── Field resolver ────────────────────────────────────────────────────────
# Reads a dotted-path field from cached pack.yaml.
# Usage: resolve_pack_field voice.default_tier  → "internal"
#        resolve_pack_field compliance.mode     → "advisory"
resolve_pack_field() {
  local path="${1:-}"
  [ -z "$path" ] && return 1

  _prime_cache_for_session || {
    # Last-resort fallback: hardcoded neutral defaults
    case "$path" in
      voice.default_tier) printf 'internal' ;;
      compliance.mode) printf 'advisory' ;;
      compliance.workprofile_default) printf 'off' ;;
      navigation.default_workflow) printf 'cycle' ;;
      navigation.orientator_budget_tokens) printf '2000' ;;
      navigation.orientator_max_output_tokens) printf '200' ;;
      navigation.escalation_threshold) printf 'medium' ;;
      brief_forge_handoffs.budget_tokens) printf '5000' ;;
      *) printf '' ;;
    esac
    return 0
  }

  # Walk dotted path through YAML using awk
  local parent="${path%.*}"
  local key="${path##*.}"

  # Simple two-level resolver (parent.key)
  if [ "$parent" = "$path" ]; then
    # Top-level scalar
    grep -E "^${key}:" "$PACK_CACHE_FILE" | head -1 | awk -F': *' '{print $2}' | tr -d '[:space:]'
  else
    # Nested: handle both block form and inline-flow form
    #   block:        parent:\n  key: value
    #   flow inline:  parent: {key: value, key2: value2}
    awk -v parent="$parent" -v key="$key" '
      BEGIN { in_parent=0 }
      # Inline flow form on single line
      $0 ~ "^"parent":[[:space:]]*\\{" {
        line = $0
        sub("^"parent":[[:space:]]*\\{[[:space:]]*", "", line)
        sub("[[:space:]]*\\}[[:space:]]*$", "", line)
        sub("[[:space:]]*#.*$", "", line)
        n = split(line, pairs, ",")
        for (i = 1; i <= n; i++) {
          gsub(/^[[:space:]]+|[[:space:]]+$/, "", pairs[i])
          pos = index(pairs[i], ":")
          if (pos > 0) {
            k = substr(pairs[i], 1, pos - 1)
            v = substr(pairs[i], pos + 1)
            gsub(/^[[:space:]]+|[[:space:]]+$/, "", k)
            gsub(/^[[:space:]]+|[[:space:]]+$/, "", v)
            if (k == key) { print v; exit }
          }
        }
        next
      }
      # Block form: parent: on its own (no opening brace)
      /^[A-Za-z_]/ {
        if ($0 ~ "^"parent":[[:space:]]*$") { in_parent=1; next }
        if (in_parent) in_parent=0
      }
      in_parent && $0 ~ "^[[:space:]]+"key":" {
        sub("^[[:space:]]+"key":[[:space:]]*", "")
        sub("[[:space:]]*#.*$", "")    # strip trailing comments
        gsub(/^[[:space:]]+|[[:space:]]+$/, "")
        print
        exit
      }
    ' "$PACK_CACHE_FILE"
  fi
}

# Boolean helper: returns 0 (true) if resolved value is "true", else 1
pack_field_is_true() {
  local v
  v=$(resolve_pack_field "$1")
  [ "$v" = "true" ] || [ "$v" = "yes" ] || [ "$v" = "on" ]
}

# List the loaded pack name (operator visibility)
get_loaded_pack() {
  _prime_cache_for_session 2>/dev/null || true
  if [ -f "$PACK_CACHE_FILE" ]; then
    grep -E '^name:' "$PACK_CACHE_FILE" | head -1 | awk '{print $2}'
  else
    printf '_default'
  fi
}

# Clear cache (mid-session pack-switch → cache discarded for NEXT cycle, not this one)
clear_pack_cache() {
  rm -f "$PACK_CACHE_FILE" 2>/dev/null || true
  _resolver_audit cache_cleared "session=$LINTEL_SESSION_ID"
}

# ─── Self-test mode ────────────────────────────────────────────────────────
if [ "${BASH_SOURCE[0]}" = "$0" ]; then
  echo "pack-resolver.sh self-test:"
  echo "  LINTEL_REPO_ROOT = $LINTEL_REPO_ROOT"
  echo "  LINTEL_PACKS_DIR = $LINTEL_PACKS_DIR"
  echo "  Active pack: $(get_active_pack_name)"
  echo "  Loaded pack: $(get_loaded_pack)"
  echo "  voice.default_tier = $(resolve_pack_field voice.default_tier)"
  echo "  compliance.mode = $(resolve_pack_field compliance.mode)"
  echo "  navigation.default_workflow = $(resolve_pack_field navigation.default_workflow)"
  echo "  brief_forge_handoffs.budget_tokens = $(resolve_pack_field brief_forge_handoffs.budget_tokens)"
fi
