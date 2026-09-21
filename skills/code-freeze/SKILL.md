---
name: code-freeze
layer: foundation
v1_alias: [li-freeze]
description: Record advisory do-not-modify scope for an explicitly identified session or cycle; this metadata does not enforce a filesystem or universal host write lock.
color: red
tools: Read, Edit, Bash
voice: internal
cli_support: [claude-code, codex]
---

# /code-freeze

Session/cycle-scoped **advisory** do-not-modify metadata in
`.claude/runtime/state/code-freeze/<session-id>.yaml`. It records operator intent,
not a filesystem lock, host permission or automatic refusal by every skill.
BUILD/QA must honor explicit operator scope through their normal authorization
checks; no universal automatic freeze consumer is implemented or claimed here.

Use to prevent drift: "we're working on portal/, do not touch landing/ this session."

## When to use

- Mid-session, operator notices a skill is wandering into unrelated areas — lock those areas
- Refactor with surgical scope — freeze everything except the target dir
- Working alongside a teammate on a shared branch; lock their files
- Surface a project frozen-zone rule alongside temporary scope reminders, without
  claiming new runtime enforcement

## When NOT to use

- Permanent project policy — that belongs in CLAUDE.md, not session freeze
- Read protection — metadata does not grant or remove read permission
- Multi-session enforcement — no expiry watcher or automatic cleanup is installed

## Inputs

- Required: one or more paths (file or directory, glob accepted)
- Optional `--reason <text>` — why this is frozen (logged to audit, helpful when reviewing later)
- Optional `--until <expr>` — requested expiry intent (`eod`, `session`, `1h` or
  an explicit time), evaluated when inspected; not a timer or automatic unfreeze
- Optional `--list` — show current freeze state without adding

## Workflow

1. **Resolve paths.** Use literal repository-relative paths and P03's bounded
   selector for existing glob matches. Reject escapes/links; do not eval input.
   A nonexistent future path remains explicit prospective scope, not a failed match
   silently broadened to its parent.
2. **Sanity check.** Reject obvious mistakes: empty path, root `/`, freezing `~/.lintel/` itself.
3. **Write to the explicitly selected session/cycle freeze file.** Use an actual
   host session ID or retained cycle ID, never a shell PID or guessed `default`.
   Read back the intended entries before reporting persistence. Example:
   ```yaml
   advisory: true
   frozen:
     - path: src/components/landing/
       reason: working on portal, keep landing untouched
       added_at: 2026-05-27T17:14:03Z
       expires: session
   ```
4. **Carry the pointer.** Link this scope reminder from the selected work/handoff.
   Report that enforcement is cooperative. Do not claim every write skill consumes it.
5. **Audit observation.** Use the existing `audit_log code-freeze freeze` writer
   with selected path/reason references. An observation is not evidence of enforcement.
6. **Report current freeze state.**

## Report format

```
Advisory freeze: 2 paths recorded; automatic enforcement not verified

Currently frozen this session:
- src/components/landing/    (reason: working on portal)
- supabase/migrations/       (reason: migration churn risk)

To unfreeze: /code-unfreeze <path>
An exception needs explicit scoped operator authorization; no universal --ignore-freeze flag exists.
```

## How other skills honor the freeze

An agent honoring this reminder should:

1. Read `.claude/runtime/state/code-freeze/<session-id>.yaml` before any Edit/Write.
2. If target path matches a frozen entry: refuse, report the freeze + reason.
3. Require explicit scope authorization for an exception. A reason or local marker
   cannot override project governance, host permissions or required controls.

This is instruction-driven and advisory, not a claim that every writer implements a
check. The optional `frozen-zone-warn` hook remains warn-only and dormant; its legacy
reader uses `$LINTEL_HOME/freeze/<session-id>.yaml`, not this repository path.
Do not silently copy records there, activate the hook or call it enforcement.

## Compliance integration

- Freeze cannot prevent Layer 2 always-on checks (those override). E.g. you can't freeze "skip the sanity-scan" — the sanity-scan is Layer 2.
- Project frozen-zone rules remain authoritative independently. Context restore/help
  are not promised to auto-populate this metadata.

## Failure modes

- **Path doesn't exist:** WARN, still add to freeze (you may be locking a path that will be created — refusal is "do not create this path either").
- **Path conflicts with existing freeze:** consolidate, do not duplicate. Update reason if operator supplies a new one.
- **Session file corrupted:** preserve it and report unknown scope. Do not reset
  to an empty, apparently unrestricted state.
- **Operator passes `--ignore-freeze` without reason:** WARN — require a reason, do not allow silent override.

## Examples

**Lock a directory:**
```
> /code-freeze src/components/landing/ --reason "working on portal"
✓ Advisory scope recorded. Honor it during BUILD; automatic host enforcement is unverified.
```

**Lock multiple with auto-expire:**
```
> /code-freeze supabase/migrations/ scripts/deploy/ --reason "migration cooldown" --until 1h
✓ 2 advisory paths recorded with a requested one-hour expiry; no timer was installed.
```

**List current state:**
```
> /code-freeze --list
3 paths frozen this session:
- src/components/landing/    (working on portal, until session end)
- supabase/migrations/       (migration cooldown, until 18:14:03)
- .lovable/memory/style/     (designsystem-policy lockdown, until session end)
```

## See also

- `/code-unfreeze` — remove a path from session freeze
- `/help` — shows currently frozen paths at session start
- `/context-restore` — restores owned checkpoints; no automatic freeze enforcement implied
- Project CLAUDE.md "frozen zones" section — permanent freezes, not session-scoped
