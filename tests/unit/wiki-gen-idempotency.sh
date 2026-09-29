#!/usr/bin/env bash
# tag: unit generated-docs wiki
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

assert_files() {
  local output="$1"
  shift
  (cd "$output" && find . -type f | sed 's#^\./##' | LC_ALL=C sort) > "$TMP/actual-files"
  printf '%s\n' "$@" | LC_ALL=C sort > "$TMP/expected-files"
  if ! cmp -s "$TMP/expected-files" "$TMP/actual-files"; then
    echo "FAIL: generated files escaped the selected output scope" >&2
    diff -u "$TMP/expected-files" "$TMP/actual-files" >&2 || true
    exit 1
  fi
}

wiki="$TMP/wiki-only"
bash "$ROOT/bin/li-wiki-gen" --wiki-only --output "$wiki" >/dev/null
assert_files "$wiki" docs/wiki/README.md docs/wiki/skills.md docs/wiki/agents.md \
  docs/wiki/packs.md docs/wiki/schemas.md
test ! -e "$wiki/docs/showcase"

showcase="$TMP/showcase-only"
bash "$ROOT/bin/li-wiki-gen" --showcase-only --output "$showcase" >/dev/null
assert_files "$showcase" docs/showcase/lintel-the-harness.html
test ! -e "$showcase/docs/wiki"

# Partial generation and checks leave even malformed, unselected output alone.
printf 'Operator README without generated markers.\n' > "$wiki/README.md"
mkdir -p "$wiki/docs/showcase"
printf 'Operator showcase.\n' > "$wiki/docs/showcase/lintel-the-harness.html"
cp "$wiki/README.md" "$TMP/readme-sentinel"
cp "$wiki/docs/showcase/lintel-the-harness.html" "$TMP/showcase-sentinel"
bash "$ROOT/bin/li-wiki-gen" --wiki-only --output "$wiki" >/dev/null
bash "$ROOT/bin/li-wiki-gen" --wiki-only --output "$wiki" --check
cmp "$wiki/README.md" "$TMP/readme-sentinel"
cmp "$wiki/docs/showcase/lintel-the-harness.html" "$TMP/showcase-sentinel"
printf '\nSelected wiki drift\n' >> "$wiki/docs/wiki/skills.md"
if bash "$ROOT/bin/li-wiki-gen" --wiki-only --output "$wiki" --check > "$TMP/partial-drift"; then
  echo 'FAIL: wiki-only check ignored drift in a selected artifact' >&2
  exit 1
fi
grep -q '^STALE: docs/wiki/skills.md' "$TMP/partial-drift"
grep -q 'Selected wiki drift' "$wiki/docs/wiki/skills.md"

printf 'Operator README without generated markers.\n' > "$showcase/README.md"
mkdir -p "$showcase/docs/wiki"
printf 'Operator wiki.\n' > "$showcase/docs/wiki/README.md"
cp "$showcase/docs/wiki/README.md" "$TMP/wiki-sentinel"
bash "$ROOT/bin/li-wiki-gen" --showcase-only --output "$showcase" >/dev/null
bash "$ROOT/bin/li-wiki-gen" --showcase-only --output "$showcase" --check
cmp "$showcase/README.md" "$TMP/readme-sentinel"
cmp "$showcase/docs/wiki/README.md" "$TMP/wiki-sentinel"
printf '\nSelected showcase drift\n' >> "$showcase/docs/showcase/lintel-the-harness.html"
if bash "$ROOT/bin/li-wiki-gen" --showcase-only --output "$showcase" --check > "$TMP/partial-drift"; then
  echo 'FAIL: showcase-only check ignored drift in a selected artifact' >&2
  exit 1
fi
grep -q '^STALE: docs/showcase/lintel-the-harness.html' "$TMP/partial-drift"
grep -q 'Selected showcase drift' "$showcase/docs/showcase/lintel-the-harness.html"

for mode in wiki-only showcase-only default; do
  absent="$TMP/missing-$mode"
  rc=0
  if [ "$mode" = default ]; then
    bash "$ROOT/bin/li-wiki-gen" --output "$absent" --check > "$TMP/missing-check" || rc=$?
  else
    bash "$ROOT/bin/li-wiki-gen" --"$mode" --output "$absent" --check > "$TMP/missing-check" || rc=$?
  fi
  test "$rc" -eq 1
  test ! -e "$absent"
  grep -q '^STALE:' "$TMP/missing-check"
done

rc=0
bash "$ROOT/bin/li-wiki-gen" --wiki-only --showcase-only --output "$TMP/conflicting" > "$TMP/invalid" 2>&1 || rc=$?
test "$rc" -eq 2
test ! -e "$TMP/conflicting"
# Exercise the actual argument parser without letting a regressed empty path
# reach generation and write to the host filesystem root.
awk '
  /^# Validate schema inputs before opening any generated output\.$/ { found=1; exit }
  { print }
  END { if (!found) exit 2 }
' "$ROOT/bin/li-wiki-gen" > "$TMP/argument-parser.sh"
printf '\nprintf "parser-completed\\n"\nexit 0\n' >> "$TMP/argument-parser.sh"
for argument in missing empty; do
  rc=0
  if [ "$argument" = missing ]; then
    bash "$TMP/argument-parser.sh" --output > "$TMP/invalid" 2>&1 || rc=$?
  else
    bash "$TMP/argument-parser.sh" --output "" > "$TMP/invalid" 2>&1 || rc=$?
  fi
  test "$rc" -eq 2
  grep -q -- '--output' "$TMP/invalid"
  ! grep -q 'parser-completed' "$TMP/invalid"
