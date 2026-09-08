#!/usr/bin/env bash
# tests/shape/extension-pack-contract.sh
# Guards the extension-pack contract (ADR-0018): _default ships the block OFF;
# the resolver resolves it + the awareness helpers exist; validate_pack enforces
# namespace+workflow when is_extension:true; li-pack-scaffold emits a valid skeleton.
set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
FAILED=0
pass(){ echo "  PASS: $1"; }
fail(){ echo "  FAIL: $1"; FAILED=1; }
echo "tests/shape/extension-pack-contract.sh"
echo "======================================"

TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT
export LINTEL_HOME="$TMP/.lintel"
export LINTEL_PACKS_DIR="$TMP/.lintel/packs"
export LINTEL_AUDIT_DIR="$TMP/.lintel/audit"
export LINTEL_SESSION_ID="exttest-$$"
mkdir -p "$LINTEL_PACKS_DIR" "$LINTEL_AUDIT_DIR"

# ── 1. _default ships the extension block, OFF ──────────────────────────────
echo ""; echo "[1] _default has extension block, is_extension:false"
DEF="$REPO_ROOT/packs/_default/pack.yaml"
grep -qE '^extension:' "$DEF" && pass "_default has extension: block" || fail "_default missing extension: block"
grep -qE '^[[:space:]]*is_extension:[[:space:]]*false' "$DEF" && pass "_default is_extension:false" || fail "_default is_extension not false"

# ── 2. resolver resolves extension.* + awareness helpers exist ──────────────
echo ""; echo "[2] resolver resolves extension.* + helpers"
source "$REPO_ROOT/lib/pack-resolver.sh"
for fn in pack_is_extension pack_namespace pack_workflow; do
  command -v "$fn" >/dev/null 2>&1 && pass "helper $fn defined" || fail "helper $fn missing"
done
v=$(resolve_pack_field extension.is_extension)
[ "$v" = "false" ] && pass "resolve extension.is_extension=false (_default)" || fail "resolve extension.is_extension got '$v'"
if pack_is_extension; then fail "_default wrongly reports as extension"; else pass "_default not an extension (pack_is_extension false)"; fi

# ── 3. validate_pack enforces namespace+workflow when is_extension:true ──────
echo ""; echo "[3] validate_pack enforces extension fields"
mk_pack(){ # <name> <is_ext> <ns> <wf>
  local d="$LINTEL_PACKS_DIR/$1"; mkdir -p "$d"
  cat > "$d/pack.yaml" <<YAML
name: $1
version: 1.0.0
voice:
  default_tier: internal
compliance:
  mode: advisory
navigation:
  default_workflow: cycle
extension:
  is_extension: $2
  namespace: $3
  workflow: $4
YAML
}
mk_pack ext-bad  true  null null
mk_pack ext-good true  s4l  s4l-forge
mk_pack ident-ok false null null
if validate_pack ext-bad 2>/dev/null; then fail "ext-bad (is_extension:true, no ns/wf) should NOT validate"; else pass "ext-bad rejected (missing ns/wf)"; fi
if validate_pack ext-good 2>/dev/null; then pass "ext-good validates"; else fail "ext-good should validate"; fi
if validate_pack ident-ok 2>/dev/null; then pass "identity pack (is_extension:false) validates"; else fail "identity pack should validate"; fi

# ── 3b. adversarial: truthy-alias, block-scoping, comment-strip, null→empty ──
# (regression guards for the ADR-0018 review findings)
echo ""; echo "[3b] adversarial parse cases"
# P1b: a truthy ALIAS (yes/on) without ns/wf must still be rejected — validate_pack
# must use the same truthiness as pack_is_extension or the invariant is bypassable.
mk_pack ext-yes yes null null
if validate_pack ext-yes 2>/dev/null; then fail "is_extension:yes w/o ns/wf should be rejected (alias bypass)"; else pass "truthy alias (yes) enforced by 2b"; fi
# P1a: namespace/workflow present only under ANOTHER block must NOT satisfy the requirement
d="$LINTEL_PACKS_DIR/ext-scoped"; mkdir -p "$d"
cat > "$d/pack.yaml" <<'YAML'
name: ext-scoped
version: 1.0.0
voice:
  default_tier: internal
compliance:
  mode: advisory
navigation:
  default_workflow: cycle
roles:
  namespace: legacy
  workflow: legacy-flow
extension:
  is_extension: true
