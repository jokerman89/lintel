# Getting started

Get Lintel running on your AI CLI in about five minutes. Lintel is a company-neutral,
pack-driven session harness — markdown + bash that your CLI loads as a plugin. There is no
runtime and no daemon; your CLI executes, Lintel supplies the disciplines.

## Prerequisites

- **Git** — any recent version (`git --version`).
- **An AI CLI.** Lintel is **full** on Claude Code, Codex, and Cursor; **supported** on Gemini CLI,
  OpenCode, GitHub Copilot CLI, and Factory Droid; best-effort elsewhere. See the capability table in
  the [README](../README.md#multi-cli-support-honest-table). One important caveat: the **enforcement
  hooks fire only on Claude Code** — every other CLI gets the skills, the cycle discipline, and the
  pack-driven knowledge, just not the live hook gate.
- **Bash** (Linux/macOS/WSL/Git Bash) or **PowerShell 7+** — only needed if you want the scaffolding
  factory (`bin/li-scaffold`) or to run the installer/tests locally.

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

## 3. Run a real cycle

When you have a real task, run the full development cycle:

```
/li:cycle "add a rate limiter to the login endpoint"
```

It walks SENSE → SCOPE → DEFINE → DISCOVER → PLAN → BUILD → REVIEW → SHIP → CAPTURE, with gates
(cost estimate before BUILD, a founder-approval pause at the end of PLAN, adversarial review before
SHIP). For a quick fix, `/li:fix`; to just plan, `/li:plan`. Browse everything with `/li:catalog`.

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

That drops a `CLAUDE.md`, `CORE-PRINCIPLES.md`, `tasks/` (lessons/memory/personas/todo), `docs/adr/`,
and baseline subagents into the repo — a disciplined AI workspace in about thirty seconds. It never
clobbers existing files.

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
- **Hooks don't fire** — hooks are a Claude-Code-only mechanism *and* ship opt-in (you symlink the
  ones you want into `~/.claude/hooks/` and register them in `~/.claude/settings.json`). `/li:welcome`
  shows you exactly how. On other CLIs they don't fire at all — that's by design, stated honestly.
- **Installer issues** — `li-doctor --verbose` reports per-CLI state; re-running the install is safe
  (idempotent).
