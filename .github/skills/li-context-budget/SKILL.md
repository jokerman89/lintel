---
name: li-context-budget
description: Show observed context capacity and usage where available, clearly labeled input estimates otherwise; --watch compares available observations with local warning thresholds.
---

> **Lintel on GitHub Copilot.** Generated from `skills/context-budget/SKILL.md`; edit the canonical file, then run
> `li-copilot init`.
> - **Resource root:** `../../..` from this skill's base directory (the Lintel source with `bin/`,
>   `lib/`, `skills/`). Write plans, state and evidence into the working repository's `.claude/`
>   tree, never into the resource root.
> - **Skill-relative paths:** this skill's own `scripts/`, `references/` and `data/` folders (and a
>   `<base>` that the workflow defines as its own directory) mean
>   `../../../skills/context-budget/` in the Lintel source, not this generated folder.
>   `${LINTEL_SKILLS_DIR:-skills}` means the skills root, `../../../skills`. A `bin/li-run` step
>   runs in the working repository, so use `$LINTEL_SKILLS_DIR/context-budget/` there.
> - **Shell steps:** run Bash snippets with Bash (Git for Windows' `bash.exe` on Windows, never
>   `System32\bash.exe`). Save a snippet to a temporary `.sh` file and run
>   `bash "<resource root>/bin/li-run" <file>`; it prepares `LINTEL_SOURCE_ROOT`, `LINTEL_REPO_ROOT`
>   and the profile context.
> - **Tools:** Read=`view`, Write=`create`, Edit=`edit`, Bash=`bash`/`powershell`, Grep=`grep`,
>   Glob=`glob`, AskUserQuestion=`ask_user`, TodoWrite=the plan checklist, Task or a named role=`task`
>   with that custom agent, WebFetch=`web_fetch`.
> - **Other Lintel workflows** are native skills: invoke `/li-<name>` rather than reading their
>   files. Named roles such as `CodeReviewer` are custom agents.

# Context budget

Report four different quantities separately: selected source size, currently active model
context, cumulative/billable usage and disk storage. They are not interchangeable.
There is no universal 1M window and a saved marker cannot change the host's limit.

Use before a large warm, to answer a resource question or to diagnose repeated/irrelevant
context. A checkpoint file on disk does not reset active usage. A new session may have
different host-reported capacity and preloaded instructions.

## Shared admission reader

```bash
source_root="${LINTEL_SOURCE_ROOT:?Set the trusted Lintel source root}"
source "$source_root/bin/_context.sh"
context_budget "$@"
```

The helper is read-only. With no arguments it reports capacity, usage and headroom as
unknown. `--bytes <N>` comes from the actual selection manifest; the returned input
estimate is `ceil(bytes / 4)`, not measured active usage.

Only supply `--capacity <N> --capacity-source <observation>` for the current host/model
limit actually exposed by the client. Supply `--used <N> --usage-source <observation>`
for active usage; add `--usage-kind estimated` for a stated heuristic. `--reserve <N>`
reserves explicitly chosen output/tool headroom. A known over-capacity selection is
reported as such. An estimated fit is labeled estimated, never verified.

Read `.claude/runtime/state/context-budget.md` as a source/read history when present.
Do not infer the full conversation from it, sum repeated loads as exact active usage,
or treat absent telemetry/logs as an empty window. Report observation age and remeasure
before relying on earlier headroom.

## Local thresholds and compatibility

`mode_envelopes` remain optional **local advisory workload thresholds**, not client limits
or automatically installed settings. Retain the historical examples for existing plans:

```yaml
mode_envelopes:
  hotfix:              { soft: 200k, hard: 300k }
  customer-engagement: { soft: 500k, hard: 750k }
  research-dive:       { soft: 750k, hard: 900k }
  demo-prep:           { soft: 300k, hard: 450k }
  internal-tool:       { soft: 400k, hard: 600k }
```

The former 500k soft / 750k hard figures are **not defaults for model capacity**.
No mode, company context or larger window is inferred when configuration is absent.
An operator may choose lower local warnings; a local threshold can never raise a host
limit. A policy-mandated admission bound stays mandatory and must name its policy source.
Synthetic vs real warming describes provenance only: **both** spend tokens when sent.
There is no synthetic-brief exemption.

## Watch mode (`--watch`)

Keep `--watch`, `--budget <yaml>`, `--quiet` and `--mode <soft|hard|both>` as skill inputs.
The skill reads the selected configuration as data and passes only actual observations
to the shared helper; it does not pass those skill-only flags to `context_budget`.

1. Read explicit watcher configuration, if authorized, and show its source. Existing
   `soft_token`, `hard_token`, `soft_tool_calls`, `hard_tool_calls` keys denote local warning
   thresholds. Missing keys may use labeled advisory examples (50000/80000 tokens and
   80/130 tool calls), never model capacity. Other clients' key shapes need adapter mapping.
2. Read available session telemetry. Mark each token/tool count observed, estimated or
   unknown and identify its source. Do not fabricate elapsed time or per-turn usage.
3. Compare known counts with selected thresholds: below soft, warning at soft, red at hard.
   Missing counts remain unknown; missing all telemetry cannot produce a healthy green.
4. With `--quiet`, suppress only a known below-threshold result. Still report unknown/error.
   In CI, report red/unknown as non-success if this check is required; zero observations
   are not a verified pass. This skill is not a background watcher or a registered hook.
5. Recommend bounded retrieval, `/li-pause` and a fresh session where useful.
   Only suggest a host compaction control when that exact control is available and its
   result can be observed. `/clean` or disk archival alone cannot reclaim model context.

## Report

```text
Host capacity: unknown | <observed limit, source and time>
Active usage: unknown | <observed/estimated count, source and time>
Selected sources: <paths, bytes, estimated input tokens>
Headroom: unknown | <value, observed/estimated>
Local warning threshold: unset | <configured value and source>
Billable cumulative usage/cost: unknown unless separately observed
Disk cleanup: none performed
```

Never turn an advisory color/score into a policy clearance. Warming, cooling, save and
restore keep their own read/mutation boundaries and preserve the owner-aware checkpoints.
