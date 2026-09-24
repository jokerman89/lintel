---
name: hooks-status
layer: foundation
description: Reader for hooks.jsonl — per-hook observed records, override patterns and hooks with no observed record in a window, read through the structured event reader. Absence stays unobserved.
color: yellow
tools: Read, Write, Bash, Glob
voice: internal
cli_support:
  - cli: claude-code
    level: full
  - cli: codex
    level: degraded
---

You are the `hooks-status` skill — reader for the `hooks` audit category. It reports what the
hook producers actually recorded and keeps unrecorded activity unobserved.

## What this skill does

Lintel ships 33 hooks, 9 of them auto-registered on a plugin install. Hooks record only some
outcomes: findings, blocks, overrides and failures (for example an unavailable scanner), plus
the session digest's own observation. Clean passes write nothing, `context-bloat-warn` never
records, a failed write only warns, and some hooks discard that warning. This skill therefore:

1. Counts observed records per hook, with the catalog's `class` and `check` for each
2. Surfaces override patterns ("customer-data-block overridden 6× this week" is worth a look)
3. Lists hooks with **no observed record in the window**, with what each would record and when
4. Keeps block decisions separate from proof: a `block_decision` record means a hook decided to
   block; enforcement depends on the host honoring its exit code

## When to use

- "Which hooks left records?" → `/li:hooks-status --records --days 30`
- "Have I overridden too much?" → `/li:hooks-status --overrides`
- "Which hooks have no observed record?" → `/li:hooks-status --unobserved --days 90`
- Maintenance pre-flight: combine with `/li:usage-log --report` for a full observation pass

## When NOT to use

- Real-time hook-execution detection — this is retroactive and reads records after the fact
- Hook installation state — the integrated doctor (`bin/li-doctor --json`, which runs
  `li-lifecycle doctor`) compares installed hook bytes and reports only whether the hooks log
  exists. Read its JSON through `bin/li-events.py installer --file <doctor.json>`, which keeps
  registration, hook execution and host activation `unverified`. Registration, symlinks and
  settings are activation observations, not evidence that a hook ran

## Workflow

### Step 1 — Resolve and name the log

Read the first existing file from the shared router, name it, and report any later listed
file that also exists (pre-migration history is never hidden silently):

```bash
source "${LINTEL_SOURCE_ROOT:?select trusted source}/bin/_audit.sh"
log=""
while IFS= read -r candidate; do
  if [ -z "$log" ]; then [ -f "$candidate" ] && log="$candidate"
  elif [ -e "$candidate" ]; then echo "Also present, not read: $candidate" >&2; fi
done < <(audit_read_files hooks)
if [ -z "$log" ]; then
  echo "No hook records observed in: $(audit_read_files hooks | paste -sd ' ' -)."
  echo "Absence is not evidence that hooks did not run."
  exit 0
fi
echo "Reading: $log"
```

### Step 2 — Read it through the structured reader

`bin/li-events.py` parses, classifies and diagnoses; never grep the JSON by hand. Exits 3 and 4
are data outcomes, so do not run the reader under `set -e`:

```bash
since=""
if [ -n "${days:-}" ]; then
  since="$(audit_days_ago "$days")" || {
    echo "The window start could not be computed; stopping instead of reading all history."; exit 2; }
fi
rc=0
rows="$(python3 "$LINTEL_SOURCE_ROOT/bin/li-events.py" records --file "$log" --category hooks \
  ${since:+--since "$since"})" || rc=$?
case "$rc" in
  0|3|4) ;;   # 3: nothing selected; 4: records plus diagnostics — report both
  *) echo "li-events could not read $log (exit $rc)"; exit "$rc" ;;
esac
```

Each JSONL row is either a record — `line`, `kind`, `ts`, `class`, `check`, raw string `fields`
and alias-`normalized` values — or a diagnostic line (`malformed_json`, `duplicate_key`,
`unknown_kind`, `undated`, `incomplete_tail`, …). List diagnostic lines separately; never fold
them into a count.

### Step 3 — Aggregate per requested view

Use the producers' actual fields: `hook`, `tier`, `blocked`, `reason` and the string
`override: "true"`, with each record's `class` and `check`. There is no `hook_name`,
`override_reason` or `run_id` field.

**`--records --days N`:**
- Group records by `fields.hook`; per hook show count, `tier`, `class`/`check` and last `ts`
- Show `block_decision` records with `check: not_performed` (for example
  `reason: scanner-unavailable`) apart from blocks whose scan ran

**`--overrides`:**
- Select records whose `class` is `override` (`fields.override == "true"`)
- Group by `fields.hook` + `fields.reason`: "hook X overridden N× (reasons: ...)"
- Flag if N > 5 for any hook in the past 7 days (signals friction)

**`--unobserved --days N`:**
- For every directory under the trusted source's `hooks/shared/` without a record in the window,
  report **"no observed record in window"** and what it records, from `lib/event-catalog.json`:
  the kind's `records_when` (for example `finding`, `block`, `override`, `unavailable`)
- Name the catalog's `non_recording_hooks` (such as `context-bloat-warn`) as writing no records
  by design
- Report registration, symlinks and settings as activation observations only

### Step 4 — Render report

Markdown table output to stdout. State the log that was read, the window, the diagnostics and
that absence is unobserved. Operator pipes to less or redirects to a file.

## Status protocol

- **DONE** — report rendered
- **DONE_WITH_CONCERNS** — report rendered with reader diagnostics (malformed, duplicate-key,
  unknown-kind, undated or truncated lines are listed, never skipped silently)
- **BLOCKED** — the reader exits 2 (unreadable log or catalog) or the window cannot be computed
- **NEEDS_CONTEXT** — invocation without a view flag (`--records` / `--overrides` / `--unobserved`)

## Integration

**Reads:**
- The `hooks` category through `audit_read_files hooks` (repo-scoped on the v5 layout)
- `lib/event-catalog.json` (`records_when`, classes and `non_recording_hooks`)
- `hooks/shared/` directory scan (which hooks exist; not whether they ran)
- Optional: the integrated doctor's JSON through `bin/li-events.py installer` (installed hook
  bytes and P10 installer state; host activation, registration and execution `unverified`)
- Optional: `usage-*.jsonl` via `/li:usage-log` — correlate only by `cycle_id` and time window,
  as a hint, never as causation

**Writes:**
- stdout (markdown report)

**Consumed by:**
- Operator (solo-invocation pattern)
- `/li:maintenance` (5.3 — observation data)

## Anti-patterns

- **Modifying hooks.jsonl** — this is reader-only. The audit log is append-only.
- **Turning absence into a verdict** — no record means unobserved, not "did not run".
- **Streaming live records** — this processes batches.

## Failure recovery

- Reader diagnostics: list each line number and code at the end of the report.
- No log in any listed path: "No hook records observed in <paths>; absence is not evidence that
  hooks did not run."
- Window start not computable: report it and stop rather than reading all history silently.

## Recommended next steps after invocation

- For the full picture: pair with `/li:usage-log --report` (sibling skill)
- On an override spike: surface to operator decision on whether hook-tuning is needed
- On a hook with no observed record: `bin/li-doctor --target <repo> --json` shows installed hook
  bytes; read it through `bin/li-events.py installer`. Registration, activation and execution stay
  `unverified` and need their own evidence before any cleanup decision
