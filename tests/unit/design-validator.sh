#!/usr/bin/env bash
# tests/unit/design-validator.sh
# Behavior: validate_design.py gates objectively bad HTML (exit 1) and passes
# clean HTML (exit 0). Positive AND negative assertions per L-012 — the gate
# must block the bad thing and must not flag the good thing.
# tag: design-dna validator gate behavior
set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"
FAILED=0
pass(){ echo "  PASS: $1"; }
fail(){ echo "  FAIL: $1"; FAILED=1; }
echo "tests/unit/design-validator.sh"
echo "=============================="

if ! command -v python3 >/dev/null 2>&1; then
  echo "  SKIP: python3 not available — degradation path is the review checklist"
  echo ""
  echo "design-validator: ALL PASS (skipped)"
  exit 0
fi

V="skills/design-dna/scripts/validate_design.py"
P="skills/design-dna/profiles/anthropic-default.yaml"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

cat > "$TMP/bad.html" <<'EOF'
<html><head><meta name="viewport" content="width=device-width, user-scalable=no"></head>
<body><style>button{outline:none;transition: all .2s;font-size:10px;color:#a855f7}</style>
<button class="icon">🚀</button></body></html>
EOF

# Good HTML uses design tokens (var()) — the three-layer discipline (ADR-0017).
cat > "$TMP/good.html" <<'EOF'
<html><head><meta name="viewport" content="width=device-width, initial-scale=1"></head>
<body><style>@media (prefers-reduced-motion: reduce){*{animation:none}}
:root{--color-fg:#141413;--color-bg:#faf9f5;--color-primary:#d97757;--font-body:Lora,serif}
button:focus-visible{outline:2px solid var(--color-primary)}
body{color:var(--color-fg);background:var(--color-bg);font-family:var(--font-body)}</style>
<button>Save changes</button></body></html>
EOF

# 1. Bad HTML blocks
out=$(python3 "$V" "$TMP/bad.html" --profile "$P" 2>&1); rc=$?
[ $rc -eq 1 ] && pass "bad HTML exits 1 (gate closed)" || fail "bad HTML exit $rc — gate is open"
echo "$out" | grep -q "zoom disabled" && pass "catches zoom-disable" || fail "missed zoom-disable"
echo "$out" | grep -q "focus outline removed" && pass "catches killed focus" || fail "missed killed focus"
echo "$out" | grep -q "emoji used as icon" && pass "catches emoji-as-icon" || fail "missed emoji-as-icon"
echo "$out" | grep -q "outside the active profile palette" && pass "catches off-palette hex" || fail "missed off-palette hex"

# 2. Good HTML passes clean
out=$(python3 "$V" "$TMP/good.html" --profile "$P" 2>&1); rc=$?
[ $rc -eq 0 ] && pass "good HTML exits 0" || fail "good HTML exit $rc — false positive"
echo "$out" | grep -q "0 error(s), 0 warning(s)" && pass "good HTML fully clean" || fail "good HTML has findings: $out"

# 3. Negative control: missing file is an error, not a silent pass
python3 "$V" "$TMP/nope.html" >/dev/null 2>&1; rc=$?
[ $rc -eq 1 ] && pass "missing file exits 1" || fail "missing file exit $rc"

# 4. No masking: a benign content emoji must NOT hide a later icon emoji (review P1)
cat > "$TMP/mask.html" <<'EOF'
<html><head><meta name="viewport" content="width=device-width"></head>
<body><p>We launched 🎉 today</p><button class="icon">🔍</button></body></html>
EOF
python3 "$V" "$TMP/mask.html" >/dev/null 2>&1; rc=$?
[ $rc -eq 1 ] && pass "content emoji does not mask icon emoji (gate stays closed)" || fail "icon emoji masked by earlier content emoji (rc=$rc)"

# 5. HTML-entity emoji cannot sneak past the gate (review P1)
cat > "$TMP/entity.html" <<'EOF'
<html><head><meta name="viewport" content="width=device-width"></head>
<body><button class="icon">&#x1F680;</button></body></html>
EOF
python3 "$V" "$TMP/entity.html" >/dev/null 2>&1; rc=$?
[ $rc -eq 1 ] && pass "entity-encoded emoji icon still blocked" || fail "entity emoji bypassed the gate (rc=$rc)"

# 6. A CSS comment cannot disarm the focus check (review P2)
cat > "$TMP/focustrick.html" <<'EOF'
<html><head><meta name="viewport" content="width=device-width"></head>
<body><style>/* :focus */ button{outline:none}</style><button>Go</button></body></html>
EOF
python3 "$V" "$TMP/focustrick.html" >/dev/null 2>&1; rc=$?
[ $rc -eq 1 ] && pass "commented-out :focus does not disarm the outline check" || fail "focus check disarmed by CSS comment (rc=$rc)"

# 7. No false positives on legitimate typography: arrows + checkmarks pass (review P0)
cat > "$TMP/arrows.html" <<'EOF'
<html><head><meta name="viewport" content="width=device-width"></head>
<body><a href="/next">Next →</a><ul><li>✓ Done</li><li>★ Featured</li></ul>
<button>Save changes</button></body></html>
EOF
python3 "$V" "$TMP/arrows.html" >/dev/null 2>&1; rc=$?
[ $rc -eq 0 ] && pass "arrows/checkmarks are NOT flagged (no false positive in a hard gate)" || fail "legitimate typography blocked (rc=$rc)"

echo ""
[ "$FAILED" -eq 0 ] && { echo "design-validator: ALL PASS"; exit 0; } || { echo "design-validator: FAILURES"; exit 1; }
