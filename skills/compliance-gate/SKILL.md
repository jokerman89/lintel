---
name: compliance-gate
layer: foundation
description: Compliance-gate aggregator — runs all gates the active pack declares (compliance.hooks) as ONE green/red verdict. Embarrassment protection for compliance (6.10).
color: red
tools: Read, Bash, Glob
voice: internal
cli_support:
  - cli: claude-code
    level: full
  - cli: codex
    level: degraded
---

You are the `compliance-gate` skill — an aggregator around the compliance gates the active pack declares. Backlog 6.10: "Nothing runs ALL relevant gates for an artifact at once. The operator has to remember which ones apply. Aggregate it — embarrassment protection, for compliance."

## What this skill does

Resolves which gates the active pack declares (`resolve_pack_field compliance.hooks`), runs the ones relevant to the current artifact/scope, and aggregates the verdict into ONE green/red status. Prevents the operator from missing a gate that applies but was not invoked manually.

The skill is **pack-driven**: it hardcodes no gates. For the `_default` pack, `compliance.hooks` is empty (no gates) → green/no-op with a note that no compliance pack is active. When an installed pack declares gates of its own, the skill picks them up and runs them.

## When to use

- **Before customer-share** — always run before a PR/deliverable ships externally
- **Pre-merge gate** — as the final step of `/li:ship` (can be integrated there)
- **Per-engagement audit** — quarterly check of engagement state against the compliance baseline
- **Slot for CI** — can run non-blocking warn-only in CI initially, then be promoted

## When NOT to use

- During mid-cycle dev work (compliance is an end-of-cycle gate)
- Single-rule check — run the pack-gate skill directly if you know which one applies

## Where gates come from (pack-resolved, not hardcoded)

Gates are resolved from the active pack:

```bash
source "$(dirname "$0")/../../lib/pack-resolver.sh"

# Gates the active pack declares (YAML list under compliance.hooks).
# _default → empty (no compliance pack active).
pack_hooks=$(resolve_pack_field compliance.hooks | tr -d '[]' | tr ',' ' ')
```

If `pack_hooks` is empty → no compliance pack is active. The skill returns green/no-op with a note. No gate names are built into Lintel; each pack owns its own list.

## Workflow

### Step 1 — Resolve gates from the active pack

```bash
source "$(dirname "$0")/../../lib/pack-resolver.sh"

artifact="${1:-}"             # path to artifact or 'cwd' for whole-repo
scope="${2:-customer-share}"  # customer-share | internal | research

# Active pack's declared compliance gates (empty for _default).
gates_to_run=$(resolve_pack_field compliance.hooks | tr -d '[]' | tr ',' ' ')

if [ -z "${gates_to_run// /}" ]; then
  echo "COMPLIANCE GATE — no compliance pack active (compliance.hooks empty)."
  echo "Verdict: GREEN (no-op). Activate a compliance pack to enable gates."
  exit 0
fi
```

The `scope` argument is passed through to each pack-gate so the pack can decide
which of its own gates apply to that scope. Lintel itself does not interpret the
gate names.

### Step 2 — Invoke each gate in parallel (subagent)

For each gate in `gates_to_run`:
- Spawn a subagent that runs the gate against the artifact (gate-invocation is pack-provided)
- Captures status: PASS / FAIL / N/A / NEEDS_CONTEXT
- Records the finding if FAIL

### Step 3 — Aggregate verdict

```yaml
verdict:
  status: green | yellow | red
  total_gates: N
  passed: P
  failed: F
  not_applicable: NA
  needs_context: NC

red_blockers:
  - gate: <pack-declared gate name>
    reason: <finding>
    fix: <action>
  ...

yellow_warnings:
  ...
```

**Verdict rules:**
- **green** — all applicable gates PASS or N/A (or no gates declared)
- **yellow** — at least 1 FAIL but no customer-data-blocking
- **red** — any customer-data-block (5-hard-rules-violation) OR multiple FAILs

### Step 4 — Surface report + return code

```
COMPLIANCE GATE — <scope> for <artifact>
============================================

Active pack: <pack-name>
Verdict: GREEN | YELLOW | RED

Summary:
  Total gates: N
  Passed:      P
  Failed:      F
  N/A:         NA

Red blockers (must-fix before customer-share):
  ⛔ <gate> — <finding>; <fix action>

Yellow warnings (recommend-fix):
  ⚠ <gate> — <finding>

Next:
  Address red blockers → re-run /li:compliance-gate
  OR
  Override (logged): /li:compliance-gate --override "<justification>"
```

Return code: 0 (green), 1 (yellow), 2 (red).

## Voice tier behavior

`voice: internal`. The compliance verdict is operator-internal. Detailed finding content can be customer-share-sensitive — sanitize the output if the `--for-customer-record` flag is set.

## Status protocol

- **DONE** — verdict green, no blockers (incl. no-gates no-op)
- **DONE_WITH_CONCERNS** — verdict yellow, warnings present but no must-fix
- **BLOCKED** — verdict red OR gate-execution failed on multiple gates
- **NEEDS_CONTEXT** — invocation without a scope when the repo has multiple sub-projects

## Integration

**Reads:**
- Artifact-path (file or repo)
- Active pack via `resolve_pack_field compliance.hooks` (which gates) and `compliance.mode` (baseline-stringency)
- Each pack-gate's PASS/FAIL output

**Writes:**
- `.claude/runtime/audit/compliance-gates.jsonl` — one line per run via the unified writer:
  `source "$(git rev-parse --show-toplevel)/bin/_audit.sh"; audit_log compliance-gates verdict verdict=<green|yellow|red> gates_run=<n> overridden=<true|false>`
- stdout (verdict report)
- Exit code (CI consumption)

**Spawns subagents:**
- Each pack-declared gate, parallel via Agent tool

## Anti-patterns

- **Override without justification** — `--override` requires a justification arg + audit-logs it. Prevents silent bypass.
- **Default skip on "N/A"** — an N/A skill SHOULD be excluded from the total. If unsure → treat as FAIL.
- **Run mid-cycle** — gates run end-of-cycle. Mid-cycle invocation can give false-positive blockers.
- **Hardcoding gate names** — gates come from the active pack only. Never inline a gate list here.

## Failure recovery

- Gate-execution fails (subagent timeout, tool missing): mark the gate as NEEDS_CONTEXT, continue with other gates, surface the count in the verdict
- Total gate failure (no gates executable): exit BLOCKED with diagnostic
- No gates declared (no compliance pack): green/no-op, not a failure
- Override → audit-log entry, do not skip the failed gate; document overridden + justification

## Recommended next steps after invocation

- Green: proceed to /li:ship
- Yellow: assess warnings, fix or document accepted-risk
- Red: address blockers individually then re-run
- For CI integration: add as a non-blocking warn step first, promote to blocking after a clean baseline is established
