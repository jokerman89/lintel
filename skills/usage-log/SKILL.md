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

You are the `usage-log` skill — the observation foundation under maintenance, token budgeting, hook audit, and "what rusts."

## What this skill does

Two modes:

**Writer mode (manual, operator-invoked):** records one JSONL line per invocation the operator wants counted, via the unified audit writer. There is NO automatic at-skill-invocation trigger — nothing fires this for you (the wrapper-hook this was originally designed around was never built):

```bash
source "${LINTEL_SOURCE_ROOT:-$(git rev-parse --show-toplevel)}/bin/_audit.sh"
audit_log usage-skill invocation skill=<name>     # optional: mode=<mode> tokens_est=<n> cli=<cli>
```

→ appends to `~/.lintel/audit/usage-skill.jsonl` (`usage-*` categories always route operator-global — see `bin/_audit.sh`).

**Reader mode (solo-invokable for reports):** reads existing usage records, surfaces top-skills + frequency + estimated token spend per skill family. Pairs with `/li:hooks-status` (siblings in the observation spine).

The foundation that `/li:maintenance` (5.3) and `/li:catalog` (1.6 trends) build on — both degrade gracefully when no records exist.

## When to use

- **Writer mode:** the operator (or a skill the operator instructs) wants an invocation counted — run the one-liner above.
- **Reader mode:** "what have I used most over the past week?" → `/li:usage-log --report --days 7`
- Maintenance pre-flight: `/li:usage-log --report --topn 10` sees what's rusting (skills used <2× per month)
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
  "skill": "research",
  "mode": "full",
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
audit_log usage-skill invocation skill=research mode=full tokens_est=3500 cli=claude-code
```

### Step 2 — Reader mode (solo-invokable)

```bash
~/.lintel/audit/usage-*.jsonl
```

Glob across files (the writer appends to `usage-skill.jsonl`; older `usage-<YYYYMMDD>.jsonl` files, if any exist, still match). Surface:
- **Top N skills by frequency** (`--topn 10 --days 7`)
- **Token spend by skill family** (`--tokens-by-skill`)
- **Rust detection** (skills used < 2× past 30 days — flag candidates for archive)
- **Override-pattern correlation** (cross-reference with hooks.jsonl override-counts)

If no records exist: surface "No usage data yet — the writer is manual (see writer mode)" and stop. Never invent counts.

## Integration

**Writes (writer mode):**
- `~/.lintel/audit/usage-skill.jsonl` (append, one line per recorded invocation, via `audit_log`)

**Reads (reader mode):**
- `~/.lintel/audit/usage-*.jsonl` (glob)
- `.claude/runtime/audit/hooks.jsonl` (cross-reference for override-pattern correlation, if requested)

**Consumed by:**
- `/li:maintenance` (5.3 — token-cost simulation, rust detection; falls back to defaults when no records exist)
- `/li:catalog` (1.6 — usage-trend coloring for top-N skills)
- `/li:hooks-status` (1.2 + 1.7 — sibling observation skill)
- Operator (solo-report invocation)

## Anti-patterns

- **Bespoke per-skill `>>` writers** — breaks DRY across 113 skills (Finding 2A) and skips the ts/operator/cycle_id envelope. The `audit_log usage-skill ...` one-liner is the only writer.
- **Claiming automatic capture** — there is no wrapper-hook; records exist only when someone ran the one-liner. Reports must say so.
- **Token-counting "exactly" via the OpenAI API** — out of scope. The heuristic IS the tokens_est field.
- **Read-back for forensic purposes** — wrong skill. Use `.claude/runtime/audit/hooks.jsonl` (audit-canonical).

## Failure recovery

- Append fails (permission, disk-full): `audit_log` warns on stderr and continues — observation never blocks work.
- Reader-report empty (no records yet): surface "No usage data yet. The writer is manual — `audit_log usage-skill invocation skill=<name>`."

## Recommended next steps after invocation

- For full observation: pair with `/li:hooks-status` (sibling skill)
- For maintenance: `/li:maintenance` uses this as a data source (if usage records exist)
- For catalog-trending: `/li:catalog --trends` overlays usage-frequency on discoverability
