#!/usr/bin/env bash
# tests/unit/capture-vault-sink.sh
# Config contract for CAPTURE Step 7b (vault sink): the _default pack ships
# capture.vault_sink_enabled / capture.vault_sink_path and both resolve
# through resolve_pack_field. The sink itself is skill-level (LLM-executed);
# this test pins the config surface it depends on.

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
echo "[1] _default pack: capture.vault_sink_enabled resolves to true"
TMP1=$(make_temp_home)
(
  export LINTEL_HOME="$TMP1/.lintel"
  export LINTEL_REPO_ROOT="$REPO_ROOT"
  export LINTEL_SESSION_ID="test-vault-sink-1-$$"
  source "$RESOLVER"
  v=$(resolve_pack_field capture.vault_sink_enabled)
  if [ "$v" = "true" ]; then
    echo "  PASS: capture.vault_sink_enabled = true"
  else
    echo "  FAIL: got '$v', expected 'true'"
    exit 1
  fi
) || FAILED=1
rm -rf "$TMP1"

echo ""
echo "[2] _default pack: capture.vault_sink_path resolves with trailing comment stripped"
TMP2=$(make_temp_home)
(
  export LINTEL_HOME="$TMP2/.lintel"
  export LINTEL_REPO_ROOT="$REPO_ROOT"
  export LINTEL_SESSION_ID="test-vault-sink-2-$$"
  source "$RESOLVER"
  v=$(resolve_pack_field capture.vault_sink_path)
  if [ "$v" = "../jokerman-vault/50-sessions" ]; then
    echo "  PASS: capture.vault_sink_path = ../jokerman-vault/50-sessions"
  else
    echo "  FAIL: got '$v', expected '../jokerman-vault/50-sessions'"
    exit 1
  fi
) || FAILED=1
rm -rf "$TMP2"

echo ""
echo "[3] pack_field_is_true gates the sink"
TMP3=$(make_temp_home)
(
  export LINTEL_HOME="$TMP3/.lintel"
  export LINTEL_REPO_ROOT="$REPO_ROOT"
  export LINTEL_SESSION_ID="test-vault-sink-3-$$"
  source "$RESOLVER"
  if pack_field_is_true capture.vault_sink_enabled; then
    echo "  PASS: pack_field_is_true capture.vault_sink_enabled"
  else
    echo "  FAIL: pack_field_is_true returned false"
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
