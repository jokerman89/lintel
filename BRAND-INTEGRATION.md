# Brand Integration (JStack v2)

Brand-compliant doc-generation foundation. Phase E of v2 build.

Goal: customer-bound deliverables (PPT, Word, Web) that carry MS brand identity correctly + are tuned for CAIP-SE audiences. Realistic scope per eng-review P4 — not "better than PPT", but brand-compliant at CAIP-SE-tier quality.

---

## Architecture

```
~/.jstack/brand/                          # operator-pulled (manual)
  ppt-templates/                          # PowerPoint .pptx templates
    pitch-deck.pptx
    workshop.pptx
    customer-summary.pptx
  word-templates/                         # Word .docx templates
    technical-deliverable.docx
    customer-summary.docx
    transparency-note.docx
  web-templates/                          # HTML / Next.js scaffolds
    landing-single-file.html
    demo-site/                            # multi-file scaffold
  azure-assets/                           # SVG icon library
    services/                             # Azure service icons
    primitives/                           # diagram primitives (arrows, boxes)
  voice/                                  # latest Trailblazer copy patterns
    headline-patterns.md
    cta-patterns.md
  brand-version.txt                       # pull date + version stamp
  .cache/                                 # parsed asset cache (P3 fix T12)

scaffolding/03-personal-advanced/doc-gen/
  default-templates/                      # in-repo fallback (P1 fix T3)
    default-ppt-template.json             # neutral styling, system font
    default-word-template.json
    default-web-template.html
```

---

## Acquisition (P1 fix T3 — minimal default fallback)

Operator pulls MS brand assets manually from MS brand portal. JStack doesn't automate the pull — credentials + corporate procurement step is operator-driven.

**Until the pull lands**, doc-gen uses the in-repo defaults. Output is marked `brand_version: default-fallback` in meta.yaml. Operator can ship with defaults if needed; updates later when pull lands.

### Pull workflow (operator-side)

1. Authenticate to MS brand portal (operator-side, varies by org)
2. Download latest PowerPoint template stack
3. Download Word template stack
4. Download Azure icon SVG library
5. Place in `~/.jstack/brand/` per the structure above
6. Run `/brand-update --register` to record the pull metadata
7. Cache invalidates automatically

### Why in-repo defaults?

- Unblocks doc-gen runtime regardless of brand-acquisition timing
- New CAIP-SE teammates can run `/generate-ppt` from day one (with default-fallback marker)
- Tests can run in CI without operator brand assets

---

## Cache + invalidation (P3 fix T12)

Brand asset loading is cached at `~/.jstack/brand/.cache/`:
- Parsed template metadata (slide layouts, available styles)
- Asset index (SVG file paths + tags + dimensions)
- Voice patterns (parsed markdown → structured rules)

### Invalidation triggers

- `/brand-update` invocation — full cache rebuild
- `brand-version.txt` timestamp newer than `.cache/` → auto-rebuild on next doc-gen
- Manual: `/brand-update --invalidate-cache`

### Cache size guideline

Typical brand asset set: ~50MB raw → ~5MB cache. Cache directory should never exceed 100MB. If it does: surface to operator + offer rebuild.

---

## Brand staleness watcher

`brand-staleness-warn` hook (warn-only, opt-in symlink to activate):
- Fires when `brand-version.txt` is >90 days old
- Surfaces "brand assets stale — consider re-pulling from MS portal"
- No block; some operators legitimately use stale brand for archival deliverables

Audit log entry per fire: `~/.jstack/audit/brand-staleness.jsonl`

---

## Minimal default templates (in-repo)

### `default-ppt-template.json`

```json
{
  "name": "default-ppt-template",
  "brand_version": "default-fallback",
  "page_size": { "width": 13.333, "height": 7.5, "unit": "inches" },
  "fonts": {
    "title": "system-ui, -apple-system, Segoe UI, sans-serif",
    "body": "system-ui, -apple-system, Segoe UI, sans-serif",
    "size_title": 36,
    "size_body": 18
  },
  "colors": {
    "primary": "#0078d4",
    "secondary": "#666666",
    "background": "#ffffff",
    "ink": "#1a1a1a"
  },
  "layouts": ["title", "title-and-content", "two-column", "section-divider", "blank"],
  "notes": "Generic neutral styling. No MS brand. Used when ~/.jstack/brand/ppt-templates/ is empty."
}
```

### `default-word-template.json`

```json
{
  "name": "default-word-template",
  "brand_version": "default-fallback",
  "page_margin": { "top": 1, "bottom": 1, "left": 1.25, "right": 1.25, "unit": "inches" },
  "fonts": {
    "heading": "system-ui, sans-serif",
    "body": "Cambria, serif",
    "code": "Consolas, monospace"
  },
  "styles": {
    "h1": { "size": 18, "weight": "bold", "color": "#1a1a1a" },
    "h2": { "size": 14, "weight": "bold" },
    "h3": { "size": 12, "weight": "bold" },
    "body": { "size": 11, "line_height": 1.5 }
  },
  "notes": "Generic neutral styling. Used when ~/.jstack/brand/word-templates/ is empty."
}
```

### `default-web-template.html`

Minimal HTML5 scaffold with system-font typography, neutral palette, semantic structure. Used as base by `/generate-web` when brand templates absent. (File created in repo with full HTML content.)

---

## Library choices (locked per P1 fix T6)

- **PPT generation:** `pptx-genjs` (TypeScript-native; consistent with v2 stack direction)
- **Word generation:** `docx-templater` (Node.js, templater-style placeholder substitution)
- **Web generation:** native HTML / Next.js scaffold (no external lib needed)

These choices land in `package.json` when Phase F runtime is built.

---

## New skills introduced by Phase E

| Skill | Purpose |
|-------|---------|
| `/brand-update` | Manual pull from MS brand portal with version tracking |
| `/asset-search` | Search `~/.jstack/brand/azure-assets/` for icons + diagram primitives |

Plus hook: `brand-staleness-warn` (warn-only).

---

## See also

- `/brand-update` skill
- `/asset-search` skill
- `/generate-ppt`, `/generate-word`, `/generate-web` (Phase F) — consumers
- `brand-staleness-warn` hook (Layer 2 / SDL)
- `MIGRATION-TABLE.md` — Phase E entries
