# Brief Forge — universal hand-off gate

**Last updated:** 2026-05-29 (v4.0 Phase 3)
**Status:** Concept doc — referenced by `skills/brief-forge/SKILL.md`, `lib/brief-forge.sh`, `lib/brief-forge-evaluators.sh`, `lib/envelope-schema.yaml`

> Every hand-off in Lintel — skill spawning a subagent, phase transitioning to the next phase, workflow handing to another workflow, plan + spec + prompt born together for a cold executor — carries an envelope. Brief Forge is the **gate that constructs that envelope, runs evaluators on it, scores completeness, audits the result, and surfaces escape hatches**. It is what makes hand-offs uniform across the harness.

## The problem

Pre-v4.0 hand-offs were ad-hoc. Each kind of hand-off shaped its payload differently:

- Subagent spawn: parent skill wrote a free-form prompt
- Phase transition: phase appended to 00-state.md and the next phase read it
- Cold-executor: plan + spec + prompt files in `.claude/runtime/state/`

Three failure modes:

1. **Drift across hand-off kinds.** Five hand-offs, five shapes. Operators learning Lintel encountered different vocabularies. Tooling couldn't audit uniformly.
2. **No completeness signal.** A hand-off either worked or broke; there was no shared score telling the receiver "this brief is at 65/100; expect to need escape hatches."
3. **No replay.** When a hand-off produced bad output, the brief that caused it lived in whatever file the original skill wrote. After cleanup or compaction, it was gone.

Brief Forge fixes all three by being **the single gate every hand-off passes through**.

## The model

```
Source skill (e.g. plan)
    │
    │ wants to hand off to receiver (e.g. PlanReviewer)
    ▼
Brief Forge invoked with: kind, from, to, content_type, content_file
    │
    ▼
Step 1: resolve pack policy
    │  pack.brief_forge_handoffs.on_<kind>.{enabled, evaluators, budget_tokens}
    │  pack.brief_forge_handoffs.cold_path_bypass.eligible_skills
    ▼
Step 2: cold-path-bypass check
    │  if from in eligible_skills OR enabled = false → write stub audit + exit 0
    ▼
Step 3: construct envelope
    │  forge_envelope_head + forge_envelope_body
    │  HEAD: envelope_id, schema_version, kind, from, to, issued_at, pack, operator, voice_tier
    │  BODY: content_type, content (from content_file)
    ▼
Step 4: run evaluators (parallel where possible)
    │  evaluator_security, _completeness, _stale, _sdl_compliance, _trailblazer_alignment
    │  each returns {score, budget_used, notes}
    │  stop on budget exhaustion
    ▼
Step 5: compose tail
    │  completeness_score = min(evaluator scores)
    │  evaluators_run = list of evaluator names
    │  escape_hatches = built per content_type
    │  audit_pointer = .claude/runtime/audit/envelopes-<date>.jsonl
    ▼
Step 6: write audit + emit envelope
    │  envelope written to audit JSONL
    │  envelope emitted to stdout (receiver consumes)
    ▼
Step 7: score-based decision
    │  score < 40 → escalate to operator (block hand-off)
    │  score 40-59 → warn (receiver should expect to use escape hatches)
    │  score ≥ 60 → proceed
```

The pack policy determines which evaluators run for which event. Operators tune this per-pack without changing skill code.

## The five evaluators

`lib/brief-forge-evaluators.sh` ships five. All return JSON `{score: 0-100, budget_used: int, notes: string}`. Lower score = worse envelope.

### security

Scans for known-dangerous patterns: secret strings (API keys, OAuth tokens), shell-injection markers (`$(rm -rf`, `curl ... | sh`), prompt-injection markers (`ignore previous instructions`, `system: you are now`). Mechanical-first via regex.

Score impact: secret detected = -60, shell-injection = -40, prompt-injection = -30. Clean envelope = 100.

### completeness

Checks content_type-specific required fields. For `content_type: brief`, requires `task`, `constraints`, `acceptance`. For `spec`, requires `intent`, `inputs`, `outputs`. For `plan`, requires `tasks`.

Score impact: each missing required field = -25 (brief/spec) or -50 (plan). Complete = 100.

### stale

