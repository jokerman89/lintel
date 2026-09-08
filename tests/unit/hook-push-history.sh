#!/usr/bin/env bash
# component: hook-push-history-test
# implements: ADR-0013
# intent: hooks/shared/secret-scan-block/HOOK.md
# constraints: temporary local repositories and synthetic markers; no push/fetch
# last_intent_review: 2026-09-08
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TEST_PARENT="$(cd "${TMPDIR:-/tmp}" && pwd -P)"
TEST_TMP="$(mktemp -d "$TEST_PARENT/lintel-git-gate.XXXXXX")" || exit 1
cleanup() {
  case "$TEST_TMP" in "$TEST_PARENT"/lintel-git-gate.*)
    [ -d "$TEST_TMP" ] && [ "$(cd "$TEST_TMP" && pwd -P)" = "$TEST_TMP" ] && rm -rf -- "$TEST_TMP" ;;
  esac
}
trap cleanup EXIT
export GIT_CONFIG_NOSYSTEM=1 GIT_CONFIG_GLOBAL="$TEST_TMP/absent-config" XDG_CONFIG_HOME="$TEST_TMP/config"
export LINTEL_HOME="$TEST_TMP/home" LINTEL_AUDIT_DIR="$TEST_TMP/audit" LINTEL_REPO_ROOT="$TEST_TMP"
mkdir -p "$LINTEL_AUDIT_DIR"
source "$ROOT/hooks/shared/_input.sh"
source "$ROOT/hooks/shared/_patterns.sh"
failed=0
pass() { printf 'PASS: %s\n' "$1"; }
fail() { printf 'FAIL: %s\n' "$1"; failed=1; }
init_repo() {
  mkdir -p "$1"
  git -C "$1" init -q -b main
  git -C "$1" config user.email fixture@example.invalid
  git -C "$1" config user.name fixture
  git -C "$1" config core.autocrlf false
  printf 'clean\n' > "$1/note"
  git -C "$1" add note
  git -C "$1" commit -qm seed
  git -C "$1" remote add origin https://example.invalid/no-network
}
has_secret() {
  local content rc=0
  content=$(cd "$1" && hook_git_gate_content "$2") || rc=$?
  if [ "$rc" -eq 0 ] && [ -n "$(scan_secrets tier1 "$content")" ]; then pass "$3"; else fail "$3 (collection rc=$rc)"; fi
}
clean_scan() {
  local content rc=0
  content=$(cd "$1" && hook_git_gate_content "$2") || rc=$?
  if [ "$rc" -eq 0 ] && [ -z "$(scan_secrets tier1 "$content")" ]; then pass "$3"; else fail "$3 (collection rc=$rc)"; fi
}
blocked_scan() {
  local rc=0
  (cd "$1" && hook_git_gate_content "$2") >/dev/null 2>&1 || rc=$?
  [ "$rc" -eq 2 ] && pass "$3" || fail "$3 (rc=$rc)"
}
hook_status() {
  local rc=0
  (cd "$1" && bash "$ROOT/hooks/shared/$2/run.sh" "$3" </dev/null) >/dev/null 2>&1 || rc=$?
  [ "$rc" = "$4" ] && pass "$5" || fail "$5 (rc=$rc)"
}

# Construct a synthetic scanner fixture without putting a literal token in the
# repository. This value is not a usable credential.
token="AKIA""ABCDEFGHIJKLMNOP"
repo="$TEST_TMP/repo with spaces"
init_repo "$repo"
seed=$(git -C "$repo" rev-parse HEAD)
git -C "$repo" update-ref refs/remotes/origin/main "$seed"
git -C "$repo" branch --set-upstream-to=origin/main main >/dev/null
printf 'key=%s\n' "$token" >> "$repo/note"
git -C "$repo" commit -qam introduce
printf 'clean\n' > "$repo/note"
git -C "$repo" commit -qam remove
for n in {1..12}; do git -C "$repo" commit --allow-empty -qm "later-$n"; done
has_secret "$repo" 'git push' 'default push scans every outgoing commit, including an added then removed secret'
hook_status "$repo" secret-scan-block 'git push origin main:main' 2 'actual secret hook blocks historical introduction'
# Both actual gates must inspect a supported wrapper or fail explicitly. The
# customer marker is synthetic and deliberately outside a real identity range.
printf 'fixture=%s\n' '000000-0000' >> "$repo/note"
git -C "$repo" commit -qam synthetic-customer-marker
for hook in secret-scan-block customer-data-block; do
  hook_status "$repo" "$hook" 'command -- git push origin HEAD:main' 2 "$hook scans command -- wrapper"
  hook_status "$repo" "$hook" 'env -i git push origin HEAD:main' 2 "$hook rejects environment-clearing wrapper"
  hook_status "$repo" "$hook" 'sudo git push origin HEAD:main' 2 "$hook rejects identity-changing wrapper"
  hook_status "$repo" "$hook" 'unknown-wrapper git push origin HEAD:main' 2 "$hook rejects unknown wrapper"
