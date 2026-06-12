#!/usr/bin/env bash
# component: lintel-memory
# implements: ADR-0006
# intent: docs/concepts/memory-v2.md
# constraints: token-frugal — surfacing is grep-rank, no embeddings, no DB
# last_intent_review: 2026-06-12
#
# lib/memory.sh — mechanical memory helpers (v5 memory v2).
# Closes the prose-only gap: lessons-surface was declared in SENSE Step 0a but
# had no implementation. These helpers make the promises mechanical:
#
#   lessons_surface <keyword...>     → top-3 relevant lessons (id — title [score])
#   lessons_find_related <keyword...>→ all matching lesson ids+titles (for the
#                                      CAPTURE update-phase: add/update/supersede/no-op)
#   lessons_count                    → number of non-superseded lessons
#   memory_budget_check              → warn lines if MEMORY.md / lessons.md
#                                      exceed their block budgets (ADR-0006)
#
# Supersede-don't-delete: a lesson block containing a `superseded_by:` line is
# excluded from surfacing but kept in the file (git holds ingestion history;
# the marker holds validity). Never edit a lesson away — supersede it.

_MEMORY_LIB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
command -v lintel_lessons_file >/dev/null 2>&1 || source "$_MEMORY_LIB_DIR/paths.sh"

# Block budgets (Letta-style: hard caps force consolidation, the same rule
# native MEMORY.md applies with its 200-line auto-load cap).
LINTEL_MEMORY_INDEX_MAX_LINES="${LINTEL_MEMORY_INDEX_MAX_LINES:-200}"
LINTEL_LESSONS_SOFT_MAX="${LINTEL_LESSONS_SOFT_MAX:-30}"

# Score lesson blocks by keyword hits, skip superseded, print top-N.
# Args: <keyword...>   (env: LESSONS_TOP_N, default 3)
lessons_surface() {
  local file
  file="$(lintel_lessons_file 2>/dev/null)" || return 0
  [ -f "$file" ] || return 0
  [ $# -gt 0 ] || return 0
  local top_n="${LESSONS_TOP_N:-3}"

  awk -v keywords="$*" -v topn="$top_n" '
    BEGIN {
      n = split(tolower(keywords), kw, /[ \t]+/)
    }
    /^## L-[0-9]+/ {
      if (id != "") emit()
      id = $0; sub(/^## /, "", id)
      body = ""; superseded = 0
      next
    }
    {
      if (id != "") {
        body = body " " tolower($0)
        if ($0 ~ /^superseded_by:/ || $0 ~ /^> superseded_by:/) superseded = 1
      }
    }
    function emit(   i, score, hay) {
      if (superseded) return
      hay = tolower(id) body
      score = 0
      for (i = 1; i <= n; i++) {
        if (kw[i] != "" && index(hay, kw[i]) > 0) score++
      }
      if (score > 0) {
        count++
        scores[count] = score
        titles[count] = id
      }
    }
    END {
      if (id != "") emit()
      # selection sort, descending score, stable
      for (i = 1; i <= count && i <= topn; i++) {
        best = i
        for (j = i + 1; j <= count; j++) if (scores[j] > scores[best]) best = j
        t = scores[i]; scores[i] = scores[best]; scores[best] = t
        s = titles[i]; titles[i] = titles[best]; titles[best] = s
        printf "%s [matched %d]\n", titles[i], scores[i]
      }
    }
  ' "$file"
}

# All matching lessons (no top-N cap) — input to the CAPTURE update-phase,
# where each candidate lesson is classified add / update / supersede / no-op
# against what already exists.
lessons_find_related() {
  LESSONS_TOP_N=999 lessons_surface "$@"
}

# Count non-superseded lessons (budget input).
lessons_count() {
  local file
  file="$(lintel_lessons_file 2>/dev/null)" || { printf '0'; return 0; }
  [ -f "$file" ] || { printf '0'; return 0; }
  awk '
    /^## L-[0-9]+/ { if (id != "" && !superseded) c++; id = $0; superseded = 0; next }
    /^superseded_by:|^> superseded_by:/ { superseded = 1 }
    END { if (id != "" && !superseded) c++; print c + 0 }
  ' "$file"
}

# Budget check — prints one WARN line per breach, silent when within budget.
# Used by the memory-budget-warn hook and runnable standalone.
memory_budget_check() {
  local idx lessons lines count
  idx="$(lintel_memory_index 2>/dev/null)" || return 0
  if [ -f "$idx" ]; then
    lines=$(wc -l < "$idx" | tr -d ' ')
    if [ "${lines:-0}" -gt "$LINTEL_MEMORY_INDEX_MAX_LINES" ] 2>/dev/null; then
      echo "WARN [lintel/memory]: MEMORY.md is $lines lines (budget $LINTEL_MEMORY_INDEX_MAX_LINES — native auto-load truncates beyond it). Consolidate: move detail into topic files, keep the index an index."
    fi
  fi
  lessons="$(lintel_lessons_file 2>/dev/null)" || return 0
  if [ -f "$lessons" ]; then
    count=$(lessons_count)
    if [ "${count:-0}" -gt "$LINTEL_LESSONS_SOFT_MAX" ] 2>/dev/null; then
      echo "WARN [lintel/memory]: $count active lessons (soft budget $LINTEL_LESSONS_SOFT_MAX). Consolidate near-duplicates (supersede, don't delete) so surfacing stays sharp."
    fi
  fi
  return 0
}

# Self-test
if [ "${BASH_SOURCE[0]}" = "$0" ]; then
  echo "lib/memory.sh self-test:"
  echo "  lessons file: $(lintel_lessons_file 2>/dev/null || echo '(no repo)')"
  echo "  active lessons: $(lessons_count)"
  echo "  surface 'review subagent diff':"
  lessons_surface review subagent diff | sed 's/^/    /'
  memory_budget_check | sed 's/^/  /'
fi
