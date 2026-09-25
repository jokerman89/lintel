---
name: review
layer: foundation
description: Use after BUILD, before SHIP, to adversarially review what was built — checks spec compliance, code quality, the active pack's compliance gates, and cross-artifact consistency. A P1 finding blocks SHIP until resolved.
color: cyan
tools: Read, Bash, Grep, Glob
voice: internal
cli_support: [claude-code, codex, copilot]
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
- intent=docs-only may use proportionate inline review, but selected documents still bind to acceptance and delivery evidence
- Before BUILD complete (mid-task reviews happen in BUILD's two-stage cycle, not REVIEW phase)

## Workflow

### Resolve authoritative artifacts before review

If this initiative has a committed work.json, validate the explicit map with
`bin/li-work-artifacts.py` using the [shared work-map contract](../spec-kit/references/work-map.md).
Use mapped `spec` for requirements, `plan` for technical decisions, and `tasks` for every task
ID and acceptance check. All “plan.md requirements/tasks” below refer to these mapped sources;
reference-only Lintel companions are navigation, not duplicate specifications. Compare actual
code and evidence to the original Spec Kit tasks. A work-map approval never replaces review.

Before reviewing, follow [the shared evidence procedure](references/evidence.md):
prepare an explicit selection and immutable context with package/leaf acceptance,
base, staged/unstaged/new/deleted content, attempt, profile and required controls.
Use the actual builder and reviewer invocation identities. Substantive work requires
separately corroborated independent review; missing delegation means a durable manual
handoff, not role-play. A reviewer reports findings and never repairs their own findings.

### Swarm integrated-tree close gate

When the validated work map explicitly selects `execution_mode: "swarm"`, REVIEW starts only on
the reconciled integration branch declared by the coordination document:

```bash
repo="${LINTEL_REPO_ROOT:-$(git rev-parse --show-toplevel)}"
if [ -n "${LINTEL_SOURCE_ROOT:-}" ]; then
  source_root="$LINTEL_SOURCE_ROOT"
elif [ -n "${CLAUDE_PLUGIN_ROOT:-}" ]; then
  source_root="$CLAUDE_PLUGIN_ROOT"
else
  echo "NEEDS_CONTEXT: trusted Lintel source root unavailable; set LINTEL_SOURCE_ROOT" >&2
  exit 1
fi
[ -f "$source_root/bin/li-swarm.py" ] || { echo "NEEDS_CONTEXT: trusted swarm helper missing" >&2; exit 1; }
python3 "$source_root/bin/li-swarm.py" verify --repo "$repo" --coord "$coordination"
```

Other host adapters substitute/export their installed bundle path as `LINTEL_SOURCE_ROOT`; tests and
self-checks set it explicitly. The working repository is data supplied only through `--repo`, never
an executable-source fallback.

The gate requires every worker report and distinct two-stage lane review to be structurally valid
and PASS. Also confirm that each attributable passing change set is present on the declared
integration branch, generated reducers were rebuilt after producer fan-in, and focused integration
checks passed there. Evidence left only in an isolated worktree is not integrated completion.

After this gate, run all three ordinary REVIEW stages across the full integrated diff. Per-lane
reviews reduce fan-in risk but never replace specification, quality, compliance, or security review
of the reconciled system. A missing independent lane review stays BLOCKED on every host; sequenced or
no-subagent execution changes concurrency only, not evidence requirements.


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
- The prepared snapshot's selected files and states, including dirty/new files and deletions;
  a commit-range diff is supporting context, not the complete review boundary
- Subset of plan tasks (if --tasks flag) or all
- Default: full BUILD output

### Step 2 — Stage 1: Spec compliance review

Dispatch CodeReviewer agent (or general-purpose) with the shared
[Review Method](references/method.md) packet for stage `spec`. Keep packet files in an owned
run directory outside the review selection, for example
`run="$LINTEL_REPO_ROOT/.claude/runtime/review/<cycle-or-review-id>"`. Render the packet once
from the prepared snapshot's selected content, with every selected requirement or leaf ID:

```bash
python3 "$LINTEL_SOURCE_ROOT/bin/li-review-packet.py" --repo "$LINTEL_REPO_ROOT" render \
  --kind implementation --stage spec --acceptance <ID> [--acceptance <ID> ...] \
  --subject-file <selected diff/content> --subject-ref "<branch or package>" \
  --body-out "$run/inputs/stage1.md" --meta-out "$run/inputs/stage1.json" \
  --request-out "$run/records/stage1.request.md" --requested-by "<operator via session>" --surface <client>
```

Send the rendered request unchanged. The method sets the strictness ("close enough" is a
deviation) and the report shape; validate the reply with
`li-review-packet.py check --report <reply> --meta "$run/inputs/stage1.json"`. Any
`deviation` row fails Stage 1 (outcome `changes-requested`: fix loop, defer with ADR or
accept-risk). A missing, duplicated or `unverified` acceptance row, or a header that
contradicts the findings, is `incomplete` (exit 3): re-request it, never score it as PASS.

Record exact `pass`, `fail`, `unverified` or `error` per acceptance control and map
every selected leaf to its evidence. A missing acceptance result blocks that leaf;
scores cannot average it away.

If Stage 1 FAILS:
- Surface per-task deviations
- AskUserQuestion: fix now (loop back to BUILD with fix-list) / defer with ADR / accept-risk
- Most cases: fix loop. Re-dispatch Stage 1 review. Max 3 iterations.

### Step 3 — Stage 2: Code quality review (ONLY after Stage 1 PASS)

Dispatch CodeReviewer agent with the method packet for stage `quality`, rendered the same
way with `--stage quality` and the confirmed surface tags (`li-review-packet.py tags`
proposes them from the changed paths and diff; you confirm and pass `--tags`). The packet
carries the selected standing questions, the evidence levels and the one severity rubric:
P1 blocks ship, P2 is fixed before ship unless explicitly accepted, P3 is a nit; confidence
never changes severity. `check` returns `incomplete` when a selected question lacks a
status or evidence; re-request instead of treating the silence as a pass.

If Stage 2 FAILS:
- P1 findings BLOCK — fix loop required
- P2 findings: AskUserQuestion fix now / defer
- P3 findings: log + can ship
- Max 3 iterations on P1 fixes

### Step 4 — Stage 3: Compliance gates (fires per the active pack + voice + audience)

Resolve required-policy status before using the active pack's controls. Use
`evaluate_controls` / `li-review-evidence.py controls`, not failure counts or an
average. Each applicable **mandatory** fail/error/unverified result blocks; advisory
findings remain advisory. Unknown applicability or a failed required profile load is
not a neutral exemption. A pack contributes its own gate skills/agents; examples:

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

**Dependency audit** (dispatch the `DependencyAuditor` agent — ships with the plugin fleet):
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

If unavailable: record the optional pass as unverified. It cannot replace the
required independent reviewer or supply a fictitious observation.

### Step 6b — Optional MARS panel mode (gated)

Standalone review only: when `li-mars.py offer` (caller `review`, live host facts, no
cycle route) returns 0 and MARS was not already offered or declined for this target,
offer it once. Inside a cycle the only offer belongs to PLAN; never offer here. With
consent, run [MARS](../mars/SKILL.md) with the same method packet and stage as the single
reviewer it replaces, bound to the same selection (`panel init --caller review --select <path>
--method-meta <meta>`; an unbound REVIEW panel is never complete). REVIEW records
its own stage decision through the existing content-bound path from the adjudicated
result (`synthesis-header --adjudicated` outcome, `panel inspection` record); MARS itself
never marks the review PASS. Surface panel findings under "MARS (multi-model):".
Declined or unavailable: continue the single-reviewer path unchanged and say nothing
unless the operator asked for MARS.

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

## MARS (multi-model, if run)
[synthesis header, adjudicated findings, preserved dissent, inspection record path]

## Verdict
- Ship-ready: <yes/no/yes-with-caveats>
- Remaining concerns: <list>
- Loop-back recommended: <to BUILD if P1 unaddressed; to PLAN if scope-gap; to DEFINE if requirements unclear>
```

**`compliance-report.md`** (if the active pack defines compliance gates):
- Per-gate breakdown for audit trail
- Path: `.claude/runtime/state/compliance-report-<datetime>.md`

Keep these human-readable artifacts and persist the version-2 decision using the
[shared writer/reader](references/evidence.md). Include unverified/error and grounded
not-applicable controls, full leaf coverage, content-hashed evidence links and
declared actor provenance. Only the shared reader's strict result can set ship-ready;
a heading in this report or a historical positive string cannot. The prepared
`qa_requirements` owns QA IDs/kinds/mandatory applicability/policy; review results
must match it, not redefine it. V1 evidence requires fresh preparation and review
for v2 clearance, without rewriting its history.

### Step 8 — 00-state.md append

Mechanical since v5.0 (ADR-0008) — one command, not a YAML obligation. `next=` is SHIP, or BUILD on loop-back, or DEFINE on scope gap; per-stage detail lives in review-report.md:

```bash
_sl="${LINTEL_SOURCE_ROOT:-${LINTEL_REPO_ROOT:-$(git rev-parse --show-toplevel 2>/dev/null)}}/lib/state.sh"
[ -f "$_sl" ] || _sl="$HOME/.lintel/lib/state.sh"; source "$_sl"   # installed by install.sh in consumer repos
state_append REVIEW <DONE|DONE_WITH_CONCERNS|BLOCKED> next=<SHIP|BUILD|DEFINE> review_report_path=<path> p1_findings=<count> p2_findings=<count> p3_findings=<count> ship_ready=<yes|no|yes-with-caveats>
```

## Status protocol

- **DONE** — all required stages and leaf acceptance verified for the selected result, strict reader clear
- **DONE_WITH_CONCERNS** — P2/P3 findings noted, voice gate <100% but ≥85%
- **BLOCKED** — any required failure/error/unverified result, stale content or outstanding independent review
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

Skip-condition: intent=research-only. Documentation-only work uses proportionate
review, not an exemption from selected-content and acceptance binding.

## Integration

**Reads:**
- BUILD output (git diff)
- optional swarm coordination plus all lane reports/reviews and integration attribution
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
- **Reviewing isolated lanes instead of the reconciled branch** — run the swarm close gate, confirm
  integration, then review the complete integrated diff
- **Treating lane review as final REVIEW** — both per-lane and integrated review are required

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
source "${LINTEL_SOURCE_ROOT:-$LINTEL_REPO_ROOT}/lib/cycle-footer.sh"   # fallback: "${LINTEL_SOURCE_ROOT:-$(git rev-parse --show-toplevel)}/lib/cycle-footer.sh"
render_cycle_footer                               # reads .claude/runtime/state/00-state.md; --compact for short replies
```

Skipped phases render `⊘`; ASCII via `LINTEL_ASCII=1`. See [ADR-0003](../../.claude/decisions/0003-cycle-position-footer.md).
