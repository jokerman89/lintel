#!/usr/bin/env bash
# component: pack-resolver
# implements: ADR-0018, ADR-0029
# intent: docs/concepts/pack-resolver.md
# constraints: data-only parser from the installed source; never execute target configuration
# last_intent_review: 2026-09-20
#
# Public shell accessors over the shared structured profile implementation.
# A sourced library must not change its caller's shell options.

LINTEL_HOME="${LINTEL_HOME:-$HOME/.lintel}"
LINTEL_SOURCE_ROOT="${LINTEL_SOURCE_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." 2>/dev/null && pwd)}"
LINTEL_REPO_ROOT="${LINTEL_REPO_ROOT:-$LINTEL_SOURCE_ROOT}"
LINTEL_PACKS_DIR="${LINTEL_PACKS_DIR:-$LINTEL_HOME/packs}"
LINTEL_ACTIVE_PACK_FILE="${LINTEL_ACTIVE_PACK_FILE:-$LINTEL_PACKS_DIR/active-pack}"
LINTEL_AUDIT_DIR="${LINTEL_AUDIT_DIR:-$LINTEL_HOME/audit}"

# A real host/session or selected work identity may be inherited. Never invent
# one from a process ID; copilot-env supplies the durable no-host-ID bootstrap.
LINTEL_SESSION_ID="${LINTEL_SESSION_ID:-${CLAUDE_SESSION_ID:-}}"
PACK_CACHE_FILE="${LINTEL_PROFILE_CONTEXT_FILE:-}"

command -v audit_log >/dev/null 2>&1 || source "${LINTEL_SOURCE_ROOT}/bin/_audit.sh"

_resolver_audit() {
  audit_log "pack-resolver" "pack_resolver_${1:-info}" "msg=${2:-}"
}

_resolver_warn() {
  printf '[lintel/pack-resolver] WARN: %s\n' "${1:-}" >&2
  _resolver_audit warn "${1:-}"
}

_resolver_fail() {
  printf '[lintel/pack-resolver] FAIL: %s\n' "${1:-}" >&2
  _resolver_audit fail "${1:-}"
}

_profile_python() {
  if [ -n "${_LINTEL_PROFILE_PYTHON:-}" ]; then return 0; fi
  local candidate
  for candidate in python3 python; do
    if command -v "$candidate" >/dev/null 2>&1 &&
      "$candidate" -c 'import sys; assert sys.version_info >= (3, 9)' >/dev/null 2>&1; then
      _LINTEL_PROFILE_PYTHON="$candidate"
      return 0
    fi
  done
  _resolver_fail "PROFILE_DEPENDENCY: Python 3.9+ is required; no neutral emergency fallback"
  return 2
}

_profile_cli() {
  _profile_python || return $?
  local rc=0 context="${LINTEL_PROFILE_CONTEXT:-}"
  if [ -z "$context" ] && [ -z "${LINTEL_PROFILE_REFERENCE:-}" ]; then
    context="${LINTEL_SESSION_ID:-}"
  fi
  "$_LINTEL_PROFILE_PYTHON" "$LINTEL_SOURCE_ROOT/lib/profile_context.py" \
    --source "$LINTEL_SOURCE_ROOT" --repo "$LINTEL_REPO_ROOT" --home "$LINTEL_HOME" \
    --packs "$LINTEL_PACKS_DIR" --pointer "$LINTEL_ACTIVE_PACK_FILE" \
    --context "$context" --reference "${LINTEL_PROFILE_REFERENCE:-}" \
    --context-file "${LINTEL_PROFILE_CONTEXT_FILE:-}" --pack "${LINTEL_PROFILE_PACK:-}" \
    "$@" || rc=$?
  if [ "$rc" -gt 1 ]; then
    _resolver_audit fail "operation=${1:-unknown} profile-context-unresolved"
  fi
  return "$rc"
}

