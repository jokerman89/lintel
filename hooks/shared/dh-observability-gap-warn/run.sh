#!/usr/bin/env bash
# dh-observability-gap-warn — Lintel warn-only hook
# Surfaces service entry-point edits without observability instrumentation.

set -euo pipefail

LINTEL_HOME="${LINTEL_HOME:-$HOME/.lintel}"
mkdir -p "$LINTEL_HOME/audit"

command -v audit_log >/dev/null 2>&1 || source "$(dirname "${BASH_SOURCE[0]}")/../../../bin/_audit.sh"

file_edited="${1:-}"
[ -z "$file_edited" ] || [ ! -f "$file_edited" ] && exit 0

# Detect service entry points (heuristic)
matches_entry=0
case "$file_edited" in
  src/api/*|src/handlers/*|src/routes/*|src/controllers/*|src/endpoints/*) matches_entry=1 ;;
  *_handler*|*_controller*|*Handler*|*Controller*) matches_entry=1 ;;
  pkg/*/api/*|pkg/*/handlers/*) matches_entry=1 ;;
esac

if [ "$matches_entry" -eq 0 ] && [ -f "$LINTEL_REPO_ROOT/lib/pack-resolver.sh" ]; then
  source "$LINTEL_REPO_ROOT/lib/pack-resolver.sh" 2>/dev/null
  entry_glob=$(resolve_pack_field devops_hosting.service_entry_glob 2>/dev/null || true)
  if [ -n "$entry_glob" ]; then
    IFS=',' read -ra patterns <<< "$entry_glob"
    for p in "${patterns[@]}"; do
      p=$(printf '%s' "$p" | tr -d '[:space:]')
      case "$file_edited" in $p) matches_entry=1; break ;; esac
    done
  fi
fi

[ "$matches_entry" -eq 0 ] && exit 0

# Scan for observability markers
markers_found=0

# Metric emission
grep -qiE '(counter|histogram|gauge|metric|tracer|recordMetric|emitMetric|prometheus|otel)' "$file_edited" 2>/dev/null && markers_found=$((markers_found + 1))

# Trace spans
grep -qiE '(startSpan|tracer\.|withSpan|trace\.start|otel\.|opentelemetry)' "$file_edited" 2>/dev/null && markers_found=$((markers_found + 1))

# Structured logging
grep -qiE '(log\.(info|warn|error|debug)|logger\.|slog\.|zap\.|logrus\.|winston)' "$file_edited" 2>/dev/null && markers_found=$((markers_found + 1))

if [ "$markers_found" -eq 0 ]; then
  audit_log "hooks" "dh_observability_gap_warn" "hook=dh-observability-gap-warn" "tier=warn" "file_edited=$file_edited" "markers_found=0"

  echo "WARN [Lintel hook dh-observability-gap-warn]: $file_edited"
  echo "WARN: service entry-point without observability instrumentation (no metric/trace/log markers detected)"
  echo "WARN: consider /li:dh single --action observability-spec, or pass --ignore-observability-gap if instrumentation is in middleware/decorators."
fi

exit 0
