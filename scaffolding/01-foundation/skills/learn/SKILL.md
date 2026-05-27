---
name: jstack-learn
description: Record an insight, correction, or pattern as a lesson — readable at future session start.
color: blue
tools: Read, Write, Edit, Bash
voice: internal
cli_support: [claude-code, codex]
---

# /learn

Captures something worth remembering across sessions: a correction from the operator, a discovered pattern, a workaround for a specific quirk. Lands as a structured entry in `tasks/lessons.md` (project-level) or `~/.jstack/lessons.jsonl` (operator-level).

The only mechanism in JStack that compounds learning across fresh sessions. Without it, the same correction gets made repeatedly.

## When to use

- Operator just corrected the assistant's approach — record the pattern
- A debugging session revealed a non-obvious project quirk — record it
- A new convention has been agreed (naming, file layout, framework idiom) — record it
- A reusable workflow emerged that's not yet a skill — record it as a "skillify candidate"

## When NOT to use

- One-off info that won't recur — wasted bytes, signal noise
- Code-level patterns better captured in code comments — comments belong in code
- Something that belongs in CLAUDE.md or design docs — those are higher-authority, write there instead
- Sensitive info (passwords, customer data, internal IDs) — Layer 2 blocks

## Inputs

- Required: the lesson body (inline prose)
- Optional `--scope <project|global>` — `project` writes to `tasks/lessons.md` in the current repo; `global` writes to `~/.jstack/lessons.jsonl` (default: project)
- Optional `--type <correction|pattern|quirk|skillify-candidate>` — categorization (default: pattern)
- Optional `--source <text>` — what triggered this (e.g. "operator correction at 16:42", "debug session for refund flow")

## Workflow

1. **Validate scope.** If `--scope project` and no `tasks/lessons.md` exists: create it with a frontmatter header. If `--scope global` and no `~/.jstack/lessons.jsonl` exists: create empty.
2. **Compliance scan.** Run Layer 2 patterns over the lesson body. If a secret/customer-data pattern hits: BLOCK + ask operator to rewrite without the sensitive bit.
3. **Format entry.** Project lessons:
   ```markdown
   ## YYYY-MM-DD — <type> — <one-line summary>
   <source>
   
   <body>
   ```
   Global lessons:
   ```jsonl
   {"date": "YYYY-MM-DD", "type": "...", "source": "...", "body": "...", "repo": "..."}
   ```
4. **Append.** Atomic write (read existing, append entry, write back).
5. **Audit log.** Append to `~/.jstack/audit/lessons.jsonl`.
6. **Report.**

## Report format

```
Lesson recorded

Scope: project (tasks/lessons.md)
Type: pattern
Source: operator correction at 16:42 — wanted "Starta gratis ärende" not "Kom igång"

Body:
> CTA copy on landing pages should use "Starta gratis ärende" (canonical primary CTA).
> Never use "Kom igång", "Starta din analys", or other variants. Refactor when seen.

Future sessions reading tasks/lessons.md will surface this at session start (per repo CLAUDE.md "Review at session start" rule).
```

## Compliance integration

- Layer 2 secret/customer-data scan on lesson body — BLOCKS if pattern hits.
- Project lessons file (`tasks/lessons.md`) is committed to repo — anything in it is visible to all collaborators. Sanity-scan applies.
- Global lessons file (`~/.jstack/lessons.jsonl`) is local-only. Looser scanning, but still no customer-data.

## Voice tier note

`voice: internal`. Lessons are engineering-internal — direct, no rhetorical flourish.

## Failure modes

- **Lesson body too vague to be useful:** WARN + ask whether to proceed. A vague lesson signals nothing actionable to future sessions.
- **Duplicate lesson (same body within 30 days):** report + ask whether to skip or merge.
- **Compliance scan hits:** BLOCK, surface what hit, refuse to write. Operator rewrites + retries.
- **Project lessons file conflicts with `/code-freeze`:** if frozen, refuse + ask operator to `/code-unfreeze` first.

## Examples

**Operator correction:**
```
> /learn "CTA copy must be 'Starta gratis ärende' on landing, never 'Kom igång' — canonical primary CTA per project memory" --type correction
✓ Lesson appended to tasks/lessons.md. Visible to future sessions.
```

**Skillify candidate:**
```
> /learn "Recurring task: regenerate /portal/cases mock data after schema change. Could be a /regen-mocks skill." --type skillify-candidate
✓ Lesson recorded. Run /skillify when ready to formalize.
```

**Global quirk:**
```
> /learn "On Windows, gh CLI returns case-normalized URLs (azureflipper instead of Azureflipper). Push works but display may surprise." --scope global --type quirk
✓ Lesson appended to ~/.jstack/lessons.jsonl. Visible in any repo.
```

## See also

- `/skillify` — turn a `skillify-candidate` lesson into a real skill
- `tasks/lessons.md` (project) / `~/.jstack/lessons.jsonl` (global) — where lessons live
- Project CLAUDE.md "Self-improvement loop" — the discipline this skill enables
- `/retro` — session-end reflection that may emit several /learn calls
