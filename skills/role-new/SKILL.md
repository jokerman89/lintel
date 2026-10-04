---
name: role-new
layer: foundation
description: Use to create a durable role through a guided interview or update its expertise with a reviewed-digest, sensitivity-aware change.
color: cyan
tools: Read, Bash, Edit, Write
voice: internal
cli_support: [claude-code, codex, copilot]
---

# Role new

The retained create/update entry delegates to the role owner's
[complete lifecycle](../role/references/lifecycle.md#create-and-update-entrypoints).

- `/li:role-new`: use the adaptive interview and reviewed-draft publication.
- `/li:role-new --update <id>`: use the targeted update procedure and expected digest;
  when omitted, the ID defaults to the actual active role, never an invented choice.

Read that method before acting. Preserve every expertise section, explicit sensitivity,
private-body consent, destination review and conflict-safe update. Neither operation
activates a role or private synchronization. One-off personas stay conversation context;
customer PII and credentials do not belong in a role file.

Existing-role selection remains `/li:role <id>`; discovery remains `/li:roles-list`.
