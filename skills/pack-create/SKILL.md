---
name: pack-create
layer: foundation
description: Use to create a blank, inherited, or cloned Lintel pack and validate it before activation.
color: green
tools: Read, Write, Edit, Bash
voice: internal
cli_support: [claude-code, codex, copilot]
---

# Pack create

Retained front door to [pack lifecycle: create](../pack-switch/references/lifecycle.md#create).
Follow that complete method for blank, inherited (`--extends`) or cloned-manifest
(`--from`) creation, explicit `--scope repo|home`, collision refusal, validation,
pattern assets and extension-skeleton limits.

This publishes a reviewed manifest, not a new active profile. No automatic
activation, private synchronization or host installation follows. Existing pack
edits and one-off workflow choices do not require creating another pack.
