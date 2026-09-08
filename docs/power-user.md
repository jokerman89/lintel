# Power-user patterns

The mechanisms on this page are optional. None of them are needed to run a cycle — see
[getting-started.md](getting-started.md) for that, and [the-cycle.md](the-cycle.md) for the nine
phases. What follows is the machinery that starts paying off when a task outlives a single session,
when the context window becomes the binding constraint, or when you need to reconstruct six months
later what the agent did and why.

This is v0.9.0-beta. Several of the mechanisms below are partly wired; each one names its own gap
rather than hiding it, and the gaps are collected at the end.

**The hooks described here use Lintel's Claude Code adapter.** The Copilot kit does not install them. Other features here are canonical skills and files available through the appropriate integration on each
CLI that can read markdown. See [multi-cli.md](multi-cli.md) for the per-CLI tier table.

---

## Context is a budget you spend on purpose

The default session-start load is roughly 5-15k tokens — the repo instruction file, the cross-CLI
ritual, lessons, the memory index, recent decision records, the active role. Everything beyond that
is an explicit choice.

### Warming

Six skills load context deliberately. Each reports the tokens it added and appends the event to
`.claude/runtime/state/context-budget.md`.

| Skill | Loads |
|---|---|
| `/li:context-warm <paths>` | Named files or globs. The base the others build on. `--pattern` warms the repo's declared high-leverage set instead of an explicit target. |
| `/li:context-warm-related <topic>` | Heuristic search across the working tree for the top N files matching a topic. |
| `/li:context-warm-adrs <topic>` | Decision records from `.claude/decisions/` whose title or body matches a topic. |
| `/li:context-warm-sessions [N]` | The last N session checkpoints on the current branch. |
| `/li:context-warm-from-url <url>` | Fetches a documentation page or reference into context. |
| `/li:context-warm-customer <name>` | Loads a separate engagement repo's instruction file, decisions and recent commits. |

Those six are the complete set. If you have seen another `context-warm-*` name in older notes, it
does not exist as a skill.

Warm before PLAN when discovery named specific files, and before REVIEW when the artifact under
review references code that is not yet in the window. Warming after the fact costs the same tokens
and buys less.

### Seeing the budget

`/li:context-budget` breaks utilization down by source and recommends warming or cooling.
`/li:context-budget --watch` runs the threshold check instead: soft at roughly 50k tokens or 80 tool
calls, hard at 80k or 130, and it recommends `/li:clean` or `/li:context-save` when a line is crossed.

Be clear about what this is: the numbers are **estimated** by summing the deltas in the budget log
plus a per-turn guess for conversation history. It is not a reading of the CLI's actual context
accounting. Treat it as a trend line, not a gauge.

### Cooling

`/li:context-cool` exists because a context window is append-only — nothing can retract tokens
mid-session. So cooling marks warmed sources as ignorable in
`.claude/runtime/state/context-ignore.md`, which downstream skills and subagents respect, and clears
the budget tracking. The only true reduction is the round trip: `/li:context-save`, restart the
session, `/li:context-restore`, then warm back only what you still need.

### Raising the ceiling

`/li:perf-mode` lifts the session budget ceiling from the 200k default to 800k, configurable up to
1M. It is for the moments where the outcome genuinely needs the whole picture loaded at once — a
multi-week consolidation, or a decomposed task whose sub-tasks share deep context. It is not a
substitute for warming the right ten files.

---

## Checkpoints and resume

Two independent stores hold "where we were", and it matters which one you left behind.

**Checkpoints** come from `/li:context-save`. The skill writes
`.claude/runtime/sessions/<branch>/<YYYYMMDD-HHMMSS>-<slug>[-<label>]-context-save.md` containing
what the task is, what got done, what is in flight, what is next, decisions taken, **failed attempts**
(so the next session does not retry them), and files touched. Pass a short label to name the
snapshot. `/li:context-restore` reads the newest checkpoint for the current branch, re-reads every
file it lists, and diffs the commits that landed since it was written.

**Cycle state** is `.claude/runtime/state/00-state.md` — the phase ledger a running cycle appends to.

`/li:resume` checks both. A session that ended mid-cycle leaves cycle state; one that ended with a
save leaves a checkpoint and no cycle state. Resume discovers whichever exists and either routes you
to the next phase or hands off to `/li:context-restore`.

**Continuous checkpointing** is off by default. Set `checkpoint_mode: continuous` in
`~/.lintel/profile.yaml` and BUILD commits a work-in-progress checkpoint after each completed task,
carrying a `[lintel-context]` block with the decisions made and what remains. It stages named files
only — never `git add -A` — and never commits a broken state. Any of those commits is a resume point.

---

## Roles load lazily

A role is a lens: identity, voice, and a per-phase outcome table. One is active at a time, and the
loading is deliberately staged so the lens costs almost nothing until you need the depth.

