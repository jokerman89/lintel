---
name: no-direct-main-push
tier: warn-only
event: PreToolUse (Bash)
fires_on: `git push` command targeting `main` (or `master`)
override: pass explicit per-batch-auth confirmation in conversation
necessity: REQUIRED
gap_if_skipped: "Unreviewed code reaches main; review + founder-approval gates bypassed; no PR audit trail."
audit: ~/.lintel/audit/hooks.jsonl
---

# no-direct-main-push

Warns on `git push origin main` (or equivalent). Per CLAUDE.md auto-mode boundaries: direct push to main requires EXPLICIT per-batch authorization.

## Detection

Regex on the Bash command:
- `git push (origin|<remote>) main`
- `git push --force.*main`
- `git push.*HEAD:main`
- `git push (origin|<remote>) master`

## Why warn-only (not block)

Many Lintel workflows are SHIP-VIA-PR (no direct main push). For these, the hook is a quiet safety net.

Some workflows (e.g. private personal repo, current jokerman-lintel) routinely land on main with operator-confirmed authorization. Block would interrupt every commit.

The warning surfaces "you're about to do something CLAUDE.md flags as needing auth — make sure you have it."

## Override path

The auth happens in conversation, not via flag. Operator says "yes, push to main, I authorize this batch" and the push proceeds. The hook fires either way; auto-confirm replies the warning in audit.

## Companion: branch protection

Real production branches should have GitHub/GitLab branch protection. This hook is a local-side reminder, NOT a substitute for server-side protection.
