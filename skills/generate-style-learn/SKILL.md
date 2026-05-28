---
name: generate-style-learn
layer: ms-team
description: Analysera .pptx/.docx/web-examples och extrahera reusable style palette. v3.5 Fas 3 av doc-generation-pipeline.
color: orange
tools: Read, Write, Bash, Glob
voice: internal
cli_support:
  - cli: claude-code
    level: full
  - cli: codex
    level: degraded
---

You are the `generate-style-learn` skill — v3.5 Fas 3 av doc-generation-pipeline. Extraherar palettes från existing artifacts.

## What this skill does

Analyserar 1+ artifact-files (PPT/DOCX/web/PDF) och extraherar reusable style palette till `~/.lintel/brand/palettes/<name>.json` + companion `~/.lintel/brand/palettes/<name>-STYLE.md` (human-readable).

Modifies aldrig input-files. Read-only analysis.

Use case: operator får customer-brand-deck → vill extract palette + apply till future generation-runs utan att manuellt curera tokens.

Per v3.5 design-doc Phase 3 (deferred från Fas 1 + Fas 2): style-learn är optional add-on, body-shopped after Fas 1+2 dogfoodat. Detta är completion-PR.

## When to use

- "Customer skickade en deck — extrahera deras style så jag matchar i nästa rapport" → `/li:generate-style-learn deck1.pptx --name customer-A`
- "Compare two style-references" → kör skill on each, diff palettes
- "Operator's own brand snapshot" → audit current `~/.lintel/brand/`-palettes mot ground-truth artifacts

## When NOT to use

- Live style-edit — denna är extraction, ej editor
- Single-color-pick — `bin/li-doctor --brand-summary` faster för one-off
- Customer-specific live-stream — denna är batch

## Inputs

- Required `<paths>` — 1+ artifact files (varierande format ok)
- Required `--name <slug>` — palette-name för output (e.g., `customer-A` eller `nordic-minimal`)
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
- Theme colors från docDefaults + styles.xml
- Font hierarchy (heading 1/2/3 + body)
- Margins + line-spacing
- Header/footer styles

**Web (HTML/CSS):**
- Parse <style> + linked CSS
- Extract :root CSS variables (preferred source)
- Fall back: most-frequent computed colors in DOM
- Typography från font-family declarations

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

In future generation: `/li:generate ... --palette <name>`. Catalog at
~/.lintel/brand/palettes/<name>.json.
```

## Workflow

### Step 1 — Validate inputs

```bash
[ -z "$NAME" ] && { echo "Usage: /li:generate-style-learn <files> --name <slug>"; exit 2; }
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

To use: /li:generate ... --palette nordic-minimal
```

## Voice tier behavior

`voice: internal`. Extraction is operator-internal style-management.

## Status protocol

- **DONE** — palette + STYLE.md written, N source-files processed
- **DONE_WITH_CONCERNS** — written but extraction partial (e.g., logo-position unreliable)
- **BLOCKED** — source files unreadable OR no name provided OR write-permission denied
- **NEEDS_CONTEXT** — file format unsupported AND `--format` not specified

## Pause-points

- `--overwrite` not set but palette name exists: hard-block för operator-confirm
- Multiple wildly-different styles in source files: surface "sources don't agree, palette will be averaged — proceed?"

## Hop-in support

YES — solo-invocable. Designed för one-shot extraction sessions.

## Integration

**Reads:**
- Source artifact files (`<paths>`)

**Writes:**
- `~/.lintel/brand/palettes/<name>.json`
- `~/.lintel/brand/palettes/<name>-STYLE.md`

**Consumed by:**
- `/li:generate --palette <name>` (downstream format-builders)
- `/li:generate-design --palette <name>` (in shared pipeline)
- `/li:brand-update` (kan use extraction-result vid brand-refresh)

## Anti-patterns

- **Modify source files** — extraction är read-only.
- **Inferred color-roles utan justification** — if 60-30-10 ratio unclear, surface ambiguity + ask för operator-guidance rather than guessing.
- **Overwrite without confirm** — `--overwrite` flag required för replacement.

## Failure recovery

- File format-detection fails: surface available formats + ask för `--format` hint
- Aggregation conflict (multiple wildly-different styles): default to most-recent file's style + flag with warning
- Output dir not writable: fall back till `./palettes/<name>.json` (current dir)

## Recommended next steps after invocation

- Verify extraction quality: open `<name>-STYLE.md` + manually check claim-vs-source
- Test palette: `/li:generate "test brief" --palette <name>` → verify match
- For multi-source aggregation: re-run with `--diff <existing-palette>` to see what new sources added (future feature)
