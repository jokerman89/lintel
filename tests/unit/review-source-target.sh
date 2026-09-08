#!/usr/bin/env bash
# component: review-source-target-test
# implements: ADR-0005, ADR-0024
# intent: docs/spec-kit.md
# constraints: synthetic repositories and a copied source bundle in a temporary home
# last_intent_review: 2026-09-08
set -euo pipefail
review_source="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
review_parent="$(cd "${TMPDIR:-/tmp}" && pwd -P)"
review_tmp="$(mktemp -d "$review_parent/lintel-review-roots.XXXXXX")"
trap 'case "$review_tmp" in "$review_parent"/lintel-review-roots.*) rm -rf -- "$review_tmp" ;; esac' EXIT
export LINTEL_HOME="$review_tmp/home" GSTACK_HOME="$review_tmp/legacy"
unset LINTEL_AUDIT_DIR LINTEL_REPO_ROOT LINTEL_SOURCE_ROOT
installed="$review_tmp/installed/.github/lintel"
mkdir -p "$installed/bin" "$installed/lib"
cp "$review_source/bin/li-review-log" "$review_source/bin/li-review-read" "$review_source/bin/_audit.sh" "$installed/bin/"
cp "$review_source/lib/paths.sh" "$installed/lib/"
for name in target cwd; do
  repo="$review_tmp/$name"
  mkdir -p "$repo/.claude"
  printf 'layout_version: 5\n' > "$repo/.claude/lintel-layout.yaml"
  git -C "$repo" init -q
  git -C "$repo" symbolic-ref HEAD "refs/heads/$name-branch"
  git -C "$repo" -c user.name=Test -c user.email=test@example.invalid commit --allow-empty -qm "$name"
done
target_head=$(git -C "$review_tmp/target" rev-parse --short HEAD)
cwd_head=$(git -C "$review_tmp/cwd" rev-parse --short HEAD)
test "$target_head" != "$cwd_head"

# Without environment hints, the installed executable finds its sibling helper
# code but records the caller's working repository and commit.
(cd "$review_tmp/cwd" && bash "$installed/bin/li-review-log" '{"skill":"plan-eng-review","status":"CLEAR"}' > "$review_tmp/cwd-write.out"
 bash "$installed/bin/li-review-read" > "$review_tmp/cwd-read.out")
grep -Fq "current_head: $cwd_head" "$review_tmp/cwd-read.out"
test -f "$review_tmp/cwd/.claude/runtime/audit/reviews.jsonl"
test ! -d "$installed/.claude"

export LINTEL_SOURCE_ROOT="$installed" LINTEL_REPO_ROOT="$review_tmp/target"
rc=0
(cd "$review_tmp/cwd" && bash "$installed/bin/li-review-read") > "$review_tmp/target-empty.out" || rc=$?
test "$rc" = 3
grep -Fq "current_head: $target_head" "$review_tmp/target-empty.out"
echo 'PASS: an installed reader does not reuse a conflicting cwd review'

# Execute the skill's real persistence block with concrete review values. Only
# its JSON placeholders are filled; command paths and helper calls stay intact.
awk '
  /^Persist via first-party/ { section=1; next }
  section && /^```bash/ { code=1; next }
  code && /^```/ { exit }
  code { sub(/\r$/, ""); print }
' "$review_source/skills/plan-eng-review/SKILL.md" \
  | sed 's/"status":"\.\.\."/"status":"CLEAR"/g;s/:N/:0/g' > "$review_tmp/persist.sh"
test -s "$review_tmp/persist.sh"
(cd "$review_tmp/cwd" && source "$review_tmp/persist.sh") > "$review_tmp/target-review.out"
grep -Fq "current_head: $target_head" "$review_tmp/target-review.out"
grep -q 'VERDICT: Eng Review CLEAR' "$review_tmp/target-review.out"
target_log="$LINTEL_REPO_ROOT/.claude/runtime/audit/reviews.jsonl"
grep -Fq "\"commit\":\"$target_head\"" "$target_log"
! grep -Fq "\"commit\":\"$cwd_head\"" "$target_log"
test ! -e "$LINTEL_REPO_ROOT/bin/_audit.sh"
echo 'PASS: the real engineering-review snippet writes and reads the target through installed source helpers'

# The one-time legacy import must derive both slug and branch from the target.
for name in target cwd; do
  mkdir -p "$GSTACK_HOME/projects/$name"
  printf '{"skill":"legacy-%s","status":"CLEAR","commit":"%s","timestamp":"%s"}\n' \
    "$name" "$target_head" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    > "$GSTACK_HOME/projects/$name/$name-branch-reviews.jsonl"
done
(cd "$review_tmp/cwd" && bash "$installed/bin/li-review-read" --json) > "$review_tmp/target-json.out"
grep -Fq '"kind":"legacy-target"' "$review_tmp/target-json.out"
! grep -Fq 'legacy-cwd' "$review_tmp/target-json.out"
grep -Fxq "$GSTACK_HOME/projects/target/target-branch-reviews.jsonl" \
  "$LINTEL_REPO_ROOT/.claude/runtime/audit/reviews-legacy-import.done"
echo 'PASS: legacy import follows the target repository and branch'
