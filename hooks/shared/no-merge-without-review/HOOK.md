---
name: no-merge-without-review
tier: warn-only
event: PreToolUse (Bash)
fires_on: `gh pr merge`, `git merge` to main, similar merge ops
override: pass explicit operator confirmation
audit: ~/.lintel/audit/hooks.jsonl
---

# no-merge-without-review

Warns when a merge to main is about to happen without a recent `/review` or `/plan-eng-review` record. Reads `~/.lintel/review-log/` for current-commit-within-7-days clearance.

## Detection

- Bash command contains `gh pr merge`, `git merge`, or `--squash` patterns
- Target appears to be main
- Cross-reference review log for the current HEAD commit

## What it surfaces

"Merging to main without a passed /review or /plan-eng-review in the last 7 days. Confirm or run /review first."
