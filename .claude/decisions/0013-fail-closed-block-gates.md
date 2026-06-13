# ADR-0013: fail-closed block gates — added-lines scanning, git -C follow, mechanical one-way doors

**Status:** Accepted (2026-06-13)
**Decided by:** operator (cli-issues workstream 2: "issues we'll share — overcome them before they hit us")
**Implements:** docs/audit/2026-06-13-cli-issues-craft-synthesis.md (workstream 2, I1/I3) — landed in 0042312
**Note on numbering:** written after ADR-0014–0017; the security decision shipped under the
synthesis's "ADR-0014" label while 0014 became prompt-craft. This record fills the gap so the
control change has its own decision record (repo law: non-trivial decision → ADR).

## Context

Issue-mining of the tools Lintel descends from / runs on found a class we share: claude-code
#60490/#66573 — a PreToolUse hook that intends to block (`exit 2`) but runs `set -euo pipefail`
exits at the FIRST upstream non-zero (a grep with no match, a tr on empty input) with rc 1,
which Claude Code treats as warn-and-proceed. Lintel's two BLOCK hooks (secret-scan-block,
customer-data-block) had exactly this shape: the flagship control was silently downgradeable to
advisory by any internal hiccup. Two adjacent gaps shipped with it: the gates scanned full diff
hunks (context lines caused false positives that train operators to override), and `--auto`
mode had no mechanical notion of a one-way door (gstack #603's sovereignty incident — prose-only
AUTO_DECIDE let an agent auto-decide an irreversible change).

## Decision

1. **BLOCK hooks run without `set -e`.** Explicit exits only: 0 = allow, 2 = block. `-u` and
   `pipefail` stay for correctness. A comment in each hook states the why so a cleanup sweep
   doesn't "fix" it back.
2. **Fail closed when the scanner cannot load.** If `scan_secrets`/`scan_customer` is undefined
   after sourcing `_patterns.sh`, the hook blocks (exit 2) with an explicit error naming the
   override env var — a gate that cannot scan must not silently allow.
3. **Scan added lines only, and follow `git -C` targets.** `hook_git_gate_content` extracts
   `+`-lines of staged ∪ unstaged-tracked diffs and resolves the repo the command actually
   targets, so out-of-cwd commits are not a blind spot (tests/unit/hook-gate-content.sh
   executes both behaviors).
4. **One-way doors are mechanical, not prose.** `lib/auto-decide.sh` classifies a pending
   decision by keyword class (delete/rotate/push-main/provision/…); `--auto` may auto-decide
   reversible gates only — irreversible ones always surface to the operator.

## Consequences

- The I1 regression block in tests/integration/security-controls-fire.sh and
  tests/unit/hook-gate-content.sh keep the closures closed; skill-descriptions-trigger.sh
  guards ADR-0014's craft contract alongside.
- Known residuals stay tracked in the launch register (docs/audit/2026-06-12-launch-readiness-
  register.md §3): newline/line-continuation matcher bypass + newline-forged override (fixed in
  the launch-readiness waves with negative tests), push-path scan of already-committed secrets,
  `git diff` textconv hardening, and the structural close — the real git pre-commit/pre-push
  install (dated 2026-07-15).
- macOS stock bash 3.2: `read -t 0.2` in `_input.sh` errors and the hooks fall back to empty
  input — fixed in the same wave (integer timeout fallback) so the gate holds on every
  supported platform.
