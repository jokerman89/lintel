#!/usr/bin/env bash
# tests/shape/manifest-identity.sh
# Single-source identity sync guard (decision D2 of the five-lens remediation).
# `.claude-plugin/plugin.json` is the canonical source for version + repo slug +
# maintainer email; every other plugin manifest must agree, and no stale identity
# may reappear anywhere on the shipped surface (manifests + installers + .opencode
# + bin/). Fails CI on drift.
#
# Why this exists: the repo carried THREE different identities at once —
#   jokerman89/lintel              (the actual git remote — ground truth)
#   jokerman89/jokerman-lintel     (all 8 plugin manifests + install)
#   Azureflipper/jokerman-session-setup (bin/li-doctor, li-scaffold, li-update)
# plus a stale 3.5.0-dev version and an @microsoft.com email that disagreed with
# the git identity. Reconciled to the observable remote; this guard prevents
# silent re-drift the next time a manifest is added.
# tag: hygiene identity manifests
set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"
FAILED=0
pass(){ echo "  PASS: $1"; }
fail(){ echo "  FAIL: $1"; FAILED=1; }

echo "tests/shape/manifest-identity.sh"
echo "================================"

# Version-parity needs a JSON reader. Drift tripwires below do NOT — they run
# unconditionally so the guard still bites where jq is unavailable (e.g. a bare
# Git-for-Windows shell). CI (ubuntu) has jq, so parity is enforced there.
if command -v jq >/dev/null 2>&1; then
  CANON=".claude-plugin/plugin.json"
  CANON_VERSION=$(jq -r '.version' "$CANON")
  CANON_REPO=$(jq -r '.repository // empty' "$CANON")

  if [ -n "$CANON_VERSION" ] && [ "$CANON_VERSION" != "null" ]; then
    pass "canonical version present: $CANON_VERSION"
  else
    fail "canonical .version missing in $CANON"
  fi
  case "$CANON_REPO" in
    *jokerman89/lintel*) pass "canonical repository -> $CANON_REPO" ;;
    *) fail "canonical repository wrong/absent: '$CANON_REPO'" ;;
  esac

  VERSION_MANIFESTS=(
    .claude-plugin/plugin.json
    .claude-plugin/marketplace.json
    .codex-plugin/plugin.json
    .cursor-plugin/plugin.json
    gemini-extension.json
  )
  for m in "${VERSION_MANIFESTS[@]}"; do
    [ -f "$m" ] || { fail "missing manifest: $m"; continue; }
    jq empty "$m" 2>/dev/null || { fail "invalid JSON: $m"; continue; }
    v=$(jq -r '.version // .metadata.version // empty' "$m")
    if [ "$v" = "$CANON_VERSION" ]; then
      pass "$m version == $CANON_VERSION"
    else
      fail "$m version '$v' != canonical '$CANON_VERSION'"
    fi
  done
else
  echo "  NOTE: jq absent — version-parity checks skipped (enforced in CI); drift tripwires below still run"
fi

# Drift tripwires: no stale identity anywhere on the shipped surface (jq-free).
SURFACE=(.claude-plugin .codex-plugin .cursor-plugin gemini-extension.json install .opencode bin)
for bad in 'jokerman89/jokerman-lintel' 'Azureflipper/jokerman-session-setup' '3.5.0-dev' 'akerman@microsoft.com'; do
  if git grep -qF "$bad" -- "${SURFACE[@]}" 2>/dev/null; then
    fail "stale identity '$bad' still present: $(git grep -lF "$bad" -- "${SURFACE[@]}" 2>/dev/null | tr '\n' ' ')"
  else
    pass "no '$bad' on shipped surface"
  fi
done

# Focused docs tripwire: README + SECURITY are user-facing identity surfaces the
# SURFACE loop above does NOT scan (v4.9 audit found this gap → false confidence).
# Scan them for the two most damaging stale strings only. Skip absent files.
DOCS=(README.md SECURITY.md)
for f in "${DOCS[@]}"; do
  [ -f "$f" ] || { pass "doc absent, skipped: $f"; continue; }
  for bad in 'akerman@microsoft.com' 'jokerman89/jokerman-lintel'; do
    if grep -qF "$bad" "$f" 2>/dev/null; then
      fail "stale identity '$bad' present in $f"
    else
      pass "no '$bad' in $f"
    fi
  done
done

echo ""
[ "$FAILED" -eq 0 ] && { echo "manifest-identity: ALL PASS"; exit 0; } || { echo "manifest-identity: FAILURES"; exit 1; }
