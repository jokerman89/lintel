---
name: jstack-code-freeze
layer: foundation
v1_alias: [jstack-freeze]
description: Mark paths as DO-NOT-MODIFY for this session — other skills check + refuse to touch.
color: red
tools: Read, Edit, Bash
voice: internal
cli_support: [claude-code, codex]
---

# /code-freeze

Session-scoped lockdown of files or directories. While a path is frozen, other JStack skills refuse to modify it. The freeze is metadata in `~/.jstack/code-freeze/<session-id>.yaml` — not a filesystem lock — so an explicit override is possible if the operator means it.

Use to prevent drift: "we're working on portal/, do not touch landing/ this session."

## When to use

- Mid-session, operator notices a skill is wandering into unrelated areas — lock those areas
- Refactor with surgical scope — freeze everything except the target dir
- Working alongside a teammate on a shared branch; lock their files
- Frozen-zone in project CLAUDE.md needs runtime enforcement (skill checks `freeze` AS WELL AS the static CLAUDE.md list)

## When NOT to use

- Permanent project policy — that belongs in CLAUDE.md, not session freeze
- Read protection — freeze blocks WRITES only; reads are always allowed
- Multi-session enforcement — freeze expires when session ends

## Inputs

- Required: one or more paths (file or directory, glob accepted)
- Optional `--reason <text>` — why this is frozen (logged to audit, helpful when reviewing later)
- Optional `--until <expr>` — auto-expire: `eod`, `session`, `1h`, `2026-05-28T12:00` (default: session)
- Optional `--list` — show current freeze state without adding

## Workflow

1. **Resolve paths.** Expand globs, canonicalize.
2. **Sanity check.** Reject obvious mistakes: empty path, root `/`, freezing `~/.jstack/` itself.
3. **Write to session freeze file.** `~/.jstack/code-freeze/<session-id>.yaml`:
   ```yaml
   frozen:
     - path: src/components/landing/
       reason: working on portal, keep landing untouched
       added_at: 2026-05-27T17:14:03Z
       expires: session
   ```
4. **Notify chained skills.** Other JStack skills read this file before any Edit/Write. If the target matches: skill refuses + reports the freeze.
5. **Audit log.** Append to `~/.jstack/audit/code-freeze.jsonl`.
6. **Report current freeze state.**

## Report format

```
Freeze: 2 paths added

Currently frozen this session:
- src/components/landing/    (reason: working on portal)
- supabase/migrations/       (reason: migration churn risk)

To unfreeze: /code-unfreeze <path>
To override for one skill invocation: skill --ignore-freeze
```

## How other skills honor the freeze

Every JStack skill that writes files MUST:

1. Read `~/.jstack/code-freeze/<session-id>.yaml` before any Edit/Write.
2. If target path matches a frozen entry: refuse, report the freeze + reason.
3. Honor `--ignore-freeze` ONLY if operator passes it AND logs a reason to audit.

This is enforced at skill-author-level (every skill includes the check). Future runtime engine may centralize the check; for now it's a per-skill discipline.

## Compliance integration

- Freeze cannot prevent Layer 2 always-on checks (those override). E.g. you can't freeze "skip the sanity-scan" — the sanity-scan is Layer 2.
- Freeze IS load-bearing for frozen-zone enforcement: project CLAUDE.md frozen-zone files SHOULD be added to freeze on session start by `/context-restore` or `/help`.

## Voice tier note

`voice: internal`. Freeze ops are engineering-internal.

## Failure modes

- **Path doesn't exist:** WARN, still add to freeze (you may be locking a path that will be created — refusal is "do not create this path either").
- **Path conflicts with existing freeze:** consolidate, do not duplicate. Update reason if operator supplies a new one.
- **Session file corrupted:** offer to back up + recreate empty. Operator confirms.
- **Operator passes `--ignore-freeze` without reason:** WARN — require a reason, do not allow silent override.

## Examples

**Lock a directory:**
```
> /code-freeze src/components/landing/ --reason "working on portal"
✓ Frozen. Other skills will refuse to edit landing/ this session.
```

**Lock multiple with auto-expire:**
```
> /code-freeze supabase/migrations/ scripts/deploy/ --reason "migration cooldown" --until 1h
✓ 2 paths frozen for 1 hour.
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
- `/context-restore` — auto-loads frozen-zone paths from project CLAUDE.md
- Project CLAUDE.md "frozen zones" section — permanent freezes, not session-scoped
