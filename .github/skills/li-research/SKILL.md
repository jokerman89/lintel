---
name: li-research
description: Use when the operator wants to understand a domain, codebase or option space before committing to implementation. Runs the research-dive cycle — SENSE, DEFINE and DISCOVER — and stops with sourced findings, never BUILD or SHIP.
---

> **Lintel on GitHub Copilot.** Generated from `skills/research/SKILL.md`; edit the canonical file, then run
> `li-copilot init`.
> - **Resource root:** `../../..` from this skill's base directory (the Lintel source with `bin/`,
>   `lib/`, `skills/`). Write plans, state and evidence into the working repository's `.claude/`
>   tree, never into the resource root.
> - **Skill-relative paths:** paths relative to this skill's own folder (such as `<base>`,
>   `scripts/`, `references/`, `data/` or `${LINTEL_SKILLS_DIR:-skills}/…`) mean
>   `../../../skills/research/` in the Lintel source, not this generated folder. `bin/li-run` exports
>   `LINTEL_SKILLS_DIR` for shell steps.
> - **Shell steps:** run Bash snippets with Bash (Git for Windows' `bash.exe` on Windows, never
>   `System32\bash.exe`). Save a snippet to a temporary `.sh` file and run
>   `bash "<resource root>/bin/li-run" <file>`; it prepares `LINTEL_SOURCE_ROOT`, `LINTEL_REPO_ROOT`
>   and the profile context.
> - **Tools:** Read=`view`, Write=`create`, Edit=`edit`, Bash=`bash`/`powershell`, Grep=`grep`,
>   Glob=`glob`, AskUserQuestion=`ask_user`, TodoWrite=the plan checklist, Task or a named role=`task`
>   with that custom agent, WebFetch=`web_fetch`.
> - **Other Lintel workflows** are native skills: invoke `/li-<name>` rather than reading their
>   files. Named roles such as `CodeReviewer` are custom agents.

# Research

A compatibility shortcut for exactly one route:

```
/li-cycle --mode research-dive
```

Follow the [cycle](../../../skills/cycle/SKILL.md) research-dive preset. It runs SENSE, DEFINE and
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
`/li-cycle --from PLAN` on the selected design.