done
echo 'PASS: partial generation and checks are scoped; invalid selections refuse before writes'

# Build with byte ordering, then verify under a locale that collates PascalCase
# agent names differently (e.g. AccessibilityChecker versus ADRDrafter on macOS).
LC_ALL=C bash "$ROOT/bin/li-wiki-gen" --output "$TMP" >/dev/null
[[ "$(grep -c '^schema_version: 1$' "$TMP/docs/wiki/schemas.md")" -eq 2 ]]
grep -qx 'Required top-level fields: name, version, voice, compliance, navigation' "$TMP/docs/wiki/schemas.md"
grep -qx 'Structure: HEAD (6 required) + BODY (content_type discriminator; 2 required) + TAIL (4 required)' "$TMP/docs/wiki/schemas.md"
LC_ALL=en_US.UTF-8 bash "$ROOT/bin/li-wiki-gen" --output "$TMP" --check
# A changed artifact must fail verification without rewriting the baseline.
printf '\nIntentional drift\n' >> "$TMP/docs/wiki/skills.md"
if bash "$ROOT/bin/li-wiki-gen" --output "$TMP" --check > "$TMP/result"; then
  echo 'FAIL: changed generated documentation passed the drift check' >&2
  exit 1
fi
grep -q 'STALE: docs/wiki/skills.md' "$TMP/result"
grep -q 'Intentional drift' "$TMP/docs/wiki/skills.md"
# CRLF source must not silently empty the skill index.
grep -q '| catalog | foundation |  | internal | \[claude-code, codex, copilot\] |' "$TMP/docs/wiki/skills.md"
grep -q '| spec-kit | foundation |' "$TMP/docs/wiki/skills.md"
# The capability table renders a surface with recorded observations (lib/cli-tiers.yaml) as
# "partial session observations"; copilot-cli has recorded observations since 0.13.0.
grep -q '| GitHub Copilot CLI | .github/skills | documented | partial session observations |' "$TMP/README.md"

# Different schema data must change the reference, not require a generator edit.
source "$ROOT/lib/wiki-gen.sh"
cat > "$TMP/pack.yaml" <<'YAML'
schema_version: "7"
schema_kind: pack-manifest
required_fields: [name, additional]
optional_fields: [requires_lintel]
YAML
wgen_schema_summary "$TMP/pack.yaml" pack-manifest > "$TMP/pack-summary"
grep -qx 'schema_version: 7' "$TMP/pack-summary"
grep -qx 'Required top-level fields: name, additional' "$TMP/pack-summary"
cat > "$TMP/envelope.yaml" <<'JSON'
{"tail":{"required":["audit_pointer"]},"schema_kind":"envelope","schema_version":"9","body":{"required":["content_type","content","additional"]},"head":{"required":["id","source"]}}
JSON
wgen_schema_summary "$TMP/envelope.yaml" envelope > "$TMP/envelope-summary"
grep -qx 'schema_version: 9' "$TMP/envelope-summary"
grep -qx 'Structure: HEAD (2 required) + BODY (content_type discriminator; 3 required) + TAIL (1 required)' "$TMP/envelope-summary"

# A malformed contract must fail before touching an existing output tree.
mkdir -p "$TMP/source/bin" "$TMP/source/lib"
cp "$ROOT/bin/li-wiki-gen" "$TMP/source/bin/"
cp "$ROOT/lib/wiki-gen.sh" "$ROOT/lib/profile_context.py" "$ROOT/lib/native_paths.py" "$ROOT/lib/pack-schema.yaml" "$TMP/source/lib/"
cp "$TMP/envelope.yaml" "$TMP/source/lib/envelope-schema.yaml"
printf 'keep this output\n' > "$TMP/docs/wiki/schemas.md"
cp "$TMP/docs/wiki/schemas.md" "$TMP/schema-sentinel"
for invalid in missing-version wrong-kind malformed empty-version wrong-required duplicate-key; do
  case "$invalid" in
    missing-version) printf '{"schema_kind":"envelope"}\n' ;;
    wrong-kind) printf '{"schema_version":"1","schema_kind":"other"}\n' ;;
    malformed) printf '{"schema_version":\n' ;;
    empty-version) printf '{"schema_version":"","schema_kind":"envelope"}\n' ;;
    wrong-required) printf '{"schema_version":"1","schema_kind":"envelope","head":{"required":"id"}}\n' ;;
    duplicate-key) printf '{"schema_version":"1","schema_version":"2","schema_kind":"envelope"}\n' ;;
  esac > "$TMP/source/lib/envelope-schema.yaml"
  rc=0
  bash "$TMP/source/bin/li-wiki-gen" --output "$TMP" > "$TMP/result" 2>&1 || rc=$?
  [[ "$rc" -eq 2 ]]
  grep -q 'ERROR: schema reference' "$TMP/result"
  cmp "$TMP/schema-sentinel" "$TMP/docs/wiki/schemas.md"
  ! grep -q 'wrote\|li-wiki-gen: complete' "$TMP/result"
done
rm "$TMP/source/lib/pack-schema.yaml"
if bash "$TMP/source/bin/li-wiki-gen" --output "$TMP" --check > "$TMP/result" 2>&1; then
  echo 'FAIL: missing schema passed generated-documentation verification' >&2
  exit 1
fi
grep -q 'ERROR: schema reference' "$TMP/result"
cmp "$TMP/schema-sentinel" "$TMP/docs/wiki/schemas.md"
echo 'PASS: generated documentation is deterministic; check detects drift without rewriting it'
echo 'PASS: schema metadata follows source data; malformed or missing schemas refuse before writes'
