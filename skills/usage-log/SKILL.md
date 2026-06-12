---
name: usage-log
layer: foundation
description: Append-only usage log for skill/agent invocations. Wrapper pattern per L-001 (one log, no per-skill duplicates). Solo-invokable for reports.
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

**Writer mode (default at-skill-invocation):** Appends a JSON line per skill/agent invocation to `~/.lintel/audit/usage-<YYYYMMDD>.jsonl`. Schema: `{ts, skill, mode, tokens_est, cli, run_id}`. Daily-file rotation from day 1 (Finding 3A from plan-eng-review — multi-MB growth otherwise).

**Reader mode (solo-invokable for reports):** Reads recent usage logs, surfaces top-skills + frequency + estimated token spend per skill family. Pairs with `/li:hooks-status` (siblings in the observation spine).

Designed per Cohort 2 in the v3.6 backlog. The foundation that `/li:maintenance` (5.3) and `/li:catalog` (1.6 trends) build on.

## When to use

- **Writer mode:** invoked automatically via the wrapper-hook after each skill invocation. The operator does not touch this directly.
- **Reader mode:** "what have I used most over the past week?" → `/li:usage-log --report --days 7`
- Maintenance pre-flight: `/li:usage-log --report --topn 10` sees what's rusting (skills used <2× per month)
- Token-budget debugging: `/li:usage-log --tokens-by-skill` aggregates token-est per skill

## When NOT to use

- Real-time telemetry — this is append-only, not streaming
- Forensic audit — `hooks.jsonl` is audit-canonical (per L-001 premise 1: forensic logs are exempt from the read-back rule)
- Per-invocation token-counting — this estimates (tokens_est is a heuristic, not OpenAI-counted)

## Schema (per JSONL line)

```json
{
  "ts": "2026-05-28T14:23:45Z",
  "skill": "research",
  "mode": "full",
  "tokens_est": 3500,
  "cli": "claude-code",
  "run_id": "20260528-142345-a7c"
}
```

**Field spec:**
- `ts` — ISO-8601 UTC timestamp
- `skill` — frontmatter `name:` value
- `mode` — invocation mode if relevant ("full", "brief", "section:<x>", or null)
- `tokens_est` — heuristic estimate (input + output, not cached)
- `cli` — claude-code | codex | cursor | gemini | copilot-cli | droid
- `run_id` — unique invocation ID (timestamp + random suffix, links to other logs)

## Workflow

### Step 1 — Writer mode (automatic, via wrapper-hook)

Wrapper-hook at `hooks/post-skill-invocation.sh` calls:

```bash
~/.claude/skills/usage-log/bin/append.sh \
  --skill "$INVOKED_SKILL" \
  --mode "$INVOKE_MODE" \
  --tokens-est "$TOKENS_EST" \
  --cli "$ACTIVE_CLI" \
  --run-id "$RUN_ID"
```

Append-script:
1. Compute today's filename: `~/.lintel/audit/usage-$(date +%Y%m%d).jsonl`
2. JSON-encode args + ts via `jq -nc`
3. Append to the file (atomic — write to .tmp then mv for concurrent-safety)
4. Silent — no operator output unless an error

### Step 2 — Reader mode (solo-invokable)

```bash
~/.lintel/audit/usage-*.jsonl
```

Glob across days. Surface:
- **Top N skills by frequency** (`--topn 10 --days 7`)
- **Token spend by skill family** (`--tokens-by-skill`)
- **Rust detection** (skills used < 2× past 30 days — flag candidates for archive)
- **Override-pattern correlation** (cross-reference with hooks.jsonl override-counts)

### Step 3 — Rotation policy (built-in)

- **Daily-file rotation** by default — new file per day → no single-file multi-MB risk
- **Retention:** keep the last 90 days, archive older ones to `~/.lintel/audit/archive/` (gzipped)
- **Compaction:** a quarterly summary written to `~/.lintel/audit/usage-summary-<YYYY-Q>.json` with the top-100 skills + total-invocations

The operator can trigger compaction via `/li:usage-log --compact`.

## Integration

**Reads (writer mode):**
- Wrapper-hook context (invoked skill, mode, tokens-est, cli, run_id)

**Writes:**
- `~/.lintel/audit/usage-<YYYYMMDD>.jsonl` (append, daily-file rotation)
- `~/.lintel/audit/archive/usage-*.jsonl.gz` (after 90 days)
- `~/.lintel/audit/usage-summary-<YYYY-Q>.json` (quarterly compaction)

**Reads (reader mode):**
- `~/.lintel/audit/usage-*.jsonl` (glob)
- `.claude/runtime/audit/hooks.jsonl` (cross-reference for override-pattern correlation, if requested)

**Consumed by:**
- `/li:maintenance` (5.3 — token-cost simulation, rust detection)
- `/li:catalog` (1.6 — usage-trend coloring for top-N skills)
- `/li:hooks-status` (1.2 + 1.7 — sibling observation skill)
- Operator (solo-report invocation)

## Anti-patterns

- **Per-skill append-bash in SKILL.md** — breaks DRY across 113 skills (Finding 2A). Wrapper-hook only.
- **Single growing file (`usage.jsonl` flat)** — breaks the rotation policy. Multi-MB risk after months.
- **Token-counting "exactly" via the OpenAI API** — out of scope. The heuristic IS the tokens_est field.
- **Read-back for forensic purposes** — wrong skill. Use `.claude/runtime/audit/hooks.jsonl` (audit-canonical).

## Failure recovery

- Append fails (permission, disk-full): silent skip, error logged to stderr only. Skill invocation continues — observation should never block work.
- Rotation fails: fall back to today's file (no daily file change), warn to stderr.
- Reader-report empty (no logs yet): surface "No usage data yet. Skill invocations start logging once this hook is installed."

## Recommended next steps after invocation

- For full observation: pair with `/li:hooks-status` (sibling skill)
- For maintenance: `/li:maintenance` uses this as a data source
- For catalog-trending: `/li:catalog --trends` overlays usage-frequency on discoverability
