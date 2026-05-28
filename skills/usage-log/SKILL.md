---
name: usage-log
layer: foundation
description: Append-only usage log för skill/agent-invocations. Wrapper-pattern per L-001 (en log, ingen per-skill duplikat). Solo-invokable för rapport.
color: yellow
tools: Read, Write, Bash, Glob
voice: internal
cli_support:
  - cli: claude-code
    level: full
  - cli: codex
    level: degraded
---

You are the `usage-log` skill — observation foundation under maintenance, token-premiering, hook-audit, och "what rusts."

## What this skill does

Two modes:

**Writer mode (default at-skill-invocation):** Appends a JSON line per skill/agent invokation till `~/.lintel/audit/usage-<YYYYMMDD>.jsonl`. Schema: `{ts, skill, mode, tokens_est, cli, run_id}`. Daily-file rotation från dag 1 (Finding 3A från plan-eng-review — multi-MB growth annars).

**Reader mode (solo-invokable for reports):** Reads recent usage logs, surfaces top-skills + frequency + estimated-token-spend per skill family. Pairs with `/li:hooks-status` (siblings i observation spine).

Designed per Cohort 2 i v3.6 backlog. Foundation som `/li:maintenance` (5.3) och `/li:catalog` (1.6 trends) bygger på.

## When to use

- **Writer mode:** invoked automatiskt via wrapper-hook efter varje skill-invocation. Operatör rör inte denna direkt.
- **Reader mode:** "vad har jag använt mest senaste veckan?" → `/li:usage-log --report --days 7`
- Maintenance-pre-flight: `/li:usage-log --report --topn 10` ser vad som rostar (skills used <2× per månad)
- Token-budget-debugging: `/li:usage-log --tokens-by-skill` aggregerar token-est per skill

## When NOT to use

- Real-time telemetry — denna är append-only, ej streaming
- Forensic audit — `hooks.jsonl` är audit-canonical (per L-001 premiss 1: forensiska loggar undantagna från read-back-rule)
- Per-invocation token-counting — denna estimerar (tokens_est är heuristik, ej OpenAI-counted)

## Schema (per JSONL line)

```json
{
  "ts": "2026-05-28T14:23:45Z",
  "skill": "az-tldr",
  "mode": "full",
  "tokens_est": 3500,
  "cli": "claude-code",
  "run_id": "20260528-142345-a7c"
}
```

**Fält-spec:**
- `ts` — ISO-8601 UTC timestamp
- `skill` — frontmatter `name:` value
- `mode` — invocation mode if relevant ("full", "brief", "section:<x>", or null)
- `tokens_est` — heuristic estimate (input + output, ej cached)
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
3. Append to file (atomic — write to .tmp then mv för concurrent-safety)
4. Silent — no operator-output unless error

### Step 2 — Reader mode (solo-invokable)

```bash
~/.lintel/audit/usage-*.jsonl
```

Glob across days. Surface:
- **Top N skills by frequency** (`--topn 10 --days 7`)
- **Token-spend by skill family** (`--tokens-by-skill`)
- **Rust detection** (skills used < 2× past 30 days — flag candidates för archive)
- **Override-pattern correlation** (cross-reference med hooks.jsonl override-counts)

### Step 3 — Rotation policy (built-in)

- **Daily-file rotation** by default — new file per day → ingen single-file-multi-MB-risk
- **Retention:** keep last 90 days, archive older till `~/.lintel/audit/archive/` (gzipped)
- **Compaction:** quarterly summary written till `~/.lintel/audit/usage-summary-<YYYY-Q>.json` med top-100 skills + total-invocations

Operator kan trigga compaction via `/li:usage-log --compact`.

## Voice tier behavior

`voice: internal`. Telemetry är operator-internal observability. Aldrig customer-bound, ingen voice-gate.

## Status protocol

- **DONE** — writer-append klar OR reader-report rendered
- **DONE_WITH_CONCERNS** — append klar men file-rotation eller compaction failade non-fatally
- **BLOCKED** — `~/.lintel/audit/` write-permission saknas
- **NEEDS_CONTEXT** — reader mode utan `--report` / `--topn` / `--tokens-by-skill`-flag

## Pause-points

- File-rotation conflict (concurrent invocations försöker rotate samma minut) — atomic-mv-pattern lös detta
- Quarterly compaction tar > 30s — surface progress, allow operator-interrupt

## Hop-in support

YES — reader mode solo-invokable. Writer mode körs automatiskt via wrapper-hook.

## Integration

**Reads (writer mode):**
- Wrapper-hook context (invoked skill, mode, tokens-est, cli, run_id)

**Writes:**
- `~/.lintel/audit/usage-<YYYYMMDD>.jsonl` (append, daily-file rotation)
- `~/.lintel/audit/archive/usage-*.jsonl.gz` (after 90 days)
- `~/.lintel/audit/usage-summary-<YYYY-Q>.json` (quarterly compaction)

**Reads (reader mode):**
- `~/.lintel/audit/usage-*.jsonl` (glob)
- `~/.lintel/audit/hooks.jsonl` (cross-reference för override-pattern correlation, if requested)

**Consumed by:**
- `/li:maintenance` (5.3 — token-cost simulation, rust detection)
- `/li:catalog` (1.6 — usage-trend coloring for top-N skills)
- `/li:hooks-status` (1.2 + 1.7 — sibling observation skill)
- Operator (solo-report invocation)

## Anti-patterns

- **Per-skill append-bash i SKILL.md** — bryter DRY över 113 skills (Finding 2A). Wrapper-hook only.
- **Single growing file (`usage.jsonl` flat)** — bryter rotation policy. Multi-MB risk efter månader.
- **Token-counting "exakt" via OpenAI API** — out of scope. Heuristic ÄR tokens_est-fältet.
- **Read-back i forensisk syfte** — fel skill. Use `~/.lintel/audit/hooks.jsonl` (audit-canonical).

## Failure recovery

- Append fails (permission, disk-full): silent skip, error logged till stderr only. Skill-invocation continues — observation ska aldrig blocka work.
- Rotation fails: fall back till today's file (no daily file change), warn till stderr.
- Reader-report empty (no logs yet): surface "No usage data yet. Skill-invocations börjar logga efter denna hook installerats."

## Recommended next steps after invocation

- För full observation: pair med `/li:hooks-status` (sibling skill)
- För maintenance: `/li:maintenance` använder denna som data-source
- För catalog-trending: `/li:catalog --trends` overlayer usage-frequency på discoverability
