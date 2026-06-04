---
name: brief-forge
layer: foundation
description: Phase 3 v4.0 — universal hand-off gate. Constructs envelopes per lib/envelope-schema.yaml + runs evaluators on every subagent_spawn / phase_transition / workflow_handoff / cold_executor / operator_input per pack policy.
color: cyan
tools: Read, Write, Bash
voice: internal
cli_support: [claude-code, codex]
---

You are the BRIEF-FORGE — the universal hand-off gate at every workflow boundary.

## What this skill does

Every time control passes from one component to another in Lintel, Brief Forge:
1. **Constructs an envelope** per `lib/envelope-schema.yaml` (HEAD + BODY + TAIL)
2. **Runs evaluators** per active pack's `brief_forge_handoffs.<event>.evaluators` list
3. **Scores completeness** (0-100) and writes to `tail.completeness_score`
4. **Audits the envelope** to `~/.lintel/audit/envelopes-<date>.jsonl`
5. **Surfaces escape hatches** the receiver can use if context is insufficient

Five hand-off events trigger Brief Forge:

| Event | Trigger | Default pack policy |
|---|---|---|
| `subagent_spawn` | Parent skill spawns a subagent | enabled, evaluators: [security, stale] |
| `phase_transition` | Phase N → Phase N+1 within a cycle | enabled, evaluators: [completeness] |
| `workflow_handoff` | One workflow hands to another | enabled, evaluators: [completeness] |
| `cold_executor` | plan + spec + prompt born together (v3.8) | enabled, evaluators: [security, completeness] |
| `operator_input` | Operator → skill (curated input) | DISABLED by default (operator-curated) |

Per-pack overrides in `brief_forge_handoffs.<event>.{enabled, evaluators}`.

## When to use

- AUTOMATICALLY: every hand-off in Lintel triggers Brief Forge unless the source skill declares `brief_forge_bypass: true` or operator passes `--no-brief-forge`
- DIRECT: `/li:brief-forge <kind> <from> <to> <content_type> <content_file>` to construct an envelope manually (e.g. for testing)

## When NOT to use

- Inside Brief Forge itself (no recursive forging)
- For audit-only emissions (those are logged but skip evaluators)
- When `pack.yaml.brief_forge_handoffs.<event>.enabled: false`

## Workflow

### Step 1 — Resolve pack policy

```bash
source "$LINTEL_REPO_ROOT/lib/pack-resolver.sh"
source "$LINTEL_REPO_ROOT/lib/brief-forge.sh"
source "$LINTEL_REPO_ROOT/lib/brief-forge-evaluators.sh"

kind="${1:?usage: brief-forge <kind> <from> <to> <content_type> <content_file>}"
from="${2:?}"
to="${3:?}"
content_type="${4:?}"
content_file="${5:?}"

event_field="on_${kind}"
enabled=$(resolve_pack_field "brief_forge_handoffs.${event_field}.enabled")
evaluators_csv=$(resolve_pack_field "brief_forge_handoffs.${event_field}.evaluators")
budget=$(resolve_pack_field brief_forge_handoffs.budget_tokens)
budget="${budget:-5000}"
```

### Step 2 — Cold-path-bypass check

```bash
# Source skill frontmatter may declare brief_forge_bypass: true
bypass_eligible_csv=$(resolve_pack_field brief_forge_handoffs.cold_path_bypass.eligible_skills)

# Check if source ("from") is in eligible_skills CSV
case ",$bypass_eligible_csv," in
  *",$from,"*)
    # Bypass — write a stub audit entry and return
    write_bypass_audit "$kind" "$from" "$to"
    exit 0
    ;;
esac

# Check enabled flag from pack policy
if [ "$enabled" != "true" ]; then
  write_bypass_audit "$kind" "$from" "$to"
  exit 0
fi
```

### Step 3 — Construct envelope (HEAD + BODY + TAIL)

```bash
envelope_path=$(mktemp)
trap 'rm -f "$envelope_path"' EXIT

forge_envelope_head "$kind" "$from" "$to" > "$envelope_path"
forge_envelope_body "$content_type" "$content_file" >> "$envelope_path"
```

`forge_envelope_head` generates:
```yaml
head:
  envelope_id: <ULID>
  envelope_schema_version: "1"
  kind: <kind>
  from: <from>
  to: <to>
  issued_at: <ISO 8601 UTC>
  cycle_id: <if inside a cycle>
  pack: <active pack name>
  operator: <whoami>
  voice_tier: <resolved>
```

`forge_envelope_body` validates content against the content_type's schema rules in `lib/envelope-schema.yaml`.

### Step 4 — Run evaluators

