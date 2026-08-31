#!/usr/bin/env bash
# lib/orientator-routing.sh — mechanical routing helpers for skills/orientator
#
# Sourced by skills/orientator/SKILL.md. Provides:
#   classify_intent <prompt>        → intent enum
#   match_workflow <intent> <default> → workflow string
#   assess_risk <workflow> <high_risk_csv> → risk enum
#   score_confidence <intent> <workflow> → confidence enum
#   check_escalation_threshold <confidence> <threshold> → yes|no
#   invoke_llm_orientation <prompt> <default> <budget> → stub (Phase 4)
#
# Ref: docs/concepts/orientator.md

# sourced library: no 'set -uo pipefail' here (shell opts leak into every caller — skills/hooks/tests); functions guard their own vars

# ─── classify_intent ───────────────────────────────────────────────────────
# Returns: build | fix | review | research | ship | deploy | scaffold | resume | unclear
classify_intent() {
  local p="${1:-}"
  [ -z "$p" ] && { printf 'unclear'; return 0; }

  # Lowercase for matching
  local lp
  lp=$(printf '%s' "$p" | tr '[:upper:]' '[:lower:]')

  # Order matters: first match wins
  case "$lp" in
    *bug*|*broken*|*error*|*crash*|*fix\ *|*fixa*|*felsök*)        printf 'fix'; return 0 ;;
    *deploy*|*deploya*|*provision*|*driftsätt*)                     printf 'deploy'; return 0 ;;
    *ship*|*release*|*shippa*|*landa*)                              printf 'ship'; return 0 ;;
    *review\ *|*audit*|*check\ *|*granska*)                         printf 'review'; return 0 ;;
    *research*|*explore*|*understand*|*utforska*|*förstå*)          printf 'research'; return 0 ;;
    *scaffold*|*new\ project*|*new\ repo*|*nytt\ projekt*|*starta*) printf 'scaffold'; return 0 ;;
    *resume*|*continue*|*pick\ up*|*fortsätt*)                      printf 'resume'; return 0 ;;
    *build*|*add\ *|*implement*|*new\ feature*|*bygg*|*lägg\ till*) printf 'build'; return 0 ;;
  esac

  printf 'unclear'
}

# ─── match_workflow ────────────────────────────────────────────────────────
# Maps intent → workflow string. `default` used for `unclear`.
match_workflow() {
  local intent="${1:-unclear}"
  local default="${2:-cycle}"
  case "$intent" in
    build)    printf '/li:cycle' ;;
    fix)      printf '/li:cycle --mode hotfix' ;;
    review)   printf '/li:review' ;;
    research) printf '/li:cycle --mode research-dive' ;;
    ship)     printf '/li:cycle --from SHIP' ;;
    deploy)   printf '/li:cycle --from SHIP' ;;
    scaffold) printf 'bin/li-scaffold init' ;;
    resume)   printf '/li:resume' ;;
    unclear|*) printf '/li:%s' "$default" ;;
  esac
}

# ─── assess_risk ───────────────────────────────────────────────────────────
# Returns: low | medium | high
# High if workflow appears in pack's high_risk_workflows CSV.
assess_risk() {
  local workflow="${1:-}"
  local high_risk_csv="${2:-}"

  # Strip flags/args from workflow for matching
  local base_workflow
  base_workflow=$(printf '%s' "$workflow" | awk '{print $1}' | sed 's|^/li:||' | sed 's|^bin/||')

  # Default high-risk if not specified by pack
  if [ -z "$high_risk_csv" ]; then
    high_risk_csv="cycle,plan,ship"
  fi

  # CSV match
  case ",$high_risk_csv," in
    *",$base_workflow,"*) printf 'high'; return 0 ;;
  esac

  # Hotfix is medium (touches code without full review)
  case "$workflow" in
    *hotfix*) printf 'medium'; return 0 ;;
  esac

  # Research is low (read-only)
  case "$workflow" in
    *research-dive*) printf 'low'; return 0 ;;
  esac

  # Default: medium
  printf 'medium'
}

# ─── score_confidence ──────────────────────────────────────────────────────
# Returns: low | medium | high
score_confidence() {
  local intent="${1:-unclear}"
  local workflow="${2:-}"

  case "$intent" in
    unclear) printf 'low' ;;
    build|fix|review|research|ship|deploy|scaffold|resume) printf 'high' ;;
    *) printf 'medium' ;;
  esac
}

# ─── check_escalation_threshold ────────────────────────────────────────────
# Returns: yes | no
# Escalate when confidence ≤ threshold (threshold ordering: never < low < medium < high)
check_escalation_threshold() {
  local confidence="${1:-low}"
  local threshold="${2:-medium}"

  # threshold "never" means never escalate
  [ "$threshold" = "never" ] && { printf 'no'; return 0; }

  # Numeric ranks for comparison
  local c_rank t_rank
  case "$confidence" in low) c_rank=1 ;; medium) c_rank=2 ;; high) c_rank=3 ;; *) c_rank=1 ;; esac
  case "$threshold" in low) t_rank=1 ;; medium) t_rank=2 ;; high) t_rank=3 ;; *) t_rank=2 ;; esac

  # Escalate if confidence < threshold (strict)
  if [ "$c_rank" -lt "$t_rank" ]; then
    printf 'yes'
  else
    printf 'no'
  fi
}

# ─── invoke_llm_orientation ────────────────────────────────────────────────
# Phase 4 hook. v4.0 ships as stub that returns "mechanical" (no LLM call).
# When operator opts into LLM-escalation in Phase 4, this gets replaced with
# a real subagent invocation respecting the budget.
invoke_llm_orientation() {
  local prompt="${1:-}"
  local default="${2:-cycle}"
  local budget="${3:-0}"
  # v4.0 stub
  printf '{"source":"mechanical","budget_used":0,"recommendation":"%s"}' "$default"
}

# ─── Self-test mode ────────────────────────────────────────────────────────
if [ "${BASH_SOURCE[0]}" = "$0" ]; then
  echo "orientator-routing.sh self-test:"
  for p in "fix the broken button" "build a new feature" "what should I do?" "review my PR" "ship it" "deploy a website to azure"; do
    intent=$(classify_intent "$p")
    workflow=$(match_workflow "$intent" cycle)
    risk=$(assess_risk "$workflow" "cycle,plan,ship")
    confidence=$(score_confidence "$intent" "$workflow")
    printf '  prompt=%-30s intent=%-10s workflow=%-30s risk=%-7s confidence=%s\n' \
      "\"$p\"" "$intent" "$workflow" "$risk" "$confidence"
  done
fi
