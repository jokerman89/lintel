---
name: generate-ppt
layer: foundation
description: Produce an editable PowerPoint deck through available native tools or pptxgenjs, retaining source detail in notes and inspecting actual rendered slides.
color: orange
tools: Read, Write, Bash, Glob
voice: mixed
cli_support:
  - cli: claude-code
    level: full
  - cli: codex
    level: degraded
    degradation:
      - capability: AskUserQuestion
        strategy: auto-pick-recommended
      - capability: Browser
        strategy: degraded-output
license_note: produces customer-bound output; honors the active pack's compliance gates for customer-facing voice tiers
---

# /generate-ppt

Produces an editable PowerPoint deck (.pptx) from a complete source brief. Visible
slides are a presentation view, not permission to discard evidence or reasoning.
Apply the selected profile's actual brand/voice requirements without inventing
neutral thresholds or scanning personal templates. Generation is not distribution.

## Prerequisites

Discover the actual host tool schemas first. Prefer an available native slide API:
on the Copilot canvas surface call `list_canvas_capabilities` for `powerpoint`,
then `open_canvas` on a new owned path and use discovered `get_model`, `batch`,
`set_notes` and `render_slide` actions. Follow the
[native PowerPoint procedure](references/native-powerpoint.md).

The existing declared Node alternative is `pptxgenjs`. Inspect its task-local
availability and supported operations before use; do not assume it imports an
arbitrary `.pptx` template. Record a missing-tool failure before considering an
authorized task-local restore. No automatic/global install or security bypass.
If no editable writer exists, retain the full source and mark PPTX blocked.
HTML/PDF/Markdown may be explicitly chosen alternatives, never silently relabelled
editable PowerPoint or rendered PPTX evidence.

## When to use

- Customer-engagement deliverable (pitch deck, workshop deck, summary deck)
- Internal presentation that needs the active pack's brand identity
- Reusing engagement-specific content across multiple PPT outputs
- Replacing manual PPT authoring with a workflow that has voice + brand + provenance gates

## When NOT to use

- One-slide quick mockup — `/design-html` is faster
- Non-PPT artifact — use `/generate-word` or `/generate-web`
- Pack compliance gate not satisfied AND output is customer-bound — resolve the gate first

## Inputs

