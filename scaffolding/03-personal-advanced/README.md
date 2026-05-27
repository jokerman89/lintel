# Layer 3 — Personal advanced

Opinionated workflow choices. The interesting layer for anyone wanting to scale past basic usage.

## What lives here

- **`voice/`** — Trailblazer voice tier infrastructure. Per-agent `voice:` declaration mechanism. Sanitized corpus. TEST + CALIBRATION for `/rais-customer-voice-check`. **Currently populated:** OurVoice-test.md, OurVoice-corpus.md (skeleton awaiting operator content), OurVoice-calibration.md (pending), README.md.
- **`precedence/`** (pending Phase 1 completion) — 5-level agent selection precedence model + selection-flow decision tree.
- **`promoted-agents.md`** (pending Phase 4) — tier-stamped Level-2 promoted agents list (permissive vs restricted).
- **`harness-selection.md`** (pending Phase 1 completion) — when to use which harness pattern by project type.

## Change rate

**Opinionated.** Changes don't go through `EVOLUTION.md`'s heavy process, but they DO change how the team works across projects. PR-based with team review.

## Why this layer exists

With 80+ agents and 60+ skills installed in v1, default description-matching fails. A promoted-agents list with tier-stamping makes routing predictable. A precedence model makes "which agent fires" deterministic.

## The voice tier mechanism (load-bearing)

Per-agent frontmatter declares which voice an agent's output uses:

```yaml
---
name: CustomerVoiceWriter
description: Drafts customer-facing demo content per MS Our Voice
voice: trailblazer
cli_support: [claude-code]
tools: Read, Edit, Write
---
```

Three valid values:
- `voice: internal` — direct, builder-talking-to-builder (gstack-style). Default.
- `voice: trailblazer` — Kind + Daring + Deep, 3 modes, 6 ground rules. For customer-facing / official-communication output ONLY.
- `voice: mixed` — agent produces both kinds in different sections (e.g., `TransparencyDocAuthor` writes internal-tone docs that get polished for customer publish later).

`verify.sh --voice-tier-validity` rejects unknown values.
`/rais-customer-voice-check` runs against `voice: trailblazer` agent output; bypassed for `voice: internal`.
