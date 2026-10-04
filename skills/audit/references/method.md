# Audit and hook observations

Audit owns this read-only procedure, shared by `audit`, `hooks-status` and
maintenance's usage view. The existing `_audit.sh` router owns log selection;
`li-events.py` owns parsing, classes, aliases, counts and diagnostics. Do not add
another JSONL schema, telemetry service or activation policy.

## What this skill does

Every Lintel audit record lands in `<category>.jsonl` via the unified `audit_log` writer in `bin/_audit.sh`. Since v5 the trail is split in two: repo events (cycle runs, jobs, brief-forge, granularity, …) land in `<repo>/.claude/runtime/audit/<category>.jsonl`; operator events (pack lifecycle, pack-resolver, migrations, `usage-*`) stay in `~/.lintel/audit/<category>.jsonl`. The writer's own router decides which: this reader asks `audit_read_files <category>` for the write file and, when it differs, the legacy global file, reads the first that exists and names any later one it did not read. Each record is a single JSON line with the shape:

```json
{"ts":"...","kind":"...","operator":"...","cycle_id":"...", ...extra k=v fields...}
```

This skill reads those logs through the structured reader `bin/li-events.py`, so counts, classes and malformed-line diagnostics come from one parser instead of hand-grepped JSONL. It never writes — pure read. A missing record is unobserved, not proof that nothing happened.

## When to use

- "What's in the audit trail?" — no args, lists every category + record count
- "Show me the jobs audit" — `--category jobs`
- "Is there a brief-forge bypass record this week?" — `--kind brief_forge_bypassed --since 7`
- After a meta-infra change — confirm the expected override/pack-resolver events landed

## When NOT to use

- To WRITE audit records — that's `audit_log` in `bin/_audit.sh`, called by the producing code
- For current work status — use `/li:status` (selected work/cycle authority, with job records only as supplementary observations)
- For git history — this is Lintel's internal event trail, not VCS

## Inputs

All optional:

- `--category <name>` — restrict to one log file (e.g. `jobs`, `pack-resolver`, `brief-forge`, `alias-resolution`, `hooks`). Default: all categories.
- `--kind <kind>` — filter records by their `kind` field (e.g. `job_begin`, `brief_forge_bypassed`).
- `--since <N>` — only records from the last N days, using the router's computed
  window and the reader's timestamp parser; an invalid window is never dropped.
- `--limit <N>` — cap output lines (default 50).

## Shared read

Select explicitly authorized repository/operator log roots first. The historical
`~/.lintel/audit/` spelling below denotes the configured operator store, not
permission to search a real personal home. Read-only observation does not authorize
exporting raw URLs, private content or audit history.

Use [read.sh](read.sh) with the existing audit flags as literal arguments:

```bash
bash "${LINTEL_SOURCE_ROOT:?select trusted source}/skills/audit/references/read.sh" "$@"
```

The route reads the first existing `audit_read_files <category>` path and names every
later existing path not read. With no category it inventories the router's repository
and operator directories. It never merges legacy files silently. Missing/invalid
arguments and uncomputable windows stop instead of dropping a filter.

It returns the actual `summary` JSON and, for filtered requests, a bounded preview of
`records`. `--limit` limits only displayed rows; all diagnostics and counts remain in
the summary. A truncated preview is not a complete population for manual aggregation.
If rows change between the two reads, report that limitation rather than claiming an
atomic snapshot. Use the selected source/time and retain all reader exits:

- 0: observed records; still no enforcement or completion claim.
- 3: unobserved/empty selection, including missing logs.
- 4: reader diagnostics; report their line/code/detail, separately from records.
- Other nonzero: error/unavailable; preserve it, not a successful partial read.

Render selected/valid/malformed counts from `summary.records`, not line counts or
grep. Records preserve `line`, `kind`, `ts`, `class`, `check`, raw string `fields`
and alias-normalized values. Diagnostics include malformed JSON, duplicate keys,
unknown kinds, undated records and incomplete tails; do not count them as executions.

`audit_count` in `bin/_audit.sh` stays an approximate bash line counter for quick shell checks
(it returns 3 with `unobserved:` on stderr when no listed log exists); the counts above come from
the structured reader.

