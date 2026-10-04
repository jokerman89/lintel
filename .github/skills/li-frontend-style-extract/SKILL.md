---
name: li-frontend-style-extract
description: Use to extract reusable layout, motion, interaction and component patterns from selected sites, screenshots or frontend source into an explicitly owned output.
---

> **Lintel on GitHub Copilot.** Generated from `skills/frontend-style-extract/SKILL.md`; edit the canonical file, then run
> `li-copilot init`.
> - **Resource root:** `../../..` from this skill's base directory (the Lintel source with `bin/`,
>   `lib/`, `skills/`). Write plans, state and evidence into the working repository's `.claude/`
>   tree, never into the resource root.
> - **Skill-relative paths:** this skill's own `scripts/`, `references/` and `data/` folders (and a
>   `<base>` that the workflow defines as its own directory) mean
>   `../../../skills/frontend-style-extract/` in the Lintel source, not this generated folder.
>   `${LINTEL_SKILLS_DIR:-skills}` means the skills root, `../../../skills`. A `bin/li-run` step
>   runs in the working repository, so use `$LINTEL_SKILLS_DIR/frontend-style-extract/` there.
> - **Shell steps:** run Bash snippets with Bash (Git for Windows' `bash.exe` on Windows, never
>   `System32\bash.exe`). Save a snippet to a temporary `.sh` file and run
>   `bash "<resource root>/bin/li-run" <file>`; it prepares `LINTEL_SOURCE_ROOT`, `LINTEL_REPO_ROOT`
>   and the profile context.
> - **Tools:** Read=`view`, Write=`create`, Edit=`edit`, Bash=`bash`/`powershell`, Grep=`grep`,
>   Glob=`glob`, AskUserQuestion=`ask_user`, TodoWrite=the plan checklist, Task or a named role=`task`
>   with that custom agent, WebFetch=`web_fetch`.
> - **Other Lintel workflows** are native skills: invoke `/li-<name>` rather than reading their
>   files. Named roles such as `CodeReviewer` are custom agents.

You are the `frontend-style-extract` skill — pattern-level extraction for the frontend family.

## What this skill does

Reads 1+ artifacts (live URLs, screenshots, Figma exports, existing .tsx/.svelte/.vue files) → extracts **pattern-level design DNA**:

- **Layout grammar** (max-width, grid-system, section-spacing, breakpoint-strategy)
- **Motion language** (libraries detected, scroll-trigger fingerprint, animation-energy-level)
- **Interaction patterns** (scroll-smoothing, hover-intent, page-transitions, cursor-behaviors)
- **Component-library fingerprint** (shadcn? Aceternity? Magic UI? bespoke?)
- **Shader thesis** (mesh-gradient? noise-field? particle? none?)
- **Typography** (delegated to generate-style-learn for palette+fonts; this skill imports those)

Writes the explicitly selected `<out>/` with these artifacts:
- `pattern.json` — top-level synthesis (schema_version: 1)
- `typography.json` — embedded from generate-style-learn-output OR fresh extraction
- `motion.json` — motion-language extraction
- `shader-snippets/` — GLSL extraction (if detected)
- `component-imports.json` — component-library-fingerprint + import-references

**Boundary with generate-style-learn:**
- generate-style-learn extracts PALETTE + FONTS (low-level visual tokens) → its explicit `--out-dir`
- frontend-style-extract extracts PATTERN (high-level design grammar) → its explicit `--out`
- Together they cover full design-DNA. Sister disciplines, disjoint output paths.

L-001-discipline: skill body is the contract. Agent at invocation does the actual extraction. Don't pre-bake what "patterns" look like.

