# Getting started

Get Lintel running on your AI CLI in about five minutes. Lintel is a company-neutral, pack-driven
session harness — markdown and bash that your CLI loads as a plugin. There is no runtime and no
daemon; your CLI executes, Lintel supplies the disciplines.

> **This is v0.9.0-beta — the first public release.** The harness is dogfooded daily on its own
> repo, and its structure is covered by 90 tests (36 shape, 48 unit, 4 integration, 1 behavior,
> 1 end-to-end) on Ubuntu and Windows CI. Beta means the surface is tested but not frozen: skill names, pack fields,
> and file layouts can still change between releases, and each change that needs action from you
> gets an entry in [migrations](migrations/_INDEX.md). There is no uninstall script — a plugin
> install is removed through your CLI's plugin manager, a bare install by deleting `~/.lintel/`.

New here? Keep the **[glossary](GLOSSARY.md)** open — it defines pack, spine, the 9-step cycle, the
trio, and the rest of the load-bearing terms in one screen. **[docs/README.md](README.md)** is the
index to everything else.

What you get on install: **125 skills**, **69 agents** across 8 categories, **33 hooks** (9 of which
auto-register — see below), and **1 pack**, the neutral `_default`.

## Prerequisites

- **Git** — any recent version (`git --version`).
- **An AI CLI.** Lintel is **full** on Claude Code, Codex, and Cursor; **supported** on Gemini CLI,
  OpenCode, GitHub Copilot CLI, and Factory Droid; best-effort on Cline / Continue / Aider. The
  generated capability table is in the [README](../README.md); what degrades where, and why, is in
  [multi-cli.md](multi-cli.md). One important caveat: the **enforcement hooks fire only on Claude
  Code** — every other CLI gets the skills, the cycle discipline, and the pack-driven knowledge,
  just not the live hook gate.
- **Bash** (Linux/macOS/WSL/Git Bash) or **PowerShell 7+** — only needed if you want the scaffolding
  factory (`bin/li-scaffold`) or to run the bare installer and tests locally. On **Windows**, run
  `install\install.ps1` in PowerShell 7+; the bash installer is `install/install.sh`. A plugin
  install needs neither.

The installer copies files out of this repo into `~/.lintel/` and does nothing else. It does not
clone, vendor, or update third-party tools, and it never writes to your `~/.claude/settings.json`.

## 1. Install for your CLI

Lintel ships as a plugin per CLI, all pointing at the same `skills/` and `agents/`. Pick yours:

```bash
# Claude Code
#   /plugin marketplace add jokerman89/lintel
#   /plugin install li@jokerman-lintel

# Codex CLI / App
#   /plugins  →  search lintel  →  Install

# Cursor
#   /add-plugin lintel

# Gemini CLI
gemini extensions install https://github.com/jokerman89/lintel

# GitHub Copilot CLI
copilot plugin marketplace add jokerman89/lintel
copilot plugin install li@jokerman-lintel

# Factory Droid
droid plugin marketplace add jokerman89/lintel
droid plugin install li@jokerman-lintel

# OpenCode
#   fetch and follow .opencode/INSTALL.md
```

These commands come from `lib/cli-tiers.yaml`, the single source for per-CLI truth. The README's
capability table is generated from the same file, and a shape test fails the build if the two
disagree.

## 2. See it work — `/li:welcome`

In your CLI, run:

```
/li:welcome
```

It detects your CLI, shows that CLI's **honest** capability tier (what works and what does not here),
runs one cycle in **dry-run** so you see the 9-step discipline without mutating anything, and
demonstrates a safety hook — or explains why it cannot fire on your CLI. This is the fastest way to
understand what Lintel does for you. Run it first.

## How hook activation works

> This is the **canonical** explanation. The README, `/li:welcome`, and `install/install.sh` all
> point here — if you read it elsewhere and it disagrees, this section wins. The decision behind it
> is ADR-0008, in `.claude/decisions/`.

Hooks are the enforcement layer: a secret scan and a customer-data scan that **block** at `git
commit` and `git push`, a warning on direct pushes to `main`, the session digest, and the cycle
position footer. They are a **Claude-Code-only** mechanism — no other CLI runs them. *How* they turn
on depends on how you installed Lintel:

| Install path | Hook activation | What you do |
|---|---|---|
| **Plugin install** (`/plugin install li@jokerman-lintel`) | **Auto-registered, zero-setup** | Nothing. The plugin ships `hooks/hooks.json`; Claude Code registers it on install. |
| **Bare / non-plugin install** (clone + `install/install.sh`) | **Manual (opt-in)** | Symlink the hooks you want into `~/.claude/hooks/` and merge the settings snippet into `~/.claude/settings.json`. `/li:welcome` prints the exact lines. |