| Invocation | Effect |
|---|---|
| `/li:role <id>` | Activate. Loads identity, voice and the outcome-lens summary — roughly 500 tokens. |
| `/li:role --deep-dive [id]` | Load the full role file, roughly 2-3k tokens, on demand. |
| `/li:role --rotate <id>` | Swap atomically. Verifies the new role file exists **before** deactivating the current one. |
| `/li:role --frame <artifact>` | Apply the active role's outcome lens to an artifact. |
| `/li:role --off` | Deactivate. Voice tier reverts to the mode default. |

Activation writes `role_active` to `~/.lintel/profile.yaml`, so it persists across sessions —
including deactivation. Roles resolve from the active pack's role directory first, then
`~/.lintel/roles/private/`, then `~/.lintel/roles/`. A role marked `sensitivity: private` prompts
before activating and keeps its notes in repo runtime state rather than exporting them.

**The neutral default pack ships no roles**, and Lintel ships none of its own. `/li:roles-list` on a
fresh install is empty. Write your own with `/li:role-new`, or install a pack that carries a set.

---

## Jobs

A job is a curated flow with state — a cycle or a plan in flight. The store is repo-local:

```
<repo>/.claude/runtime/jobs/
├── _active.md                  regenerated on every state change
├── <workflow>-<YYYYMMDD-HHMM>-<hash>/
│   ├── job.yaml                workflow, current_step, waiting-on, timestamps
│   ├── 00-state.md             the phase ledger, scoped to this job
│   ├── outputs/                what this job produced
│   └── inputs/                 references to upstream job outputs
└── _archive/<date>/<job-id>/
```

`~/.lintel/jobs/_active.md` is a thin cross-repo registry — one line per open job anywhere, each
pointing at its owning repo — which is what gives `/li:resume` and `/li:status` a "what is open
anywhere" view.

`/li:jobs list` surfaces the store. `continue <id>` resumes at the job's current step, `replan <id>`
re-runs it whole or `--from <step>`, `abort <id>` archives it with a reason, and `branch <id>` forks
a parallel job from the same starting point — useful for trying a second approach without losing the
first. `/li:status` is the shorter name for `list`.

**Gap:** job auto-spawn is dormant. The `job-begin` and `job-end` hooks exist under `hooks/shared/`
but are not among the nine hooks that auto-register (ADR-0008), so nothing creates a job folder for
you yet. Until that lands, `_active.md` may simply not exist, and `/li:status` says so rather than
inventing state. Concept doc: [concepts/jobs-system.md](concepts/jobs-system.md).

---

## Mode presets

`/li:cycle --mode <preset>` picks a phase subset and a posture instead of running all nine phases.

| Preset | Phases | Rough cost | Use when |
|---|---|---|---|
| `hotfix` | SENSE, BUILD, REVIEW, SHIP | ~5k tokens, 10-30 min | The bug is diagnosed and the fix path is clear. |
| `internal-tool` | All, with a lighter REVIEW | ~25-50k tokens, 45 min to 2 h | The default for ordinary feature work. |
| `research-dive` | SENSE, DEFINE, DISCOVER | ~10-20k tokens, 20-40 min | Explore and understand; no code yet. |
| `meta-infra` | All, with heavier REVIEW and CAPTURE | ~80-200k tokens, 2-6 h | The change modifies the harness itself. |
| `auto` | SENSE recommends, you confirm | — | You are unsure which fits. |

Set the default for your machine with `default_mode` in `~/.lintel/profile.yaml`. `--from`, `--to`
and `--skip` compose a custom subset when no preset matches; conflicting flags are surfaced rather
than silently resolved. `/li:cycle --dry-run` prints the phase chain, the gates and the budget
envelope without executing anything.

`meta-infra` is the interesting one. It is auto-detected from the paths in your working diff, and it
activates four extra gates: a structure-impact entry written during DEFINE, a mechanical
compatibility audit (`bin/li-compat-audit`, which sweeps frontmatter contracts, renames, changed
defaults and shared-helper signatures) plus the shape tests during REVIEW, and a
clarity-for-the-next-operator recap during CAPTURE. A red compatibility audit requires an explicit
override, and the override is audit-logged.

Packs can contribute their own modes with their own voice and compliance posture; the cycle merges
them into the preset list at invocation. Nothing about audience or compliance is hardcoded — see
[concepts/pack-resolver.md](concepts/pack-resolver.md).

---

## Code freeze

`/li:code-freeze <paths> --reason "<why>" --until <session|eod|1h|timestamp>` marks paths
do-not-modify for the session. Other skills read
`.claude/runtime/state/code-freeze/<session-id>.yaml` before any Edit or Write and refuse a match.
`/li:code-unfreeze` reverses it. Both actions are audit-logged.

The honest description: this is **cooperative metadata, not a filesystem lock**. It works because the
skills check it, so a raw editor or a direct tool call outside the harness is unaffected. It blocks
writes only — reads are always allowed. It is session-scoped and expires; permanent policy belongs in
a frozen-zones section of the repo instruction file instead. A `frozen-zone-warn` hook exists that
surfaces the freeze at Edit time from both sources, but it is warn-only and not auto-registered — opt
in by symlinking it.

