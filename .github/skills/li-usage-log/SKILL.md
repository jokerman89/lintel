---
name: li-usage-log
description: Use to record an explicitly requested invocation or inspect authorized usage records through the shared audit reader; missing records do not prove disuse and estimates are not billed usage.
---

> **Lintel on GitHub Copilot.** Generated from `skills/usage-log/SKILL.md`; edit the canonical file, then run
> `li-copilot init`.
> - **Resource root:** `../../..` from this skill's base directory (the Lintel source with `bin/`,
>   `lib/`, `skills/`). Write plans, state and evidence into the working repository's `.claude/`
>   tree, never into the resource root.
> - **Skill-relative paths:** this skill's own `scripts/`, `references/` and `data/` folders (and a
>   `<base>` that the workflow defines as its own directory) mean
>   `../../../skills/usage-log/` in the Lintel source, not this generated folder.
>   `${LINTEL_SKILLS_DIR:-skills}` means the skills root, `../../../skills`. A `bin/li-run` step
>   runs in the working repository, so use `$LINTEL_SKILLS_DIR/usage-log/` there.
> - **Shell steps:** run Bash snippets with Bash (Git for Windows' `bash.exe` on Windows, never
>   `System32\bash.exe`). Save a snippet to a temporary `.sh` file and run
>   `bash "<resource root>/bin/li-run" <file>`; it prepares `LINTEL_SOURCE_ROOT`, `LINTEL_REPO_ROOT`
>   and the profile context.
> - **Tools:** Read=`view`, Write=`create`, Edit=`edit`, Bash=`bash`/`powershell`, Grep=`grep`,
>   Glob=`glob`, AskUserQuestion=`ask_user`, TodoWrite=the plan checklist, Task or a named role=`task`
>   with that custom agent, WebFetch=`web_fetch`.
> - **Other Lintel workflows** are native skills: invoke `/li-<name>` rather than reading their
>   files. Named roles such as `CodeReviewer` are custom agents.

You are the `usage-log` skill — the observation foundation under maintenance, token budgeting, hook audit, and low-observed-usage review.

## What this skill does

Two modes:

**Writer mode (manual, operator-invoked):** records one JSONL line per invocation the operator wants counted, via the unified audit writer. There is NO automatic at-skill-invocation trigger — nothing fires this for you (the wrapper-hook this was originally designed around was never built):

```bash
export LINTEL_SOURCE_ROOT="${LINTEL_SOURCE_ROOT:-${CLAUDE_PLUGIN_ROOT:?trusted Lintel source root unavailable; set LINTEL_SOURCE_ROOT}}"
source "$LINTEL_SOURCE_ROOT/bin/_audit.sh" || exit $?
audit_log usage-skill invocation skill=<name>     # optional: mode=<mode> tokens_est=<n> cli=<cli>
```

→ appends to `$(audit_file usage-skill)`, the operator-global `usage-skill.jsonl` (`usage-*` categories always route operator-global — see `bin/_audit.sh`).

**Reader mode (solo-invokable for reports):** reads existing usage records, surfaces top-skills + frequency + estimated token spend per skill family. Pairs with `/li-hooks-status` (siblings in the observation spine). Absent or low recorded usage is reported as unobserved or low observed usage — never as a verdict that a skill is unused.

These records support `/li-maintenance` and explicit operator-selected comparisons
with `/li-catalog --kind=all` metadata. The catalog does not consume them as a built-in
trend overlay; absent records remain unobserved rather than zero usage.

## When to use

- **Writer mode:** the operator (or a skill the operator instructs) wants an invocation counted — run the one-liner above.
- **Reader mode:** "what have I used most over the past week?" → `/li-usage-log --report --days 7`
- Maintenance pre-flight: `/li-usage-log --report --topn 10` shows low observed usage (skills with <2 recorded invocations per month)
- Token-budget debugging: `/li-usage-log --tokens-by-skill` aggregates token-est per skill

## When NOT to use

- Real-time telemetry — this is append-only, not streaming
- Broader audit investigation — use `/li-audit` with the relevant categories; no single log is the whole audit trail
- Per-invocation token-counting — this estimates (tokens_est is a heuristic, not OpenAI-counted)

## Schema (per JSONL line)

`audit_log` writes the unified envelope; the one-liner's k=v args add the usage fields:

```json
{
  "ts": "2026-06-13T14:23:45Z",
  "kind": "invocation",
  "operator": "<operator>",
  "cycle_id": "<cycle id or unknown>",
  "skill": "cycle",
  "mode": "research-dive",
  "tokens_est": "3500",
  "cli": "claude-code"
}
```

