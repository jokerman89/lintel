---
name: ship
layer: foundation
description: Use after REVIEW passes, when reviewed work is ready to land, to open a PR, deploy, or hand off to a customer — runs the active pack's final compliance hard-stops, voice gates on customer-facing artifacts, and pack-configured CI/deploy validation. The cycle's last gate before code leaves the repo.
color: cyan
tools: Read, Bash, Edit, Grep, Glob
voice: mixed
cli_support: [claude-code, codex]
necessity: REQUIRED
gap_if_skipped: "No deployment validation, rollback plan, or audit log; production mutations without authorization."
---

You are the SHIP skill — Phase 7 of the Lintel cycle.

## What this skill does

Ships the BUILD output via PR (default) or direct-push (with explicit per-batch authorization). Customer-deliverables go through the doc-gen pipeline. Release notes generated.

Hard-stops from the active pack's compliance gates (`resolve_pack_field compliance.hooks`; none by default). When a pack activates them, typical gates include:
- customer-data in commit
- secrets in any file
- prod-mutations without explicit per-call auth

The active pack's voice gates (`resolve_pack_field voice.gates_active`; none by default) fire on customer-facing artifacts.

## When to use

- After REVIEW PASS, ship-ready=yes
- Operator types `/li:ship` to ship existing branch
- Doc-gen customer-deliverable shipping (PPT/Word/Web with 4-gate pipeline)
- Demo deliverable handoff to customer

## When NOT to use

- REVIEW returned BLOCKED (P1 unfixed) → fix loop, then ship
- intent=research-only — no ship
- intent=local-dev-only — operator works locally, no ship
- intent=draft-PR-only — use lighter PR-open without compliance gates

## Workflow

### Step 1 — Pre-flight (MANDATORY)

Verify ship-readiness:
- `git status` is clean OR operator confirms uncommitted is intentional
- Current branch is NOT main (unless explicit per-batch direct-push auth)
- All tests pass (run `/li:qa` if not already passed in REVIEW)
- review-report.md shows PASS (or operator overrides with documented rationale)
- compliance-report.md shows PASS (if the active pack defines compliance gates)
- `.claude/runtime/state/analyze-report.md` verdict surfaced if present (ADR-0004; advisory — RED/YELLOW
  goes to the operator with the findings table, it does not auto-block)

If pre-flight fails: BLOCKED. Don't proceed.

### Step 2 — Audience + voice classification

From mode + role:
- audience: solo / team / customer
- voice_tier: internal / mixed / trailblazer
- artifact_kind: code-only / docs / customer-deliverable / demo

Determines which gates fire in subsequent steps.

### Step 3 — Compliance hard-stop check (active pack's gates)

Run the active pack's compliance gates (`resolve_pack_field compliance.hooks`; none by default). NEVER bypassable when present. Re-verify even if REVIEW passed (last-second pre-ship sanity). Example gates a pack may activate:

```bash
# Customer data
grep -rE '(customer-name-patterns|PII-patterns)' --include='*.md' --include='*.ts' --include='*.json' staged_files
# Secrets
gitleaks detect --staged
# Production mutations without auth
# (operator-specific, check for prod-deploy commands or live-cloud-mutation)
```

If ANY gate violation:
- HARD STOP
- Surface to operator: violation + file:line + recommended fix
- Operator MUST fix or explicitly override (rarely warranted)
- Log the stop mechanically (one line; ts/operator/cycle_id come from the envelope):

```bash
source "$(git rev-parse --show-toplevel)/bin/_audit.sh"
audit_log compliance-stops gate_violation gate=<gate> file=<file:line> resolution=<fixed|overridden>
# → .claude/runtime/audit/compliance-stops.jsonl
```

### Step 4 — Voice + brand gate (if customer-facing)

If `audience=customer` AND the active pack defines voice gates (`resolve_pack_field voice.gates_active`; none by default):
- Run the pack's voice gates (already done in REVIEW Stage 3, but final verification)
- If new edits since REVIEW: re-run
- Threshold: ≥85% known-good match against the pack's voice corpus (`resolve_pack_field voice.corpus`)

