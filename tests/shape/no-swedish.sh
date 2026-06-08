#!/usr/bin/env bash
# tests/shape/no-swedish.sh
# Tripwire: Lintel ships English-only. This guard FAILS CI if Swedish text
# reappears in the shipped surface (skills/ agents/ hooks/ install/ .github/
# .codex-plugin/ seeds/). It detects Swedish letters (å ä ö Å Ä Ö) and a set
# of high-signal Swedish words that never appear in English technical prose.
#
# These carry FUNCTIONAL Swedish (capability, not prose — translating them would
# remove functionality) and are allowlisted or out of scan scope:
#   - hooks/shared/_patterns.sh         : customer-PII regex (ärende, ÅÄÖ,
#                                         personnummer) sourced by the customer hooks
#   - lib/orientator-routing.sh         : Swedish intent keywords (matches Swedish
#                                         operator input) — out of scan scope (lib/)
#   - skills/CATALOG.md                  : generated from frontmatter; the source
#                                         SKILL.md files are scanned instead
#
# Closes the v4.9 five-lens audit's #1 hygiene finding (~500 lines of Swedish
# across the shipped surface). Decision D4 of the engineering-reviewed plan.
# tag: hygiene i18n english-only
set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"
FAILED=0
pass() { echo "  PASS: $1"; }
fail() { echo "  FAIL: $1"; FAILED=1; }

echo "tests/shape/no-swedish.sh"
echo "========================="

is_allowlisted() {
  case "$1" in
    # Functional Swedish PII regex (ärende, ÅÄÖ) now lives once in _patterns.sh,
    # which the customer-data hooks source — so only this file needs the allowlist.
    hooks/shared/_patterns.sh) return 0 ;;
    skills/CATALOG.md) return 0 ;;
  esac
  return 1
}

SCAN_DIRS=(skills agents hooks install .github .codex-plugin seeds)
# UTF-8 byte pattern for å ä ö Å Ä Ö (each is C3 followed by one of these bytes).
CHAR_RE=$'[\xc3][\xa5\xa4\xb6\x85\x84\x96]'
# High-signal Swedish words with no English collision (word-bounded, case-insensitive).
# Includes ASCII-only Swedish words that the letter check above cannot catch
# (kategori, mellan, ...). Conservative set — every entry is unambiguously Swedish.
WORD_RE='(och|inte|eller|denna|detta|utan|finns|vilka|ingen|aldrig|samma|kategori|framtida|eftersom|mellan|genom|samt|endast|enbart|stycka|vilket)'

hits=0
while IFS= read -r f; do
  is_allowlisted "$f" && continue
  [ -f "$f" ] || continue
  while IFS= read -r line; do
    [ -n "$line" ] && { fail "$f — Swedish letter — $line"; hits=$((hits+1)); }
  done < <(LC_ALL=C grep -nE "$CHAR_RE" "$f" 2>/dev/null)
  while IFS= read -r line; do
    [ -n "$line" ] && { fail "$f — Swedish word — $line"; hits=$((hits+1)); }
  done < <(grep -nwiE "$WORD_RE" "$f" 2>/dev/null)
done < <(git ls-files "${SCAN_DIRS[@]}")

[ "$hits" -eq 0 ] && pass "no Swedish in shipped surface (${SCAN_DIRS[*]}; 3 functional files allowlisted)"

echo ""
[ "$FAILED" -eq 0 ] && { echo "no-swedish: ALL PASS"; exit 0; } || { echo "no-swedish: FAILURES ($hits hit(s))"; exit 1; }
