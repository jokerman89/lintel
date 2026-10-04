---
name: pack-switch
layer: foundation
description: Use to explicitly switch the effective pack through the structured profile lifecycle, preserving required policy, configured paths and generation-bound recovery.
color: green
tools: Read, Write, Bash
voice: internal
cli_support: [claude-code, codex, copilot]
---

# Pack switch

This entry owns the [shared pack lifecycle](references/lifecycle.md#switch).
Follow its validation, authorization, real helper invocation, full returned
reference and interruption/recovery procedure. An explicit switch request already
authorizes its stated scope; ask only for missing decisions.

The existing `pack-list`, `pack-validate`, `pack-create` and `pack-switch` names
remain. Read-only discovery/validation never implies mutation. A switch changes
the selected policy context; it does not install plugins, activate hooks, grant
host permission or select models. Required-policy errors stay blocked.
