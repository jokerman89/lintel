#!/usr/bin/env bash
# component: optional-hook-text-count
# implements: ADR-0008
# intent: .claude/plans/universal-implementation/packages/P01.md
# constraints: literal file operands; unavailable observation is not a zero count
# last_intent_review: 2026-10-04

hook_text_count() {
  local pattern="$1" file="$2" count status=0
  local flags=(-cE)
  case "${3:-}" in
    "") ;;
    -i) flags+=(-i) ;;
    *) echo "WARN [Lintel hook]: unsupported text-count mode; observation unavailable." >&2; return 2 ;;
  esac
  count=$(grep "${flags[@]}" -- "$pattern" < "$file") || status=$?
  if [ "$status" -gt 1 ] || ! [[ "$count" =~ ^[0-9]+$ ]]; then
    echo "WARN [Lintel hook]: text observation unavailable (grep exit $status); no clean result inferred." >&2
    return 2
  fi
  printf '%s\n' "$count"
}
