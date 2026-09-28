---
name: li-generate-style-learn
description: Analyze .pptx/.docx/web-examples and extract a reusable style palette. v3.5 Phase 3 of the doc-generation-pipeline.
---

> **Lintel on GitHub Copilot.** Generated from `skills/generate-style-learn/SKILL.md`; edit the canonical file, then run
> `li-copilot init`.
> - **Resource root:** `../../..` from this skill's base directory (the Lintel source with `bin/`,
>   `lib/`, `skills/`). Write plans, state and evidence into the working repository's `.claude/`
>   tree, never into the resource root.
> - **Skill-relative paths:** this skill's own `scripts/`, `references/` and `data/` folders (and a
>   `<base>` that the workflow defines as its own directory) mean
>   `../../../skills/generate-style-learn/` in the Lintel source, not this generated folder.
>   `${LINTEL_SKILLS_DIR:-skills}` means the skills root, `../../../skills`. A `bin/li-run` step
>   runs in the working repository, so use `$LINTEL_SKILLS_DIR/generate-style-learn/` there.
> - **Shell steps:** run Bash snippets with Bash (Git for Windows' `bash.exe` on Windows, never
>   `System32\bash.exe`). Save a snippet to a temporary `.sh` file and run
>   `bash "<resource root>/bin/li-run" <file>`; it prepares `LINTEL_SOURCE_ROOT`, `LINTEL_REPO_ROOT`
>   and the profile context.
> - **Tools:** Read=`view`, Write=`create`, Edit=`edit`, Bash=`bash`/`powershell`, Grep=`grep`,
>   Glob=`glob`, AskUserQuestion=`ask_user`, TodoWrite=the plan checklist, Task or a named role=`task`
>   with that custom agent, WebFetch=`web_fetch`.
> - **Other Lintel workflows** are native skills: invoke `/li-<name>` rather than reading their
>   files. Named roles such as `CodeReviewer` are custom agents.

You are the `generate-style-learn` skill — v3.5 Phase 3 of the doc-generation-pipeline. Extracts palettes from existing artifacts.

## What this skill does

Analyzes 1+ artifact-files (PPT/DOCX/web/PDF) and extracts a reusable style palette to `~/.lintel/brand/palettes/<name>.json` + companion `~/.lintel/brand/palettes/<name>-STYLE.md` (human-readable).

Never modifies input-files. Read-only analysis.

Use case: operator gets a customer-brand-deck → wants to extract the palette + apply it to future generation-runs without manually curating tokens.

Per v3.5 design-doc Phase 3 (deferred from Phase 1 + Phase 2): style-learn is an optional add-on, body-shopped after Phase 1+2 were dogfooded. This is the completion-PR.

## When to use

- "Customer sent a deck — extract their style so I match it in the next report" → `/li-generate-style-learn deck1.pptx --name customer-A`
- "Compare two style-references" → run the skill on each, diff palettes
- "Operator's own brand snapshot" → audit current `~/.lintel/brand/`-palettes against ground-truth artifacts

## When NOT to use

- Live style-edit — this is extraction, not an editor
- Single-color-pick — `bin/li-doctor --brand-summary` is faster for a one-off
- Customer-specific live-stream — this is batch

## Inputs

- Required `<paths>` — 1+ artifact files (varierande format ok)
- Required `--name <slug>` — palette-name for output (e.g., `customer-A` or `nordic-minimal`)
- Optional `--format <ppt|web|word|auto>` — explicit format hint (default: auto-detect)
- Optional `--overwrite` — replace existing `<name>.json` if present
- Optional `--out-dir <path>` — palette output dir (default: `~/.lintel/brand/palettes/`)

## Extraction (per format)

**PPT (.pptx):**
- Open via python-pptx OR pptx-genjs
- Iterate theme colors → most-frequently-used fill/text colors
- Classify into primary/secondary/accent/text/background (60-30-10 rule)
- Extract heading font + body font + most-common sizes
- Layout distribution (% per layout type)
- Logo position from Slide Master
- Visual patterns (accent bars, animation style)

**DOCX (.docx):**
- Open via python-docx OR docx-templater
- Theme colors from docDefaults + styles.xml
- Font hierarchy (heading 1/2/3 + body)
- Margins + line-spacing
- Header/footer styles

**Web (HTML/CSS):**
- Parse <style> + linked CSS
- Extract :root CSS variables (preferred source)
- Fall back: most-frequent computed colors in DOM
- Typography from font-family declarations

**Auto-detect:** file extension determines format

## Output schema (palette JSON)

