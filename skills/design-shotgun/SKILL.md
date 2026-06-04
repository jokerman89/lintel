---
name: design-shotgun
layer: foundation
description: Parallel design exploration — spawn N variants of a seed HTML, present side-by-side.
color: purple
tools: Read, Write, Bash, Glob
voice: internal
cli_support: [claude-code]
---

# /design-shotgun

Parallel variant generation. Takes a seed HTML (typically from `/design-html`) and a constraint axis (palette, layout, density, motion language), produces N variants by mutating along that axis, writes them as separate files, and assembles an index.html that shows them side-by-side for fast comparison.

The shotgun pattern: when you don't know what you want yet, generate many possibilities cheaply and pick.

## When to use

- Seed mockup exists; want to explore the design space around it
- Stuck between 2-3 directions and a structured side-by-side would clarify
- Design review with multiple operators needs a unified comparison artifact
- Early design phase where parallel exploration beats sequential refinement

## When NOT to use

- Direction is already clear — refine the seed instead of branching
- Constraint axis is "make it better" — too vague; pick a concrete axis
- Need pixel-level execution — shotgun is for direction, not finish

## Inputs

- Required `--seed <path>` — seed HTML file (from `/design-html` or hand-written)
- Required `--count <N>` — number of variants (2-8, default 4)
- Required `--axis <name>` — what to vary. Pick one:
  - `palette` — color system (warm/cool, mono/colorful, light/dark)
  - `layout` — structure (grid/list, hero-heavy/dense, centered/split)
  - `density` — information per viewport (sparse → dense)
  - `motion-language` — motion idiom (static/subtle/playful/dramatic)
  - `type-system` — type hierarchy (modest/expressive, serif-led/sans-led, condensed/wide)
- Optional `--brief <path>` — additional constraints layered on top
- Optional `--out <dir>` — output directory (default: `~/.lintel/design-shotgun/<ts>/`)

## Workflow

1. **Load seed.** Read seed HTML. Extract its structure into a manipulable form (sections, tokens used, copy slots).
2. **Define axis.** Map `--axis` to a set of concrete mutation rules. Example for `palette`: variant 1 = cool-mono, variant 2 = warm-mono, variant 3 = cool-accent, variant 4 = warm-accent.
3. **Generate variants in parallel.** Spawn N parallel workers (each can be a sub-process or sequential — see Failure modes). Each worker mutates the seed along the axis rule.
4. **Assemble index.** Create `index.html` with N iframes (or static screenshots if iframes are heavy) side-by-side, labeled, with a one-line description of each variant's design move.
5. **Report.** Output dir path. Open command. Mark which variant the skill would pick if forced (rationale optional).

## Variant axis rules (built-in)

```yaml
palette:
  - cool-mono     # blues/slates, monochromatic
  - warm-mono     # ambers/stones, monochromatic
  - cool-accent   # neutral base + single cool accent
  - warm-accent   # neutral base + single warm accent
  - high-contrast # near-black + near-white + one signal color
  - duotone       # two saturated colors in tension
  - pastel        # desaturated, light values
  - jewel-tone    # saturated, dark values

layout:
  - hero-heavy    # 60% viewport hero, content below
  - dense-grid    # 12-col, low padding, info-rich
  - split-screen  # 50/50 narrative + content
  - centered-narrow # max-width 720, single column
  - sidebar-led   # persistent navigation left
  - magazine      # asymmetric, editorial composition
```

(Other axes have similar built-in rule sets; see [SKILL.md inputs] for full set.)

## Report format

```
Design Shotgun: portal-dashboard

Seed: ~/.lintel/design-html/portal-dashboard-v3-20260527-163100.html
Axis: palette
Count: 4

## Variants

1. cool-mono    → variant-1-cool-mono.html (22KB)
                  Slate-100 base, slate-900 ink, no accent color
2. warm-mono    → variant-2-warm-mono.html (22KB)
                  Stone-100 base, stone-900 ink, no accent color
3. cool-accent  → variant-3-cool-accent.html (23KB)
                  Slate-100 base, emerald-600 single accent
4. warm-accent  → variant-4-warm-accent.html (23KB)
                  Stone-100 base, amber-600 single accent

Side-by-side: ~/.lintel/design-shotgun/20260527-164200/index.html
Preview: /open-managed-browser --url file://...

## Skill's pick (advisory)
Variant 3 (cool-accent). Reason: emerald accent maps to existing brand tokens; mono variants lose the brand signature.
```

## Compliance integration

- Variants inherit seed's compliance state. If seed had pack-voice copy: all variants do too, and the active pack's compliance gates apply to all of them.
- No production touch. No Layer 2 mutations.
- Output dir lives at `~/.lintel/design-shotgun/` — operator owns distribution.

## Voice tier note

`voice: internal`. Skill output is engineering-internal. Variants carry whatever voice the seed had.

## Failure modes

- **Seed unreadable / malformed HTML:** report + bail. Do not generate variants from a broken seed.
- **Axis name not in built-in set:** list available axes, exit. Do not silently invent.
- **Parallel worker crashes mid-generation:** generated variants persist; failed variants reported with which axis-rule they were assigned. Operator can re-run with `--only <axis-rule>` to fill gaps.
- **iframe-based index too heavy (>50MB):** fall back to screenshot-based index (one PNG per variant via `/browse`, embedded in index.html).
- **`--count > 8`:** refuse — beyond 8 the side-by-side stops being scannable.

## Examples

**Palette exploration:**
```
> /design-shotgun --seed ./seed.html --count 4 --axis palette
[Generates 4 variants]
✓ 4 variants, index at ~/.lintel/design-shotgun/.../index.html
```

**Layout exploration with brief:**
```
> /design-shotgun --seed ./seed.html --count 3 --axis layout --brief ./constraints.md
[Reads brief: "mobile-first, content-dense, no hero"]
[Filters layout axis to: dense-grid, centered-narrow, sidebar-led]
✓ 3 variants generated.
```

**Resume failed run:**
```
> /design-shotgun --seed ./seed.html --count 4 --axis palette --only warm-accent
[Re-runs just the one that failed previously]
```

## See also

- `/design-html` — generate the seed
- `/design-review` — review each variant after opening
- `/design-consultation` — pre-shotgun: which axis matters most?
- `/open-managed-browser` — open index.html for review
- `/make-pdf` — assemble winning variant as PDF deliverable
