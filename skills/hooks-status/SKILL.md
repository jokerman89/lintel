---
name: hooks-status
layer: foundation
description: Use to inspect recorded hook outcomes, overrides or unobserved hooks through the shared audit reader; absence is not an execution verdict.
color: yellow
tools: Read, Write, Bash, Glob
voice: internal
cli_support:
  - cli: claude-code
    level: full
  - cli: codex
    level: degraded
  - cli: copilot
    level: full
---

# Hooks status

Retained front door to audit's [hook observation method](../audit/references/method.md#hook-views).
Select `--records`, `--overrides` or `--unobserved`, with optional `--days N`.
No view means `NEEDS_CONTEXT`; do not silently choose one.

Follow the shared reader, producer-field interpretation, aggregation and diagnostic
procedure. These flags choose a report, not new helper arguments. This entry writes
nothing and keeps absence unobserved.

This is not live hook detection or installation repair. For installed-byte questions,
use the doctor observation route named by the same method. Current host registration,
activation and execution remain unverified without their own actual evidence.
