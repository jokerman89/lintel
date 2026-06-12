---
slug: subtraction-release
date: 2026-06-12
cycle_id: subtraction-20260612
operator: jokerman
affected_paths:
  - docs/concepts/skill-protocol.md (new — the protocol stated once)
  - skills/ (166 → 124; ceremony diet across ~93 files)
  - skills/{ta,da,sc,dh,tq}/SKILL.md (dispatch tables; 35 sub-skill dirs removed)
  - skills/role/ (new — lifecycle; 6 role skills removed)
  - skills/gbrain-setup, gbrain-sync (removed, 0 refs)
  - agents/customer/WorkshopFacilitator.md (removed, 0 dispatchers)
  - config/aliases.yaml (+41 aliases, 2 retired)
  - tests/shape/{ta,da,sc,dh,tq}-module-contract.sh (assert tables, not dirs)
risk_class: medium
breaking_change: true
---

# Structure change: subtraction-release

> Gate M1 artifact — ADR-0009.

## What changed (shape)

| Cut | Before → after |
|---|---|
| Skill surface | 27.0k → 20.8k lines (−23%) · 166 → 124 skills |
| Engineering sub-skills | 35 files (4,404 lines) → 5 dispatch tables; invoke `/li:ta api-design` |
| Role family | 8 commands / 1,217 lines → 3 / 383 (`role`, `role-new --update`, `roles-list`) |
| Ceremony | ~700 boilerplate lines stripped where they restated docs/concepts/skill-protocol.md |
| 0-ref tail | gbrain-setup, gbrain-sync, WorkshopFacilitator removed |
| Agents | 70 → 69 |

New optional frontmatter: `hop_in: no` (6 skills). The audit estimated ~60% of size was
reachable; the judgment-applied result is 77% — the difference is sections that LOOKED like
ceremony but carried real gates (customer-data blocks, license confirms, verdict taxonomies)
and were kept by exception. That is the diet working as designed.

## Backward-compat

Every removed skill name resolves via config/aliases.yaml (35 sub-skills → modules, 6 role
commands → role/role-new; grace to 2026-09-12) EXCEPT setup-brain/sync-brain/gbrain-* which
retire without successor (0 references; documented in the aliases file). Module behavior,
checkpoints, rubrics and thresholds preserved verbatim in the dispatch tables.

## Migration path

Operators: old names route automatically; the sub-skill form becomes `/li:<module> <capability>`.
No data moves. Removal of aliases: 2026-09-12.

## Forward-compat

New skills follow docs/concepts/skill-protocol.md — protocol sections only on deviation.
Module capabilities are table rows; promoting a row back to a file requires evidence of
solo-invocation demand.

## Verification

- Suite 75/75 on the tree post-cut (module contracts now assert dispatch tables)
- frontmatter-lint, uniformity-coverage, workflow-root-navigation, alias tests all green
- CATALOG + wiki regenerated (124/69)

## Rollback

git revert restores the files; aliases are additive and revert cleanly.
