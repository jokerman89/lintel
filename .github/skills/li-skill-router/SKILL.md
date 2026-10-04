---
name: li-skill-router
description: Use to find a relevant Lintel method from free-text intent through catalog's metadata-first shortlist.
---

> **Lintel on GitHub Copilot.** Generated from `skills/skill-router/SKILL.md`; edit the canonical file, then run
> `li-copilot init`.
> - **Resource root:** `../../..` from this skill's base directory (the Lintel source with `bin/`,
>   `lib/`, `skills/`). Write plans, state and evidence into the working repository's `.claude/`
>   tree, never into the resource root.
> - **Skill-relative paths:** this skill's own `scripts/`, `references/` and `data/` folders (and a
>   `<base>` that the workflow defines as its own directory) mean
>   `../../../skills/skill-router/` in the Lintel source, not this generated folder.
>   `${LINTEL_SKILLS_DIR:-skills}` means the skills root, `../../../skills`. A `bin/li-run` step
>   runs in the working repository, so use `$LINTEL_SKILLS_DIR/skill-router/` there.
> - **Shell steps:** run Bash snippets with Bash (Git for Windows' `bash.exe` on Windows, never
>   `System32\bash.exe`). Save a snippet to a temporary `.sh` file and run
>   `bash "<resource root>/bin/li-run" <file>`; it prepares `LINTEL_SOURCE_ROOT`, `LINTEL_REPO_ROOT`
>   and the profile context.
> - **Tools:** Read=`view`, Write=`create`, Edit=`edit`, Bash=`bash`/`powershell`, Grep=`grep`,
>   Glob=`glob`, AskUserQuestion=`ask_user`, TodoWrite=the plan checklist, Task or a named role=`task`
>   with that custom agent, WebFetch=`web_fetch`.
> - **Other Lintel workflows** are native skills: invoke `/li-<name>` rather than reading their
>   files. Named roles such as `CodeReviewer` are custom agents.

# Skill router

Retained front door for an operator who does not know the method's name. Follow
catalog's [intent narrowing](../../../skills/catalog/references/intent.md) in full, including
literal queries, at most three selected-body reads, source/parser failures,
privacy, aliases and the actual host's discovery and permission boundaries.
Catalog owns selection; this entry adds no routing algorithm or model call.

If the request already names a method, use that method rather than adding a routing
turn. For agents, use the same catalog metadata and an actual authorized delegation
binding, not a role file as proof of availability or independent review.

Return fit, alternatives and limitations. A recommendation does not execute work,
change installation, or waive SENSE's pack-configured high-risk confirmation.
