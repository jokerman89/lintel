# ADR-0017: Close the UUPM parity gaps — slide decision engine + three-layer tokens

- **Status:** Accepted
- **Date:** 2026-06-13
- **Deciders:** operator ("our design tools must be better than UI/UX Pro Max — that's the requirement", 2026-06-13), Claude (execution)
- **Supersedes:** —
- **Superseded by:** —
- **Amends:** ADR-0015 (records two additional consumed subsystems + the deliberate scope-outs)

## Context

After v5.4 shipped (ADR-0015/0016) the operator set a hard requirement: Lintel's design tools
must be **strictly better** than UI/UX Pro Max, not just architecturally cleaner. An adversarial
completeness audit (a dedicated agent, byte-level data diff + check-by-check validator comparison)
was run to verify the claim rather than assert it.

Verdict: on the **core engine** (BM25 search, design-system composition, MASTER/pages persistence,
the 27 shared + stack data files) Lintel was at parity-or-better, with a stronger accessibility-
first validator and a swappable profile system replacing UUPM's hardcoded brand. But UUPM ships
**five periphery skills** Lintel had no home for, and two were genuine design-*intelligence* gaps
that blocked an honest "strictly better" claim:

1. **Slide decision engine** — 8 CSVs mapping emotion→color, goal→layout, plus narrative
   strategies carrying Duarte sparkline-beats and copy formulas. Lintel's generate-ppt had a
   narrative agent but no retrieval-grounded decision data.
2. **Three-layer token architecture** — primitive→semantic→component token system + generator.
   Lintel's profiles were flat token sets with no layering or emitter.

## Decision

Closed both P1 gaps the same way ADR-0015 consumed the core (vendor data + register in the
existing engine — a data move, not structural):

- **Slides:** vendored the 8 slide CSVs into `skills/design-dna/data/slides/`, registered
  `SLIDE_CONFIG` + `search_slide()` in `core.py` and a `--slide <domain>` flag, exposed a `slide`
  capability in the dispatch table, and wired generate-ppt Step 2b to query it (strategy arc +
  per-slide emotion→color / goal→layout).
- **Tokens:** vendored the token-architecture reference docs; wrote `emit_tokens.py` (stdlib
  YAML-subset parser) that reads the active profile and emits a layered `design-tokens.css`
  (primitive → semantic aliases → component starters). Added two token-discipline **warnings** to
  the validator (var() usage, hardcoded font) — warnings, never hard errors, per L-012.

**Deliberately scoped OUT** (documented, not silently dropped):
- **Individual Google Fonts catalog lookup** (1,924-row CSV): the 73 curated pairings + the
  frontend-typography agent cover font *selection*; a 745K catalog for arbitrary by-subset/by-axis
  lookup is ballast against the subtraction bias. Re-add only if offline arbitrary-font lookup
  becomes a real need.
- **Logo / CIP / banner / social generators:** Gemini-API-keyed content generators. Per L-001,
  Lintel ships structure + retrieval, not content generators that need external keys and rot.
  These are a separate skill-family decision, not a parity gap in the design-knowledge core.

## Alternatives considered

- **Port UUPM's separate `slide_search_core.py`**: a second BM25 engine duplicating ours. Rejected
  — our generic engine already does BM25; registering the slide CSVs as domains reuses it.
- **Require PyYAML for emit_tokens**: breaks the stdlib-only portability contract. Rejected — wrote
  a tolerant line parser that survives our own profile format (incl. the `#hex`-in-quotes trap).
- **Re-add google-fonts + build the generators to claim "everything they have"**: bloat (745K) +
  large external-key-dependent surface for capabilities outside the design-knowledge core.
  Rejected — "better" means better at producing design, not feature-count parity on content
  generators.

## Consequences

- **Positive:** the "strictly better" claim is now honest on every design-*intelligence* dimension
  — retrieval-grounded slide design (which generate-ppt lacked), a real three-layer token system
  with a generator (which no Lintel profile had), plus everything from v5.4. On the core we were
  already ahead (a11y-first validator, swappable profiles); the periphery gaps that mattered are closed.
- **Negative:** two more vendored data subsystems to re-sync from upstream (procedure in
  ATTRIBUTION.md); slide search needs the controlled emotion/goal vocabulary (documented in SKILL.md).
- **Neutral:** the honest residual scope — google-fonts catalog + content generators — is recorded
  as a deliberate non-goal, not a gap. The defensible claim is now: "strictly better at design
  retrieval, slide intelligence, token architecture, and a11y validation; we deliberately do not
  ship their Gemini-keyed content generators."

## References

- Audit: adversarial completeness agent (2026-06-13), gap table in the session record
- ADR-0015 (core consume), ADR-0016 (anthropic-default), L-001 (scaffolding-not-content),
  L-012 (warnings-not-hard-gate), the subtraction bias
- Attribution: `skills/design-dna/ATTRIBUTION.md`
- Shape contract: `tests/shape/design-dna-corpus.sh`; behavior:
  `tests/unit/{design-dna-search,design-tokens-emit,design-validator}.sh`
