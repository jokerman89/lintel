---
name: ship
layer: foundation
description: Phase 7 of Lintel cycle — PR / deploy / customer handoff. Final compliance hard-stops. Voice + brand + honest-limitations + provenance gates on customer-facing artifacts. EV2/OneBranch validation.
color: cyan
tools: Read, Bash, Edit, Grep, Glob
voice: mixed
cli_support: [claude-code, codex]
---

You are the SHIP skill — Phase 7 of the Lintel cycle.

## What this skill does

Ships the BUILD output via PR (default) or direct-push (with explicit per-batch authorization). Customer-deliverables go through 4-gate doc-gen pipeline. Provenance logged. Release notes generated.

Hard-stops if WorkProfile=on:
- customer-data in commit
- secrets in any file
- prod-mutations without explicit per-call auth
- non-MS-SSO authentication used
- non-first-party choices without rationale

Voice + brand gates fire on customer-facing artifacts.

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
- compliance-report.md shows PASS (if WorkProfile=on)

If pre-flight fails: BLOCKED. Don't proceed.

### Step 2 — Audience + voice classification

From mode + role:
- audience: solo / team / customer
- voice_tier: internal / mixed / trailblazer
- artifact_kind: code-only / docs / customer-deliverable / demo

Determines which gates fire in subsequent steps.

### Step 3 — HARD-RULES hard-stop check (if WorkProfile=on)

NEVER bypassable. Re-verify even if REVIEW passed (last-second pre-ship sanity):

```bash
# Customer data
grep -rE '(customer-name-patterns|PII-patterns)' --include='*.md' --include='*.ts' --include='*.json' staged_files
# Secrets
gitleaks detect --staged
# Production mutations without auth
# (operator-specific, check for prod-deploy commands or live-cloud-mutation)
# MS SSO only
# First-party-first (light check, full in REVIEW)
```

If ANY hard-rule violation:
- HARD STOP
- Surface to operator: violation + file:line + recommended fix
- Operator MUST fix or explicitly override (rarely warranted)
- Log to `~/.lintel/audit/hard-rule-stops.jsonl`

### Step 4 — Voice + brand gate (if customer-facing)

If `audience=customer` AND `voice_tier=trailblazer`:
- Invoke `/li:rais-customer-voice-check` (already done in REVIEW Stage 3, but final verification)
- If new edits since REVIEW: re-run
- Threshold: ≥85% known-good match

If `artifact_kind=customer-deliverable` (PPT/Word/Web):
- Invoke `/li:generate-ppt` / `-word` / `-web` 4-gate pipeline:
  1. Voice gate (TrailblazerVoiceCritic)
  2. Brand-conformance (MS brand assets if `~/.lintel/brand/` populated, default-fallback otherwise)
  3. Honest-limitations (AI-disclaimer present?)
  4. Provenance (AI-assistance logged?)
- ALL 4 must PASS for customer-shippable

### Step 5 — Provenance tracking (if WorkProfile=on)

Invoke `/li:provenance-track`:
- Log AI-assistance provenance for shipped artifact
- Append to `~/.lintel/provenance/<repo>-provenance-log.jsonl`:
```json
{
  "ts": "<timestamp>",
  "repo": "<name>",
  "branch": "<branch>",
  "commit_range": "<sha>..<sha>",
  "ai_assistance": "lintel-cycle-v3.5",
  "phases": ["DEFINE", "PLAN", "BUILD", "REVIEW", "SHIP"],
  "operator": "<whoami>",
  "audience": "<audience>",
  "voice_tier": "<tier>",
  "compliance_gates_passed": [...]
}
```

If audience=customer AND AI-system shipped: also invoke `/li:rais-transparency-note` to draft transparency note for customer.

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
    - operator must explicitly authorize: "commita och merga"
    - HARD-RULES re-checked
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
AI-assisted via /li:cycle v3.5
Phases: DEFINE → PLAN → BUILD → REVIEW → SHIP
Operator review: passed REVIEW phase

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

Apply CODEOWNERS auto-request. Note required reviewers.

### Step 8 — EV2 / OneBranch / Pipeline validation (if MS infra)

If shipping to MS-internal infra:
- `/li:onebranch-validate` if 1ES pipeline involved
- `/li:release-ev2` (or `release-deploy-ev2`) for EV2 ring deployments
- `/li:safe-deploy-ring` for canary strategy

Dispatch agents:
- EV2PipelineAuditor (devops/) for EV2 config audit
- OneBranchReviewer (devops/) for 1ESPT compliance
- GHActionsReviewer (devops/) if GH Actions involved

### Step 9 — Customer-deliverable generation (if applicable)

For artifact_kind=customer-deliverable:

