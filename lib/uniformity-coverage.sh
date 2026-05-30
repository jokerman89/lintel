#!/usr/bin/env bash
# lib/uniformity-coverage.sh — helpers for the uniformity coverage matrix.
#
# Sourced by bin/li-uniformity. Holds the frontmatter-parsing + cell-rendering
# logic so the generator stays thin (same split as lib/wiki-gen.sh ↔
# bin/li-wiki-gen). Pure functions, no side effects, no I/O of their own.
#
# Contract: docs/concepts/uniformity-contract.md

set -uo pipefail

# True (exit 0) if the file's YAML frontmatter declares `<field>:` (any value).
# CRLF-safe — the repo ships scripts/markdown with Windows line endings.
unif_fm_has_field() {
  local file="${1:?}" field="${2:?}"
  awk -v field="$field" '
    { sub(/\r$/, "") }
    /^---[[:space:]]*$/ { if (++fm == 2) exit; next }
    fm == 1 && $0 ~ "^"field":" { found = 1; exit }
    END { exit (found ? 0 : 1) }
  ' "$file"
}

# Echo the scalar value of a frontmatter field (empty string if absent).
unif_fm_value() {
  local file="${1:?}" field="${2:?}"
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

# Skill kind: "workflow_root" if frontmatter has `workflow_root: true`, else "regular".
unif_skill_kind() {
  local f="${1:?}"
  if awk '
       { sub(/\r$/, "") }
       /^---[[:space:]]*$/ { if (++fm == 2) exit; next }
       fm == 1 && /^workflow_root:[[:space:]]*true[[:space:]]*$/ { found=1; exit }
       END { exit (found ? 0 : 1) }
     ' "$f"; then
    echo "workflow_root"
  else
    echo "regular"
  fi
}

# Hook kind from its tier: block | warn | lifecycle.
unif_hook_kind() {
  local f="${1:?}" tier
  tier="$(unif_fm_value "$f" tier)"
  case "$tier" in
    JUSTIFIED-BLOCK|HARD-RULE) echo "block" ;;
    lifecycle)                 echo "lifecycle" ;;
    *)                         echo "warn" ;;
  esac
}

# ─── Fast path: single-pass frontmatter field-set reader ──────────────────────
# Emit, one per line, every top-level frontmatter KEY present in the file, with
# a trailing "=1" if that key has a non-empty inline scalar value and "=0" if it
# is a block key (value-less line, value lives on following indented lines).
# ONE awk fork per file — used by the matrix generator to avoid the O(files ×
# columns) fork blow-up that made the naive per-cell version too slow under
# Windows/MSYS awk.
unif_fm_fieldset() {
  local file="${1:?}"
  awk '
    { sub(/\r$/, "") }
    /^---[[:space:]]*$/ { if (++fm == 2) exit; next }
    fm == 1 && /^[A-Za-z_][A-Za-z0-9_]*:/ {
      key = $0
      sub(/:.*/, "", key)
      val = $0
      sub(/^[^:]*:[[:space:]]*/, "", val)
      sub(/[[:space:]]*#.*$/, "", val)
      gsub(/^[[:space:]]+|[[:space:]]+$/, "", val)
      printf "%s=%s\n", key, (length(val) ? "1" : "0")
    }
  ' "$file"
}

# Render a cell from a precomputed field-set (the output of unif_fm_fieldset,
# passed as a single newline-joined string in $2). Requirement level in $3.
#   present (key in set) -> "yes"
#   absent               -> "—"  (optional)  or  "MISS" (required floor cell)
#   n/a-for-kind         -> "n/a"
# A block-style key (value on following lines) still counts as present — the key
# being declared is the signal, not whether its scalar is inline.
unif_cell_from_set() {
  local field="${1:?}" fieldset="${2:-}" req="${3:?}"
  if [ "$req" = "na" ]; then echo "n/a"; return; fi
  case "
$fieldset
" in
    *"
$field="*) echo "yes" ;;
    *) [ "$req" = "R" ] && echo "MISS" || echo "—" ;;
  esac
}

# True if <field> appears as a key in the precomputed field-set string.
unif_set_has() {
  local field="${1:?}" fieldset="${2:-}"
  case "
$fieldset
" in
    *"
$field="*) return 0 ;;
    *) return 1 ;;
  esac
}

# Render a matrix cell for a (file, field) pair given the requirement level.
# Requirement level: R (required/floor), O (optional/tracked), or n/a.
#   present  -> "yes" (with a "!" marker if it is a satisfied floor cell)
#   absent   -> "—"   (R-and-absent renders "MISS" so floor gaps are obvious)
#   n/a-kind -> "n/a"
# Args: <file> <field> <requirement R|O|na>
unif_cell() {
  local file="${1:?}" field="${2:?}" req="${3:?}"
  if [ "$req" = "na" ]; then
    echo "n/a"
    return
  fi
  if unif_fm_has_field "$file" "$field"; then
    if [ -n "$(unif_fm_value "$file" "$field")" ]; then
      echo "yes"
    else
      # present-but-blank: counts as present for tracking, flagged for floor
      [ "$req" = "R" ] && echo "MISS(blank)" || echo "yes(blank)"
    fi
  else
    [ "$req" = "R" ] && echo "MISS" || echo "—"
  fi
}

# Integer percent (rounded down) or "n/a" if denominator is 0.
unif_pct() {
  local n="${1:?}" d="${2:?}"
  if [ "$d" -eq 0 ]; then echo "n/a"; else echo "$(( (n * 100) / d ))%"; fi
}
