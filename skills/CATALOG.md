# Lintel Skill Catalog

**Auto-generated från frontmatter.** Regenerated av `.github/workflows/catalog.yml` per push när `skills/**/SKILL.md` ändras. Hand-edits skrivs över — edit frontmatter i source SKILL.md istället.

> Initial seed för v3.6 cohort 2 item 1.6. Faktisk catalog populeras vid första CI-run efter merge.

To regenerate locally: `/li:catalog --regenerate`

## How to use this catalog

- **Find a skill:** Ctrl-F för name eller keyword i description
- **Browse by family:** Look at `--family <name>` på `/li:catalog --family generate` för all generate-* skills
- **See trends:** `/li:catalog --trends` overlayer usage-frequency (om usage-log seeded)

## Coming after first merge

Layer-sections will appear here automatically:
- Foundation layer (~20 skills)
- MS-team layer (~70 skills)
- SDL layer (~15 skills)
- Personal-advanced layer (~8 skills)

Each row format:
```
| /li:<name> | <description from frontmatter> |
```

Total target: ~113 skills + auto-trending if usage-log present.
