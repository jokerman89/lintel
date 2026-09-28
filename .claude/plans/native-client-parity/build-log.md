# Build log: native client parity, increment 1

- **cycle_id:** native-client-parity-20260928
- **work_map:** .claude/plans/native-client-parity/work.json
- **tasks_path:** .claude/plans/native-client-parity/plan.md
- **profile:** _default (verified by `workflow_begin`; compliance advisory, voice internal)
- **required_policy:** not required (neutral baseline)
- **Branch:** `jokerman-microsoft-copilot-skill-loading-research` (base `origin/main` 49f2d152)

Entries are appended per package in execution order. Leaf results carry the command and its
observed result. Reviews reference their evidence records.

## Pre-flight (2026-09-28)

- Approved map: `work.json` APPROVED; trio gate PASS (see the PLAN ledger entry).
- Branch: `jokerman-microsoft-copilot-skill-loading-research` (not `main`); tree clean.
- Controls: pack `_default` declares no compliance hooks, so there is no mandatory control. Lintel's
  own hooks are the product under change.
- Code freeze: none declared.
- Deviation: PLAN's "link work.json from todo.md" was not applied. `.claude/plans/todo.md` is a
  byte-bound record (legacy-cleanup `residuals.md` spans), and editing it failed the command-surface
  guard with 550 findings in an LF clone. It was restored in `2a422d2a`, and the guard passes (0
  findings). The initiative is indexed from the working state and MEMORY hot notes at CAPTURE.
- Guard rule for every package: run `bash tests/shape/native-command-surface.sh` in a
  `core.autocrlf=false` clone of the package head (L-061) before review.
- Commit rule: Conventional Commits, no AI-authorship trailer (CONTRIBUTING line 134), new commits
  only (L-055/L-060), and only on this branch (L-059).

## P1: native skills and agents

- **start_ref:** `2a422d2a`
