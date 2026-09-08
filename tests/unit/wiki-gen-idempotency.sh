#!/usr/bin/env bash
# tag: unit generated-docs wiki
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
# Build with byte ordering, then verify under a locale that collates PascalCase
# agent names differently (e.g. AccessibilityChecker versus ADRDrafter on macOS).
LC_ALL=C bash "$ROOT/bin/li-wiki-gen" --output "$TMP" >/dev/null
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
grep -q '| help | foundation |  | internal | \[claude-code, codex, copilot\] |' "$TMP/docs/wiki/skills.md"
grep -q '| spec-kit | foundation |' "$TMP/docs/wiki/skills.md"
grep -q '| GitHub Copilot CLI | supported | native | native | not ported |' "$TMP/README.md"
echo 'PASS: generated documentation is deterministic; check detects drift without rewriting it'
