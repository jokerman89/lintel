---
name: no-merge-without-review
tier: warn-only
event: PreToolUse (Bash)
fires_on: `gh pr merge`, `git merge` to main, similar merge ops
override: pass explicit operator confirmation
audit: .claude/runtime/audit/hooks.jsonl
---

# no-merge-without-review

Warns when a detected merge lacks sufficient content-bound review evidence. It calls
the trusted source's `bin/li-review-read`, which selects the latest applicable
decision before checking its exact status, acceptance and result identity. Legacy
`CLEARED` strings, short-HEAD matches and elapsed time cannot suppress the warning.

The hook stays opt-in and advisory; this change does not register or activate it.
Exit 0 is **not** permission or enforcement. SHIP additionally checks same-context QA
through the shared [evidence procedure](../../../skills/review/references/evidence.md).

## Detection

- Recognizes `gh pr merge` or a `git merge` command naming main/master.
- Uses the source bundle from `LINTEL_SOURCE_ROOT` (otherwise its own installed
  root), and the target from `LINTEL_REPO_ROOT` (otherwise the caller's repository).
- `LINTEL_REVIEW_CONTEXT` names the explicit expected context.
  `LINTEL_REVIEW_CORROBORATION` names separately supplied host/human provenance.
  `LINTEL_REVIEW_SKILL` selects the gate, default `review`.
- Missing context, later rejection, changed selected input, insufficient provenance
  or a reader error leaves the warning active. It never searches for any old PASS.

## What it surfaces

"Merge detected without a current content-bound review decision. Inspect
li-review-read diagnostics and satisfy the actual review requirement."
