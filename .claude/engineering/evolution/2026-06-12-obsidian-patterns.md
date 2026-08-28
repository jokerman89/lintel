---
slug: obsidian-patterns
date: 2026-06-12
cycle_id: claude-home-20260612
operator: jokerman
affected_paths:
  - bin/li-vault-init (new)
  - templates/obsidian/sessions.base (new)
  - skills/capture/SKILL.md (Step 7b schema + links + index)
risk_class: low
breaking_change: false
---

# Structure change: obsidian-patterns

> Gate M1 artifact — ADR-0007.

## What changed (shape)

New operator tool `bin/li-vault-init` (installs sessions.base + repo hub + index seed into an
existing vault, idempotent, never overwrites). New `templates/obsidian/` directory. CAPTURE
Step 7b's vault note gains three locked frontmatter fields (`type`, `branch`, `outcome`), a
Links section (hub + predecessor wikilinks), and index/hub maintenance instructions.

## Backward-compat

Additive. Pre-existing vault notes lack the new fields — they simply don't appear in the
filtered Bases views. The sink remains config-gated and OFF in the neutral pack. No pack-key
changes.

## Migration path

No migration needed — additive change. Operators with an active sink run `bin/li-vault-init`
once (optional).

## Forward-compat

The frontmatter schema is the contract; sessions.base and any future vault tooling key on it.
Schema changes require an ADR superseding ADR-0007.

## Verification

- tests/unit/obsidian-patterns.sh (vault-init idempotency + schema pinned in capture prose)
- full suite green (see PR)

## Rollback

git revert; vault files are operator-owned and unaffected by a revert (additive, never
overwritten by the tool).
