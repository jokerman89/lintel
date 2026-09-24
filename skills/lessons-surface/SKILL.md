---
name: lessons-surface
layer: foundation
description: Use before or during a task to pull up prior lessons relevant to it — searches the lessons store by keyword and context and surfaces matching entries so past corrections actually inform the current work. Runs at SENSE and is callable on its own when you want to check what's been learned about a topic.
color: yellow
tools: Read, Bash, Grep
voice: internal
cli_support:
  - cli: claude-code
    level: full
  - cli: codex
    level: degraded
---

You are the `lessons-surface` skill — closes the L-001/L-002 loop. Without this skill, `.claude/memory/lessons.md` grows but is never read → compounding learning that doesn't compound.

## What this skill does

Reads the project lessons store resolved by `lintel_lessons_file` (`.claude/memory/lessons.md` on the v5 layout), matches entries against the operator's current context (keyword from prompt OR current branch/phase), surfaces relevant lessons up-front so future sessions don't repeat the same mistakes. Outside a repository it reports "no project lessons store (unobserved)".

Designed for Cohort 2 item 1.3. Solo-invokable. Auto-invoked from `/li:sense` Step 0 when relevant.

Critical: L-001 (scaffolding ≠ content) + L-002 (grep first) were created in this session, but without lessons-surface the next session would not know they exist.

## When to use

- **Auto from SENSE** — `/li:sense` calls this as Step 0 to warm up context with relevant lessons
- **Solo before planning** — "which lessons apply to my new skill family?" → `/li:lessons-surface --keyword "new family"`
- **Audit lessons** — "what have I collected?" → `/li:lessons-surface --all`
- **Specific lesson lookup** — `/li:lessons-surface --id L-001`

## When NOT to use

- Lessons authoring — use `/li:learn` (`bin/li-lessons.py` allocates IDs and writes conditionally)
- Lesson application enforcement — this surfaces; enforcement is skill-specific
- Historical lesson archaeology — `git log .claude/memory/lessons.md` is canonical

## Workflow

### Step 1 — Mechanical surface (lib/memory.sh — ADR-0006)

The scoring is implemented in bash, not prose. Run it:

```bash
source "${LINTEL_SOURCE_ROOT:-$LINTEL_REPO_ROOT}/lib/memory.sh"   # sources lib/paths.sh for the lessons location

# Keyword mode (--keyword "<text>"):
lessons_surface <keyword tokens>

# Auto-from-SENSE mode (no flag): derive keywords from branch + recent commits
kw="$(git rev-parse --abbrev-ref HEAD 2>/dev/null | tr '/-' ' ') $(git log -3 --format=%s 2>/dev/null | tr '\n' ' ')"
LESSONS_TOP_N=2 lessons_surface $kw    # top-2 — SENSE is short
```

`lessons_surface` scores each `L-NNN` block by keyword hits, SKIPS superseded lessons
(`superseded_by:` marker — supersede-don't-delete convention), and prints the top-3
(`LESSONS_TOP_N` overrides). Empty output = no relevant lessons; say so in one line. Malformed
headings, duplicate IDs, missing supersede targets and dated legacy headings are reported on
stderr — relay them rather than skipping them.

**All mode (`--all`):** `lessons_index` lists every lesson heading in file order, 1 line each,
with superseded ones ending in `(superseded)`.

**ID mode (`--id L-NNN`):** `python3 "$LINTEL_SOURCE_ROOT/bin/li-lessons.py" get --id L-NNN`
prints that exact block, a superseded one with its visible marker. Exit 1 means absent, exit 2
duplicated or malformed.

### Step 2 — Read the surfaced lessons

For each id `lessons_surface` returned, print its full block with `li-lessons.py get --id`
(Rule + Why + How to apply + [[cross-references]]) — the ranked line alone is not enough context
to apply a lesson.

### Step 3 — Render

Markdown per lesson:

```markdown
### L-001 — Lintel is scaffolding, not curated content (relevance: 8/10)

**Rule:** Lintel ships structure (templates, tests, agent-mapping, invocation skills) and ONE canonical deep example per pattern.

**Why:** Operator caught it: "No need to build more services, only for the template and the example."

**How to apply:** [bullets, first 2-3]

Related: [[L-002]]
```

Surface MAX 3 lessons (avoid drowning operator). Sort by relevance.

## Status protocol

- **DONE** — N lessons surfaced (or 0 if no match)
- **DONE_WITH_CONCERNS** — lessons store present but reader diagnostics were reported (malformed headings, duplicate IDs, missing supersede targets or dated legacy entries)
- **BLOCKED** — the resolved lessons store denies read
- **NEEDS_CONTEXT** — `--keyword` mode without a keyword arg

## Pause-points

- Lessons.md has > 50 entries and no keyword → ask for focus ("topic narrowing" via AskUserQuestion)
- Multiple lessons score > 7 → ask the operator which is most relevant (or surface all)

## Integration

**Reads:**
- The project lessons store from `lintel_lessons_file` (`.claude/memory/lessons.md` on the v5 layout)

**Writes:**
- stdout (markdown report)

**Consumed by:**
- `/li:sense` (Step 0 auto-invocation)
- Operator (solo before planning)
- `/li:plan` (can call this for pre-plan context-warming)
- `/li:cycle` (auto-call at cycle-start)

## Anti-patterns

- **Auto-surface ALL lessons every session** — drowns. Max 3 by default.
- **Hard-blocking on lesson-violation** — this surfaces for awareness, not enforcement. Enforcement is skill-specific (e.g., frontmatter-lint enforces discipline lessons).
- **Generate new lessons** — this is reader-only. New lessons are written through `/li:learn` or `/li:capture`, which use `bin/li-lessons.py`.

## Failure recovery

- Malformed entry (unparseable `## L-` heading, duplicate ID, missing supersede target, dated heading): the reader names it on stderr; count it and report it at the end
- Empty store: surface "Lessons capture empty. Record insights with /li:learn or /li:capture." Outside a repository: "no project lessons store (unobserved)".
- > 1000 lessons (someday): paginate `lessons_index` output

## Recommended next steps after invocation

- Apply surfaced lessons immediately to current work (that's the point)
- If a lesson is missing but should exist: record it with `/li:learn`
- Periodically `/li:lessons-surface --all` for audit + cleanup
