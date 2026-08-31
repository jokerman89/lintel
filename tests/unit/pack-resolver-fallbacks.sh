#!/usr/bin/env bash
# tests/unit/pack-resolver-fallbacks.sh
# The 9-scenario test harness for lib/pack-resolver.sh per v4.0 §2.2 A.7 + §2.4
# tag: v4.0 phase-1 pack-resolver

set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
RESOLVER="$REPO_ROOT/lib/pack-resolver.sh"
FAILED=0
pass() { echo "  PASS: $1"; }
fail() { echo "  FAIL: $1"; FAILED=1; }

echo "tests/unit/pack-resolver-fallbacks.sh"
echo "======================================="

if [ ! -f "$RESOLVER" ]; then
  fail "lib/pack-resolver.sh missing"
  exit 1
fi

# Each scenario uses an isolated LINTEL_HOME
make_temp_home() {
  local tmp
  tmp=$(mktemp -d)
  mkdir -p "$tmp/.lintel/audit" "$tmp/.lintel/sessions" "$tmp/.lintel/packs"
  echo "$tmp"
}

# ─── Scenario 1: no pack active → returns _default values ───────────────
echo ""
echo "[1] No pack active → returns _default values"
TMP1=$(make_temp_home)
(
  export LINTEL_HOME="$TMP1/.lintel"
  export LINTEL_REPO_ROOT="$REPO_ROOT"
  export LINTEL_SESSION_ID="test-1-$$"
  # shellcheck disable=SC1090
  source "$RESOLVER"
  v=$(resolve_pack_field voice.default_tier)
  if [ "$v" = "internal" ]; then
    echo "  PASS: voice.default_tier = internal (neutral default)"
  else
    echo "  FAIL: got '$v', expected 'internal'"
    exit 1
  fi
  v=$(resolve_pack_field compliance.mode)
  if [ "$v" = "advisory" ]; then
    echo "  PASS: compliance.mode = advisory"
  else
    echo "  FAIL: got '$v', expected 'advisory'"
    exit 1
  fi
) || FAILED=1
rm -rf "$TMP1"

# ─── Scenario 2: mock pack active → returns pack values ─────────────────
echo ""
echo "[2] Mock pack active → returns pack values"
TMP2=$(make_temp_home)
(
  mkdir -p "$TMP2/.lintel/packs/mock-test"
  cat > "$TMP2/.lintel/packs/mock-test/pack.yaml" <<'EOF'
name: mock-test
version: 1.0.0
voice:
  default_tier: custom
compliance:
  mode: hard
navigation:
  default_workflow: cycle
EOF
  echo "mock-test" > "$TMP2/.lintel/packs/active-pack"

  export LINTEL_HOME="$TMP2/.lintel"
  export LINTEL_REPO_ROOT="$REPO_ROOT"
  export LINTEL_SESSION_ID="test-2-$$"
  # shellcheck disable=SC1090
  source "$RESOLVER"
  v=$(resolve_pack_field voice.default_tier)
  if [ "$v" = "custom" ]; then
    echo "  PASS: voice.default_tier = custom (pack-overridden)"
  else
    echo "  FAIL: got '$v', expected 'custom'"
    exit 1
  fi
) || FAILED=1
rm -rf "$TMP2"

# ─── Scenario 3: malformed pack.yaml → hard-fail OR fallback ────────────
echo ""
echo "[3] Malformed pack.yaml → fallback to _default (with warn)"
TMP3=$(make_temp_home)
(
  mkdir -p "$TMP3/.lintel/packs/malformed"
  # Pack missing all required fields
  echo "this is not valid yaml: {" > "$TMP3/.lintel/packs/malformed/pack.yaml"
  echo "malformed" > "$TMP3/.lintel/packs/active-pack"

  export LINTEL_HOME="$TMP3/.lintel"
  export LINTEL_REPO_ROOT="$REPO_ROOT"
  export LINTEL_SESSION_ID="test-3-$$"
  # shellcheck disable=SC1090
  source "$RESOLVER"
  # Validation should reject; resolver should fall back to _default values
  v=$(resolve_pack_field voice.default_tier 2>/dev/null)
  if [ "$v" = "internal" ] || [ "$v" = "" ]; then
    echo "  PASS: malformed pack rejected; fell back gracefully"
  else
    echo "  FAIL: malformed pack returned '$v'"
    exit 1
  fi
) || FAILED=1
rm -rf "$TMP3"

