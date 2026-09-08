#!/usr/bin/env bash
# component: enterprise-pack-impact-test
# implements: ADR-0018, ADR-0002
# intent: docs/concepts/pack-resolver.md
# constraints: none; synthetic packs and audits, no real profile or workflow execution
# last_intent_review: 2026-09-08
set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
review_parent="$(cd "${TMPDIR:-/tmp}" && pwd -P)"
review_tmp="$(mktemp -d "$review_parent/lintel-enterprise.XXXXXX")" || exit 1
cleanup() {
  case "$review_tmp" in "$review_parent"/lintel-enterprise.*)
    [ "$(cd "$review_tmp" && pwd -P)" = "$review_tmp" ] && rm -rf -- "$review_tmp" ;;
  esac
}
trap cleanup EXIT
export LINTEL_HOME="$review_tmp/home" LINTEL_REPO_ROOT="$REPO_ROOT"
export LINTEL_PACKS_DIR="$LINTEL_HOME/packs" LINTEL_ACTIVE_PACK_FILE="$LINTEL_HOME/packs/active-pack"
export LINTEL_AUDIT_DIR="$review_tmp/audit" LINTEL_SESSION_ID="enterprise-impact-$$"
mkdir -p "$LINTEL_PACKS_DIR/enterprise" "$LINTEL_PACKS_DIR/team"
source "$REPO_ROOT/lib/pack-resolver.sh"
source "$REPO_ROOT/lib/orientator-routing.sh"
source "$REPO_ROOT/lib/brief-forge-evaluators.sh"
failed=0
assert_eq() {
  if [ "$1" = "$2" ]; then printf 'PASS: %s\n' "$3";
  else printf 'FAIL: %s expected=<%s> actual=<%s>\n' "$3" "$1" "$2"; failed=1; fi
}
cat > "$LINTEL_PACKS_DIR/enterprise/pack.yaml" <<'YAML'
name: enterprise
version: 1.0.0
voice: {default_tier: external}
compliance:
  mode: hard
  hooks:
    - evidence-check
    - privacy-check
navigation:
  default_workflow: delivery
  high_risk_workflows: [cycle, plan, ship]
  auto_mode_eligible: true
brief_forge_handoffs:
  on_subagent_spawn:
    enabled: true
    evaluators:
      - security
      - stale
YAML
cat > "$LINTEL_PACKS_DIR/team/pack.yaml" <<'YAML'
name: team
version: 1.0.0
extends: enterprise
brand: {name: Engineering}
YAML
# This stale profile matches the state produced by the old pack-switch flow.
printf 'active_pack: _default\ndefault_mode: internal-tool\n' > "$LINTEL_HOME/profile.yaml"
printf '_default\n' > "$LINTEL_ACTIVE_PACK_FILE"
neutral_mode=$(resolve_pack_field compliance.mode)
neutral_gates=$(resolve_pack_field compliance.hooks | tr -d '[]' | tr ',' ' ')
assert_eq advisory "$neutral_mode" 'neutral baseline mode'
assert_eq '' "$neutral_gates" 'neutral baseline has no pack gates'
printf 'team\n' > "$LINTEL_ACTIVE_PACK_FILE"
assert_eq _default "$(get_loaded_pack)" 'pack switch preserves current session cache'
clear_pack_cache
assert_eq hard "$(resolve_pack_field compliance.mode)" 'next cycle inherits enterprise requirements'
# Exercise the actual input-normalization pipeline from compliance-gate, without
# pretending that synthetic names are installed executable compliance gates.
gates=$(resolve_pack_field compliance.hooks | tr -d '[]' | tr ',' ' ')
read -r -a gate_ids <<< "$gates"
assert_eq 2 "${#gate_ids[@]}" 'aggregator receives both required gates instead of GREEN no-op'
assert_eq evidence-check "${gate_ids[0]:-}" 'first gate identity reaches aggregator'
workflow=$(match_workflow research "$(resolve_pack_field navigation.default_workflow)")
risk=$(assess_risk "$workflow" "$(resolve_pack_field navigation.high_risk_workflows)")
assert_eq high "$risk" 'pack high-risk rule wins over read-only heuristic'
assert_eq high "$(assess_risk '/li:cycle' $'cycle\nplan\nship')" 'legacy newline risk list'
assert_eq high "$(assess_risk '/li:cycle' 'cycle,plan,ship')" 'legacy CSV risk list'
assert_eq 'security  stale' "$(evaluators_for_handoff on_subagent_spawn)" 'existing evaluator consumer receives nested list'
digest=$(bash "$REPO_ROOT/hooks/shared/session-digest/run.sh")
case "$digest" in *'Pack: team'*'compliance: hard'*) printf 'PASS: digest reports loaded pack and its compliance\n' ;;
  *) printf 'FAIL: digest disagrees with loaded enterprise identity\n'; failed=1 ;; esac
assert_eq _default "$(sed -n 's/^active_pack: //p' "$LINTEL_HOME/profile.yaml")" 'digest does not rewrite operator profile'
exit "$failed"
