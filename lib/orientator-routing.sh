#!/usr/bin/env bash
# lib/orientator-routing.sh — mechanical routing helpers for skills/orientator
# component: orientator-routing
# implements: ADR-0028
# intent: docs/concepts/orientator.md
# constraints: none; recommendations do not execute workflows
# last_intent_review: 2026-09-20
#
# Sourced by skills/orientator/SKILL.md. Provides:
#   classify_intent <prompt>        → intent enum
#   match_workflow <intent> <default> [namespace] → workflow string
#   assess_risk <workflow> <high_risk_csv> → risk enum
#   score_confidence <intent> <workflow> → confidence enum
#   check_escalation_threshold <confidence> <threshold> → yes|no
#   invoke_llm_orientation <prompt> <default> <budget> → stub (Phase 4)
#
# Ref: docs/concepts/orientator.md

# sourced library: no 'set -uo pipefail' here (shell opts leak into every caller — skills/hooks/tests); functions guard their own vars

# ─── classify_intent ───────────────────────────────────────────────────────
# Returns: build | fix | plan | review | research | ship | deploy | scaffold | resume | unclear
classify_intent() {
  local p="${1:-}"
  [ -z "$p" ] && { printf 'unclear'; return 0; }

  local lp normalized token next intent suffix negated=0 saw_negation=0 skipped_negation=0 i
  local -a words
  lp=$(printf '%s' "$p" | tr '[:upper:]' '[:lower:]')
  lp="${lp//don\'t/do not}"
  normalized=$(printf '%s' "$lp" | tr '[:space:][:punct:]' ' ')
  IFS=' ' read -r -a words <<< "$normalized"

  case "${words[0]:-}" in
    how|why|should) printf 'research'; return 0 ;;
    what|where|when|who)
      if [ "${#words[@]}" -eq 4 ] && [ "${words[1]}" = should ] &&
          [ "${words[2]}" = i ] && [ "${words[3]}" = do ]; then
        printf 'unclear'
      else
        printf 'research'
      fi
      return 0 ;;
  esac

  # An operation precedes its subject: "review the release" is not SHIP, but
  # "fix review comments" remains FIX. Negated operations grant no write intent.
  for ((i=0; i<${#words[@]}; i++)); do
    token="${words[$i]}"
    next="${words[$((i + 1))]:-}"
    case "$token" in
      not|never|without) negated=1; saw_negation=1; continue ;;
      and|or) [ "$skipped_negation" -eq 0 ] || negated=1; continue ;;
      but|instead) negated=0; skipped_negation=0; continue ;;
    esac
    intent=""
    case "$token" in
      review|audit|check|inspect|examine|analyze|analyse|granska) intent=review ;;
      research|explore|understand|explain|describe|read|compare|summarize|summarise|show|list|utforska|förstå) intent=research ;;
      plan|design|outline) intent=plan ;;
      tell) [ "$next" != me ] || intent=research ;;
      fix|fixa|felsök) intent=fix ;;
      deploy|deploya|provision|driftsätt) intent=deploy ;;
      ship|release|shippa|landa) intent=ship ;;
      resume|continue|fortsätt) intent=resume ;;
      scaffold|starta) intent=scaffold ;;
      build|add|implement|create|edit|change|modify|write|bygg) intent=build ;;
      pick) [ "$next" != up ] || intent=resume ;;
      new)
        case "$next" in project|repo|repository) intent=scaffold ;; feature) intent=build ;; esac ;;
      nytt) [ "$next" != projekt ] || intent=scaffold ;;
      lägg) [ "$next" != till ] || intent=build ;;
    esac
    [ -n "$intent" ] || continue
    case "$token:$next" in
      build:is|build:was|build:has|build:error|build:broken|build:crash)
        continue ;;
    esac
    if [ "$negated" -eq 1 ]; then
      negated=0
      skipped_negation=1
      continue
    fi
    if [ "$token" = create ]; then
      case "${words[$((i + 1))]:-} ${words[$((i + 2))]:-} ${words[$((i + 3))]:-}" in
        "a new project"|"a new repo"|"a new repository"|"new project "*|"new repo "*|"new repository "*)
          intent=scaffold ;;
      esac
    fi
    # A sequence is not one high-confidence operation. Explanations of a
    # sequence remain read-only; an actual "review then deploy" needs scoping.
    suffix=$(printf '%s ' "${words[@]:$((i + 1))}")
    if [ "$intent" != research ] && [[ " $suffix " =~ [[:space:]]then[[:space:]]+(review|audit|check|research|explore|fix|deploy|ship|release|build|add|implement|create|edit|change|modify|write)[[:space:]] ]]; then
      printf 'unclear'
      return 0
    fi
    printf '%s' "$intent"
    return 0
  done

  # Preserve symptom-only triage without allowing a negated fix to reappear.
  if [ "$saw_negation" -eq 0 ]; then
    case "$lp" in
      *bug*|*broken*|*error*|*crash*) printf 'fix'; return 0 ;;
    esac
  fi
  printf 'unclear'
}

