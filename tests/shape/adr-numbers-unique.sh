#!/usr/bin/env bash
# tests/shape/adr-numbers-unique.sh
# Structural invariant: every ADR under .claude/decisions/ has a UNIQUE NNNN number.
# A numbering collision (two ADRs sharing 0015, etc.) landed on main once — two parallel
# branches each claimed 0015/0016/0017 and the merge kept both. This guard fails CI on the
# next collision instead of letting it merge silently. (setup-hardening 2026-06-14)
# tag: adr decisions numbering drift-guard
set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"
FAILED=0
pass(){ echo "  PASS: $1"; }
fail(){ echo "  FAIL: $1"; FAILED=1; }
echo "tests/shape/adr-numbers-unique.sh"
echo "================================="

DIR=".claude/decisions"
[ -d "$DIR" ] || { fail "$DIR missing"; echo "adr-numbers-unique: FAILURES"; exit 1; }

# Collect the NNNN prefix of every NNNN-*.md (skip TEMPLATE/README non-numeric)
nums="$(find "$DIR" -maxdepth 1 -name '[0-9][0-9][0-9][0-9]-*.md' -printf '%f\n' 2>/dev/null \
        | sed -E 's/^([0-9]{4})-.*/\1/' | sort)"
total="$(printf '%s\n' "$nums" | grep -c .)"
uniq_n="$(printf '%s\n' "$nums" | sort -u | grep -c .)"

if [ "$total" -eq "$uniq_n" ]; then
  pass "all $total ADR numbers are unique"
else
  dupes="$(printf '%s\n' "$nums" | uniq -d | paste -sd ' ' -)"
  fail "duplicate ADR number(s): $dupes — renumber the later-created one(s); the first claimant keeps the number"
  for d in $dupes; do
    echo "      $d →"; find "$DIR" -maxdepth 1 -name "$d-*.md" -printf '        %f\n'
  done
fi

# Also assert the title's number matches the filename's number (no internal/filename drift)
while IFS= read -r f; do
  [ -n "$f" ] || continue
  fnum="$(basename "$f" | sed -E 's/^([0-9]{4})-.*/\1/')"
  tnum="$(grep -m1 -oE '^# ADR-([0-9]{4})' "$f" | grep -oE '[0-9]{4}')"
  [ -z "$tnum" ] && continue
  [ "$fnum" = "$tnum" ] || fail "filename/title mismatch: $(basename "$f") titles itself ADR-$tnum"
done < <(find "$DIR" -maxdepth 1 -name '[0-9][0-9][0-9][0-9]-*.md')

echo ""
[ "$FAILED" -eq 0 ] && { echo "adr-numbers-unique: ALL PASS"; exit 0; } || { echo "adr-numbers-unique: FAILURES"; exit 1; }