YAML
if validate_pack ext-scoped 2>/dev/null; then fail "ns/wf under roles: wrongly satisfied extension req (unscoped grep)"; else pass "extension req is block-scoped (roles ns/wf ignored)"; fi
# P2a: a trailing inline comment on namespace/workflow must be stripped
d="$LINTEL_PACKS_DIR/ext-comment"; mkdir -p "$d"
cat > "$d/pack.yaml" <<'YAML'
name: ext-comment
version: 1.0.0
voice:
  default_tier: internal
compliance:
  mode: advisory
navigation:
  default_workflow: cycle
extension:
  is_extension: true
  namespace: s4l # routing prefix
  workflow: s4l-forge # the cycle
YAML
if validate_pack ext-comment 2>/dev/null; then pass "comment-bearing extension validates"; else fail "comment-bearing extension should validate"; fi
nsval=$(_pack_ext_field "$LINTEL_PACKS_DIR/ext-comment/pack.yaml" namespace)
[ "$nsval" = "s4l" ] && pass "_pack_ext_field strips trailing comment" || fail "_pack_ext_field comment leak: got '$nsval'"
# P2c: pack_namespace normalizes literal null → "" for identity packs
nsdef=$(pack_namespace)
[ -z "$nsdef" ] && pass "pack_namespace empty for identity _default (null normalized)" || fail "pack_namespace non-empty for _default: '$nsdef'"

# ── 4. li-pack-scaffold emits a valid extension-pack skeleton ───────────────
echo ""; echo "[4] li-pack-scaffold output validates"
SCAF="$TMP/scaf"; mkdir -p "$SCAF"
if bash "$REPO_ROOT/bin/li-pack-scaffold" demo-pack --namespace demo --workflow demo-forge --target "$SCAF" >/dev/null 2>&1; then
  pass "scaffold ran"
else
  fail "scaffold failed"
fi
PK="$SCAF/demo-pack"
[ -f "$PK/.claude-plugin/plugin.json" ] && pass "plugin.json created" || fail "plugin.json missing"
[ -f "$PK/pack.yaml" ] && pass "pack.yaml created" || fail "pack.yaml missing"
grep -qE '^[[:space:]]*is_extension:[[:space:]]*true' "$PK/pack.yaml" 2>/dev/null && pass "scaffold is_extension:true" || fail "scaffold not is_extension:true"
grep -qE '^[[:space:]]*namespace:[[:space:]]*demo([[:space:]]|$)' "$PK/pack.yaml" 2>/dev/null && pass "scaffold namespace set" || fail "scaffold namespace not set"
grep -qE '^[[:space:]]*workflow:[[:space:]]*demo-forge' "$PK/pack.yaml" 2>/dev/null && pass "scaffold workflow set" || fail "scaffold workflow not set"
for d in skills agents hooks knowhow; do [ -d "$PK/$d" ] && pass "dir $d/ present" || fail "dir $d/ missing"; done
# the scaffolded pack must validate via the resolver
export LINTEL_PACKS_DIR="$SCAF"
if validate_pack demo-pack 2>/dev/null; then pass "scaffolded pack validates"; else fail "scaffolded pack fails validate_pack"; fi

# ── 4b. manifest-injection guard: hostile --description must not poison plugin.json ──
echo ""; echo "[4b] scaffolder manifest-injection guard"
SCAF2="$TMP/scaf2"; mkdir -p "$SCAF2"
bash "$REPO_ROOT/bin/li-pack-scaffold" poison --namespace evil --workflow evil-forge --target "$SCAF2" \
  --description 'x", "name": "hijacked", "extra": "evil' >/dev/null 2>&1
PJ="$SCAF2/poison/.claude-plugin/plugin.json"
[ -f "$PJ" ] && pass "poison scaffold produced manifest" || fail "poison scaffold produced no manifest"
nc=$(grep -cE '"name":' "$PJ" 2>/dev/null || echo 0)
[ "$nc" = "1" ] && pass "exactly one name key (no key injection)" || fail "plugin.json has $nc name keys (injection)"
grep -qE '"name":[[:space:]]*"poison"' "$PJ" 2>/dev/null && pass "manifest name is the real pack name" || fail "manifest name hijacked"
if command -v jq >/dev/null 2>&1; then
  jq . "$PJ" >/dev/null 2>&1 && pass "plugin.json parses as valid JSON (jq)" || fail "plugin.json invalid JSON after hostile --description"
  [ "$(jq -b -r .name "$PJ" 2>/dev/null)" = "poison" ] && pass "jq .name == poison (not hijacked)" || fail "jq .name was hijacked"
else
  echo "  SKIP: jq not present — structural name-key checks only"
fi

echo ""
if [ "$FAILED" -eq 0 ]; then echo "ALL PASS"; else echo "FAILURES present"; exit 1; fi
