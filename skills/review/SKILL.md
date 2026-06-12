---
name: review
layer: foundation
description: Phase 6 of Lintel cycle — adversarial review of BUILD output across 3 stages (spec compliance, code quality, the active pack's compliance gates). Cross-artifact consistency. P1 blocks SHIP.
color: cyan
tools: Read, Bash, Grep, Glob
voice: internal
cli_support: [claude-code, codex]
necessity: STRONGLY_RECOMMENDED
gap_if_skipped: "Unreviewed code reaches SHIP with no signal; spec-compliance and compliance gates never fire yet a ship-ready verdict is asserted."
---

You are the REVIEW skill — Phase 6 of the Lintel cycle.

## What this skill does

Comprehensive adversarial review of BUILD output across three sequential stages. P1 findings block SHIP. The active pack's voice + compliance gates fire if applicable. Produces `review-report.md` + `compliance-report.md`.

Three-stage discipline (extends superpowers' two-stage with compliance):
1. **Spec compliance** — does built code match plan.md requirements exactly?
2. **Code quality** — only after Stage 1 PASS. Quality dimensions per CodeReviewer agent.
3. **Compliance gates** — only after Stage 2 PASS. Fires per the active pack's compliance hooks + voice tier + audience.

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

Invocation: `/li:lessons-surface --keyword "review specification compliance correctness"` (a portable skill call; silent if no relevant matches).

Then read:
- plan.md (from PLAN) — source of requirements
- design doc (from DEFINE) — original intent
- build-log.md (from BUILD) — task outcomes
- review-report.md (if exists, prior REVIEW result)
- CORE-PRINCIPLES.md
- the active pack's compliance gates (`resolve_pack_field compliance.hooks`; none by default)

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

### Step 4 — Stage 3: Compliance gates (fires per the active pack + voice + audience)

Run the active pack's compliance gates (`resolve_pack_field compliance.hooks`; none by default). Each blocks if it fails. A pack contributes its own gate skills/agents; Lintel ships none by default. Typical pack-contributed gates:

**Pack compliance audit** (if the pack defines one):
- Pack-specific compliance sweep (hard-rules + on-demand items as the pack configures)
- Output: per-rule PASS/FAIL with evidence

**Pack voice gate** (if the pack defines voice gates AND audience=customer):
- Run `resolve_pack_field voice.gates_active` (none by default)
- Score against the pack's voice corpus (`resolve_pack_field voice.corpus`; none by default)
- Threshold: ≥85% known-good match per cell
- If <85%: surface, suggest edits, re-score

**Pack agentic-governance gate** (if BUILD includes an agentic system AND the pack defines one):
- Tier classification per the pack's governance framework
- Output: tier (informational / advisory / action-taking / autonomous) + governance posture

**Pack provenance gate** (if the pack activates one AND artifact will ship):
- Log AI-assisted-generation provenance
- Append to repo's provenance log

**`/li:dependency-audit`** (ships with Lintel, always available):
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

**`review-report.md`** (`.claude/runtime/state/review-report-<datetime>.md`):
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
### Pack compliance audit: PASS/FAIL/n-a
### Voice gate: <score>% / n-a
### Provenance: logged / n-a
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

**`compliance-report.md`** (if the active pack defines compliance gates):
- Per-gate breakdown for audit trail
- Path: `.claude/runtime/state/compliance-report-<datetime>.md`

### Step 8 — 00-state.md append

Mechanical since v5.0 (ADR-0008) — one command, not a YAML obligation. `next=` is SHIP, or BUILD on loop-back, or DEFINE on scope gap; per-stage detail lives in review-report.md:

```bash
_sl="${LINTEL_REPO_ROOT:-$(git rev-parse --show-toplevel 2>/dev/null)}/lib/state.sh"
[ -f "$_sl" ] || _sl="$HOME/.lintel/lib/state.sh"; source "$_sl"   # installed by install.sh in consumer repos
state_append REVIEW <DONE|DONE_WITH_CONCERNS|BLOCKED> next=<SHIP|BUILD|DEFINE> review_report_path=<path> p1_findings=<count> p2_findings=<count> p3_findings=<count> ship_ready=<yes|no|yes-with-caveats>
```

## Status protocol

- **DONE** — all stages PASS, P1 findings addressed, ship-ready
- **DONE_WITH_CONCERNS** — P2/P3 findings noted, voice gate <100% but ≥85%
- **BLOCKED** — P1 unfixed OR a blocking compliance gate failed
- **NEEDS_CONTEXT** — review can't proceed without more info (rare)

## Pause-points (MANDATORY)

1. After Stage 1: confirm pass before Stage 2 (don't merge stages)
2. After Stage 2: confirm pass before compliance gates
3. Per P1 finding: operator decision (fix now / defer with rationale / accept-risk via ADR)
4. On a blocking compliance-gate failure: full stop, surface to operator
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
- the active pack's compliance gates (`resolve_pack_field compliance.hooks`; none by default)
- the active pack's voice corpus (`resolve_pack_field voice.corpus`; none by default — if voice gate)
- `.claude/memory/lessons.md` (via `/li:lessons-surface`, keyword-scoped, non-blocking)

**Writes:**
- `.claude/runtime/state/review-report-<datetime>.md`
- `.claude/runtime/state/compliance-report-<datetime>.md` (if the active pack defines compliance gates)
- `.claude/runtime/state/00-state.md` (REVIEW entry)
- `.claude/runtime/audit/review-metrics.jsonl`

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
- EUAIActReviewer — if AI in EU market
- SOC2Reviewer — if SOC2 scope
- PrivacyBoundaryAudit (security/) — if cross-tenant

**Pack-contributed compliance:**
- The active pack's compliance gates (`resolve_pack_field compliance.hooks`; none by default) supply any further reviewers (e.g. agentic-governance, provenance, customer-engagement audits).

**Voice + doc-gen:**
- The active pack's voice gates (`resolve_pack_field voice.gates_active`; none by default) — if a voice tier requires it
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
- **Compliance-gate violation found**: NEVER silently proceed. Hard stop. Operator must fix or explicitly override (rare, never recommended).
- **Cross-artifact analyze finds critical gap**: loop-back to DEFINE (scope problem) or PLAN (decomposition problem), not just BUILD fix.

## Voice tier behavior

`voice: internal`. Review reports are engineering-internal. If the active pack defines voice gates AND a customer-facing artifact is reviewed, the voice-gate output is operator-internal critique but the artifact itself goes through the pack's voice gates (`resolve_pack_field voice.gates_active`; none by default).

## Cycle-position footer

Close your report with the shared position footer so the operator always knows where they are in the
cycle and the one logical next action — whether this phase ran standalone or inside `/li:cycle`:

```bash
source "$LINTEL_REPO_ROOT/lib/cycle-footer.sh"   # fallback: "$(git rev-parse --show-toplevel)/lib/cycle-footer.sh"
render_cycle_footer                               # reads .claude/runtime/state/00-state.md; --compact for short replies
```

Skipped phases render `⊘`; ASCII via `LINTEL_ASCII=1`. See [ADR-0003](../../.claude/decisions/0003-cycle-position-footer.md).
