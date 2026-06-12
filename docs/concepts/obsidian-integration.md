# Obsidian integration — the L6 layer made navigable

> Implements ADR-0007. Builds on the capture vault sink (docs/concepts/capture-vault-sink.md)
> and the v5 `.claude/` home (ADR-0005). Pack-gated, write-only, optional.

## What ships

Four research-validated patterns, nothing more:

1. **Locked session-note schema.** CAPTURE Step 7b writes flat typed frontmatter
   (`created` · `type: session` · `repo` · `branch` · `outcome` (controlled vocabulary) ·
   `tags` · `session`). Flat properties are what Bases and the vault's own skills can query.
2. **`sessions.base` dashboard.** `bin/li-vault-init` installs a Bases view (core plugin) over
   the session notes — sortable by repo/branch/outcome, plus an "Open threads" view
   (`outcome != shipped`). Headless later via `obsidian base:query --format=json`.
3. **Deliberate wikilinks, graph for free.** Every session note links `[[<repo-hub>]]` and its
   predecessor session. The hub note's backlinks panel IS the per-repo session history; the
   graph clusters sessions around hubs without any graph-specific work.
4. **Agent-maintained index.** CAPTURE regenerates `00-index.md` (newest 15, wikilinked) — the
   cheap read path that makes the vault navigable instead of a write-only graveyard.

## Repo as read-vault

`.obsidian/` is gitignored everywhere (v4.12), so any Lintel repo opens directly in Obsidian.
With the v5 layout this is genuinely useful: `.claude/memory/lessons.md` (with `[[L-NNN]]`
cross-references), `.claude/decisions/`, `.claude/plans/` are wikilink-friendly markdown — the
repo's `.claude/` is a mini-vault of the harness's own knowledge. Open the repo (or just
`.claude/`) as a vault to see the work graph.

## Division of labor with the operator's vault

Lintel WRITES well-formed notes; the vault's own automation (e.g. `today`, `connect`,
`weekly-review` skills) does the synthesis. Lintel deliberately does NOT duplicate rollups or
synthesis — well-formed frontmatter is the interface that makes the user's workflow better,
whatever it is.

## Deliberately skipped (research-validated)

- **Vault → agent read path** — where token pain lives (MCP read blowups); the sink stays
  write-only. The one sanctioned read is the operator pasting from the vault.
- **Canvas generation** — spec frozen since 1.0; generated canvases don't get reopened.
- **Smart Connections / Copilot plugins** — human-side tools, wrong consumer.
- **Dataview** — maintenance mode; Bases is the target.
- **PARA/Zettelkasten ceremony** — the vault's own CLAUDE.md owns its conventions; Lintel
  adapts to the sink dir it is given and never reorganizes the vault.

## Configuration

Reuses the existing pack keys — no new surface: `capture.vault_sink_enabled` +
`capture.vault_sink_path` (neutral default: OFF/null; operators opt in via their pack or a
local `~/.lintel/packs/_default` override). `li-vault-init` resolves the same path.