If `artifact_kind=customer-deliverable` (PPT/Word/Web):
- Invoke `/li:generate-ppt` / `-word` / `-web` pipeline; gates derive from the active pack:
  1. Voice gate (`resolve_pack_field voice.gates_active`; none by default)
  2. Brand-conformance (`resolve_pack_field brand.templates`; default-fallback if null)
  3. Honest-limitations (AI-disclaimer present?)
  4. Provenance (AI-assistance logged?)
- All configured gates must PASS for customer-shippable

### Step 5 — Provenance tracking (if the active pack requires it)

If the active pack activates a provenance gate (`resolve_pack_field compliance.hooks`; none by default):
- Log AI-assistance provenance for the shipped artifact — one line via the unified writer (ts/operator/cycle_id come from the envelope; the audit dir is already repo-scoped in v5 repos, so no `<repo>-` prefix in the filename):

```bash
source "$(git rev-parse --show-toplevel)/bin/_audit.sh"
audit_log provenance-log shipped branch=<branch> commit_range=<sha>..<sha> ai_assistance=lintel-cycle \
  phases=<DEFINE,PLAN,BUILD,REVIEW,SHIP> audience=<audience> voice_tier=<tier> gates_passed=<gate1,gate2>
# → .claude/runtime/audit/provenance-log.jsonl
```

If audience=customer AND an AI-system shipped: if the pack provides a transparency-note generator, draft a transparency note for the customer.

### Step 6 — Choose ship path

```yaml
ship_path:
  # PR (default, recommended)
  pr:
    - git push -u origin <branch>
    - gh pr create with structured body
    - PR includes: design-doc link, plan.md link, review-report link, compliance-report link
  
  # Direct-push (requires explicit per-batch auth)
  direct_main:
    - operator must explicitly authorize: "commit and merge"
    - the active pack's compliance gates re-checked
    - merge commit message includes review-report path
  
  # Demo handoff (no PR, customer deliverable)
  demo:
    - generate customer artifact (PPT/Word/Web via 4-gate pipeline)
    - operator distributes via approved channel
    - provenance logged
```

Operator chooses path via flag or auto-detect from artifact_kind.

### Step 7 — PR creation (default path)

```bash
# Use gh CLI
gh pr create --title "<short title>" --body "$(cat <<'EOF'
## Summary
[1-3 bullets from design doc]

## Design + Plan
- Design: <docs/design/lintel-*-design-*.md>
- Plan: <plan.md>
- Review report: <review-report.md>
- Compliance report: <compliance-report.md if applicable>

## Test plan
[Bulleted checklist from plan.md acceptance criteria]

## Provenance
AI-assisted via /li:cycle
Phases: DEFINE → PLAN → BUILD → REVIEW → SHIP
Operator review: passed REVIEW phase

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

Apply CODEOWNERS auto-request. Note required reviewers.

### Step 8 — CI / deploy validation (if the active pack configures deploy targets)

If the active pack defines CI/deploy targets (and provides validation skills for them), run them here. Generic targets work out of the box:
- GHActionsReviewer (devops/) if GH Actions involved
- TerraformReviewer / K8sManifestReviewer (devops/) if infra ship

Pack-specific deploy pipelines (e.g. ring-based or canary strategies) are contributed by the active pack and run via the pack's own validation skills; none ship with Lintel by default.

### Step 9 — Customer-deliverable generation (if applicable)

For artifact_kind=customer-deliverable:

**PPT path:**
```bash
# Invoke /li:generate-ppt with the pack-configured gate pipeline
# Dispatch agents: PPTNarrativeArchitect (5-beat slide arc) + the pack's voice gate (resolve_pack_field voice.gates_active; none by default)
# Output: <name>.pptx
# Brand: from resolve_pack_field brand.templates or default fallback template
```

**Word path:**
```bash
# /li:generate-word with WordTechnicalEditor agent
# Variants: technical / customer-summary / transparency-note
```

**Web path:**
```bash
# /li:generate-web with WebExperienceCritic agent  
# Variants: single-file HTML OR Next.js scaffold
```

All paths go through the pack-configured gates before customer-shippable.

**Demo handoff path** (ship_path=demo): before distributing demo comms + after the demo, dispatch the customer agents:

```bash
empathy_brief=$(mktemp)
cat > "$empathy_brief" <<EOF
task: Empathy-review the customer-facing demo handout / follow-up comms
context_pointers:
  - <demo comms draft path>
