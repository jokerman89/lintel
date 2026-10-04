---
name: li-generate-style-learn
description: Use to extract a reusable palette and typography reference from selected presentation, document or web artifacts without modifying the sources.
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

You are the `generate-style-learn` skill — extracts palettes from selected existing artifacts.

## What this skill does

Analyzes 1+ supported artifact-files (PPT/DOCX/web) and extracts a reusable style palette
to `<out-dir>/<name>.json` plus companion `<out-dir>/<name>-STYLE.md` (human-readable).
Choose the source paths and owned output explicitly; a palette name is not a
personal-directory lookup.

Never modifies input-files. Read-only analysis.

Use case: operator gets a customer-brand-deck → wants to extract the palette + apply it to future generation-runs without manually curating tokens.

Follow [owned source and output selection](../../../skills/design-dna/references/design-contract.md#owned-source-and-output-selection).
Missing or unwritable output fails visibly; no destination is selected on the
operator's behalf.

## When to use

- "Customer sent a deck — extract their style so I match it in the next report" → `/li-generate-style-learn deck1.pptx --name customer-A`
- "Compare two style-references" → run the skill on each, diff palettes
- "Operator's own brand snapshot" → compare explicitly selected palettes against
  the supplied ground-truth artifacts

## When NOT to use

- Live style-edit — this is extraction, not an editor
- Single-color-pick — use the named `brand-source`
  [selected asset evidence procedure](../../../skills/design-dna/references/design-contract.md#selected-asset-evidence)
  to read the requested token from the explicit palette/profile; no diagnostic command
- Customer-specific live-stream — this is batch

## Inputs

- Required `<paths>` — 1+ artifact files (varierande format ok)
- Required `--name <slug>` — palette-name for output (e.g., `customer-A` or `nordic-minimal`)
- Optional `--format <ppt|web|word|auto>` — explicit format hint (default: auto-detect)
- Optional `--overwrite` — replace existing `<name>.json` if present
- Required `--out-dir <path>` — explicitly owned repository-relative palette output directory

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
- Parse `<style>` + linked CSS
- Extract :root CSS variables (preferred source)
- Fall back: most-frequent computed colors in DOM
- Typography from font-family declarations

**PDF or another unsupported format:**
- Lintel supplies no PDF reader here. A `.pdf` extension is not an extraction
  capability and a print/export result is not readable source evidence.
- Use an actually available external read operation only with explicit source
  and operation authority, recording its coverage and limitations. Otherwise
  report that extraction is unsupported/unverified and leave that input open.
- Do not install a reader, restore the removed PDF dependency, invent style
  observations or mark a partially inspected set complete.

**Auto-detect:** the extension is a format hint, not proof of a reader.

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
<out-dir>/<name>.json; supply this source explicitly or register it in the
authorized configuration before name-based reuse. Extraction does not activate it.
```

## Workflow

### Step 1 — Validate inputs

```bash
out_dir="${OUT_DIR:?select an owned repository-relative output directory}"
[ -z "${NAME:-}" ] && { echo "Usage: /li-generate-style-learn <files> --name <slug> --out-dir <path>"; exit 2; }
[ "$#" -gt 0 ] || { echo "Required: 1+ artifact files"; exit 2; }
for f in "$@"; do
  [ -f "$f" ] || { echo "Missing: $f"; exit 2; }
done
```

Complete the shared owned-path checks before reading or creating anything.
Capture original output states for both named files. Validate `NAME` as a single
slug, not a path; missing/linked/out-of-root sources or outputs fail. The actual
configured P07 path is an alternative source only when verified and authorized.

### Step 2 — Per-file extraction

Use the extension as a hint, then establish the actual supported read operation.
Apply the format-specific method above. Unsupported/unreadable inputs stay
explicitly unverified; continue independent supported inputs without claiming
that the entire requested set was processed.

### Step 3 — Aggregate across files

If multiple files: merge extractions:
- Colors: union of palettes; classify into 6 roles via 60-30-10
- Fonts: most-common heading + body
- Layout distribution: weighted average

### Step 4 — Write outputs

Keep the generated strings as `palette_json` and `style_md`. With explicit `repo`,
`out_dir`, `name`, boolean `overwrite`, and the captured `original_output_states`
keyed by repository-relative destination, publish through existing P03:

```python
import re
import sys
import context_safety as safety

try:
    root = safety.checked_root(repo)
    directory = safety.selector_path(out_dir)
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", name):
        raise ValueError("Palette name must be a single slug")
    outputs = {
        f"{directory}/{name}.json": palette_json.encode("utf-8"),
        f"{directory}/{name}-STYLE.md": style_md.encode("utf-8"),
    }
    for path in outputs:
        previous = original_output_states[path]
        if previous is not None and not overwrite:
            raise ValueError(f"Output already exists; explicit --overwrite required: {path}")
    for path, payload in outputs.items():
        previous = original_output_states[path]
        safety.atomic_write(root, path, payload,
                            mode=previous["mode"] if previous is not None else 0o600,
                            expected=previous, check_expected=True)
        if safety.read_owned(root, path, len(payload))[0] != payload:
            raise ValueError(f"Output failed readback: {path}")
except (KeyError, ValueError, OSError, UnicodeError) as error:
    print(f"ERROR [lintel/style-learn]: {error}", file=sys.stderr)
    raise SystemExit(2)
```

This is publication, not extraction or license approval. Both files must pass
readback before reporting completion. Retain and report any partial output on
failure at its original owned destination; do not switch folders or erase evidence.

### Step 5 — Surface confirmation

```
Style 'nordic-minimal' extracted.
  Source files: deck1.pptx, deck2.pptx
  Colors: 6 roles classified
  Fonts: 2 family (Segoe UI Semibold heading, Segoe UI Light body)
  Layout distribution: 5 categories
  Saved: <out-dir>/nordic-minimal.json
         <out-dir>/nordic-minimal-STYLE.md

To use: /li-generate ... --palette nordic-minimal
```

## Reusable patterns

Follow the [reusable pattern consumer contract](../../../skills/pattern/references/consumer-contract.md). The
palette and STYLE.md output is unchanged and is observation, not policy. Palette tokens can
reach a universal draft only through the `frontend-style-extract` adapter as
`visual.palette.<token>` defaults with exact `#RRGGBB` values. Fonts, licensing and
accessibility are never inferred as confirmed from an image or page.

## Status protocol

- **DONE** — palette + STYLE.md written and every required selected source actually processed
- **DONE_WITH_CONCERNS** — required sources were processed; advisory details remain uncertain (e.g., logo-position reliability)
- **BLOCKED** — any required source/reader is missing or unverified, name is absent, or output permission fails; retain partial observations without claiming the full request passed
- **NEEDS_CONTEXT** — the format or authorized reader is unresolved; a format flag does not supply a missing reader

## Pause-points

- `--overwrite` not set but palette name exists: hard-block for operator-confirm
- Multiple wildly-different styles in source files: surface "sources don't agree, palette will be averaged — proceed?"

## Integration

**Reads:**
- Source artifact files (`<paths>`)

**Writes:**
- `<out-dir>/<name>.json`
- `<out-dir>/<name>-STYLE.md`

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
- Output missing/unwritable: BLOCKED with the actual selected path and error;
  preserve inputs and any owned partial output. No current-directory, HOME or
  neighboring-run fallback; a new destination requires explicit selection.

## Recommended next steps after invocation

- Verify extraction quality: open `<name>-STYLE.md` + manually check claim-vs-source
- Test palette: `/li-generate "test brief" --palette <name>` → verify match
- For multi-source aggregation: re-run with `--diff <existing-palette>` to see what new sources added (future feature)
