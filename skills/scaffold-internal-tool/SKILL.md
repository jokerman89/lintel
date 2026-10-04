---
name: scaffold-internal-tool
layer: foundation
description: Use for the retained internal-tool scaffold entry; delegates the selected CLI, service, dashboard or script intent to scaffold's owned method in internal-tool mode.
color: green
tools: Read, Write, Bash, Glob
voice: internal
cli_support: [claude-code, codex, copilot]
---

# Scaffold an internal tool

Delegate to [scaffold](../scaffold/SKILL.md#application-mode-acceptance-one-owner)
with the existing `--mode internal-tool`. Preserve supplied `--name`, `--path`,
`--language`, `--type` and `--ci`, existing acceptance answers, selected map/profile
and authority. `--path` maps to the explicit working target, never a basename guess.

Scaffold owns the application acceptance/failure questions and the actual
`bin/li-scaffold init` operation. Retain CLI, service, dashboard and automation-script
intent, but do not repeat its interview, stack advice or foundation-copy procedure.
Intent-only options are not blindly forwarded as helper flags.

Follow that owner's source/target, collision, profile and recovery checks, no-install
without authority, actual flow verification and handoff limits. This alias grants no
extra write, deployment, publication or private synchronization authority.
