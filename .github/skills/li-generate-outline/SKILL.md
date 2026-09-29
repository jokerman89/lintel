---
name: li-generate-outline
description: Produce outline.md (structured presentation/document skeleton) from a brief. Shared content-pipeline sub-skill, solo-invokable.
---

> **Lintel on GitHub Copilot.** Generated from `skills/generate-outline/SKILL.md`; edit the canonical file, then run
> `li-copilot init`.
> - **Resource root:** `../../..` from this skill's base directory (the Lintel source with `bin/`,
>   `lib/`, `skills/`). Write plans, state and evidence into the working repository's `.claude/`
>   tree, never into the resource root.
> - **Skill-relative paths:** this skill's own `scripts/`, `references/` and `data/` folders (and a
>   `<base>` that the workflow defines as its own directory) mean
>   `../../../skills/generate-outline/` in the Lintel source, not this generated folder.
>   `${LINTEL_SKILLS_DIR:-skills}` means the skills root, `../../../skills`. A `bin/li-run` step
>   runs in the working repository, so use `$LINTEL_SKILLS_DIR/generate-outline/` there.
> - **Shell steps:** run Bash snippets with Bash (Git for Windows' `bash.exe` on Windows, never
>   `System32\bash.exe`). Save a snippet to a temporary `.sh` file and run
>   `bash "<resource root>/bin/li-run" <file>`; it prepares `LINTEL_SOURCE_ROOT`, `LINTEL_REPO_ROOT`
>   and the profile context.
> - **Tools:** Read=`view`, Write=`create`, Edit=`edit`, Bash=`bash`/`powershell`, Grep=`grep`,
>   Glob=`glob`, AskUserQuestion=`ask_user`, TodoWrite=the plan checklist, Task or a named role=`task`
>   with that custom agent, WebFetch=`web_fetch`.
> - **Other Lintel workflows** are native skills: invoke `/li-<name>` rather than reading their
>   files. Named roles such as `CodeReviewer` are custom agents.

You are the `generate-outline` skill — first stage of the v3.5 shared content pipeline. Produces an outline.md from a brief.

## What this skill does

Reads a brief (path or inline text) + audience + arc + target-format hints, then produces a structured outline.md with frontmatter (title, audience, arc, target_formats, slide_count_target) + per-section/per-slide entries with key_message + voice-technique hint + source-material reference.

Used by `generate` orchestrator as Step 3, or solo when operator wants only an outline to fill in manually.

Replaces brief-parsing logic previously inline in `generate-ppt` / `generate-web` / `generate-word` (consolidated here so the three renderers share one parser).

## When to use

- First step of `/li-generate` orchestrator chain
- Operator wants ideation-only — "give me an outline I can fill in manually"
- Re-outline an existing run with different audience/arc (rerun against same brief)
- Outline-tinder: produce N candidate outlines, operator picks one

## When NOT to use

- Operator already has a content.md — skip directly to `/li-generate-design`
- Single-slide quick mockup — bypass outline, write content directly
- Re-render of existing run without content changes — use format-builder solo with `--from-pipeline`

## Inputs

- Required `--brief <path|inline>` — content brief
- Required `--target-formats <ppt,web,word,...>` — comma-separated format list (affects slide_count_target + arc choice)
- Optional `--audience <text>` — primary audience (default: "general business")
- Optional `--arc <name>` — narrative arc (see Arcs section)
- Optional `--slide-count <N>` — presentation-view target; PPT-only advisory starting hint is 8-15 slides (default 12), subject to brief/duration constraints and explained adjustment
- Optional `--language <language-tag|name>` — output language, including regional or multilingual requirements (default: match brief; respect applicable configured policy)
- Optional `--out <path>` — output path (default: `${run_dir}/outline.md` or `./outline.md`)

## Narrative arcs

| Arc | Structure | Best for |
|-----|-----------|----------|
| problem-solution | Problem → Solution → Proof → CTA | Customer pitch |
| deep-dive | Context → Analysis → Implications → Next steps | Technical review |
| keynote | Hook → Story → Data → Takeaway | Conference talk |
| scr | Situation → Complication → Resolution | Executive briefing |
| status | Recap → Progress → Blockers → Plan | Internal update |

If no arc specified, agent picks based on audience + brief signal.

## Output schema (outline.md)

```markdown
---
title: <descriptive title, preserving the brief's meaning>
audience: <string>
arc: <name from arcs table>
language: <selected language, for example en-GB, sv, or ja>
target_formats: [ppt, web, word]
slide_count_target: <int>
generated_at: <iso-8601>
source_brief_hash: <sha256 of brief>
---

# <title>

## §1 — <Section title>
- **type:** title | agenda | section-header | content | content-image | two-column | comparison | data-viz | quote | timeline | demo | thank-you
- **key_message:** <one sentence — the one thing this section communicates>
- **source_material:** <explicit source path and paragraph/heading/table/claim references, or labelled "agent synthesis">
- **voice_technique:** <configured technique or null>
- **notes_for_writer:** <reasoning, citations, tables, qualifications and material limitations to retain>

## §2 — <next section title>
...
```

