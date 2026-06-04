---
name: capture
layer: foundation
description: Phase 8 of Lintel cycle — durable capture. Lessons updated, ADR drafted, EVOLUTION-LOG appended, cold-executor handoff trio REAFFIRMED against build evidence (trio born in PLAN per v3.8 Feature 2.2, not here). Cross-session continuity.
color: cyan
tools: Read, Write, Edit, Bash, Grep, Glob
voice: internal
cli_support: [claude-code, codex]
necessity: STRONGLY_RECOMMENDED
gap_if_skipped: "Lessons, ADRs, and EVOLUTION-LOG entries are never written and the cold-executor trio is never reaffirmed against build evidence; cross-session continuity is lost and the next operator re-derives everything."
---

You are the CAPTURE skill — Phase 8 (final) of the Lintel cycle.

## What this skill does

Closes the cycle by capturing what's durable. The work is shipped; CAPTURE makes sure the NEXT operator (could be you in 6 months, or a teammate, or a fresh cold session) can pick up where this ended without re-deriving everything.

Five artifact categories:
1. **Lessons** — corrections from BUILD/REVIEW → `tasks/lessons.md` (filtered, durable patterns only)
2. **ADR** — non-trivial decisions → `docs/adr/NNNN-<slug>.md`
3. **EVOLUTION-LOG** — CLAUDE.md changes → log entry
4. **Cold-executor handoff trio** — reaffirm `spec.md` + `plan.md` + `prompt.md` against build evidence (trio BORN in PLAN per v3.8 Feature 2.2; CAPTURE only annotates with actual-build outcomes)
5. **Operator profile** — append session entry to `~/.lintel/state/operator-profile.jsonl` for tier tracking

Plus role-debrief (if role active) and retro (optional).

## When to use

- After SHIP completes successfully
- After failed cycle (BLOCKED state) for capturing what was learned even without ship
- Standalone post-implementation reflection
- Pre-handoff to teammate or to your future-self

## When NOT to use

- Mid-cycle (premature)
- For trivial single-file edits (no lessons/ADR worth capturing)
- intent=research-only ended (light capture only — retro + maybe lessons)

## Workflow

### Step 1 — Cycle history aggregation

Read entire cycle's `.lintel/state/00-state.md` log. Extract:
- Phases completed + their durations + token cost
- Corrections operator made during BUILD/REVIEW (from build-log)
- Decisions taken (alternatives chosen in DEFINE, scope changes in PLAN)
- Reviewer concerns from REVIEW
- Compliance gates that fired + outcomes

This is the source data for capture artifacts.

### Step 2 — Lessons capture (filtered)

Invoke `/li:learn` (or inline):

For each correction operator made during the cycle:
- Was this correction GENERAL (would apply to future work) or SPECIFIC (one-time)?
- If GENERAL: candidate for `tasks/lessons.md`
- If SPECIFIC: keep in this cycle's notes only

Examples of LESSON-worthy:
- "Don't mock the vendor SDK in tests — last 3 cycles' tests passed but prod failed because mocks diverged from real API"
- "Always map the codebase first when planning infra work — saved 90 min on this engagement"

Examples NOT lesson-worthy:
- "Use specific port 8443 in this customer's deployment" — too specific
- "Forgot to update README" — operational, not a pattern

AskUserQuestion per candidate lesson: "Capture? (yes / no / edit-first)"

If yes: append to `tasks/lessons.md`:
```markdown
## <date> — <lesson title>
<lesson body>
<-- Captured from cycle <cycle-id> by <operator>. -->
```

### Step 3 — Promote lesson check (NEW)

For each NEW lesson captured, AskUserQuestion: "Promote to Lintel global lessons (scaffolding/01-foundation/tasks/lessons.md)? — applies to ALL future scaffolded repos."

If yes: invoke `/li:lessons-promote`.

This is how operator-discovered patterns become team-wide knowledge.

### Step 4 — ADR draft (if non-trivial decision)

Scan cycle history for non-trivial decisions:
- Architectural picks (alternative A vs B chosen)
- Pattern adoptions (new pattern introduced)
- Trade-off decisions (accepted P3 finding, deferred P2)
- Scope changes (descoped feature, added scope)

For each candidate, AskUserQuestion: "Draft ADR for this decision?"

If yes: invoke `/li:adr-new "<decision title>"`:
- Reads `docs/adr/TEMPLATE.md`
- Auto-numbers (NNNN)
- Substitutes title + date + status (Proposed)
- Operator fills Context / Decision / Consequences / Alternatives during draft
- Commits on feature branch
- Suggested status: Accepted (if implemented this cycle) or Proposed (if forward decision)

