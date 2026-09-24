#!/usr/bin/env bash
# lib/orientator-routing.sh — mechanical routing helpers for skills/orientator
# component: orientator-routing
# implements: ADR-0028
# intent: docs/concepts/orientator.md
# constraints: none; recommendations do not execute workflows
# last_intent_review: 2026-09-22
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

_orientator_request_head() {
  local question="$1"; shift
  local -a words=("$@")
  local i=0 token next intent="" explicit=0 embedded=0 request=0 nominal=0 width=1
  while :; do
    case "${words[$i]:-}" in
      please|kindly) explicit=1; i=$((i + 1)) ;;
      ',') i=$((i + 1)) ;;
      *) break ;;
    esac
  done
  token="${words[$i]:-}"; next="${words[$((i + 1))]:-}"
  case "$token" in
    not|never|without|no|avoid|skip) intent=prohibited ;;
    what)
      if [ "$next" = should ] && [ "${words[$((i + 2))]:-}" = i ] &&
          [ "${words[$((i + 3))]:-}" = do ] && [ "${#words[@]}" -eq "$((i + 4))" ]; then
        intent=ambiguous
      else intent=research; fi ;;
    how|why|where|when|who|which|whose|should|is|are|am|was|were|has|have|had|does|did)
      intent=research ;;
    do)
      case "$next" in
        i|we|you|they|he|she|it|this|that|these|those|the) intent=research ;;
        *) explicit=1; i=$((i + 1)) ;;
      esac ;;
    can|could|would|will|may|might|must)
      if [ "$next" = you ]; then question=1; i=$((i + 2))
      else intent=research; fi ;;
    i|we)
      request=1
      case "$next" in
        want|need) i=$((i + 2)) ;;
        would)
          [ "${words[$((i + 2))]:-}" = like ] || intent=ambiguous
          i=$((i + 3)) ;;
        *) intent=ambiguous ;;
      esac
      if [ "${words[$i]:-}" = you ]; then i=$((i + 1)); fi
      case "${words[$i]:-}" in
        to) explicit=1; i=$((i + 1)) ;;
        advice|information) intent=research ;;
        *) intent=ambiguous ;;
      esac ;;
  esac
  [ "$intent" != research ] || embedded=1
  if [ -z "$intent" ] && [ "${words[$i]:-}" = help ] &&
      [ "${words[$((i + 1))]:-}" = me ]; then
    explicit=1; i=$((i + 2))
  fi
  token="${words[$i]:-}"; next="${words[$((i + 1))]:-}"
  if [ -z "$intent" ]; then
    # Nominal heads can also modify a shared object ("audit and review logging").
    # Initial and boundary positions consume this same vocabulary and metadata.
    case "$token" in
      not|never|without|no|avoid|skip) intent=prohibited ;;
      review|audit|check) intent=review; nominal=1 ;;
      inspect|examine|analyze|analyse|assess|evaluate|granska) intent=review ;;
      research) intent=research; nominal=1 ;;
      explore|understand|explain|describe|read|compare|summarize|summarise|show|list|know|utforska|förstå) intent=research ;;
      plan|design|outline) intent=plan; nominal=1 ;;
      tell) if [ "$next" = me ]; then intent=research; width=2; fi ;;
      fix) intent=fix; nominal=1 ;;
      fixa|felsök) intent=fix ;;
      deploy|deploya|provision|driftsätt) intent=deploy ;;
      ship|release) intent=ship; nominal=1 ;;
      shippa|landa) intent=ship ;;
      resume|continue|fortsätt) intent=resume ;;
      scaffold|starta) intent=scaffold ;;
      build) intent=build; nominal=1 ;;
      test) nominal=1 ;;
      add|implement|create|edit|change|modify|write|bygg) intent=build ;;
      pick) if [ "$next" = up ]; then intent=resume; width=2; fi ;;
      new) case "$next" in project|repo|repository) intent=scaffold ;; feature) intent=build ;; esac ;;
      nytt) [ "$next" != projekt ] || intent=scaffold ;;
      lägg) if [ "$next" = till ]; then intent=build; width=2; fi ;;
    esac
  fi
  if [ "$token" = create ] && [ "$intent" = build ]; then
    case "${words[$((i + 1))]:-} ${words[$((i + 2))]:-} ${words[$((i + 3))]:-}" in
      "a new project"|"a new repo"|"a new repository"|"new project "*|"new repo "*|"new repository "*)
        intent=scaffold ;;
    esac
  fi
  printf '%s:%s:%s:%s:%s:%s:%s:%s' \
    "$intent" "$i" "$explicit" "$embedded" "$request" "$nominal" "$width" "$question"
}

