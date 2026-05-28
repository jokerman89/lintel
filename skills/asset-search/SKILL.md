---
name: asset-search
layer: ms-team
description: Search ~/.lintel/brand/azure-assets/ for the right icon or diagram primitive.
color: green
tools: Read, Bash, Glob, Grep
voice: internal
cli_support:
  - cli: claude-code
    level: full
  - cli: codex
    level: full
  - cli: copilot-cli
    level: full
  - cli: copilot-app
    level: full
---

# /asset-search

Search the registered MS Azure asset library for icons, primitives, diagram elements. Returns paths + tags + dimensions for use in doc-gen.

## When to use

- Mid-`/generate-ppt` — find the right Azure service icon
- Mid-`/generate-web` — find a primitive (arrow, box) for a diagram
- Operator hand-authoring a doc and needs the canonical Azure SQL icon, etc.
- Verify a brand pull landed all expected categories

## When NOT to use

- `~/.lintel/brand/azure-assets/` empty (no brand pull yet) — run `/brand-update` first OR use defaults
- One-off non-Azure imagery — operator's own asset library, not this skill

## Inputs

- `--query <text>` — natural language search (e.g. "azure sql", "queue arrow", "load balancer")
- `--tag <tag>` — filter by explicit tag (e.g. `service:sql`, `primitive:arrow`)
- `--category <cat>` — filter by category (`services`, `primitives`, `diagrams`)
- `--limit <N>` — max results (default: 10)
- `--format <yaml|json|paths-only>` — output format

## Workflow

1. **Load asset index** from cache (`~/.lintel/brand/.cache/asset-index.yaml`). If cache empty: rebuild from `~/.lintel/brand/azure-assets/`.
2. **Match query.** Use:
   - Filename match (e.g. "azure-sql.svg" → match "azure sql")
   - Tag match (parsed from filename or sidecar `.json` metadata)
   - Category filter if provided
3. **Rank.** Filename-direct matches first, tag matches second, partial matches last.
4. **Return.** Paths + tags + dimensions per result.

## Report format

```yaml
asset_search:
  query: "azure sql"
  results:
    - path: ~/.lintel/brand/azure-assets/services/azure-sql-database.svg
      tags: [service, sql, database, azure]
      dimensions: { width: 64, height: 64, format: svg }
      relevance: high
    - path: ~/.lintel/brand/azure-assets/services/azure-sql-managed-instance.svg
      tags: [service, sql, mi, database]
      dimensions: { width: 64, height: 64, format: svg }
      relevance: high
    - path: ~/.lintel/brand/azure-assets/diagrams/sql-architecture-pattern.svg
      tags: [diagram, sql, pattern]
      dimensions: { width: 320, height: 240, format: svg }
      relevance: medium
  total_in_library: 87
  matched: 3
```

## Compliance integration

- Read-only on `~/.lintel/brand/`. No Layer 2 concern.
- Asset paths not committed to git.
- Output is paths-only by default — operator copies the path into their work.

## Voice tier note

`voice: internal`.

## Failure modes

- **No `~/.lintel/brand/azure-assets/`** — surface "no brand pulled" + recommend `/brand-update`. Return empty.
- **Index cache stale** — auto-rebuild on first search after brand-update. Subsequent searches fast.
- **Query too broad** (returns 50+ matches) — recommend narrower query or `--category` filter.
- **No results** — suggest alternative spellings + show top-5 categories present in library.

## Examples

**Find Azure SQL icons:**
```
> /asset-search --query "azure sql"
[3 results returned]
```

**Diagram primitive:**
```
> /asset-search --query "arrow right" --category primitives
[2 results: standard-arrow.svg, dashed-arrow.svg]
```

**Tag-based search:**
```
> /asset-search --tag "service:storage"
[6 storage-category service icons]
```

**Paths-only for piping:**
```
> /asset-search --query "load balancer" --format paths-only --limit 1
/Users/jokerman/.lintel/brand/azure-assets/services/azure-load-balancer.svg
```

## See also

- `BRAND-INTEGRATION.md` — asset organization
- `/brand-update` — registers + indexes the library
- `/generate-ppt`, `/generate-web` — primary consumers
- brand-version.txt — current brand version (`/brand-update --verify`)
