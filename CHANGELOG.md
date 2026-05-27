# Changelog

All notable changes to this repo are tracked here. Format is loose — date headings + bulleted changes. Major behavior changes to the canonical instructions are also logged in `scaffolding/EVOLUTION-LOG.md` (which travels with each scaffolded repo).

## 2026-05-26 — Initial release

- Repo created at `~/Workspace/jokerman-session-setup/` on `main` branch.
- Scaffolding extracted from `claude-scaffolding` and adapted (refs updated to `jokerman-session-setup`).
- Multi-CLI shim architecture: canonical `AGENT-INSTRUCTIONS.md` + per-CLI shims under `shims/` for Claude Code, GitHub Copilot Enterprise, and Codex CLI.
- Install scripts for bash (`install/install.sh`) and PowerShell 7+ (`install/install.ps1`).
- `install/upstream-sources.yaml` declares 8 upstream sources across 3 tiers (permissive / restricted / reference-only):
  - **Permissive (MIT):** gstack, GSD Redux, AgentShield, ECC.
  - **Restricted:** Trail of Bits skills (CC-BY-SA-4.0), Anthropic skills (mixed Apache-2.0 + source-available).
  - **Reference-only:** Trail of Bits claude-code-config, Anthropic plugins-official.
- New scaffolding files added on top of the `claude-scaffolding` base: `tasks/memory.md`, `tasks/personas.md`, `docs/adr/README.md`, `docs/adr/TEMPLATE.md`, `docs/personas/EXAMPLE.md`.
- Documentation: `README.md`, `getting-started.md`, `multi-cli.md`, `compliance.md`, `promoted-agents.md`, `precedence.md`, `power-user.md`, `faq.md`.
- MIT license (with `LICENSE` note explaining that installed upstreams keep their own licenses).
- `.gitignore` excludes session data, secrets, customer-data-likely paths, and common dev artifacts.
