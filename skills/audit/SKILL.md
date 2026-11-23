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

For manually requested usage reports, follow the
[usage observation method](references/usage.md). `--usage` selects that skill-level
view; `--report`, `--days`, `--topn` and `--tokens-by-skill` describe report choices,
not additional `li-events.py` or shell-reader flags. The view uses the same selected
audit reader and never writes unless the operator separately requests manual recording.

Follow the shared method and its source-owned `read.sh`; it delegates path selection
to `_audit.sh` and parsing to `li-events.py`. `hooks-status` delegates its existing
view flags to that same method. Neither front door writes logs or creates state.
Missing logs remain unobserved; malformed records and reader errors stay visible.

The former maintenance flags and their replacements are mapped in the
[usage and retirement reference](references/usage.md#retired-maintenance-routes).
These are intent mappings, not flags for the underlying helpers. None starts
compaction, monitoring, prediction or cleanup.

In-flight work belongs to `status`/`jobs`; Git history is not this event trail.
Producers keep the existing audit writer. Do not edit history or treat a reader as
proof of enforcement, host activation or delivery.
