---
name: li-perf-mode
description: Advise on bounded working sets, context observations and checkpoint strategy for heavy phases; never changes model capacity.
---

> **Lintel on GitHub Copilot.** Generated from `skills/perf-mode/SKILL.md`; edit the canonical file, then run
> `li-copilot init`.
> - **Resource root:** `../../..` from this skill's base directory (the Lintel source with `bin/`,
>   `lib/`, `skills/`). Write plans, state and evidence into the working repository's `.claude/`
>   tree, never into the resource root.
> - **Shell steps:** run Bash snippets with Bash (Git for Windows' `bash.exe` on Windows, never
>   `System32\bash.exe`). Save a snippet to a temporary `.sh` file and run
>   `bash "<resource root>/bin/li-run" <file>`; it prepares `LINTEL_SOURCE_ROOT`, `LINTEL_REPO_ROOT`
>   and the profile context.
> - **Tools:** Read=`view`, Write=`create`, Edit=`edit`, Bash=`bash`/`powershell`, Grep=`grep`,
>   Glob=`glob`, AskUserQuestion=`ask_user`, TodoWrite=the plan checklist, Task or a named role=`task`
>   with that custom agent, WebFetch=`web_fetch`.
> - **Other Lintel workflows** are native skills: invoke `/li-<name>` rather than reading their
>   files. Named roles such as `CodeReviewer` are custom agents.

# Perf mode

Keep `/perf-mode` as the resource-advice entry point for long integrations, multi-session
consolidation and heavy deliverables. It does **not** activate a larger model window,
install a context engine, change a host setting or promise a fixed dollar cost.
Routine small edits do not need this additional planning.

## Inputs retained

| Input | Actual effect |
|---|---|
| `--budget <N>` | Desired local working-set size for planning, not capacity |
| `--ceiling <N>` | Local advisory upper bound; cannot override the host |
| `--decay-policy <prompt-operator|aggressive|conservative|retain-all>` | Advice on future retrieval/checkpointing, not deletion of conversation |
| `--cost-estimate` | Reports unknown without actual pricing and billable-usage inputs |
| `--off` | Ends this advisory preference; active conversation is unchanged |

Ask through the actual host question mechanism only when a needed decision is missing.
Lack of a specifically named question tool is not permission to choose a costly setting.

## Shared observation and advice

```bash
source_root="${LINTEL_SOURCE_ROOT:?Set the trusted Lintel source root}"
source "$source_root/bin/_context.sh"
context_perf "$@"
```

Pass `--bytes` from the bounded source manifest. Host capacity/usage arguments have the
same semantics as `/li-context-budget`: `--capacity --capacity-source` must be actually
reported for this session; `--used --usage-source` needs an observation or a labeled
`--usage-kind estimated` heuristic. Do not infer a capacity from the chosen model's name
or a saved preference.

The helper returns resource advice without writing any host configuration or activation
marker. There is no automatic reader of historical `perf-mode-active` files: leave them
as historical preferences, never evidence of activation. No watcher, billing aggregator,
phase engine or decay control is implicitly enabled.

## Make the advice useful

1. Name the deliverable and the smallest source set required for its next phase.
2. Preview literal paths or declared globs with `/li-context-warm`, including source sizes.
   Do not recommend `--pattern all` as a whole-repository load.
3. Show known active usage and capacity separately from planned inputs and cumulative
   billable tokens. Unknown capacity stays unknown even with `--budget 800000`.
4. Break oversized work into evidence-preserving checkpoints. Retain failure context
   for debugging, decisions for integration, and exact source identities for review.
5. If cost matters, obtain current provider/model pricing and actually billable input,
   output/cache observations before calculating an explicitly labeled estimate. Do not
   derive dollars or hours of runway from a requested context budget.
6. Suggest model/host configuration changes only through a real available control and
   within current authorization. Describe unavailable controls as unavailable.

Report the selected sources, local advisory preferences, observation provenance, unknowns
and checkpoint recommendation. `host_settings_changed` is false; `--off` cannot restore
a fictional "default 200k" limit. `/li-context-cool` affects future reads only, while
`/li-pause` and selected checkpoint reads retain useful continuity.
