---
name: lessons-add
layer: foundation
description: Use after a correction, insight, or recurring pattern worth remembering to record it as a lesson the next session will read at startup. Reach for it whenever the operator corrects you or you discover something that should prevent the same mistake recurring.
color: blue
tools: Read, Write, Edit, Bash
voice: internal
cli_support: [claude-code, codex]
---

# Lessons add

Captures something worth remembering across sessions: a correction from the operator, a discovered pattern, a workaround for a specific quirk. Lands as an ID-managed `L-NNN` entry in the project lessons store (`lintel_lessons_file`; `.claude/memory/lessons.md` on the v5 layout). No operator-global lessons sink is activated.

Use the existing memory helpers so allocation, lookup, conditional writes and supersession
keep the same grammar across fresh sessions.

## When to use

- Operator just corrected the assistant's approach — record the pattern
- A debugging session revealed a non-obvious project quirk — record it
- A new convention has been agreed (naming, file layout, framework idiom) — record it
- A reusable workflow emerged that's not yet a skill — record it for `/li:skill-new`

## When NOT to use

- One-off info that won't recur — wasted bytes, signal noise
- Code-level patterns better captured in code comments — comments belong in code
- Something that belongs in CLAUDE.md or design docs — those are higher-authority, write there instead
- Sensitive info (passwords, customer data, internal IDs) — Layer 2 blocks

## Inputs

- Required: the lesson body (inline prose)
- Optional `--scope <project|global>` — `project` writes to the resolved project store (default). `global` refuses with "operator lessons sink not activated": no operator-global destination is active, and activating one is a separate operator decision
- Optional `--type <correction|pattern|quirk|skillify-candidate>` — categorization (default: pattern)
- Optional `--source <text>` — what triggered this (e.g. "operator correction at 16:42", "debug session for refund flow")

Retain `skillify-candidate` in existing lesson metadata and caller inputs. It is a stored
classification, not an instruction to invoke a removed command; no type migration is needed.

## Workflow

1. **Validate scope.** `project` only. The helper resolves the store with `lintel_lessons_file`, names any second store it ignores, and creates a missing store from the scaffolding template (inside a repository only). `--scope global` refuses; nothing is written to `~/.lintel/lessons.jsonl`, which stays a read-only legacy view.
2. **Compliance scan.** Run Layer 2 patterns over the lesson body. If a secret/customer-data pattern hits: BLOCK + ask operator to rewrite without the sensitive bit.
2b. **Update-phase (ADR-0006).** Before writing, check what already exists:
   `source lib/memory.sh; lessons_find_related <keywords>` — classify the candidate
   add / update / supersede / no-op exactly as CAPTURE Step 2 does.
3. **Format the body.** The helper writes the `## L-NNN — <one-line summary>` heading itself;
   supply the body:
   ```markdown
   **Rule:** <the durable rule>
   **Why:** <source / what triggered it, with date>
   **How to apply:** <bullets>
   ```
4. **Write through the helper.** It allocates the next ID (one more than the highest existing ID,
   superseded and duplicated IDs included), takes the store lock and replaces the file only if it
   is unchanged since it was read:
   ```bash
   source "${LINTEL_SOURCE_ROOT:?select trusted source}/lib/memory.sh"
   lessons_helper add --title "<one-line summary>" --body-file "$body_file"          # add
   lessons_helper update --id L-NNN --body-file "$body_file"                         # update
   lessons_helper supersede --id L-OLD --title "<summary>" --body-file "$body_file"  # supersede
   ```
   A held lock or a store that changed meanwhile refuses with exit 9 and replaces nothing — retry.
   Without Python 3.9+ the shim refuses visibly; surfacing and counts keep working.
5. **Audit.** After a successful write the helper records one advisory line itself:
   `lessons lesson_recorded|lesson_updated|lesson_superseded` with `scope`, `id` and
   `classification`. Do not add a second manual `audit_log` call.
6. **Report.**

## Report format

```
Lesson recorded: L-042

Scope: project (.claude/memory/lessons.md)
Type: pattern
Source: operator correction — a verification command inspected the wrong target

Body:
> Pass the selected repository explicitly to diagnostic helpers.
> Verify the reported target before accepting a result.

Future sessions reading the project lessons store will surface this at session start (per repo CLAUDE.md "Review at session start" rule).
```

## Compliance integration

- Layer 2 secret/customer-data scan on lesson body — BLOCKS if pattern hits.
- The project lessons store is committed to the repo — anything in it is visible to all collaborators. Sanity-scan applies.
- No operator-global lessons sink is active, so nothing is written outside the project store.

## Failure modes

- **Lesson body too vague to be useful:** WARN + ask whether to proceed. A vague lesson signals nothing actionable to future sessions.
- **Duplicate lesson:** prefer no-op or update regardless of age; report the existing ID.
- **Compliance scan hits:** BLOCK, surface what hit, refuse to write. Operator rewrites + retries.
- **Store locked or changed during the write (exit 9):** nothing was replaced; inspect and retry.
- **Update or supersede of an absent (exit 1) or duplicated (exit 2) ID:** refused; resolve the ID first.
- **Project lessons file conflicts with `/code-freeze`:** the freeze is advisory; honor the operator's recorded scope and ask before writing.

## Examples

**Operator correction:**
```
> /li:lessons-add "Pass the selected repository explicitly to diagnostic helpers." --type correction
✓ L-042 appended to .claude/memory/lessons.md. Visible to future sessions.
```

**Reusable skill candidate:**
```
> /li:lessons-add "Regenerate owned test fixtures after a schema change." --type skillify-candidate
✓ Lesson recorded. Run /li:skill-new --from-lesson L-043 with an authorized draft destination when ready.
```

**Global scope (refused):**
```
> /li:lessons-add "Check path identity rather than display spelling." --scope global --type quirk
✗ operator lessons sink not activated; nothing was written. Record it in the project store instead.
```

## See also

- `/li:skill-new` — turn a selected lesson into a skill draft (`--from-lesson L-NNN`)
- `/li:lessons-surface` — keyword, index and exact-ID lookup
- The project lessons store (`lintel_lessons_file`) — where lessons live; `bin/li-lessons.py get --id L-NNN` prints one exactly. `~/.lintel/lessons.jsonl` is a read-only legacy view (`lessons_legacy_operator`), not ID-managed
- Project CLAUDE.md "Self-improvement loop" — the discipline this skill enables
- `/li:capture --retrospective` — reflection that may propose several lessons
