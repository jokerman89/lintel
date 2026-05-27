#!/usr/bin/env bash
# non-first-party-warn — JStack warn-only hook
# Surfaces 3P-dep-with-MS-alternative when manifest is edited.

set -euo pipefail

TARGET_PATH="${1:-}"
PAYLOAD="${2:-}"
[ -z "$TARGET_PATH" ] && exit 0

JSTACK_HOME="${JSTACK_HOME:-$HOME/.jstack}"
mkdir -p "$JSTACK_HOME/audit"
AUDIT="$JSTACK_HOME/audit/hooks.jsonl"

# Only fire on manifest files
case "$TARGET_PATH" in
  *package.json|*requirements.txt|*pyproject.toml|*Cargo.toml|*go.mod|*pom.xml) ;;
  *) exit 0 ;;
esac

ALT_FILE="$JSTACK_HOME/first-party-alternatives.yaml"
[ ! -f "$ALT_FILE" ] && exit 0   # No mapping = nothing to compare

# Built-in default mapping (operator can extend via the YAML)
# Format: 3p-package-name → MS first-party alternative

hits=()
while IFS= read -r line; do
  # Match lines like: `pkg-name:` followed by alternative text
  pkg=$(echo "$line" | sed -nE 's/^[ ]*([a-zA-Z0-9@/_-]+):[ ]*.*/\1/p')
  [ -z "$pkg" ] && continue
  if echo "$PAYLOAD" | grep -qE "\"$pkg\"" 2>/dev/null; then
    alt=$(echo "$line" | sed -nE 's/^[ ]*[^:]+:[ ]*"?(.+?)"?[ ]*$/\1/p')
    hits+=("${pkg} -> ${alt}")
  fi
done < "$ALT_FILE"

if [ ${#hits[@]} -gt 0 ]; then
  ts=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
  joined=$(IFS='|'; echo "${hits[*]}")
  printf '{"hook":"non-first-party-warn","tier":"warn","ts":"%s","target":"%s","hits":"%s"}\n' \
    "$ts" "$TARGET_PATH" "$joined" >> "$AUDIT"
  echo "WARN [JStack hook]: 3P deps with MS-1P alternatives found in $TARGET_PATH"
  for hit in "${hits[@]}"; do
    echo "WARN:   $hit"
  done
  echo "WARN: Justify in commit message or run /first-party-check for migration plan."
fi

exit 0
