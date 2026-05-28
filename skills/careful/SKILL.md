---
name: careful
layer: foundation
description: Slow-down mode for high-stakes work — extra gates, double-confirm before mutations.
color: red
tools: Read, Bash, Grep, Glob, Edit
voice: internal
cli_support: [claude-code, codex]
---

# /careful

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
- Read-only investigation — `/investigate` already has the right cadence
- Time-critical incident response — `/incident-respond` (Phase 3) handles urgency-with-rigor

## Inputs

- Optional `--for <skill>` — wrap a specific skill invocation in careful mode (e.g. `/careful --for /release-ev2`)
- Optional `--reason <text>` — operator's stated reason for elevation (logged to audit)
- Optional `--off` — explicitly disable careful mode if it was auto-enabled by a watcher

## Workflow

1. **State the elevation.** Print "CAREFUL MODE ON — reason: <reason>". Make it visually distinct so the operator knows the cadence has changed.
2. **Re-confirm intent.** AskUserQuestion: "Restating goal: <one-line>. Continue?" The point is to surface assumption-drift before action.
3. **Show before mutate.** Every Edit, every Bash command that mutates state, is shown in full FIRST. Operator confirms before execution. Read-only Bash (`git status`, `ls`, `cat`) does not need confirmation.
4. **Name the rollback.** Before any mutation, state the exact undo command (e.g. "git reset --hard HEAD@{1}", "supabase migration repair --revert").
5. **One-thing-at-a-time.** No batched mutations. Each Edit, each command, is a separate confirmation cycle.
6. **End-of-task verification.** Read-only verification step before declaring done — re-read the changed files, run smoke tests, confirm state matches intent.
7. **Audit log.** Every confirmed mutation written to `~/.lintel/audit/careful-mode.jsonl` with timestamp + reason + command.

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

- Layer 2 production-mutation rules apply at maximum strictness — every per-call auth is explicit AND logged.
- 5 always-on rules check on every mutation (not just session-start).
- Sanity scan on every Edit payload (Layer 2 secret/customer-data patterns).
- If `--for /release-ev2` and the target is `main`: triple confirmation required.

## Voice tier note

`voice: internal`. Careful-mode prompts are engineering-internal — calm, precise, no rhetorical flourish.

## Failure modes

- **Operator declines a mutation mid-task:** stop cleanly. Report partial state: which mutations landed, which were aborted. Operator owns the next move.
- **Mutation succeeds but verification fails:** state the divergence, name the rollback command, do NOT auto-rollback. Operator decides.
- **Audit log unwriteable:** treat as a Layer 2 issue. Surface + ask whether to proceed without audit (default: NO).
- **Confirmation fatigue (operator hits "yes" reflexively):** if 5+ consecutive yeses without modification, surface "still in careful mode — confirming you want this cadence". Re-engage attention.

## Examples

**Wrapping /release-ev2 for a high-stakes branch:**
```
> /careful --for /release-ev2 --reason "merging to main, prod deploy follows"
CAREFUL MODE ON — reason: merging to main, prod deploy follows
Restated goal: ship branch feat/billing-refund-v2 via PR to main
Operator confirmed: yes
[/release-ev2 runs with per-step confirmation, takes ~3x longer]
```

**Manual mutation flow:**
```
> /careful --reason "editing frozen-zone PlatformScenes.tsx for tour-page work"
CAREFUL MODE ON.
Planned: Edit PlatformScenes.tsx lines 42-50.
Rollback: git checkout HEAD -- src/components/PlatformScenes.tsx
Confirm? [yes/no]
```

**Disable after auto-elevation:**
```
> /careful --off
CAREFUL MODE OFF. Back to normal cadence.
```

## See also

- `/release-ev2` — high-stakes invocation: prefer `/careful --for /release-ev2`
- `/release-deploy-ev2` — production deploy: prefer `/careful --for /release-deploy-ev2`
- `/investigate` — read-only by default, careful mode is optional overlay for prod-data investigation
- Layer 2 compliance — careful mode is the operator-side counterpart to Layer 2 auto-checks
