---
name: frontend-style-extract
layer: ms-team
description: Pattern-level extraction sister till generate-style-learn. Reads artifacts (URLs, screenshots, .tsx files) → extracts layout-grammar + motion-language + interaction-patterns + component-library-fingerprint + shader-thesis → writes ~/.lintel/brand/design-patterns/<name>/. Solo-invokable.
color: orange
tools: Read, Write, Bash, Glob
voice: internal
cli_support:
  - cli: claude-code
    level: full
  - cli: codex
    level: degraded
    degradation:
      - capability: AskUserQuestion
        strategy: auto-pick-recommended
---

You are the `frontend-style-extract` skill — pattern-level extraction for v3.7 frontend-* family (Fas A2).

## What this skill does

Reads 1+ artifacts (live URLs, screenshots, Figma exports, existing .tsx/.svelte/.vue files) → extracts **pattern-level design DNA**:

- **Layout grammar** (max-width, grid-system, section-spacing, breakpoint-strategy)
- **Motion language** (libraries detected, scroll-trigger fingerprint, animation-energy-level)
- **Interaction patterns** (scroll-smoothing, hover-intent, page-transitions, cursor-behaviors)
- **Component-library fingerprint** (shadcn? Aceternity? Magic UI? bespoke?)
- **Shader thesis** (mesh-gradient? noise-field? particle? none?)
- **Typography** (delegated to generate-style-learn för palette+fonts; this skill imports those)

Writes `~/.lintel/brand/design-patterns/<name>/` med 5 files:
- `pattern.json` — top-level synthesis (schema_version: 1)
- `typography.json` — embedded from generate-style-learn-output OR fresh extraction
- `motion.json` — motion-language extraction
- `shader-snippets/` — GLSL extraction (om detected)
- `component-imports.json` — component-library-fingerprint + import-references

**Boundary med generate-style-learn:**
- generate-style-learn extracts PALETTE + FONTS (low-level visual tokens) → `~/.lintel/brand/palettes/`
- frontend-style-extract extracts PATTERN (high-level design grammar) → `~/.lintel/brand/design-patterns/`
- Together they cover full design-DNA. Sister disciplines, disjoint output paths.

L-001-discipline: skill body är contract. Agent at invocation does actual extraction. Don't pre-bake what "patterns" look like.

## When to use

- "Customer just shared their site — extract their pattern for future runs"
- "Awwwards-of-the-day inspired me — capture the language"
- Operator-engagement compounding: build vault av extracted patterns over time → L-001 disciplinerad way
- Sister-pair: run `/li:generate-style-learn <artifact>` FIRST för palette → then `/li:frontend-style-extract <artifact>` för pattern

## When NOT to use

- Live style-edit — denna är extraction, ej editor
- Single-color-pick — `bin/li-doctor --brand-summary` faster
- Component-library-version-pinning — that's package.json territory
- Pure-palette extraction — use `/li:generate-style-learn` (palette ≠ pattern)

## Inputs

- Required `<artifacts>` — 1+ paths (URLs OK), space-separated. Examples: `https://example.com`, `screenshots/hero.png`, `existing-site/components/`
- Required `--name <pattern-name>` — kebab-case identifier för vault entry
- Optional `--overwrite` — inherits from `generate-style-learn`. Default fail-on-existing (m-3 resolution).
- Optional `--out <path>` — override default `~/.lintel/brand/design-patterns/<name>/`
- Optional `--with-palette` — chain `/li:generate-style-learn` first för palette → embed in pattern.json
- Optional `--customer-share` — triggers compliance-gate

## Workflow

### Step 1 — Parse + validate

```bash
artifacts=("$@")
name="${NAME:-}"
overwrite="${OVERWRITE:-0}"
out_dir="${OUT:-$HOME/.lintel/brand/design-patterns/$name}"

[ -z "$name" ] && { echo "Required: --name <kebab-case>"; exit 2; }
[ "${#artifacts[@]}" -eq 0 ] && { echo "Required: 1+ artifact paths/URLs"; exit 2; }

# m-3: collision-handling per generate-style-learn convention
if [ -d "$out_dir" ] && [ "$overwrite" != "1" ]; then
  echo "Pattern $name already exists at $out_dir."
  echo "Pass --overwrite to replace, OR pick a different --name."
  exit 3
fi

mkdir -p "$out_dir/shader-snippets"
```

### Step 2 — Artifact ingestion

For each artifact:
- URL: fetch HTML + CSS + (best-effort) detect JS bundles. Note: shader/canvas may require runtime inspection.
- Screenshot: visual-language extraction only (no JS-side detection)
- .tsx/.svelte/.vue files: parse imports + components + animation-call-sites

Output: per-artifact `raw-extraction.json` in `$out_dir/_raw/` (gitignored runtime cache).

### Step 3 — Optional palette chain

If `--with-palette` flag:
```bash
/li:generate-style-learn "${artifacts[@]}" --name "$name" --embed-target "$out_dir/typography.json"
```

This produces the typography.json + palette block that pattern.json references.

### Step 4 — Pattern synthesis

Agent (FrontendArchitect.md — yes the Fas A1 agent — reused for extraction-direction) synthesizes per-axis findings:

