#!/usr/bin/env bash
# lib/pack-resolver.sh — Lintel PackResolver (v4.0 Phase 1)
# component: pack-resolver
# implements: ADR-0018
# intent: docs/concepts/pack-resolver.md
# constraints: none; parses local pack data without executing manifest values
# last_intent_review: 2026-09-08
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
# - Cached value immutable for current cycle (mid-cycle pack-switch deferred);
#   exception: a pack.yaml whose mtime is NEWER than the cache re-resolves —
#   manifest edits must not be invisible until a manual clear_pack_cache
#
# Usage (sourced by skills):
#   source "$(dirname "$0")/../../lib/pack-resolver.sh"
#   voice_tier=$(resolve_pack_field voice.default_tier)
#   compliance_mode=$(resolve_pack_field compliance.mode)
#   workflow=$(resolve_pack_field navigation.default_workflow)
#
# NOTE: no `set -uo pipefail` here — this file is SOURCED; setting shell options
# in a sourced library leaks them into every caller (skills, hooks, tests).
# Positional params are hardened with ${1:-} instead.

LINTEL_HOME="${LINTEL_HOME:-$HOME/.lintel}"
LINTEL_SOURCE_ROOT="${LINTEL_SOURCE_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." 2>/dev/null && pwd)}"
LINTEL_REPO_ROOT="${LINTEL_REPO_ROOT:-$LINTEL_SOURCE_ROOT}"
LINTEL_PACKS_DIR="${LINTEL_PACKS_DIR:-$LINTEL_HOME/packs}"
LINTEL_ACTIVE_PACK_FILE="${LINTEL_ACTIVE_PACK_FILE:-$LINTEL_PACKS_DIR/active-pack}"
LINTEL_AUDIT_DIR="${LINTEL_AUDIT_DIR:-$LINTEL_HOME/audit}"

# Per-session cache (lives at ~/.lintel/sessions/<id>-pack-cache.yaml).
# Key precedence: explicit LINTEL_SESSION_ID (the documented test seam — must
# out-rank ambient CLI env or sandboxed tests break) > the CLI's session id >
# PPID-$$. Bare PPID was a CONSTANT on platforms where every tool call spawns
# from PID 1 → one permanent shared cache, pack.yaml edits invisible.
LINTEL_SESSION_ID="${LINTEL_SESSION_ID:-${CLAUDE_SESSION_ID:-${PPID:-1}-$$}}"
PACK_CACHE_FILE="${LINTEL_HOME}/sessions/${LINTEL_SESSION_ID}-pack-cache.yaml"

mkdir -p "$LINTEL_AUDIT_DIR" "${LINTEL_HOME}/sessions" 2>/dev/null || true

# Unified audit writer (resolved via repo-root). Idempotent source.
command -v audit_log >/dev/null 2>&1 || source "${LINTEL_SOURCE_ROOT}/bin/_audit.sh"

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

# Resolve a pack directory: configured packs, working repository, bundled source.
_pack_dir() {
  local name="${1:-}"
  [[ "$name" =~ ^[A-Za-z_][A-Za-z_0-9-]*$ ]] || return 1
  local home_path="$LINTEL_PACKS_DIR/$name"
  local repo_path="$LINTEL_REPO_ROOT/packs/$name"
  local source_path="$LINTEL_SOURCE_ROOT/packs/$name"
  if [ -d "$home_path" ]; then
    printf '%s' "$home_path"
  elif [ -d "$repo_path" ]; then
    printf '%s' "$repo_path"
  elif [ -d "$source_path" ]; then
    printf '%s' "$source_path"
  else
    return 1
  fi
}

