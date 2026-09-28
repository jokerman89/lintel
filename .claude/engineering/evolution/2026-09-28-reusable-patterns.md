---
slug: reusable-patterns
date: 2026-09-28
cycle_id: reusable-patterns-20260928
operator: jokerman
affected_paths:
  - lib/patterns.py
  - lib/pattern_visual.py
  - bin/li-pattern.py
  - bin/li-pattern
  - bin/li-copilot.py
  - lib/paths.sh
  - lib/pack-schema.yaml
  - packs/_default/pack.yaml
  - skills/pattern/
  - skills/{sense,scope,define,discover,cycle,plan,build,resume,review,ship,capture}/SKILL.md
  - skills/{generate,generate-outline,generate-write,generate-design,generate-qa,generate-word,generate-ppt,generate-pdf,generate-xlsx,generate-visio}/SKILL.md
  - skills/{ta,da,sc,dh,tq}/SKILL.md
  - skills/{frontend-style-extract,generate-style-learn,frontend-design,generate-web,design-dna,frontend-typography,frontend-motion,frontend-shader,generate-app,frontend-design-review}/SKILL.md
  - skills/{pack-create,pack-validate}/SKILL.md
  - skills/CATALOG.md
  - .github/skills/li-pattern/SKILL.md
  - .github/lintel/manifest.json
  - scaffolding/01-foundation/templates/pattern/
  - docs/concepts/patterns.md
  - docs/{architecture,the-cycle,multi-cli,copilot}.md
  - tests/unit/{patterns,pattern-visual,pattern-pack-origins,pattern-launcher-roots}.*
  - tests/unit/pattern_pack_harness.py
  - tests/integration/{pattern-workflows,pattern-visual-roundtrip,pattern-portability}.*
  - tests/integration/pattern_consumer_fixtures.py
  - tests/integration/design-contract.py
  - tests/shape/{pattern-contract,skill-descriptions-trigger}.sh
  - .claude/plans/reusable-patterns/
  - .claude/decisions/0038-reusable-patterns.md
risk_class: medium
breaking_change: false
---

# Structure change: reusable patterns

> Gate M1 (structure-impact analysis) artifact for ADR-0038. Updated by the integration owner
> after the PACK and WF joins and the INT packaging, 2026-09-28.

## What changed (shape)

A new data-only runtime module and CLI with registered unit tests. Pattern, catalog,
binding, context, reference, override, exception, roots-envelope and resolution-report
records are validated by one module. No hook, MCP server, scheduler, service, network
access, frontmatter field, cycle phase, work-map field or state schema changes. Planned
later packages add an optional `patterns.source` pack field, a launcher, a canonical
pattern workflow, consumer wiring and a visual adapter.

## Backward-compat

Additive. Without configured pattern sources, no workflow behavior changes and no file is
written. Existing pack accessors, profile context records and review evidence are unchanged.

## Migration path

Upgrading an installation replaces the neutral pack manifest, which invalidates bound profile
contexts (ADR-0029 drift). Rebind each active context explicitly with a reason, then re-plan
dependent work. See ADR-0038 "Upgrade notice". No automatic rebind exists.

There is no data migration. The only required action is that explicit, reason-bearing context
rebind. Repositories may add `.claude/patterns/catalog.json` and `.claude/patterns/bindings.json`;
legacy visual `pattern.json` assets stay readable.

## Forward-compat

Enables versioned locks, per-package clause projections, review coverage and local sharing.
Forecloses automatic policy promotion from inferred observations and implicit personal
activation.

## Verification

- Unit: `tests/unit/patterns.sh`, `pattern-visual.sh`, `pattern-pack-origins.sh` and
  `pattern-launcher-roots.sh`.
- Integration: `tests/integration/pattern-workflows.sh`, `pattern-visual-roundtrip.sh` and
  `pattern-portability.sh`. The last one covers the installed kit, a non-Git root, the missing
  runtime, and CRLF assets through Git for repository and pack sources.
- Shape: `tests/shape/pattern-contract.sh`.
- Contract and evidence: `.claude/plans/reusable-patterns/contract.md` and `build-log.md`.

## Rollback procedure

Revert the feature commits. Nothing else reads the new module until later packages wire it.
