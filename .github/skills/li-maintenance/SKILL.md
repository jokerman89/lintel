---
name: li-maintenance
description: Use for on-demand storage/context guidance, scoped path diagnostics and labeled usage estimates without treating partial logs as health or claiming model compaction.
---

> **Lintel on GitHub Copilot.** Generated from `skills/maintenance/SKILL.md`; edit the canonical file, then run
> `li-copilot init`.
> - **Resource root:** `../../..` from this skill's base directory (the Lintel source with `bin/`,
>   `lib/`, `skills/`). Write plans, state and evidence into the working repository's `.claude/`
>   tree, never into the resource root.
> - **Skill-relative paths:** this skill's own `scripts/`, `references/` and `data/` folders (and a
>   `<base>` that the workflow defines as its own directory) mean
>   `../../../skills/maintenance/` in the Lintel source, not this generated folder.
>   `${LINTEL_SKILLS_DIR:-skills}` means the skills root, `../../../skills`. A `bin/li-run` step
>   runs in the working repository, so use `$LINTEL_SKILLS_DIR/maintenance/` there.
> - **Shell steps:** run Bash snippets with Bash (Git for Windows' `bash.exe` on Windows, never
>   `System32\bash.exe`). Save a snippet to a temporary `.sh` file and run
>   `bash "<resource root>/bin/li-run" <file>`; it prepares `LINTEL_SOURCE_ROOT`, `LINTEL_REPO_ROOT`
>   and the profile context.
> - **Tools:** Read=`view`, Write=`create`, Edit=`edit`, Bash=`bash`/`powershell`, Grep=`grep`,
>   Glob=`glob`, AskUserQuestion=`ask_user`, TodoWrite=the plan checklist, Task or a named role=`task`
>   with that custom agent, WebFetch=`web_fetch`.
> - **Other Lintel workflows** are native skills: invoke `/li-<name>` rather than reading their
>   files. Named roles such as `CodeReviewer` are custom agents.

# Maintenance

Retained compatibility front door for four on-demand routes. Choose one requested
mode, then follow its existing owner in full; do not run another path manifest,
token predictor, event parser or cleanup procedure here.

| Retained mode | Owner and supported invocation | Meaning |
|---|---|---|
| `--force-compact` | [Context budget](../../../skills/context-budget/SKILL.md): `/li-context-budget --advice` | Working-set/storage advice, not compaction |
| `--monitor-paths` | [Doctor inspection](../../../skills/doctor/references/inspection.md): `/li-doctor --layers-only` | Actual source/foundation/layout/adapter observations |
| `--simulate-tokens <workflow>` | [Context budget](../../../skills/context-budget/SKILL.md): observation, or `--handoff --map <selected work.json>` for explicit mapped inputs | Selected-input estimate, not a workflow-cost prediction |
| `--rust-report` | [Audit observations](../../../skills/audit/references/method.md): `/li-audit --category usage-skill --since 30` | Recorded usage samples, not a disuse verdict |

The skill names above are workflow routes. Doctor's filtered view is presentation,
not a `--layers-only` argument to `bin/li-doctor`; its owner supplies the real helper
arguments and preserves the complete diagnostic exit. Audit maps its filters to the
existing event reader. Use native entrypoints actually available on the host, or the
same trusted owner through a permitted file handoff; never bypass a denied operation.

## Context and estimates

`--force-compact` cannot clear a conversation, enable a watcher or invoke an unavailable
host control. Follow context-budget's advice and, if useful and authorized, its
pause/fresh-session/resume route. Retain the same original map, verified profile and
required policy; do not select a newer basename as the current task.

For `--simulate-tokens`, retain the supplied workflow name as a report label only.
Do not pass it as a size or unsupported provider flag. Use actual selected bytes with
the owner's `--bytes` observation, or explicitly selected mapped artifacts through
`--handoff --map`. Pass `--capacity`, `--capacity-source`, `--used`, `--usage-source`
and other owner-supported observation arguments only when those facts exist.
No selected inputs or compatible measurements means **unknown**, not a stock token range.
Selected input size, active context, cumulative usage and disk bytes remain separate.
No billing/cost or p95 precision can be inferred from a few optional manual entries.

## Path and usage results

`--monitor-paths` returns doctor's actual results. A missing/failed required observation
is incomplete, not a successful partial health check. Repairs, migration and profile
changes require separate scoped authority; file presence is not host activation.

`--rust-report` uses only explicitly authorized log roots. If requested, inspect other
actual `usage-*` categories through audit too. Count **recorded** invocations in the
named source/window; the historical fewer-than-two samples threshold is only a review
prompt for observed rows. An absent name/log is **unobserved/coverage unknown**, not
unused or safe to delete. Preserve malformed-line diagnostics and preview limitations.
Use catalog's ordinary metadata separately if an explicit join was requested, not a
different catalog feature or an implicit personal telemetry scan.

## No implicit cleanup

All four routes are read-only/advisory. Age and partial usage never authorize archiving,
deletion, profile changes or a global sink. Any later disk operation must name exact
owned paths and destination, preserve unrelated content, and use the existing owned
snapshot/recovery method under separate authority. Report storage changed only after
observing it; active-context reclamation remains unestablished without actual host evidence.

Return the selected owner, actual command/result, observations, limitations and one
appropriate next step. Missing tools, denied reads and parser failures remain explicit;
there is no automatic fallback estimator, background monitor or maintenance daemon.
