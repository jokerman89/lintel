#!/usr/bin/env bash
# tag: unit generated-docs wiki
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
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
grep -q '| GitHub Copilot CLI | .github/skills | documented | not_run |' "$TMP/README.md"

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