```json
{
  "name": "nordic-minimal",
  "source_files": ["deck1.pptx", "deck2.pptx"],
  "extracted_at": "2026-05-28T18:00:00Z",
  "colors": {
    "primary": "#002855",
    "secondary": "#4A90D9",
    "accent": "#F2A900",
    "text_dark": "#1B1B1B",
    "text_light": "#FFFFFF",
    "background": "#FFFFFF"
  },
  "fonts": {
    "heading": "Segoe UI Semibold",
    "body": "Segoe UI Light",
    "heading_size_px": 32,
    "body_size_px": 13
  },
  "layout_distribution": {
    "content": 0.55,
    "section-header": 0.15,
    "title": 0.10,
    "two-column": 0.10,
    "data-viz": 0.10
  },
  "visual_patterns": {
    "logo_position": "top-right",
    "accent_bar": "left-edge-vertical",
    "bullet_style": "square",
    "animation": "fade"
  }
}
```

## Output schema (companion STYLE.md)

Human-readable summary describing the style in plain language:

```markdown
# <name> style

**Extracted from:** deck1.pptx, deck2.pptx (2026-05-28)

## Color story

Primary navy (#002855) with bright accent (#F2A900). High-contrast text-on-light.
60-30-10 ratio: navy dominant, blue secondary, gold accent.

## Typography

Segoe UI family across the board — Semibold for heading (32px), Light for body (13px).
Tight line-height, deliberate hierarchy.

## Layout pattern

Content-heavy (55%) with regular section-header punctuation (15%). Balanced
two-column + data-viz (10% each).

## Visual signature

Logo top-right, vertical accent bar left edge, square bullets, fade animations.

## Use this style

In future generation: `/li-generate ... --palette <name>`. Catalog at
~/.lintel/brand/palettes/<name>.json.
```

## Workflow

### Step 1 — Validate inputs

```bash
[ -z "$NAME" ] && { echo "Usage: /li-generate-style-learn <files> --name <slug>"; exit 2; }
for f in "$@"; do
  [ -f "$f" ] || { echo "Missing: $f"; exit 2; }
done
```

### Step 2 — Per-file extraction

Detect format from extension. Apply format-specific extraction (per above section).

### Step 3 — Aggregate across files

If multiple files: merge extractions:
- Colors: union of palettes; classify into 6 roles via 60-30-10
- Fonts: most-common heading + body
- Layout distribution: weighted average

### Step 4 — Write outputs

```bash
mkdir -p "$OUT_DIR"
echo "$palette_json" > "$OUT_DIR/$NAME.json"
echo "$style_md" > "$OUT_DIR/$NAME-STYLE.md"
```

### Step 5 — Surface confirmation

```
Style 'nordic-minimal' extracted.
  Source files: deck1.pptx, deck2.pptx
  Colors: 6 roles classified
  Fonts: 2 family (Segoe UI Semibold heading, Segoe UI Light body)
  Layout distribution: 5 categories
  Saved: ~/.lintel/brand/palettes/nordic-minimal.json
        ~/.lintel/brand/palettes/nordic-minimal-STYLE.md

To use: /li-generate ... --palette nordic-minimal
```

## Status protocol

- **DONE** — palette + STYLE.md written, N source-files processed
- **DONE_WITH_CONCERNS** — written but extraction partial (e.g., logo-position unreliable)
- **BLOCKED** — source files unreadable OR no name provided OR write-permission denied
- **NEEDS_CONTEXT** — file format unsupported AND `--format` not specified

## Pause-points

- `--overwrite` not set but palette name exists: hard-block for operator-confirm
- Multiple wildly-different styles in source files: surface "sources don't agree, palette will be averaged — proceed?"

## Integration

**Reads:**
- Source artifact files (`<paths>`)

**Writes:**
- `~/.lintel/brand/palettes/<name>.json`
- `~/.lintel/brand/palettes/<name>-STYLE.md`

**Consumed by:**
- `/li-generate --palette <name>` (downstream format-builders)
- `/li-generate-design --palette <name>` (in shared pipeline)

## Anti-patterns

- **Modify source files** — extraction is read-only.
- **Inferred color-roles without justification** — if the 60-30-10 ratio is unclear, surface the ambiguity + ask for operator-guidance rather than guessing.
- **Overwrite without confirm** — `--overwrite` flag required for replacement.

## Failure recovery

- File format-detection fails: surface available formats + ask for a `--format` hint
- Aggregation conflict (multiple wildly-different styles): default to most-recent file's style + flag with warning
- Output dir not writable: fall back to `./palettes/<name>.json` (current dir)

## Recommended next steps after invocation

- Verify extraction quality: open `<name>-STYLE.md` + manually check claim-vs-source
- Test palette: `/li-generate "test brief" --palette <name>` → verify match
- For multi-source aggregation: re-run with `--diff <existing-palette>` to see what new sources added (future feature)
