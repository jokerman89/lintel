---
name: roles-list
layer: foundation
description: Use to list configured role metadata and the current selection, with explicit consent before including private roles.
color: cyan
tools: Read, Bash, Grep, Glob
voice: internal
cli_support: [claude-code, codex, copilot]
---

# Roles list

Retained read-only front door to the role owner's
[lifecycle inventory](../role/references/lifecycle.md#list). Use its configured
roots, bounded metadata, duplicate/shadowed rows and actual-selection reporting.
`--include-private` requires the method's explicit private-metadata consent; it
does not authorize reading a private role body.

Listing changes no preference, profile, ledger or synchronization state. Empty
neutral-pack inventory is valid; errors are not an empty success. If a role ID
is already known, use `/li:role <id>` directly. Creation remains `/li:role-new`.
