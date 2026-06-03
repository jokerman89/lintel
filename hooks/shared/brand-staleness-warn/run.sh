#!/usr/bin/env bash
# brand-staleness-warn — Lintel warn-only hook
# Surfaces when doc-gen runs against brand assets older than 90 days.

set -euo pipefail

LINTEL_HOME="${LINTEL_HOME:-$HOME/.lintel}"
BRAND_VERSION_FILE="$LINTEL_HOME/brand/brand-version.txt"
mkdir -p "$LINTEL_HOME/audit" "$LINTEL_HOME/brand"

# Unified audit writer (hooks/shared/<name>/ → repo-root → bin/). Idempotent source.
command -v audit_log >/dev/null 2>&1 || source "$(dirname "${BASH_SOURCE[0]}")/../../../bin/_audit.sh"

[ -f "$BRAND_VERSION_FILE" ] || exit 0   # No brand pulled = different problem, not this hook

# Get pull date
pulled_at=$(grep -E '^pulled_at:' "$BRAND_VERSION_FILE" 2>/dev/null | sed 's/^pulled_at:[ ]*//')
[ -z "$pulled_at" ] && exit 0   # malformed file, skip

# Compute age (cross-platform; fall back to file mtime)
if stat -c "%Y" "$BRAND_VERSION_FILE" >/dev/null 2>&1; then
  mtime=$(stat -c "%Y" "$BRAND_VERSION_FILE")
else
  mtime=$(stat -f "%m" "$BRAND_VERSION_FILE" 2>/dev/null || echo 0)
fi
now=$(date +%s)
age_days=$(( (now - mtime) / 86400 ))

if [ "$age_days" -gt 90 ]; then
  brand_version=$(grep -E '^version:' "$BRAND_VERSION_FILE" 2>/dev/null | sed 's/^version:[ ]*//')
  skill_invoked="${1:-unknown}"

  audit_log "hooks" "brand_staleness_warn" "hook=brand-staleness-warn" "tier=warn" "brand_age_days=$age_days" "brand_version=$brand_version" "skill_invoked=$skill_invoked"

  echo "WARN [Lintel hook]: brand version $brand_version is $age_days days old (>90 day threshold)"
  echo "WARN: Consider /brand-update to refresh from MS portal. Override with --ignore-stale-brand if intentional."
fi

exit 0
