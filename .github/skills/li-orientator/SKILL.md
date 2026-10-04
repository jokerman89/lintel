---
name: li-orientator
description: Use for entry-time method guidance through catalog, preserving SENSE's existing pack navigation and high-risk confirmation.
---

> **Lintel on GitHub Copilot.** Generated from `skills/orientator/SKILL.md`; edit the canonical file, then run
> `li-copilot init`.
> - **Resource root:** `../../..` from this skill's base directory (the Lintel source with `bin/`,
>   `lib/`, `skills/`). Write plans, state and evidence into the working repository's `.claude/`
>   tree, never into the resource root.
> - **Skill-relative paths:** this skill's own `scripts/`, `references/` and `data/` folders (and a
>   `<base>` that the workflow defines as its own directory) mean
>   `../../../skills/orientator/` in the Lintel source, not this generated folder.
>   `${LINTEL_SKILLS_DIR:-skills}` means the skills root, `../../../skills`. A `bin/li-run` step
>   runs in the working repository, so use `$LINTEL_SKILLS_DIR/orientator/` there.
> - **Shell steps:** run Bash snippets with Bash (Git for Windows' `bash.exe` on Windows, never
>   `System32\bash.exe`). Save a snippet to a temporary `.sh` file and run
>   `bash "<resource root>/bin/li-run" <file>`; it prepares `LINTEL_SOURCE_ROOT`, `LINTEL_REPO_ROOT`
>   and the profile context.
> - **Tools:** Read=`view`, Write=`create`, Edit=`edit`, Bash=`bash`/`powershell`, Grep=`grep`,
>   Glob=`glob`, AskUserQuestion=`ask_user`, TodoWrite=the plan checklist, Task or a named role=`task`
>   with that custom agent, WebFetch=`web_fetch`.
> - **Other Lintel workflows** are native skills: invoke `/li-<name>` rather than reading their
>   files. Named roles such as `CodeReviewer` are custom agents.

# Orientator

Retained `/li-orientator <prompt>` front door for entry-time guidance. For a supplied
intent, follow catalog's [intent narrowing](../../../skills/catalog/references/intent.md), not a
second keyword table or selection method. Return the recommended method, rationale,
alternatives and observed limitations without running it.

Skip this discovery turn when the operator already selected a workflow or supplied
`--mode` / `--from`. Mid-cycle work keeps its selected map and phase; do not infer a
new task from a state-file tail.

## SENSE owns navigation control

[SENSE Step 0d](../../../skills/sense/SKILL.md#step-0d--orientator-invocation-v40-phase-3)
calls `lib/orientator-routing.sh` directly, **not this public skill**. That existing
method verifies the profile, reads the pack's navigation, obtains a mechanical
recommendation and records its actual decision through `audit_log`. The library and
its [navigation reference](../../../docs/concepts/orientator.md) remain compatible.

Keep these boundaries when proceeding from guidance to an authorized workflow:

- SENSE's high-risk workflow always requires explicit confirmation, including when
  auto-mode is eligible. Low confidence needs judgment or an unresolved-decision
  question; it is not evidence of another model call.
- Configured defaults and extension namespaces remain pack-owned. A missing or drifted
  required profile blocks dependent navigation; never substitute neutral success.
- Explicit operator choices override a recommendation, not host permissions or
  mandatory controls. Verify the selected native entrypoint before execution.
- The compatibility escalation hook performs no model request. Do not report it as
  executed escalation, token consumption or measured routing success.

This wrapper writes no audit or state. SENSE remains the decision producer when it
actually runs; discovery alone must not fabricate an orientation event or execution.