A plugin install registers **nine hooks across five events** (`SessionStart`, `PreToolUse`,
`PostToolUse`, `Stop`, `UserPromptSubmit`) with no setup: `session-digest`, `no-secrets-in-edit`,
`secret-scan-block`, `customer-data-block`, `no-direct-main-push`, `memory-budget-warn`,
`cycle-incomplete-warn`, `cycle-position-inject`, and `no-customer-data-in-message`. The repo carries
33 hook directories in total (`hooks/shared/<name>/{HOOK.md,run.sh}`); the rest stay opt-in.

On a bare install (bare install only) the hooks ship inert until you arm them — Lintel never edits
your `settings.json` behind your back. On every CLI except Claude Code, hooks do not fire at all, by
design; you still get the skills, the cycle discipline, and the pack-driven knowledge.

A block is overridable, but never silently: every override is written to the
audit log under `~/.lintel/audit/`.

## Where things live

Four roots matter — three that Lintel writes to, plus your CLI's own home, which it reads but
never edits on its own. Knowing which is which is the whole mental model for "where did my state
go":

| Root | Scope | Holds |
|---|---|---|
| `~/.lintel/` | machine-global | operator identity and cross-repo state — `profile.yaml` (active pack, mode, role), the packs, the cross-repo jobs registry, the audit log, and the scaffolding source |
| `~/.claude/` | machine-global | Claude Code's own home — your `settings.json`, plus any hooks you symlinked in on a bare install |
| `<repo>/.claude/` | per-repo, **committed** | the knowledge that should travel with the code — `memory/lessons.md`, `memory/working-state.md`, `memory/personas.md`, `decisions/` (ADRs), `plans/todo.md` |
| `<repo>/.claude/runtime/` | per-repo, **gitignored** | the churn that should not — cycle state (`runtime/state/00-state.md`), job data, session saves, the repo event log |

The committed/gitignored split (ADR-0005) is deliberate: knowledge is reviewed in pull requests,
runtime noise stays local. [architecture.md](architecture.md) has the full state map;
[GLOSSARY.md](GLOSSARY.md) has the terms.

## 3. Run a real cycle

When you have a real task, run the full development cycle:

```
/li:cycle "add a rate limiter to the login endpoint"
```

This is **the 9-step cycle: 8 core phases + SCOPE** — SENSE → SCOPE → DEFINE → DISCOVER → PLAN →
BUILD → REVIEW → SHIP → CAPTURE, with gates (a cost estimate before BUILD, an approval pause at the
end of PLAN, adversarial review before SHIP). For a fix whose diagnosis is already done, use
`/li:fix`; to plan only, `/li:plan`. Each phase — what it produces, where its gate sits, what
skipping it costs — is in [the-cycle.md](the-cycle.md).

## Finding skills

125 skills is more than anyone browses. Two ways in:

- **`/li:help`** — lists installed skills, agents, and hooks; filter by category, voice tier, or CLI.
- **`/li:catalog`** — the generated catalog, also readable as [skills/CATALOG.md](../skills/CATALOG.md).

A rough mental map by purpose, so you know what to reach for:

- **cycle phases** — `/li:cycle` plus the per-phase skills (`/li:sense`, `/li:scope`, `/li:define`, `/li:discover`, `/li:plan`, `/li:build`, `/li:review`, `/li:ship`, `/li:capture`); shortcuts `/li:fix`, `/li:jobs`, `/li:resume`.
- **engineering modules** — depth on one domain: `/li:ta` (architecture), `/li:da` (data), `/li:sc` (security), `/li:dh` (devops and hosting), `/li:tq` (testing and quality).
- **context** — manage the session window: `/li:context-warm`, `/li:context-save`, `/li:context-restore`, `/li:context-budget`.
- **document generation** — produce artifacts: `/li:generate-ppt`, `/li:generate-word`, `/li:generate-web`, `/li:document-generate`.
- **frontend** — design work: `/li:frontend-design`, `/li:design-review`, `/li:generate-app`.
- **pack and identity** — who the harness is being right now: `/li:pack-list`, `/li:pack-switch`, `/li:pack-create`, `/li:role`.
- **meta** — the harness on itself: `/li:doctor`, `/li:welcome`, `/li:scaffold`, `/li:adr-new`, `/li:learn`, `/li:catalog`.

The 69 agents are dispatched by name from inside skills rather than invoked directly. They span 8
categories: engineering (33), security (9), customer (7), devops (5), frontend (5), communication
(4), compliance (3), document generation (3).

## 4. Make it yours — packs

