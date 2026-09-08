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
Read it to discover existing workflows before designing another skill. Copilot's native
entrypoints are the smaller `li-*` adapter set; the complete catalog is available on demand
and is not a claim of validated host parity.

## Generate and check

From the Lintel source root, run:

```bash
python3 bin/li-catalog.py
python3 bin/li-catalog.py --check
```

The same deterministic generator runs in CI. CI fails on stale output and never commits
or pushes the catalog on behalf of the operator. Edit source descriptions, regenerate,
review the diff and commit both together. Missing frontmatter and an empty source tree
are errors; never replace a usable catalog with an empty or guessed result.

For `--search <keyword>` or `--family <prefix>` requests, filter the catalog or source
frontmatter for display. A trends overlay is a session report over available usage data;
do not add private telemetry or a transient sort order to the committed catalog.

## Source and output boundaries

In a consumer repo, read the catalog from the adapter's resource root. Regenerate only when
the task actually changes that source. Do not write the tooling catalog into project state.
Descriptions and source links are public output: keep them accurate and company-neutral.
