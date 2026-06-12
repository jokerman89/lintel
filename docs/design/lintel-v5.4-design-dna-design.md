# Lintel v5.4 — design DNA: retrieval-augmented design + anthropic-default profile

> component: design-dna-design
> implements: ADR-0015, ADR-0016
> intent: this document
> constraints: L-001 (negotiated exception, see ADR-0015), L-004 (decision/execution split preserved)
> last_intent_review: 2026-06-13

Operator mandate (2026-06-12): consume https://github.com/nextlevelbuilder/ui-ux-pro-max-skill
(MIT, verified) entirely, rebuild its quality mechanisms into Lintel's own skill system, and make
the result better. Default design for everything Lintel produces: Anthropic's design system,
exactly, built through the new workflow. "Allt vi producerar ska ge det bästa som finns."

Research basis: `.claude/runtime/research/{A1-uupm-core,A2-uupm-periphery,B-lintel-design-surface,C-anthropic-design-dna}.md` (4 reports, 2026-06-12/13).

## What UUPM actually does that produces its results (A1/A2 findings)

1. **Retrieval before generation.** A mandatory `--design-system` search runs BEFORE any design
   decision: BM25 (stdlib Python, zero deps) over curated CSVs — 84 styles, 161 palettes
   (WCAG-audited, shadcn-shaped), 161 product types, 161 reasoning rules with JSON decision
   conditions + anti-patterns + severity, 73 font pairings, 99 UX rules, 16 per-stack rule files
   (Do/Don't/Code-Good/Code-Bad/Severity). The model picks from vetted options instead of
   free-associating from memory.
2. **Anti-patterns as first-class data.** Every recommendation carries "avoid X" (incl. the named
   "AI purple/pink gradients" anti-slop rule). The forbidden-six (no emoji icons / cursor-pointer /
   no layout-shift hover / 4.5:1 contrast / 150-300ms motion / visible focus) repeats at every
   output surface.
3. **Mandatory pre-delivery checklists** + one hard mechanical gate (an HTML token validator,
   regex forbidden-patterns, exit 1).
4. **Persistence with precedence.** `design-system/MASTER.md` + `pages/<page>.md` overrides, the
   precedence contract written INTO the artifacts, so consistency survives across sessions.
5. **Config-as-data multi-platform distribution** (18 platforms from 1 template + 25-line JSONs) —
   validates Lintel's own manifest approach; we don't need their CLI.

Their weaknesses (we do better): manual `cp -r` data sync already drifted their own canonical
template ("React Native is this project's only stack" leaked into the generic base); 18× data
duplication; no graceful degradation without Python; no tests on the skill path; retrieval stops
at "synthesize and implement" — no wiring into build/review/ship.

## Lintel current state (B findings)

frontend-* (decision) / generate-* (render) split per L-004 with `frontend-design-spec.json` as
contract — but the spec has **no palette/color field**, the knowledge behind every choice is
~20 fonts/7 motion libs in prose (model memory, no retrieval), the review gate is optional and
stubbed, `brand.color_tokens` pack field is declared but dead (zero callsites), and no curated
corpus exists anywhere.

## Decision 1 (ADR-0015) — consume the UUPM corpus + search as `skills/design-dna/`

New module skill `design-dna` (knowledge + retrieval layer; it makes no rendering decisions, so
the L-004 split is preserved — it FEEDS the decision layer):

```
skills/design-dna/
  SKILL.md              # dispatch table: search | system | persist | validate | profile
  data/*.csv            # corpus from UUPM src/ui-ux-pro-max/data/ (canonical tree)
  data/stacks/*.csv     # 16 per-stack rule files
  scripts/search.py     # BM25 search        (adapted, attribution headers)
  scripts/core.py       #   engine
  scripts/design_system.py  # multi-domain compose + reasoning rules + persist
  scripts/validate_design.py # hard gate (adapted from UUPM html-token-validator)
  profiles/anthropic-default.yaml
  ATTRIBUTION.md        # MIT (c) 2024 Next Level Builder + Apache-2.0 (c) 2026 Anthropic, PBC
```

Exclusions (subtraction): `google-fonts.csv` (728K = 43% of corpus, lookup ballast — domain
registry patched), `draft.csv` (dead backup), `_sync_all.py` (their maintenance tooling),
the Gemini-keyed generation skills (logo/CIP/banner/slides/social), their brand Node scripts
(Lintel has packs), their CLI (Lintel has install + manifests).

**L-001 negotiation:** this is reference data (like `lib/cli-tiers.yaml`), third-party-maintained,
re-syncable from upstream, consumed at invocation — not self-authored curated content. The
operator explicitly mandated the consumption. Recorded as an explicit L-001 exception in ADR-0015.

**Degradation:** python3 absent → SKILL.md instructs direct CSV reads (grep/Read) with the same
domain → file map. The CSVs stay LLM-greppable (UUPM just dies here; we don't).

## Decision 2 (ADR-0016) — `anthropic-default` design profile as harness default

`profiles/anthropic-default.yaml`: the 7 canonical tokens (ink #141413, paper #faf9f5,
neutral-mid #b0aea5, neutral-subtle #e8e6dc, accents #d97757/#6a9bcc/#788c5d with ordered cycle),
Poppins/Lora (OFL; the Anthropic skill's own substitution for Styrene/Tiempos), plus deliberate
derived gap-fills (type scale, spacing, radius, shadows, motion tokens, dark mode, semantic
states, mono, breakpoints, dataviz ramp, contrast-pair matrix) — every block marked
`source: canonical|derived`. Constraint carried from research: accents are graphic/display-only
(~3:1 on paper — never body text); ink/paper is 16.8:1.

**Resolution seam (no pack-contract change):** skills resolve `resolve_pack_field design.profile`;
null/missing → `anthropic-default`. Packs override by shipping their own profile. The frozen
pack.yaml is untouched; the field is additive-by-convention. Trademark hygiene per Apache-2.0 §6:
the profile is *described* as derived from Anthropic's published skills; no marks shipped, no
endorsement implied.

## Workflow rewire (the "new car")

```
brief → frontend-design Step 1.5 (NEW, required): design-dna system search + active profile
      → typography/motion/shader dispatch (sub-agents receive corpus hits + profile defaults)
      → FrontendArchitect synthesizes spec  (+ two-pass doctrine: token plan → self-critique)
      → frontend-design-spec.json           (additive fields: palette, style, design_dna)
      → generate-web / generate-app          (NEW step: per-stack search before render)
      → validate_design.py + pre-delivery checklist (NEW, mandatory — review no longer optional)
```

- `frontend-design-spec.json`: additive optional fields `palette`, `style`, `design_dna`
  (provenance). `schema_version` stays 1 — readers unaffected; roundtrip test verified.
- Agents get judgment, not bloat (ADR-0014 house style): FrontendArchitect carries the two-pass
  doctrine + the three named AI-cliché looks + "spend your boldness in one place";
  DesignSystemAuditor runs validator-first; TypographyCurator/MotionDirector query the corpus
  before picking.
- Persistence: `design-dna persist` writes `docs/design-system/MASTER.md` + `pages/<page>.md`
  in the TARGET repo (committed knowledge, v5 philosophy) with the self-describing precedence
  contract.

## Gates

- M1: this doc + structure-changes entry. M2: `bin/li-compat-audit` (expect YELLOW on spec-field
  addition; additive). M3: full shape suite + 3 new tests (corpus shape, search behavior,
  validator behavior). M4: CAPTURE recap + migration row (none needed — additive).
- Collision checks from B honored: no `*design-spec*` filename introduced; skill name `design-dna`
  collides with nothing; `~/.lintel/brand/` untouched; frozen zones untouched.

## Out of scope (flagged, not silent)

Slide decision-engine (emotion→layout CSVs) → follow-up candidate for generate-ppt. Logo/CIP/
banner/social generators → Gemini-keyed, separate concern. Their google-fonts dump → dropped;
revisit if typography flow needs alternatives lookup beyond the 73 pairings.