get_active_pack_name() { _profile_cli selected; }
get_loaded_pack() { _profile_cli loaded; }
validate_pack() { _profile_cli validate "${1:-_default}"; }
pack_compatibility() { _profile_cli compatibility "${1:-_default}"; }
resolve_pack_field() { _profile_cli field "${1:-}"; }
resolve_pack_field_json() { _profile_cli field-json "${1:-}"; }
profile_field_provenance() { _profile_cli provenance "${1:-}"; }
pack_field_is_true() { _profile_cli true "${1:-}"; }
pack_is_extension() { pack_field_is_true extension.is_extension; }
pack_namespace() { _profile_cli nullable extension.namespace; }
pack_workflow() { _profile_cli nullable extension.workflow; }
profile_context_json() { _profile_cli context; }
profile_context_reference() { _profile_cli reference; }
profile_required_policy() { _profile_cli required-policy; }
verify_profile_context() {
  local reference
  if [ "$#" -gt 0 ] && [ -z "${LINTEL_PROFILE_CONTEXT:-}" ]; then
    # An explicit cold-resume reference outranks the new host's ambient session.
    reference=$(LINTEL_SESSION_ID="" LINTEL_PROFILE_REFERENCE="" _profile_cli verify "$@") || return $?
  else
    reference=$(_profile_cli verify "$@") || return $?
  fi
  # Carry the exact verified generation into following calls and child processes,
  # not just the single verification subprocess. The shared parser owns this data.
  export LINTEL_PROFILE_REFERENCE="$reference"
  printf '%s\n' "$reference"
}

bind_profile_context() {
  local reference
  reference=$(_profile_cli bind "${1:-}") || return $?
  export LINTEL_PROFILE_CONTEXT="$1"
  export LINTEL_PROFILE_REFERENCE="$reference"
  PACK_CACHE_FILE="$(_profile_cli context-path)" || return $?
  _resolver_audit context_bound "context=$LINTEL_PROFILE_CONTEXT"
  printf '%s\n' "$reference"
}

rebind_profile_context() {
  local reference
  reference=$(_profile_cli rebind "${1:-}") || return $?
  export LINTEL_PROFILE_REFERENCE="$reference"
  _resolver_audit context_rebound "context=${LINTEL_PROFILE_CONTEXT:-${LINTEL_SESSION_ID:-explicit-file}}"
  printf '%s\n' "$reference"
}

# Compatibility entry point: intentional re-resolution retains the old generation.
# It must not delete evidence or silently clear another process's selected policy.
clear_pack_cache() {
  if [ -z "${LINTEL_PROFILE_CONTEXT:-${LINTEL_SESSION_ID:-}${LINTEL_PROFILE_REFERENCE:-}}" ] &&
    [ -z "${LINTEL_PROFILE_CONTEXT_FILE:-}" ]; then
    _resolver_warn "no bound profile context to clear; one-shot reads are not pinned"
    return 0
  fi
  # Existing callers also clear before their first read. Bind that first generation
  # explicitly; a missing resume file remains an error in the shared implementation.
  local path
  path=$(_profile_cli context-path) || return $?
  if [ -f "$path" ]; then
    rebind_profile_context "explicit legacy clear_pack_cache; replan dependent work" >/dev/null
  else
    _profile_cli context >/dev/null
  fi
}

_pack_dir() {
  local path
  path=$(_profile_cli dir "${1:-}") || return $?
  case "$path" in
    [A-Za-z]:*)
      if command -v cygpath >/dev/null 2>&1; then
        path=$(cygpath -u "$path") || return $?
      fi ;;
  esac
  printf '%s' "$path"
}
_pack_yaml_field() { _profile_cli yaml-field "${1:-}" "${2:-}"; }
_pack_ext_field() { _pack_yaml_field "${1:-}" "extension.${2:-}"; }
_pack_chain_field() { _profile_cli chain-field "${1:-}" "${2:-}"; }
_resolve_extends_chain() { _profile_cli chain "${1:-}"; }

_prime_cache_for_session() {
  _profile_cli context >/dev/null || return $?
  if [ -n "${LINTEL_PROFILE_CONTEXT:-${LINTEL_SESSION_ID:-}${LINTEL_PROFILE_CONTEXT_FILE:-}${LINTEL_PROFILE_REFERENCE:-}}" ]; then
    PACK_CACHE_FILE="$(_profile_cli context-path)" || return $?
  fi
}

_merge_packs_into_cache() {
  local chain="${1:-}" selected
  selected=$(get_active_pack_name) || return $?
  if [ "${chain##* }" != "$selected" ]; then
    _resolver_fail "explicit merge must match the selected pack; bind or rebind first"
    return 2
  fi
  _prime_cache_for_session
}

if [ "${BASH_SOURCE[0]}" = "$0" ]; then
  profile_context_json
fi
