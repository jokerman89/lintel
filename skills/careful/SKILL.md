---
name: careful
layer: foundation
description: Slow-down mode for high-stakes work — extra gates, double-confirm before mutations.
color: red
tools: Read, Bash, Grep, Glob, Edit
voice: internal
necessity: OPTIONAL
gap_if_skipped: "High-stakes mutations run at normal cadence — no per-mutation confirm, no stated rollback path, no elevated audit. Fine for routine work; risky for irreversible or production-adjacent changes."
cli_support:
  - cli: claude-code
    level: full
  - cli: codex
    level: degraded
---

# /li:careful

A mode-switching skill that wraps the current task in extra rigor: every mutation gets a pre-flight AskUserQuestion, every command is shown before execution, every assumption is named explicitly. Use when the work is production-adjacent, irreversible, or operating on data you cannot afford to corrupt.

Not a standalone workflow — invokes other skills (or your direct work) with elevated caution.

## When to use

- Production database migration about to run
- Destructive git operation (force push, branch delete, history rewrite)
- Working in a frozen-zone file per repo's CLAUDE.md
- Customer-facing copy change where wording is contractual
- First-time use of a new external API where the failure mode is unknown
- Any moment you find yourself thinking "wait, am I sure about this?"

## When NOT to use

- Routine code edits — the overhead is wasted
- Read-only investigation — `/li:investigate` already has the right cadence
- Time-critical incident response — urgency-with-rigor is its own cadence; careful mode's per-step confirms can slow a live incident

## Inputs

- Optional `--for <skill>` — wrap a specific skill invocation in careful mode (e.g. `/li:careful --for /li:ship`)
- Optional `--reason <text>` — operator's stated reason for elevation (logged to audit)
- Optional `--off` — explicitly disable careful mode if it was auto-enabled by a watcher

## Workflow

1. **State the elevation.** Print "CAREFUL MODE ON — reason: <reason>". Make it visually distinct so the operator knows the cadence has changed.
2. **Re-confirm intent.** AskUserQuestion: "Restating goal: <one-line>. Continue?" The point is to surface assumption-drift before action.
3. **Show before mutate.** Every Edit, every Bash command that mutates state, is shown in full FIRST. Operator confirms before execution. Read-only Bash (`git status`, `ls`, `cat`) does not need confirmation.
4. **Name the rollback.** Before any mutation, state the exact undo command (e.g. "git reset --hard HEAD@{1}", "supabase migration repair --revert").
5. **One-thing-at-a-time.** No batched mutations. Each Edit, each command, is a separate confirmation cycle.
6. **End-of-task verification.** Read-only verification step before declaring done — re-read the changed files, run smoke tests, confirm state matches intent.
7. **Audit log.** After each confirmed mutation, one line via the unified writer (ts/operator/cycle_id come from the envelope):
   `source "${LINTEL_SOURCE_ROOT:-$(git rev-parse --show-toplevel)}/bin/_audit.sh"; audit_log careful-mode mutation_confirmed reason=<reason> command=<command>` → `.claude/runtime/audit/careful-mode.jsonl`.

## Report format

```
CAREFUL MODE: <reason>

Restated goal: <one-line>
Operator confirmed: yes (at 14:23:01)

## Planned mutations (5)
1. Edit src/lib/billing.ts:42 — change refund logic
   Rollback: git checkout HEAD -- src/lib/billing.ts
2. Run supabase migration up 20260527_add_refund_audit
   Rollback: supabase migration down 20260527_add_refund_audit
3. ...

[Confirmation cycle per mutation]

## Final verification
- Read src/lib/billing.ts:38-50 — confirmed expected diff
- Run npm test --scope billing — 12/12 pass
- supabase db lint — clean

✓ Task complete in CAREFUL MODE. 5 mutations, 0 unconfirmed, all rollback paths logged.
```

## Compliance integration

- The active pack's production-mutation rules apply at maximum strictness — every per-call auth is explicit AND logged (`resolve_pack_field compliance.hooks`; none in the neutral `_default` pack).
- The pack's compliance gates re-check on every mutation (not just session-start).
- The secret-scan-block + customer-data-block hooks scan every Edit payload (they already fire on `git commit`/`push`; careful mode surfaces them per-mutation).
- If `--for /li:ship` and the target is `main`: triple confirmation required.

## Failure modes

- **Operator declines a mutation mid-task:** stop cleanly. Report partial state: which mutations landed, which were aborted. Operator owns the next move.
- **Mutation succeeds but verification fails:** state the divergence, name the rollback command, do NOT auto-rollback. Operator decides.
- **Audit log unwriteable:** treat as blocking. Surface + ask whether to proceed without audit (default: NO).
- **Confirmation fatigue (operator hits "yes" reflexively):** if 5+ consecutive yeses without modification, surface "still in careful mode — confirming you want this cadence". Re-engage attention.

## Examples

**Wrapping /li:ship for a high-stakes branch:**
```
> /li:careful --for /li:ship --reason "merging to main, prod deploy follows"
CAREFUL MODE ON — reason: merging to main, prod deploy follows
Restated goal: ship branch feat/billing-refund-v2 via PR to main
Operator confirmed: yes
[/li:ship runs with per-step confirmation, takes ~3x longer]
```

**Manual mutation flow:**
```
> /li:careful --reason "editing frozen-zone PlatformScenes.tsx for tour-page work"
CAREFUL MODE ON.
Planned: Edit PlatformScenes.tsx lines 42-50.
Rollback: git checkout HEAD -- src/components/PlatformScenes.tsx
Confirm? [yes/no]
```

**Disable after auto-elevation:**
```
> /li:careful --off
CAREFUL MODE OFF. Back to normal cadence.
```

## See also

- `/li:ship` — high-stakes invocation: prefer `/li:careful --for /li:ship`
- `/li:investigate` — read-only by default, careful mode is optional overlay for prod-data investigation
- The active pack's compliance gates — careful mode is the operator-side counterpart to the pack's auto-checks
