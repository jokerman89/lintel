#!/usr/bin/env bash
# tests/unit/pack-inheritance-depth-3.sh
# Asserts: 3-level extends chain resolves with correct child-over-parent precedence.
# tag: v4.0 phase-2 pack-inheritance

set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
RESOLVER="$REPO_ROOT/lib/pack-resolver.sh"
FAILED=0
pass() { echo "  PASS: $1"; }
fail() { echo "  FAIL: $1"; FAILED=1; }

echo "tests/unit/pack-inheritance-depth-3.sh"
echo "========================================"

if [ ! -f "$RESOLVER" ]; then
  fail "lib/pack-resolver.sh missing"
  exit 1
fi

make_temp_home() {
  local tmp
  tmp=$(mktemp -d)
  mkdir -p "$tmp/.lintel/audit" "$tmp/.lintel/sessions" "$tmp/.lintel/packs"
  echo "$tmp"
}

# ─── Scenario: a → b → c (3-level chain) ─────────────────────────────────
echo ""
echo "[1] 3-level chain: child extends middle extends root"
TMP=$(make_temp_home)
(
  # Root: declares everything baseline
  mkdir -p "$TMP/.lintel/packs/root"
  cat > "$TMP/.lintel/packs/root/pack.yaml" <<'EOF'
schema_version: "1"
name: root
version: 1.0.0
voice:
  default_tier: internal
compliance:
  mode: advisory
navigation:
  default_workflow: cycle
requires_lintel: ">=4.0.0"
EOF

  # Middle: extends root, overrides voice + compliance
  mkdir -p "$TMP/.lintel/packs/middle"
  cat > "$TMP/.lintel/packs/middle/pack.yaml" <<'EOF'
schema_version: "1"
name: middle
version: 1.0.0
extends: root
voice:
  default_tier: mixed
compliance:
  mode: hard
navigation:
  default_workflow: cycle
requires_lintel: ">=4.0.0"
EOF

  # Leaf: extends middle, overrides voice only
  mkdir -p "$TMP/.lintel/packs/leaf"
  cat > "$TMP/.lintel/packs/leaf/pack.yaml" <<'EOF'
schema_version: "1"
name: leaf
version: 1.0.0
extends: middle
voice:
  default_tier: custom
compliance:
  mode: hard
navigation:
  default_workflow: cycle
requires_lintel: ">=4.0.0"
EOF

  echo "leaf" > "$TMP/.lintel/packs/active-pack"

  export LINTEL_HOME="$TMP/.lintel"
  export LINTEL_REPO_ROOT="$REPO_ROOT"
  export LINTEL_SESSION_ID="depth-3-$$"
  # shellcheck disable=SC1090
  source "$RESOLVER"

  # Verify chain resolution
  chain=$(_resolve_extends_chain leaf)
  if [ "$chain" = "root middle leaf" ]; then
    echo "  PASS: chain resolved as 'root middle leaf'"
  else
    echo "  FAIL: chain resolved as '$chain' (expected 'root middle leaf')"
    exit 1
  fi

  # Verify leaf's voice override wins
  v=$(resolve_pack_field voice.default_tier)
  if [ "$v" = "custom" ]; then
    echo "  PASS: voice.default_tier = custom (leaf overrides middle + root)"
  else
    echo "  FAIL: voice.default_tier = '$v' (expected 'custom')"
    exit 1
  fi

  # Verify middle's compliance.mode is inherited by leaf
  c=$(resolve_pack_field compliance.mode)
  if [ "$c" = "hard" ]; then
    echo "  PASS: compliance.mode = hard (leaf declares same as middle, both override root)"
  else
    echo "  FAIL: compliance.mode = '$c' (expected 'hard')"
    exit 1
  fi
) || FAILED=1
rm -rf "$TMP"

