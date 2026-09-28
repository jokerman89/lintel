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
  - skills/design-dna/scripts/design_contract.py
  - skills/design-dna/references/design-contract.md
  - skills/generate/scripts/pipeline_inputs.py
  - skills/generate-web/references/mockup.md
  - skills/pattern/references/consumer-contract.md
  - tests/shape/{pattern-contract,skill-descriptions-trigger}.sh
  - .claude/plans/reusable-patterns/
  - .claude/decisions/0038-reusable-patterns.md
risk_class: medium
breaking_change: false
---

# Structure change: reusable patterns

> Gate M1 (structure-impact analysis) artifact for ADR-0038. Updated by the integration owner
> after the PACK and WF joins, the INT packaging and the RN-14/RN-15 join corrections, 2026-09-28.

## What changed (shape)

A data-only runtime module (`lib/patterns.py`) and JSON CLI (`bin/li-pattern.py`), with
registered unit tests. One module validates the pattern, catalog, binding, context, reference,
override, exception, roots-envelope, resolution-report and lock records. The integrated feature
also has:

- **Pack field.** The optional pack manifest field `patterns.source`. The neutral pack declares it
  `null`; ADR-0029 provenance records it.
- **Launcher.** `bin/li-pattern` builds the roots envelope from the ADR-0029 profile record. A
  missing runtime reports "pattern check unavailable".
- **Workflow.** The canonical `skills/pattern/` workflow, its single consumer contract, and the
  generated `li-pattern` native wrapper.
- **Consumers.** Consumer wiring in the cycle, document-pipeline, engineering and frontend skills.
  The `generate-web` direct `--mode mockup`/`--brief` entries resolve for themselves (RN-14).
- **Visual adapter.** `lib/pattern_visual.py`: projection, validation, pipeline attachment and
  palette winners.
- **Design loader.** A verified-pattern palette admission in
  `skills/design-dna/scripts/design_contract.py` `load_design`, and its
  `renderer-args`/`review` CLI and `skills/generate/scripts/pipeline_inputs.py` caller (RN-15).
  With an optional pattern lock and current context that the core verifies and P05 selects, a
  selected pattern palette winner outranks the pinned Design DNA profile. Without one, loading
  is unchanged. A spec that carries a `pattern_context` without its lock is refused.
- **Packaging.** The authoring template with one neutral example, and the docs.

No hook, MCP server, scheduler, service, network access, frontmatter field, cycle phase,
work-map field, installer, policy, or P05/P07 schema changes. Profile and corpus files are never
modified.

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

Revert the feature commits as a whole, by an ordinary revert of the feature merge. Consumer
skills, the launcher and the Copilot kit reference the module, and `design_contract.load_design`
and `pipeline_inputs` gained optional pattern arguments. Reverting only part of it would leave
dangling references or refused `pattern_context` specs. After a revert:

- run `li-copilot.py init` and `li-catalog.py` to regenerate the managed outputs;
- rebind profile contexts that were bound to the manifest carrying `patterns.source: null`,
  explicitly and with a reason, as described in the upgrade notice.

Repository `.claude/patterns` data stays inert. Locks and task maps remain historical files.
