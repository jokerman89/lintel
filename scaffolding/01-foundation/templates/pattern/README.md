# Pattern authoring template

This directory holds the authoring material for data-only reusable patterns (ADR-0038). The
workflow is `skills/pattern/SKILL.md`, and consumers follow
`skills/pattern/references/consumer-contract.md`.

- `pattern.template.json` is a valid **draft** to copy and edit. Capture it with
  `li-pattern capture --input <file> --scope repo|personal --name <id> [--source-id <namespaced.id>]`.
  Then review it and approve a new version with `li-pattern approve`.
- `example/` is the one canonical, neutral and synthetic example. It is a complete pattern source
  (catalog, one approved pattern, one asset and a source-local `.gitattributes`). It is not
  curated team policy. Copy it only to learn the format, and replace its owner, sources, selector
  and clauses with your own confirmed expectations.

## Layouts

| Scope | Where the source lives | How it is activated |
| --- | --- | --- |
| Repository | `.claude/patterns/` in the working repository (`catalog.json`, optional `bindings.json`, `<id>/<version>/` directories) | Automatically: repository bindings and catalog bindings apply at repository scope |
| Pack | `patterns.source: <relative/catalog.json>` in the pack manifest, relative to the declaring pack root | Only the effective `patterns.source` and its pinned includes are active; pack bindings apply at pack scope |
| Personal | `$LINTEL_HOME/patterns/` | Never automatic: only an explicit `--refs` entry or a repository binding selects a personal pattern |

A pack declares `patterns: { source: patterns/catalog.json }` in its `pack.yaml`. The bundled
neutral pack declares `source: null`.

Changing the neutral manifest invalidates bound profile contexts. After an upgrade, rebind each
context explicitly with a reason and re-plan dependent work. Nothing rebinds automatically.

## Keep file bytes exact

Every declared asset and pinned `root: pattern` source is checked against its sha256 over the
**raw bytes**. The canonical JSON digest protects only the pattern record. If Git line-ending
conversion rewrites an asset (for example, a repository-wide `*.md text eol=lf` rule applied to a
CRLF asset), its digest no longer matches after a fresh clone, and `check` and `read_asset` report
`unavailable`.

Keep a source-local `.gitattributes` beside the catalog, as `example/.gitattributes` does:

```text
* -text
```

- **Repository source:** put it at `.claude/patterns/.gitattributes`.
- **Pack source:** put it in the directory that holds the pack's pattern catalog.

Git applies the most specific attributes file, so this changes only the pattern source. It never
rewrites an existing file.

If your repository already has an authoritative attributes policy for that path, do not override
it silently. Either decide explicitly to adopt `* -text` for the pattern source, or commit the
assets with bytes the policy already preserves. Then re-check with `li-pattern check`.

Git is not a runtime requirement: patterns work from any directory, and this matters only when
the source travels through Git.

## Checks

- `li-pattern check` validates every registered entry, including each version's declared files.
- `li-pattern list` reads only catalog metadata.
- Missing Python 3.10+ is "pattern check unavailable" (exit 5), never "no patterns".
