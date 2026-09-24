---
name: audit
layer: foundation
description: Read the unified Lintel audit trail — surface .claude/runtime/audit/ (repo events) and ~/.lintel/audit/ (operator events) <category>.jsonl records with optional category / kind / since-days filters. Read-only.
color: yellow
tools: Read, Bash
voice: internal
cli_support:
  - cli: claude-code
    level: full
  - cli: codex
    level: full
---

You are the `audit` skill — read-only window onto the unified Lintel audit trail (v4.0 Phase 1).

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
- For in-flight job status — use `/li:status` (reads `_active.md`, not the audit log)
- For git history — this is Lintel's internal event trail, not VCS

## Inputs

All optional:

- `--category <name>` — restrict to one log file (e.g. `jobs`, `pack-resolver`, `brief-forge`, `alias-resolution`, `hooks`). Default: all categories.
- `--kind <kind>` — filter records by their `kind` field (e.g. `job_begin`, `brief_forge_bypassed`).
- `--since <N>` — only records from the last N days (ISO-8601 string compare on `ts`).
- `--limit <N>` — cap output lines (default 50).

## Workflow

```bash
source "${LINTEL_SOURCE_ROOT:?select trusted source}/bin/_audit.sh"
reader() { python3 "$LINTEL_SOURCE_ROOT/bin/li-events.py" "$@"; }

category=""
kind=""
since=""
limit=50
while [ $# -gt 0 ]; do
  case "$1" in
    --category) category="$2"; shift 2 ;;
    --kind)     kind="$2";     shift 2 ;;
    --since)    since="$2";    shift 2 ;;
    --limit)    limit="$2";    shift 2 ;;
    *) echo "Usage: /li:audit [--category <c>] [--kind <k>] [--since <days>] [--limit <n>]"; exit 2 ;;
  esac
done

# A window that cannot be computed is reported; the filter is never silently dropped.
since_iso=""
if [ -n "$since" ]; then
  since_iso="$(audit_days_ago "$since")" || {
    echo "Cannot compute the date $since days ago; no records are shown instead of unfiltered history."
    exit 2
  }
fi

# Categories: the requested one, or every <category>.jsonl in the writer's repo and
# operator directories (the router's answer, not a second routing copy).
if [ -n "$category" ]; then
  categories=("$category")
else
  mapfile -t categories < <(for d in "$(audit_dir hooks)" "$(audit_dir pack-resolver)"; do
    for f in "$d"/*.jsonl; do [ -f "$f" ] && basename "$f" .jsonl; done
  done | sort -u)
fi
if [ "${#categories[@]}" -eq 0 ]; then
  echo "No records observed in $(audit_dir hooks) or $(audit_dir pack-resolver); absence is not evidence that nothing ran."
  exit 0
fi

filters=()
[ -n "$kind" ] && filters+=(--kind "$kind")
[ -n "$since_iso" ] && filters+=(--since "$since_iso")
for c in "${categories[@]}"; do
  log=""
  while IFS= read -r candidate; do
    if [ -z "$log" ]; then [ -f "$candidate" ] && log="$candidate"
    elif [ -e "$candidate" ]; then echo "- $c: also present, not read: $candidate"; fi
  done < <(audit_read_files "$c")
  if [ -z "$log" ]; then
    echo "- $c: no records observed in $(audit_read_files "$c" | paste -sd ' ' -); absence is not evidence that nothing ran"
    continue
  fi
  rc=0
  summary="$(reader summary --file "$log" --category "$c" "${filters[@]}")" || rc=$?
  case "$rc" in
    0|3|4) ;;   # data outcomes; 4 means records and diagnostics both exist
    *) echo "- $c: the reader could not read $log (exit $rc)"; continue ;;
  esac
  # Counts come from the reader; malformed and other diagnostic lines are listed separately.
  python3 - "$c" "$summary" <<'PY'
import json, sys
name, summary = sys.argv[1], json.loads(sys.argv[2])
counts = summary["records"]
print("- {}: {} selected of {} valid records, {} malformed, in {} ({})".format(
    name, counts["selected"], counts["valid"], counts["malformed"], summary["source"]["path"],
    summary["status"]))
for item in summary["diagnostics"]:
    print("  - line {}: {} ({})".format(item["line"], item["code"], item["detail"]))
PY
  if [ -n "$category" ] || [ -n "$kind" ] || [ -n "$since" ]; then
    reader records --file "$log" --category "$c" "${filters[@]}" | grep -v '"diagnostic"' | head -n "$limit"
  fi
done
```

`audit_count` in `bin/_audit.sh` stays an approximate bash line counter for quick shell checks
(it returns 3 with `unobserved:` on stderr when no listed log exists); the counts above come from
the structured reader.

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
- **Using this to drive control flow** — it's a forensic reader, not a gate. Gates live in hooks.
- **Re-implementing the JSON shape elsewhere** — the schema is owned by `bin/_audit.sh`. Read it through this skill.

## See also

- `bin/_audit.sh` (the unified writer — `audit_log <category> <kind> [k=v ...]`)
- `/li:status` (in-flight jobs, reads `_active.md` not the audit log)
- `/li:jobs` (the jobs lifecycle controller — produces `jobs.jsonl` records)
- `tests/shape/audit-writes-via-helper.sh` (guard: no inline JSONL writers bypass the helper)
