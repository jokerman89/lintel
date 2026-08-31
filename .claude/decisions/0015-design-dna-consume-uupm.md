# ADR-0015: Design DNA — consume the UI/UX Pro Max corpus as Lintel's retrieval layer

- **Status:** Accepted
- **Date:** 2026-06-13
- **Deciders:** operator (mandate 2026-06-12), Claude (execution)
- **Supersedes:** —
- **Superseded by:** —

## Context

Lintel's design family (v3.7 `frontend-*` decision layer + `generate-*` rendering layer) made
every visual choice from model memory: ~20 fonts and 7 motion libraries listed in prose, no
palette knowledge, no UX-rule corpus, no per-stack rules, an optional/stubbed review gate, and a
`frontend-design-spec.json` contract with no palette field. Output quality depended entirely on
what the invoked model happened to free-associate.

The operator mandated (2026-06-12) consuming nextlevelbuilder/ui-ux-pro-max-skill (v2.5.0, MIT
— license verified in-repo) entirely and rebuilding its quality mechanisms into Lintel, better.
Research (4 reports, `.claude/runtime/research/`) identified what actually produces its results:
**retrieval before generation** — a mandatory BM25 search over curated CSVs (84 styles, 161
WCAG-audited palettes, 161 product reasoning rules with anti-patterns + severity, 73 font
pairings, 99 UX rules, 16 per-stack rule files) composed by reasoning rules, plus mandatory
pre-delivery checklists and one hard mechanical validator.

**L-001 tension:** Lintel ships scaffolding, not curated content. This corpus IS curated
content. Negotiation: it is *reference data* (like `lib/cli-tiers.yaml`) — third-party-
maintained, re-syncable from upstream, consumed at invocation time, not self-authored content
that rots with pricing pages. The operator explicitly authorized the consumption. This ADR is
the explicit L-001 exception record.

## Decision

We consumed the UUPM corpus + search engine into `skills/design-dna/` (new module skill:
search | system | stack | persist | validate | profile) and wired retrieval into the design
family: `frontend-design` Step 1.5 (required DNA pass), corpus-query steps in
`frontend-typography`/`frontend-motion`, stack-guidance passes + mechanical Gate 0 in
`generate-web`/`generate-app`, validator pre-pass in both review skills. The spec contract
gained additive optional fields (`palette`, `style`, `design_dna`); `schema_version` stays 1.

## Alternatives considered

- **Build our own corpus from scratch**: months of curation for a worse v1; the operator's
  mandate was explicitly to reuse ("allt är MIT-licens... återbruka det man vill"). Rejected.
- **Keep UUPM as an external dependency (install their skill alongside)**: no integration with
  Lintel's spec contract, pack system, or gates; their own repo shows data-drift between its
  three copies. Rejected — consume once into a single canonical tree.
- **Consume everything including the generation skills**: logo/CIP/banner/slides generators are
  Gemini-API-keyed (different concern, fails without keys) and the google-fonts dump is 43% of
  corpus weight for a lookup table. Rejected — corpus + search + validator only; subtractions
  recorded in ATTRIBUTION.md; slide decision-engine flagged as a generate-ppt follow-up.

## Consequences

- **Positive:** every design decision starts from vetted options with anti-patterns attached;
  the review gate is mandatory and partly mechanical (objective violations exit 1); per-stack
  Do/Don't rules reach the rendering layer; quality floor no longer depends on model memory.
- **Positive (vs upstream):** single canonical tree (their cp-r sync already drifted their own
  template); graceful python-absent degradation (CSVs stay grep-readable — they just die);
  full-harness wiring (search → spec → render → gate) where they stop at "synthesize".
- **Negative:** 720K of third-party CSV in the repo; upstream re-sync is manual (re-copy +
  re-apply the registry patch documented in `scripts/core.py`); a python3 dependency on the
  happy path (degradation documented).
- **Neutral:** L-001 now has one recorded exception class: third-party reference corpora.

## Implementation notes

Shape contract: `tests/shape/design-dna-corpus.sh` (corpus present, subtractions hold,
attribution intact). Behavior: `tests/unit/design-dna-search.sh` +
`tests/unit/design-validator.sh` (positive AND negative per L-012).

## References

- Design doc: `.claude/engineering/design-archive/lintel-v5.4-design-dna-design.md`
- Research: `.claude/runtime/research/{A1,A2,B,C}*.md` (runtime, not committed)
- ADR-0016 (anthropic-default profile), L-001, L-004 (split preserved: design-dna feeds the
  decision layer, decides nothing itself)
- Attribution: `skills/design-dna/ATTRIBUTION.md`
