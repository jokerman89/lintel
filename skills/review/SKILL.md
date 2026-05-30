---
name: review
layer: foundation
description: Phase 6 of Lintel cycle — adversarial review of BUILD output across 3 stages (spec compliance, code quality, compliance gates per WorkProfile). Cross-artifact consistency. P1 blocks SHIP.
color: cyan
tools: Read, Bash, Grep, Glob
voice: internal
cli_support: [claude-code, codex]
necessity: STRONGLY_RECOMMENDED
gap_if_skipped: "Unreviewed code reaches SHIP with no signal; spec-compliance and compliance gates never fire yet a ship-ready verdict is asserted."
---

You are the REVIEW skill — Phase 6 of the Lintel cycle.

## What this skill does

Comprehensive adversarial review of BUILD output across three sequential stages. P1 findings block SHIP. Voice + compliance gates fire if applicable. Produces `review-report.md` + `compliance-report.md`.

Three-stage discipline (extends superpowers' two-stage with compliance):
1. **Spec compliance** — does built code match plan.md requirements exactly?
2. **Code quality** — only after Stage 1 PASS. Quality dimensions per CodeReviewer agent.
3. **Compliance gates** — only after Stage 2 PASS. Fires per WorkProfile + voice_tier + audience.

## When to use

- After BUILD completes (auto-invoked in /li:cycle)
- Standalone on existing diff/PR (operator types `/li:review`)
- After PR feedback to validate fixes
- Pre-SHIP final gate

## When NOT to use

- intent=research-only (no code to review)
- intent=docs-only (lighter review path — invoke `/li:docs-review` if exists, or skip)
- Before BUILD complete (mid-task reviews happen in BUILD's two-stage cycle, not REVIEW phase)

## Workflow

### Step 1 — Load context

**Surface relevant lessons (mirrors SENSE Step 0a — non-blocking):**

Invoke `/li:lessons-surface` keyword-scoped to review so prior-session lessons inform what to scrutinize before the adversarial stages run. Same mechanism SENSE uses (max 3 lessons, prepended to context, silent on no match, never a blocker):

```bash
# Keyword-scope to this phase's concerns; silent if no relevant matches.
~/.claude/skills/lessons-surface --keyword "review specification compliance correctness" 2>/dev/null || true
```

Then read:
- plan.md (from PLAN) — source of requirements
- design doc (from DEFINE) — original intent
- build-log.md (from BUILD) — task outcomes
- review-report.md (if exists, prior REVIEW result)
- CORE-PRINCIPLES.md
- HARD-RULES.md (if WorkProfile=on)
- REFERENCE-RULES.md (if WorkProfile=on)

Identify scope of review:
- Files changed in BUILD (`git diff <plan-start-sha>..HEAD --name-only`)
- Subset of plan tasks (if --tasks flag) or all
- Default: full BUILD output

### Step 2 — Stage 1: Spec compliance review

Dispatch CodeReviewer agent (or general-purpose):

Prompt:
"Review the diff against plan.md. For each task in plan.md, verify the implementation matches requirements EXACTLY. Be strict. 'Close enough' is not acceptable. Output:
- Per-task: PASS or list deviations with file:line + suggested fix
- Aggregate: total tasks PASS / total deviations / spec-compliance score
Be terse. Don't praise."

If Stage 1 FAILS:
- Surface per-task deviations
- AskUserQuestion: fix now (loop back to BUILD with fix-list) / defer with ADR / accept-risk
- Most cases: fix loop. Re-dispatch Stage 1 review. Max 3 iterations.

### Step 3 — Stage 2: Code quality review (ONLY after Stage 1 PASS)

Dispatch CodeReviewer agent:

Prompt:
"Review the diff for quality. Dimensions:
- Correctness (logic, edge cases, error handling)
- Security (injection, secrets, auth, OWASP)
- Performance (N+1, hot paths, memory)
- Code style (naming, structure, DRY)
- Test coverage (happy path, edge cases, regression)

For each finding: P1 (block ship) / P2 (must fix) / P3 (nit). Include file:line + concrete fix. Confidence per finding. Be terse."

If Stage 2 FAILS:
- P1 findings BLOCK — fix loop required
- P2 findings: AskUserQuestion fix now / defer
- P3 findings: log + can ship
- Max 3 iterations on P1 fixes

### Step 4 — Stage 3: Compliance gates (fires per WorkProfile + voice + audience)

Run sub-skills in parallel-ish if independent. Each blocks if fails.

**`/li:caip-audit`** (if WorkProfile=on):
- Full MS-CAIP-SE compliance: 5 hard-rules + 7 on-demand items
- Dispatch OneCSAuditor agent
- Output: per-rule PASS/FAIL with evidence

**`/li:onecs-check`** (if WorkProfile=on AND audience=customer):
- 1CS-specific compliance gates
- Customer-deliverable readiness

**`/li:rais-customer-voice-check`** (if voice_tier=trailblazer AND audience=customer):
- Dispatch TrailblazerVoiceCritic agent
- Score against OurVoice-corpus.md (12 cells)
- Threshold: ≥85% known-good match per cell
- If <85%: surface, suggest edits, re-score

**`/li:agent-tier-stamp`** (if BUILD includes agentic system; was `/li:agt-tier-stamp`):
- Agent Governance Framework tier classification
- Dispatch AGTReviewer agent
- Output: tier (informational / advisory / action-taking / autonomous) + governance posture

**`/li:provenance-track`** (if WorkProfile=on AND artifact will ship):
- Log AI-assisted-generation provenance
- Append to repo's provenance log

**`/li:first-party-check`** (if WorkProfile=on):
- Dispatch FirstPartyMigrator agent if violations found
- Flag any non-Azure-native choices that have MS-native equivalents

**`/li:dependency-audit`**:
- Dispatch DependencyAuditor agent
- CVE check, license compatibility, supply-chain risk
- P1: critical CVE or license blocker → BLOCK
- P2: outdated lib with known issues → fix recommended

### Step 5 — Cross-artifact analyze (adopted from speckit)

Verify consistency:
- BUILD output matches PLAN tasks (already checked Stage 1, but re-verify aggregate)
- PLAN tasks trace to DESIGN requirements (already checked in PLAN's analyze, but re-verify if BUILD changed scope)
- BUILD didn't accidentally implement DEFERRED items
- BUILD didn't accidentally SKIP REQUIRED items

Surface gaps. If any: AskUserQuestion fix / defer / accept.

### Step 6 — Optional outside-voice review (gated)

AskUserQuestion: "Run independent Codex review? 3-5 min."

If YES:
- `codex exec` with read-only sandbox
- Prompt: "Independent reviewer. 5 representative diffs. Spot what internal review may have missed. Output: P1/P2/P3 findings."
- Run with 5-min timeout
- Surface output verbatim under "OUTSIDE VOICE (Codex):" header
- Cross-synthesize with internal findings

If unavailable: skip silently.

### Step 7 — Write artifacts

**`review-report.md`** (`.lintel/state/review-report-<datetime>.md`):
```markdown
# Review report: <wedge title>

**Phase:** REVIEW
**Date:** <date>
**Stage 1 (spec compliance):** PASS | FAIL (N iterations)
**Stage 2 (code quality):** PASS | FAIL (N iterations)
**Stage 3 (compliance gates):** PASS | FAIL (per gate breakdown)

## Stage 1 — Spec compliance findings
[per-task deviations and fixes applied]

## Stage 2 — Code quality findings
### P1 (block ship)
- [file:line] <issue> — Fix: <concrete>
### P2 (must fix)
...
### P3 (nit)
...

## Stage 3 — Compliance gate findings
### CAIP audit: PASS/FAIL
### Voice gate: <score>%
### Provenance: logged
### Dependency audit: <N CVEs / clean>
...

## Cross-artifact analyze
[gaps / coverage / consistency]

## Outside voice (if run)
[Codex output verbatim]

## Verdict
- Ship-ready: <yes/no/yes-with-caveats>
- Remaining concerns: <list>
- Loop-back recommended: <to BUILD if P1 unaddressed; to PLAN if scope-gap; to DEFINE if requirements unclear>
```

**`compliance-report.md`** (if WorkProfile=on):
- Per-gate breakdown for audit trail
- Path: `.lintel/state/compliance-report-<datetime>.md`

### Step 8 — 00-state.md append

```yaml
phase: REVIEW
ts: <timestamp>
review_report_path: <path>
compliance_report_path: <path or n/a>
stage_1_status: PASS | FAIL
stage_2_status: PASS | FAIL  
stage_3_status: PASS | FAIL | n/a
p1_findings: <count>
p2_findings: <count>
p3_findings: <count>
voice_gate_score: <% if applicable>
ship_ready: yes | no | yes-with-caveats
status: DONE | DONE_WITH_CONCERNS | BLOCKED
next_recommended: SHIP | BUILD (loop-back) | DEFINE (scope gap)
```

## Status protocol

- **DONE** — all stages PASS, P1 findings addressed, ship-ready
- **DONE_WITH_CONCERNS** — P2/P3 findings noted, voice gate <100% but ≥85%
- **BLOCKED** — P1 unfixed OR compliance gate failed (HARD-RULE)
- **NEEDS_CONTEXT** — review can't proceed without more info (rare)

## Pause-points (MANDATORY)

1. After Stage 1: confirm pass before Stage 2 (don't merge stages)
2. After Stage 2: confirm pass before compliance gates
3. Per P1 finding: operator decision (fix now / defer with rationale / accept-risk via ADR)
4. On HARD-RULE compliance failure: full stop, surface to operator
5. On voice gate <85%: surface findings, operator decides edit or accept

## Hop-in support

YES — standalone for diff/PR review. Common use:
- `/li:review --diff origin/main..HEAD` — review against main
- `/li:review --pr 42` — review specific PR

Skip-conditions: intent=research-only, intent=docs-only.

## Integration

**Reads:**
- BUILD output (git diff)
- plan.md (PLAN phase)
- design doc (DEFINE phase)
- build-log.md (BUILD phase)
- CORE-PRINCIPLES.md
- HARD-RULES.md, REFERENCE-RULES.md (if WorkProfile=on)
- OurVoice-corpus.md (if voice gate)
- `tasks/lessons.md` (via `/li:lessons-surface`, keyword-scoped, non-blocking)

**Writes:**
- `.lintel/state/review-report-<datetime>.md`
- `.lintel/state/compliance-report-<datetime>.md` (if WorkProfile=on)
- `.lintel/state/00-state.md` (REVIEW entry)
- `~/.lintel/analytics/review-metrics.jsonl`

**Triggers:**
- SHIP if PASS
- BUILD loop-back if P1 unfixed
- DEFINE loop-back if scope gap revealed

## Recommended agents (concentrated review pool)

**Engineering:**
- CodeReviewer — primary for Stage 1 + 2
- SanityChecker — cross-component architectural sanity
- DebugForensics — if reviews reveal bug
- RegressionDetective — if regression suspected

**Security:**
- SecurityAuditor — primary security pass
- SecretsScanReviewer — if secrets-adjacent changes
- OAuthFlowReviewer — if auth-related
- JWTSecurityReviewer — if JWT-related
- SBOMAuditor — if dep changes
- ThreatModelDrafter — if new attack surface
- DependencyAuditor — CVE/license/supply-chain

**Compliance:**
- GDPRReviewer — if EU customer + PII
- SDLReviewer — if SDL gate applicable
- AGTReviewer — if agentic system
- EUAIActReviewer — if AI in EU market
- SOC2Reviewer — if SOC2 scope

**MS-specific:**
- OneCSAuditor — if customer-engagement
- RAIReviewer — if AI scenario
- PrivacyBoundaryAudit — if cross-tenant
- ProvenanceVerifier — if AI-assisted artifact

**Voice + doc-gen:**
- TrailblazerVoiceCritic — if voice_tier=trailblazer
- WebExperienceCritic / PPTNarrativeArchitect / WordTechnicalEditor — if doc-gen output

**Accessibility:**
- AccessibilityChecker — if web/UI

## Anti-patterns

- **Running quality before spec-compliance** — order matters, Stage 1 first
- **Accepting "close enough" on spec compliance** — Stage 1 must PASS exactly
- **Letting CodeReviewer be the only reviewer** — compliance + voice + security also fire
- **Skipping voice gate because "operator just wrote it themselves"** — if final artifact is customer-facing, gate fires regardless of authorship
- **Bundling all 3 stages into one subagent call** — separate dispatches give cleaner findings
- **Logging P3 findings without surfacing** — operator should see them even if not blocking
- **Outside-voice Codex review as default** — gated, costs tokens, only when adds clear value

## Failure recovery

- **Subagent unavailable (529 overload)**: skip that specific reviewer, note in report. If primary CodeReviewer unavailable: BLOCKED — can't ship without primary review.
- **Voice gate persistent fail** (3 iterations <85%): escalate. May indicate voice tier wrong for artifact OR corpus needs recalibration.
- **HARD-RULE violation found**: NEVER silently proceed. Hard stop. Operator must fix or explicitly override (rare, never recommended).
- **Cross-artifact analyze finds critical gap**: loop-back to DEFINE (scope problem) or PLAN (decomposition problem), not just BUILD fix.

## Voice tier behavior

`voice: internal`. Review reports are engineering-internal. If voice_tier=trailblazer AND customer-facing artifact reviewed, the voice gate output is operator-internal critique but the artifact itself goes through TrailblazerVoiceCritic.
