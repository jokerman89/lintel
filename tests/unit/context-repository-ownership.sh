#!/usr/bin/env bash
# component: context-ownership-test
# implements: ADR-0005, ADR-0006
# intent: docs/concepts/memory-v2.md
# constraints: synthetic repositories and a temporary shared legacy home
# last_intent_review: 2026-09-08
set -euo pipefail
review_source="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
review_parent="$(cd "${TMPDIR:-/tmp}" && pwd -P)"
review_tmp="$(mktemp -d "$review_parent/lintel-context.XXXXXX")"
trap 'case "$review_tmp" in "$review_parent"/lintel-context.*) rm -rf -- "$review_tmp" ;; esac' EXIT
export LINTEL_HOME="$review_tmp/home"
mkdir -p "$LINTEL_HOME/sessions" "$review_tmp/a/repo" "$review_tmp/b/repo"
for repo in "$review_tmp/a/repo" "$review_tmp/b/repo"; do
  git -C "$repo" init -q
  git -C "$repo" symbolic-ref HEAD refs/heads/shared
  git -C "$repo" -c user.name=Test -c user.email=test@example.invalid commit --allow-empty -qm init
done
source "$review_source/bin/_context.sh"
in_repo() (cd "$1"; export LINTEL_REPO_ROOT="$1"; shift; "$@")
a="$review_tmp/a/repo"; b="$review_tmp/b/repo"
pa=$(in_repo "$a" context_save_path saved)
pb=$(in_repo "$b" context_save_path saved)
[ "$pa" != "$pb" ]
printf 'repository A\n' > "$pa"
printf 'repository B\n' > "$pb"
[ "$(in_repo "$a" context_latest)" = "$pa" ]
[ "$(in_repo "$b" context_latest)" = "$pb" ]
echo 'PASS: identical branch and basename do not mix shared checkpoints'

legacy="$LINTEL_HOME/sessions/shared/20990101-000000-legacy-context-save.md"
printf 'unattributed newest checkpoint\n' > "$legacy"
[ "$(in_repo "$a" context_latest)" = "$pa" ]
printf '**Repository:** %s\nowned legacy\n' "$(cd "$b" && pwd -P)" > "$legacy"
[ "$(in_repo "$a" context_latest)" = "$pa" ]
[ "$(in_repo "$b" context_latest)" = "$legacy" ]
[ -f "$legacy" ]
echo 'PASS: old legacy checkpoint requires exact ownership and is preserved'

mkdir -p "$a/.claude/runtime/sessions/shared"
printf 'layout_version: 5\n' > "$a/.claude/lintel-layout.yaml"
local_old="$a/.claude/runtime/sessions/shared/21000101-000000-old-context-save.md"
printf 'old local checkpoint\n' > "$local_old"
[ "$(in_repo "$a" context_latest)" = "$local_old" ]
[ "$(in_repo "$a" context_list | wc -l | tr -d ' ')" = 2 ]
echo 'PASS: migrated repository retains local history and its owned legacy checkpoint'

# Execute the warm skill's real discovery block from a different repository.
git -C "$b" branch -m target-branch
warm_script="$review_tmp/warm.sh"
awk '/^```bash/{inside=1;next} inside && /^```/{exit} inside{print}' \
  "$review_source/skills/context-warm-sessions/SKILL.md" > "$warm_script"
