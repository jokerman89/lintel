---
slug: design-dna
date: 2026-06-13
cycle_id: v5.4-design-dna
operator: jokerman
affected_paths:
  - skills/design-dna/ (NEW — module skill + corpus + scripts + profiles)
  - skills/frontend-design/SKILL.md
  - skills/frontend-typography/SKILL.md
  - skills/frontend-motion/SKILL.md
  - skills/generate-web/SKILL.md
  - skills/generate-app/SKILL.md
  - skills/frontend-design-review/SKILL.md
  - skills/design-review/SKILL.md
  - agents/frontend/{FrontendArchitect,TypographyCurator,MotionDirector,DesignSystemAuditor}.md
  - tests/shape/design-dna-corpus.sh (NEW)
  - tests/unit/{design-dna-search,design-validator}.sh (NEW)
risk_class: medium
breaking_change: false
---

# Structure change: design-dna

> Gate M1 (structure-impact analysis) artifact for ADR-0015/0016.

## What changed (shape)

1. NEW module skill `skills/design-dna/` carrying a consumed third-party reference corpus
   (27 CSVs, 720K, MIT-attributed), three consumed python scripts (stdlib-only), one Lintel-
   written validator, and a `profiles/` directory with `anthropic-default.yaml`.
2. `frontend-design-spec.json` contract: three ADDITIVE optional fields — `palette`, `style`,
   `design_dna`. `schema_version` stays 1 (minor-additive per the existing evolution policy);
   readers tolerate absence.
3. A new pack-resolvable field BY CONVENTION: `design.profile` (resolver returns null →
   `anthropic-default`). `packs/_default/pack.yaml` and `lib/pack-schema.yaml` are NOT touched.
4. `frontend-design` Step 7 changed from optional stub to mandatory gate (validator exit 1 →
   BLOCKED).

## Backward-compat

- Existing `frontend-design-spec.json` v1 readers (generate-web, generate-app, roundtrip test)
  work unchanged — new fields are optional.
- Packs that declare nothing get anthropic-default; packs that ship `design.profile` +
  a profile file override cleanly.
- All existing skill invocations (`--brief`, `--from-pipeline`, `--from-frontend-design`)
  unchanged; new steps are internal to the workflows.
- Repos without python3: every new search step documents a grep fallback; the validator
  degrades to the review checklist.

## Migration path

No migration needed — additive change.

## Forward-compat

Enables: pack-shipped design profiles (company identity for design, sister to voice corpora);
corpus re-sync from upstream (documented in ATTRIBUTION.md); future profiles (e.g. a customer
pack's brand) without touching the spine. Forecloses: nothing — the corpus can be removed by
deleting `skills/design-dna/` + reverting 7 SKILL.md edits (no other coupling).

## Verification

- Shape-tests added: `tests/shape/design-dna-corpus.sh` (37 assertions: corpus present,
  subtractions hold, 7 canonical hexes verbatim, attribution intact, consumers wired)
- Behavior tests added: `tests/unit/design-dna-search.sh` (engine answers domain/stack/compose
  queries; auto-detect survives the google-fonts subtraction; negative: unknown stack rejected),
  `tests/unit/design-validator.sh` (positive + negative gate assertions per L-012)
- Existing shape-tests affected: none renamed/moved; frontmatter-lint covers the new SKILL.md
- Regression coverage: full suite green on the committed tree (L-010) before push

## Rollback procedure

`git revert` the v5.4 commit range (corpus, profile+skill+validator, integration, agents,
tests, docs — atomic commits on feat/v5.4-design-dna). No state migrations to unwind; runtime
artifacts (`docs/design-system/` in consumer repos) are plain markdown the operator keeps or
deletes.
