#!/usr/bin/env bash
# tests/shape/audit-writes-via-helper.sh
# Asserts (v4.0 Phase 1): all audit JSONL writes route through the unified
# audit_log helper in bin/_audit.sh. No inline JSONL writers may remain in
# bin/ lib/ hooks/ — the only sanctioned writer is bin/_audit.sh.
# Covers BOTH writer forms: literal-path redirects and variable-indirection
# redirects — and scans EVERY shell script under bin/ lib/ hooks/, including the
# extensionless bin/li-* executables (sniffed by shebang, not just *.sh). The
# *.sh-only scope of an earlier version let bin/li-envelope-replay's inline
# writer slip through; that gap is now closed.
# tag: shape v4.0

set -uo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
FAILED=0
pass() { echo "  PASS: $1"; }
fail() { echo "  FAIL: $1"; FAILED=1; }

echo "tests/shape/audit-writes-via-helper.sh"
echo "========================================"

# The single sanctioned writer. Everything else must call audit_log instead.
WHITELIST="bin/_audit.sh"

# Search scope. NOTE: the scan must include EXTENSIONLESS shell scripts — the
# bin/li-* executables ship without a .jsonl/.sh suffix (shebang #!/usr/bin/env
# bash). An earlier version of this guard used `find -name '*.sh'`, which
# silently skipped every bin/li-* script and let bin/li-envelope-replay's inline
# `>> "$AUDIT_LOG"` writer slip through. We now treat any file whose first line
# is a bash/sh shebang as a shell script, in addition to *.sh files.
SCAN_DIRS=("$REPO_ROOT/bin" "$REPO_ROOT/lib" "$REPO_ROOT/hooks")

# Emit the path of every shell script under SCAN_DIRS: *.sh by name, plus any
# extensionless file whose first line is a sh/bash shebang (covers bin/li-*).
_is_shell_script() {
  local file="$1"
  case "$file" in
    *.sh) return 0 ;;
  esac
  # Extensionless (or other) — sniff the shebang. Strip a trailing carriage
  # return first: these scripts ship with CRLF line endings on Windows, so the
  # first line is e.g. "#!/usr/bin/env bash\r" and a naive glob on "*bash"
  # would miss it.
  IFS= read -r first_line < "$file" 2>/dev/null || return 1
  first_line="${first_line%$'\r'}"
  case "$first_line" in
    '#!'*sh|'#!'*sh\ *|'#!'*bash|'#!'*bash\ *) return 0 ;;
    *) return 1 ;;
  esac
}

# An INLINE JSONL append is any writer that bypasses the audit_log helper. Two
# forms exist and BOTH are caught here:
#
#   FORM 1 — literal path: the redirect target on the same line names a .jsonl
#     file directly.  e.g.  printf '{...}' >> "$DIR/foo.jsonl"
#     (the form the first migration pass removed from bin/_jobs.sh,
#      bin/_aliases.sh, lib/pack-resolver.sh, lib/brief-forge.sh,
#      hooks/.../no-trailblazer-without-corpus)
#
#   FORM 2 — variable indirection: a variable is assigned a value containing a
#     .jsonl path ANYWHERE in the same file, and the append redirects to that
#     variable.  The value may be a literal
#     (AUDIT="$LINTEL_HOME/audit/hooks.jsonl") OR a path composed from another
#     variable (AUDIT_LOG="$AUDIT_DIR/envelope-replay.jsonl") — the
#     var-collection regex keys off the literal ".jsonl" substring on the RHS,
#     so both compose-styles are caught.  The redirect is then matched as
#     >> "$AUDIT" / >> $AUDIT / >> "${AUDIT}".
#     (the form the ~19 compliance hooks in hooks/shared/*/run.sh and
#      hooks/entropy-secret-check.sh used, plus bin/li-envelope-replay's
#      >> "$AUDIT_LOG"; all now migrated)
#
#   Scope note: a var that only *reads* a .jsonl path (e.g. REVIEWS_LOG in
#     bin/li-review-read, used only with cat/-f) is NOT flagged — there is no
#     append redirect to it. Purely-transitive aliasing (X="$Y" where $Y holds a
#     .jsonl path, then >> "$X") is not resolved; no such pattern exists in the
#     tree, so adding that resolution would be unused complexity. If one is ever
#     introduced, assign the .jsonl literal at the redirected var instead.
#
# Both forms are what a regression would reintroduce. Any such line outside the
# whitelisted helper is a FAIL. The only sanctioned .jsonl writer is
# bin/_audit.sh (whitelisted).
PATTERN_REDIRECT_LITERAL='>>[[:space:]]*"?[^"]*\.jsonl'

offenders=0
scanned=0

while IFS= read -r f; do
  [ -f "$f" ] || continue
  rel="${f#"$REPO_ROOT/"}"
  # Whitelist the sanctioned writer
  case "$rel" in
    "$WHITELIST") continue ;;
  esac
  scanned=$((scanned + 1))

  # FORM 1 — direct redirect to a literal .jsonl target
  while IFS= read -r hit; do
    [ -z "$hit" ] && continue
    fail "inline JSONL write in $rel (FORM 1 — redirect to literal .jsonl): ${hit#*:}"
    offenders=$((offenders + 1))
  done < <(grep -nE "$PATTERN_REDIRECT_LITERAL" "$f" 2>/dev/null)

  # FORM 2 — variable indirection. Collect variable names assigned a .jsonl
  # path (e.g.  AUDIT="$LINTEL_HOME/audit/hooks.jsonl"  or  HOOK_LOG=foo.jsonl),
  # then flag any append redirect targeting one of those variables
  # (>> "$AUDIT" / >> $AUDIT / >> "${AUDIT}").
  jsonl_vars=$(grep -nE '^[[:space:]]*[A-Za-z_][A-Za-z0-9_]*=.*\.jsonl' "$f" 2>/dev/null \
    | sed -E 's/^[0-9]+:[[:space:]]*([A-Za-z_][A-Za-z0-9_]*)=.*/\1/' | sort -u)
  if [ -n "$jsonl_vars" ]; then
    while IFS= read -r var; do
      [ -z "$var" ] && continue
      while IFS= read -r hit; do
        [ -z "$hit" ] && continue
        fail "inline JSONL write in $rel (FORM 2 — redirect to \$$var which holds a .jsonl path): ${hit#*:}"
        offenders=$((offenders + 1))
      done < <(grep -nE ">>[[:space:]]*\"?\\\$\{?${var}\}?\"?" "$f" 2>/dev/null)
    done <<< "$jsonl_vars"
  fi

done < <(find "${SCAN_DIRS[@]}" -type f 2>/dev/null | while IFS= read -r cand; do
  _is_shell_script "$cand" && printf '%s\n' "$cand"
done)

if [ "$offenders" -eq 0 ]; then
  pass "no inline JSONL writers in bin/ lib/ hooks/ — literal or variable-indirection (scanned $scanned files; bin/_audit.sh whitelisted)"
fi

# Sanity: the sanctioned writer must actually exist and export audit_log
if [ -f "$REPO_ROOT/bin/_audit.sh" ] && grep -qE '^audit_log\(\)' "$REPO_ROOT/bin/_audit.sh"; then
  pass "bin/_audit.sh exists and defines audit_log()"
else
  fail "bin/_audit.sh missing or does not define audit_log()"
fi

echo ""
if [ "$FAILED" -eq 0 ]; then echo "All audit-writes-via-helper assertions PASSED"; exit 0
else echo "Some audit-writes-via-helper assertions FAILED"; exit 1; fi