```bash
budget_used=0
declare -a evaluator_results

IFS=',' read -ra evaluators <<< "$evaluators_csv"
for e in "${evaluators[@]}"; do
  e=$(printf '%s' "$e" | tr -d '[:space:]')
  [ -z "$e" ] && continue

  # Each evaluator runs against the envelope, returns score + notes + budget consumed
  result=$(run_evaluator "$e" "$envelope_path")
  evaluator_results+=("$e:$result")

  # Sum budget consumed; stop if budget exhausted
  eval_cost=$(printf '%s' "$result" | jq -r '.budget_used // 0' 2>/dev/null || echo 0)
  budget_used=$((budget_used + eval_cost))

  if [ "$budget_used" -gt "$budget" ]; then
    echo "WARN: Brief Forge budget ($budget) exhausted after evaluator '$e'" >&2
    break
  fi
done
```

`run_evaluator <name> <envelope_path>` dispatches to `lib/brief-forge-evaluators.sh` functions:
- `evaluator_security`
- `evaluator_completeness`
- `evaluator_stale`
- `evaluator_compliance` (the active pack's compliance gates; none by default)
- `evaluator_voice_alignment` (the active pack's voice tier)

Each returns JSON `{score: 0-100, budget_used: N, notes: "..."}`.

### Step 5 — Compose tail + finalize

```bash
# Aggregate completeness score (min of all evaluator scores, weighted by importance)
completeness_score=$(aggregate_evaluator_scores "${evaluator_results[@]}")

# Compose escape hatches (per content_type)
escape_hatches=$(build_escape_hatches "$content_type" "$from")

# Audit pointer
audit_dir="${LINTEL_HOME:-$HOME/.lintel}/audit"
audit_path="$audit_dir/envelopes-$(date -u +%Y-%m-%d).jsonl"
mkdir -p "$audit_dir"

forge_envelope_tail "$completeness_score" "${evaluator_results[@]}" "$escape_hatches" "$audit_path" >> "$envelope_path"
```

### Step 6 — Write audit + emit envelope

```bash
# Write the envelope as a single JSON line to audit
envelope_json=$(yaml_to_json "$envelope_path")
echo "$envelope_json" >> "$audit_path"

# Emit envelope to stdout (for the receiver to consume)
cat "$envelope_path"

# Brief Forge stats
ts=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
printf '{"ts":"%s","kind":"brief_forge_emitted","event":"%s","from":"%s","to":"%s","completeness":%d,"budget_used":%d,"evaluators_run":%d}\n' \
  "$ts" "$kind" "$from" "$to" "$completeness_score" "$budget_used" "${#evaluators[@]}" \
  >> "$audit_dir/brief-forge.jsonl"
```

### Step 7 — Score-based decision

```bash
# Per design doc §2.2 Brief Forge: low scores escalate
if [ "$completeness_score" -lt 40 ]; then
  echo "BRIEF FORGE: completeness score $completeness_score < 40 — ESCALATE to operator" >&2
  exit 1
fi

if [ "$completeness_score" -lt 60 ]; then
  echo "BRIEF FORGE: completeness score $completeness_score < 60 — receiver should expect to use escape hatches" >&2
fi

exit 0
```

## Status protocol

- **DONE** — envelope constructed, evaluators clean, score ≥ 60
- **DONE_WITH_CONCERNS** — envelope constructed, score 40-59 (receiver should use escape hatches)
- **BLOCKED** — score < 40 (escalates to operator) OR evaluator returned hard fail OR budget exhausted before evaluators ran
- **NEEDS_CONTEXT** — content_file missing or content_type unknown

## Pause-points

- Step 7 if score < 40: surface to operator, wait for re-invoke or skip-decision
- Operator passes `--no-brief-forge` to bypass entirely (audited as override)

## Hop-in support

None — Brief Forge is invoked on hand-off events, not standalone.

## Integration

**Reads:**
- `lib/envelope-schema.yaml` (envelope shape)
- `lib/pack-resolver.sh` (pack policy)
- `lib/brief-forge.sh` (envelope helpers)
- `lib/brief-forge-evaluators.sh` (5 evaluators)
- Content file passed in (varies by content_type)

**Writes:**
- `~/.lintel/audit/envelopes-<date>.jsonl` (per-envelope audit)
- `~/.lintel/audit/brief-forge.jsonl` (per-forge stats)
- stdout (the envelope, for receiver consumption)

**Triggered by:**
- Every skill's hand-off operation
- `hooks/shared/brief-forge-pre-spawn.sh` (auto-fire before subagent spawn)
- `hooks/shared/brief-forge-pre-phase.sh` (auto-fire on phase transition)

## Anti-patterns

- **Bypassing without audit** — every bypass writes a stub audit entry; silent bypass is a bug
- **Aggregating scores as average** — minimum is the right aggregation (one bad evaluator = bad envelope)
- **Skipping the audit_pointer** — the envelope IS the audit; no audit = no replay = no debuggability
- **Ignoring budget exhaustion** — if evaluators couldn't finish, the score is partial; surface that
- **Forging recursively** — Brief Forge does not forge envelopes for its own evaluator runs