Reuse the [shared design contract](../../../skills/design-dna/references/design-contract.md)
when a pattern is selected for a new design. Extraction is source evidence, not
automatic library/license/profile approval. Preserve unknown motion/shader behavior
as unobserved; a screenshot cannot establish absence. Choose explicit owned output,
not a personal-home search, and bind the source bytes on later consumption.
Follow [owned source and output selection](../../../skills/design-dna/references/design-contract.md#owned-source-and-output-selection);
missing or unwritable output fails visibly without another destination.

## When to use

- "Customer just shared their site — extract their pattern for future runs"
- "Awwwards-of-the-day inspired me — capture the language"
- Operator-engagement compounding: build a vault of extracted patterns over time → the L-001 disciplined way
- Sister-pair: run `/li-generate-style-learn <artifact>` FIRST for palette → then `/li-frontend-style-extract <artifact>` for pattern

## When NOT to use

- Live style-edit — this is extraction, not an editor
- Single-color-pick — use the named `brand-source`
  [selected asset evidence procedure](../../../skills/design-dna/references/design-contract.md#selected-asset-evidence)
  on the explicit palette/profile instead of a diagnostic command
- Component-library-version-pinning — that's package.json territory
- Pure-palette extraction — use `/li-generate-style-learn` (palette ≠ pattern)

## Inputs

- Required `<artifacts>` — 1+ paths (URLs OK), space-separated. Examples: `https://example.com`, `screenshots/hero.png`, `existing-site/components/`
- Required `--name <pattern-name>` — kebab-case identifier for vault entry
- Optional `--overwrite` — inherits from `generate-style-learn`. Default fail-on-existing (m-3 resolution).
- Required `--out <path>` — explicitly owned repository-relative pattern output directory
- Optional `--with-palette` — chain `/li-generate-style-learn` first for palette → embed in pattern.json
- Optional `--customer-share` — triggers compliance-gate

## Workflow

### Step 1 — Parse + validate

```bash
artifacts=("$@")
name="${NAME:-}"
overwrite="${OVERWRITE:-0}"
out_dir="${OUT:?select an owned repository-relative output directory}"

[ -z "$name" ] && { echo "Required: --name <kebab-case>"; exit 2; }
[ "${#artifacts[@]}" -eq 0 ] && { echo "Required: 1+ artifact paths/URLs"; exit 2; }

# m-3: collision-handling per generate-style-learn convention
if [ -d "$out_dir" ] && [ "$overwrite" != "1" ]; then
  echo "Pattern $name already exists at $out_dir."
  echo "Pass --overwrite to replace, OR pick a different --name."
  exit 3
fi

```

Before ingestion, run the shared rooted source/output checks, validate `name` as
a single slug and capture original output states. Do not create a directory as
proof of permission. New children, including `shader-snippets` and `_raw`, are
created only within the explicitly owned write set after source admission.
An unavailable/missing root or unwritable output is an error, not a cwd fallback.

Before any extraction output, `--with-palette` also requires every selected
source to have a supported file handoff. For URL input, establish an actually
available and authorized capture operation first; otherwise refuse this
combination without writing partial pattern/palette output.

### Step 2 — Artifact ingestion

For each artifact:
- URL: fetch HTML + CSS + (best-effort) detect JS bundles. Note: shader/canvas may require runtime inspection.
- Screenshot: visual-language extraction only (no JS-side detection)
- .tsx/.svelte/.vue files: parse imports + components + animation-call-sites

Output: per-artifact `raw-extraction.json` in `$out_dir/_raw/` (gitignored runtime cache).

For a requested palette handoff, retain an explicitly owned, supported local
capture for each admitted source. `palette_artifacts` contains those actual
HTML/CSS/document files, not the original URL strings or a metadata-only JSON
file. Keep each capture's source URL/path, content hash, permitted operation and
coverage alongside it. Existing local files can retain their original admitted
paths. A URL requires an available authorized capture first; if no supported
file can be retained, refuse the URL-plus-palette combination before writing
partial extraction output. Do not grant the child network capability or invent
a capture from source metadata.

### Step 3 — Optional palette chain

If `--with-palette` flag:
```text
/li-generate-style-learn "${palette_artifacts[@]}" --name "$name" --out-dir "$out_dir/palette"
```

Pass only the admitted capture files and their source/coverage record. The child
remains file-only and performs its existing file admission; source provenance
is not replaced by the cache pathname.

This is a native workflow handoff, not an executable Bash command. If the parent
received `--overwrite` and the confirmed write set includes both
`$out_dir/palette/$name.json` and `$out_dir/palette/$name-STYLE.md`, pass
`--overwrite` to that exact child invocation as well. The child captures and
checks its own two preimages; a parent directory selection is not replacement
permission. If those files are outside the confirmed replacement scope, resolve
only that missing scope and retain the child's default refusal. Never enable
child overwrite merely because `--with-palette` is present.

Read the returned `<name>.json` palette/font evidence. It does not directly emit
`typography.json`; the old `--embed-target` argument was not supported. Adapt the
observed font roles into the shared typography fragment explicitly, retain
unresolved fallback/license data, and validate with `--kind typography` before
synthesis. Do not silently label the palette JSON a frontend spec.

### Step 4 — Pattern synthesis

Agent (FrontendArchitect.md — yes the Phase A1 agent — reused for extraction-direction) synthesizes per-axis findings:

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
# shader-snippets/<n>.glsl — raw GLSL where detected
# component-imports.json — { "imports": [...], "fingerprint": "shadcn+aceternity" }
```
Use the shared helper for typography/motion/shader fragments. No detected JS
library is not automatically proof of no animation; select none/CSS/library only
from supported observation or an explicit design decision.
Publish each artifact through P03's owned-output procedure against its captured
preimage and read back the bytes. Retain source bytes and partial results on
failure; no automatic new destination or completion claim.

### Step 6 — Validate emit

```bash
jq -e '.schema_version == 1' "$out_dir/pattern.json" || { echo "Schema invalid"; exit 1; }

# Required files present
for f in pattern.json typography.json motion.json component-imports.json; do
  [ -f "$out_dir/$f" ] || { echo "Required file missing: $f"; exit 1; }
done

# Log to audit via the unified writer (ts/operator/cycle_id come from the envelope)
export LINTEL_SOURCE_ROOT="${LINTEL_SOURCE_ROOT:-${CLAUDE_PLUGIN_ROOT:?trusted Lintel source root unavailable; set LINTEL_SOURCE_ROOT}}"
source "$LINTEL_SOURCE_ROOT/bin/_audit.sh" || exit $?
audit_log frontend-style-extract-runs pattern_extracted "name=$name" "artifacts=${artifacts[*]}"
# → .claude/runtime/audit/frontend-style-extract-runs.jsonl
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
  Reuse:            /li-frontend-design "<new brief>" --pattern <name>
  Review:           cat <out_dir>/pattern.json
  Diff vs another:  diff <out_dir>/pattern.json <other-out>/pattern.json
```

## Reusable patterns

Follow the [reusable pattern consumer contract](../../../skills/pattern/references/consumer-contract.md). The
vault output above is unchanged, including a custom `--out` location. To propose it for reuse,
convert the legacy `pattern.json` with `$LINTEL_SOURCE_ROOT/lib/pattern_visual.py`
`legacy_to_draft`: it emits a universal draft of defaults only, with observation confidence
(never confirmed) and the original bytes kept unchanged as a `visual-legacy` asset by digest;
unrecognized fields stay in that asset. Pass `source_ref` as a portable vault label (for example
`brand/design-patterns/<name>/pattern.json`) or an https URL, never an absolute or home path.
Stage the draft and that sidecar into a new scratch directory with `stage_draft`, then register
it only through `bash "$LINTEL_SOURCE_ROOT/bin/li-pattern" capture --input <dir>/pattern.json`,
which verifies and stages the declared files before registration; approval is separate. The
legacy `schema_version: 1` is not the universal schema. Never copy proprietary code, shaders or
assets without permission, and record fonts, accessibility and licensing as unknown unless
evidenced.

## Status protocol

- **DONE** — all 4 required files emitted + schema valid
- **DONE_WITH_CONCERNS** — extraction confidence "low" (screenshot-only, lots of inferred)
- **BLOCKED** — vault-collision without `--overwrite`, OR artifacts unreadable, OR compliance-fail
- **NEEDS_CONTEXT** — artifact-format unparseable

## Pause-points

- Vault-collision: surface options (overwrite | pick different name | abort) (m-3 resolution)
- Customer-share + source is customer-site: ask if extraction is authorized re-use
- Extraction-confidence low: surface "we inferred X from screenshot — verify before applying"

## Integration

**Reads:**
- `<artifacts>` (URLs, files, screenshots)
- The explicitly selected `<palette-out>/<name>.json` returned by generate-style-learn

**Writes:**
- `<out>/` (pattern artifacts and explicitly scoped raw evidence)
- Audit-log: `.claude/runtime/audit/frontend-style-extract-runs.jsonl`

**Calls into:**
- `agents/frontend/FrontendArchitect.md` (synthesis-direction, shared with the design orchestrator)
- `/li-generate-style-learn` (chained if `--with-palette` flag)
- `/li-compliance-gate` (if --customer-share)

**Consumed by:**
- `/li-frontend-design --pattern <name>` (vault lookup)
- `/li-frontend-design-review` (compare produced output vs vault baseline)

## --overwrite flag inheritance (m-3 resolution)

Pattern from `generate-style-learn`:
- Default: refuse to overwrite. Exit code 3.
- `--overwrite` flag: replace only the confirmed pattern write set, log to audit
  with `previous_pattern_hash`, and propagate the flag to the palette child only
  under the two-file authorization and preimage procedure above.

To preserve an earlier extraction, choose a different explicit owned `--out`.
Do not delete an existing tree to make the collision check pass.

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

- Reuse extracted pattern: `/li-frontend-design "<brief>" --pattern <name>` (Phase A1 orchestrator supports --pattern flag)
- Diff vs a selected baseline: `diff <out>/pattern.json <explicit-baseline>/pattern.json`
- L-001 vault-growth check: after 3+ operator-extracted patterns, re-evaluate whether the canonical one can be demoted to docs/samples/
