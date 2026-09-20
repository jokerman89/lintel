#!/usr/bin/env bash
set -uo pipefail
root="$PWD"
probe="$root/.claude/runtime/universal-probes"
mkdir -p "$probe/packs/company" "$probe/packs/other" "$probe/home" "$probe/target/.claude"
export LINTEL_HOME="$probe/home" LINTEL_SOURCE_ROOT="$root" LINTEL_REPO_ROOT="$probe/target"
export LINTEL_PACKS_DIR="$probe/packs" LINTEL_ACTIVE_PACK_FILE="$probe/active-pack" LINTEL_AUDIT_DIR="$probe/audit"
unset CLAUDE_SESSION_ID LINTEL_SESSION_ID PACK_CACHE_FILE
printf 'layout_version: 5\n' > "$probe/target/.claude/lintel-layout.yaml"
cat > "$probe/packs/company/pack.yaml" <<'EOF'
name: company
version: 1.0.0
voice:
  default_tier: internal
compliance:
  mode: hard
navigation:
  default_workflow: cycle
EOF
cat > "$probe/packs/other/pack.yaml" <<'EOF'
name: other
version: 1.0.0
voice:
  default_tier: internal
compliance:
  mode: advisory
navigation:
  default_workflow: cycle
EOF
cat > "$probe/read-pack.sh" <<'EOF'
source "$LINTEL_SOURCE_ROOT/lib/pack-resolver.sh"
printf 'loaded=%s mode=%s session=%s\n' "$(get_loaded_pack)" "$(resolve_pack_field compliance.mode)" "$LINTEL_SESSION_ID"
EOF
printf 'PACK_SESSION_WITHOUT_HOST_ID\n'
printf 'company\n' > "$probe/active-pack"
bash "$probe/read-pack.sh"
printf 'other\n' > "$probe/active-pack"
bash "$probe/read-pack.sh"

printf 'CYCLE_MARKER_ORDER\n'
source "$root/lib/state.sh"
state_append SENSE DONE next=SCOPE
state_append SCOPE DONE next=DEFINE
state_append CYCLE STARTING cycle_id=audit-fixture cycle_mode=internal-tool
state_cycle_segment | grep '^phase:'

printf 'ROUTER_READ_ONLY_INTENT\n'
source "$root/lib/orientator-routing.sh"
for text in 'review the fix without changing code' 'research deployment options only' 'review the release plan'; do
  intent=$(classify_intent "$text")
  printf 'request=%s intent=%s workflow=%s confidence=%s\n' "$text" "$intent" "$(match_workflow "$intent" cycle)" "$(score_confidence "$intent" cycle)"
done

printf 'NO_VALID_PACK_FALLBACK\n'
mkdir -p "$probe/bad-source/bin" "$probe/bad-packs/_default"
cp "$root/bin/_audit.sh" "$probe/bad-source/bin/_audit.sh"
printf 'bad yaml\n' > "$probe/bad-packs/_default/pack.yaml"
printf '_default\n' > "$probe/active-pack"
export LINTEL_SOURCE_ROOT="$probe/bad-source" LINTEL_PACKS_DIR="$probe/bad-packs" LINTEL_SESSION_ID=audit-invalid-default
source "$root/lib/pack-resolver.sh"
value=$(resolve_pack_field compliance.mode)
rc=$?
printf 'resolved_mode=%s exit=%s\n' "$value" "$rc"
