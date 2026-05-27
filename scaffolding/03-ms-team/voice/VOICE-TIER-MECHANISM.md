# Voice Tier Mechanism

JStack's per-skill / per-agent voice-tier system. Explains the `voice:` frontmatter and how it propagates through the toolchain.

## The three voice tiers

Every skill, agent, and authored content artifact carries a `voice:` frontmatter declaration:

### `voice: internal`

Engineering-internal speech. Builder-talking-to-builder. Direct, technical, no rhetorical flourish.

**Use for:**
- Test reports, audit output, code review findings
- Internal-only design docs, ADRs
- Diagnostic / debug prose
- The 5 always-on rules, the 7 on-demand items
- Most skills + agents (default)

**Examples in JStack:**
- `/qa`, `/qa-only`, `/investigate`, `/review`, `/release-ev2` — all internal
- `CodeReviewer`, `SecurityAuditor`, `TestRunner` agents — all internal

### `voice: trailblazer`

Microsoft "Our Voice" (Trailblazer) speech for customer-facing surfaces. Kind + Daring + Deep, mode-tagged paragraphs, ground-rules-respecting.

**Use for:**
- Customer-bound deliverables (script, handout, follow-up, demo)
- Customer-facing AI output (Copilot responses)
- Public web pages, marketing copy
- Customer transparency notes (under voice + provenance gates)

**Examples in JStack:**
- `/msvoice-rewrite` skill — produces trailblazer-voice from internal-voice source
- `/demo-deliverable-gen` skill — produces trailblazer-voice from substance + key-message
- The customer-facing PDF/handout that's been gated through `/rais-customer-voice-check`

### `voice: mixed`

Skill or artifact that consumes one tier and produces / references the other. Body explicitly tags which sections are which.

**Use for:**
- Skills that GENERATE trailblazer content but PRODUCE internal-voice reports about it
- Documentation that contains both engineering-internal explanation AND customer-bound copy as examples
- Reviewers that score trailblazer content via internal-voice prose

**Examples in JStack:**
- `/design-review` — reviews trailblazer-content but report itself is internal
- `/document-generate` — `--target customer-guide` produces mixed (trailblazer body + internal scaffolding)
- `/landing-report --voice trailblazer` — engineering-summary scaffolding + trailblazer-bound narrative paragraphs

## How voice propagates

### At skill/agent invocation

When a skill or agent is invoked, the runtime reads the frontmatter:

```yaml
---
name: jstack-msvoice-rewrite
voice: trailblazer
---
```

The runtime knows: anything this skill writes that lands as an artifact carries `voice: trailblazer` propagation. Downstream skills can detect this.

### Through hooks

Hooks read the `voice:` frontmatter of edited files:

- `no-en-vocab-in-trailblazer` — fires only on `voice: trailblazer` edits
- `no-trailblazer-without-corpus` — fires only when voice is trailblazer + corpus uncalibrated

### Through gates

- `/rais-customer-voice-check` — required ANY time `voice: trailblazer` content leaves the building
- `/provenance-track` — REQUIRED before distribution of `voice: trailblazer` artifacts

## Why per-skill voice tier

Two reasons:

**1. Honest scoping.** The voice rubric is hard. The 12-cell Trailblazer rubric is appropriate for customer-bound copy; applying it to a test report would be ridiculous. Per-skill voice keeps the rubric applied where it belongs.

**2. Hook efficiency.** Hooks scan content based on voice tier. Without the tier, a hook would either scan everything (false-positive flood) or nothing (miss the real cases). With the tier, scope is precise.

## The mixed-voice pattern

Mixed-voice skills follow this pattern:

```markdown
## Engineering-internal section (default voice: internal)
The Skill produces structured output...

## Output section (voice: trailblazer-DRAFT)
<the actual customer-bound content, mode-tagged>
```

The skill's own prose is internal. The SKILL'S OUTPUT may be trailblazer. Output artifacts get their own frontmatter declaring the tier.

## Trailblazer-DRAFT vs trailblazer

A subtle but important distinction:

- `voice: trailblazer-DRAFT` — content has been generated as trailblazer but has NOT yet passed `/rais-customer-voice-check`. Cannot be distributed.
- `voice: trailblazer` (or `voice: trailblazer-FINAL`) — content has passed the voice gate AND has a `/provenance-track` record. Can be distributed.

The DRAFT marker is honest about UNCERTIFIED state. Downstream tooling refuses to distribute DRAFT.

## Operator overrides

In rare cases the operator may need to bypass voice machinery:

- `--ignore-stale-calibration` on `/rais-customer-voice-check` (logs reason)
- `--uncalibrated` on `/msvoice-rewrite` (logs reason)
- `JSTACK_OVERRIDE_VOICE=1` env var for one-off scripts that produce trailblazer without going through skills

All overrides are audit-logged. Periodic `/caip-audit` surfaces overrides for review.

## Why three tiers, not two or five

Two tiers (internal/trailblazer) would force every skill to pick one — many skills genuinely consume trailblazer and produce internal report.

Five tiers (internal/trailblazer-draft/trailblazer-final/customer-internal/etc.) over-specifies and bloats the rubric.

Three tiers (internal/trailblazer/mixed) covers the realistic distribution + matches the operator's mental model.

## See also

- [OurVoice.md](OurVoice.md) — what trailblazer voice actually is
- [OurVoice-corpus.md](OurVoice-corpus.md) — calibration anchor
- `/rais-customer-voice-check` skill — the gate
- `/provenance-track` skill — the record-keeping
- `02-sdl/hooks/no-en-vocab-in-trailblazer/` — voice-aware hook
