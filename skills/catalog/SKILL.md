---
name: catalog
layer: foundation
description: Use to discover Lintel skills by name, purpose or family, or regenerate the committed skill catalog after frontmatter changes.
color: yellow
tools: Read, Write, Bash, Glob, Grep
voice: internal
cli_support: [claude-code, codex, copilot]
---

# Skill catalog

`skills/CATALOG.md` is a generated view of canonical `skills/*/SKILL.md` frontmatter.
Use the existing generator's compact metadata for discovery before reading selected canonical
skill or role bodies. Source declarations are not native discovery, permission or verified
host execution. Copilot's native entrypoints remain the smaller, separately verified `li-*` set.

## Discover without regeneration

Resolve `LINTEL_SOURCE_ROOT` from the loaded trusted adapter or explicit operator-selected
Lintel source, not the target repository's working directory or a personal installation.
Use an available permitted shell and Python 3.9+ (`python` when that is the Python 3 command):

```bash
python3 "$LINTEL_SOURCE_ROOT/bin/li-catalog.py" --json
python3 "$LINTEL_SOURCE_ROOT/bin/li-catalog.py" --json --query="$keyword"
python3 "$LINTEL_SOURCE_ROOT/bin/li-catalog.py" --json --family=context
python3 "$LINTEL_SOURCE_ROOT/bin/li-catalog.py" --json --kind=agent --query="$keyword"
python3 "$LINTEL_SOURCE_ROOT/bin/li-catalog.py" --json --name=match
```

Only pass a query when the operator supplied a nonempty keyword. `--search` is an alias
for `--query`. Family filters are literal prefixes, not globs; query/filter values are
data, never shell fragments. Pass each as one quoted argument, without `eval` or command
construction. Listing and filtering do not write or regenerate `skills/CATALOG.md`.

Use returned names, descriptions, aliases and source-relative paths to choose the relevant
entry. Then read only the selected body beneath the returned, trusted `source_root`.
Preserve template/staged warnings and alias notes; inspect the selected method before
promising an output. `maturity: unknown` and frontmatter `full` hints do not establish
implemented formats, native registration or execution.

The [metadata reference](references/metadata.md) defines the output, filters, shared parser
dependency and source binding. On a helper/parser error, report the error rather than
inventing an empty inventory or parsing every prompt yourself. If execution is unavailable,
the existing trusted `skills/CATALOG.md` is a skills-only fallback; disclose that it is a
committed snapshot without agent metadata. An explicitly named canonical file can still
be read through a permitted file tool. Neither fallback activates a workflow.

## Generate and check

From the Lintel source root, run:

```bash
python3 bin/li-catalog.py
python3 bin/li-catalog.py --check
```

Use generation only when source maintenance is authorized, not while answering discovery
requests. The same deterministic generator runs in CI. CI fails on stale output and never commits
or pushes the catalog on behalf of the operator. Edit source descriptions, regenerate,
review the diff and commit both together. Missing frontmatter and an empty source tree
are errors; never replace a usable catalog with an empty or guessed result.

A trends overlay requires separately available, authorized usage data. Do not inspect
personal telemetry or add a transient sort order to the committed catalog.

## Source and output boundaries

In a consumer repo, read the catalog from the adapter's resource root. Regenerate only when
the task actually changes that source. Do not write the tooling catalog into project state.
Descriptions and source links are public output: keep them accurate and company-neutral.
