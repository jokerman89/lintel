---
name: research
layer: foundation
description: Use when the operator wants to understand a domain, codebase or option space before committing to implementation. Runs the research-dive cycle — SENSE, DEFINE and DISCOVER — and stops with sourced findings, never BUILD or SHIP.
color: cyan
tools: Read, Bash, Grep, Glob
voice: internal
cli_support: [claude-code, codex, copilot]
---

# Research

A compatibility shortcut for exactly one route:

```
/li:cycle --mode research-dive
```

Follow the [cycle](../cycle/SKILL.md) research-dive preset. It runs SENSE, DEFINE and
DISCOVER and skips PLAN, BUILD, REVIEW, SHIP and CAPTURE. This entry adds no phase
engine, mode or flag of its own; forward only the operator's research scope.

- DEFINE frames the research question and source boundary. It does not require an
  approved implementation design, and its findings are not implementation approval.
- Keep the selected work, scope and data-handling boundaries. Read-only research is not
  a policy exemption; the active pack's read and data rules still apply.
- Write research or discover artifacts only where writing is authorized. When all
  writes are forbidden, report findings in the conversation instead.
- Ask only for missing source access or material research questions; do not ask again
  whether to do the research the operator requested.

Implementation afterwards needs its own scoped DEFINE/PLAN approval, for example
`/li:cycle --from PLAN` on the selected design.
