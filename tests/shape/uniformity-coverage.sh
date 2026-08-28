#!/usr/bin/env bash
# tests/shape/uniformity-coverage.sh
# Asserts (v4.0): the uniformity-as-contract FLOOR holds, and REPORTS adoption
# of the tracked dimensions above the floor.
#
# Contract: docs/concepts/uniformity-contract.md
#   - FLOOR (HARD-FAIL, exit 1):
#       * every `workflow_root: true` skill declares `necessity:`
#       * every block-hook (tier JUSTIFIED-BLOCK / HARD-RULE) declares `necessity:`
#   - ABOVE THE FLOOR (REPORT only, never fails CI):
#       * per-kind adoption % of the tracked dimension fields
#
# The floor is deliberately small so it is always satisfiable. The long tail
# (regular skills / agents / warn-hooks lacking necessity) is TRACKED, not
# enforced — adding it to the floor is the contract's explicit non-goal.
#
# Coordination note: a sibling backfill adds `necessity:` to exactly the
# workflow_root skills + block-hooks. Until that lands, this test will name the
# offending workflow_root skill(s)/hook(s) and FAIL on the floor — that failure
# is EXPECTED and is the coordination signal, not a bug in this test.
#
# tag: shape v4.0

set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
FAILED=0
pass() { echo "  PASS: $1"; }
fail() { echo "  FAIL: $1"; FAILED=1; }

echo "tests/shape/uniformity-coverage.sh"
echo "===================================="

# ─── Frontmatter helpers (CRLF-safe, same discipline as the other shape tests) ─
# True if the file's YAML frontmatter declares `<field>:` (any value).
fm_has_field() {
  local file="$1" field="$2"
  awk -v field="$field" '
    { sub(/\r$/, "") }                       # strip CRLF
    /^---[[:space:]]*$/ { if (++fm == 2) exit; next }
    fm == 1 && $0 ~ "^"field":" { found = 1; exit }
    END { exit (found ? 0 : 1) }
  ' "$file"
}

# Echo the scalar value of a frontmatter field (empty if absent).
fm_value() {
  local file="$1" field="$2"
  awk -v field="$field" '
    { sub(/\r$/, "") }
    /^---[[:space:]]*$/ { if (++fm == 2) exit; next }
    fm == 1 && $0 ~ "^"field":" {
      sub("^"field":[[:space:]]*", "")
      sub("[[:space:]]*#.*$", "")
      gsub(/^[[:space:]]+|[[:space:]]+$/, "")
      print
      exit
    }
  ' "$file"
}

# True if the field is present AND its value is non-empty (a present-but-blank
# `necessity:` does not satisfy the floor).
fm_has_nonempty() {
  local file="$1" field="$2"
  fm_has_field "$file" "$field" || return 1
  [ -n "$(fm_value "$file" "$field")" ]
}

# ─── Enumerate components (directory-derived) ──────────────────────────────────
SKILL_FILES=()
while IFS= read -r f; do SKILL_FILES+=("$f"); done < <(find "$REPO_ROOT/skills" -name "SKILL.md" -type f 2>/dev/null | sort)

AGENT_FILES=()
while IFS= read -r f; do AGENT_FILES+=("$f"); done < <(find "$REPO_ROOT/agents" -name "*.md" -type f 2>/dev/null | grep -v README | grep -v "_TEMPLATE" | sort)

HOOK_FILES=()
while IFS= read -r f; do HOOK_FILES+=("$f"); done < <(find "$REPO_ROOT/hooks/shared" -name "HOOK.md" -type f 2>/dev/null | sort)

PACK_FILES=()
while IFS= read -r f; do PACK_FILES+=("$f"); done < <(find "$REPO_ROOT/packs" -name "pack.yaml" -type f 2>/dev/null | sort)

pass "Enumerated: ${#SKILL_FILES[@]} skills, ${#AGENT_FILES[@]} agents, ${#HOOK_FILES[@]} hooks, ${#PACK_FILES[@]} packs"

# ─── KIND derivation ───────────────────────────────────────────────────────────
# Skill kind: workflow_root if frontmatter has `workflow_root: true`, else regular.
skill_is_workflow_root() {
  local f="$1"
  awk '
    { sub(/\r$/, "") }
    /^---[[:space:]]*$/ { if (++fm == 2) exit; next }
    fm == 1 && /^workflow_root:[[:space:]]*true[[:space:]]*$/ { print "yes"; exit }
  ' "$f"
}

# Hook kind from tier: block | warn | lifecycle.
hook_kind() {
  local f="$1" tier
  tier="$(fm_value "$f" tier)"
  case "$tier" in
    JUSTIFIED-BLOCK|HARD-RULE) echo "block" ;;
    lifecycle)                 echo "lifecycle" ;;
    *)                         echo "warn" ;;   # warn-only / surface-only / blank
  esac
}

# ─── FLOOR ENFORCEMENT (the only HARD-FAIL path) ───────────────────────────────
echo ""
echo "-- FLOOR (hard-fail) --"

# Floor A: every workflow_root: true skill declares a non-empty `necessity:`.
WR_COUNT=0
WR_MISSING=()
for f in "${SKILL_FILES[@]}"; do
  [ "$(skill_is_workflow_root "$f")" = "yes" ] || continue
  WR_COUNT=$((WR_COUNT + 1))
  if ! fm_has_nonempty "$f" necessity; then
    WR_MISSING+=("$(basename "$(dirname "$f")")")
  fi
done

if [ "$WR_COUNT" -eq 0 ]; then
  fail "no workflow_root: true skills found (expected cycle + plan + ta at minimum)"
