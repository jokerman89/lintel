# Lintel — OpenCode install instructions

Instructions for OpenCode to follow when an operator runs:

```
Fetch and follow instructions from https://raw.githubusercontent.com/jokerman89/lintel/refs/heads/main/.opencode/INSTALL.md
```

## What Lintel is

Lintel is a company-neutral, pack-driven session harness for agent-based development —
markdown + bash scaffolding that an AI CLI loads as a plugin: skills (slash-commands),
agents (subagent roles), hooks, and repo-scaffolding templates. Identity (voice,
compliance, persona) resolves from the active pack; only the neutral `_default` pack
ships in this repo.

## Install steps

1. Clone the repo (or fetch raw files on demand): `git clone https://github.com/jokerman89/lintel`
2. Read `AGENTS.md` (repo map + load-bearing rules), then `AGENT-INSTRUCTIONS.md` —
   the canonical cross-CLI session ritual. Treat both as the session bootstrap.
3. Load skills from `skills/<name>/SKILL.md` and agents from `agents/<category>/<Name>.md`
   per OpenCode's discovery mechanism. Counts are computed, never hardcoded:
   `find skills -name SKILL.md | wc -l` and `find agents -name '*.md' | grep -cv README`
4. Hooks (`hooks/shared/`) are optional; hook *enforcement* fires on Claude Code only.
   On OpenCode, read each `HOOK.md` and apply its discipline manually.
5. Capability honesty: `source lib/cli-tiers.sh; cli_tier_field opencode tier` before
   claiming a capability — never over-claim what this CLI cannot do.

## Update flow

Re-fetch from `main` and re-read `AGENT-INSTRUCTIONS.md`. Per-skill OpenCode shims (if
ever needed) live in `.opencode/plugins/` — currently empty; skills load as content.

## Issues

https://github.com/jokerman89/lintel/issues
