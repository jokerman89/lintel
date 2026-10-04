---
name: audit
layer: foundation
description: Use to read selected audit records and diagnostics, including hook or usage observations, without inferring execution from missing logs.
color: yellow
tools: Read, Bash
voice: internal
cli_support:
  - cli: claude-code
    level: full
  - cli: codex
    level: full
  - cli: copilot
    level: full
---

# Audit

Owns the [shared audit and hook observation method](references/method.md).
Retain `--category <name>`, `--kind <kind>`, `--since <days>` and `--limit <N>`
(default 50 displayed rows). No arguments lists actual categories and counts.

Follow the shared method and its source-owned `read.sh`; it delegates path selection
to `_audit.sh` and parsing to `li-events.py`. `hooks-status` delegates its existing
view flags to that same method. Neither front door writes logs or creates state.
Missing logs remain unobserved; malformed records and reader errors stay visible.

In-flight work belongs to `status`/`jobs`; Git history is not this event trail.
Producers keep the existing audit writer. Do not edit history or treat a reader as
proof of enforcement, host activation or delivery.
