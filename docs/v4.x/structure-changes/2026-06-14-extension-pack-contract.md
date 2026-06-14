---
slug: extension-pack-contract
date: 2026-06-14
cycle_id: s4l-extension-pack
operator: jokerman
affected_paths:
  - packs/_default/pack.yaml
  - lib/pack-resolver.sh
  - bin/li-pack-scaffold
  - skills/pack-switch/SKILL.md
  - tests/shape/extension-pack-contract.sh
risk_class: medium
breaking_change: false
---

# Structure change: extension-pack-contract

> Gate M1 (structure-impact analysis) artifact. Meta-infra mode, ADR-0018.

## What changed (shape)

The pack contract gained an optional top-level `extension:` block (flat / two-level):
`is_extension` · `namespace` · `workflow` · `provides_skills` · `provides_agents` ·
`provides_hooks`. This lets a pack be an **extension pack** — a pack that is also a Claude
Code plugin shipping its own `skills/ agents/ hooks/` and a workflow, declared so Lintel is
aware of it. `_default` ships the block with `is_extension: false` (i.e. unchanged behavior).

Companion shape deltas: `lib/pack-resolver.sh` gained three awareness helpers
(`pack_is_extension`, `pack_namespace`, `pack_workflow`) and a `validate_pack` rule (when
`is_extension: true`, `namespace` + `workflow` are required); `bin/li-pack-scaffold` is a new
generator that emits an extension-pack skeleton (plugin manifest + `pack.yaml` + dir tree).

## Backward-compat

- **Identity-only packs (every existing pack):** unaffected. `extension:` is optional; absent or
  `is_extension: false` means "not an extension pack" and no code path changes. `validate_pack`
  already ignored unknown blocks, so older packs without the block still validate.
- **`resolve_pack_field` callers (~30 skills):** unchanged — the resolver is untouched except for
  three additive helper functions; the two-level parser is not modified. The `extension:` fields
  are flat precisely so the existing two-level resolver reads them.
- **`pack-switch`:** additive Step 5b only fires for extension targets; identity switches print as before.

## Migration path

No migration needed — additive change. Existing packs require no edits; `_default` documents the
new block as off.

## Forward-compat

Enables packs to ship executable surface (skills/agents/hooks/workflow) as first-class capability
extensions — the foundation for the S4L pack and any future domain pack. Does **not** change how the
host CLI discovers skills (still the plugin manifest); Lintel adds *awareness*, not a second
discovery path. Forecloses nothing — identity-only packs remain the default shape.

## Verification

- Shape-tests added: `tests/shape/extension-pack-contract.sh` (21 assertions: _default off, resolver
  + helpers, validate_pack enforcement of ns/workflow, li-pack-scaffold emits a validating skeleton).
- Existing shape-tests affected: none (additive).
- Regression coverage: full `tests/runner/run-all.sh` must stay green (resolver is on the critical path
  for ~30 skills); the new test pins the contract against future cleanup sweeps reverting it.

## Rollback procedure

Revert the five affected files. The `extension:` block is inert for identity packs, so a partial
rollback (leaving the block in `_default` but removing the resolver helpers / scaffolder) is also
safe — the block is just documentation until a pack sets `is_extension: true`.