### Step 5 — EVOLUTION-LOG append (if CLAUDE.md changed)

```bash
# Detect CLAUDE.md changes in cycle
CLAUDE_CHANGED=$(git diff <cycle-start-sha>..HEAD --name-only | grep -c '^CLAUDE.md')

if [ "$CLAUDE_CHANGED" -gt 0 ]; then
  # Append to EVOLUTION-LOG.md
  cat >> EVOLUTION-LOG.md <<EOF
## <date> — <cycle title>
- Change: <brief>
- Why: <rationale>
- Cycle: <cycle-id>
- Commit: <sha>
EOF
fi
```

Auto-append (not optional) when CLAUDE.md changes — this is the audit trail for how guidance evolves.

### Step 6 — Cold-executor handoff trio (REAFFIRM, v3.8 Feature 2.2)

**v3.8 change:** the trio (plan.md + spec.md + prompt.md) is now BORN TOGETHER in PLAN, not split across PLAN+CAPTURE. CAPTURE's job here is to RE-AFFIRM the trio against actual-build evidence — not generate.

**`spec.md` reaffirm** (born in PLAN):
- Verify spec.md still matches actual implementation
- Update interfaces/contracts that drifted during BUILD (annotated as post-build-evidence)
- Status: APPROVED (from PLAN) — unchanged unless drift detected

**`plan.md` reaffirm** (born in PLAN):
- Annotate plan.md tasks with actual STATUS (DONE/SKIPPED/DEFERRED) from build-log
- Acceptance criteria post-verification (which actually passed)

**`prompt.md` reaffirm** (born in PLAN, v3.8 Feature 2.2 moved birth to PLAN):
- Verify prompt.md still describes the work accurately
- Add any "What you DON'T need to know" entries discovered during BUILD
- Path: root `prompt.md` OR `docs/plans/<slug>/prompt.md` (born by PLAN, lives there)

**Why moved to PLAN:** standalone `/li:plan <design.md>` (workflow_root post-v3.8) needs to produce the complete trio at PLAN-time. CAPTURE-only generation broke that — operator running PLAN solo got 2/3 of a handoff. Trio born together fixes this.

AskUserQuestion: "Want to dogfood the trio? Spawn fresh subagent with ONLY these 3 files + verify it can describe what was built." (Optional verification step — same as before, but now against finalized trio.)

### Step 7 — Role debrief (if role was active)

If role was active during cycle:
- Review role's OUTCOME LENS per phase against actual outcomes
- Did role lens add value? Where did it conflict with engineering reality?
- Update role file with any new INSIGHTS learned (operator confirms)
- Sensitivity-aware: if role is private, updates stay in `~/.lintel/roles/private/<role-id>.md`

### Step 8 — Retro (optional, light)

Append to `~/.lintel/retros/<date>-<cycle-id>.md`:
```yaml
cycle_id: <id>
duration_human: <hours>
duration_cc: <minutes>
tokens_used: <approx>
cost_estimate_dollars: <X>

what_worked:
  - <thing>
what_friction:
  - <thing>
next_time:
  - <pattern to repeat>
  - <pattern to avoid>
```

Not always written — only if cycle was substantial enough that retro adds value (operator-driven).

### Step 9 — Operator profile update (gstack-inherited)

Append to `~/.lintel/state/operator-profile.jsonl`:
```json
{
  "ts": "<timestamp>",
  "cycle_id": "<id>",
  "mode": "<preset>",
  "audience": "<audience>",
  "phases_completed": ["SENSE", "DEFINE", ...],
  "tokens_used": <N>,
  "duration_minutes": <N>,
  "outcome": "DONE | DONE_WITH_CONCERNS | BLOCKED",
  "lessons_captured": <count>,
  "lessons_promoted": <count>,
  "adrs_drafted": <count>,
  "trio_finalized": <yes/no>,
  "voice_gate_avg": <% if applicable>
}
```

Used by SENSE in future sessions for tier-tracking + welcome-back-recognition (gstack pattern adapted).

### Step 10 — 00-state.md final entry

```yaml
phase: CAPTURE
ts: <timestamp>
cycle_complete: true
artifacts_produced:
  - lessons_captured: <count>
  - lessons_promoted: <count>
  - adrs_drafted: <count>
  - evolution_log_appended: <yes/no>
  - spec_md_finalized: <path>
  - plan_md_finalized: <path>
  - prompt_md_written: <path>
  - retro_written: <yes/no>
  - role_debriefed: <yes/no>
operator_profile_updated: yes
cycle_summary:
  total_duration: <hours>
  total_tokens: <N>
  cost_estimate: <$X>
  outcome: <DONE | DONE_WITH_CONCERNS | BLOCKED>
status: DONE
next_action: cycle_complete
```

