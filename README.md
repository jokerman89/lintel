# lintel (Lintel)

**Company-neutral, pack-driven session harness for agent-based development.** Markdown + bash scaffolding that any modern AI CLI loads as a plugin. No runtime, no daemons — your CLI handles execution. Identity (voice, compliance, personas, brand) is supplied by an installable **pack**; the harness ships only the neutral `_default` pack.

**Status:** v5.3 — company-neutral, pack-driven harness with the `.claude/` home layout (ADR-0005), mechanical memory (ADR-0006), zero-setup hook activation (plugin install) (ADR-0008 — bare installs arm hooks manually; see [How hook activation works](docs/getting-started.md#how-hook-activation-works)) and trigger-form prompt craft (ADR-0014). The Microsoft CAIP-SE identity has been extracted to the separate [lintel-caip-pack](https://github.com/jokerman89/lintel-caip-pack); Lintel ships only the neutral `_default` pack. See [CHANGELOG.md](CHANGELOG.md) for release notes and [SHIP-GATE.md](SHIP-GATE.md) for readiness gates. New to Lintel? Start with the **[glossary](docs/GLOSSARY.md)** and [getting-started](docs/getting-started.md). Current architecture lives at [docs/design/lintel-v4.0-reframe-design.md](docs/design/lintel-v4.0-reframe-design.md).

Lintel ships **124 skills + 69 agents + 1 pack (`_default`)** organized for the plugin-manifest pattern across 8 CLIs. Plus the foundation scaffolding-template system (CORE-PRINCIPLES, EVOLUTION-LOG, .claude/memory/lessons.md, decision-record templates) that gets copied into new repos via `bin/li-scaffold`. The engineering-domain modules (`/li:ta`, `/li:da`, `/li:sc`, `/li:dh`, `/li:tq`) plus the 9-step cycle (8 core phases + SCOPE) are the core.

Lintel is the **complete session harness** — not just a skill catalog. It manages the full lifecycle: session-start ritual → mid-session interventions (hooks, voice gates, compliance) → end-of-session capture (lessons, ADR drafting, EVOLUTION-LOG) → cross-session continuity (memory, lessons-sync). See [docs/session-harness.md](docs/session-harness.md) for the full mental model.

---

## What Lintel is

Two distinct categories, both shipped in this repo:

**Category A — Agent-invokable** (what your CLI sees via plugin manifest):
- `skills/` — slash-commands (9-step cycle + engineering modules + session-harness)
- `agents/` — subagent roles organized per domain
- `hooks/shared/` — compliance + workflow hooks

**Category B — Repo-scaffolding** (copied INTO other repos via `li-scaffold`):
- `scaffolding/01-foundation/` — CLAUDE.md template, CORE-PRINCIPLES, EVOLUTION/EVOLUTION-LOG, .claude/memory/{lessons,working-state,personas}.md, .claude/plans/todo.md, .claude/decisions/ templates, .claude/agents/ subagent overrides

Company-specific scaffolding (compliance reference, voice corpus, doc-gen templates) is supplied by an installable pack — Lintel ships only the neutral `_default` pack. See the [lintel-caip-pack](https://github.com/jokerman89/lintel-caip-pack) example for the Microsoft CAIP-SE identity.

The architecture: write skills/agents once at repo root, ship tiny per-CLI plugin manifests (`.claude-plugin/`, `.codex-plugin/`, `.cursor-plugin/`, `.opencode/`, `gemini-extension.json`) that all point at the same `./skills/` and `./agents/` directories. Copilot CLI and Factory Droid read the `.claude-plugin/` manifest directly via Claude-plugin interop — no separate manifest needed. Each CLI's native plugin marketplace handles discovery + invocation; AGENTS.md carries the instructions to every CLI natively.

## Who this is for

Anyone running an AI CLI who wants a disciplined session harness. The harness itself is company-neutral; team-specific compliance, voice, personas, and brand load from an installable pack. The Microsoft CAIP-SE identity (Trailblazer voice, RAIS/OneCS/AGT/SDL compliance, EV2/OneBranch) ships as the separate [lintel-caip-pack](https://github.com/jokerman89/lintel-caip-pack); build your own pack with `/li:pack-create`.

---

## Multi-CLI support (honest table)

Full on Claude Code, Codex, and Cursor; supported on four more; best-effort elsewhere. The
**enforcement hooks fire only on Claude Code** — every other CLI still gets the skills, the
9-step cycle discipline, and the pack-driven knowledge, just not the live hook gate. This
table is generated from `lib/cli-tiers.yaml` (the single source); `/li:welcome` reads the same
file to tell you, on first run, exactly what works on *your* CLI. See [docs/per-cli/](docs/per-cli/)
for per-CLI install guides.

<!-- CLI-TIERS:START — generated from lib/cli-tiers.yaml via cli_tiers_markdown_table; do not hand-edit. -->
| CLI | Tier | Skills | Subagents | Hooks |
|---|---|---|---|---|
| Claude Code | full | native | native | yes |
| Codex CLI / App | full | native | native | no (Claude Code only) |
| Cursor | supported | native | sequenced | no (Claude Code only) |
| Gemini CLI | supported | manual | none | no (Claude Code only) |
| OpenCode | supported | manual | none | no (Claude Code only) |
| GitHub Copilot CLI | supported | native | none | no (Claude Code only) |
| Factory Droid | supported | native | none | no (Claude Code only) |
| Cline / Continue / Aider | best-effort | manual | none | no (Claude Code only) |
<!-- CLI-TIERS:END -->

---

## Quick start

### 1. Clone Lintel

```bash
git clone https://github.com/jokerman89/lintel ~/Workspace/lintel
cd ~/Workspace/lintel
```

### 2. Install for your CLI

```bash
# Claude Code:
#   /plugin marketplace add jokerman89/lintel
#   /plugin install li@jokerman-lintel

# Codex CLI:
#   /plugins → search lintel → Install Plugin

# Cursor:
#   /add-plugin lintel

# Gemini CLI:
gemini extensions install https://github.com/jokerman89/lintel

# Copilot CLI:
copilot plugin marketplace add jokerman89/lintel
copilot plugin install li@jokerman-lintel
```

**Then run `/li:welcome`** in your CLI — it detects your CLI, shows your honest capability tier
(what works and what doesn't here), runs a dry-run cycle so you feel the 9-step discipline
without mutating anything, and demonstrates a safety hook. The fastest way to see the harness work.

### 3. Install scaffolding source (for `li-scaffold` in new repos)

```bash
# Set up local cache for scaffolding templates + bin/ scripts (run from your clone root)
mkdir -p ~/.lintel
ln -s "$PWD/scaffolding" ~/.lintel/scaffolding
export PATH="$PWD/bin:$PATH"
```

### 4. Verify

```bash
li-doctor      # cross-CLI health check
bash install/verify.sh
```

**Windows:** the bare installer is `install\install.ps1` (run it in PowerShell 7+) — `install/install.sh`
is the bash/Linux/macOS/WSL/Git Bash path. A plugin install needs neither.

### 5. Scaffold a new repo

```bash
cd ~/new-repo
li-scaffold init --mode internal-tool --pack _default
```

That creates CLAUDE.md, CORE-PRINCIPLES.md, and .claude/ (memory, plans, decisions, agents) with neutral defaults. Activate a company pack (e.g. `caip-se`) for team-specific voice/compliance.

Full walkthrough: [docs/getting-started.md](docs/getting-started.md).

---

## What you get

- **Skills** for daily workflows: the 9-step `/li:cycle` (sense→capture), engineering-domain modules (`/li:ta`, `/li:da`, `/li:sc`, `/li:dh`, `/li:tq`), `/qa`, `/investigate`, `/plan-eng-review`, `/office-hours`, `/generate-ppt`, `/generate-word`, `/generate-web`, plus session-harness skills (`/skill-router`, `/li:doctor`, `/li:scaffold`, `/lessons-promote`, `/adr-new`, `/personas-rotate`, `/pack-create`, `/pack-switch`).
- **Agents** organized per domain: engineering, security, compliance (generic frameworks — GDPR/SOC2/EU-AI-Act), devops, customer, communication, doc-gen, frontend. Company-specific agents load from a pack.
- **Compliance hooks** — `customer-data-block`, `secret-scan-block`, `no-direct-main-push`, etc. Auto-registered on a plugin install; armed manually on a bare install. See [How hook activation works](docs/getting-started.md#how-hook-activation-works).
- **Pack-driven compliance + voice**: the active pack declares its compliance gates and voice tier; the neutral `_default` pack enforces nothing. Company packs (e.g. lintel-caip-pack) supply tiered compliance and a calibrated voice corpus.
- **Repo scaffolding mechanism** via `bin/li-scaffold` — 30-second new-repo setup.
- **Cross-repo lessons sync** via `bin/li-lessons-sync` (operator-opt-in).
- **Cross-CLI health check** via `bin/li-doctor`.

---

## Where things live

Lintel writes to **four roots** — two machine-global, two in your repo:

| Root | Scope | Holds |
|---|---|---|
| `~/.lintel/` | machine-global | operator identity + cross-repo state — `profile.yaml` (active pack/mode/role), packs, cross-repo jobs registry, audit log |
| `~/.claude/` | machine-global | Claude Code's own home — your `settings.json` and any hooks you symlinked in (bare install) |
| `<repo>/.claude/` | per-repo, **committed** | knowledge that travels with the code — `memory/` (lessons, working-state, personas), `decisions/` (ADRs), `plans/` |
| `<repo>/.claude/runtime/` | per-repo, **gitignored** | churn that shouldn't — cycle state, job data, session saves, repo event log |

The committed/gitignored split is deliberate (ADR-0005): knowledge is shared in PRs, runtime noise
stays local. Full map + lifecycle in [CLAUDE.md](CLAUDE.md#where-state-lives-the-memory-map).

---

## What you don't get

- **No customer data.** This repo is for tooling. Customer artifacts never land here.
- **No third-party code bundled.** v2 had install/upstream-sources.yaml for fetching upstream packs — v3 simplified, Lintel is now self-contained.
- **No runtime.** Lintel = markdown + bash. Your CLI executes — Lintel provides the patterns + scaffolding.
- **No production cross-CLI parity for everything.** Hooks are Claude-Code-only mechanism. Subagent abstractions differ per CLI. We're honest about gaps; see [docs/multi-cli.md](docs/multi-cli.md).

---

## License

MIT — see [LICENSE](LICENSE).

Lintel ships **only operator-authored content** (no vendored upstream). Permissive license throughout. The license-tier mechanism is preserved for any future upstream-derived agents.

---

## Compliance

See [docs/compliance.md](docs/compliance.md). Key rules (always-on):
1. No customer data in prompts, files, or commits
2. No secrets, credentials, tokens
3. Production mutations require explicit per-call authorization

Beyond these neutral baselines, tiered compliance (SSO policy, vendor preference, regulatory gates) is supplied by the active pack — see the lintel-caip-pack example for the Microsoft CAIP-SE ruleset.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). PR-based against `main`.

Lessons learned go in `scaffolding/01-foundation/.claude/memory/lessons.md`. Promote a lesson from a customer repo via `bin/li-lessons-promote`.

---

## Versioning

Semantic versioning since v3; the current line is v5.3. Releases ship when [SHIP-GATE.md](SHIP-GATE.md) gates are all green.
Pre-v3 used date-based versioning — see [CHANGELOG.md](CHANGELOG.md).

---

## Security

See [SECURITY.md](SECURITY.md). Report security concerns to johannes.akerman@gmail.com.
