---
name: migrations
layer: foundation
description: Read the installed-source migration catalog against the selected target, preserving overdue, unknown and historical recovery states.
color: yellow
tools: Read, Bash, Glob, Grep
voice: internal
cli_support:
  - cli: claude-code
    level: full
  - cli: codex
    level: full
  - cli: copilot
    level: full
---

# Migrations

Retained read-only front door to doctor's [migration inspection procedure](../doctor/references/inspection.md#migrations).
Use the existing catalog reader, with `--all` for archived schedules. Keep schedule
and actual target observation separate; missing detectors remain unknown.

Read the full owner method for layout, historical identity signals and explicit
execution/recovery boundaries. This entry neither applies migrations nor selects
a pack. Age, missing observations and an archived schedule authorize no cleanup.