constraints:
  - flag transactional / corporate / dismissive phrasing
  - preserve substance, add humanity
acceptance:
  - per-passage empathy verdict + specific rewrite recommendations
EOF

/li:brief-forge subagent_spawn ship CustomerEmpathyCheck brief "$empathy_brief"

followup_brief=$(mktemp)
cat > "$followup_brief" <<EOF
task: Advise post-demo follow-up — what to send, when, which expansion paths to open
context_pointers:
  - demo signal (questions asked, follow-up requests, decision-maker presence)
constraints:
  - cadence: immediate / 48hr / weekly
  - shape next 30-day plan + expansion paths (next demo / PoC / workshop)
acceptance:
  - follow-up plan with cadence + expansion paths
EOF

/li:brief-forge subagent_spawn ship PostDemoFollowup brief "$followup_brief"
```

### Step 10 — Release notes (if version tag)

If shipping tags release version:
- Invoke `/li:landing-report`
- Generate release notes from commit log between tags
- The active pack's voice gates fire if customer-facing release (`resolve_pack_field voice.gates_active`; none by default)
- Output: `CHANGELOG.md` entry + `RELEASE-NOTES.md`

### Step 11 — 00-state.md append

Mechanical since v5.0 (ADR-0008) — one command, not a YAML obligation. `hard_rule_violations` must be 0 to reach here; gate detail lives in the compliance/provenance logs:

```bash
_sl="${LINTEL_REPO_ROOT:-$(git rev-parse --show-toplevel 2>/dev/null)}/lib/state.sh"
[ -f "$_sl" ] || _sl="$HOME/.lintel/lib/state.sh"; source "$_sl"   # installed by install.sh in consumer repos
state_append SHIP <DONE|DONE_WITH_CONCERNS|BLOCKED> next=CAPTURE ship_path=<pr|direct_main|demo> pr_url=<url-if-PR> commit_range=<sha>..<sha> hard_rule_violations=0
```

## Status protocol

- **DONE** — PR opened / deployed / handoff complete, all gates PASS
- **DONE_WITH_CONCERNS** — shipped with caveats (e.g., voice gate at 85%, P3 deferred)
- **BLOCKED** — compliance-gate violation OR critical compliance failure
- **NEEDS_CONTEXT** — deploy target unclear, or PR template not configured

## Pause-points (MANDATORY)

1. Before PR open: confirm commit messages + branch state + base branch
2. On ANY compliance-gate violation: full stop, never silently proceed (per CLAUDE.md)
3. Per customer-deliverable: the pack-configured gates (voice + brand + honest-limitations + provenance) each fire
4. PR creation confirmation: AskUserQuestion "Open PR now?" — last chance to cancel
5. If direct-main path: AskUserQuestion explicit per-batch authorization required (per CLAUDE.md)

## Hop-in support

YES — operator can `/li:ship` on existing branch outside full cycle.

Skip-conditions: intent=research-only, intent=local-dev-only, intent=draft-only.

## Integration

**Reads:**
- the active pack's compliance gates (`resolve_pack_field compliance.hooks`; none by default)
- review-report.md (must show PASS)
- compliance-report.md (if the active pack defines compliance gates)
- brand assets (`resolve_pack_field brand.templates` if doc-gen)
- the active pack's voice corpus (`resolve_pack_field voice.corpus`; none by default — if voice gate)
- plan.md (for PR body)
- design doc (for PR body)

**Writes:**
- PR (via gh)
- release-notes.md (if tag)
- provenance-log.md (append)
- customer deliverables (.pptx, .docx, .html if applicable)
- transparency-note.md (if AI-system shipped to customer)
- `.claude/runtime/state/00-state.md` (SHIP entry)
- `.claude/runtime/audit/compliance-stops.jsonl` (if any violations)

**Triggers:**
- CAPTURE next (final phase)

## Recommended agents

**Release infrastructure:**
- ReleaseEngineer (engineering/) — primary
- GHActionsReviewer (devops/) — GH Actions
- TerraformReviewer / K8sManifestReviewer (devops/) — if infra ship

**Compliance final (pack-contributed):**
- The active pack's compliance gates (`resolve_pack_field compliance.hooks`; none by default) supply any final compliance + provenance reviewers.

**Voice + doc-gen (customer artifacts):**
- The active pack's voice gates (`resolve_pack_field voice.gates_active`; none by default) — voice gate
- PPTNarrativeArchitect (doc-gen/) — slide arc
- WordTechnicalEditor (doc-gen/) — Word variants
- WebExperienceCritic (doc-gen/) — web review

**Customer:**
- DemoNarrativeArc (customer/) — if demo
- DemoNarratorJunior (customer/) — if narrative needed
- CustomerEmpathyCheck (customer/) — empathy-review demo comms before handoff (Step 9 demo path)
- PostDemoFollowup (customer/) — post-demo follow-up cadence + expansion paths (Step 9 demo path)
- ExecutiveBriefingDrafter / ProposalDrafter / RFPResponseDrafter (customer/) — if engagement deliverables

**Communication:**
- EmailCustomerDrafter (communication/) — if announce email
- BlogPostDrafter / LinkedInPostDrafter (communication/) — if public post

## Anti-patterns

- **Direct-push to main without explicit per-batch auth** — never (per CLAUDE.md)
- **Skipping the pack's compliance re-check at SHIP** — REVIEW passed but pre-ship sanity is mandatory when the pack defines gates
- **Skipping voice gate because "operator wrote it themselves"** — if final artifact customer-facing and the pack defines voice gates, they fire regardless
- **Letting honest-limitations be implicit** — must be explicit AI-disclaimer
- **Shipping AI-assisted artifacts without provenance log** — audit trail mandatory if the pack activates a provenance gate
- **Bundling unrelated changes in one PR** — atomic per design doc (one logical change per PR)
- **PR body without design+plan+review links** — traceability requirement
- **Skipping --no-verify** to bypass hooks — never bypass hooks unless explicitly authorized

## Failure recovery

- **Compliance-gate violation at pre-ship**: full stop. Operator fixes. Re-run SHIP from Step 3. Log to audit.
- **gh CLI unavailable**: surface command, operator runs manually. Save state for resume.
- **Voice gate fails after edits**: surface findings, operator decides accept-with-caveat or further edit + re-gate.
- **Brand assets missing AND default templates failed**: surface, operator either pulls brand or accepts text-only output.
- **Pack deploy validation fails**: BLOCKED. Fix infra config. Re-run.
- **Customer wants to delay deliverable**: SHIP completes commit/PR but skips customer-handoff. Resume customer-handoff later via the doc-gen path (`/li:generate-ppt` / `-word` / `-web`).

## Voice tier behavior

`voice: mixed`. PR body + release notes follow the active pack's voice tier (`resolve_pack_field voice.default_tier`; default: internal). Customer-facing artifacts go through the pack's voice gates (`resolve_pack_field voice.gates_active`; none by default). Internal handoff (engineering team) uses internal voice.

## Cycle-position footer

Close your report with the shared position footer so the operator always knows where they are in the
cycle and the one logical next action — whether this phase ran standalone or inside `/li:cycle`:

```bash
source "$LINTEL_REPO_ROOT/lib/cycle-footer.sh"   # fallback: "$(git rev-parse --show-toplevel)/lib/cycle-footer.sh"
render_cycle_footer                               # reads .claude/runtime/state/00-state.md; --compact for short replies
```

Skipped phases render `⊘`; ASCII via `LINTEL_ASCII=1`. See [ADR-0003](../../.claude/decisions/0003-cycle-position-footer.md).
