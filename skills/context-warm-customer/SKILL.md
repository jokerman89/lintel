---
name: context-warm-customer
layer: foundation
description: Load customer-engagement repo state into context — customer's Bicep, their CLAUDE.md, their ADRs, recent commits.
color: cyan
tools: Read, Bash, Glob
voice: internal
cli_support: [claude-code, codex]
---

You are the context-warm-customer skill — customer-engagement repo loader.

## When to use

- Pre-customer-meeting prep on operator's machine
- Cross-repo reasoning: "compare our reference architecture against customer X's actual state"
- Operator wants to assess a customer's architecture posture before recommending

## When NOT to use

- Customer-data risk: customer repo contains customer-PII NOT scrubbed for operator's machine — verify before load
- Customer repo is huge: cap aggressively, don't load everything

## Workflow

### Step 1 — Locate customer repo

```bash
engagement="$1"  # e.g., "acme" or full path
default_root="${LINTEL_CUSTOMER_ROOT:-~/Workspace}"

customer_repo=""
for candidate in \
  "$default_root/customer-$engagement" \
  "$default_root/$engagement" \
  "$default_root/customer-engagements/$engagement"; do
  [ -d "$candidate" ] && { customer_repo="$candidate"; break; }
done

if [ -z "$customer_repo" ]; then
  echo "Customer repo for '$engagement' not found. Suggest --path <full-path>."
  exit 1
fi
```

### Step 2 — Sensitivity check

If the active pack's compliance mode is `hard` (`resolve_pack_field compliance.mode`): verify customer repo's `.gitignore` excludes customer-PII patterns. If patterns present in tracked files: warn + ask confirm.

### Step 3 — Identify relevant files (limited scope)

Default load set:
- `CLAUDE.md`, `README.md` (context)
- `.claude/decisions/[0-9]*.md` (top 10 most-recent)
- `*.bicep`, `*.tf`, `*.bicepparam` (top 20 by file size)
- `recent git log --oneline -20`

Operator can override with `--scope <pattern>` flag.

### Step 4 — Estimate + confirm

```
CONTEXT WARM — customer engagement "<engagement>"

Repo: <path>
Files identified: <count>
Estimated tokens: ~<X>k

Sensitivity: <verified / warn-only / blocked>
Customer-data patterns: <none detected | found in <files>>

Load all? (Y / select subset / cancel)
```

### Step 5 — Delegate to context-warm

```bash
/li:context-warm <selected-files>
```

### Step 6 — 00-state.md append + audit log

```yaml
event: context_warm_customer
engagement: <name>
repo_path: <path>
files_loaded: <N>
tokens_added: <approx>
sensitivity_check: <result>
```

Also append one traceability line via the unified writer:

```bash
source "$(git rev-parse --show-toplevel)/bin/_audit.sh"
audit_log customer-repo-access context_warm engagement=<name> repo=<path> files_loaded=<N> sensitivity_check=<result>
# → .claude/runtime/audit/customer-repo-access.jsonl
```

## Pause-points

- Sensitivity confirmation (MANDATORY if the active pack's compliance mode is `hard`)

## Integration

Reads customer repo via Read/Glob. Delegates to `/li:context-warm`. Logs audit.

## Anti-patterns

- **Loading customer-data unscrubbed** — sensitivity check is MANDATORY
- **Loading entire customer repo** — bounded scope, default file types only
- **Forgetting audit log** — customer-repo access must be traceable