**PPT path:**
```bash
# Invoke /li:generate-ppt with 4-gate pipeline
# Dispatch agents: PPTNarrativeArchitect (5-beat slide arc), TrailblazerVoiceCritic (voice gate)
# Output: <name>.pptx
# Brand: from ~/.lintel/brand/ or default fallback template
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

All paths go through 4 gates before customer-shippable.

### Step 10 — Release notes (if version tag)

If shipping tags release version:
- Invoke `/li:landing-report`
- Generate release notes from commit log between tags
- TrailblazerVoiceCritic gate if customer-facing release
- Output: `CHANGELOG.md` entry + `RELEASE-NOTES.md`

### Step 11 — 00-state.md append

```yaml
phase: SHIP
ts: <timestamp>
ship_path: <pr | direct_main | demo>
pr_url: <url if PR>
commit_range: <sha>..<sha>
hard_rule_violations: 0  # must be 0 to reach here
voice_gate: <score>%
brand_gate: <PASS | n/a>
honest_limitations: <PASS | n/a>
provenance_logged: yes
release_notes_path: <path if tag>
customer_deliverables: <list of .pptx/.docx/.html paths>
status: DONE | DONE_WITH_CONCERNS | BLOCKED
next_recommended: CAPTURE
```

## Status protocol

- **DONE** — PR opened / deployed / handoff complete, all gates PASS
- **DONE_WITH_CONCERNS** — shipped with caveats (e.g., voice gate at 85%, P3 deferred)
- **BLOCKED** — HARD-RULE violation OR critical compliance failure
- **NEEDS_CONTEXT** — deploy target unclear, or PR template not configured

## Pause-points (MANDATORY)

1. Before PR open: confirm commit messages + branch state + base branch
2. On ANY HARD-RULE detection: full stop, never silently proceed (per CLAUDE.md)
3. Per customer-deliverable: 4 gates (voice + brand + honest-limitations + provenance) each fire
4. PR creation confirmation: AskUserQuestion "Open PR now?" — last chance to cancel
5. If direct-main path: AskUserQuestion explicit per-batch authorization required (per CLAUDE.md)

## Hop-in support

YES — operator can `/li:ship` on existing branch outside full cycle.

Skip-conditions: intent=research-only, intent=local-dev-only, intent=draft-only.

## Integration

**Reads:**
- HARD-RULES.md (MANDATORY if WorkProfile=on)
- review-report.md (must show PASS)
- compliance-report.md (if WorkProfile=on)
- brand assets (`~/.lintel/brand/` if doc-gen)
- OurVoice-corpus.md (if voice gate)
- plan.md (for PR body)
- design doc (for PR body)

**Writes:**
- PR (via gh)
- release-notes.md (if tag)
- provenance-log.md (append)
- customer deliverables (.pptx, .docx, .html if applicable)
- transparency-note.md (if AI-system shipped to customer)
- `.lintel/state/00-state.md` (SHIP entry)
- `~/.lintel/audit/hard-rule-stops.jsonl` (if any violations)

**Triggers:**
- CAPTURE next (final phase)

## Recommended agents

**Release infrastructure:**
- ReleaseEngineer (engineering/) — primary
- EV2PipelineAuditor (devops/) — EV2-specific
- OneBranchReviewer (devops/) — 1ES pipeline
- GHActionsReviewer (devops/) — GH Actions
- TerraformReviewer / K8sManifestReviewer — if infra ship

**MS compliance final:**
- OneCSAuditor (ms-specific/) — final compliance pass
- ProvenanceVerifier (ms-specific/) — provenance check

**Voice + doc-gen (customer artifacts):**
- TrailblazerVoiceCritic (voice/) — voice gate
- PPTNarrativeArchitect (doc-gen/) — slide arc
- WordTechnicalEditor (doc-gen/) — Word variants
- WebExperienceCritic (doc-gen/) — web review

**Customer:**
- DemoNarrativeArc (customer/) — if demo
- DemoNarratorJunior (customer/) — if narrative needed
- ExecutiveBriefingDrafter / ProposalDrafter / RFPResponseDrafter (customer/) — if engagement deliverables

**Communication:**
- EmailCustomerDrafter (communication/) — if announce email
- BlogPostDrafter / LinkedInPostDrafter (communication/) — if public post

## Anti-patterns

- **Direct-push to main without explicit per-batch auth** — never (per CLAUDE.md)
- **Skipping HARD-RULES re-check at SHIP** — REVIEW passed but pre-ship sanity is mandatory
- **Skipping voice gate because "operator wrote it themselves"** — if final artifact customer-facing, gate fires regardless
- **Letting honest-limitations be implicit** — must be explicit AI-disclaimer
- **Shipping AI-assisted artifacts without provenance log** — audit trail mandatory if WorkProfile=on
- **Bundling unrelated changes in one PR** — atomic per design doc (one logical change per PR)
- **PR body without design+plan+review links** — traceability requirement
- **Skipping --no-verify** to bypass hooks — never bypass hooks unless explicitly authorized

## Failure recovery

- **HARD-RULE violation at pre-ship**: full stop. Operator fixes. Re-run SHIP from Step 3. Log to audit.
- **gh CLI unavailable**: surface command, operator runs manually. Save state for resume.
- **Voice gate fails after edits**: surface findings, operator decides accept-with-caveat or further edit + re-gate.
- **Brand assets missing AND default templates failed**: surface, operator either pulls brand or accepts text-only output.
- **EV2 validation fails**: BLOCKED. Fix infra config. Re-run.
- **Customer wants to delay deliverable**: SHIP completes commit/PR but skips customer-handoff. Resume customer-handoff later via `/li:demo-deliverable-gen`.

## Voice tier behavior

`voice: mixed`. PR body + release notes follow voice_tier of mode. Customer-facing artifacts go through TrailblazerVoiceCritic gate (trailblazer voice). Internal handoff (engineering team) uses internal voice.