Verifies `context_pointers` (file paths or URLs in the envelope's BODY) still exist at hand-off time. Envelopes can be issued + replayed minutes/hours later; the world may have moved.

Score impact: each missing pointer = -30, capped at 0.

### sdl_compliance

Verifies SDL hooks ran on the payload. Mechanical check: does the active pack's SDL audit log contain a recent invocation tied to the envelope's `from` or `to`? Used by `ms-internal` and `caip-se` packs.

Score impact: no SDL audit log = 60 (acceptable for non-MS packs, fails for ms-internal); SDL invocation found = 100; no match = 70 (warn).

### trailblazer_alignment

Only runs when `head.voice_tier: trailblazer`. Mechanical voice check: scans for AI-corporate clichés (`delve into`, `crucial`, `robust`, `leverage`, `seamlessly integrate`) and em-dashes (per voice rules: no em-dashes).

Score impact: cliché detected = -35, em-dash present = -10. Clean = 100. When voice_tier ≠ trailblazer: evaluator is no-op (returns 100).

## Score aggregation

`aggregate_evaluator_scores` returns the MINIMUM score across evaluators. Rationale: a brief that passes 4 evaluators at 100 but fails security at 30 is a 30-quality brief, not an 82-quality brief. The worst evaluator wins.

If you average, you can hide a serious problem behind several mild successes. The receiver acts on the score; they need to know if there's a serious problem.

## Cold-path-bypass

Brief Forge has performance cost. For some hand-offs the cost isn't worth it:

- **Hotfix workflow** — operator is in fast-iteration mode; evaluators add friction without much value
- **Operator input** — operator's curated input doesn't need Brief Forge evaluation (the operator IS the evaluator)

Two ways to bypass:

1. **Skill frontmatter:** add `brief_forge_bypass: true` to the source skill's SKILL.md frontmatter. Brief Forge sees this at Step 2 and writes a stub audit entry instead of constructing/evaluating.
2. **Pack policy:** `pack.yaml.brief_forge_handoffs.cold_path_bypass.eligible_skills: [hotfix, ...]`. Operator opts a pack out of forging for specific source skills.

Either way, the bypass is audited so the trail survives. Operators inspecting `.claude/runtime/audit/brief-forge.jsonl` see `kind: brief_forge_bypassed` entries with reason.

## Budget enforcement

`pack.yaml.brief_forge_handoffs.budget_tokens` caps total budget per hand-off (default 5000; ms-internal 6000; caip-se 7000 for the extra Trailblazer evaluator).

Each evaluator declares `budget_used` in its JSON return. Brief Forge sums consumption per hand-off and stops invoking further evaluators when the budget is exhausted. The completeness score reflects only the evaluators that ran.

Why total budget vs per-evaluator: gives pack authors a single tuning knob. If a Phase 4 module adds a heavy LLM-backed evaluator, the budget can grow once at the pack level instead of per-evaluator.

## Audit + replay

Every envelope is appended to `.claude/runtime/audit/envelopes-<date>.jsonl` (per-day file for log rotation). The envelope is the audit record — there's no separate log of "Brief Forge ran"; the envelope itself is the evidence.

`bin/li-envelope-replay <envelope-id>` pulls the envelope from the audit log and dry-runs it: surfaces what the receiver would do, given current state of the world. `--apply` actually re-invokes the receiver (audited as `envelope_replay_applied`).

`bin/li-forge-stats` (planned — not yet shipped) will aggregate envelopes across audit logs and report per-skill / per-pack completeness over time. Operators use this to spot evaluators that are too strict (too many low scores) or skills that consistently produce bad briefs (always needing escape hatches).

## Hand-off events

Five events trigger Brief Forge. Each can be enabled/disabled per-pack:

| Event | Trigger | Typical evaluators (default _default) | ms-internal adds | caip-se adds |
|---|---|---|---|---|
| `subagent_spawn` | Parent skill spawns subagent | [security, stale] | sdl_compliance | (inherited) |
| `phase_transition` | Phase N → Phase N+1 | [completeness] | (inherited) | trailblazer_alignment |
| `workflow_handoff` | One workflow → another | [completeness] | sdl_compliance | trailblazer_alignment |
| `cold_executor` | plan + spec + prompt born together (v3.8) | [security, completeness] | sdl_compliance | (inherited) |
| `operator_input` | Operator → skill | DISABLED (operator-curated) | — | — |

Per-pack overrides via `pack.yaml.brief_forge_handoffs.<event>.{enabled, evaluators}`.

## Why this matters for v4.0

Brief Forge is the **interlock that makes packs meaningful in practice**. Without it, packs declare their evaluator preferences in `pack.yaml.brief_forge_handoffs` but nothing enforces them. With Brief Forge as a mandatory gate, the pack's policy is what runs.

Phase 4 modules wire their hand-offs through Brief Forge automatically. A `tech_architecture_review` content_type can be added without changing the gate — the gate already supports content_type dispatch.

## Anti-patterns

- **Bypassing without audit** — every bypass writes a stub entry; silent bypass is a bug
- **Aggregating scores as average** — minimum is correct; average hides serious problems
- **Skipping the audit_pointer** — the envelope IS the audit; no audit = no replay = no debuggability
- **Ignoring budget exhaustion** — surface that not all evaluators ran; the score is partial
- **Forging recursively** — Brief Forge doesn't forge envelopes for its own evaluator runs
- **Hardcoding evaluator weights** — minimum-score aggregation means each evaluator is binary-veto-capable; weights would mask serious problems

## Integration points

**Reads:**
- `lib/envelope-schema.yaml` (envelope shape)
- `lib/pack-resolver.sh` (pack policy)
- `lib/brief-forge.sh` (envelope helpers)
- `lib/brief-forge-evaluators.sh` (5 evaluators)
- Content file passed in (varies by content_type)

**Writes:**
- `.claude/runtime/audit/envelopes-<date>.jsonl` (per-envelope, the audit-of-record)
- `.claude/runtime/audit/brief-forge.jsonl` (per-forge stats: who-when-score-budget)
- stdout (the envelope, for receiver consumption)

**Triggered by:**
- Every skill's hand-off operation
- Hooks (Phase 4): `hooks/shared/brief-forge-pre-spawn.sh`, `hooks/shared/brief-forge-pre-phase.sh`

**Tested by:**
- `tests/unit/brief-forge-evaluator-runs.sh`
- `tests/shape/brief-forge-evaluators-present.sh`
- `tests/shape/every-handoff-uses-envelope.sh`
