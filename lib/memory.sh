#!/usr/bin/env bash
# component: lintel-memory
# implements: ADR-0006
# intent: docs/concepts/memory-v2.md
# constraints: token-frugal — surfacing is grep-rank, no embeddings, no DB; reads work without Python
# last_intent_review: 2026-09-23
#
# lib/memory.sh — mechanical memory helpers (v5 memory v2).
# The awk program below is one of exactly two implementations of the lesson
# grammar; bin/li-lessons.py is the other (allocation, by-ID retrieval,
# add/update/supersede, promotion). Both pass tests/fixtures/lessons/.
#
#   lessons_surface <keyword...>     → top-3 relevant lessons (id — title [score])
#   lessons_find_related <keyword...>→ all matching lesson ids+titles (for the
#                                      CAPTURE update-phase: add/update/supersede/no-op)
#   lessons_count                    → number of non-superseded lessons
#   lessons_recent [N]               → the N active lessons with the highest IDs (digest)
#   lessons_index                    → every lesson heading, superseded ones marked
#   lessons_store_paths              → root, store and any ignored second store (TSV)
#   lessons_legacy_operator          → read-only view of ~/.lintel/lessons.jsonl
#   lessons_helper <command> ...     → bin/li-lessons.py; refuses visibly without Python
#   memory_budget_check              → warn lines if MEMORY.md / lessons.md
#                                      exceed their block budgets (ADR-0006)
#
# Grammar: a lesson heading is `## L-<digits> — <title>` (` - ` is also read)
# outside fenced code; a block runs to the line before the next level-two
# heading outside a fence. `superseded_by:` / `supersedes: L-NNN` markers may
# sit on any block line, optionally behind `> `, with trailing text. A block
# with `superseded_by:` is kept in the file but skipped by surfacing and counts
# (supersede, don't delete). Unparseable `## L-` headings, duplicate IDs,
# missing supersede targets and dated `## YYYY-MM-DD` legacy headings are
# reported on stderr; stdout formats are unchanged.

_MEMORY_LIB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
command -v lintel_lessons_file >/dev/null 2>&1 || source "$_MEMORY_LIB_DIR/paths.sh"

# Block budgets (Letta-style: hard caps force consolidation, the same rule
# native MEMORY.md applies with its 200-line auto-load cap).
LINTEL_MEMORY_INDEX_MAX_LINES="${LINTEL_MEMORY_INDEX_MAX_LINES:-200}"
LINTEL_LESSONS_SOFT_MAX="${LINTEL_LESSONS_SOFT_MAX:-30}"

# The project store is always the lintel_lessons_file resolution. Also names a
# second store that exists but is not read, so its lessons are never hidden.
lessons_store_paths() {
  local root file new legacy
  root="$(lintel_repo_root)"
  [ -n "$root" ] && [ -d "$root" ] || return 1
  file="$(lintel_lessons_file)" || return 1
  new="$root/.claude/memory/lessons.md"
  legacy="$root/tasks/lessons.md"   # legacy-fallback-ok
  printf 'root\t%s\nstore\t%s\n' "$root" "$file"
  if [ "$file" = "$legacy" ] && [ -e "$new" ]; then
    printf 'ignored\t%s\n' "$new"
  elif [ "$file" = "$new" ] && [ -e "$legacy" ]; then
    printf 'ignored\t%s\n' "$legacy"
  fi
}

_LESSONS_FILE=""
_lessons_store() {
  local listing key value store="" ignored=""
  _LESSONS_FILE=""
  listing="$(lessons_store_paths 2>/dev/null)" || {
    echo "WARN [lintel/lessons]: no project lessons store (unobserved)" >&2
    return 1
  }
  while IFS=$'\t' read -r key value; do
    case "$key" in
      store) store="$value" ;;
      ignored) ignored="$value" ;;
    esac
  done <<< "$listing"
  [ -z "$ignored" ] || echo "WARN [lintel/lessons]: reading $store; also present and ignored: $ignored" >&2
  if [ ! -f "$store" ]; then
    echo "WARN [lintel/lessons]: project lessons store absent (unobserved): $store" >&2
    return 1
  fi
  _LESSONS_FILE="$store"
}

