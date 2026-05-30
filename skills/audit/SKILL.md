---
name: audit
layer: foundation
description: Read the unified Lintel audit trail — surface ~/.lintel/audit/<category>.jsonl records with optional category / kind / since-days filters. Read-only.
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

Every Lintel audit record now lands in `~/.lintel/audit/<category>.jsonl` via the unified `audit_log` writer in `bin/_audit.sh`. Each record is a single JSON line with the shape:

```json
{"ts":"...","kind":"...","operator":"...","cycle_id":"...", ...extra k=v fields...}
```

This skill cats/greps those logs so an operator can answer "what happened, and when?" without hand-parsing JSONL. It never writes — pure read.

## When to use

- "What's in the audit trail?" — no args, lists every category + record count
- "Show me the jobs audit" — `--category jobs`
- "Did any brief-forge bypass fire this week?" — `--kind brief_forge_bypassed --since 7`
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
LINTEL_HOME="${LINTEL_HOME:-$HOME/.lintel}"
AUDIT_DIR="${LINTEL_AUDIT_DIR:-$LINTEL_HOME/audit}"

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

if [ ! -d "$AUDIT_DIR" ]; then
  echo "_No audit trail yet._ (Nothing has been audit-logged on this machine.)"
  exit 0
fi

# No filters → summary table of categories + counts
if [ -z "$category" ] && [ -z "$kind" ] && [ -z "$since" ]; then
  echo "## Lintel audit categories"
  echo ""
  found=0
  for f in "$AUDIT_DIR"/*.jsonl; do
    [ -f "$f" ] || continue
    found=1
    n=$(wc -l < "$f" | tr -d ' ')
    printf -- '- %s: %s records\n' "$(basename "$f" .jsonl)" "$n"
  done
  [ "$found" -eq 0 ] && echo "_No audit records yet._"
  echo ""
  echo "Run with --category <name> to view records."
  exit 0
fi

# Build the cut-off ISO timestamp for --since
since_iso=""
if [ -n "$since" ]; then
  since_iso=$(date -u -d "$since days ago" +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null || \
              date -u -v "-${since}d" +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null || echo "")
fi

# Resolve which files to scan
if [ -n "$category" ]; then
  files=("$AUDIT_DIR/$category.jsonl")
else
  files=("$AUDIT_DIR"/*.jsonl)
fi

shown=0
for f in "${files[@]}"; do
  [ -f "$f" ] || continue
  while IFS= read -r line; do
    [ -z "$line" ] && continue
    # kind filter (field-based; tolerates extra fields)
    if [ -n "$kind" ] && ! printf '%s' "$line" | grep -q "\"kind\":\"${kind}\""; then
      continue
    fi
    # since filter (ISO-8601 lexicographic compare on ts)
    if [ -n "$since_iso" ]; then
      ts=$(printf '%s' "$line" | grep -oE '"ts":"[^"]+"' | head -1 | sed 's/.*"ts":"//; s/"$//')
      [ -n "$ts" ] && [ "$ts" \< "$since_iso" ] && continue
    fi
    printf '%s\t%s\n' "$(basename "$f" .jsonl)" "$line"
    shown=$((shown + 1))
    [ "$shown" -ge "$limit" ] && break 2
  done < "$f"
done

[ "$shown" -eq 0 ] && echo "_No matching audit records._"
```

The skill leans on `audit_count` / `audit_days_ago` semantics already defined in `bin/_audit.sh`; it can also source that helper if richer counting is needed (`source bin/_audit.sh; audit_count jobs job_begin`).

## Voice tier behavior

`voice: internal`. Operator-only diagnostic. No customer-bound output.

## Status protocol

- **DONE** — records (or the category summary) printed
- **NEEDS_CONTEXT** — `--category` named a log that doesn't exist (suggest running with no args to list categories)

## Hop-in support

YES — always solo-invocable. Pure read, safe to call anytime.

## Integration

**Reads:**
- `~/.lintel/audit/<category>.jsonl` (all categories written by `bin/_audit.sh`)

**Writes:**
- nothing (pure read)

**Calls into:**
- `bin/_audit.sh` helpers `audit_count` / `audit_days_ago` (optional, for counting)

## Anti-patterns

- **Editing the .jsonl logs by hand** — they're append-only event trails. Don't rewrite history.
- **Using this to drive control flow** — it's a forensic reader, not a gate. Gates live in hooks.
- **Re-implementing the JSON shape elsewhere** — the schema is owned by `bin/_audit.sh`. Read it through this skill.

## See also

- `bin/_audit.sh` (the unified writer — `audit_log <category> <kind> [k=v ...]`)
- `/li:status` (in-flight jobs, reads `_active.md` not the audit log)
- `/li:jobs` (the jobs lifecycle controller — produces `jobs.jsonl` records)
- `tests/shape/audit-writes-via-helper.sh` (guard: no inline JSONL writers bypass the helper)