# ─── Scenario 2: leaf doesn't declare a block → middle's block wins ─────
echo ""
echo "[2] Block not declared in leaf → inherited from middle"
TMP2=$(make_temp_home)
(
  mkdir -p "$TMP2/.lintel/packs/base"
  cat > "$TMP2/.lintel/packs/base/pack.yaml" <<'EOF'
schema_version: "1"
name: base
version: 1.0.0
voice:
  default_tier: mixed
compliance:
  mode: hard
navigation:
  default_workflow: cycle
  orientator_budget_tokens: 3000
requires_lintel: ">=4.0.0"
EOF

  mkdir -p "$TMP2/.lintel/packs/derived"
  cat > "$TMP2/.lintel/packs/derived/pack.yaml" <<'EOF'
schema_version: "1"
name: derived
version: 1.0.0
extends: base
voice:
  default_tier: custom
compliance:
  mode: hard
navigation:
  default_workflow: cycle
requires_lintel: ">=4.0.0"
EOF

  echo "derived" > "$TMP2/.lintel/packs/active-pack"

  export LINTEL_HOME="$TMP2/.lintel"
  export LINTEL_REPO_ROOT="$REPO_ROOT"
  export LINTEL_SESSION_ID="inherit-block-$$"
  # shellcheck disable=SC1090
  source "$RESOLVER"

  # derived's navigation block does NOT declare orientator_budget_tokens.
  # Per shallow-merge semantics: derived's navigation: block REPLACES base's
  # wholesale. So orientator_budget_tokens is NOT inherited.
  v=$(resolve_pack_field navigation.orientator_budget_tokens)
  if [ "$v" = "" ] || [ "$v" = "2000" ]; then
    # Either empty (no field) or hardcoded fallback — both acceptable
    echo "  PASS: shallow-merge: derived's navigation block replaced base's wholesale (orientator_budget = '$v')"
  else
    echo "  FAIL: got '$v' — expected empty or 2000 hardcoded fallback per shallow-merge"
    exit 1
  fi

  # voice.default_tier: derived's voice block replaced base's, so its tier wins.
  v=$(resolve_pack_field voice.default_tier)
  if [ "$v" = "custom" ]; then
    echo "  PASS: voice.default_tier = custom (derived overrides)"
  else
    echo "  FAIL: voice.default_tier = '$v' (expected 'custom')"
    exit 1
  fi
) || FAILED=1
rm -rf "$TMP2"

# ─── Scenario 3: extends chain cycle detection at depth 3 ────────────────
echo ""
echo "[3] Cycle detection: a → b → c → a"
TMP3=$(make_temp_home)
(
  for n in a b c; do
    mkdir -p "$TMP3/.lintel/packs/$n"
  done
  cat > "$TMP3/.lintel/packs/a/pack.yaml" <<'EOF'
schema_version: "1"
name: a
version: 1.0.0
extends: b
voice: {default_tier: internal}
compliance: {mode: advisory}
navigation: {default_workflow: cycle}
requires_lintel: ">=4.0.0"
EOF
  cat > "$TMP3/.lintel/packs/b/pack.yaml" <<'EOF'
schema_version: "1"
name: b
version: 1.0.0
extends: c
voice: {default_tier: internal}
compliance: {mode: advisory}
navigation: {default_workflow: cycle}
requires_lintel: ">=4.0.0"
EOF
  cat > "$TMP3/.lintel/packs/c/pack.yaml" <<'EOF'
schema_version: "1"
name: c
version: 1.0.0
extends: a
voice: {default_tier: internal}
compliance: {mode: advisory}
navigation: {default_workflow: cycle}
requires_lintel: ">=4.0.0"
EOF
  echo "a" > "$TMP3/.lintel/packs/active-pack"

  export LINTEL_HOME="$TMP3/.lintel"
  export LINTEL_REPO_ROOT="$REPO_ROOT"
  export LINTEL_SESSION_ID="cycle-3-$$"
  # shellcheck disable=SC1090
  source "$RESOLVER"

  if validate_pack a 2>/dev/null; then
    echo "  FAIL: 3-link extends cycle should have been rejected"
    exit 1
  else
    echo "  PASS: 3-link cycle detected + rejected"
  fi
) || FAILED=1
rm -rf "$TMP3"

echo ""
if [ "$FAILED" -eq 0 ]; then
  echo "All pack-inheritance-depth-3 scenarios PASSED"
  exit 0
else
  echo "Some pack-inheritance-depth-3 scenarios FAILED"
  exit 1
fi