# ─── match_workflow ────────────────────────────────────────────────────────
# Generic new work and unclear requests use the pack default. Specific operations
# retain their canonical routes; a pack default must not turn "review" into BUILD.
_workflow_command() {
  local workflow="${1:-cycle}" namespace="${2:-}"
  case "$workflow" in
    /*|bin/*) printf '%s' "$workflow"; return ;;
    *:*) printf '/%s' "$workflow"; return ;;
  esac
  if [ -z "$namespace" ] && declare -F pack_is_extension >/dev/null 2>&1 && pack_is_extension; then
    namespace=$(pack_namespace)
  fi
  printf '/%s:%s' "${namespace:-li}" "$workflow"
}

match_workflow() {
  local intent="${1:-unclear}"
  local default="${2:-cycle}"
  case "$intent" in
    build)    _workflow_command "$default" "${3:-}" ;;
    fix)      printf '/li:cycle --mode hotfix' ;;
    plan)     printf '/li:plan' ;;
    review)   printf '/li:review' ;;
    research) printf '/li:cycle --mode research-dive' ;;
    ship)     printf '/li:cycle --from SHIP' ;;
    deploy)   printf '/li:cycle --from SHIP' ;;
    scaffold) printf 'bin/li-scaffold init' ;;
    resume)   printf '/li:resume' ;;
    unclear|*) _workflow_command "$default" "${3:-}" ;;
  esac
}

# ─── assess_risk ───────────────────────────────────────────────────────────
# Returns: low | medium | high
# High if workflow appears in pack's high_risk_workflows CSV.
assess_risk() {
  local workflow="${1:-}"
  local high_risk_csv="${2:-}"

  # Strip flags/args from workflow for matching
  local base_workflow short_workflow declared
  base_workflow="${workflow%%[[:space:]]*}"
  base_workflow="${base_workflow#/}"; base_workflow="${base_workflow#bin/}"
  short_workflow="${base_workflow##*:}"

  # Default high-risk if not specified by pack
  if [ -z "$high_risk_csv" ]; then
    high_risk_csv="cycle,plan,ship"
  fi

  # Resolver lists use [a, b]; legacy callers pass CSV or newline-separated IDs.
  # Match normalized complete IDs, so YAML punctuation cannot lower declared risk.
  high_risk_csv=$(printf '%s' "$high_risk_csv" | tr '\n' ',' | tr -d '[]"\047[:space:]')
  # A qualified ID matches only that namespace; a bare ID applies to any namespace.
  # Preserve the legacy `cycle` spelling while supporting `/team:deliver` policies.
  local IFS=' '
  for declared in ${high_risk_csv//,/ }; do
    declared="${declared#/}"; declared="${declared#bin/}"
    if [ "$declared" = "$base_workflow" ] || [ "$declared" = "$short_workflow" ]; then
      printf 'high'; return 0
    fi
  done

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
    build|fix|plan|review|research|ship|deploy|scaffold|resume) printf 'high' ;;
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