**Field spec:**
- `ts` / `kind` / `operator` / `cycle_id` — supplied by the `audit_log` envelope
- `skill` — frontmatter `name:` value (the one required k=v)
- `mode` — invocation mode if relevant ("full", "brief", "section:<x>") — optional
- `tokens_est` — heuristic estimate (input + output, not cached) — optional
- `cli` — claude-code | codex | cursor | copilot-cli — optional

## Workflow

### Step 1 — Writer mode (manual)

Run the one-liner from "What this skill does". That is the whole writer — no script, no hook:

```bash
export LINTEL_SOURCE_ROOT="${LINTEL_SOURCE_ROOT:-${CLAUDE_PLUGIN_ROOT:?trusted Lintel source root unavailable; set LINTEL_SOURCE_ROOT}}"
source "$LINTEL_SOURCE_ROOT/bin/_audit.sh" || exit $?
audit_log usage-skill invocation skill=cycle mode=research-dive tokens_est=3500 cli=claude-code
```

### Step 2 — Reader mode (solo-invokable)

Follow the [shared audit read method](../../../skills/audit/references/method.md#shared-read).
Select authorized log roots and the actual time window; no personal-home scan is
implied. Retain the shared reader's empty/diagnostic/error distinctions.

```bash
usage_args=(--category usage-skill)
[ -z "${days:-}" ] || usage_args+=(--since "$days")
bash "${LINTEL_SOURCE_ROOT:?select trusted source}/skills/audit/references/read.sh" "${usage_args[@]}"
```

The shared router selects the current/legacy category files and names paths not
read. An explicitly selected older dated log can be inspected with the existing
`li-events.py records --file <path> --category usage-skill` operation; do not glob
or silently combine every personal log. Obtain the complete selected rows before
aggregating: a bounded preview is not the full population. Surface:
- **Top N skills by frequency** (`--topn 10 --days 7`)
- **Token spend by skill family** (`--tokens-by-skill`)
- **Low observed usage** (fewer than 2 recorded invocations in 30 days — review candidates only; unrecorded use is unobserved, not disuse)
- **Override-pattern correlation** (cross-reference with hooks.jsonl override-counts)

These are manual report selections over actual reader rows, not additional
`li-events.py` flags or automatic telemetry. Keep the chosen log/window, missing
fields and record count visible; estimates are not exact billed tokens.

If no records exist, name the selected paths/window and report that usage was not
observed; the writer is manual. Never invent counts or call malformed records
successful executions.

## Integration

**Writes (writer mode):**
- `$(audit_file usage-skill)` — operator-global `usage-skill.jsonl` (append, one line per recorded invocation, via `audit_log`)

**Reads (reader mode):**
- Explicitly authorized usage category files through the shared audit reader
- Explicitly selected hook records through that same reader, only if correlation was requested

**Consumed by:**
- `/li-maintenance` through its shared audit route; absent measurements remain unobserved
- Operator-selected joins with `/li-catalog --kind=all` metadata; no built-in trend overlay
- `/li-hooks-status` through the same observation owner
- Operator (solo-report invocation)

## Anti-patterns

- **Bespoke per-skill `>>` writers** — duplicate the shared writer and skip its ts/operator/cycle_id envelope. The `audit_log usage-skill ...` one-liner remains the writer.
- **Claiming automatic capture** — there is no wrapper-hook; records exist only when someone ran the one-liner. Reports must say so.
- **Token-counting "exactly" via the OpenAI API** — out of scope. The heuristic IS the tokens_est field.
- **Treat one log as the complete audit or a cause** — use actual selected categories and distinguish temporal correlation from causation.

## Failure recovery

- Append fails (permission, disk-full, a path that is not a directory): `audit_log` warns on stderr and returns 0 — observation never blocks work. Some hooks discard that stderr, so a missing record stays unobserved rather than meaning the invocation did not happen.
- Reader-report empty (no records yet): surface "No usage records observed. The writer is manual — `audit_log usage-skill invocation skill=<name>`."

## Recommended next steps after invocation

- For full observation: pair with `/li-hooks-status` (sibling skill)
- For maintenance: `/li-maintenance` uses this as a data source (if usage records exist)
- For metadata context: `/li-catalog --kind=all` lists declarations; any requested
  comparison with recorded usage is explicit and does not classify unobserved entries as unused
