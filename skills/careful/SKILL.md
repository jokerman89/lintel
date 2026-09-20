---
name: careful
layer: foundation
description: Use for high-stakes work that needs explicit mutation boundaries, attributable recovery and verification before continuation.
color: red
tools: Read, Bash, Grep, Glob, Edit
voice: internal
necessity: OPTIONAL
gap_if_skipped: "High-stakes mutations run at normal cadence — no per-mutation confirm, no stated rollback path, no elevated audit. Fine for routine work; risky for irreversible or production-adjacent changes."
cli_support: [claude-code, codex, copilot, cursor, gemini, opencode, droid]
---

# /li:careful

A workflow overlay for extra rigor: state the mutation scope, show commands before execution,
name assumptions and require the authorization appropriate to that action. Use the actual
host question tool; use conversation only if no question channel is available. This is not
a host mode switch, permission API or automatic watcher.

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
- Optional `--off` — end this explicit workflow overlay; it never disables required controls

## Workflow

1. **State the elevation.** Print "CAREFUL MODE ON — reason: <reason>". Make it visually distinct so the operator knows the cadence has changed.
2. **Confirm only unresolved intent.** Restate the goal and authority. Ask for a missing decision,
   changed scope or new permission boundary through the actual host channel, not a required tool name.
3. **Show before mutate.** Show the intended effect and scoped command. A requested per-mutation
   confirmation cadence applies to that scope; preserve authorization already given. Read-only
   checks do not need redundant approval, but sensitive reads still follow policy.
4. **Name owned recovery.** Identify the exact owned files/revision or approved migration recovery.
   Capture unrelated dirty changes before proposing recovery. Never use a whole-tree reset or
   checkout as a generic undo. A backup, valid rollback and permission to run it are separate facts.
5. **One-thing-at-a-time.** No batched mutations. Each Edit, each command, is a separate confirmation cycle.
6. **End-of-task verification.** Read-only verification step before declaring done — re-read the changed files, run smoke tests, confirm state matches intent.
7. **Audit log.** Use the shared writer from the trusted installed source, not executable code
   discovered in an inspected target. Record sanitized reason, owned scope and result; do not
   log raw secret-bearing command lines. A log entry describes an event, not verified enforcement.

## Report format

```
CAREFUL MODE: <reason>

Restated goal: <one-line>
Operator confirmed: yes (at 14:23:01)

## Planned mutations (5)
1. Edit src/lib/billing.ts:42 — change refund logic
   Recovery: restore the owned change from its captured baseline after checking later edits.
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
- Check applicable controls at each affected boundary. Record actual hook registration/execution
  or the policy-accepted equivalent; the overlay cannot make a hook run or change its event API.
- Missing mandatory evidence stays blocked. A compatible advisory check is not upgraded to a gate.
- A main push or production action needs explicit authorization for that action/batch; repeating
  "yes" a fixed number of times is not a stronger permission or an expanded scope.

## Failure modes

- **Operator declines a mutation mid-task:** stop cleanly. Report partial state: which mutations landed, which were aborted. Operator owns the next move.
- **Mutation succeeds but verification fails:** state the divergence, name the rollback command, do NOT auto-rollback. Operator decides.
- **Audit log unwriteable:** treat as blocking. Surface + ask whether to proceed without audit (default: NO).
- **Confirmation fatigue:** summarize the remaining decision boundary instead of adding ritual
  approvals. Do not weaken mandatory host controls or assume that repetitive answers authorize more.

## Examples

**Wrapping /li:ship for a high-stakes branch:**
```
> /li:careful --for /li:ship --reason "merging to main, prod deploy follows"
CAREFUL MODE ON — reason: merging to main, prod deploy follows
Restated goal: ship branch feat/billing-refund-v2 via PR to main
Operator confirmed: yes
[/li:ship follows the agreed scoped confirmation cadence; actual overhead is unmeasured]
```

**Manual mutation flow:**
```
> /li:careful --reason "editing frozen-zone PlatformScenes.tsx for tour-page work"
CAREFUL MODE ON.
Planned: Edit PlatformScenes.tsx lines 42-50.
Recovery: captured owned-file baseline, subject to checking intervening edits
Confirm? [yes/no]
```

**End the explicitly selected overlay:**
```
> /li:careful --off
CAREFUL MODE OFF. Back to normal cadence.
```

## See also

- `/li:ship` — high-stakes invocation: prefer `/li:careful --for /li:ship`
- `/li:investigate` — read-only by default, careful mode is optional overlay for prod-data investigation
- The active pack's compliance gates — careful mode is the operator-side counterpart to the pack's auto-checks