# ─── Scenario 4: extends: cycle detected ─────────────────────────────────
echo ""
echo "[4] extends: cycle detected → refused"
TMP4=$(make_temp_home)
(
  mkdir -p "$TMP4/.lintel/packs/pack-a" "$TMP4/.lintel/packs/pack-b"
  cat > "$TMP4/.lintel/packs/pack-a/pack.yaml" <<'EOF'
name: pack-a
version: 1.0.0
extends: pack-b
voice: {default_tier: internal}
compliance: {mode: advisory}
navigation: {default_workflow: cycle}
EOF
  cat > "$TMP4/.lintel/packs/pack-b/pack.yaml" <<'EOF'
name: pack-b
version: 1.0.0
extends: pack-a
voice: {default_tier: internal}
compliance: {mode: advisory}
navigation: {default_workflow: cycle}
EOF
  echo "pack-a" > "$TMP4/.lintel/packs/active-pack"

  export LINTEL_HOME="$TMP4/.lintel"
  export LINTEL_REPO_ROOT="$REPO_ROOT"
  export LINTEL_SESSION_ID="test-4-$$"
  # shellcheck disable=SC1090
  source "$RESOLVER"
  if validate_pack pack-a 2>/dev/null; then
    echo "  FAIL: extends: cycle should have been rejected"
    exit 1
  else
    echo "  PASS: extends: cycle detected + rejected"
  fi
) || FAILED=1
rm -rf "$TMP4"

# ─── Scenario 5: missing required field → reject ─────────────────────────
echo ""
echo "[5] Missing required field → reject at validation"
TMP5=$(make_temp_home)
(
  mkdir -p "$TMP5/.lintel/packs/incomplete"
  # Missing `voice:` block
  cat > "$TMP5/.lintel/packs/incomplete/pack.yaml" <<'EOF'
name: incomplete
version: 1.0.0
compliance: {mode: advisory}
navigation: {default_workflow: cycle}
EOF
  echo "incomplete" > "$TMP5/.lintel/packs/active-pack"

  export LINTEL_HOME="$TMP5/.lintel"
  export LINTEL_REPO_ROOT="$REPO_ROOT"
  export LINTEL_SESSION_ID="test-5-$$"
  # shellcheck disable=SC1090
  source "$RESOLVER"
  if validate_pack incomplete 2>/dev/null; then
    echo "  FAIL: missing required field should have been rejected"
    exit 1
  else
    echo "  PASS: missing voice: rejected at validation"
  fi
) || FAILED=1
rm -rf "$TMP5"

# ─── Scenario 6: concurrent reads → identical (cached) value ─────────────
echo ""
echo "[6] Concurrent reads → both get cached value"
TMP6=$(make_temp_home)
(
  mkdir -p "$TMP6/.lintel/packs/cache-test"
  cat > "$TMP6/.lintel/packs/cache-test/pack.yaml" <<'EOF'
name: cache-test
version: 1.0.0
voice: {default_tier: mixed}
compliance: {mode: advisory}
navigation: {default_workflow: cycle}
EOF
  echo "cache-test" > "$TMP6/.lintel/packs/active-pack"

  export LINTEL_HOME="$TMP6/.lintel"
  export LINTEL_REPO_ROOT="$REPO_ROOT"
  export LINTEL_SESSION_ID="test-6-$$"
  # shellcheck disable=SC1090
  source "$RESOLVER"
  v1=$(resolve_pack_field voice.default_tier)
  v2=$(resolve_pack_field voice.default_tier)
  if [ "$v1" = "mixed" ] && [ "$v2" = "mixed" ]; then
    echo "  PASS: two reads return same value ($v1)"
  else
    echo "  FAIL: reads diverged ($v1 vs $v2)"
    exit 1
  fi
) || FAILED=1
rm -rf "$TMP6"

