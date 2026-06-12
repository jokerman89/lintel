#!/usr/bin/env bash
# component: cycle-modes
# implements: ADR-0003
# intent: .claude/decisions/0003-cycle-position-footer.md
# last_intent_review: 2026-06-09
#
# lib/cycle-modes.sh — the canonical 9-step cycle order (the 8 core phases + the light
# SCOPE phase between SENSE and DEFINE, per skills/cycle/SKILL.md) + the mode→skipped-phases
# map, defined ONCE. Shared by skills/cycle (the orchestrator presets) and
# lib/cycle-footer.sh (the position footer), so the two can never disagree about
# which phases a mode runs. This is the shared-schema discipline: the skip-map was
# previously implicit only in the cycle preset prose; it now has a single home.
# CRLF-safe, no external deps. Idempotent source.
#
# cycle_phases            -> the 9 cycle steps in canonical order, one per line.
# cycle_mode_skips <mode> -> phases skipped by <mode>, space-separated (empty = none).
# cycle_phase_known <p>   -> exit 0 if <p> is a canonical phase (case-insensitive).
command -v cycle_mode_skips >/dev/null 2>&1 && return 0 2>/dev/null

# Canonical order. SCOPE is the light phase between SENSE and DEFINE.
_CYCLE_PHASES="SENSE SCOPE DEFINE DISCOVER PLAN BUILD REVIEW SHIP CAPTURE"

cycle_phases() {
  local p
  for p in $_CYCLE_PHASES; do printf '%s\n' "$p"; done
}

cycle_phase_known() {
  local p; p="$(printf '%s' "${1:-}" | tr '[:lower:]' '[:upper:]')"
  case " $_CYCLE_PHASES " in *" $p "*) return 0 ;; *) return 1 ;; esac
}

# mode→skipped. Mirrors the presets in skills/cycle/SKILL.md. Modes that run the
# full pipeline (full, internal-tool, meta-infra, auto) skip nothing. Unknown modes
# degrade to "skip nothing" so a new pack-contributed mode never renders wrong.
cycle_mode_skips() {
  local mode; mode="$(printf '%s' "${1:-full}" | tr '[:upper:]' '[:lower:]')"
  case "$mode" in
    hotfix)        printf 'SCOPE DEFINE DISCOVER PLAN CAPTURE' ;;
    research-dive) printf 'SCOPE PLAN BUILD REVIEW SHIP CAPTURE' ;;
    *)             printf '' ;;
  esac
}
