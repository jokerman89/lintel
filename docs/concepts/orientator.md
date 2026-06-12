# Orientator — lightweight workflow routing at SENSE

**Last updated:** 2026-05-29 (v4.0 Phase 3)
**Status:** Concept doc — referenced by `skills/orientator/SKILL.md`, `lib/orientator-routing.sh`, `skills/sense/SKILL.md` (Step 0d)

> The operator types a prompt. Sometimes it's "fix the broken button" — obviously a hotfix. Sometimes it's "what should I do?" — genuinely ambiguous. The orientator is the **mechanical-first router** that turns prompts into workflow recommendations, escalates to LLM only when mechanical confidence falls below the pack's threshold, and writes every decision to an audit log the operator can inspect.

## The problem

Pre-v4.0 routing happened three ways:
- Operator typed `/li:cycle --mode hotfix` (explicit, always works)
- Operator typed `/li:cycle --mode auto` and SENSE used a hardcoded intent classifier
- Operator typed something ambiguous and got the default cycle with all 8 phases

Three failure modes:

1. **No pack-awareness.** The hardcoded classifier couldn't honor pack-specific routing (a CAIP-SE pack wants different defaults from a hotfix-heavy internal-tool pack).
2. **All-or-nothing LLM.** Either the LLM ran every time (expensive) or never (no escalation when needed).
3. **No audit.** Routing decisions were ephemeral. Operators couldn't see what classifier produced what recommendation — no feedback loop.

The orientator fixes all three by being a **lightweight agent invoked at SENSE that reads pack policy + applies mechanical heuristics + escalates to LLM only when mechanical confidence is low + audits every decision**.

## The model

```
Operator prompt
       │
       ▼
SENSE Step 0d invokes orientator
       │
       ▼
lib/orientator-routing.sh::classify_intent
       │  (mechanical keyword + path heuristics)
       ▼
match_workflow(intent, pack.navigation.default_workflow)
       │
       ▼
assess_risk(workflow, pack.navigation.high_risk_workflows)
       │
       ▼
score_confidence(intent, workflow)
       │
       ▼
check_escalation_threshold(confidence, pack.navigation.escalation_threshold)
       │  yes → invoke_llm_orientation (v4.0 stub; Phase 4 wires real subagent)
       │  no  → use mechanical result
       ▼
Decision:
       │  auto_start (low-risk + high-confidence + pack auto_mode_eligible)
       │  confirm_with_operator (high-risk OR low-confidence)
       │  surface_and_wait (default)
       ▼
Audit to .claude/runtime/audit/orientator-decisions.jsonl
       │
       ▼
SENSE report surfaces recommendation
```

Three layers of decision: mechanical classify → pack-policy lookup → escalation gate.

## Pack-configurable parameters

All four parameters live in `pack.yaml.navigation.*`:

| Field | Type | Default | What it controls |
|---|---|---|---|
| `default_workflow` | string | `cycle` | Fallback workflow when intent unclear |
| `high_risk_workflows` | list[string] | `[cycle, plan, ship]` | Workflows that always require confirm |
| `orientator_budget_tokens` | int | 2000 | LLM budget cap when escalating |
| `orientator_max_output_tokens` | int | 200 | LLM output cap |
| `escalation_threshold` | enum | medium | When to escalate (never / low / medium / high) |
| `auto_mode_eligible` | bool | false | Master gate for auto-start of low-risk + high-confidence |

Per design doc §1.4: the tweak from operator's spec is that all four parameters are pack-overridable. A research-heavy pack might want `escalation_threshold: low` (escalate often, intent is harder to detect). A hotfix-heavy pack might want `escalation_threshold: high` (rarely escalate, intents are usually clear).

## Mechanical-first routing

`classify_intent` returns one of eight intents using keyword heuristics. First match wins, so order matters:

1. `fix` — keywords: bug, broken, error, crash, "fix", fixa, felsök
2. `ship` — keywords: ship, release, deploy, shippa, landa
3. `review` — keywords: review, audit, "check", granska
4. `research` — keywords: research, explore, understand, utforska, förstå
5. `scaffold` — keywords: scaffold, "new project", "new repo", nytt projekt, starta
6. `resume` — keywords: resume, continue, "pick up", fortsätt
7. `build` — keywords: build, add, implement, "new feature", bygg, lägg till
8. `unclear` — none of the above; falls back to `pack.navigation.default_workflow`

Swedish + English keywords reflect operator language. Adding a language is one PR per keyword block.

## Mapping intent → workflow

| Intent | Workflow |
|---|---|
| build | `/li:cycle` |
| fix | `/li:cycle --mode hotfix` |
| review | `/li:review` |
| research | `/li:cycle --mode research-dive` |
| ship | `/li:cycle --from SHIP` |
| scaffold | `bin/li-scaffold init` |
| resume | `/li:resume` |
| unclear | `<pack.navigation.default_workflow>` |

The mapping is hardcoded in `lib/orientator-routing.sh::match_workflow`. Operators wanting to override per-pack add a `pack.yaml.navigation.intent_overrides:` block (Phase 4 enhancement; v4.0 ships with the hardcoded mapping).