done
git -C "$repo" checkout -qb clean "$seed"
clean_scan "$repo" 'git push origin HEAD:refs/heads/clean' 'explicit clean source does not scan unrelated local branches'
clean_scan "$repo" 'command -- git push origin HEAD:refs/heads/clean' 'supported command wrapper permits clean history'
clean_scan "$repo" 'command env git push origin HEAD:refs/heads/clean' 'nested plain wrappers permit clean history'
for hook in secret-scan-block customer-data-block; do
  hook_status "$repo" "$hook" 'git push origin clean:clean && sudo git push origin main:main' 2 "$hook rejects uninspected later wrapper after clean operation"
done
blocked_scan "$repo" 'sudo git push origin main:main' 'collector rejects unsupported wrapper instead of returning empty content'
blocked_scan "$repo" 'true' 'collector requires an inspected Git operation'
has_secret "$repo" 'git push origin refs/heads/main:refs/heads/release' 'non-HEAD source and different destination are scanned'
has_secret "$repo" 'git push origin +main:release clean:clean' 'multiple refspecs and forced source are all scanned'
has_secret "$TEST_TMP" "git -C 'repo with spaces' push origin main:main" 'quoted git -C target outside the current repository'
has_secret "$TEST_TMP" "cd 'repo with spaces' && git push origin main:main" 'literal cd target is followed before push'
has_secret "$repo" 'git push --all origin' 'bulk branch push includes non-HEAD history'
git -C "$repo" tag history main
has_secret "$repo" 'git push --tags origin' 'tag push scans the referenced commit history'
git -C "$repo" config remote.origin.push refs/heads/main:refs/heads/release
has_secret "$repo" 'git push origin' 'configured default refspec replaces the current branch selection'
git -C "$repo" update-ref refs/remotes/origin/main main
has_secret "$repo" 'git push origin main' 'bare ref with configured destination cannot exclude an unrelated tracking tip'
git -C "$repo" config --unset-all remote.origin.push
has_secret "$repo" 'git push origin main:refs/heads/main' 'local tracking tip cannot exclude history from a rewritten or deleted destination'
git -C "$repo" config remote.origin.pushurl https://example.invalid/another-target
has_secret "$repo" 'git push origin main:refs/heads/main' 'separate push URL cannot reuse fetch destination exclusions'
git -C "$repo" config --unset-all remote.origin.pushurl
git -C "$repo" config push.default current
clean_scan "$repo" 'git push' 'push.default=current scans the current clean branch'
git -C "$repo" config push.default matching
blocked_scan "$repo" 'git push' 'ambiguous matching default fails explicitly'
git -C "$repo" config push.default simple
clean_scan "$repo" 'git push --delete origin main' 'deleting a remote ref introduces no content'

# A newly merged blob can be absent from both parents. Scan pairwise merge
# diffs even when log.diffMerges would otherwise suppress those changes.
merge_repo="$TEST_TMP/merge"
init_repo "$merge_repo"
merge_seed=$(git -C "$merge_repo" rev-parse HEAD)
git -C "$merge_repo" update-ref refs/remotes/origin/main "$merge_seed"
git -C "$merge_repo" checkout -qb side
printf 'side\n' > "$merge_repo/note"; git -C "$merge_repo" commit -qam side
git -C "$merge_repo" checkout -q main
printf 'main\n' > "$merge_repo/note"; git -C "$merge_repo" commit -qam main
git -C "$merge_repo" merge --no-commit side >/dev/null 2>&1 || true
printf 'resolution=%s\n' "$token" > "$merge_repo/note"
git -C "$merge_repo" add note; git -C "$merge_repo" commit -qm resolved
git -C "$merge_repo" config log.diffMerges off
has_secret "$merge_repo" 'git push origin main:main' 'merge-resolution additions remain visible despite repository log configuration'

# Local replacement refs affect display, but pack transfer uses the originals.
replace_repo="$TEST_TMP/replace"
init_repo "$replace_repo"
replace_seed=$(git -C "$replace_repo" rev-parse HEAD)
printf 'key=%s\nfixture=%s\n' "$token" '000000-0000' >> "$replace_repo/note"
git -C "$replace_repo" commit -qam originals
git -C "$replace_repo" replace HEAD "$replace_seed"
replace_display=$(git -C "$replace_repo" show HEAD:note)
if [ -z "$(scan_secrets tier1 "$replace_display")" ] && [ -z "$(scan_customer "$replace_display")" ]; then
  pass 'replacement fixture hides both synthetic markers in ordinary Git display'
else fail 'replacement fixture did not hide the markers'; fi
has_secret "$replace_repo" 'git push origin HEAD:main' 'collector inspects original history despite local replacement refs'
for hook in secret-scan-block customer-data-block; do
  hook_status "$replace_repo" "$hook" 'git push origin HEAD:main' 2 "$hook blocks original content hidden by a replacement ref"
done