Identity — voice, compliance mode, personas, brand, roles, navigation policy — is **not** hardcoded.
It resolves at runtime from the active **pack** through a single accessor. Lintel ships exactly one
pack, the neutral `_default`, which enforces nothing.

```
/li:pack-list             # what packs are available
/li:pack-switch <name>    # switch identity and compliance for this repo
/li:pack-create           # encode your own rules as a pack
```

The active pack is recorded in `~/.lintel/profile.yaml`, so you can run a stricter pack at work and
the neutral default on personal projects. Company identity installs as a separate external pack; it
is deliberately not part of the neutral spine. [compliance.md](compliance.md) covers the neutral
baseline and what a pack may add on top.

## 5. (Optional) Install the disciplines into another repo

Lintel is also a **factory**. `bin/li-scaffold` reads its templates from
`~/.lintel/scaffolding/01-foundation/`, so run the bare installer once first — that is what
populates it:

```bash
git clone https://github.com/jokerman89/lintel && cd lintel
bash install/install.sh          # Windows: pwsh install\install.ps1
export PATH="$PWD/bin:$PATH"

cd ~/your-other-repo
li-scaffold check                # what exists and what would be created
li-scaffold init --mode internal-tool --pack _default
```

`init` creates exactly this, and skips any file that already exists — it never clobbers:

- `CLAUDE.md`, rendered from the template with your repo name, pack, mode, and voice tier
- `AGENTS.md`, a short pointer file so AGENTS.md-aware CLIs find the same instructions
- `CORE-PRINCIPLES.md`, `EVOLUTION.md`, `EVOLUTION-LOG.md`, `TEMPLATE-skill.md`, `TEMPLATE-agent.md`
- `.claude/memory/` — `lessons.md`, `working-state.md`, `personas.md`, `personas-example.md`, and a seeded `MEMORY.md` index
- `.claude/plans/todo.md`
- `.claude/decisions/` — `README.md` and `TEMPLATE.md`
- `.claude/rules/README.md` — the path-scoped rules convention
- `.claude/SUBAGENT-GUIDE.md`
- `.claude/lintel-layout.yaml` (the layout marker) and a `.gitignore` entry for `.claude/runtime/`

**No `.claude/agents/` is scaffolded.** The 69-agent fleet ships with the plugin, and a repo-local
agent would shadow the fleet's same-named one — so scaffolding deliberately creates none. Add one
only for a genuinely project-specific agent.

Two lesson tools exist and are not interchangeable: `bin/li-lessons-promote` promotes a lesson from
one repo into the scaffolding baseline, so every repo scaffolded afterwards inherits it;
`bin/li-lessons-sync` syncs your own lessons across the repos you already work in.

## 6. Health check

```bash
li-doctor                    # which CLIs are installed, Lintel install state, drift
bash install/verify.sh --all # bare-install verification with an aggregate verdict
```

## Where to next

- **[docs/README.md](README.md)** — the documentation index; start here for anything not covered above.
- **[architecture.md](architecture.md)** — spine and pack, the mechanical layer, where state lives.
- **[the-cycle.md](the-cycle.md)** — the nine phases in depth.
- **[multi-cli.md](multi-cli.md)** — how one source ships to eight CLIs, and where each degrades.
- **[power-user.md](power-user.md)** — context warming, roles, jobs, budgets, checkpoints.
- **[faq.md](faq.md)** and **[precedence.md](precedence.md)** — short answers, and which instruction wins when two disagree.
- **[CHANGELOG.md](../CHANGELOG.md)** — release notes.

## Troubleshooting

- **`/li:<skill>` not found** — confirm the plugin installed for your CLI (`li-doctor`). Native
  slash-command invocation works on Claude Code, Codex, Cursor, GitHub Copilot CLI, and Factory
  Droid. Gemini CLI, OpenCode, and best-effort CLIs have no native invocation: open the skill's
  `SKILL.md` and follow it, or point the CLI at `AGENT-INSTRUCTIONS.md` as custom instructions.
- **Hooks do not fire** — see [How hook activation works](#how-hook-activation-works) above. Short
  version: a **plugin install auto-registers** them (zero setup); a **bare install** needs a manual
  symlink plus a settings merge. Either way, hooks are a Claude-Code-only mechanism.
- **`li-scaffold` reports the scaffolding source is not found** — it reads
  `~/.lintel/scaffolding/01-foundation/`, which the bare installer creates. Run
  `bash install/install.sh`, or set `LINTEL_HOME`, before scaffolding.
- **Installer issues** — `li-doctor --verbose` reports per-CLI state; re-running the install is safe,
  and it backs up an existing `~/.lintel/` before writing.