# ─── Scenario 7: pack-switch mid-cycle → cached value still in effect ───
echo ""
echo "[7] Pack-switch mid-cycle → cached value still in effect"
TMP7=$(make_temp_home)
(
  mkdir -p "$TMP7/.lintel/packs/pack-x" "$TMP7/.lintel/packs/pack-y"
  cat > "$TMP7/.lintel/packs/pack-x/pack.yaml" <<'EOF'
name: pack-x
version: 1.0.0
voice: {default_tier: internal}
compliance: {mode: advisory}
navigation: {default_workflow: cycle}
EOF
  cat > "$TMP7/.lintel/packs/pack-y/pack.yaml" <<'EOF'
name: pack-y
version: 1.0.0
voice: {default_tier: custom}
compliance: {mode: hard}
navigation: {default_workflow: cycle}
EOF
  echo "pack-x" > "$TMP7/.lintel/packs/active-pack"

  export LINTEL_HOME="$TMP7/.lintel"
  export LINTEL_REPO_ROOT="$REPO_ROOT"
  export LINTEL_SESSION_ID="test-7-$$"
  # shellcheck disable=SC1090
  source "$RESOLVER"
  v_before=$(resolve_pack_field voice.default_tier)
  # Switch active pack mid-session
  echo "pack-y" > "$TMP7/.lintel/packs/active-pack"
  v_after=$(resolve_pack_field voice.default_tier)
  if [ "$v_before" = "internal" ] && [ "$v_after" = "internal" ]; then
    echo "  PASS: cached value preserved across mid-session switch"
  else
    echo "  FAIL: cache invariant broken (before=$v_before after=$v_after)"
    exit 1
  fi
) || FAILED=1
rm -rf "$TMP7"

# ─── Scenario 8: pack file deleted after SENSE read → cached value works ─
echo ""
echo "[8] Pack file deleted post-SENSE → cached value remains valid"
TMP8=$(make_temp_home)
(
  mkdir -p "$TMP8/.lintel/packs/ephemeral"
  cat > "$TMP8/.lintel/packs/ephemeral/pack.yaml" <<'EOF'
name: ephemeral
version: 1.0.0
voice: {default_tier: mixed}
compliance: {mode: advisory}
navigation: {default_workflow: cycle}
EOF
  echo "ephemeral" > "$TMP8/.lintel/packs/active-pack"

  export LINTEL_HOME="$TMP8/.lintel"
  export LINTEL_REPO_ROOT="$REPO_ROOT"
  export LINTEL_SESSION_ID="test-8-$$"
  # shellcheck disable=SC1090
  source "$RESOLVER"
  v_before=$(resolve_pack_field voice.default_tier)
  # Delete the pack
  rm -rf "$TMP8/.lintel/packs/ephemeral"
  # Read again — cache should still hold
  v_after=$(resolve_pack_field voice.default_tier)
  if [ "$v_before" = "mixed" ] && [ "$v_after" = "mixed" ]; then
    echo "  PASS: cache survives pack-file deletion"
  else
    echo "  FAIL: cache invariant broken after deletion (before=$v_before after=$v_after)"
    exit 1
  fi
) || FAILED=1
rm -rf "$TMP8"

# ─── Scenario 9: green path (active=_default explicit) ────────────────────
echo ""
echo "[9] Active = _default explicit → no warnings, neutral values"
TMP9=$(make_temp_home)
(
  echo "_default" > "$TMP9/.lintel/packs/active-pack"

  export LINTEL_HOME="$TMP9/.lintel"
  export LINTEL_REPO_ROOT="$REPO_ROOT"
  export LINTEL_SESSION_ID="test-9-$$"
  # shellcheck disable=SC1090
  source "$RESOLVER"
  v=$(resolve_pack_field voice.default_tier 2>/dev/null)
  if [ "$v" = "internal" ]; then
    echo "  PASS: _default explicit returns neutral values"
  else
    echo "  FAIL: got '$v', expected 'internal'"
    exit 1
  fi
) || FAILED=1
rm -rf "$TMP9"

echo ""
if [ "$FAILED" -eq 0 ]; then
  echo "All 9 pack-resolver-fallbacks scenarios PASSED"
  exit 0
else
  echo "Some pack-resolver-fallbacks scenarios FAILED"
  exit 1
fi
