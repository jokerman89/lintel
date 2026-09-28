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

## Interruption and recovery (2026-09-28, detected 18:18)

A runtime restart at about 18:14 cleared all three background implementers. Their agent IDs return
not-found, and no lane process was running (checked read-only with `Get-CimInstance`). Recovery used
the durable evidence below and resumed only the unfinished leaves.

- **P1 (`1ac56994`)**
  - Commits:
    - `b2f31102` (li-run)
    - `d5433e08` (complete native skills and agents)
    - `5347c9f0` (agent preamble)
    - `d58ac2b1` (helper rename)
    - `fa2f95bd` (host spelling in native descriptions)
  - Tree: clean.
  - Targeted run (`li-p1-kit-targeted.log`, 17:31, 6 tests in 2522.8 s): FAILED with 1 failure and
    1 error.
    - The failure was `/li:` in a generated agent description. `fa2f95bd` targets it; verification
      is pending.
    - The error was `read_text()` decoding generated UTF-8 with cp1252 in
      `test_modified_managed_file_refuses_entire_update`. That is a test-portability defect.
    - The same log observed 96 native skills and 72 agents, equal to canonical discovery.
  - Full run (`li-p1-copilot-kit.log`): interrupted at 26 tests (21 ok, 5 ERROR, no summary or
    tracebacks). The errors were:
    - `test_canonical_default_caller_child_keeps_verified_parent_and_unbound_child`
    - `test_canonical_required_caller_policy_refuses_missing_drifted_and_conflicting_context`
    - `test_git_verification_directory_linked_and_plain_folder_controls`
    - `test_installed_scaffold_preserves_seeded_short_and_long_plain_targets`
    - `test_installed_scaffold_refuses_late_long_target_changes`
- **P2 (`ff10758e`)**
  - No commits. Uncommitted work inside its boundary: `hooks/shared/_input.sh` (+161 lines),
    `hooks/adapters/{copilot.sh,_json.sh}`, `tests/fixtures/copilot-hooks/` (11 fixtures and a
    README), `tests/unit/copilot-hook-adapter.sh` (38 KB), and additions to `hook-input-adapter.sh`
    and `hook-gate-content.sh`.
  - The work is preserved in place and also backed up outside the repository in the session folder
    (`p2-interrupted-backup`, tracked patch SHA-256 prefix `6E1B951A32476C78`, 14 untracked files).
- **Preparation lane (`497430ea`)**
  - Commits:
    - `948ab2dc` (P4 `cli_support` hints)
    - `b3063189` (registry sources)
  - Tree: clean. The PR-1a documentation leaves had not started.
- **Coordinator actions on the P1 branch after recovery**
  - `c69c177a`: an ordinary merge of `main` `c3ffa153` (PR #110). No conflict; #110's
    `tests/unit/native-command-surface.py` assertion is kept exactly.
  - `d29a78d4`: the ADR-0039 renumber. 38 decision files, no duplicate number, highest 0039.
