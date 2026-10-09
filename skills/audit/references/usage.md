# Usage observations

This reference preserves the manual writer and reader method formerly exposed by
`usage-log` without making usage a separate public skill, automatic telemetry
source or complete audit of operator activity.

## Manual recording

Only record an invocation when the operator explicitly requests it. Use the
existing audit producer and envelope; do not append JSONL directly or add a
second writer:

```bash
source_root="${LINTEL_SOURCE_ROOT:-${CLAUDE_PLUGIN_ROOT:-}}"
[ -n "$source_root" ] && [ -f "$source_root/bin/_audit.sh" ] || {
  echo 'NEEDS_CONTEXT: trusted audit source root unavailable.' >&2; exit 2;
}
LINTEL_SOURCE_ROOT="$(cd "$source_root" && pwd -P)" || exit 2
export LINTEL_SOURCE_ROOT
source "$LINTEL_SOURCE_ROOT/bin/_audit.sh" || exit $?
audit_log usage-skill invocation skill=cycle mode=research-dive tokens_est=3500 cli=claude-code
```

`skill` is the required observed skill name; `mode`, `tokens_est` and `cli` are
optional and should be included only when supplied or observed. The writer is
manual, not a skill-invocation hook. `tokens_est` is a heuristic, not billed
usage. Its advisory write failure may warn while returning success; a missing
record is unobserved, not proof an invocation did not happen.

## Read reports

The audit skill's `--usage` view retains the former report selections:
`--report`, `--days <N>`, `--topn <N>` and `--tokens-by-skill`. These are
skill-level report choices, not flags accepted by `li-events.py` or `read.sh`.
Translate `--days N` to the shared reader's `--since N`; apply `topn` only to the
displayed aggregate and token aggregation only to actual `tokens_est` values.

Follow the [shared audit read method](method.md#shared-read). Select only
authorized roots, then read through the existing reader:

```bash
usage_args=(--category usage-skill)
[ -z "${days:-}" ] || usage_args+=(--since "$days")
bash "${LINTEL_SOURCE_ROOT:?select trusted source}/skills/audit/references/read.sh" \
  "${usage_args[@]}"
```

The reader selects the current/legacy category file according to `_audit.sh`,
names a later existing file it did not read, and reports actual summary counts
and diagnostics. Do not glob or silently combine logs. An explicitly selected
older file can be read with the same bounded
`usage_stream.py --file <path>` operation; never
search all dated or personal logs implicitly.

For `usage-skill`, the shared route delegates to the bounded
[streaming usage method](usage_stream.py). It reuses `li-events.py`'s catalog,
single-line parser and classifier, never its whole-file materialization.
Its JSON keeps every `li-events.py summary` key with the same type and
meaning (`source:{path,state}`, `by_kind`, `evidence`, `verification`,
`enforcement` and absent/unreadable/invalid-window error summaries) and adds
`processing`, `usage`, diagnostic counts/codes and the bounded preview.
Only `diagnostics` detail is capped at 50 entries; `diagnostic_count` and
`diagnostics_omitted` keep the totals. Top-level `diagnostics`, `status` and
the exit code follow the legacy parser semantics exactly: a valid record
without optional `tokens_est` stays `observed`/exit 0. Usage-only findings
(`missing_skill`, `skill_bound`, `missing_tokens_est`, `invalid_tokens_est`)
are additive under `usage.diagnostics`/`usage.diagnostic_codes` and set
`usage.aggregate_complete` to false. A file that exists but cannot be opened or
read is `source.state: unreadable` with a `cannot read …` error summary, exit 2.
`--limit` caps detailed preview before retention (at most 50 rows and 64 KiB).
Before aggregating all rows, inspect `processing.complete` and
`usage.aggregate_complete`; do not request the entire population as a preview.
The scan stops at 8 MiB or 100,000 physical lines, parses at most 64 KiB per
line, and retains at most 1,024 skill keys of at most 256 characters. Oversized
lines are drained in bounded chunks, excluded from aggregates and diagnosed.
Unprocessed input and omitted details are explicitly incomplete; totals are
only for processed usable rows, never a complete total after a bound or error.
Retain selected source, window, counts and diagnostic/omission information.

The route displays the top 20 skills by count with estimated token totals.
For another authorized `--topn N` selection (1 through 50), use the same
streaming method with the exact selected file and computed window:

```bash
python3 -B "$LINTEL_SOURCE_ROOT/skills/audit/references/usage_stream.py" \
  --file "$selected_usage_file" --topn "$topn" --limit 50
```

Pass any actual `--since` ISO window and `--kind` filter unchanged. The helper
caps diagnostics at 50 entries while reporting totals by code and omitted count;
missing/invalid estimates are diagnosed rather than fabricated. Source changes
during a read remain a coverage limitation, not an atomic snapshot.

For rows with missing or empty `fields.skill`, exclude the row from all
per-skill counts and token aggregates; surface its selected source and line as
incomplete input. Do not crash, invent a skill name or silently claim complete
coverage. Keep these rows in the reader's raw summary counts and diagnostics;
the reporting exclusion does not rewrite the log or change the shared parser.

For `--report` or `--topn N`, count observed rows by their actual `fields.skill`,
sort by count and limit the displayed result. For `--tokens-by-skill`, sum only
numeric `fields.tokens_est` values by skill and disclose missing or malformed
values; these remain estimates. Low observed usage is only a review prompt
(historically fewer than two recorded invocations in 30 days), never a verdict
that a skill is unused. Do not infer skill-family classification, causes, exact
token totals, billing or a usage rate without the relevant data.

If override-pattern correlation is explicitly requested, use the existing
`/li:hooks-status --overrides` view for its selected window. Compare observed
counts only as temporal/`cycle_id` correlation hints, never as causation. No
report selection enables automatic capture or a catalog trend overlay.

No records or an absent log means **unobserved/coverage unknown**. Preserve
malformed-line diagnostics and distinguish reader exits 3 (unobserved), 4
(diagnostics), and other errors from observed records. The reader is read-only;
manual recording remains a separate, explicitly requested operation.

## Retired maintenance routes

The former `maintenance` public front is retired. These flags now identify an
intent and its existing owner; they are not compatibility aliases or arguments
to the receiving helper:

| Former maintenance option | Receiving owner and supported route | Preserved boundary |
|---|---|---|
| `--force-compact` | [Context budget](../../context-budget/SKILL.md#advice---advice), `--advice` with the preserved numeric advice and observed-usage flags | Advisory checkpoint/working-set advice only; cannot compact a conversation or activate a watcher. |
| `--monitor-paths` | [Doctor](../../doctor/SKILL.md), `--layers-only` through its actual inspection procedure | Returns the doctor's real observations and complete exit; missing/failed required checks remain incomplete. No background monitor or repair. |
| `--simulate-tokens <workflow>` | [Context budget](../../context-budget/SKILL.md#shared-observation-and-interpretation), using an actual `--bytes <N>` selection or `--handoff --map <work.json>` | The workflow string is a report label, not a prediction input; missing selection/observations stay unknown. |
| `--rust-report` | [Audit usage view](../SKILL.md) with `--usage --report --days <N> --topn <N>` or `--tokens-by-skill` | Only explicitly authorized recorded rows; absent/partial data is unobserved, never disuse or permission for cleanup. |

All four routes are read-only/advisory. They do not authorize archiving,
deletion, profile changes or a global sink. Age or partial usage never implies
cleanup is safe; any later disk operation needs exact owned paths and separate
authority. Report storage changes only after observing them, and do not claim
active-context reclamation without actual host evidence.
