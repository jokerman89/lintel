---
name: context-warm-adrs
layer: foundation
description: Load topic-relevant ADRs into context — design constraints + prior decisions surfaced for current work.
color: cyan
tools: Read, Bash, Grep, Glob
voice: internal
cli_support: [claude-code, codex]
---

You are the context-warm-adrs skill.

## When to use

- Pre-PLAN when wedge touches area with prior ADRs
- DEFINE phase if operator suspects related prior decision
- Explicitly authorized cross-repository ADR comparison, read-only; no implicit sync/remote

## When NOT to use

- No ADR directory exists (report missing architecture context rather than an empty verified set)
- ADRs already loaded by SENSE (already in context)

## Workflow

### Step 1 — Scan ADRs by topic match

```bash
source "${LINTEL_SOURCE_ROOT:?Set the trusted Lintel source root}/bin/_context.sh"
topic="${1:?Supply a literal topic}"
root=$(_context_repo_identity) || exit 1
adrs=$(lintel_decisions_dir) || exit 1
case "$adrs" in "$root"/*) relative="${adrs#"$root"/}" ;;
  *) echo 'ADR directory is outside the selected repository.' >&2; exit 1 ;;
esac
context_select --glob "$relative/[0-9]*.md" --topic "$topic" \
  --adr-status "${2:-active}" --limit 10
```

### Step 2 — Filter by status

Operator can flag:
- `--accepted-only`: just Accepted ADRs
- `--include-deprecated`: include Deprecated/Superseded
- Default: Accepted + Proposed

Map these skill flags to helper `--adr-status accepted`, `all` or `active`, respectively.
The shared metadata reader recognizes YAML fields, `**Status:** Accepted (date)` and
bullet-style `- **Status:** Accepted` / `- **Date:** ...`. Unknown/missing metadata stays
visible as **unknown**, including under accepted-only: do not pretend it is accepted or
silently discard a potentially binding decision. Inspect those candidates before relying
on the filter. Superseded/deprecated sources remain explicitly recoverable with `all`.

### Step 3 — Surface candidate list

```
ADRs MATCHING "<topic>":

| # | Title | Status | Date | Tokens (est) |
|---|---|---|---|---|
| 0042 | <title> | Accepted | 2026-04 | 1.2k |
| 0058 | <title> | Proposed | 2026-05 | 0.8k |
| 0023 | <title> | Deprecated | 2025-11 | 0.5k |

Total est: <X>k tokens

Load all? (Y / accepted only / select subset / cancel)
```

### Step 4 — Delegate to context-warm

Pass each selected manifest path as a separate literal `--path` to `/li:context-warm`.
Show the exact root, matched paths, omitted count and metadata uncertainty. Missing
files, an absent ADR directory or an unsupported status is not evidence of no constraints.

### Step 5 — 00-state.md append

```yaml
event: context_warm_adrs
topic: <topic>
adrs_loaded: <N>
estimated_input_tokens: <source-byte heuristic; capacity unknown unless observed>
```

## Integration

Reads `.claude/decisions/*.md`. Delegates to `/li:context-warm`.

## Anti-patterns

- **Loading ALL ADRs ever** — filter by topic
- **Loading deprecated without note** — surface explicitly that ADR is deprecated
