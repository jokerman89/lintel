#!/usr/bin/env bash
# component: audit-read-route
# implements: ADR-0008, ADR-0034
# intent: skills/audit/references/method.md
# constraints: read-only glue; _audit owns paths and li-events owns parsing/classification
# last_intent_review: 2026-10-03
set -uo pipefail
source_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)" || exit 2
source "$source_root/bin/_audit.sh" || exit $?
python="${LINTEL_PYTHON:-python3}"
category="" kind="" since="" limit=50
while [ "$#" -gt 0 ]; do
  case "$1" in
    --category|--kind|--since|--limit)
      [ "$#" -ge 2 ] && [ -n "$2" ] || {
        printf 'audit: %s requires a nonempty value.\n' "$1" >&2; exit 2;
      }
      case "$1" in
        --category) category="$2" ;;
        --kind) kind="$2" ;;
        --since) since="$2" ;;
        --limit) limit="$2" ;;
      esac
      shift 2 ;;
    *) printf 'audit: unknown option: %s\n' "$1" >&2; exit 2 ;;
  esac
done
[[ "$limit" =~ ^[1-9][0-9]*$ ]] || { echo 'audit: --limit must be a positive integer.' >&2; exit 2; }
filters=()
[ -z "$kind" ] || filters+=(--kind "$kind")
if [ -n "$since" ]; then
  since_iso="$(audit_days_ago "$since")" || {
    echo 'audit: cannot compute window; refusing an unfiltered read.' >&2; exit 2;
  }
  filters+=(--since "$since_iso")
fi
categories=()
if [ -n "$category" ]; then
  # The existing router owns category validation as well as source precedence.
  audit_read_files "$category" >/dev/null || exit $?
  categories=("$category")
else
  directories=("$(audit_dir hooks)" "$(audit_dir pack-resolver)")
  for directory in "${directories[@]}"; do
    if [ -e "$directory" ] && { [ ! -d "$directory" ] || [ ! -r "$directory" ]; }; then
      printf 'audit: unreadable log directory: %s\n' "$directory" >&2; exit 2
    fi
  done
  mapfile -t categories < <(
    for directory in "${directories[@]}"; do
      for file in "$directory"/*.jsonl; do
        [ ! -e "$file" ] && [ ! -L "$file" ] || basename "$file" .jsonl
      done
    done | sort -u
  )
fi
if [ "${#categories[@]}" -eq 0 ]; then
  echo 'unobserved: no audit categories in the selected roots; coverage is unknown.'
  exit 3
fi
observed=false diagnostics=false
for category_name in "${categories[@]}"; do
  candidates="$(audit_read_files "$category_name")" || exit $?
  log="" first=""
  while IFS= read -r candidate; do
    [ -n "$first" ] || first="$candidate"
    if [ -e "$candidate" ] || [ -L "$candidate" ]; then
      if [ -z "$log" ]; then log="$candidate"
      else printf 'audit: also present, not read: %s\n' "$candidate" >&2
      fi
    fi
  done <<< "$candidates"
  # Let the actual reader describe an absent file rather than manufacturing counts.
  [ -n "$log" ] || log="$first"
  printf 'Reading category %s: %s\n' "$category_name" "$log"
  code=0
  summary="$("$python" -B "$source_root/bin/li-events.py" summary \
    --file "$log" --category "$category_name" "${filters[@]}")" || code=$?
  printf '%s\n' "$summary"
  case "$code" in
    0) observed=true ;;
    3) ;;
    4) diagnostics=true ;;
    *) exit "$code" ;;
  esac
  if [ -n "$category$kind$since" ]; then
    code=0
    records="$("$python" -B "$source_root/bin/li-events.py" records \
      --file "$log" --category "$category_name" "${filters[@]}")" || code=$?
    case "$code" in 0|3) ;; 4) diagnostics=true ;; *) exit "$code" ;; esac
    printf 'Preview: at most %s rows; summary above retains all counts and diagnostics.\n' "$limit"
    printf '%s\n' "$records" | sed -n "1,${limit}p" || exit $?
  fi
done
[ "$diagnostics" = false ] || exit 4
[ "$observed" = true ] || exit 3
exit 0
