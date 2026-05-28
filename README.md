# jokerman-lintel (Lintel)

**MS-CAIP-SE session harness for agent-based development.** Markdown + bash scaffolding that any modern AI CLI loads as a plugin. No runtime, no daemons — your CLI handles execution.

**Status:** v3-dev (2026-05-27). See [CHANGELOG.md](CHANGELOG.md) for v3 release notes and [SHIP-GATE.md](SHIP-GATE.md) for v3.0.0 readiness gates. The v3 design lives at [docs/design/lintel-v3-plan.md](docs/design/lintel-v3-plan.md).

v3 ships **81 skills + 78 agents + 15 hooks** organized for plugin-manifest pattern across 8 CLIs. Plus full Kategori B scaffolding-template system (CORE-PRINCIPLES, EVOLUTION-LOG, tasks/lessons.md, ADR templates) that gets copied into new MS engagement repos via `bin/li-scaffold`.

Lintel is the **complete session harness** — not just a skill catalog. It manages the full lifecycle: session-start ritual → mid-session interventions (hooks, voice gates, compliance) → end-of-session capture (lessons, ADR drafting, EVOLUTION-LOG) → cross-session continuity (memory, lessons-sync). See [docs/session-harness.md](docs/session-harness.md) for the full mental model.

---

## What Lintel is

Two distinct categories, both shipped in this repo:

**Kategori A — Agent-invokable** (what your CLI sees via plugin manifest):
- `skills/` — 81 slash-commands (foundation + ms-team layers)
- `agents/` — 78 subagent roles organized per domain
- `hooks/shared/` — 15 compliance + workflow hooks

**Kategori B — Repo-scaffolding** (copied INTO other repos via `li-scaffold`):
- `scaffolding/01-foundation/` — CLAUDE.md template, CORE-PRINCIPLES, EVOLUTION/EVOLUTION-LOG, tasks/{lessons,memory,personas,todo}.md, docs/adr/ templates, .claude/agents/ subagent overrides
- `scaffolding/02-sdl/` — 5+7+8 compliance reference (HARD-RULES + ON-DEMAND + REFERENCE)
- `scaffolding/03-ms-team/` — voice corpus (60 paragraphs, 12 cells) + doc-gen default templates

The architecture: write skills/agents once at repo root, ship tiny per-CLI plugin manifests (`.claude-plugin/`, `.codex-plugin/`, `.cursor-plugin/`, `.opencode/`, `gemini-extension.json`, `.copilot-plugin/`, `.droid-plugin/`) that all point at the same `./skills/` and `./agents/` directories. Each CLI's native plugin marketplace handles discovery + invocation.

## Who this is for

Microsoft Sweden CAIP solution engineers. The compliance assumptions, auto-mode bounds, precedence model, and voice corpus are tuned to that team's constraints. If you're outside this team and want to fork: see [docs/compliance.md](docs/compliance.md).

---

## Multi-CLI support (v3 — honest table)

| CLI | Install mechanism | Skill/agent discovery | Status |
|---|---|---|---|
| Claude Code | `/plugin marketplace add jokerman89/jokerman-lintel` + `/plugin install lintel@jokerman-lintel` | native, namespaced `/li:<skill>` | ✓ full |
| Codex CLI / App | `/plugins` → search lintel → Install | native | ✓ full |
| Cursor | `/add-plugin lintel` | native (rules + agents) | ✓ full |
| Gemini CLI | `gemini extensions install https://github.com/jokerman89/jokerman-lintel` | context-file based (GEMINI.md) + skill references | ✓ supported |
| OpenCode | Fetch + follow `.opencode/INSTALL.md` instructions | manual install, agent reads SKILL.md | ✓ supported |
| GitHub Copilot CLI | `copilot plugin marketplace add` + `install` | native | ✓ supported (schema verified post-launch) |
| Factory Droid | `droid plugin marketplace add` + `install` | native | ✓ supported (schema verified post-launch) |
| Cline / Continue / Aider | Manual setup via custom instructions | degraded (no plugin discovery) | ~ best-effort |

See [docs/per-cli/](docs/per-cli/) for per-CLI install guides.

---

## Quick start

### 1. Clone Lintel

```bash
git clone https://github.com/jokerman89/jokerman-lintel ~/Workspace/jokerman-lintel
cd ~/Workspace/jokerman-lintel
```

### 2. Install for your CLI

