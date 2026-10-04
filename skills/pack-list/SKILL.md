---
name: pack-list
layer: foundation
description: List configured-store, repository and installed-source packs with resolver precedence, validation results and the actual effective profile.
color: green
tools: Read, Bash, Glob
voice: internal
cli_support: [claude-code, codex, copilot]
---

# Pack list

Retained read-only front door to [pack lifecycle: list](../pack-switch/references/lifecycle.md#list).
Use its actual configured-root inventory, selected/shadowed origins, effective
profile and diagnostics. Preserve `--validate` as the request for per-row details,
not a new helper option.

Use before selecting or creating a pack, or after an explicitly authorized identity
change. Listing binds nothing, changes no pointer and does not prove host activation.
Use `pack-validate` for effective fields and `pack-switch` for a policy-context change.