Sections are numbered §1, §2, ... — a consistent §-pattern across content artifacts.
Keep these IDs stable during writing and format composition. A section is a unit of
reasoning, not necessarily one slide or one page. `slide_count_target` remains an
integer planning hint for compatibility; it is not a content budget or a truncation rule.

## Workflow

### Step 1 — Parse brief

Read the complete brief and its explicitly supplied sources. If inline, retain the
exact supplied text in the owned run directory before computing its SHA-256.
Keep a source inventory of claims, evidence, tables, citations and material limitations.
Do not reconstruct the brief from its key messages later. Follow the
[content fidelity and evidence procedure](../../../skills/generate-write/references/fidelity-and-evidence.md).

### Step 2 — Detect language + audience signal

An explicit language choice overrides an inferred preference, subject to applicable
configured policy; otherwise preserve the brief's language. Keep original quotations,
identifiers and citations even in a translated document, marking translations where
needed. There is no fixed language pair or required first-person pronoun. Audience
cues inform the default arc if `--arc` is not specified.

### Step 3 — Pick arc

If `--arc` provided: use it. Otherwise:
- Brief mentions customer + pitch words → `problem-solution`
- Brief is technical-deep → `deep-dive`
- Brief mentions executive / board → `scr`
- Brief is status / progress → `status`
- Brief is keynote / conference → `keynote`

### Step 4 — Choose slide_count_target

If `--slide-count` is provided, use it as the presentation-view target. Otherwise
honor the brief/duration constraints before applying a starting hint. Use the
retained 8-15 slides (default 12) advisory fallback only when `ppt` is in `target_formats`.
Material, audience and pacing may justify an explained adjustment outside that
range; it is never a mandatory count gate or permission to trim source content.
Conflicting explicit requirements need resolution, not silent substitution.

For Word/web without PPT there is no fixed section-count quota: record the
planned section count in the existing field rather than forcing a slide-sized
structure. Split at reasoning boundaries. If the presentation target is tight,
plan notes, appendices or linked long-form content; do not delete evidence to fit
the target.

### Step 5 — Generate section/slide list

For each section/slide:
- Pick type from available list
- Write an informative title; brief slide headlines can be composed later
- Write key_message (one sentence, distinct from every other key_message)
- Map every source claim, supporting argument, table, citation and limitation to a section
- Pick voice_technique from the configured corpus, or null when none applies
- Write notes_for_writer, including content that needs a continuation or appendix

### Step 6 — Validate

- All key_messages distinct
- Arc internally consistent (matches first → middle → last structure for chosen arc)
- Source inventory is covered without dropping qualifications or unsupported synthesis
- For slides, review pacing and variety as presentation advice, not universal hard gates
- Explain count drift and any continuation/appendix plan; never resolve drift by content loss

### Step 7 — Write outline.md + return path

Write to `--out` path. Surface summary (slide_count, section types, language, arc) to operator.

## Reusable patterns

Follow the [reusable pattern consumer contract](../../../skills/pattern/references/consumer-contract.md). Use
the clauses of a verified run attachment; on direct entry without one, resolve for the brief's
context. Sections required by mandatory clauses become outline sections tagged with their clause
IDs before other structure choices; defaults inform only unconstrained choices. `needs-context`,
`conflict` and `unavailable` stop the outline.

## Status protocol

- **DONE** — outline.md written, validation passed
- **DONE_WITH_CONCERNS** — outline written with pacing/count advice or an uncertain arc explicitly recorded
- **BLOCKED** — brief is unparseable, missing, or too vague to outline
- **NEEDS_CONTEXT** — `--target-formats` not specified (ambiguous slide-count target)

## Pause-points

- Brief lacks the purpose, audience or evidence necessary for the requested output: ask for the missing input, not an arbitrary word quota
- Multiple plausible arcs detected: surface options + recommendation

## Integration

**Reads:**
- Brief (path or inline)
- Explicitly supplied or verified profile arc preferences, when present; no personal-directory scan

**Writes:**
- `outline.md` to `--out` path

**Consumed by:**
- `/li-generate` orchestrator (Step 3)
- `/li-generate-write` (input → content.md)
- Operator (solo-invocation use case)

## Anti-patterns

- **Generating content INSIDE outline.md** — outline holds structure + key_messages only. Content (bodies, bullets) belongs in content.md (generate-write).
- **Duplicate key_messages across sections** — clarify the different purpose; consolidate only when all source detail and references remain covered.
- **Inferring `--target-formats`** — slide_count_target depends on this. Block on missing instead of guessing.
- **Hard-coded language or voice** — use the brief, explicit choice and applicable configured policy.

## Failure recovery

- Missing source material: identify the exact gap; do not invent facts to fill a section
- All arcs deadlock (each scores equal): pick `problem-solution` (most-versatile default), flag in notes
- Count drift: adjust the presentation plan or retain an explicit concern; preserve the source

## Recommended next steps after invocation

- For full chain: invoke `/li-generate-write --outline <outline.md>` to produce content.md
- For solo-iteration: operator edits outline.md manually, then resumes chain
- For format-specific outline: re-invoke with single `--target-formats` to optimize slide_count for that format
