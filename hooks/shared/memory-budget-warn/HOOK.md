---
name: memory-budget-warn
tier: warn-only
event: PostToolUse (Edit/Write)
fires_on: MEMORY.md over its 200-line auto-load cap, or active lessons over the soft budget
override: not applicable (informational only)
audit: .claude/runtime/audit/hooks.jsonl kind=memory_budget_warn (rate-limited)
---

# memory-budget-warn

Block budgets for the v5 memory home (ADR-0006). Warns when `.claude/memory/MEMORY.md` exceeds
200 lines (Claude Code's native auto-load truncates beyond that — overflow is silently invisible
at session start) or when the count of active (non-superseded) lessons in
`.claude/memory/lessons.md` exceeds the soft budget (default 30).

## Behavior

- Runs `memory_budget_check` from `lib/memory.sh`; prints its WARN lines verbatim.
- Rate-limited to once per hour per repo (`.claude/runtime/state/.last-memory-budget-warn`).
- Pre-v5 repos (no `.claude/lintel-layout.yaml`): exits silently — no budget contract yet.
- Budgets configurable: `LINTEL_MEMORY_INDEX_MAX_LINES`, `LINTEL_LESSONS_SOFT_MAX`.

## Why warn-only

Append-only memory bloat is the documented failure mode of file-based agent memory — but the
right consolidation (which lessons to merge, what to supersede) is a judgment call. The hook
surfaces the breach; the operator (or CAPTURE's update-phase) decides. The remedy is
**supersede, don't delete**: add `superseded_by: L-NNN (date)` instead of editing entries away.
