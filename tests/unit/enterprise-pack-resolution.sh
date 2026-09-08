#!/usr/bin/env bash
# component: enterprise-pack-resolution-test
# implements: ADR-0018
# intent: docs/concepts/pack-resolver.md
# constraints: none; fixtures, cache and audit are isolated from the operator home
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
export LINTEL_AUDIT_DIR="$review_tmp/audit" LINTEL_SESSION_ID="enterprise-unit-$$"
mkdir -p "$LINTEL_PACKS_DIR/base" "$LINTEL_PACKS_DIR/team"
source "$REPO_ROOT/lib/pack-resolver.sh"
failed=0
assert_eq() {
  if [ "$1" = "$2" ]; then printf 'PASS: %s\n' "$3";
  else printf 'FAIL: %s expected=<%s> actual=<%s>\n' "$3" "$1" "$2"; failed=1; fi
}
reject() {
  if validate_pack "$1" 2>/dev/null; then printf 'FAIL: accepted %s\n' "$2"; failed=1;
  else printf 'PASS: rejected %s\n' "$2"; fi
}
cat > "$LINTEL_PACKS_DIR/base/pack.yaml" <<'YAML'
name: base
version: "1.0.0"
description: An enterprise's rules
voice: {default_tier: 'external', corpus: "voice/customer # guide.md"}
compliance:
  mode: "hard" # enforce the pack gates
  hooks:
    - "audit-required"
    - data-residency
navigation:
  default_workflow: delivery
  high_risk_workflows: ['cycle', "plan", ship]
brief_forge_handoffs:
  on_subagent_spawn:
    enabled: true
    evaluators: [security, stale]
brand:
  name: 'Acme''s # brand'
  copy_tone: "Say \"hello\""
policy-set: parent
YAML
cat > "$LINTEL_PACKS_DIR/team/pack.yaml" <<'YAML'
name: team
version: 1.0.0
extends: 'base' # explicit enterprise inheritance
voice: {default_tier: internal}
brand: {name: Team}
policy-set : child
YAML
printf 'tab-policy\t: parent\n' >> "$LINTEL_PACKS_DIR/base/pack.yaml"
printf 'tab-policy\t: child\n' >> "$LINTEL_PACKS_DIR/team/pack.yaml"
printf 'base\n' > "$LINTEL_ACTIVE_PACK_FILE"
validate_pack base || failed=1
assert_eq hard "$(resolve_pack_field compliance.mode)" 'quoted scalar and trailing comment'
assert_eq '[audit-required, data-residency]' "$(resolve_pack_field compliance.hooks)" 'block list is usable by gate consumers'
assert_eq '[cycle, plan, ship]' "$(resolve_pack_field navigation.high_risk_workflows)" 'flow list uses the same contract'
assert_eq 'voice/customer # guide.md' "$(resolve_pack_field voice.corpus)" 'quoted spaces and hash preserved'
assert_eq "Acme's # brand" "$(resolve_pack_field brand.name)" 'single quote escaping'
assert_eq 'Say "hello"' "$(resolve_pack_field brand.copy_tone)" 'double quote escaping'
assert_eq true "$(resolve_pack_field brief_forge_handoffs.on_subagent_spawn.enabled)" 'nested handoff boolean'
assert_eq '[security, stale]' "$(resolve_pack_field brief_forge_handoffs.on_subagent_spawn.evaluators)" 'nested handoff list'
assert_eq 2000 "$(resolve_pack_field navigation.orientator_budget_tokens)" 'missing optional field uses neutral fallback'
assert_eq '' "$(resolve_pack_field undeclared.field)" 'unknown optional field stays empty'

cat > "$review_tmp/indentless.yaml" <<'YAML'
compliance:
  mode: hard
  hooks:
  - audit-required
  - data-residency
navigation:
  high_risk_workflows:
  - cycle
  default_workflow: delivery
YAML
assert_eq '[audit-required, data-residency]' "$(_pack_yaml_field "$review_tmp/indentless.yaml" compliance.hooks)" 'indentationless YAML sequence keeps its field owner'
assert_eq '[cycle]' "$(_pack_yaml_field "$review_tmp/indentless.yaml" navigation.high_risk_workflows)" 'sibling list starts a fresh accumulator'
assert_eq delivery "$(_pack_yaml_field "$review_tmp/indentless.yaml" navigation.default_workflow)" 'mapping resumes after indentationless sequence'

