#!/usr/bin/env bash
# bin/_aliases.sh — sourced helper for env-var alias resolution
#
# Per design: docs/design/lintel-v3.6-alias-mechanism.md
# Used by bin/li-* scripts to honor deprecated env-var names during grace period.
#
# Usage (in bin/li-foo):
#   source "$(dirname "$0")/_aliases.sh"
#   LINTEL_HOME=$(resolve_env_var LINTEL_HOME)
#
# Behavior:
# - Read $NEW_NAME first. If populated, return as-is.
# - If empty, scan config/aliases.yaml env_var_aliases for an old-name mapping to NEW_NAME.
# - If an old-name has a populated value, warn to stderr + return that value.
# - If both empty, return empty string (caller falls back to default).

LINTEL_REPO_ROOT="${LINTEL_REPO_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." 2>/dev/null && pwd)}"
LINTEL_ALIASES_FILE="${LINTEL_ALIASES_FILE:-$LINTEL_REPO_ROOT/config/aliases.yaml}"
LINTEL_AUDIT_DIR="${LINTEL_AUDIT_DIR:-$HOME/.lintel/audit}"

resolve_env_var() {
  local new_name="$1"
  local new_value
  # Indirect expansion — bash-portable across 3.x/4.x/5.x
  new_value="${!new_name:-}"
  if [ -n "$new_value" ]; then
    printf '%s' "$new_value"
    return 0
  fi

  # New is empty — check if any alias maps to this new-name
  [ -f "$LINTEL_ALIASES_FILE" ] || { printf ''; return 0; }

  # Parse env_var_aliases section — simple grep+awk (yq not required for portability)
  # Expects: lines like "  - old: OLD_NAME" and "    new: NEW_NAME"
  local in_env_section=0
  local current_old=""
  while IFS= read -r line; do
    case "$line" in
      "env_var_aliases:"*) in_env_section=1; continue ;;
      "skill_aliases:"*|"plugin_slug_aliases:"*) in_env_section=0; continue ;;
    esac
    [ "$in_env_section" = "1" ] || continue

    # Match "  - old: NAME"
    if [[ "$line" =~ ^[[:space:]]*-[[:space:]]*old:[[:space:]]*([A-Za-z_][A-Za-z0-9_]*) ]]; then
      current_old="${BASH_REMATCH[1]}"
      continue
    fi
    # Match "    new: NAME"
    if [[ "$line" =~ ^[[:space:]]+new:[[:space:]]*([A-Za-z_][A-Za-z0-9_]*) ]]; then
      local current_new="${BASH_REMATCH[1]}"
      if [ "$current_new" = "$new_name" ] && [ -n "$current_old" ]; then
        local old_value="${!current_old:-}"
        if [ -n "$old_value" ]; then
          echo "[lintel] WARN: \$$current_old is deprecated, please switch to \$$new_name" >&2
          # Audit-log
          mkdir -p "$LINTEL_AUDIT_DIR" 2>/dev/null || true
          local ts
          ts=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
          printf '{"ts":"%s","kind":"env_var","old":"%s","new":"%s","context":"resolve_env_var"}\n' \
            "$ts" "$current_old" "$new_name" >> "$LINTEL_AUDIT_DIR/alias-resolution.jsonl" 2>/dev/null || true
          printf '%s' "$old_value"
          return 0
        fi
      fi
    fi
  done < "$LINTEL_ALIASES_FILE"

  printf ''
  return 0
}

# List all skill_aliases — used by bin/li-doctor --aliases
list_skill_aliases() {
  [ -f "$LINTEL_ALIASES_FILE" ] || return 0

  local in_skill_section=0
  local current_old=""
  while IFS= read -r line; do
    case "$line" in
      "skill_aliases:"*) in_skill_section=1; continue ;;
      "env_var_aliases:"*|"plugin_slug_aliases:"*) in_skill_section=0; continue ;;
    esac
    [ "$in_skill_section" = "1" ] || continue

    if [[ "$line" =~ ^[[:space:]]*-[[:space:]]*old:[[:space:]]*([A-Za-z0-9_-]+) ]]; then
      current_old="${BASH_REMATCH[1]}"
    fi
    if [[ "$line" =~ ^[[:space:]]+new:[[:space:]]*([A-Za-z0-9_-]+) ]]; then
      local current_new="${BASH_REMATCH[1]}"
      [ -n "$current_old" ] && printf '%s -> %s\n' "$current_old" "$current_new"
      current_old=""
    fi
  done < "$LINTEL_ALIASES_FILE"
}

# Self-test: source + call resolve_env_var with a dummy
if [ "${BASH_SOURCE[0]}" = "$0" ]; then
  # Direct invocation = self-test mode
  echo "_aliases.sh self-test:"
  echo "  LINTEL_ALIASES_FILE = $LINTEL_ALIASES_FILE"
  if [ -f "$LINTEL_ALIASES_FILE" ]; then
    echo "  Skill aliases:"
    list_skill_aliases | sed 's/^/    /'
  else
    echo "  (aliases.yaml not found)"
  fi
fi