- Required `--brief <path|inline>` — content brief describing the deck purpose **OR** `--from-pipeline <dir>` (shared pipeline mode)
- Required `--template <name|path>` unless `--use-defaults` is selected — resolve names only within the verified configured template directory
- Optional `--audience <text>` — primary audience (affects voice tier output)
- Optional `--slide-count <N>` — presentation-view target; retained advisory fallback is 20-30 slides based on duration, not a source-content cap
- Optional `--duration <minutes>` — presentation duration (informs slide pacing)
- Optional `--voice <tier>` — voice tier for slide content (default: the active pack's voice tier, `internal` by default)
- Optional `--use-defaults` — available neutral template or explicitly blank native deck; do not invent a bundled template
- Optional `--ignore-stale-brand <reason>` — advisory exception only; does not waive mandatory policy
- Optional `--out <path>` — new `.pptx` output (default: `<brief-stem>.pptx` in the working directory)

## From-pipeline mode (v3.5 Phase 2 — generate-pipeline integration)

If invoked with `--from-pipeline <run-dir>` instead of `--brief`:

Preserve this entry point and its existing fields. First follow
[existing pipeline input admission](../generate-write/references/fidelity-and-evidence.md#existing-pipeline-input-admission)
with `--format ppt`, external input context, original package/leaves and current
profile. It verifies canonical content/notes/hash identity and the existing PPT
projection without rendering. Shared theme/artifact acceptance remains the
A15.3.shared gate. Standalone `--brief` still needs no generate-design output or
new domain envelope.

1. **Read shared pipeline-output:**
   - `<run-dir>/content.md` — written content (with HTML-comment annotations for voice/type/key_message per section)
   - `<run-dir>/speaker-notes.md` — speaker notes per slide
   - `<run-dir>/design-spec.json` — per-format layout-mappings (read `per_format.ppt.layouts`)

2. **Replace brief-parsing logic** with direct-read of content.md sections +
   design-spec layouts. Do not run a second narrative rewrite that could discard
   shared content; the format-specific fidelity review in step 3 still applies.

3. **Apply format-specific design-pass via design_pass_hook:**
   - Reads `per_format.ppt.layouts[N].design_pass_hook` (canonical: PPTNarrativeArchitect)
   - Invokes agent for a PPT-specific fidelity-pass (slide-narrative-arc, FastPath-recommendations, animation-cues) on top of the shared baseline
   - Acknowledges plan-eng-review Reviewer Concern #7 — per-format design-agents stay per-format

4. **CLI stays backward-compat:** existing `--brief`-flag invocations work unchanged. `--from-pipeline` is additive.

5. **Use the same source-retention, native inspection and configured controls as
   standalone mode.** Layout mappings must not discard unmapped source detail.
   Keep complete returned content and notes, including facts not shown in a
   visible placeholder. Continuation layouts keep the original section ID.
   Select template/config overrides before admission and refresh final P05
   evidence after the deck is created or edited; input checks do not establish
   notes serialization, editability or rendered layout.

Existing skill arguments and data field names are retained; this is not a claim
that every host or shared-pipeline script has been executed.

## Workflow

1. **Preflight and policy:**
   - Follow the [P05/P07 evidence procedure](../generate-write/references/fidelity-and-evidence.md).
   - Select explicit source/output/template roots; refuse unapproved replacement.
   - Verify the pinned profile, actual template capability and requested inspections.
   - Derive mandatory versus advisory brand, voice, freshness and disclosure controls
     from applicable configuration and the brief, not a fixed score or age proxy.
   - A required missing tool/control remains blocked; neutral mode needs no logo.

2. **Read brief + extract structure:**
   - Goal / key message (one sentence)
   - Audience profile
   - All substantive sections, claims/evidence, tables, citations and material limitations
   - Opening context and closing decision/CTA where appropriate
   - Retain full source separately from the concise slide view

   **Standalone count selection:** Explicit `--slide-count` takes precedence.
   Honor brief/duration constraints before the retained 20-30 slides based on
   duration starting range; material, audience and pacing can justify an
   explained adjustment. This is an advisory fallback, not a mandatory gate,
   not a Word/web section quota, and not the outline stage's 8-15/default-12 hint.
   Surface conflicting explicit requirements without deleting source content.

2b. **Design DNA slide pass (ADR-0017 — retrieval before slide design).** Query the slide
   decision engine so the arc is grounded in the corpus, not invented:
   ```bash
   dna="${LINTEL_SOURCE_ROOT:?select the trusted source}/skills/design-dna"
   python3 "$dna/scripts/search.py" "<deck goal / pitch type>" --slide strategy -n 1   # narrative arc + sparkline-beats
   # then per slide, by the slide's emotion (trust|urgency|confidence…) and goal (hook|proof|cta…):
   python3 "$dna/scripts/search.py" "<emotion>" --slide color-logic -n 1   # background/text/accent + full-bleed
   python3 "$dna/scripts/search.py" "<goal>"    --slide layout-logic -n 1  # layout pattern + break-pattern
   python3 "$dna/scripts/search.py" "<slide-type>" --slide copy -n 1       # headline formula
   ```
   Feed the strategy's `sparkline_beats` + `emotion_arc` to PPTNarrativeArchitect as the arc spine.
   python3 absent → Read `design-dna/data/slides/*.csv` directly (controlled vocabulary in design-dna SKILL.md).

3. **Use the accepted read-only `PPTNarrativeArchitect` method** to design the arc;
   delegate only through a real available host operation, otherwise label the
   builder's own pass as self-review:
   - Slide-by-slide content goals — seeded by the slide-strategy `sparkline_beats`
   - Mode tags from the configured corpus when applicable; neutral is valid
   - Layout suggestions per slide — from `--slide layout-logic` (pattern + break-pattern at 1/3, 2/3)
   - Asset suggestions (from the active pack's asset library, if one is configured)

4. **Generate editable slides through the selected native API or pptxgenjs:**
   - Apply an explicit compatible template or the requested neutral blank design
   - Add slides per architect's arc
   - Compose readable visible text without changing the scope of source claims
   - Insert assets from the active pack's asset library where matched
   - Write complete supporting paragraphs, citations, tables and the claim ledger
     into actual speaker notes, an appendix or delivered linked long-form content.
     Always retain the full source. Put a material limitation on the visible slide
     whenever omitting it would misrepresent a visible claim.
   - Keep source §N IDs and record continuation/appendix locations. A slide-count
     target cannot authorize losing facts, shrinking illegibly or clipping text.

4b. **Critique narration using the accepted read-only `SlideNarrationCritic`
method** when a talk track exists. Supply the exact deck/notes, intended audience,
duration and current profile reference through the available host delegation
operation. Check pacing and recovery lines without deleting supporting evidence.
Keep speaker talk time separate from appendix/reference material. A claimed
words-per-minute target is not an observed rehearsal.

5. **Inspect the saved artifact, then apply the familiar control categories:**

   First reopen through the actual available application/API, make a small scoped
   edit and read it back. Compare full source to slides plus actual saved notes.
   Render every slide using the available renderer and inspect wrapping, overflow,
   overlap, table legibility and assets. Check notes separately; slides alone cannot
   prove note retention. Fix layout by reflow/splitting, not by discarding facts.

   **Voice:** apply only the verified corpus's requirements and applicability.
   Neutral clarity/pacing advice does not become a hard vocabulary or score gate.

   **Brand:** check configured template/tokens and explicitly authorized local
   assets. No invented logo, personal library scan or claim that a blank deck is
   company-branded. Missing mandatory brand data cannot silently fall back.

   **Honest limitations:** check each material claim against its evidence,
   assumptions and failure boundary, including claims on pitch/workshop slides.
   Disclosure requirements follow the brief/policy; counts cannot prove honesty.
   Record a grounded N/A only for a genuinely inapplicable requirement.

   **Provenance:** bind the exact brief, source content, notes, template/config,
   output and live P07 reference using existing P05 snapshot/control evidence.
   File metadata or a made-up provenance ID cannot replace those observations.

6. **Report the actual result at the explicit owned output path.**
   Mandatory failure/error/unverified blocks the affected acceptance or
   distribution regardless of scores. Retain useful editable output and its
   source while naming any missing renderer or review. Do not use an implicit
   personal draft directory. An API edit/readback is not every-client acceptance.

## Report format

Record exact source/output paths and hashes; actual profile/template; audience and
arc; slide-to-section/notes mapping; writer and native provider/instance/actions;
edit/readback result; rendered slides inspected and specific renderer limits;
retained claims, citations, table data and material limitations; configured
control outcomes; and remaining acceptance/review gates. Keep documentary checks,
package extraction, native actions and render evidence separate.

## Compliance integration

- Configured applicable controls keep their mandatory/advisory semantics.
- No customer data, secrets, macros, external upload or automatic asset download
  in synthetic validation. Use explicit authorized local assets.
- Required independent review and delivery controls remain separate from creation.

## Voice tier note

`voice: mixed`. Skill itself is engineering-internal; the SLIDE CONTENT may use a customer-facing voice tier (gated by Gate 1).

## Failure modes

- **Writer error** — preserve source and the owned draft, record the actual error; do not emit a passing gate.
- **Required template missing** — block; offer neutral defaults only when applicable policy permits.
- **Voice gate fails after 2 regen attempts** — keep draft, surface specific slide failures with fix recommendations
- **Required asset unavailable** — report its exact gap; do not invent a successful asset inspection.
- **Renderer absent** — retain editable deck/source but keep rendered-layout acceptance unverified.
- **Customer-data in brief** — BLOCK before generation. Sanitize first.

## Examples

**Standard pitch deck:**
```
> /generate-ppt --brief docs/engagement/customer-A-pitch-brief.md --template pitch-deck --audience "public-sector CIO"
[Resolve the explicit template, preserve evidence, and inspect the actual artifact.]
```

**Workshop deck with defaults:**
```
> /generate-ppt --brief synthetic-brief.md --template workshop --use-defaults --voice internal --out workshop.pptx
[An explicitly blank native deck is valid neutral output; configured requirements still apply.]
```

**Stale brand override:**
```
> /generate-ppt --brief archive-pitch.md --template pitch-deck --ignore-stale-brand "archival deliverable, brand version pinned"
[Records an advisory exception; does not waive required brand policy.]
```

## See also

- [Native PowerPoint procedure](references/native-powerpoint.md)
- [Content fidelity and evidence](../generate-write/references/fidelity-and-evidence.md)
- `PPTNarrativeArchitect` agent — slide arc design
- `SlideNarrationCritic` agent — slide narration / talk-track critique (post-generation)
- The active pack's compliance gates — Gate 1
- `/generate-word`, `/generate-web` — sibling doc-gen skills
- `brand-staleness-warn` hook — Phase E