_orientator_object_marker() {
  case "${1:-}" in
    a|an|the|this|that|these|those|my|our|your|his|her|its|their|it|them|new|to|from|en|ett|den|det|v[0-9]*|[0-9]*)
      return 0 ;;
  esac
  return 1
}

_orientator_clause_intent() {
  local question="$1"; shift
  local -a words=("$@")
  local i j token next intent explicit embedded request nominal width negative=-1 symptom=0 objects=0
  local head head_index head_explicit head_embedded head_request head_nominal head_width head_question
  for ((j=0; j<${#words[@]}; j++)); do
    case "${words[$j]}" in
      not|never|without|no|avoid|skip) [ "$negative" -ge 0 ] || negative="$j" ;;
      bug|bugs|broken|error|errors|crash|crashes) symptom=1 ;;
    esac
  done
  IFS=: read -r intent i explicit embedded request nominal width question \
    <<< "$(_orientator_request_head "$question" "${words[@]}")"
  token="${words[$i]:-}"; next="${words[$((i + 1))]:-}"
  case "$intent" in prohibited|ambiguous) printf '%s' "$intent"; return ;; esac
  if [ "$negative" -ge 0 ] && { [ -z "$intent" ] || [ "$negative" -le "$i" ]; }; then
    printf 'prohibited'; return
  fi
  if [ -z "$intent" ]; then
    case "$token" in
      if|unless|assuming|__quoted__) printf 'ambiguous' ;;
      *) if [ "$symptom" -eq 1 ] && [ "$request" -eq 0 ]; then printf 'symptom'
         else printf 'context'; fi ;;
    esac
    return
  fi
  for ((j=i+width; j<${#words[@]}; j++)); do
    case "${words[$j]}" in
      how|whether|why|what|which|if)
        case "$intent" in research|review) embedded=1 ;; esac ;;
      then)
        [ "$embedded" -eq 1 ] || { printf 'ambiguous'; return; } ;;
      and|or)
        [ "$embedded" -eq 0 ] || continue
        IFS=: read -r head head_index head_explicit head_embedded head_request head_nominal head_width head_question \
          <<< "$(_orientator_request_head 0 "${words[@]:j+1}")"
        case "$head" in ''|prohibited) continue ;; esac
        if [ "$j" -eq "$((i + width + 1))" ] && [ "$head_index" -eq 0 ] &&
            [ "$head_nominal" -eq 1 ] && [ -n "${words[$((j + 2))]:-}" ] &&
            ! _orientator_object_marker "${words[$((i + width))]}" &&
            ! _orientator_object_marker "${words[$((j + 2))]}"; then
          IFS=: read -r head head_index head_explicit head_embedded head_request head_nominal head_width head_question \
            <<< "$(_orientator_request_head 0 "${words[$((i + width))]}")"
          if [ "$head_nominal" -eq 1 ]; then
            # A write-head noun can already be the first operation's whole object.
            case "$head:$intent" in
              research:*|review:*|:*|*:research|*:review) objects=1; continue ;;
            esac
          fi
        fi
        printf 'ambiguous'; return ;;
    esac
  done
  case "$intent" in
    research|review) ;;
    *)
      if [ "$question" -eq 1 ] || [ "$negative" -ge 0 ]; then printf 'ambiguous'; return; fi
      for ((j=i+1; j<${#words[@]}; j++)); do
        case "${words[$j]}" in
          if|unless|whether|when) printf 'ambiguous'; return ;;
          is|are|was|were|has|have|had|must|should|can|could|would|will|may|might|needs)
            if [ "$symptom" -eq 1 ] && [ "$explicit" -eq 0 ]; then printf 'symptom'
            else printf 'context'; fi
            return ;;
        esac
      done
      # Bare noun/verb heads need an object marker or explicit request wrapper.
      if [ "$explicit" -eq 0 ]; then
        case "$token" in
          build|release|ship)
            if ! _orientator_object_marker "$next" &&
                { [ "$token" != build ] || [ "$objects" -eq 0 ]; }; then
              printf 'context'; return
            fi ;;
        esac
      fi ;;
  esac
  printf '%s' "$intent"
}

_orientator_line_boundary() {
  local count="$1"; shift
  local -a before=("${@:1:count}") after=("${@:count+1}")
  local intent i explicit embedded request nominal width question
  [ "$count" -gt 0 ] || return 1
  case "${before[$((count - 1))]}" in
    and|or|to|of|about|on|in|for|with|without|a|an|the|this|that|my|our|your|its|their|den|det|en|ett)
      return 1 ;;
  esac
  IFS=: read -r intent i explicit embedded request nominal width question \
    <<< "$(_orientator_request_head 0 "${before[@]}")"
  # A wrapper or bare head still awaiting its operand is a line wrap.
  [ "$count" -gt "$((i + width))" ] || return 1
  IFS=: read -r intent i explicit embedded request nominal width question \
    <<< "$(_orientator_request_head 0 "${after[@]}")"
  case "$intent" in ''|prohibited) return 1 ;; esac
  return 0
}