```bash
# Claude Code:
#   /plugin marketplace add jokerman89/jokerman-lintel
#   /plugin install lintel@jokerman-lintel

# Codex CLI:
#   /plugins → search lintel → Install Plugin

# Cursor:
#   /add-plugin lintel

# Gemini CLI:
gemini extensions install https://github.com/jokerman89/jokerman-lintel

# Copilot CLI:
copilot plugin marketplace add jokerman89/jokerman-lintel
copilot plugin install lintel@jokerman-lintel
```

### 3. Install scaffolding source (for `li-scaffold` in new repos)

```bash
# Set up local cache for scaffolding templates + bin/ scripts
mkdir -p ~/.lintel
ln -s ~/Workspace/jokerman-lintel/scaffolding ~/.lintel/scaffolding
export PATH="$HOME/Workspace/jokerman-lintel/bin:$PATH"
```

### 4. Verify

```bash
li-doctor      # cross-CLI health check
bash install/verify.sh
```

### 5. Scaffold a new repo

```bash
cd ~/new-customer-engagement
li-scaffold init --engagement customer-engagement --voice trailblazer
```

That creates CLAUDE.md, CORE-PRINCIPLES.md, tasks/, docs/adr/, .claude/agents/ with sane MS defaults.

Full walkthrough: [docs/getting-started.md](docs/getting-started.md).

---

## What you get

- **81 skills** for daily workflows: `/qa`, `/release-ev2`, `/safe-deploy-ring`, `/investigate`, `/plan-eng-review`, `/office-hours`, `/rais-customer-voice-check`, `/onecs-check`, `/agt-tier-stamp`, `/generate-ppt`, `/generate-word`, `/generate-web`, `/scaffold-engagement-demo`, plus 7 new v3 session-harness skills (`/match`, `/li:doctor`, `/li:scaffold`, `/lessons-promote`, `/adr-new`, `/personas-rotate`, `/lessons`).
- **78 agents** organized per domain: ms-specific (15), engineering (25), security (8), compliance (6), devops (7), customer (8), communication (5), doc-gen (3), voice (1).
- **15 compliance hooks** (opt-in via symlinks): `customer-data-block`, `secret-scan-block`, `no-direct-main-push`, etc.
- **5+7+8 compliance tiering**: 5 always-on hard rules, 7 on-demand check items, 8 reference docs (RAIS, OneCS, AGT, SDL, etc).
- **OurVoice corpus**: 60 sanitized paragraphs across 12 cells (4 Reveal × 3 Inspire × 5 Provoke techniques) — operator-driven calibration via `T0-CALIBRATION-WORKFLOW.md`.
- **Repo scaffolding mechanism** via `bin/li-scaffold` — 30-second new-repo setup.
- **Cross-repo lessons sync** via `bin/li-lessons-sync` (operator-opt-in).
- **Cross-CLI health check** via `bin/li-doctor`.

---

## What you don't get

- **No customer data.** This repo is for tooling. Customer artifacts never land here.
- **No third-party code bundled.** v2 had install/upstream-sources.yaml for fetching upstream packs — v3 simplified, Lintel is now self-contained.
- **No runtime.** Lintel = markdown + bash. Your CLI executes — Lintel provides the patterns + scaffolding.
- **No production cross-CLI parity for everything.** Hooks are Claude-Code-only mechanism. Subagent abstractions differ per CLI. We're honest about gaps; see [docs/multi-cli.md](docs/multi-cli.md).

---

## License

MIT — see [LICENSE](LICENSE).

v3 ships **only operator-authored content** (no vendored upstream). Permissive license throughout. v1 license-tier mechanism preserved for any future upstream-derived agents.

---

## Compliance

See [docs/compliance.md](docs/compliance.md). Key rules (always-on):
1. No customer data in prompts, files, or commits
2. No secrets, credentials, tokens
3. Production mutations require explicit per-call authorization
4. MS SSO only; no personal accounts
5. First-party first (GHCP Enterprise, M365 Copilot, Azure OpenAI) preferred over OpenAI direct API

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). PR-based against `main`. v3 work happens on `v3-dev` branch.

Lessons learned go in `scaffolding/01-foundation/tasks/lessons.md`. Promote a lesson from a customer repo via `bin/li-lessons-promote`.

---

## Versioning

Semantic versioning since v3. v3.0.0 ships when [SHIP-GATE.md](SHIP-GATE.md) gates are all green.
Pre-v3 used date-based versioning — see [CHANGELOG.md](CHANGELOG.md).

---

## Security

See [SECURITY.md](SECURITY.md). Report security concerns to johannes.akerman@microsoft.com.
