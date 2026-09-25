---
name: usage-log
layer: foundation
description: Append-only usage log for skill/agent invocations — manual writer (one audit_log line) plus reader reports. One log, no per-skill duplicates (L-001). Solo-invokable for reports.
color: yellow
tools: Read, Write, Bash, Glob
voice: internal
cli_support:
  - cli: claude-code
    level: full
  - cli: codex
    level: degraded
---

You are the `usage-log` skill — the observation foundation under maintenance, token budgeting, hook audit, and low-observed-usage review.

## What this skill does

Two modes:

**Writer mode (manual, operator-invoked):** records one JSONL line per invocation the operator wants counted, via the unified audit writer. There is NO automatic at-skill-invocation trigger — nothing fires this for you (the wrapper-hook this was originally designed around was never built):

```bash
source "${LINTEL_SOURCE_ROOT:-$(git rev-parse --show-toplevel)}/bin/_audit.sh"
audit_log usage-skill invocation skill=<name>     # optional: mode=<mode> tokens_est=<n> cli=<cli>
```

→ appends to `$(audit_file usage-skill)`, the operator-global `usage-skill.jsonl` (`usage-*` categories always route operator-global — see `bin/_audit.sh`).

**Reader mode (solo-invokable for reports):** reads existing usage records, surfaces top-skills + frequency + estimated token spend per skill family. Pairs with `/li:hooks-status` (siblings in the observation spine). Absent or low recorded usage is reported as unobserved or low observed usage — never as a verdict that a skill is unused.

The foundation that `/li:maintenance` (5.3) and `/li:catalog` (1.6 trends) build on — both degrade gracefully when no records exist.

## When to use

- **Writer mode:** the operator (or a skill the operator instructs) wants an invocation counted — run the one-liner above.
- **Reader mode:** "what have I used most over the past week?" → `/li:usage-log --report --days 7`
- Maintenance pre-flight: `/li:usage-log --report --topn 10` shows low observed usage (skills with <2 recorded invocations per month)
- Token-budget debugging: `/li:usage-log --tokens-by-skill` aggregates token-est per skill

## When NOT to use

- Real-time telemetry — this is append-only, not streaming
- Forensic audit — `hooks.jsonl` is audit-canonical (per L-001 premise 1: forensic logs are exempt from the read-back rule)
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
- `cli` — claude-code | codex | cursor | gemini | copilot-cli | droid — optional

## Workflow

### Step 1 — Writer mode (manual)

Run the one-liner from "What this skill does". That is the whole writer — no script, no hook:

```bash
source "${LINTEL_SOURCE_ROOT:-$(git rev-parse --show-toplevel)}/bin/_audit.sh"
audit_log usage-skill invocation skill=cycle mode=research-dive tokens_est=3500 cli=claude-code
```

### Step 2 — Reader mode (solo-invokable)

```bash
source "${LINTEL_SOURCE_ROOT:?select trusted source}/bin/_audit.sh"
usage_dir="$(audit_dir usage-skill)"   # the router's operator-global directory
for log in "$usage_dir"/usage-*.jsonl; do
  [ -f "$log" ] || continue
  rc=0
  python3 "$LINTEL_SOURCE_ROOT/bin/li-events.py" records --file "$log" --category usage-skill \
    ${since:+--since "$since"} || rc=$?
  case "$rc" in 0|3|4) ;; *) echo "Could not read $log (exit $rc)"; exit "$rc" ;; esac
done
```

Glob across files (the writer appends to `usage-skill.jsonl`; older `usage-<YYYYMMDD>.jsonl` files, if any exist, still match and are read with the same `usage-skill` catalog entry; anything else surfaces as a reader diagnostic rather than disappearing). Surface:
- **Top N skills by frequency** (`--topn 10 --days 7`)
- **Token spend by skill family** (`--tokens-by-skill`)
- **Low observed usage** (fewer than 2 recorded invocations in 30 days — review candidates only; unrecorded use is unobserved, not disuse)
- **Override-pattern correlation** (cross-reference with hooks.jsonl override-counts)

If no records exist: surface "No usage records observed in `<usage dir>` — the writer is manual (see writer mode)" and stop. Never invent counts.

## Integration

**Writes (writer mode):**
- `$(audit_file usage-skill)` — operator-global `usage-skill.jsonl` (append, one line per recorded invocation, via `audit_log`)

**Reads (reader mode):**
- `usage-*.jsonl` in `$(audit_dir usage-skill)` (glob), through `bin/li-events.py`
- `.claude/runtime/audit/hooks.jsonl` (cross-reference for override-pattern correlation, if requested)

**Consumed by:**
- `/li:maintenance` (5.3 — token-cost simulation, low-observed-usage review; falls back to defaults when no records exist)
- `/li:catalog` (1.6 — usage-trend coloring for top-N skills)
- `/li:hooks-status` (1.2 + 1.7 — sibling observation skill)
- Operator (solo-report invocation)

## Anti-patterns

- **Bespoke per-skill `>>` writers** — breaks DRY across 113 skills (Finding 2A) and skips the ts/operator/cycle_id envelope. The `audit_log usage-skill ...` one-liner is the only writer.
- **Claiming automatic capture** — there is no wrapper-hook; records exist only when someone ran the one-liner. Reports must say so.
- **Token-counting "exactly" via the OpenAI API** — out of scope. The heuristic IS the tokens_est field.
- **Read-back for forensic purposes** — wrong skill. Use `.claude/runtime/audit/hooks.jsonl` (audit-canonical).

## Failure recovery

- Append fails (permission, disk-full, a path that is not a directory): `audit_log` warns on stderr and returns 0 — observation never blocks work. Some hooks discard that stderr, so a missing record stays unobserved rather than meaning the invocation did not happen.
- Reader-report empty (no records yet): surface "No usage records observed. The writer is manual — `audit_log usage-skill invocation skill=<name>`."

## Recommended next steps after invocation

- For full observation: pair with `/li:hooks-status` (sibling skill)
- For maintenance: `/li:maintenance` uses this as a data source (if usage records exist)
- For catalog-trending: `/li:catalog --trends` overlays usage-frequency on discoverability
