# Lintel — OpenCode install instructions

Instructions for OpenCode to follow when an operator runs:

```
Fetch and follow instructions from https://raw.githubusercontent.com/jokerman89/lintel/refs/heads/main/.opencode/INSTALL.md
```

## What Lintel is

Lintel is a company-neutral, pack-driven session harness for agent-based development:
canonical workflows (skills), specialist agent roles, optional hooks and repository
scaffolding, exposed to each client through thin adapters. Identity (voice, compliance,
persona) resolves from the active pack; only the neutral `_default` pack ships in this repo.

## Install steps

1. Clone the repo (or fetch raw files on demand): `git clone https://github.com/jokerman89/lintel`
2. Read `AGENTS.md` (repo map + load-bearing rules), then `AGENT-INSTRUCTIONS.md` —
   the canonical cross-CLI session ritual. Treat both as the session bootstrap.
3. For a shared project kit on the OpenCode CLI/TUI, run from the reviewed checkout:
   `python3 bin/li-adapter.py init --client opencode-cli --target <project>` and then
   `python3 bin/li-adapter.py check --target <project>`. This generates `.opencode/skills/li-*`
   wrappers for the core entry points plus the `.github/lintel/` source bundle. OpenCode
   desktop and IDE surfaces (`opencode-desktop`, `opencode-ide`) use the manual route.
4. Invoke wrappers by the names OpenCode actually lists. For any other workflow, or when
   discovery is unavailable, read `.github/lintel/START.md` and the canonical
   `skills/<name>/SKILL.md` explicitly. Canonical documents write `/li:<skill>`; that is
   the Claude plugin's notation, not OpenCode syntax.
5. Hooks (`hooks/shared/`) are a Claude Code-compatible bundle and are not translated for
   OpenCode. Read each `HOOK.md` and apply its discipline manually; do not claim enforcement.
6. Capability honesty: `python3 bin/li-client-capabilities.py show --client opencode-cli`
   separates vendor documentation, delivered files and observed runs. Live workflows
   remain `not_run` until a real session is recorded; do not over-claim.

## Update flow

Pull the next approved revision, re-read `AGENT-INSTRUCTIONS.md`, and re-run `init` and
`check` on an upgrade branch. Former workflow names are mapped in
`docs/migrations/2026-09-25-native-workflows.md`; they are not aliases.

## Issues

https://github.com/jokerman89/lintel/issues
