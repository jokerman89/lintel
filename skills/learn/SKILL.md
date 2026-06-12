---
name: learn
layer: foundation
description: Record an insight, correction, or pattern as a lesson — readable at future session start.
color: blue
tools: Read, Write, Edit, Bash
voice: internal
cli_support: [claude-code, codex]
---

# /learn

Captures something worth remembering across sessions: a correction from the operator, a discovered pattern, a workaround for a specific quirk. Lands as a structured entry in `.claude/memory/lessons.md` (project-level) or `~/.lintel/lessons.jsonl` (operator-level).

The only mechanism in Lintel that compounds learning across fresh sessions. Without it, the same correction gets made repeatedly.

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
- Optional `--scope <project|global>` — `project` writes to `.claude/memory/lessons.md` in the current repo; `global` writes to `~/.lintel/lessons.jsonl` (default: project)
- Optional `--type <correction|pattern|quirk|skillify-candidate>` — categorization (default: pattern)
- Optional `--source <text>` — what triggered this (e.g. "operator correction at 16:42", "debug session for refund flow")

## Workflow

1. **Validate scope.** If `--scope project` and no `.claude/memory/lessons.md` exists: create it with a frontmatter header. If `--scope global` and no `~/.lintel/lessons.jsonl` exists: create empty.
2. **Compliance scan.** Run Layer 2 patterns over the lesson body. If a secret/customer-data pattern hits: BLOCK + ask operator to rewrite without the sensitive bit.
2b. **Update-phase (ADR-0006).** Before appending, check what already exists:
   `source lib/memory.sh; lessons_find_related <keywords>` — classify the candidate
   add / update / supersede / no-op exactly as CAPTURE Step 2 does. Only `add` creates
   a new entry; `supersede` also stamps the old lesson with `superseded_by: L-NNN (date)`.
3. **Format entry.** Project lessons use the L-NNN grammar — the mechanical layer
   (`lessons_surface`, the digest, the budget check) keys on `^## L-NNN`; a dated heading
   would be invisible to all of it. Next number = highest existing + 1:
   ```markdown
   ## L-NNN — <one-line summary>
   **Rule:** <the durable rule>
   **Why:** <source / what triggered it, with date>
   **How to apply:** <bullets>
   ```
   Global lessons:
   ```jsonl
   {"date": "YYYY-MM-DD", "type": "...", "source": "...", "body": "...", "repo": "..."}
   ```
4. **Append.** Atomic write (read existing, append entry, write back).
5. **Audit log.** Append to `.claude/runtime/audit/lessons.jsonl`.
6. **Report.**

## Report format

```
Lesson recorded

Scope: project (.claude/memory/lessons.md)
Type: pattern
Source: operator correction at 16:42 — wanted "Start free case" not "Get started"

Body:
> CTA copy on landing pages should use "Start free case" (canonical primary CTA).
> Never use "Get started", "Start your analysis", or other variants. Refactor when seen.

Future sessions reading .claude/memory/lessons.md will surface this at session start (per repo CLAUDE.md "Review at session start" rule).
```

## Compliance integration

- Layer 2 secret/customer-data scan on lesson body — BLOCKS if pattern hits.
- Project lessons file (`.claude/memory/lessons.md`) is committed to repo — anything in it is visible to all collaborators. Sanity-scan applies.
- Global lessons file (`~/.lintel/lessons.jsonl`) is local-only. Looser scanning, but still no customer-data.

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
> /learn "CTA copy must be 'Start free case' on landing, never 'Get started' — canonical primary CTA per project memory" --type correction
✓ Lesson appended to .claude/memory/lessons.md. Visible to future sessions.
```

**Skillify candidate:**
```
> /learn "Recurring task: regenerate /portal/cases mock data after schema change. Could be a /regen-mocks skill." --type skillify-candidate
✓ Lesson recorded. Run /skillify when ready to formalize.
```

**Global quirk:**
```
> /learn "On Windows, gh CLI returns case-normalized URLs (jokerman89 instead of jokerman89). Push works but display may surprise." --scope global --type quirk
✓ Lesson appended to ~/.lintel/lessons.jsonl. Visible in any repo.
```

## See also

- `/skillify` — turn a `skillify-candidate` lesson into a real skill
- `.claude/memory/lessons.md` (project) / `~/.lintel/lessons.jsonl` (global) — where lessons live
- Project CLAUDE.md "Self-improvement loop" — the discipline this skill enables
- `/retro` — session-end reflection that may emit several /learn calls
