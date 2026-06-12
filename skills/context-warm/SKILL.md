---
name: context-warm
layer: foundation
description: Load specified files into session context — on-demand 1M-window utilization. Reports tokens added + budget impact. Base skill for all context-warm variants.
color: cyan
tools: Read, Bash, Glob
voice: internal
cli_support: [claude-code, codex]
---

You are the context-warm base skill — explicit file load into session.

## What this skill does

Loads files specified by operator into session context. Reports token cost. Updates context budget tracking. This is the BASE for all warm-* variants (related, sessions, adrs, customer, from-url).

`--pattern` runs the declared-pattern preload — the former standalone warmup skill is folded into this one (its old name routes here via `config/aliases.yaml`): instead of an explicit target, it warms the repo's declared high-leverage file set.

Default session-start loads ~5-15k tokens (CLAUDE.md, AGENT-INSTRUCTIONS, lessons, memory, recent ADRs, active role identity). When more context is needed for deeper work, operator explicitly warms.

## When to use

- Operator says "load these files into context"
- Pre-PLAN if DISCOVER recommended warming specific files
- Mid-BUILD when implementing requires more codebase context
- Pre-REVIEW when reviewing artifacts that reference external context

## When NOT to use

- Default session-start loading (handled by SENSE phase)
- For single-file read (just use Read tool directly)
- When context budget is tight without `/li:context-cool` first

## Workflow

### Step 1 — Parse target

```bash
target="$1"  # path, glob, or comma-separated list
# Resolve globs
files=()
for pattern in $(echo "$target" | tr ',' '\n'); do
  while IFS= read -r f; do
    [ -f "$f" ] && files+=("$f")
  done < <(eval "ls -1 $pattern 2>/dev/null")
done

if [ ${#files[@]} -eq 0 ]; then
  echo "No files matched: $target"
  exit 1
fi
```

### Step 2 — Estimate token impact

```bash
total_chars=0
for f in "${files[@]}"; do
  chars=$(wc -c < "$f")
  total_chars=$((total_chars + chars))
done
# Rough estimate: 1 token ≈ 4 chars
est_tokens=$((total_chars / 4))
```

### Step 3 — Budget check

Read current `.claude/runtime/state/context-budget.md` if exists:
- Current tokens used
- Headroom

If `est_tokens > headroom × 0.8` (would consume >80% of remaining): warn + ask confirm.

### Step 4 — Confirm with operator (if >20k tokens loading)

For loads ≥20k tokens: AskUserQuestion "Loading ~<N>k tokens. Budget after: <X>/1M (<%>). Continue?"
- A) Yes, proceed
- B) Show file list first
- C) Reduce scope (specify subset)
- D) Cancel

For loads <20k: proceed silently with summary report.

### Step 5 — Load files via Read tool

```bash
for f in "${files[@]}"; do
  # Read each file (Claude Code Read tool)
  # Files appear in session context
done
```

### Step 6 — Update budget tracking

```yaml
# .claude/runtime/state/context-budget.md (append)
event: context_warm
ts: <timestamp>
files_loaded: <count>
tokens_added: <est>
budget_before: <N>
budget_after: <N>
warm_source: explicit
```

### Step 7 — Surface report

```
CONTEXT WARM — <target spec>

Files loaded: <count>
  - <file 1> (<chars>)
  - <file 2>
  ...

Tokens added: ~<N>k
Context budget: <prev>k → <new>k / 1M (<%>)
Headroom: <X>k

Files are now in session — subsequent skills + agents will see them.
To cool / drop: /li:context-cool
To save state: /li:context-save
```

## Status protocol

- **DONE** — files loaded, budget updated, report surfaced
- **BLOCKED** — no files matched OR budget overrun rejected
- **NEEDS_CONTEXT** — operator didn't specify target

## Pause-points

- If load ≥20k tokens: confirm
- If files have sensitive markers (customer-data patterns): warn

## Hop-in support

YES — invoked anytime mid-session.

## Integration

**Reads:**
- Target files (via Read tool, into session context)
- `.claude/runtime/state/context-budget.md` (prior state)

**Writes:**
- `.claude/runtime/state/context-budget.md` (append event)
- Session context (the loaded file content)

**Triggers:**
- Nothing automatic — files now available for subsequent skills

## Anti-patterns

- **Loading entire repo by accident** — glob carefully, preview file list before load if large
- **Skipping budget check for >20k loads** — operator should see cost upfront
- **Loading customer data without a compliance check** — if the active pack's compliance mode is `hard` and files match customer-PII patterns, warn before load
- **Caching warmed content across sessions** — ephemeral by design, each session is fresh

## Failure recovery

- **Target glob matches 0 files**: surface helpful suggestion (similar names found?)
- **One file unreadable**: skip it, continue with rest, note in report
- **Budget overrun**: REFUSE, recommend `/li:context-cool` first

## Voice tier behavior

`voice: internal`. Operator coordination only.