## Hook views

`hooks-status` retains `--records`, `--overrides`, `--unobserved` and `--days N`.
These select a report, not extra `li-events.py` flags. No view supplied means ask for
one (`NEEDS_CONTEXT`), not a guessed health result. Read category `hooks` through the
shared route; translate `--days N` to its supported `--since N`. For `--overrides`
without an explicit window, use seven days. Name the actual window; other unspecified
windows mean all available records, not a secretly chosen default.

```bash
hook_args=(--category hooks)
[ -z "${days:-}" ] || hook_args+=(--since "$days")
bash "$LINTEL_SOURCE_ROOT/skills/audit/references/read.sh" "${hook_args[@]}"
```

Before per-hook aggregation, obtain all selected rows, not just the default preview.
Use the actual summary's `records.lines` as `--limit <N>` on the same category/window
when the preview was truncated; report an unstable/changing input as incomplete.
No rows means unobserved, not a reason to manufacture counts or a positive verdict.

Use only real producer fields: `hook`, `tier`, `blocked`, `reason`, and string
`override: "true"`; there is no `hook_name`, `override_reason` or `run_id`.

- **`--records`:** group observed rows by `fields.hook`, with count, tier,
  class/check and last timestamp. Keep `block_decision` / `check: not_performed`
  (such as `scanner-unavailable`) separate from checks that actually ran.
- **`--overrides`:** select class `override` / `fields.override == "true"`, then group
  by hook and reason. More than five per hook over seven days is the retained advisory
  friction signal, not a safety verdict or measured tuning threshold.
- **`--unobserved`:** compare the trusted source's `hooks/shared/` names with observed
  rows in the requested window. Use `lib/event-catalog.json` `records_when` and
  `non_recording_hooks` to explain gaps. No record means **unobserved**, not disuse.

Hooks record only certain findings, blocks, overrides, failures and the session digest's
own observation. Clean passes often record nothing, `context-bloat-warn` records nothing,
and a failed log write may only warn or have its warning discarded. Derive current
inventory/registration declarations from the source, not a stale fixed hook count.
A block decision is not proof the host enforced it. Installation, symlinks, settings
and historical rows do not prove current registration, activation or execution.

For installed-byte observations, consume an actually obtained doctor JSON using the
existing `li-events.py installer --file <doctor.json>`. Keep its activation/registration/
execution fields unverified. [Doctor's inspection owner](../../doctor/references/inspection.md)
obtains that result; do not run an installer/repair to answer a historical-record question.

Render the source path, window, coverage/preview limitation and every diagnostic.
`DONE` means report rendered; diagnostics mean `DONE_WITH_CONCERNS`, unreadable
sources/windows mean `BLOCKED`. This status is not gate or delivery clearance.
Usage correlation, if explicitly requested, goes through the same audit reader and
uses only `cycle_id` and time-window overlap as hints, never causation.

## Integration

**Reads:**
- `<category>.jsonl` from `audit_read_files <category>`: the write file (repo events on the v5
  layout) and, when it differs, the legacy global `~/.lintel/audit/<category>.jsonl`

**Writes:**
- nothing (pure read)

**Calls into:**
- `bin/_audit.sh` router (`audit_dir`, `audit_read_files`) and `audit_days_ago`
- `bin/li-events.py` (counts, classes and diagnostics; exits 3 and 4 are data outcomes)

## Anti-patterns

- **Editing the .jsonl logs by hand** — they're append-only event trails. Don't rewrite history.
- **Treating observations as clearance** — use the applicable review, profile and host-control contracts; this forensic reader neither grants permission nor proves a hook ran.
- **Re-implementing the JSON shape elsewhere** — the schema is owned by `bin/_audit.sh`. Read it through this skill.

## See also

- `bin/_audit.sh` (the unified writer — `audit_log <category> <kind> [k=v ...]`)
- `/li:status` (read-only selected-work and cycle observations, not an audit-derived task authority)
- `/li:jobs` (the jobs lifecycle controller — produces `jobs.jsonl` records)
- `tests/shape/audit-writes-via-helper.sh` (guard: no inline JSONL writers bypass the helper)