validate_pack team || failed=1
printf 'team\n' > "$LINTEL_ACTIVE_PACK_FILE"
clear_pack_cache
assert_eq hard "$(resolve_pack_field compliance.mode)" 'minimal child retains parent compliance'
assert_eq '[audit-required, data-residency]' "$(resolve_pack_field compliance.hooks)" 'minimal child retains parent gates'
assert_eq internal "$(resolve_pack_field voice.default_tier)" 'explicit child block overrides parent'
assert_eq child "$(resolve_pack_field policy-set)" 'merge accepts the same plain keys and colon spacing as validation'
assert_eq child "$(resolve_pack_field tab-policy)" 'merge accepts tab separation before a colon consistently'
assert_eq null "$(resolve_pack_field voice.corpus)" 'child voice replaces whole block; corpus falls back neutral'
cat >> "$LINTEL_PACKS_DIR/team/pack.yaml" <<'YAML'
compliance: {mode: advisory, hooks: []}
YAML
clear_pack_cache
assert_eq '[]' "$(resolve_pack_field compliance.hooks)" 'explicit empty list stays empty'
cp "$LINTEL_PACKS_DIR/team/pack.yaml" "$review_tmp/valid-team.yaml"
assert_eq team "$(get_loaded_pack)" 'cache is primed before malformed edit'
printf 'broken: [unterminated\n' >> "$LINTEL_PACKS_DIR/team/pack.yaml"
assert_eq _default "$(get_loaded_pack)" 'malformed edit invalidates an already primed cache'
cp "$review_tmp/valid-team.yaml" "$LINTEL_PACKS_DIR/team/pack.yaml"
clear_pack_cache
assert_eq team "$(get_loaded_pack)" 'valid team can be loaded again'
printf 'name: team\nversion: 1.0.0\nextends: absent\n' > "$LINTEL_PACKS_DIR/team/pack.yaml"
assert_eq _default "$(get_loaded_pack)" 'missing edited ancestor invalidates an already primed cache'
cp "$review_tmp/valid-team.yaml" "$LINTEL_PACKS_DIR/team/pack.yaml"
clear_pack_cache
assert_eq team "$(get_loaded_pack)" 'cache is primed before pointer switch'

mkdir -p "$LINTEL_PACKS_DIR/bad" "$LINTEL_PACKS_DIR/missing" "$LINTEL_PACKS_DIR/cycle"
cat > "$LINTEL_PACKS_DIR/bad/pack.yaml" <<'YAML'
name: bad
version: 1.0.0
extends: base
compliance: {hooks: [gate]}
YAML
reject bad 'child replacement missing required compliance.mode'
printf 'name: missing\nversion: 1.0.0\nextends: absent\n' > "$LINTEL_PACKS_DIR/missing/pack.yaml"
reject missing 'missing parent'
printf 'name: cycle\nversion: 1.0.0\nextends: cycle\n' > "$LINTEL_PACKS_DIR/cycle/pack.yaml"
reject cycle 'extends cycle'
for n in {0..11}; do
  mkdir -p "$LINTEL_PACKS_DIR/depth-$n"
  printf 'name: depth-%s\nversion: 1.0.0\nextends: depth-%s\n' "$n" "$((n+1))" > "$LINTEL_PACKS_DIR/depth-$n/pack.yaml"
done
reject depth-0 'ancestry beyond depth ten'
cp "$LINTEL_PACKS_DIR/base/pack.yaml" "$LINTEL_PACKS_DIR/bad/pack.yaml"
printf 'broken: [unterminated\n' >> "$LINTEL_PACKS_DIR/bad/pack.yaml"
reject bad 'malformed flow collection'
cp "$LINTEL_PACKS_DIR/base/pack.yaml" "$LINTEL_PACKS_DIR/bad/pack.yaml"
printf 'custom: &anchor value\n' >> "$LINTEL_PACKS_DIR/bad/pack.yaml"
reject bad 'unsupported anchor syntax'
printf 'name: bad\nversion: 1.0.0\nextends: base\n"compliance": {mode: hard}\n' > "$LINTEL_PACKS_DIR/bad/pack.yaml"
reject bad 'quoted block key cannot disagree with the inheritance merger'
printf 'name: bad\nversion: 1.0.0\nextends: base\ncompliance: {"mode": hard}\n' > "$LINTEL_PACKS_DIR/bad/pack.yaml"
reject bad 'quoted flow key is outside the same plain-key contract'
printf ' name: bad\n version: 1.0.0\n extends: base\n' > "$LINTEL_PACKS_DIR/bad/pack.yaml"
reject bad 'indented root cannot disagree with the inheritance merger'
cp "$LINTEL_PACKS_DIR/base/pack.yaml" "$LINTEL_PACKS_DIR/bad/pack.yaml"
printf 'version: 9.0.0\n' >> "$LINTEL_PACKS_DIR/bad/pack.yaml"
reject bad 'duplicate manifest key'
printf 'bad\n' > "$LINTEL_ACTIVE_PACK_FILE"
assert_eq team "$(get_loaded_pack)" 'invalid pointer switch does not replace the current cycle cache'
clear_pack_cache
assert_eq _default "$(get_loaded_pack)" 'invalid active pack keeps documented neutral fallback'
assert_eq advisory "$(resolve_pack_field compliance.mode)" 'fallback mode and identity agree'
exit "$failed"
