---
name: design-html
layer: foundation
description: Generate a single-file static HTML mockup from a brief — opens with /open-managed-browser.
color: green
tools: Read, Write, Glob, Bash
voice: internal
cli_support: [claude-code, codex]
---

# /design-html

Brief → single-file HTML mockup. Inline CSS, inline minimal JS if needed, no build step, no framework. The output is a `.html` file the operator can open immediately via `/open-managed-browser --url file://...` or any browser.

The point: fast exploration before any framework commitment. Use for design conversations, customer demos of UI direction, or as the seed for `/design-shotgun` to spawn variants.

## When to use

- Want to sketch a UI direction in 5 minutes, not 50
- Customer conversation needs a visual artifact and a Figma round-trip is too slow
- Seed for `/design-shotgun` (generate one, fork into N variants)
- Onboarding example for a new design pattern — single self-contained file is portable

## When NOT to use

- Production code — this is a mockup, not a component
- Multi-page flow with shared state — single-file constraint becomes painful
- Pixel-perfect Figma export — wrong tool

## Inputs

- Required: brief (inline prose or path to markdown describing the target)
- Optional `--reference <file|url>` — visual reference to anchor against (palette, type, layout style)
- Optional `--tokens <file>` — design tokens to honor (default: read project tokens if `--inherit-project` flag)
- Optional `--inherit-project` — read project's design system from `.lovable/memory/style/` or `docs/design/`
- Optional `--out <path>` — output HTML file (default: `~/.lintel/design-html/<slug>-<ts>.html`)
- Optional `--copy-tier <internal|placeholder|pack-voice>` — what kind of copy to use (see voice section below)

## Workflow

1. **Read brief.** Extract: target surface, primary user task, layout hints, brand cues.
2. **Read references.** If `--reference` is a URL: capture via `/browse` to extract palette + type. If file: read.
3. **Read tokens.** If `--inherit-project`: load color/spacing/type tokens. Otherwise use sane defaults (system font, 8px scale, neutral palette).
4. **Generate HTML.** Single file. Inline `<style>` (no external CSS). Minimal inline `<script>` only if needed for interactivity demo (toggle, accordion).
5. **Copy population.** Per `--copy-tier`:
   - `internal`: lorem ipsum or `[TODO: real copy]` placeholders
   - `placeholder`: descriptive placeholders that explain intent (`[Headline: 4-7 words, names the user benefit]`)
   - `pack-voice`: attempts real copy following the active pack's voice corpus — NEEDS the active pack's compliance gates before customer use
6. **Save.** Write file + log path. Skill does NOT auto-open — operator runs `/open-managed-browser` next.
7. **Optional preview.** If operator says "preview": chain to `/open-managed-browser --url file://...`.

## Report format

```
Design HTML: portal-dashboard-v3

Brief: 87 words, parsed.
Reference: ./refs/competitor-dashboard.png (palette extracted: emerald-50/-500/-700, slate-900)
Tokens: inherited from .lovable/memory/style/portal-design-v2.md
Copy tier: placeholder

Generated: ~/.lintel/design-html/portal-dashboard-v3-20260527-163100.html (24KB)
  - Hero with grainy emerald watermark
  - 3-card area-grid (placeholder text)
  - Italic emerald-700 accent on H1

To preview: /open-managed-browser --url file://~/.lintel/design-html/portal-dashboard-v3-20260527-163100.html
To fork into variants: /design-shotgun --seed <this path> --count 3
```

## Compliance integration

- If `--copy-tier pack-voice` and `--inherit-project` references a customer-facing surface: SURFACE reminder that the active pack's compliance gates are required before the artifact reaches a customer.
- Reference URL processed via `/browse` — Layer 2 prod-host gate applies.

## Voice tier note

`voice: internal`. The skill itself is internal. The OUTPUT (HTML) may contain pack-voice copy if explicitly opted in via `--copy-tier`. The skill warns when this happens and gates downstream distribution behind the active pack's compliance gates.

## Failure modes

- **Brief too vague:** ask one targeted clarifying question before generating. Better one question than a wasted generation.
- **Reference URL blocked by Layer 2:** generate without reference; note the gap in the report.
- **Token file unreadable:** fall back to defaults; warn in report.
- **Output dir unwriteable:** report exact path + permission issue; do not retry blindly.
- **Operator asks for `pack-voice` but no pack voice corpus configured:** WARN — copy will be best-effort but UNVALIDATED until a voice pack is installed.

## Examples

**Quick exploration:**
```
> /design-html "dashboard for showing 5-10 active cases with status chips, inspired by Linear"
[Reads brief, generates]
✓ 18KB HTML at ~/.lintel/design-html/dashboard-20260527-163100.html
  Preview: /open-managed-browser --url file://...
```

**Inherit project tokens:**
```
> /design-html "case-detail header redesign" --inherit-project --copy-tier placeholder
[Loads .lovable/memory/style/portal-design-v2.md tokens]
✓ 22KB HTML, uses portal-card + eyebrow + WaveWatermark per project tokens.
```

**Seed for shotgun:**
```
> /design-html "marketplace tool card" --reference ./refs/inspiration.png
[Generates v1]
> /design-shotgun --seed ~/.lintel/design-html/marketplace-tool-card-20260527-163200.html --count 4
[Spawns 4 variants in parallel]
```

## See also

- `/design-shotgun` — fork this output into N variants in parallel
- `/design-review` — review the rendered mockup once opened
- `/design-consultation` — talk through design decisions before generating HTML
- `/open-managed-browser` — open the generated file
- `/make-pdf` — convert HTML to PDF for distribution
