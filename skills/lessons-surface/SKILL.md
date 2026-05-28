---
name: lessons-surface
layer: foundation
description: Surface relevanta lessons.md-entries baserat på keyword/context. STÄNGER L-001/L-002-LOOPEN (lessons skrivs men läses aldrig). Solo-invokable + SENSE-integrated.
color: yellow
tools: Read, Bash, Grep
voice: internal
cli_support:
  - cli: claude-code
    level: full
  - cli: codex
    level: degraded
---

You are the `lessons-surface` skill — closes the L-001/L-002 loop. Without this skill, `tasks/lessons.md` grows but is never read → compounding learning that doesn't compound.

## What this skill does

Reads `tasks/lessons.md`, matches entries against operator's current context (keyword from prompt OR current branch/phase), surface:ar relevanta lessons up-front så framtida sessions inte upprepar samma misstag.

Designed för Cohort 2 item 1.3. Solo-invokable. Auto-invoked från `/li:sense` Step 0 om relevant.

Critical: L-001 (scaffolding ≠ content) + L-002 (grep first) skapades i denna session men utan lessons-surface skulle nästa session inte veta de finns.

## When to use

- **Auto från SENSE** — `/li:sense` calls denna som Step 0 för att värma upp context med relevanta lessons
- **Solo före planning** — "vilka lessons applies till min nya skill-familj?" → `/li:lessons-surface --keyword "new family"`
- **Audit lessons** — "vad har jag samlat?" → `/li:lessons-surface --all`
- **Specific lesson lookup** — `/li:lessons-surface --id L-001`

## When NOT to use

- Lessons authoring — manuell edit av `tasks/lessons.md` direkt
- Lesson application enforcement — denna surface:ar; enforcement är skill-specifikt
- Historical lesson archaeology — `git log tasks/lessons.md` är canonical

## Workflow

### Step 1 — Locate + parse lessons.md

```bash
LESSONS_FILE="tasks/lessons.md"
[ -f "$LESSONS_FILE" ] || { echo "No lessons.md — nothing to surface."; exit 0; }
```

Parse entries:
- Each entry starts med `## L-NNN — <name>`
- Capture: ID, name, Rule (first ** **-line), Why (one paragraph), How to apply (bullets)
- Capture [[cross-references]] mellan lessons

### Step 2 — Match against context

**Keyword mode (`--keyword "<text>"`):**
- Tokenize keyword
- For each lesson, score relevance:
  - Match in `name`: +5
  - Match in `Rule`: +3
  - Match in `How to apply`: +2
  - Match i `Why`: +1
- Surface top-3 ranked

**Auto-from-SENSE mode (no flag):**
- Read current branch name + recent git log subjects
- Use those as implicit keywords
- Surface top-2 (be quiet — SENSE is short)

**All mode (`--all`):**
- Surface all lessons med summary (1-line per)

**ID mode (`--id L-NNN`):**
- Surface specific lesson verbatim

### Step 3 — Render

Markdown per lesson:

```markdown
### L-001 — Lintel is scaffolding, not curated content (relevance: 8/10)

**Rule:** Lintel ships structure (templates, tests, agent-mapping, invocation skills) and ONE canonical deep example per pattern.

**Why:** Operator caught it: "Behöver inte göra fler services, endast för mall och exempel."

**How to apply:** [bullets, first 2-3]

Related: [[L-002]]
```

Surface MAX 3 lessons (avoid drowning operator). Sort by relevance.

## Voice tier behavior

`voice: internal`. Surface-output är operator-internal context-warming.

## Status protocol

- **DONE** — N lessons surfaced (or 0 if no match)
- **DONE_WITH_CONCERNS** — lessons.md present men malformed entries skipped
- **BLOCKED** — `tasks/lessons.md` permission denies read
- **NEEDS_CONTEXT** — `--keyword` mode utan keyword arg

## Pause-points

- Lessons.md har > 50 entries och no keyword → ask för focus ("topic narrowing" via AskUserQuestion)
- Multiple lessons score > 7 → ask operator vilken är most relevant (or surface all)

## Hop-in support

YES — primary use case är solo-invocation (eller SENSE-auto). Designed att vara invocable any time.

## Integration

**Reads:**
- `tasks/lessons.md` (canonical)

**Writes:**
- stdout (markdown report)

**Consumed by:**
- `/li:sense` (Step 0 auto-invocation)
- Operator (solo before planning)
- `/li:plan` (kan calla denna för pre-plan context-warming)
- `/li:cycle` (auto-call vid cycle-start)

## Anti-patterns

- **Auto-surface ALL lessons every session** — drowns. Max 3 by default.
- **Hard-blocking on lesson-violation** — denna surface:ar för medvetenhet, ej enforcement. Enforcement är skill-specific (e.g., frontmatter-lint enforces discipline lessons).
- **Generate new lessons** — denna är reader-only. New lessons skrivs manuellt eller via `/li:capture --as-lesson`.

## Failure recovery

- Malformed entry (missing `**Rule:**` line): skip + count + report at end
- Empty lessons.md: surface "Lessons capture empty. Start logging insights via tasks/lessons.md or /li:capture."
- > 1000 lessons (someday): paginate or recommend grep over `tasks/lessons.md`

## Recommended next steps after invocation

- Apply surfaced lessons immediately till current work (det är poängen)
- Om en lesson saknas men borde finnas: append via `/li:capture --as-lesson`
- Periodically `/li:lessons-surface --all` för audit + cleanup
