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
cp "$ROOT/lib/pack-resolver.sh" "$ROOT/lib/paths.sh" "$installed/lib/"
cp "$ROOT/bin/_audit.sh" "$installed/bin/"
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

# Execute the pack-create template and write steps from the skill itself. A blank
# pack in an ordinary consumer repo must find _default in the installed bundle.
extract_step() {
  awk -v step="$1" '
    $0 ~ "^### Step "step" " { selected=1; next }
    selected && /^### / { exit }
    selected && /^```bash/ { block=1; next }
    block && /^```/ { exit }
    block { print }
  ' "$ROOT/skills/pack-create/SKILL.md"
}
extends=""; from_pack=""; name=blank; scope=repo; target_dir="$target_repo/packs"
REPO_PACKS="$target_dir"; HOME_PACKS="$LINTEL_PACKS_DIR"
source <(extract_step 3)
source <(extract_step 5)
source <(extract_step 6)
echo 'PASS: blank pack creation uses the installed neutral template'

extends=base; name=team
source <(extract_step 3)
source <(extract_step 4)
source <(extract_step 5)
source <(extract_step 6)
printf 'team\n' > "$LINTEL_ACTIVE_PACK_FILE"
clear_pack_cache
[ "$(resolve_pack_field compliance.mode)" = hard ]
[ "$(resolve_pack_field compliance.hooks)" = '[evidence]' ]
echo 'PASS: consumer child created by the skill retains inherited enterprise gates'

mkdir -p "$LINTEL_PACKS_DIR/base"
cp "$target_repo/packs/base/pack.yaml" "$LINTEL_PACKS_DIR/base/pack.yaml"
[ "$(_pack_dir base)" = "$LINTEL_PACKS_DIR/base" ]
echo 'PASS: explicit configured pack store precedes target and bundled packs'