# Commit errors must reach both real wrappers, including their existing audit
# and override paths. Exported fake Git is inherited by the hook subprocess.
git() {
  case " $* " in *' diff '*) return 128 ;; *) command git "$@" ;; esac
}
export -f git
blocked_scan "$repo" 'git commit -am update' 'failed index reads are not an empty successful scan'
for hook in secret-scan-block customer-data-block; do
  hook_status "$repo" "$hook" 'git commit -am update' 2 "$hook blocks Git collection failure"
done
hook_status "$repo" secret-scan-block 'LINTEL_OVERRIDE_SECRET=1 git commit -am update' 0 'secret override remains available before collection'
hook_status "$repo" customer-data-block 'LINTEL_OVERRIDE_CUSTOMER_DATA=1 git commit -am update' 0 'customer override remains available before collection'
unset -f git
if grep -q '"reason":"collection-unavailable"' "$LINTEL_AUDIT_DIR/hooks.jsonl" && grep -q '"override":"true"' "$LINTEL_AUDIT_DIR/hooks.jsonl"; then
  pass 'collection blocks and explicit overrides leave audit records'
else fail 'missing block or override audit record'; fi
git() {
  case " $* " in *' log '*) return 128 ;; *) command git "$@" ;; esac
}
export -f git
blocked_scan "$repo" 'git push origin clean:clean' 'failed history reads are not an empty successful scan'
hook_status "$repo" secret-scan-block 'git push origin clean:clean' 2 'actual push hook blocks failed history collection'
unset -f git
git() { return 128; }
export -f git
blocked_scan "$repo" 'git push origin main:main' 'failed repository inspection is explicit'
unset -f git
blocked_scan "$repo" 'git -C absent commit -am update' 'missing target directory is explicit'
blocked_scan "$repo" 'git push origin missing:release' 'unresolvable source ref is explicit'
blocked_scan "$repo" 'git push origin "$BRANCH":release' 'dynamic shell expansion is never evaluated'
blocked_scan "$repo" 'git add note && git commit -m update' 'a preceding index mutation requires separate inspection'
clean_scan "$repo" 'git commit -m clean' 'ordinary clean commit flow succeeds'
printf 'plain edit\n' >> "$repo/note"
clean_scan "$repo" 'true && git commit -am update' 'ordinary tracked edit flow succeeds'
hook_status "$repo" secret-scan-block 'git commit -am update' 0 'actual hook allows a clean tracked edit'
printf '++%s\n' "$token" >> "$repo/note"
has_secret "$repo" 'git commit -am update' 'an added line starting with plus signs is content, not a diff header'
git -C "$repo" config color.ui always
has_secret "$repo" 'git commit -am update' 'forced Git color cannot hide commit patch content'
has_secret "$repo" 'git push origin main:main' 'forced Git color cannot hide push history content'

# Break only the scanner's pattern evaluation, leaving command matching and
# audit grep calls intact. Exercise the actual block wrappers with nonempty
# content so an empty-content shortcut cannot make this test vacuous.
grep() {
  local arg
  for arg in "$@"; do
    case "$arg" in *'[A-Za-z0-9]{36}'*|*'[a-zA-Z0-9._%+-]'*) return 2 ;; esac
  done
  command grep "$@"
}
export -f grep
for hook in secret-scan-block customer-data-block; do
  hook_status "$repo" "$hook" 'git push origin clean:clean' 2 "$hook blocks a failed pattern scan on clean content"
done
hook_status "$repo" secret-scan-block 'LINTEL_OVERRIDE_SECRET=1 git push origin clean:clean' 0 'secret override remains usable with broken pattern evaluation'
hook_status "$repo" customer-data-block 'LINTEL_OVERRIDE_CUSTOMER_DATA=1 git push origin clean:clean' 0 'customer override remains usable with broken pattern evaluation'
mkdir -p "$TEST_TMP/artifact"
printf 'ordinary text\n' > "$TEST_TMP/artifact/dom.html"
for hook in no-secrets-in-edit no-customer-data-in-message no-customer-data-in-screenshot; do
  payload='ordinary text'
  [ "$hook" != no-customer-data-in-screenshot ] || payload="$TEST_TMP/artifact"
  warn_rc=0
  warn_output=$(cd "$repo" && bash "$ROOT/hooks/shared/$hook/run.sh" "$payload" </dev/null 2>&1) || warn_rc=$?
  case "$warn_output" in
    *'pattern scan unavailable'*) [ "$warn_rc" -eq 0 ] && pass "$hook warns without blocking on scan failure" || fail "$hook blocked on scan failure (rc=$warn_rc)" ;;
    *) fail "$hook did not report scan failure (rc=$warn_rc)" ;;
  esac
done
unset -f grep
if grep -q '"reason":"scan-unavailable"' "$LINTEL_AUDIT_DIR/hooks.jsonl"; then
  pass 'pattern scan failures leave audit records'
else fail 'missing pattern scan failure audit record'; fi
exit "$failed"