## Risk assessment

`assess_risk` returns `low | medium | high`:

- **high** — workflow is in pack's `high_risk_workflows` CSV (default: cycle, plan, ship)
- **medium** — `--mode hotfix` (touches code without full review)
- **low** — `--mode research-dive` (read-only)
- **medium** — default

Risk determines whether the operator gets auto-start or confirm-pause.

## Confidence scoring

`score_confidence` returns `low | medium | high`:

- **high** — explicit keyword match (intent ∈ {build, fix, review, research, ship, scaffold, resume})
- **low** — intent is `unclear` (defaulted to pack workflow)
- **medium** — anything else (currently unreachable; reserved for future heuristics)

Confidence determines whether escalation fires.

## Escalation threshold

`check_escalation_threshold(confidence, threshold)` returns `yes` if confidence < threshold:

| confidence \ threshold | never | low | medium | high |
|---|---|---|---|---|
| **low** | no | no | yes | yes |
| **medium** | no | no | no | yes |
| **high** | no | no | no | no |

At `escalation_threshold: medium` (default): low confidence escalates, medium and high don't.

## Auto-mode decision

Per design doc §1.4 auto-mode level (b):
- Low-risk workflows + high confidence + pack `auto_mode_eligible: true` → **auto_start**
- High-risk workflows OR low confidence → **confirm_with_operator**
- Otherwise → **surface_and_wait** (default; operator decides)

Even with auto-mode active, the operator can interrupt at any phase boundary.

## v4.0 LLM stub

`invoke_llm_orientation` is a stub in v4.0 that returns `{source: mechanical, budget_used: 0, recommendation: <default_workflow>}`. This keeps v4.0 ship cost-bounded and deterministic.

Phase 4 will wire a real subagent (probably `OrientatorAgent` with budget-bounded prompt, parsing a structured JSON output). The interface stays the same so the SENSE integration doesn't change.

## Audit trail

Every routing decision writes to `.claude/runtime/audit/orientator-decisions.jsonl`:

```jsonl
{"ts":"2026-05-29T15:00:00Z","kind":"orientator_decision","intent":"fix","workflow":"/li:cycle --mode hotfix","risk":"medium","confidence":"high","decision":"confirm_with_operator","budget_used":0,"escalated":false,"operator":"<operator>"}
```

Operators inspect via `bin/li-doctor --orientator-stats` (Phase 4 tool) or by grepping the audit log directly. The audit is the feedback loop — if the orientator consistently misroutes a particular prompt pattern, the operator surfaces it as a bug and the routing heuristics get tightened.

## Integration with SENSE

SENSE Step 0d runs orientator after Step 0c (meta-infra detection) and before Step 1 (read configuration). Why Step 0d:
- After 0c so meta-infra cycles get the recommendation in the SENSE report
- Before Step 1 because the orientator's recommendation influences which workflow context to load

The orientator's output surfaces in the SENSE report (Step 7) as a routing recommendation block:

```
ORIENTATOR
==========
Recommended:  /li:cycle --mode hotfix
Intent:       fix       (high confidence, mechanical)
Risk:         medium
Decision:     confirm_with_operator
```

## When NOT to invoke

- Operator already typed an explicit `--mode <preset>` — orientator skipped
- Operator already typed `--from <phase>` — orientator skipped
- Mid-cycle (orientator is for cycle entry, not phase transitions)
- Pack has no `navigation` block (validation should reject the pack first)

## Anti-patterns

- **LLM-first routing** — mechanical first; LLM only on escalation. Per design doc §1.4: "Mechanical-first, LLM on escalation"
- **Ignoring pack policy** — `default_workflow`, `high_risk_workflows`, `escalation_threshold`, `auto_mode_eligible` all come from pack
- **Auto-starting high-risk workflows** — even with `auto_mode_eligible: true`, high-risk requires explicit confirm
- **Skipping the audit** — every routing decision goes to the JSONL audit. No audit = no feedback loop = drift over time
- **Hardcoding keywords** — keyword list lives in `lib/orientator-routing.sh::classify_intent` so it's editable in one place

## Integration points

**Reads:**
- Operator's last message (passed in by SENSE)
- `lib/pack-resolver.sh` for pack policy
- `.claude/runtime/state/00-state.md` (optional — for resume detection)

**Writes:**
- `.claude/runtime/audit/orientator-decisions.jsonl`
- stdout (recommendation block surfaced in SENSE report)

**Public functions in lib/orientator-routing.sh:**
- `classify_intent <prompt>` → intent enum
- `match_workflow <intent> <default>` → workflow string
- `assess_risk <workflow> <high_risk_csv>` → risk enum
- `score_confidence <intent> <workflow>` → confidence enum
- `check_escalation_threshold <confidence> <threshold>` → yes|no
- `invoke_llm_orientation <prompt> <default> <budget>` → JSON (v4.0 stub)

**Tested by:**
- `tests/unit/orientator-mechanical-routing.sh`
- `tests/shape/orientator-decisions-audited.sh`
