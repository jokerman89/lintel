#!/usr/bin/env bash
# component: pack-source-target-resolution-test
# implements: ADR-0018, ADR-0024
# intent: docs/concepts/pack-resolver.md
# constraints: none; installed source, target, profile and audits use temporary fixtures
# last_intent_review: 2026-09-08
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
test_parent="$(cd "${TMPDIR:-/tmp}" && pwd -P)"
test_dir="$(mktemp -d "$test_parent/lintel-pack-roots.XXXXXX")"
cleanup() {
  case "$test_dir" in "$test_parent"/lintel-pack-roots.*)
    [ "$(cd "$test_dir" && pwd -P)" = "$test_dir" ] && rm -rf -- "$test_dir" ;;
  esac
}
trap cleanup EXIT
installed="$test_dir/installed source"
target_repo="$test_dir/consumer"
mkdir -p "$installed/lib" "$installed/bin" "$installed/packs" "$target_repo/packs/base"
cp "$ROOT/lib/pack-resolver.sh" "$ROOT/lib/paths.sh" "$ROOT/lib/profile_context.py" "$ROOT/lib/context_safety.py" \
  "$ROOT/lib/profile-context-schema.json" "$ROOT/lib/pack-schema.yaml" "$ROOT/lib/copilot-env.sh" "$installed/lib/"
cp "$ROOT/bin/_audit.sh" "$ROOT/bin/li-lifecycle" "$ROOT/bin/li-lifecycle.py" "$installed/bin/"
cp -R "$ROOT/packs/_default" "$installed/packs/"
export LINTEL_SOURCE_ROOT="$installed" LINTEL_REPO_ROOT="$target_repo"
export LINTEL_HOME="$test_dir/operator" LINTEL_PACKS_DIR="$test_dir/operator/packs"
export LINTEL_ACTIVE_PACK_FILE="$LINTEL_PACKS_DIR/active-pack"
export LINTEL_AUDIT_DIR="$test_dir/audit" LINTEL_SESSION_ID="pack-roots-$$"
mkdir -p "$LINTEL_PACKS_DIR"
cat > "$target_repo/packs/base/pack.yaml" <<'YAML'
name: base
version: 1.0.0
voice: {default_tier: internal}
compliance: {mode: hard, hooks: [evidence]}
navigation: {default_workflow: cycle}
YAML
source "$installed/lib/pack-resolver.sh"
[ "$(resolve_pack_field voice.enforce)" = none ]
[ "$(_pack_dir _default)" = "$installed/packs/_default" ]
[ "$(_pack_dir base)" = "$target_repo/packs/base" ]
echo 'PASS: installed defaults and consumer packs resolve with distinct source/target roots'

# Execute the skill's real dispatcher. A blank pack in an ordinary consumer must
# find _default in the installed bundle, not maintain a second copy/write recipe.
extract_step() {
  awk '
    /^### 2\. Dispatch/ { selected=1; next }
    selected && /^### / { exit }
    selected && /^```bash/ { block=1; next }
    block && /^```/ { exit }
    block { print }
  ' "$ROOT/skills/pack-create/SKILL.md"
}
parent=""; template_pack=""; name=blank; scope=repo; target_dir="$target_repo/packs"
dispatcher="$(extract_step)"
[ -n "$dispatcher" ] || { echo 'FAIL: pack-create dispatcher is missing'; exit 1; }
printf '%s\n' "$dispatcher" > "$test_dir/create.sh"
source "$test_dir/create.sh"
validate_pack blank
echo 'PASS: blank pack creation uses the installed neutral template'

parent=base; name=team
source "$test_dir/create.sh"
validate_pack team
bash "$installed/bin/li-lifecycle" pack-switch team --reason 'synthetic consumer inheritance check'
[ "$(resolve_pack_field compliance.mode)" = hard ]
[ "$(resolve_pack_field compliance.hooks)" = '[evidence]' ]
echo 'PASS: consumer child created by the skill retains inherited enterprise gates'

mkdir -p "$LINTEL_PACKS_DIR/base"
cp "$target_repo/packs/base/pack.yaml" "$LINTEL_PACKS_DIR/base/pack.yaml"
[ "$(_pack_dir base)" = "$LINTEL_PACKS_DIR/base" ]
echo 'PASS: explicit configured pack store precedes target and bundled packs'
