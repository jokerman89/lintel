---
slug: reusable-patterns
date: 2026-09-28
cycle_id: reusable-patterns-20260928
operator: jokerman
affected_paths:
  - lib/patterns.py
  - bin/li-pattern.py
  - tests/unit/patterns.py
  - tests/unit/patterns.sh
  - .claude/plans/reusable-patterns/
  - .claude/decisions/0038-reusable-patterns.md
risk_class: medium
breaking_change: false
---

# Structure change: reusable patterns

> Gate M1 (structure-impact analysis) artifact for ADR-0038. Later packages extend
> `affected_paths` (pack lane, workflow lane, generator outputs); this entry is updated
> by the integration owner when those lanes land.

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

None required. Repositories may add `.claude/patterns/catalog.json` and
`.claude/patterns/bindings.json`; legacy visual `pattern.json` assets stay readable.

## Forward-compat

Enables versioned locks, per-package clause projections, review coverage and local sharing.
Forecloses automatic policy promotion from inferred observations and implicit personal
activation.

## Verification

- Unit: `tests/unit/patterns.sh` (schema, path, selector, authority and include classes).
- Contract and evidence: `.claude/plans/reusable-patterns/contract.md` and `build-log.md`.

## Rollback procedure

Revert the feature commits. Nothing else reads the new module until later packages wire it.
