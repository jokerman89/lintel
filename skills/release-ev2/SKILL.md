---
name: li-release-ev2
layer: foundation
v1_alias: [li-ship]
description: Land the current branch — verifies review readiness, squashes WIP commits, opens PR.
color: green
tools: Read, Bash, Edit, Grep, Glob
voice: internal
cli_support: [claude-code, codex]
---

# /release-ev2

The release-engineer skill. Runs the full ship gauntlet: review readiness check → WIP commit squash → conventional-commits message → PR opened. Optional auto-push to feature branch (NEVER to `main` without explicit per-call auth).

## When to use

- Branch is feature-complete, tests pass locally, ready to land
- `/plan-eng-review` has cleared (dashboard CLEAR within 7 days, current commit)
- Need to consolidate WIP commits into clean atomic commits

## When NOT to use

- Tests fail — fix first, then `/release-ev2`
- Review readiness dashboard says NOT CLEARED — run `/plan-eng-review` first
- Direct push to `main` — that's separate explicit per-batch auth

## Inputs

- Optional `--no-push` — squash + commit only, don't open PR
- Optional `--draft` — open PR as draft (default: ready for review)
- Optional `--title <text>` — override PR title (default: derived from commit messages)

## Workflow

1. **Review readiness check** — run `gstack-review-read`, verify Eng Review CLEAR within 7 days for current commit. If not: surface + ask whether to run `/plan-eng-review` first or proceed anyway.
2. **Sanity scan** — secret patterns, customer-data patterns, PII patterns. Block if any hit.
3. **WIP commit detection** — scan recent commits for `WIP:` prefix. Group into logical chunks (file overlap heuristic).
4. **Squash plan** — surface proposed squash via AskUserQuestion. Operator approves before any history rewrite.
5. **Filter-squash** — `git rebase -i` with autosquash, OR `git reset --soft` + recommit. Generate conventional-commits messages from `[gstack-context]` blocks in WIP commits.
6. **Push to feature branch** — `git push origin <branch>`. If `--no-push`: stop here.
7. **PR open** — `gh pr create --title "<title>" --body "<generated body>"`. Body includes: summary, test plan, review-log status, related-issue refs.
8. **Report PR URL** to operator.

## Report format

```
Ship Status: <branch>

✓ Review readiness: Eng Review CLEAR (PLAN, commit 7e7a021, 2026-05-27)
✓ Sanity scan: no secrets / customer-data / PII detected
⚠ WIP commits found: 3 — will squash to 1 atomic commit
✓ Push: pushed origin/feature/lintel:li-phase-2-batch-4
✓ PR opened: https://github.com/jokerman89/jokerman-lintel/pull/4

Squashed history:
- f19d388 → kept
- WIP commits 8a7b2c, 9d4e1f, ab3c5d → squashed to one commit
  Title: feat(skills): Phase 2 batch 4 — ship pipeline (4 skills)
```

## Compliance integration

- 5 always-on rules run as part of sanity scan (no customer-data, no secrets, no production-mutation auth, MS SSO, first-party-first).
- If sanity scan blocks: report which pattern hit + which file + offer to abort.
- NEVER auto-pushes to `main`. Requires explicit per-batch auth per Layer 2.

## Voice tier note

`voice: internal`. Ship is engineering-internal — no Trailblazer voice involved.

## Failure modes

- **Review NOT CLEARED:** ask whether to skip (require explicit override) or run `/plan-eng-review` first.
- **Sanity scan hits:** block ship. Do NOT push partial state.
- **Squash conflicts:** report files in conflict, ask operator to resolve manually, then re-run `/release-ev2`.
- **`gh` not authenticated:** report + suggest `gh auth login`.
- **PR open fails (network, perms):** push succeeded but PR didn't — operator opens manually via URL.

## Examples

**Clean ship:**
```
> /release-ev2
[review check, sanity, squash plan, push, PR]
✓ PR opened: <url>
```

**Blocked by sanity:**
```
> /release-ev2
✗ Sanity blocked: secret pattern detected in src/config.ts:42
  Pattern: gho_<redacted>
  Action: remove the secret, commit fix, re-run /release-ev2
```

**No-push variant:**
```
> /release-ev2 --no-push
[squash + sanity only; no push]
✓ Ready to push. Run `git push origin <branch>` when ready.
```

## See also

- `/plan-eng-review` — required gate before /release-ev2
- `/release-deploy-ev2` — extends /release-ev2 with deploy step
- `/review` — diff-scoped lighter pre-landing review