Worth it when a refactor has surgical scope, or when the agent has already wandered once.

---

## The audit trail

Every audit record is a single JSON line written by one shared writer (`bin/_audit.sh`) into a
`<category>.jsonl` file. The trail is split in two: repo events — cycle runs, jobs, compliance gates,
hook triggers, capture — land in `<repo>/.claude/runtime/audit/`; operator events — pack lifecycle,
pack resolution, migrations, usage — stay in `~/.lintel/audit/`.

`/li:audit` reads both, repo first. It is strictly read-only.

```
/li:audit                                          every category with record counts
/li:audit --category jobs --limit 20
/li:audit --kind brief_forge_bypassed --since 7
```

`/li:hooks-status` reads `hooks.jsonl` specifically, and answers a question the raw log does not:
which hooks are actually firing, which are dead, and what overrides have been used. Every block you
override is recorded with the reason you gave.

Two caveats. First, `.claude/runtime/` is gitignored — the trail is local to your machine, and it is
not a shared or tamper-evident compliance record. Treat it as a debugging and reconstruction aid.
Second, `/li:usage-log` has a writer mode but **no automatic trigger**: nothing records skill
invocations for you, because the wrapper hook it was designed around was never built. Its reports
cover only what you logged by hand.

---

## Memory that compounds

Three files carry knowledge across sessions, all under `<repo>/.claude/memory/`:

| File | Holds | Write when |
|---|---|---|
| `lessons.md` | Rules learned from corrections | After any correction, via `/li:learn` |
| `working-state.md` | Durable cross-session state — what is in flight and why | When durable state changes |
| `personas.md` | Operator calibration | When you learn how someone actually wants to be worked with |

`MEMORY.md` alongside them is the index that loads automatically at session start. The full model is
in [concepts/memory-v2.md](concepts/memory-v2.md).

**Two budget thresholds are checked by a warning hook.** `MEMORY.md` is capped at 200 lines because native auto-load
truncates beyond that — overflow is silently invisible, which is worse than absent. Active lessons
carry a soft cap of 30. The `memory-budget-warn` hook checks both after edits, rate-limited to once
per hour, and both caps are overridable by environment variable. When you hit the lessons cap the
answer is consolidation, not a bigger cap: if the same shape of correction keeps recurring, the rule
is wrong or it is not surfacing early enough.

**Habits that make lessons actually compound:**

- Write the rule, not the incident. "Never force-push a shared branch" beats "yesterday I broke the branch."
- Supersede rather than delete. A retired lesson keeps its entry and gains a `superseded_by:` pointer, so the reasoning survives.
- Run `/li:lessons-surface <topic>` before starting, not after finishing. A lesson read at the end of a task is a post-mortem, not a guardrail.
- Personas are for people you have actually worked with. Do not write one for a hypothetical reader.

**Two lessons tools that are not interchangeable:**

- `bin/li-lessons-promote` lifts a repo-local lesson into the scaffolding baseline, so every repo scaffolded afterwards inherits it. Use it when the lesson is about how software gets built, not about this codebase.
- `bin/li-lessons-sync` syncs **your own** lessons across your machines through a personal remote. Opt-in and private to you.

Promoting a lesson that only applies to one repo pollutes every future repo. Syncing one that should
have been promoted leaves every other repo without it.

---

## Where this is thin

Naming these is cheaper than you discovering them:

- **Lintel's hook bundle targets Claude Code.** Copilot has a native hook API, but this release does not adapt the bundle. Treat unregistered checks as instructions and validate mandatory controls independently.
- **Job auto-spawn is dormant.** `/li:jobs` and `/li:status` read a store nothing populates automatically yet.
- **Context budget numbers are estimates**, summed from an event log rather than read from the CLI.
- **Cooling cannot actually shrink the window.** Only a save, restart and restore round trip does.
- **`/li:usage-log` has no automatic trigger.** What it reports is what you logged by hand.
- **`/li:code-freeze` is cooperative**, enforced by the skills that check it, not by the filesystem.
- **The default pack ships no roles.** The role machinery works; the content is yours to write.
- **The audit trail is local and gitignored.** It is not a shared compliance artifact.
- **Lintel does not install, vendor, or update third-party tools.** The installer copies Lintel's own files and nothing else. There is no uninstall script; removal means deleting `~/.lintel/` and the plugin.

---

## When to skip all of this

Some work genuinely does not benefit: a throwaway exploration repo, a spike that dies next week, a
data-analysis notebook with no production target. If the work has no audit-trail requirement and no
need for cross-session memory, the scaffolding is overhead. Use judgment — nothing here is
load-bearing for a single-session task.

---

**Related:** [architecture.md](architecture.md) for where state lives and why ·
[the-cycle.md](the-cycle.md) for the phases · [precedence.md](precedence.md) for which instruction
wins when two conflict · [../skills/CATALOG.md](../skills/CATALOG.md) for the full skill list ·
[README.md](README.md) for the documentation index.
