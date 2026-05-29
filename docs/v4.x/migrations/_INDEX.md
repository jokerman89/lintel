# v4.x Migrations Index

Durable tracker for v4.x migration windows. Each row points to a migration file under `docs/v4.x/migrations/<date>-<slug>.md`. `/li:migrations` reads this file at session-start.

> Per v4.0 design Chapter 4 §5.5: this index is the durable tracker. `tasks/memory.md` stays ephemeral. Migrations live here for the entire grace + removal window.

## Active migrations

| Slug | Started | Grace until | Removal at | Description |
|---|---|---|---|---|
| _none yet_ | — | — | — | Phase 1 ships nothing breaking |

## Archived migrations

| Slug | Started | Closed | Outcome |
|---|---|---|---|
| _none yet_ | — | — | — |

## Format

Each entry in `docs/v4.x/migrations/<date>-<slug>.md` has frontmatter:

```yaml
---
slug: <kebab-case>
started_at: YYYY-MM-DD
grace_until: YYYY-MM-DD
removal_at: YYYY-MM-DD
old_shape: <description>
new_shape: <description>
risk_class: low | medium | high
detect_pattern: <grep/find pattern operator can run to find callsites>
---
```

When grace expires → migration moves from `## Active` to `## Archived` (operator file PR removing detect_pattern from `/li:migrations` surface).
