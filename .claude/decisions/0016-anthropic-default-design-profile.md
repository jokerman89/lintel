# ADR-0016: anthropic-default — Anthropic's design system as Lintel's default design profile

- **Status:** Accepted
- **Date:** 2026-06-13
- **Deciders:** operator ("vår default design är anthropics designsystem, EXAKT det anthropic
  har", 2026-06-12), Claude (execution)
- **Supersedes:** —
- **Superseded by:** —

## Context

Lintel had no house design default: `brand.color_tokens` was declared in the pack schema with
zero callsites (dead), the spec contract had no palette field, and every run's aesthetic was
whatever the model invented. The operator decided the default design for everything Lintel
produces is Anthropic's design system, exactly, with packs able to override (company identity
is pack-driven — a customer pack ships its own brand).

Token source (research C): Anthropic's published `brand-guidelines` skill (Apache-2.0,
© 2026 Anthropic, PBC) carries exactly 7 color tokens (ink `#141413`, paper `#faf9f5`,
neutral-mid `#b0aea5`, neutral-subtle `#e8e6dc`, accents `#d97757`/`#6a9bcc`/`#788c5d` with an
ordered cycle) and two font roles (Poppins display ≥24pt / Lora body — the skill's own OFL
substitution for the licensed Styrene/Tiempos faces). Their `frontend-design` skill carries the
doctrine (two-pass token plan, anti-cliché calibration, "spend your boldness in one place").
Everything else a complete profile needs (type scale, spacing, radius, shadows, motion tokens,
dark mode, semantic states, mono face, breakpoints, dataviz ramp, contrast matrix) is specified
NOWHERE in the sources — 16 gaps requiring deliberate decisions.

Derived contrast math constrains usage: accents on paper are ~3:1 — they fail WCAG AA for body
text and are graphic/display-only. Ink-on-paper is 16.8:1.

## Decision

We shipped `skills/design-dna/profiles/anthropic-default.yaml`: the 7 canonical tokens +
font roles (marked `source: canonical`) plus deliberate gap-fills (marked `source: derived`).
Resolution seam: `resolve_pack_field design.profile`, null → `anthropic-default`. The frozen
pack contract is untouched — the field is additive-by-convention; packs override by shipping
their own profile. Precedence everywhere: **brief > profile > corpus hit**.

## Alternatives considered

- **Hardcode Anthropic tokens into the spine (skills/agents)**: violates the v4.7 pack
  extraction ("never reintroduce hardcoded company/voice assumptions into the spine").
  Rejected — profile file + pack-resolvable seam.
- **Add `design.profile` to `packs/_default/pack.yaml` + pack-schema**: touches the frozen pack
  contract (~30 skill dependency) for a default that code-fallback handles identically.
  Rejected for v1 — revisit if a second profile consumer needs schema-level validation.
- **Wait for operator-licensed Styrene/Tiempos**: license friction for every consumer repo;
  the published skill's own substitution is OFL and redistributable. Rejected — Poppins/Lora
  ship as default; operators who license the real faces override per pack (gap G16).

## Consequences

- **Positive:** every Lintel-rendered artifact has a coherent, accessible house look by
  default; the dead `brand.color_tokens` ambiguity is resolved by a live, documented seam;
  contrast rules are machine-checkable (validator reads the profile's hexes).
- **Negative:** the warm-cream + serif + terracotta look is adjacent to a named AI-cliché
  (their own frontend-design skill's calibration list). Mitigation baked into
  FrontendArchitect: a pinned direction is a choice, not a default — differentiate through
  craft (type scale, signature element, spacing), never through palette novelty.
- **Negative:** derived gap-fills are Lintel's taste, not Anthropic's spec — marked
  `source: derived` so a future canonical source can replace them without archaeology.
- **Neutral:** Apache-2.0 obligations carried in `ATTRIBUTION.md` + profile header; trademark
  hygiene per §6 — descriptive naming only, no marks shipped, output never marketed as
  Anthropic-branded.

## References

- Design doc: `docs/design/lintel-v5.4-design-dna-design.md` · ADR-0015
- Research C: `.claude/runtime/research/C-anthropic-design-dna.md` (token cites BG:21-57,
  doctrine FD:9-43, license analysis)
- Shape contract: `tests/shape/design-dna-corpus.sh` (asserts the 7 canonical hexes verbatim)
