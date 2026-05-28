---
name: handoff-size-check
layer: foundation
description: Handoff-size-warning tied to 500k cap. Per v3.6 backlog 3.2 — elephant-hint och token-cap som samma mekanism från två ändar.
color: yellow
tools: Read, Bash, Glob, Grep
voice: internal
cli_support:
  - cli: claude-code
    level: full
  - cli: codex
    level: degraded
---

You are the `handoff-size-check` skill — pre-handoff payload-validation mot 500k cap.

## What this skill does

När operator picks "kör ändå" på broad idea (elephant-hint default), the plan declares its own handoff size. Om plan's payload närmar sig 500k cap → natural warning point ("denna plan yields ~480k handoff, near cap — stycka?").

Per v3.6 backlog 3.2 — kompletterar 3.1 elephant-hint + 2.1 500k cap som **samma mekanism från två ändar:**
- Elephant-hint (3.1): catches broad idea BEFORE plan-writing
- Handoff-size-check (3.2): catches large plan AFTER plan-writing
- Cleanare än två separata systems.

## When to use

- **Post-PLAN-phase auto** — `/li:cycle` invokes denna efter PLAN.md är klar
- **Standalone audit** — `/li:handoff-size-check <plan.md>` → check specific plan
- **Pre-cold-executor-handoff** — verifierar trio + warming totalt < cap

## When NOT to use

- Mid-plan-writing (warning vs partial plan är false-positive)
- Single-skill estimate — använd `/li:context-budget` direkt
- Real-time monitoring — denna är batch-check vid handoff-points

## Workflow

### Step 1 — Locate plan + warming-manifest

```bash
PLAN_FILE="${1:-.lintel/state/PLAN.md}"
WARMING_FILE=".lintel/state/warming-manifest.md"  # från context-warm-* invocations
[ -f "$PLAN_FILE" ] || { echo "No plan found at $PLAN_FILE"; exit 2; }
```

### Step 2 — Compute payload size

```bash
# Cold-executor trio sizes
spec_size=$(wc -c < .lintel/state/spec.md 2>/dev/null || echo 0)
plan_size=$(wc -c < "$PLAN_FILE")
prompt_size=$(wc -c < .lintel/state/prompt.md 2>/dev/null || echo 0)

# Warming projected loads
warming_total=0
if [ -f "$WARMING_FILE" ]; then
  # Parse warming-manifest för per-load file-sizes
  while IFS= read -r line; do
    if [[ "$line" =~ ^load:[[:space:]]*([0-9]+) ]]; then
      warming_total=$((warming_total + ${BASH_REMATCH[1]}))
    fi
  done < "$WARMING_FILE"
fi

# Convert bytes to tokens (rough: 1 token ≈ 4 bytes)
trio_tokens=$(( (spec_size + plan_size + prompt_size) / 4 ))
warming_tokens=$(( warming_total / 4 ))
total_tokens=$(( trio_tokens + warming_tokens ))
```

### Step 3 — Apply mode-aware cap (per 2.1)

Read current mode från `~/.lintel/profile.yaml`. Look up cap från context-budget mode_envelopes:

```yaml
hotfix:              { soft: 200k, hard: 300k }
customer-engagement: { soft: 500k, hard: 750k }
research-dive:       { soft: 750k, hard: 900k }
demo-prep:           { soft: 300k, hard: 450k }
internal-tool:       { soft: 400k, hard: 600k }
```

### Step 4 — Surface verdict

```
HANDOFF SIZE CHECK — <mode> mode (cap: <soft>k soft / <hard>k hard)
══════════════════════════════════════════════════════════════════

Plan + trio:      <X>k tokens (~<%> of soft cap)
Warming projected: <Y>k tokens
TOTAL HANDOFF:    <Z>k tokens

Status:
  Z < soft  → ✅ GREEN — proceed
  soft ≤ Z < hard → ⚠ YELLOW — near cap, consider:
    - Stycka planet (split into 2 smaller phases)
    - Skip --skip-warming-<X> on lowest-priority warming target
    - Switch till research-dive mode (higher cap) if research-justified
  Z >= hard → ⛔ RED — exceeds cap, MUST reduce:
    - Plan is too broad → stycka now
    - Warming includes too many files → cut to essentials
    - Mode mismatch → consider research-dive

Suggested next step: <auto-recommendation>
```

Return code: 0 (green), 1 (yellow), 2 (red).

### Step 5 — Audit-log

```bash
jq -nc --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  --arg plan "$PLAN_FILE" --arg mode "$mode" \
  --arg total "$total_tokens" --arg verdict "$verdict" \
  '{ts:$ts, plan:$plan, mode:$mode, total_tokens:$total|tonumber, verdict:$verdict}' \
  >> ~/.lintel/audit/handoff-size-checks.jsonl
```

## Voice tier behavior

`voice: internal`. Operator-internal pre-handoff gate.

## Status protocol

- **DONE** — check klar, verdict green
- **DONE_WITH_CONCERNS** — yellow verdict (near cap warnings)
- **BLOCKED** — red verdict (exceeds cap) — operator must address before handoff
- **NEEDS_CONTEXT** — no plan-file at default path och `--plan` arg saknas

## Pause-points

- Red verdict: hard-block för operator-decision (stycka / cut warming / abort handoff)
- Yellow verdict: surface options + ask if proceed (override OK with justification)
- Missing warming-manifest: assume warming = 0 + warn att estimate kan vara low

## Hop-in support

YES — solo-invocable. Designed för auto-invocation från `/li:cycle` Step 5
(post-PLAN, pre-handoff).

## Integration

**Reads:**
- `.lintel/state/PLAN.md` (or `--plan <path>` override)
- `.lintel/state/spec.md`, `prompt.md` (cold-executor trio)
- `.lintel/state/warming-manifest.md`
- `~/.lintel/profile.yaml` (current mode → cap)
- skills/context-budget/SKILL.md mode_envelopes

**Writes:**
- `~/.lintel/audit/handoff-size-checks.jsonl`
- stdout (verdict report)
- Return code (CI/script consumption)

**Consumed by:**
- `/li:cycle` (auto-invocation post-PLAN)
- Operator (pre-handoff manual check)
- `/li:ship` (could integrate som ship-gate)

## Anti-patterns

- **Auto-cut warming utan operator-approval** — cap-violation surfaces options;
  operator decides which warming targets stay.
- **Override red verdict utan justification-log** — `--override "<reason>"` logs
  intent. Silent bypass = future-debugging-pain.
- **Token-budget i bytes** — Lintel cap is in tokens. Convert at compute time.

## Failure recovery

- Plan-file unreadable: exit BLOCKED med diagnostic
- Mode unknown: fall back till customer-engagement defaults + warn
- Warming-manifest absent: assume 0 warming, surface "estimate may be low"

## Recommended next steps after invocation

- Green: proceed med cold-executor handoff
- Yellow: review warming-list för cut-candidates, consider stycka
- Red: address blocker (stycka / cut / mode-change), re-run check
- Pair med `/li:context-budget --report` för deeper headroom-analysis
