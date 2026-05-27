# jokerman-session-setup (JStack)

Session bootstrap scaffolding for agent-based development. Used by Microsoft Sweden CAIP SEs to get a consistent, multi-CLI agent setup running in minutes.

**Status:** v2 spec-complete (2026-05-27). See [CHANGELOG.md](CHANGELOG.md) for the v2 release notes and [SHIP-GATE.md](SHIP-GATE.md) for the v2.0.0 readiness gates. v2 ships 74 skills + 44 agents + 15 hooks + new MS-naming + portability shim spec + 1M context engine spec + MS-proprietary doc-gen (PPT/Word/Web) + 4-gate quality pipeline for customer-bound output. JStack is **scaffolding-only** — markdown skills/agents/hooks/content + bash scripts. No separate runtime; Claude Code (or other agent CLI) reads SKILL.md and does the work.

For the v2 design + eng-review report, see [docs/design/jstack-v2-design.md](docs/design/jstack-v2-design.md).

## What this is

A shared scaffolding repo. Two pieces:

1. **Canonical session instructions** (`AGENT-INSTRUCTIONS.md`) — one file describing how an agent should behave during a session. Each CLI gets a small shim that points here.
2. **Install script** that fetches upstream agent-tooling (gstack, GSD, AgentShield, Trail of Bits, Anthropic, ECC) directly from their official repos. We do not bundle anyone else's code.

It is intentionally minimal. The scaffolding is what we agree on as a team. The agents and skills come from upstream.

## Who this is for

Microsoft Sweden CAIP solution engineers. The compliance assumptions, the auto-mode bounds, and the precedence model are tuned to that team's constraints. If you are outside this team and want to fork: see [docs/compliance.md](docs/compliance.md) for what you would need to change.

## Multi-CLI support

Works with any agent CLI that reads a known instructions file. Out of the box:

- **Claude Code** — reads [shims/CLAUDE.md](shims/CLAUDE.md), which points at `AGENT-INSTRUCTIONS.md`
- **GitHub Copilot Enterprise** (with Opus model picker) — reads `.github/copilot-instructions.md`, which points at `AGENT-INSTRUCTIONS.md`
- **Codex CLI** — reads `AGENTS.md`, which points at `AGENT-INSTRUCTIONS.md`
- **Anything else** — add a shim under `shims/` and write the per-CLI symlink/copy step in your repo

See [docs/multi-cli.md](docs/multi-cli.md) for the model.

## Quick start

```bash
# 1. Clone this repo
git clone <internal-MS-git-url>/jokerman-session-setup ~/Workspace/jokerman-session-setup
cd ~/Workspace/jokerman-session-setup

# 2. Run the installer (bash / Linux / macOS / WSL / Git Bash)
bash install/install.sh

# 2 alt. (Windows PowerShell 7+)
pwsh install/install.ps1

# 3. Verify
bash install/verify.sh
```

Then for each repo where you want the setup:

```bash
cd <your-repo>

# Claude Code:    nothing extra — symlinks done by installer
# GitHub Copilot: cp ~/Workspace/jokerman-session-setup/shims/copilot-instructions.md .github/
# Codex:          cp ~/Workspace/jokerman-session-setup/shims/AGENTS.md .
```

Full walkthrough: [docs/getting-started.md](docs/getting-started.md).

## What you get

- A short, consistent session-start ritual (personas → compliance → memory → ADR scan → agent precedence).
- A scaffolding template (`scaffolding/`) you copy into new repos: `CORE-PRINCIPLES.md`, `EVOLUTION.md`, `EVOLUTION-LOG.md`, `tasks/{lessons,memory,personas,todo}.md`, `docs/adr/`, `.claude/agents/`.
- Curated install of 8 upstream skill/agent packs — see [install/upstream-sources.yaml](install/upstream-sources.yaml).
- Documentation for the parts that are not obvious: precedence, promoted agents, power-user patterns, compliance.

## What you don't get

- **No customer data.** This repo is for tooling scaffolding. Customer artifacts never land here. See [docs/compliance.md](docs/compliance.md).
- **No third-party code.** Upstream tools are referenced + installed from their official repos. We do not vendor them.
- **No deployment glue.** This is a development-time setup, not a runtime.

## License

MIT — see [LICENSE](LICENSE). Note that some installed upstream sources have non-MIT licenses (CC-BY-SA-4.0 for Trail of Bits, mixed for parts of Anthropic skills). The installer prints license notes when those are installed. See [docs/promoted-agents.md](docs/promoted-agents.md) for full per-source detail.

## Compliance

This setup respects Microsoft's internal guardrails for AI-assisted development. See [docs/compliance.md](docs/compliance.md) for the rule set and the 5-step session-start check. If you are using this setup with anything customer-adjacent, read that doc first.

## Contributing

PR-based against `main`. Reviewers: anyone on the CAIP SE team listed in `CODEOWNERS` (TBD when published). Lessons learned go in `scaffolding/tasks/lessons.md`. Changes that affect the canonical instructions are logged in `scaffolding/EVOLUTION-LOG.md`.

## Versioning

This repo follows date-based releases. Each release tagged `vYYYY.MM.DD-N` where N is the iteration that day. Changes are tracked in [CHANGELOG.md](CHANGELOG.md).