```json
{
  "schema_version": 1,
  "name": "ultra-modern-lovable-style",
  "generated_at": "<iso-8601>",
  "source_artifacts": ["<paths or URLs>"],
  "extraction_method": "url-fetch | screenshot-vlm | file-parse | mixed",
  "extraction_confidence": "high | medium | low",
  "layout_grammar": {
    "max_width": "1200px",
    "section_spacing": "clamp(4rem, 8vw, 8rem)",
    "grid": "12-col | 8-col | bento | freeform",
    "breakpoint_strategy": "mobile-first | desktop-first | container-queries"
  },
  "motion_language": {
    "libraries_detected": ["gsap", "@studio-freight/lenis"],
    "scroll_trigger_fingerprint": "scrub-tied parallax + section-fade-up + hero-act",
    "energy_level": "subtle | moderate | kinetic"
  },
  "interaction_patterns": {
    "scroll_smoothing": true,
    "hover_intent": "subtle | pronounced | none",
    "page_transitions": "fade-or-slide | view-transitions | none",
    "cursor_behavior": "default | custom-blob | magnetic-targets"
  },
  "component_library_fingerprint": {
    "primary": "shadcn",
    "motion_enhanced": "aceternity-ui | magic-ui | none",
    "ux_utilities": ["vaul", "cmdk"]
  },
  "shader_thesis": {
    "present": true,
    "type": "mesh-gradient | noise-field | particle | displacement | none",
    "complexity": "low | medium | high"
  },
  "typography_ref": "./typography.json",
  "motion_ref": "./motion.json",
  "shader_snippets_dir": "./shader-snippets/",
  "component_imports_ref": "./component-imports.json",
  "visual_thesis_distilled": "<one-paragraph synthesis>"
}
```

### Step 5 — Per-file extractions written

```bash
# typography.json — embedded or extracted via generate-style-learn
# motion.json — schema matches frontend-motion's contract
# shader-snippets/<n>.glsl — raw GLSL där detected
# component-imports.json — { "imports": [...], "fingerprint": "shadcn+aceternity" }
```

### Step 6 — Validate emit

```bash
jq -e '.schema_version == 1' "$out_dir/pattern.json" || { echo "Schema invalid"; exit 1; }

# Required files present
for f in pattern.json typography.json motion.json component-imports.json; do
  [ -f "$out_dir/$f" ] || { echo "Required file missing: $f"; exit 1; }
done

# Log to audit
jq -nc --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" --arg name "$name" --arg artifacts "${artifacts[*]}" \
  '{ts:$ts, action:"pattern-extracted", name:$name, artifacts:$artifacts}' \
  >> "$HOME/.lintel/audit/frontend-style-extract-runs.jsonl"
```

### Step 7 — Surface verdict

```
PATTERN EXTRACTION COMPLETE
══════════════════════════════════════════════════════════════════

Pattern name:       <name>
Output dir:         <out_dir>
Confidence:         <high|medium|low>
Files emitted:      pattern.json + typography.json + motion.json + component-imports.json (+ <N> shader snippets)

Next:
  Reuse:            /li:frontend-design "<new brief>" --pattern <name>
  Review:           cat <out_dir>/pattern.json
  Diff vs another:  diff <out_dir>/pattern.json <other-out>/pattern.json
```

## Voice tier behavior

`voice: internal`. Default. `--customer-share` triggers `/li:compliance-gate` om source-artifacts are customer-owned (re-use questions).

## Status protocol

- **DONE** — all 4 required files emitted + schema valid
- **DONE_WITH_CONCERNS** — extraction confidence "low" (screenshot-only, lots of inferred)
- **BLOCKED** — vault-collision without `--overwrite`, OR artifacts unreadable, OR compliance-fail
- **NEEDS_CONTEXT** — artifact-format unparseable

## Pause-points

- Vault-collision: surface options (overwrite | pick different name | abort) (m-3 resolution)
- Customer-share + source is customer-site: ask if extraction is authorized re-use
- Extraction-confidence low: surface "we inferred X from screenshot — verify before applying"

## Hop-in support

YES — solo-invocable.

## Integration

**Reads:**
- `<artifacts>` (URLs, files, screenshots)
- `~/.lintel/brand/palettes/<name>.json` (if generate-style-learn ran first)

**Writes:**
- `~/.lintel/brand/design-patterns/<name>/` (5 files)
- Audit-log: `~/.lintel/audit/frontend-style-extract-runs.jsonl`

**Calls into:**
- `agents/frontend/FrontendArchitect.md` (synthesis-direction, reused from Fas A1)
- `/li:generate-style-learn` (chained om `--with-palette` flag)
- `/li:compliance-gate` (om --customer-share)

**Consumed by:**
- `/li:frontend-design --pattern <name>` (vault lookup)
- `/li:frontend-design-review` (compare produced output vs vault baseline)

## --overwrite flag inheritance (m-3 resolution)

Pattern from `generate-style-learn`:
- Default: refuse to overwrite. Exit code 3.
- `--overwrite` flag: replace existing pattern, log to audit with `previous_pattern_hash`.

Operator can manually `rm -rf ~/.lintel/brand/design-patterns/<name>` if they want clean re-extract without `--overwrite` flag.

## Anti-patterns

- **Silent vault-overwrite** — destructive. Always require --overwrite OR fail.
- **Extracting from artifacts without authorization** — customer-share guard.
- **Producing pattern.json without `schema_version`** — M-5 compliance.
- **Skipping extraction_confidence field** — operator needs to know if low-confidence (screenshot-only).
- **Hardcoding "always extract X"** — L-001. Agent decides based on artifacts.

## Failure recovery

- URL unreachable: skip artifact + log warning + continue with rest
- Screenshot unparseable: low confidence, surface to operator
- Compliance-gate fail: BLOCKED with explicit reason

## Recommended next steps after invocation

- Reuse extracted pattern: `/li:frontend-design "<brief>" --pattern <name>` (Fas A1 orchestrator supports --pattern flag)
- Diff vs canonical: `diff ~/.lintel/brand/design-patterns/<name>/pattern.json ~/.lintel/brand/design-patterns/ultra-modern-lovable-style/pattern.json`
- L-001 vault-growth check: efter 3+ operator-extracted patterns, re-evaluate om canonical can demotas till docs/samples/
