#!/usr/bin/env bash
# tests/unit/capture-vault-sink.sh
# Config contract for CAPTURE Step 7b (vault sink): the NEUTRAL _default pack
# ships the sink DISABLED with no path (no operator-personal assumptions in
# the spine — frozen-zone rule). Operators opt in via their own pack or a
# local ~/.lintel/packs/_default override; an enabled override resolves and
# gates correctly. The sink itself is skill-level (LLM-executed); this test
# pins the config surface it depends on.

set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
RESOLVER="$REPO_ROOT/lib/pack-resolver.sh"
FAILED=0

echo "tests/unit/capture-vault-sink.sh"
echo "================================="

make_temp_home() {
  local tmp
  tmp=$(mktemp -d)
  mkdir -p "$tmp/.lintel/audit" "$tmp/.lintel/sessions" "$tmp/.lintel/packs"
  echo "$tmp"
}

echo ""
echo "[1] _default pack: capture.vault_sink_enabled resolves to false (neutral default)"
TMP1=$(make_temp_home)
(
  export LINTEL_HOME="$TMP1/.lintel"
  export LINTEL_REPO_ROOT="$REPO_ROOT"
  export LINTEL_SESSION_ID="test-vault-sink-1-$$"
  source "$RESOLVER"
  v=$(resolve_pack_field capture.vault_sink_enabled)
  if [ "$v" = "false" ]; then
    echo "  PASS: capture.vault_sink_enabled = false"
  else
    echo "  FAIL: got '$v', expected 'false' (neutral pack must not enable the sink)"
    exit 1
  fi
) || FAILED=1
rm -rf "$TMP1"

echo ""
echo "[2] _default pack: pack_field_is_true gates the sink OFF by default"
TMP2=$(make_temp_home)
(
  export LINTEL_HOME="$TMP2/.lintel"
  export LINTEL_REPO_ROOT="$REPO_ROOT"
  export LINTEL_SESSION_ID="test-vault-sink-2-$$"
  source "$RESOLVER"
  if pack_field_is_true capture.vault_sink_enabled; then
    echo "  FAIL: pack_field_is_true returned true on the neutral default"
    exit 1
  else
    echo "  PASS: pack_field_is_true gates the sink off"
  fi
) || FAILED=1
rm -rf "$TMP2"

echo ""
echo "[3] operator override pack: enabled sink resolves enabled + path (comment stripped)"
TMP3=$(make_temp_home)
(
  export LINTEL_HOME="$TMP3/.lintel"
  export LINTEL_REPO_ROOT="$REPO_ROOT"
  export LINTEL_SESSION_ID="test-vault-sink-3-$$"
  # Local pack override (resolver checks ~/.lintel/packs/<name>/ first)
  mkdir -p "$TMP3/.lintel/packs/vault-on"
  cat > "$TMP3/.lintel/packs/vault-on/pack.yaml" <<'EOF'
name: vault-on
version: 1.0.0
extends: _default
voice:
  default_tier: internal
compliance:
  mode: off
navigation:
  default_workflow: cycle
capture:
  vault_sink_enabled: true   # operator opt-in
  vault_sink_path: ../my-vault/50-sessions  # relative to repo root
EOF
  printf 'vault-on' > "$TMP3/.lintel/packs/active-pack"
  source "$RESOLVER"
  v=$(resolve_pack_field capture.vault_sink_enabled)
  p=$(resolve_pack_field capture.vault_sink_path)
  if [ "$v" = "true" ] && [ "$p" = "../my-vault/50-sessions" ] && pack_field_is_true capture.vault_sink_enabled; then
    echo "  PASS: override resolves enabled=true path=../my-vault/50-sessions"
  else
    echo "  FAIL: got enabled='$v' path='$p'"
    exit 1
  fi
) || FAILED=1
rm -rf "$TMP3"

echo ""
if [ "$FAILED" -eq 0 ]; then
  echo "ALL PASS"
else
  echo "FAILURES present"
  exit 1
fi