# One data-only extractor for runtime reads, validation and target previews.
# Supported manifest syntax: indented mappings, flow mappings, scalar lists in
# block/flow form, and plain/single/double-quoted scalar values. Mapping keys are
# plain identifiers; root mappings start in column one. Lists retain the existing
# [a, b] accessor contract. Absent field => 1; unsupported/malformed syntax => 2.
# Anchors, tags and multiline scalars are intentionally outside this contract.
_pack_yaml_field() {
  local manifest="${1:-}" field="${2:-}"
  [ -f "$manifest" ] || return 1
  [[ "$field" =~ ^[A-Za-z_][A-Za-z_0-9-]*(\.[A-Za-z_][A-Za-z_0-9-]*)*$ ]] || return 2
  awk -v wanted="$field" '
    function trim(s) { gsub(/^[[:space:]]+|[[:space:]]+$/, "", s); return s }
    # Find a delimiter outside quoted strings and nested flow collections.
    function delimiter(s, sep, i,c,q,depth,escaped) {
      q=""; depth=0; escaped=0
      for (i=1; i<=length(s); i++) {
        c=substr(s,i,1)
        if (q!="") {
          if (escaped) { escaped=0; continue }
          if (q=="\"" && c=="\\") { escaped=1; continue }
          if (c==q) {
            if (q==sprintf("%c",39) && substr(s,i+1,1)==q) { i++; continue }
            q=""
          }
          continue
        }
        if ((c=="\"" || c==sprintf("%c",39)) && (i==1 || substr(s,i-1,1) ~ /[[:space:]:,\[{]/)) { q=c; continue }
        if (c==sep && depth==0 && (sep!="#" || i==1 || substr(s,i-1,1) ~ /[[:space:]]/)) return i
        if (c=="[" || c=="{") depth++
        if (c=="]" || c=="}") depth--
        if (depth<0) bad=1
      }
      if (q!="" || depth!=0) bad=1
      return 0
    }
    function scalar(s, q,i,c,out) {
      s=trim(s); q=substr(s,1,1)
      if (q=="\"" || q==sprintf("%c",39)) {
        if (substr(s,length(s),1)!=q || length(s)<2) { bad=1; return "" }
        s=substr(s,2,length(s)-2)
        if (q==sprintf("%c",39)) gsub(/\047\047/, "\047", s)
        else {
          out=""
          for (i=1; i<=length(s); i++) {
            c=substr(s,i,1)
            if (c=="\\") {
              c=substr(s,++i,1)
              if (c=="n") c="\n"
              else if (c=="r") c="\r"
              else if (c=="t") c="\t"
              else if (c!="\\" && c!="\"") bad=1
            }
            out=out c
          }
          s=out
        }
      } else if (s ~ /^[&*!|>]/) bad=1
      return s
    }
    function list(s, out,pos,item) {
      out=""
      while (length(s)) {
        pos=delimiter(s,",")
        item=trim(pos ? substr(s,1,pos-1) : s)
        if (item ~ /^[\[{]/) bad=1
        out=out (out!="" ? ", " : "") scalar(item)
        if (!pos) break
        s=trim(substr(s,pos+1))
      }
      return "[" out "]"
    }
    function value(path,s, inner,pos,part,colon,key) {
      s=trim(s)
      if (seen[path]++) bad=1
      if (path==wanted) { found=1; result=scalar(s) }
      if (substr(s,1,1)=="{") {
        if (substr(s,length(s),1)!="}") { bad=1; return }
        inner=trim(substr(s,2,length(s)-2))
        while (length(inner)) {
          pos=delimiter(inner,",")
          part=trim(pos ? substr(inner,1,pos-1) : inner)
          colon=delimiter(part,":")
          if (!colon) { bad=1; return }
          key=trim(substr(part,1,colon-1))
          if (key !~ /^[A-Za-z_][A-Za-z_0-9-]*$/) { bad=1; return }
          value(path "." key,substr(part,colon+1))
          if (!pos) break
          inner=trim(substr(inner,pos+1))
        }
      } else if (substr(s,1,1)=="[") {
        if (substr(s,length(s),1)!="]") { bad=1; return }
        inner=list(trim(substr(s,2,length(s)-2)))
        if (path==wanted) result=inner
      } else scalar(s)
    }
    {
      sub(/\r$/, "")
      if ($0 ~ /^[ ]*\t/) { bad=1; next }
      line=$0
      # A YAML comment starts with # only outside quotes, after whitespace.
      comment=delimiter(line,"#")
      if (comment && (comment==1 || substr(line,comment-1,1) ~ /[[:space:]]/)) line=substr(line,1,comment-1)
      if (trim(line)=="" || trim(line)=="---" || trim(line)=="...") next
      indent=match(line,/[^ ]/)-1; line=trim(line)
      # YAML permits a block sequence at the same indentation as its field.
      # Keep that pending field as owner for sequence items; sibling mappings
      # still close it. Losing the owner would silently erase required gates.
      is_item=(line ~ /^-[[:space:]]/)
      while (depth>0 && (indent<indents[depth] || (indent==indents[depth] && !is_item))) depth--
      if (line ~ /^-[[:space:]]/) {
        if (!depth) { bad=1; next }
        if (collection[paths[depth]]=="mapping") bad=1
        collection[paths[depth]]="sequence"
        if (trim(substr(line,3)) ~ /^[\[{]|^[A-Za-z_][A-Za-z_0-9-]*:[[:space:]]/) bad=1
        item=scalar(substr(line,3))
        if (paths[depth]==wanted) {
          result=(count++ ? substr(result,1,length(result)-1) ", " : "[") item "]"
          found=1
        }
        next
      }
      colon=delimiter(line,":")
      if (!colon) { bad=1; next }
      key=trim(substr(line,1,colon-1))
      if (key !~ /^[A-Za-z_][A-Za-z_0-9-]*$/) { bad=1; next }
      if (!depth && indent!=0) { bad=1; next }
      if (depth) {
        if (collection[paths[depth]]=="sequence") bad=1
        collection[paths[depth]]="mapping"
      }
      path=(depth ? paths[depth] "." : "") key
      val=trim(substr(line,colon+1))
      value(path,val)
      if (val=="") { depth++; indents[depth]=indent; paths[depth]=path }
    }
    END { if (bad) exit 2; if (!found) exit 1; printf "%s", result }
  ' "$manifest"
}

_pack_ext_field() { _pack_yaml_field "${1:-}" "extension.${2:-}"; }

# A child owns an entire top-level block. Resolve that owner before looking up a
# nested field; this preserves whole-block replacement during pre-cache validation.
_pack_chain_field() {
  local chain="$1" field="$2" name dir owner="" top="${2%%.*}" rc
  for name in $chain; do
    dir=$(_pack_dir "$name") || return 1
    rc=0; _pack_yaml_field "$dir/pack.yaml" "$top" >/dev/null || rc=$?
    [ "$rc" -eq 2 ] && return 2
    [ "$rc" -eq 0 ] && owner="$dir/pack.yaml"
  done
  [ -n "$owner" ] || return 1
  _pack_yaml_field "$owner" "$field"
}

# ─── Pack validation (called at SENSE Step 1) ──────────────────────────────
validate_pack() {
  local name="${1:-_default}" chain pack dir field v
  chain=$(_resolve_extends_chain "$name") || return 1
  # Identity belongs to each manifest; policy blocks may be inherited. Validate
  # effective blocks, so a minimal team overlay retains its enterprise base.
  for pack in $chain; do
    dir=$(_pack_dir "$pack") || return 1
    for field in name version; do
      v=$(_pack_yaml_field "$dir/pack.yaml" "$field") || {
        _resolver_fail "pack=$pack missing or unsupported field: $field"; return 1;
      }
      if [ -z "$v" ] || [ "$v" = null ] || [ "$v" = '~' ] || [[ "$v" = \[* || "$v" = \{* ]]; then
        _resolver_fail "pack=$pack required field is empty: $field"; return 1
      fi
    done
  done
  for field in voice.default_tier compliance.mode navigation.default_workflow; do
    v=$(_pack_chain_field "$chain" "$field") || {
      _resolver_fail "pack=$name missing or unsupported required field: $field"; return 1;
    }
    if [ -z "$v" ] || [ "$v" = null ] || [ "$v" = '~' ] || [[ "$v" = \[* || "$v" = \{* ]]; then
      _resolver_fail "pack=$name required scalar is empty or invalid: $field"; return 1
    fi
    if [ "$field" = compliance.mode ]; then
      case "$v" in hard|advisory|off) ;; *)
        _resolver_fail "pack=$name unsupported compliance.mode: $v"; return 1 ;;
      esac
    fi
  done
  v=$(_pack_chain_field "$chain" extension.is_extension) || v=""
  case "$v" in true|yes|on)
    for field in extension.namespace extension.workflow; do
      v=$(_pack_chain_field "$chain" "$field") || v=""
      if [ -z "$v" ] || [ "$v" = null ] || [ "$v" = '~' ] || [[ "$v" = \[* || "$v" = \{* ]]; then
        _resolver_fail "extension pack=$name: $field is unset (required, ADR-0018)"
        return 1
      fi
    done
  ;; esac
  return 0
}

# Root-to-leaf ancestry. Validate every link, including a missing terminal parent
# and chains exceeding the documented ten-parent limit. No partial chain loads.
_resolve_extends_chain() {
  local name="${1:-}" chain="${1:-}" current="${1:-}" visited=":${1:-}:"
  local depth=0 dir ext rc
  while :; do
    dir=$(_pack_dir "$current") || {
      _resolver_fail "pack=$name parent or pack not found: $current"; return 1;
    }
    [ -f "$dir/pack.yaml" ] || {
      _resolver_fail "pack.yaml missing for pack=$current"; return 1;
    }
    rc=0; ext=$(_pack_yaml_field "$dir/pack.yaml" extends) || rc=$?
    if [ "$rc" -eq 2 ]; then
      _resolver_fail "pack=$current has unsupported or malformed manifest syntax"; return 1
    fi
    [ -z "$ext" ] || [ "$ext" = null ] || [ "$ext" = '~' ] || {
      case "$visited" in *:"$ext":*)
        _resolver_fail "pack=$name extends: cycle detected at $ext"; return 1 ;;
      esac
      if [ "$depth" -ge 10 ]; then
        _resolver_fail "pack=$name extends: exceeds maximum depth 10"; return 1
      fi
      visited="$visited$ext:"; chain="$ext $chain"; current="$ext"
      depth=$((depth + 1))
      continue
    }
    break
  done
  printf '%s' "$chain"
}

# Merge an extends-chain into the session cache. Top-level keys from later
# packs in the chain override earlier ones (child overrides parent).
# Per design doc §1.3: nested blocks REPLACE wholesale, not deep-merge.
_merge_packs_into_cache() {
  local chain="${1:-}"  # space-separated, root → leaf
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
    keys=$(grep -E '^[A-Za-z_][A-Za-z_0-9-]*[[:space:]]*:' "$manifest" | awk -F: '{sub(/[[:space:]]+$/, "", $1); print $1}' | sort -u)

    # For each key in this manifest, remove the corresponding block from $out
    for key in $keys; do
      [ -z "$key" ] && continue
      awk -v key="$key" '
        BEGIN { skip=0 }
        $0 ~ "^"key"[[:space:]]*:" { skip=1; next }
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
    # mtime invalidation: a pack.yaml edited AFTER the cache was primed must not
    # stay invisible until a manual clear_pack_cache. The active-pack POINTER is
    # deliberately not checked — mid-session pack-switch keeps the cached value
    # per the §2.4 contract (fallback-harness scenario 7); a deleted pack keeps
    # the cache too (scenario 8: _pack_dir fails → manifest not checked).
    local _name _p _pd _chain _stale=0 _reason=manifest-newer-than-cache
    _name=$(get_active_pack_name)
    if _pack_dir "$_name" >/dev/null 2>&1; then
      if _chain=$(_resolve_extends_chain "$_name"); then
        for _p in $_chain; do
          _pd=$(_pack_dir "$_p" 2>/dev/null) || continue
          [ "$_pd/pack.yaml" -nt "$PACK_CACHE_FILE" ] && _stale=1
        done
      else
        # A rejected edited manifest/ancestor is not proof of cache freshness.
        # A different active pointer still takes effect at the next cycle.
        if [ "$_name" = "$(_pack_yaml_field "$PACK_CACHE_FILE" name)" ]; then
          _stale=1; _reason=invalid-manifest-or-ancestry
        fi
      fi
    fi
    if [ "$_stale" = 0 ]; then
      return 0  # already primed and fresh
    fi
    _resolver_audit cache_invalidated "pack=$_name reason=$_reason session=$LINTEL_SESSION_ID"
    rm -f "$PACK_CACHE_FILE" 2>/dev/null || true
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

  local value rc default_dir
  rc=0; value=$(_pack_yaml_field "$PACK_CACHE_FILE" "$path") || rc=$?
  if [ "$rc" -eq 0 ]; then
    printf '%s' "$value"
    return 0
  fi
  if [ "$rc" -eq 2 ]; then
    _resolver_fail "unsupported manifest syntax or field path: $path"
    return 1
  fi
  # Missing fields use the neutral manifest; explicit null/false/[] stay explicit.
  # This is a field fallback, not deep inheritance from a parent block.
  default_dir=$(_pack_dir _default) || return 1
  rc=0; value=$(_pack_yaml_field "$default_dir/pack.yaml" "$path") || rc=$?
  [ "$rc" -eq 2 ] && return 1
  printf '%s' "$value"
}

# Boolean helper: returns 0 (true) if resolved value is "true", else 1
pack_field_is_true() {
  local v
  v=$(resolve_pack_field "${1:-}")
  [ "$v" = "true" ] || [ "$v" = "yes" ] || [ "$v" = "on" ]
}

# ─── Extension-pack awareness (ADR-0018) ───────────────────────────────────
# An extension pack ships its own skills/agents/hooks (as a plugin) + a workflow.
# These helpers let identity-aware skills (pack-switch, orientator, doctor) treat
# such a pack as more than identity, without re-implementing plugin discovery.
pack_is_extension() { pack_field_is_true extension.is_extension; }   # 0/true if active pack ships surface
# namespace/workflow: normalize the literal YAML `null` (identity-pack default) to ""
# so callers can use `[ -z "$(pack_namespace)" ]` to gate extension behavior.
pack_namespace() { local v; v=$(resolve_pack_field extension.namespace); [ "$v" = "null" ] && v=""; printf '%s' "$v"; }  # e.g. "s4l"; "" for identity packs
pack_workflow()  { local v; v=$(resolve_pack_field extension.workflow);  [ "$v" = "null" ] && v=""; printf '%s' "$v"; }  # e.g. "s4l-forge"; "" otherwise

# List the loaded pack name (operator visibility)
get_loaded_pack() {
  _prime_cache_for_session 2>/dev/null || true
  if [ -f "$PACK_CACHE_FILE" ]; then
    _pack_yaml_field "$PACK_CACHE_FILE" name
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
  echo "  extension.is_extension = $(resolve_pack_field extension.is_extension)"
  echo "  pack_is_extension = $(pack_is_extension && echo yes || echo no)"
  echo "  pack_namespace = $(pack_namespace)"
fi
