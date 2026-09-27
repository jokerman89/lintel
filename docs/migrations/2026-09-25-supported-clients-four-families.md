---
slug: supported-clients-four-families
started_at: 2026-09-25
grace_until: none
removal_at: 2026-09-25
old_shape: 38 registry records (37 client surfaces in 14 families plus the manual other route), the Gemini extension, the OpenCode guide and the Gemini and Droid update routes in li-update
new_shape: 14 registry records (13 surfaces for GitHub Copilot, Claude, Codex and Cursor plus other); no Gemini, OpenCode or Droid routes
risk_class: medium
detect_pattern: grep -E '"(gemini|opencode|droid|factory|antigravity|kiro|devin|junie|cline|continue|aider)-' .github/lintel/manifest.json
---

# Supported clients narrowed to four families

ADR-0035 keeps GitHub Copilot, Claude, Codex and Cursor. This guide applies only if you used
one of the removed clients: Gemini, OpenCode, Factory Droid, Antigravity, Kiro, Devin/Cascade
(formerly Windsurf), Junie, Cline, Continue or Aider.

## Plugin and extension users

- **Gemini CLI:** the repository no longer ships `gemini-extension.json` or `GEMINI.md`, so the
  `li` extension stops working as a Lintel route. Remove it with `gemini extensions uninstall li`.
- **Factory Droid:** `li-update` no longer updates the `li` Droid plugin. Update or remove it with
  Droid's own plugin commands.
- **OpenCode:** `.opencode/INSTALL.md` is gone. Use the manual route below.

Any of these hosts can still use a repository kit installed with `--client other`. It bundles
the same canonical workflows, which the host reads explicitly through `.github/lintel/START.md`.
It does not provide native skill discovery.

## Repository kits that selected a removed surface

The multi-client installer was never in a tagged release, so this affects only kits initialized
from unreleased `main` before ADR-0035. `li-adapter.py check` and `init` refuse such a kit before
writing anything, because its inventory names a surface or discovery root that no longer exists.
To rebuild it:

1. Save any customizations of managed files; they are not preserved by this procedure.
2. Note the `clients` list in `.github/lintel/manifest.json`. Then delete, with your normal
   reviewed Git workflow, `.github/lintel/` and every other path listed under the manifest's
   `files` key. Those paths are always under `.github/agents/lintel-*`, `.github/skills/li-*`,
   `.github/instructions/lintel-session.instructions.md`, `.github/copilot-instructions.md` or
   a `.<root>/skills/li-*/SKILL.md` wrapper. Delete nothing else: a listed path outside these
   locations means the manifest was modified, so stop and inspect it.

   The removed discovery roots were `.gemini/skills`, `.opencode/skills`, `.factory/skills`,
   `.kiro/skills`, `.windsurf/skills`, `.devin/skills`, `.junie/skills` and `.cline/skills`.
   Antigravity shared Codex's `.agents/skills`, which a Codex surface regenerates.
3. From a Lintel checkout, run `python3 bin/li-adapter.py init --target <repo>` (`python` on
   Windows when that is your Python 3 command) with one `--client` for each supported surface you
   still want from that list, or `--client other`. Then run `check` with the same `--target`.

Project-owned files and prose are not touched. `init` takes over an existing session-protocol
block in `AGENTS.md` or `CLAUDE.md` only if it matches the current protocol. Otherwise it refuses
and preserves the file; remove the marked block to let `init` add the current one. The
`.gitattributes` lines that the earlier `init` added for removed roots are harmless and can be
deleted by hand.