_LESSONS_AWK='
function lead(s,   i) { i = 0; while (i < 4 && substr(s, i + 1, 1) == " ") i++; return i }
function run(s, start, ch,   n) { n = 0; while (substr(s, start + n, 1) == ch) n++; return n }
function fence_open(s,   i, c, n) {
  i = lead(s); if (i > 3) return 0
  c = substr(s, i + 1, 1); if (c != "`" && c != "~") return 0
  n = run(s, i + 1, c); if (n < 3) return 0
  fch = c; flen = n; return 1
}
function fence_close(s,   i, n) {
  i = lead(s); if (i > 3) return 0
  n = run(s, i + 1, fch); if (n < flen) return 0
  return substr(s, i + 1 + n) ~ /^[ \t]*$/
}
function diag(line, code, detail) { nd++; dline[nd] = line; dtext[nd] = "line " line ": " code ": " detail }
function close_block() { if (cur) { cur = 0 } }
BEGIN {
  n = 0; cur = 0; infence = 0; nd = 0; nm = 0
  nk = split(tolower(ENVIRON["LESSONS_KEYWORDS"]), kw, /[ \t]+/)
}
{
  sub(/\r$/, ""); s = $0
  if (infence) {
    if (fence_close(s)) infence = 0
    if (cur) body[cur] = body[cur] " " tolower(s)
    next
  }
  if (fence_open(s)) { infence = 1; if (cur) body[cur] = body[cur] " " tolower(s); next }
  if (s ~ /^##([ \t]|$)/) {
    close_block()
    if (s ~ /^## L-[0-9]+([ \t]*$| — | - )/) {
      match(s, /^## L-[0-9]+/); id = substr(s, 4, RLENGTH - 3); num = substr(id, 3) + 0
      n++; cur = n; head[n] = substr(s, 4); ids[n] = id; nums[n] = num; lines[n] = NR; sup[n] = 0; body[n] = ""
      if (num in first) diag(NR, "duplicate_id", "duplicate lesson ID " id " (first at line " first[num] ")")
      else first[num] = NR
    } else if (s ~ /^## L-/) {
      diag(NR, "unparseable_heading", "unparseable lesson heading: " s)
    } else if (s ~ /^## [0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]/) {
      diag(NR, "dated_heading", "dated heading is an unindexed legacy entry: " s)
    }
    next
  }
  if (cur) {
    body[cur] = body[cur] " " tolower(s)
    if (s ~ /^[ \t]*(>[ \t]*)?(superseded_by|supersedes):[ \t]*L-[0-9]+/) {
      if (s ~ /^[ \t]*(>[ \t]*)?superseded_by:/) sup[cur] = 1
      t = s; sub(/^[^:]*:[ \t]*/, "", t); match(t, /^L-[0-9]+/)
      nm++; mline[nm] = NR; mid[nm] = substr(t, 1, RLENGTH); mnum[nm] = substr(t, 3, RLENGTH - 2) + 0
    }
  }
}
function score(i,   k, hay, c) {
  hay = tolower(head[i]) body[i]; c = 0
  for (k = 1; k <= nk; k++) if (kw[k] != "" && index(hay, kw[k]) > 0) c++
  return c
}
END {
  for (m = 1; m <= nm; m++)
    if (!(mnum[m] in first)) diag(mline[m], "missing_supersede_target", "marker names " mid[m] ", which does not exist")
  for (i = 1; i <= nd; i++) order[i] = i
  for (i = 2; i <= nd; i++) {
    v = order[i]; j = i - 1
    while (j >= 1 && dline[order[j]] > dline[v]) { order[j + 1] = order[j]; j-- }
    order[j + 1] = v
  }
  for (i = 1; i <= nd; i++) printf "WARN [lintel/lessons]: %s (%s)\n", dtext[order[i]], ENVIRON["LESSONS_DISPLAY"] > "/dev/stderr"
  if (mode == "count") {
    c = 0; for (i = 1; i <= n; i++) if (!sup[i]) c++
    print c + 0
  } else if (mode == "index") {
    for (i = 1; i <= n; i++) print head[i] (sup[i] ? " (superseded)" : "")
  } else if (mode == "recent") {
    k = 0
    for (i = 1; i <= n; i++) if (!sup[i]) { k++; pick[k] = i }
    for (i = 2; i <= k; i++) {
      v = pick[i]; j = i - 1
      while (j >= 1 && (nums[pick[j]] > nums[v] || (nums[pick[j]] == nums[v] && lines[pick[j]] > lines[v]))) { pick[j + 1] = pick[j]; j-- }
      pick[j + 1] = v
    }
    for (i = (k > topn ? k - topn + 1 : 1); i <= k; i++) print head[pick[i]]
  } else if (mode == "surface") {
    count = 0
    for (i = 1; i <= n; i++) {
      if (sup[i]) continue
      c = score(i)
      if (c > 0) { count++; scores[count] = c; titles[count] = head[i] }
    }
    # selection sort, descending score (top-N only; ties keep no particular order)
    for (i = 1; i <= count && i <= topn; i++) {
      best = i
      for (j = i + 1; j <= count; j++) if (scores[j] > scores[best]) best = j
      t = scores[i]; scores[i] = scores[best]; scores[best] = t
      s = titles[i]; titles[i] = titles[best]; titles[best] = s
      printf "%s [matched %d]\n", titles[i], scores[i]
    }
  }
}
'

_lessons_awk() { # <mode> <keywords> <top-n>
  LESSONS_KEYWORDS="$2" LESSONS_DISPLAY="$_LESSONS_FILE" \
    awk -v mode="$1" -v topn="${3:-3}" "$_LESSONS_AWK" "$_LESSONS_FILE"
}

# Score lesson blocks by keyword hits, skip superseded, print top-N.
# Args: <keyword...>   (env: LESSONS_TOP_N, default 3)
lessons_surface() {
  [ $# -gt 0 ] || return 0
  _lessons_store || return 0
  _lessons_awk surface "$*" "${LESSONS_TOP_N:-3}"
}

# All matching lessons (no top-N cap) — input to the CAPTURE update-phase,
# where each candidate lesson is classified add / update / supersede / no-op
# against what already exists.
lessons_find_related() {
  LESSONS_TOP_N=999 lessons_surface "$@"
}

# Count non-superseded lessons (budget input).
lessons_count() {
  _lessons_store || { printf '0'; return 0; }
  _lessons_awk count "" 0
}

# The digest view: the N active lessons with the highest numeric IDs, ascending.
lessons_recent() {
  _lessons_store || return 0
  _lessons_awk recent "" "${1:-3}"
}

# Every lesson heading in file order; superseded blocks end with "(superseded)".
lessons_index() {
  _lessons_store || return 0
  _lessons_awk index "" 0
}

# Legacy operator lessons are shown read-only; nothing imports or writes them.
lessons_legacy_operator() {
  local file="$LINTEL_HOME/lessons.jsonl"
  if [ ! -f "$file" ]; then
    printf 'legacy operator lessons, not ID-managed: none observed at %s\n' "$file"
    return 0
  fi
  printf 'legacy operator lessons, not ID-managed (read-only view of %s):\n' "$file"
  cat "$file"
}

# Allocation, by-ID retrieval and conditional writes need Python 3.9+. Without
# it they refuse visibly; the awk reads above keep working.
lessons_helper() {
  local python="${LINTEL_PYTHON:-}" candidate
  if [ -z "$python" ]; then
    for candidate in python3 python; do
      if command -v "$candidate" >/dev/null 2>&1 &&
          "$candidate" -c 'import sys; raise SystemExit(sys.version_info < (3, 9))' >/dev/null 2>&1; then
        python="$candidate"
        break
      fi
    done
  fi
  if [ -z "$python" ]; then
    echo "ERROR [lintel/lessons]: Python 3.9+ is required for lesson allocation, retrieval and conditional writes; nothing was written. Surfacing, counts and the digest still work." >&2
    return 2
  fi
  "$python" "$_MEMORY_LIB_DIR/../bin/li-lessons.py" "$@"
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