printf '\nprintf "%%s\\n" "$branch" "$candidates"\n' >> "$warm_script"
target_path=$(cd "$a"; LINTEL_REPO_ROOT="$b" context_save_path target)
case "$target_path" in */target-branch/*) ;; *) exit 1 ;; esac
printf 'target checkpoint\n' > "$target_path"
warm_output=$(cd "$a"; LINTEL_SOURCE_ROOT="$review_source" LINTEL_REPO_ROOT="$b" bash "$warm_script" 1)
[ "$warm_output" = "$(printf 'target-branch\n%s' "$target_path")" ]
if (cd "$a"; LINTEL_SOURCE_ROOT="$review_source" LINTEL_REPO_ROOT="$b" bash "$warm_script" 6) >/dev/null 2>&1; then
  echo 'FAIL: warm sessions accepted an unbounded count'; exit 1
fi
# Same-branch warm lookup must exclude a newer foreign/unattributed legacy save.
warm_output=$(cd "$b"; LINTEL_SOURCE_ROOT="$review_source" LINTEL_REPO_ROOT="$a" bash "$warm_script" 3)
[ "$warm_output" = "$(printf 'shared\n%s\n%s' "$local_old" "$pa")" ]
echo 'PASS: warm skill uses target branch, ownership filtering, and bounded selection'

fixed_save() {
  date() { printf '22000101-000000\n'; }
  context_save_path collision
}
first=$(in_repo "$a" fixed_save)
second=$(in_repo "$a" fixed_save)
[ "$first" != "$second" ]
[ -f "$first" ] && [ ! -s "$first" ]
[ "$(in_repo "$a" context_latest)" = "$local_old" ]
printf 'first completed checkpoint\n' > "$first"
printf 'second completed checkpoint\n' > "$second"
[ "$(in_repo "$a" context_latest)" = "$second" ]
in_repo "$a" context_checkpoint "$second" >/dev/null
echo 'PASS: same-time reservations do not clobber; empty interrupted saves stay undiscoverable'

if in_repo "$a" context_checkpoint "$legacy" >/dev/null 2>&1; then
  echo 'FAIL: foreign checkpoint was automatically admitted'; exit 1
fi
in_repo "$a" context_checkpoint --explicit "$legacy" >/dev/null
if in_repo "$a" context_list '../escape' >/dev/null 2>&1; then
  echo 'FAIL: branch traversal accepted'; exit 1
fi
if in_repo "$a" context_select --root "$b" --path 'private.md' >/dev/null 2>&1; then
  echo 'FAIL: selection argument replaced the target scope'; exit 1
fi
echo 'PASS: explicit historical reads survive; branch traversal and implicit scope replacement fail'

plain="$review_tmp/plain folder"
unborn="$review_tmp/unborn"
mkdir -p "$plain" "$unborn"
git -C "$unborn" init -q
git -C "$unborn" symbolic-ref HEAD refs/heads/not-yet-committed
[ "$(in_repo "$plain" _context_branch)" = no-branch ]
[ "$(in_repo "$plain" _context_repo_slug)" = 'plain folder' ]
plain_save=$(in_repo "$plain" context_save_path notes)
printf 'plain-directory checkpoint\n' > "$plain_save"
[ "$(in_repo "$plain" context_latest)" = "$plain_save" ]
[ "$(in_repo "$unborn" _context_branch)" = not-yet-committed ]
unborn_save=$(in_repo "$unborn" context_save_path notes)
printf 'unborn-branch checkpoint\n' > "$unborn_save"
[ "$(in_repo "$unborn" context_latest)" = "$unborn_save" ]
echo 'PASS: plain folders and unborn branches retain usable checkpoint paths'

git -C "$a" checkout -q --detach HEAD
[ "$(in_repo "$a" _context_branch)" = HEAD ]
detached=$(in_repo "$a" context_save_path detached)
case "$detached" in */HEAD/*-detached-context-save.md) ;; *)
  echo 'FAIL: detached HEAD checkpoint has the wrong bucket'; exit 1 ;;
esac
printf 'detached checkpoint\n' > "$detached"
[ "$(in_repo "$a" context_latest)" = "$detached" ]
[ "$(in_repo "$a" context_list HEAD)" = "$detached" ]
in_repo "$a" context_checkpoint "$detached" >/dev/null
warm_output=$(cd "$b"; LINTEL_SOURCE_ROOT="$review_source" LINTEL_REPO_ROOT="$a" bash "$warm_script" 1)
[ "$warm_output" = "$(printf 'HEAD\n%s' "$detached")" ]
git -C "$a" checkout -q shared
[ "$(in_repo "$a" context_latest)" = "$second" ]
[ "$(in_repo "$a" context_list HEAD)" = "$detached" ]
if in_repo "$a" context_list 'HEAD/../escape' >/dev/null 2>&1; then
  echo 'FAIL: detached sentinel bypassed path validation'; exit 1
fi
echo 'PASS: detached HEAD save, discovery and warming preserve the historical HEAD bucket'
