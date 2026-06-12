# Attribution — design-dna consumed sources

This skill consumes and adapts third-party material. Both licenses permit reuse,
modification and redistribution; notices are preserved here per their terms.

## UI/UX Pro Max (corpus + search engine)

- Source: https://github.com/nextlevelbuilder/ui-ux-pro-max-skill (v2.5.0)
- License: MIT License, Copyright (c) 2024 Next Level Builder
- Consumed: `data/*.csv` + `data/stacks/*.csv` (the curated design corpus: styles,
  palettes, products, reasoning rules, font pairings, UX guidelines, charts, landing
  patterns, icons, per-stack rules) and `scripts/{core,search,design_system}.py`
  (BM25 search + design-system composition + master/overrides persistence).
- Modifications (ADR-0015): `google-fonts` domain removed (728K lookup ballast;
  typography keyword routing widened to compensate); `design.csv`, `draft.csv`,
  `_sync_all.py` and the Gemini-keyed generation skills not consumed; structured
  comment headers added. `scripts/validate_design.py` is a Lintel rewrite *inspired
  by* their `html-token-validator.py`, not a copy.
- Upstream re-sync: re-copy from `src/ui-ux-pro-max/{data,scripts}` (their canonical
  tree) and re-apply the registry patch documented in `scripts/core.py`.

MIT License text: https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/blob/main/LICENSE

## Anthropic example skills (anthropic-default profile)

- Source: `brand-guidelines` and `frontend-design` skills, anthropics/skills
  (example-skills marketplace)
- License: Apache License 2.0, Copyright 2026 Anthropic, PBC
- Consumed: the 7 brand color tokens, the Poppins/Lora typography roles, usage rules,
  and the design doctrine (two-pass process, anti-cliché calibration, "spend your
  boldness in one place") — distilled into `profiles/anthropic-default.yaml` and the
  FrontendArchitect agent guidance. Derivative work; modified (gap-fills for type
  scale, spacing, radius, shadows, motion, dark mode, semantic states are Lintel
  decisions marked `source: derived`).
- Trademark note (Apache-2.0 §6): "anthropic-default" is descriptive of origin only.
  No Anthropic marks are shipped; no endorsement is implied. Output produced with
  this profile must not be marketed as Anthropic-branded.

Apache License 2.0 text: https://www.apache.org/licenses/LICENSE-2.0