### Step 11 — Closing message

Tight closing per gstack pattern (intrapreneurship-adapted, not YC plea):

```
LINTEL CYCLE COMPLETE — <wedge title>

Duration: <hours human / <minutes> CC
Cost: $<X> | Tokens: <N>
Outcome: <DONE / DONE_WITH_CONCERNS / BLOCKED>

Artifacts produced:
- Code: <commit range>
- spec.md, plan.md, prompt.md (cold-executor trio)
- Lessons captured: <N> (<N> promoted to Lintel global)
- ADRs drafted: <N>
- Customer deliverables: <list>

Operator-pattern noted:
- <specific observation 1>
- <specific observation 2>
- <specific observation 3>

Next actions:
- Trio is in <path> — ready for future cold-session re-execution
- /li:resume picks up next cycle from here
```

## Status protocol

- **DONE** — all artifacts written, profile updated
- **DONE_WITH_CONCERNS** — captured but operator deferred ADR draft or lessons capture
- **BLOCKED** — only if filesystem unavailable (rare)

## Pause-points (mostly operator-confirms)

- Per candidate lesson: AskUserQuestion capture / skip / edit
- Per candidate ADR: AskUserQuestion draft now / draft later / skip
- After trio drafted: AskUserQuestion "Verify with dogfood subagent?" (optional)
- Role debrief (if active): AskUserQuestion "Update role file with these insights?"

## Hop-in support

YES — standalone post-implementation reflection. Useful if operator forgot CAPTURE in prior session.

## Integration

**Reads:**
- All `.lintel/state/00-state.md` entries from cycle
- `.lintel/state/build-log.md`
- `.lintel/state/review-report-*.md`
- `.lintel/state/compliance-report-*.md` (if the active pack defines compliance gates)
- design doc, plan.md (DRAFT), spec.md (DRAFT)
- Cycle's git diff for change scope
- role file (if active)

**Writes:**
- `tasks/lessons.md` (append per captured lesson)
- `docs/adr/NNNN-<slug>.md` (new ADR if drafted)
- `EVOLUTION-LOG.md` (if CLAUDE.md changed)
- `spec.md` (FINALIZED from PLAN's draft)
- `plan.md` (FINALIZED with post-verification status)
- `prompt.md` (NEW — cold-executor handoff)
- `~/.lintel/retros/<date>-<cycle-id>.md` (optional)
- `~/.lintel/state/operator-profile.jsonl` (append)
- `~/.lintel/roles/<id>.md` (update if role active + insights to add)
- `.lintel/state/00-state.md` (CAPTURE final entry)
- `~/.lintel/analytics/cycle-completion.jsonl`

**Triggers:**
- Nothing automatically — cycle complete
- `/li:resume` available for next cycle
- If part of multi-cycle engagement: next cycle starts at SENSE or DEFINE

## Recommended agents

- **ADRDrafter** (engineering/) — primary, ADR drafting
- **ChangelogMaintainer** (engineering/) — release-note polish if SHIP didn't already
- **DocWriter** (engineering/) — synthesize cold-executor trio prose
- The active pack's voice gates (`resolve_pack_field voice.gates_active`; none by default) — if any CAPTURE artifact ships outside (rare)

## Anti-patterns

- **Auto-adding every correction to lessons.md** — filter for durable patterns only (operator confirms each)
- **Drafting ADR for trivial decisions** — ADR has overhead, reserve for decisions worth preserving
- **Skipping cold-executor trio because "we shipped already"** — the trio is the durable artifact, more valuable than the PR after months pass
- **Polluting role-file with session-specific data** — role files are persistent identity, not session log
- **Forgetting to update operator profile** — gstack pattern for cross-session tier tracking
- **Long retro write-up when cycle was small** — retro is optional + light

## Failure recovery

- **lessons.md missing**: create via `bin/li-scaffold` template, then proceed
- **docs/adr/TEMPLATE.md missing**: prompt operator to run `bin/li-scaffold init` first
- **operator can't decide on lesson capture**: capture as PROVISIONAL (low confidence flag), they can promote/remove later
- **CLAUDE.md changed but operator says "not significant"**: skip EVOLUTION-LOG, but log audit-trail note

## Voice tier behavior

`voice: internal`. CAPTURE artifacts are mostly engineering-internal. Customer-facing release notes (if shipped from CAPTURE) follow the active pack's voice tier (`resolve_pack_field voice.default_tier`; default: internal).
