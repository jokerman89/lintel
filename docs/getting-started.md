# Getting started

Step-by-step for a new MS Sweden CAIP SE getting this scaffolding running.

## Prerequisites

- **Git** — any recent version. Verify with `git --version`.
- **Bash** (Linux/macOS/WSL/Git Bash on Windows) **or PowerShell 7+** (Windows).
- **yq** for the bash installer / **powershell-yaml module** for the PowerShell installer (the PowerShell installer auto-installs the module on first run).
- **An agent CLI** — Claude Code, GitHub Copilot Enterprise, Codex, or another tool that reads a per-repo instruction file. Multiple is fine — they share the same canonical instructions.
- **Microsoft SSO** for your chosen CLI (enterprise tenant access).

Verify the basics:

```bash
git --version
bash --version       # OR: pwsh --version
yq --version         # bash users only
```

Missing `yq`?

- macOS: `brew install yq`
- Linux: `sudo apt install yq` (or download from the [yq releases page](https://github.com/mikefarah/yq/releases))
- Windows (bash): `scoop install yq`

## 1. Clone

```bash
# Replace with the MS-internal git URL once published
git clone <internal-MS-git-url>/jokerman-lintel ~/Workspace/jokerman-lintel
cd ~/Workspace/jokerman-lintel
```

## 2. Install

Pick one based on your shell.

```bash
# bash / zsh / Git Bash
bash install/install.sh
```

```powershell
# PowerShell 7+
pwsh install/install.ps1
```

What the installer does:

1. Verifies `git` and `yq` (or installs `powershell-yaml` if needed).
2. Backs up `~/.claude/` to `~/.claude-backup-<timestamp>/` if it exists.
3. Copies `scaffolding/` to `~/.claude-scaffolding/`.
4. Reads `install/upstream-sources.yaml` and clones each upstream source to the install path it specifies.
5. Prints license notes for any source on a restricted license tier (CC-BY-SA, mixed, no-license).

Expect the install to take 1–3 minutes depending on network and `gstack`'s post-install step.

## 3. Verify

```bash
bash install/verify.sh
```

Prints `✓` per source that is correctly installed. Any `✗` means re-run the installer or fix the underlying environment issue (network, permissions).

## 4. Wire up per-CLI

The scaffolding now lives at `~/.claude-scaffolding/`. The next step is telling each CLI to read it. Do this **once per repo where you want the setup active**, not globally.

### Claude Code

Nothing extra. The installer set up `~/.claude/CLAUDE.md` to point at the canonical instructions. Your existing per-repo `CLAUDE.md` files keep working — they have higher precedence than the user-global one.

### GitHub Copilot Enterprise (with Opus model picker)

In each repo where you want the scaffolding active:

```bash
mkdir -p .github
cp ~/Workspace/jokerman-lintel/shims/copilot-instructions.md .github/copilot-instructions.md
```

Or, on a system with symlink support, prefer a symlink so updates propagate:

```bash
ln -sf ~/Workspace/jokerman-lintel/shims/copilot-instructions.md .github/copilot-instructions.md
```

Then in the Copilot model picker, choose **Claude Opus** (or the latest Opus-class model). Default Copilot completions are tuned for inline suggestions — for agent-style work you want Opus.

### Codex CLI

In each repo where you want the scaffolding active:

```bash
cp ~/Workspace/jokerman-lintel/shims/AGENTS.md AGENTS.md
```

### Other agent CLIs

If the CLI reads a different filename: add a shim under `shims/` that points at `AGENT-INSTRUCTIONS.md`. Copy or symlink to the location your CLI expects.

## 5. First session

Open your CLI in a repo that has the shim in place. The agent should:

1. Read its shim (e.g. `CLAUDE.md` or `.github/copilot-instructions.md`).
2. Follow the shim's pointer to `AGENT-INSTRUCTIONS.md`.
3. Walk the 5-step session-start ritual (personas → compliance → memory → ADR scan → precedence).
4. Be ready to work.

If the agent does not do this, something is wrong with the shim. Re-check the file paths and that the agent actually loaded the shim file.

## 6. Where to next

- **[docs/multi-cli.md](multi-cli.md)** — how the canonical-instructions + shims pattern works across CLIs.
- **[docs/precedence.md](precedence.md)** — when an agent has multiple candidates for a task, how to pick.
- **[docs/promoted-agents.md](promoted-agents.md)** — what each installed upstream pack does + its license terms.
- **[docs/compliance.md](compliance.md)** — what you cannot do under MS guardrails.
- **[docs/power-user.md](power-user.md)** — patterns once the basics are running.
- **[docs/faq.md](faq.md)** — common questions.

## Troubleshooting

- **`yq: command not found`** — install yq, see prerequisites above.
- **Install fails partway through** — re-run `bash install/install.sh`. Already-cloned sources will `git pull` instead of re-clone.
- **Copilot ignores `.github/copilot-instructions.md`** — confirm you have Copilot Enterprise (not the standard Copilot), and that the file is in `.github/` at repo root, not in a subdirectory.
- **`gstack` post-install fails** — the gstack `./setup` script has its own prerequisites (see `~/.claude/skills/gstack/README.md`). The clone is still in place; you can re-run setup manually.
