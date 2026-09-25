---
name: context-warm-customer
layer: foundation
description: Load customer-engagement repo state into context — their infrastructure-as-code, their CLAUDE.md, their ADRs, recent commits.
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

### Step 1 — Establish scope, then locate the authorized repo

Confirm the requested customer/source boundary and data-handling authority before lookup.
An engagement name is not permission to search a user's home. Reuse prior explicit
authorization; missing authorization blocks reading regardless of advisory/hard pack mode.

```bash
engagement="${1:?Supply an authorized engagement name}"
default_root="${LINTEL_CUSTOMER_ROOT:?Set the explicitly authorized customer root, or use --path}"
case "$engagement" in ''|*[!A-Za-z0-9_-]*)
  echo 'Use a simple engagement name or an explicitly selected --path.' >&2; exit 1 ;;
esac

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

Read the active pack's actual requirements, including `resolve_pack_field compliance.mode`.
Verify the proposed selection is authorized and excludes forbidden customer data. A detected
forbidden pattern or an unavailable mandatory check blocks the affected read.

`.gitignore` is not proof that tracked or untracked content is safe. Evaluate the actual
selected files against current policy before sending them to any model/tool. An unresolved
mandatory control blocks loading; a generic "continue" cannot bypass it. An explicit
`--path` selects that single repository instead of the configured-name lookup above.

### Step 3 — Identify relevant files (limited scope)

Default load set:
- `CLAUDE.md`, `README.md` (context)
- `.claude/decisions/[0-9]*.md` (top 10 most-recent)
- `*.tf`, `*.bicep`, `*.bicepparam`, `*.yaml` infra manifests (top 20 by file size)
- `recent git log --oneline -20`

Operator can override with `--scope <pattern>` flag.

Use the trusted-source `_context.sh` reader with `LINTEL_REPO_ROOT` set to the approved
customer path for this invocation. Pass each path/glob separately to `context_select`;
never source executable helpers from that customer repository. This proves containment,
link/reparse refusal, actual file sizes and bounded selection before the read.
For ADRs use `--adr-status active --limit 10`, keeping unknown metadata visible. Preview
the bounded infra candidates and choose at most 20 by reported size; do not hide omitted
or unmatched patterns. The recent Git log is a separate explicitly scoped read.

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

Delegate the literal selected manifest paths to `/li:context-warm` in that same approved
root. Source estimates do not assert host capacity. A missing/unreadable source stays
incomplete; never silently expand to another customer repository.

### Step 6 — 00-state.md append + audit log

```yaml
event: context_warm_customer
engagement: <name>
repo_path: <path>
files_loaded: <N>
estimated_input_tokens: <source-byte heuristic, not observed active usage>
sensitivity_check: <result>
```

Also append one traceability line via the unified writer:

```bash
source "${LINTEL_SOURCE_ROOT:?Set the trusted Lintel source root}/bin/_audit.sh"
: "${caller_root:?Set the authorized caller audit root}"
: "${approved_source_id:?Set a non-sensitive source identifier}"
: "${files_loaded:?Set the actual successful read count}"
: "${sensitivity_result:?Set the actual check outcome}"
LINTEL_REPO_ROOT="$caller_root" audit_log customer-repo-access context_warm \
  "source_id=$approved_source_id" "files_loaded=$files_loaded" "sensitivity_check=$sensitivity_result"
# → .claude/runtime/audit/customer-repo-access.jsonl
```

Use the caller's authorized audit location, not a write into a read-only customer source.
Record minimal source identifiers and outcomes; do not copy customer content, credentials
or private path details into public artifacts. Audit schema/host integration is separate
from permission to read the selected sources.

## Pause-points

- Sensitivity confirmation (MANDATORY if the active pack's compliance mode is `hard`)

## Integration

Reads customer repo via Read/Glob. Delegates to `/li:context-warm`. Logs audit.

## Anti-patterns

- **Loading customer-data unscrubbed** — sensitivity check is MANDATORY
- **Loading entire customer repo** — bounded scope, default file types only
- **Forgetting audit log** — customer-repo access must be traceable