elif [ "${#WR_MISSING[@]}" -eq 0 ]; then
  pass "all $WR_COUNT workflow_root skills declare necessity: (floor A satisfied)"
else
  fail "${#WR_MISSING[@]}/$WR_COUNT workflow_root skill(s) lack necessity: (floor A) — backfill needed:"
  for s in "${WR_MISSING[@]}"; do echo "      - skills/$s/SKILL.md  (needs: necessity:)"; done
fi

# Floor B: every block-hook (JUSTIFIED-BLOCK / HARD-RULE) declares `necessity:`.
BLOCK_COUNT=0
BLOCK_MISSING=()
for f in "${HOOK_FILES[@]}"; do
  [ "$(hook_kind "$f")" = "block" ] || continue
  BLOCK_COUNT=$((BLOCK_COUNT + 1))
  if ! fm_has_nonempty "$f" necessity; then
    BLOCK_MISSING+=("$(basename "$(dirname "$f")")")
  fi
done

if [ "$BLOCK_COUNT" -eq 0 ]; then
  pass "no block-hooks found (nothing to enforce for floor B)"
elif [ "${#BLOCK_MISSING[@]}" -eq 0 ]; then
  pass "all $BLOCK_COUNT block-hooks declare necessity: (floor B satisfied)"
else
  fail "${#BLOCK_MISSING[@]}/$BLOCK_COUNT block-hook(s) lack necessity: (floor B) — backfill needed:"
  for h in "${BLOCK_MISSING[@]}"; do echo "      - hooks/shared/$h/HOOK.md  (needs: necessity:)"; done
fi

# ─── ADOPTION REPORT (tracked, never fails) ───────────────────────────────────
# For each kind, report the % of components declaring each tracked field.
echo ""
echo "-- ADOPTION (tracked, non-failing) --"

# pct <numerator> <denominator>  -> integer percent, "n/a" if denom 0
pct() {
  local n="$1" d="$2"
  if [ "$d" -eq 0 ]; then echo "n/a"; else echo "$(( (n * 100) / d ))%"; fi
}

# report_kind <label> <field-csv> <file...>
# Counts, for the given file set, how many declare each comma-separated field.
report_kind() {
  local label="$1" fields_csv="$2"; shift 2
  local files=("$@")
  local total="${#files[@]}"
  echo "  ${label} (n=${total}):"
  local IFS=','
  read -ra fields <<< "$fields_csv"
  unset IFS
  for field in "${fields[@]}"; do
    local c=0
    for f in "${files[@]}"; do
      fm_has_field "$f" "$field" && c=$((c + 1))
    done
    printf '      %-22s %3s  (%d/%d)\n' "$field" "$(pct "$c" "$total")" "$c" "$total"
  done
}

# Partition skills into workflow_root vs regular for reporting.
WR_FILES=()
REG_FILES=()
for f in "${SKILL_FILES[@]}"; do
  if [ "$(skill_is_workflow_root "$f")" = "yes" ]; then WR_FILES+=("$f"); else REG_FILES+=("$f"); fi
done

# Partition hooks by kind for reporting.
HOOK_BLOCK_FILES=()
HOOK_WARN_FILES=()
HOOK_LIFE_FILES=()
for f in "${HOOK_FILES[@]}"; do
  case "$(hook_kind "$f")" in
    block)     HOOK_BLOCK_FILES+=("$f") ;;
    lifecycle) HOOK_LIFE_FILES+=("$f") ;;
    *)         HOOK_WARN_FILES+=("$f") ;;
  esac
done

# Tracked dimension fields per kind (subset that is applicable, per the contract).
TRACK_SKILL="necessity,gap_if_skipped,navigation,brief_forge_handoffs,pack_influence,observability,recovery,checkpoints"
TRACK_AGENT="necessity,gap_if_skipped,pack_influence,observability,delegates_to"
TRACK_HOOK="necessity,gap_if_skipped,pack_influence,observability"
TRACK_PACK="necessity,pack_influence"

[ "${#WR_FILES[@]}"        -gt 0 ] && report_kind "workflow_root skills" "$TRACK_SKILL" "${WR_FILES[@]}"
[ "${#REG_FILES[@]}"       -gt 0 ] && report_kind "regular skills"        "$TRACK_SKILL" "${REG_FILES[@]}"
[ "${#AGENT_FILES[@]}"     -gt 0 ] && report_kind "agents"                "$TRACK_AGENT" "${AGENT_FILES[@]}"
[ "${#HOOK_BLOCK_FILES[@]}" -gt 0 ] && report_kind "block-hooks"          "$TRACK_HOOK"  "${HOOK_BLOCK_FILES[@]}"
[ "${#HOOK_WARN_FILES[@]}"  -gt 0 ] && report_kind "warn-hooks"           "$TRACK_HOOK"  "${HOOK_WARN_FILES[@]}"
[ "${#HOOK_LIFE_FILES[@]}"  -gt 0 ] && report_kind "lifecycle-hooks"      "$TRACK_HOOK"  "${HOOK_LIFE_FILES[@]}"
[ "${#PACK_FILES[@]}"       -gt 0 ] && report_kind "packs"                "$TRACK_PACK"  "${PACK_FILES[@]}"

echo ""
echo "  (Adoption above the floor is tracked, not enforced. The living matrix is"
echo "   .claude/engineering/audits/uniformity-matrix.md — regenerate via bin/li-uniformity.)"

# ─── Verdict ───────────────────────────────────────────────────────────────────
echo ""
if [ "$FAILED" -eq 0 ]; then
  echo "All uniformity-coverage FLOOR assertions PASSED"
  exit 0
else
  echo "Some uniformity-coverage FLOOR assertions FAILED (see backfill list above)"
  exit 1
fi
