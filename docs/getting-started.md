# Getting started

Get Lintel running on your AI CLI in about five minutes. Lintel is a company-neutral,
pack-driven session harness — markdown + bash that your CLI loads as a plugin. There is no
runtime and no daemon; your CLI executes, Lintel supplies the disciplines.

New here? Keep the **[glossary](GLOSSARY.md)** open — it defines pack, spine, the 9-step cycle, the
trio, and the rest of the load-bearing terms in one screen.

## Prerequisites

- **Git** — any recent version (`git --version`).
- **An AI CLI.** Lintel is **full** on Claude Code, Codex, and Cursor; **supported** on Gemini CLI,
  OpenCode, GitHub Copilot CLI, and Factory Droid; best-effort elsewhere. See the capability table in
  the [README](../README.md#multi-cli-support-honest-table). One important caveat: the **enforcement
  hooks fire only on Claude Code** — every other CLI gets the skills, the cycle discipline, and the
  pack-driven knowledge, just not the live hook gate.
- **Bash** (Linux/macOS/WSL/Git Bash) or **PowerShell 7+** — only needed if you want the scaffolding
  factory (`bin/li-scaffold`) or to run the bare installer/tests locally. On **Windows**, run
  `install\install.ps1` in PowerShell 7+ (the bash installer is `install/install.sh`); a plugin
  install needs neither.

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

Per-CLI install guides: [docs/per-cli/](per-cli/).

## 2. See it work — `/li:welcome`

In your CLI, run:

```
/li:welcome
```

It detects your CLI, shows your **honest** capability tier (what works and what doesn't here),
runs one cycle in **dry-run** so you see the 9-step discipline without mutating anything, and
demonstrates a safety hook (or honestly explains why it can't fire on your CLI). This is the fastest
way to understand what Lintel does for you. Run it first.

## How hook activation works

> This is the **canonical** explanation. README, `/li:welcome`, and the installer all point here —
> if you read it elsewhere and it disagrees, this section wins. The truth per [ADR-0008](../.claude/decisions/0008-activation-contract.md).

Hooks are the enforcement layer (secret-scan + customer-data blocks, no-direct-push, the session
digest). They are a **Claude-Code-only** mechanism — no other CLI runs them. *How* they turn on
depends on how you installed Lintel:

| Install path | Hook activation | What you do |
|---|---|---|
| **Plugin install** (`/plugin install li@jokerman-lintel`) | **Auto-registered, zero-setup** | Nothing. The plugin ships `hooks/hooks.json`; Claude Code registers it on install. |
| **Bare / non-plugin install** (clone + `install/install.sh`) | **Manual (opt-in)** | Symlink the hooks you want into `~/.claude/hooks/` and merge the settings snippet into `~/.claude/settings.json`. `/li:welcome` prints the exact lines. |

So: a plugin install gives you the safety hooks with no setup. On a bare install (bare install only)
the hooks ship inert until you arm them — Lintel never edits your `settings.json` behind your back. On every CLI except
Claude Code, hooks don't fire at all, by design — you still get the skills, the cycle discipline, and
the pack-driven knowledge.

## Where things live

Lintel writes to **four roots** — two machine-global, two in your repo. Knowing which is which is the
whole mental model for "where did my state go":

| Root | Scope | Holds |
|---|---|---|
| `~/.lintel/` | machine-global | operator identity + cross-repo state — `profile.yaml` (active pack/mode/role), the packs, the cross-repo jobs registry, audit log |
| `~/.claude/` | machine-global | Claude Code's own home — your `settings.json`, any hooks you symlinked in (bare install) |
| `<repo>/.claude/` | per-repo, **committed** | the knowledge that should travel with the code — `memory/` (lessons, working-state, personas), `decisions/` (ADRs), `plans/` |
| `<repo>/.claude/runtime/` | per-repo, **gitignored** | the churn that should not — cycle state, job data, session saves, the repo event log |

The committed/gitignored split (ADR-0005) is deliberate: knowledge is shared in PRs, runtime noise
stays local. See the [glossary](GLOSSARY.md) for the terms.

## 3. Run a real cycle

When you have a real task, run the full development cycle:

```
/li:cycle "add a rate limiter to the login endpoint"
```

This is **the 9-step cycle: 8 core phases + SCOPE** — it walks SENSE → SCOPE → DEFINE → DISCOVER →
PLAN → BUILD → REVIEW → SHIP → CAPTURE, with gates (cost estimate before BUILD, a founder-approval
pause at the end of PLAN, adversarial review before SHIP). For a quick fix, `/li:fix`; to just plan,
`/li:plan`.

## Finding skills

Lintel ships a large skill set (run `/li:help` to count yours, or `find skills -name SKILL.md | wc -l`).
Two ways in:

- **`/li:help`** — lists installed skills + agents + hooks; filter by category, voice tier, or CLI.
- **`/li:catalog`** — the full generated catalog.

A rough mental map by purpose so you know what to reach for:

- **cycle phases** — `/li:cycle` and the per-phase skills (`/li:sense`, `/li:scope`, `/li:define`, `/li:discover`, `/li:plan`, `/li:build`, `/li:review`, `/li:ship`, `/li:capture`); plus shortcuts `/li:fix`, `/li:jobs`, `/li:resume`.
- **engineering modules** — depth on a domain: `/li:ta` (architecture), `/li:da` (data), `/li:sc` (security), `/li:dh` (devops/hosting), `/li:tq` (testing/quality).
- **context** — manage the session window: `/li:context-warm`, `/li:context-save`, `/li:context-restore`, `/li:context-budget`.
- **doc-gen** — produce artifacts: `/li:generate-ppt`, `/li:generate-word`, `/li:generate-web`, `/li:document-generate`.
- **frontend** — design work: `/li:frontend-design`, `/li:design-review`, `/li:generate-app`.
- **pack / identity** — who the harness is being right now: `/li:pack-list`, `/li:pack-switch`, `/li:pack-create`, `/li:role-activate`.
- **meta** — the harness on itself: `/li:doctor`, `/li:welcome`, `/li:scaffold`, `/li:adr-new`, `/li:learn`, `/li:catalog`.

## 4. Make it yours — packs

Identity (voice, compliance mode, persona, brand, rules) is **not** hardcoded — it comes from the
active **pack**. The repo ships only the neutral `_default` pack, which enforces nothing.

```
/li:pack-list             # what packs are available
/li:pack-switch <name>    # switch identity/compliance for this repo
/li:pack-create           # encode your org's rules as a pack
```

Switch profiles per repo — a stricter pack at work, the neutral default for personal projects.
Company identity (for example Microsoft CAIP-SE) installs as a separate external pack, not part of
the neutral spine.

## 5. (Optional) Install the disciplines into other repos

Lintel is also a **factory**. From your clone, put `bin/` on PATH and scaffold any repo:

```bash
export PATH="$PWD/bin:$PATH"
cd ~/your-other-repo
li-scaffold init --mode internal-tool --pack _default
```

That drops a `CLAUDE.md`, `CORE-PRINCIPLES.md`, `.claude/memory/` (lessons/working-state/personas),
`.claude/plans/todo.md`, `.claude/decisions/`, and baseline subagents into the repo — a disciplined AI
workspace in about thirty seconds. It never clobbers existing files.

## 6. Health check

```bash
li-doctor          # cross-CLI: which CLIs are installed, Lintel install state, version drift
bash install/verify.sh --all
```

## Where to next

- **[docs/lintel-state-of-the-harness.md](lintel-state-of-the-harness.md)** — the full architecture +
  what every part does.
- **[docs/multi-cli.md](multi-cli.md)** — how one source ships to eight CLIs, and where each degrades.
- **`/li:catalog`** — the full skill catalog.
- **[CHANGELOG.md](../CHANGELOG.md)** — release notes.

## Troubleshooting

- **`/li:<skill>` not found** — confirm the plugin installed for your CLI (`li-doctor`), and that your
  CLI supports native skill invocation (full on Claude Code / Codex / Cursor; manual on others).
- **Hooks don't fire** — see [How hook activation works](#how-hook-activation-works) above. The short
  version: a **plugin install auto-registers** them (zero-setup); a **bare install** needs a manual
  symlink + settings merge. Either way, hooks are a Claude-Code-only mechanism — on other CLIs they
  don't fire at all, by design.
- **Installer issues** — `li-doctor --verbose` reports per-CLI state; re-running the install is safe
  (idempotent).
