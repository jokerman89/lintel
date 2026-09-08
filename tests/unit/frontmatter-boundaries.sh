#!/usr/bin/env bash
# Required metadata in markdown body examples must not make an invalid plugin pass.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
source "$ROOT/lib/frontmatter.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
cat > "$TMP/valid.md" <<'MD'
---
name: example
description: Example
color: blue
tools: []
voice: internal
cli_support: [copilot-cli]
layer: foundation
---
Body
MD
validate_lintel_frontmatter "$TMP/valid.md" skill
sed '/^layer:/d' "$TMP/valid.md" > "$TMP/body.md"
printf '\nlayer: foundation\n' >> "$TMP/body.md"
if validate_lintel_frontmatter "$TMP/body.md" skill >/dev/null; then
  echo 'FAIL: body field satisfied required metadata'; exit 1
fi
validate_lintel_frontmatter "$TMP/body.md" agent
sed '$d' "$TMP/valid.md" | sed '2,$ { /^---$/d; }' > "$TMP/open.md"
if validate_lintel_frontmatter "$TMP/open.md" skill >/dev/null; then
  echo 'FAIL: unterminated frontmatter accepted'; exit 1
fi
printf 'name: missing-opening\n' > "$TMP/bad.md"
if validate_lintel_frontmatter "$TMP/bad.md" agent >/dev/null; then
  echo 'FAIL: missing opening accepted'; exit 1
fi
echo 'PASS: frontmatter is bounded, complete, and distinguishes skills from agents'