# ─── classify_intent ───────────────────────────────────────────────────────
# Returns: build | fix | plan | review | research | ship | deploy | scaffold | resume | unclear
classify_intent() {
  local lp char following token="" quote="" heading=0 line_start=1 i j result selected="" governing=""
  local prohibited=0 context=0 ambiguous=0 symptom=0 question=0
  local -a words=() clause=() following_words=()
  lp=$(printf '%s' "${1:-}" | tr '[:upper:]' '[:lower:]')
  lp="${lp//’/\'}"; lp="${lp//n\'t/ not}"
  for ((i=0; i<${#lp}; i++)); do
    char="${lp:$i:1}"; following="${lp:$((i + 1)):1}"
    if [ "$heading" -eq 1 ]; then
      if [ "$char" = $'\n' ]; then heading=0; line_start=1; words+=(';'); fi
      continue
    fi
    if [ -n "$quote" ]; then
      if [ "$char" = "$quote" ]; then quote=""; words+=('__quoted__')
      elif [ "$char" = '\' ] && [ "$following" = "$quote" ]; then i=$((i + 1)); fi
      continue
    fi
    case "$char" in
      '"'|'`'|"'")
        if [ "$char" = "'" ] && [ -n "$token" ]; then token+="$char"; continue; fi
        [ -z "$token" ] || words+=("$token")
        token=""; quote="$char"; line_start=0; continue ;;
      '#')
        if [ "$line_start" -eq 1 ]; then heading=1; continue; fi ;;
      [[:space:]])
        [ -z "$token" ] || words+=("$token")
        token=""
        if [ "$char" = $'\n' ]; then line_start=1; words+=("$char"); fi
        continue ;;
      '.'|':')
        case "$following" in ''|[[:space:]]) ;; *) token+="$char"; line_start=0; continue ;; esac ;;
      ';'|'!'|'?'|',') ;;
      *) token+="$char"; line_start=0; continue ;;
    esac
    [ -z "$token" ] || words+=("$token")
    token=""; words+=("$char"); line_start=0
  done
  [ -z "$quote" ] || { printf 'unclear'; return 0; }
  [ -z "$token" ] || words+=("$token")
  words+=(';')
  for ((i=0; i<${#words[@]}; i++)); do
    token="${words[$i]}"
    if [ "$token" = $'\n' ]; then
      [ -z "$governing" ] || continue
      following_words=()
      for ((j=i+1; j<${#words[@]}; j++)); do
        case "${words[$j]}" in
          ';'|'.'|'!'|'?'|':'|but|instead) break ;;
          $'\n') ;;
          *) following_words+=("${words[$j]}") ;;
        esac
      done
      _orientator_line_boundary "${#clause[@]}" "${clause[@]}" "${following_words[@]}" || continue
      token=';'
    fi
    case "$token" in
      ':')
        if [ -z "$governing" ] && [ "${#clause[@]}" -gt 0 ]; then
          result=$(_orientator_clause_intent 0 "${clause[@]}")
          case "$result" in
            research|review)
              case "${clause[0]}:${clause[1]:-}" in
                review:*|audit:*|check:*|research:*)
                  case "${clause[1]:-}" in
                    a|an|the|this|that|my|our|your|it|them) governing="$result" ;;
                    *) context=1 ;;
                  esac ;;
                *) governing="$result" ;;
              esac ;;
            prohibited) prohibited=1 ;;
            *) context=1 ;;
          esac
        fi
        clause=(); continue ;;
      ';'|'.'|'!'|'?'|but|instead)
        [ "${#clause[@]}" -gt 0 ] || [ -n "$governing" ] || continue
        question=0; [ "$token" != '?' ] || question=1
        result="${governing:-$(_orientator_clause_intent "$question" "${clause[@]}")}"
        clause=(); governing=""
        case "$result" in
          prohibited) prohibited=1 ;;
          context) context=1 ;;
          ambiguous) ambiguous=1 ;;
          symptom) symptom=1 ;;
          *)
            [ -z "$selected" ] || ambiguous=1
            selected="$result" ;;
        esac ;;
      *) clause+=("$token") ;;
    esac
  done
  case "$selected" in
    research|review) ;;
    *) [ "$prohibited" -eq 0 ] && [ "$context" -eq 0 ] || ambiguous=1 ;;
  esac
  if [ "$ambiguous" -eq 1 ]; then printf 'unclear'
  elif [ -n "$selected" ]; then printf '%s' "$selected"
  elif [ "$symptom" -eq 1 ] && [ "$prohibited" -eq 0 ]; then printf 'fix'
  else printf 'unclear'; fi
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
