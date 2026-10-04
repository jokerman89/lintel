---
name: li-ship
description: Use after review to prepare a verified change for a pull request or an explicitly authorized release.
---

> **Lintel on GitHub Copilot.** Generated from `skills/ship/SKILL.md`; edit the canonical file, then run
> `li-copilot init`.
> - **Resource root:** `../../..` from this skill's base directory (the Lintel source with `bin/`,
>   `lib/`, `skills/`). Write plans, state and evidence into the working repository's `.claude/`
>   tree, never into the resource root.
> - **Skill-relative paths:** this skill's own `scripts/`, `references/` and `data/` folders (and a
>   `<base>` that the workflow defines as its own directory) mean
>   `../../../skills/ship/` in the Lintel source, not this generated folder.
>   `${LINTEL_SKILLS_DIR:-skills}` means the skills root, `../../../skills`. A `bin/li-run` step
>   runs in the working repository, so use `$LINTEL_SKILLS_DIR/ship/` there.
> - **Shell steps:** run Bash snippets with Bash (Git for Windows' `bash.exe` on Windows, never
>   `System32\bash.exe`). Save a snippet to a temporary `.sh` file and run
>   `bash "<resource root>/bin/li-run" <file>`; it prepares `LINTEL_SOURCE_ROOT`, `LINTEL_REPO_ROOT`
>   and the profile context.
> - **Tools:** Read=`view`, Write=`create`, Edit=`edit`, Bash=`bash`/`powershell`, Grep=`grep`,
>   Glob=`glob`, AskUserQuestion=`ask_user`, TodoWrite=the plan checklist, Task or a named role=`task`
>   with that custom agent, WebFetch=`web_fetch`.
> - **Other Lintel workflows** are native skills: invoke `/li-<name>` rather than reading their
>   files. Named roles such as `CodeReviewer` are custom agents.

You are the SHIP skill — Phase 7 of the Lintel cycle.

## What this skill does

Ships the BUILD output via PR (default) or direct-push (with explicit per-batch authorization).
Requested customer deliverables use the conditional customer-delivery method;
requested release notes use CAPTURE's release-report view.

Hard-stops from the active pack's compliance gates (`resolve_pack_field compliance.hooks`; none by default). When a pack activates them, typical gates include:
- customer-data in commit
- secrets in any file
- prod-mutations without explicit per-call auth

The active pack's voice gates (`resolve_pack_field voice.gates_active`; none by default) fire on customer-facing artifacts.

## When to use

- After REVIEW PASS, ship-ready=yes
- Operator types `/li-ship` to ship existing branch
- Doc-gen customer-deliverable shipping (PPT/Word/Web with 4-gate pipeline)
- Demo deliverable handoff to customer

## When NOT to use

- REVIEW returned BLOCKED (P1 unfixed) → fix loop, then ship
- intent=research-only — no ship
- intent=local-dev-only — operator works locally, no ship
- intent=draft-PR-only — retain draft labeling and every applicable mandatory policy boundary

## Workflow

### Step 1 — Pre-flight (MANDATORY)

Verify ship-readiness:
- `git status` is clean OR operator confirms uncommitted is intentional
- Current branch is NOT main (unless explicit per-batch direct-push auth)
- Run `/li-verify` in its read-only default, never `--repair` after review. Require actual nonzero
  applicable validation and explicit skipped/unavailable coverage. An approved
  docs-only package can use an observed mandatory document check with grounded
  tests N/A; applicable required tests still need nonzero executed coverage.
  Use BUILD's [documentation-fidelity method](../../../skills/build/references/documentation-fidelity.md)
  for that check and for applicable documented-behavior changes. Consume its
  current claim-to-source coverage, actual observations and unrun/divergent claims
  through the same P05 path below; do not rewrite reviewed docs or treat a source
  checklist as executed examples.
- Consume the [shared content-bound gate](../../../skills/review/references/evidence.md) with
  the selected context, actual independent corroboration and read-only QA record.
  `li-review-evidence.py ship` invokes the real audit reader, selects the latest
  applicable decision before verdict, and revalidates content/acceptance/profile.
  Require v2 review/context/QA and exact accepted `qa_requirements`; a submitted
  document pass cannot replace bound tests, and relabeling a result cannot alter
  its mandatory/applicability/kind/policy contract. Older evidence remains history
  until a fresh prepared context and independent review supersede it.
- Human-readable review/compliance reports remain supporting evidence. PASS text,
  an old commit-only review, elapsed time or an operator note is not a substitute
  for sufficient current evidence.
- Surface the ANALYZE verdict from the report explicitly linked to the selected
  work/cycle, if available, after checking its work-map, profile and package/leaf
  identity. An unlinked `.claude/runtime/state/analyze-report.md` is legacy history,
  not current readiness evidence. ADR-0004 remains advisory by default: surface
  RED/YELLOW findings to the operator, without automatic blocking or treating a
  missing report as a pass. Declared mandatory controls still use the shared gate above.

If pre-flight fails: BLOCKED. Don't proceed.

Intentional dirty work must be in the reviewed explicit selection, including new
files, deletions, documents and config. Staging, committing or editing selected
content after review requires a newly verified context and affected review/QA.
Unrelated files/commits outside selection do not alone invalidate unchanged evidence.
The helper verifies readiness only; it grants no push, merge, release or deployment
permission and does not authenticate the reviewer from a digest.

### Step 2 — Audience + voice classification

From the actual requested outcome and selected applicable profile, with mode and
role as context rather than permission or a request to create more outputs:
- audience: solo / team / customer
- voice_tier: internal / mixed / external
- artifact_kind: code-only / docs / customer-deliverable / demo

Determines which gates apply in subsequent steps. No customer request means no
customer generation, empathy-review or follow-up path: do not load those methods
for ordinary code/PR delivery. Source selection metadata and profile applicability
are separate from actual available tools and operation authority.

### Step 3 — Compliance hard-stop check (active pack's gates)

Resolve the required profile successfully, then run its applicable controls using
the shared `mandatory`/`advisory` model. A mandatory fail/error/unverified or unknown
required policy blocks even if every advisory score is green. Advisory issues do
not become hard stops merely because a gate exists. Re-verify the same context even
if REVIEW passed. Example checks a pack may require:

```bash
# Customer data
grep -rE '(customer-name-patterns|PII-patterns)' --include='*.md' --include='*.ts' --include='*.json' staged_files
# Secrets
gitleaks detect --staged
# Production mutations without auth
# (operator-specific, check for prod-deploy commands or live-cloud-mutation)
```

If any applicable mandatory control fails, errors or remains unverified:
- HARD STOP
- Surface to operator: violation + file:line + recommended fix
- Fix the violation or obtain a policy-authorized scope change and re-plan/review.
  An override note cannot relabel a failed mandatory control as passed or N/A.
- Log the stop mechanically (one line; ts/operator/cycle_id come from the envelope):

Retain advisory violations in the report without converting them into hard stops.
A configured control is not automatically mandatory.

```bash
export LINTEL_SOURCE_ROOT="${LINTEL_SOURCE_ROOT:-${CLAUDE_PLUGIN_ROOT:?trusted Lintel source root unavailable; set LINTEL_SOURCE_ROOT}}"
source "$LINTEL_SOURCE_ROOT/bin/_audit.sh" || exit $?
audit_log compliance-stops gate_violation gate=<gate> file=<file:line> resolution=<open|fixed|policy-replan>
# → .claude/runtime/audit/compliance-stops.jsonl
```

### Step 4 — Voice + brand gate (if customer-facing)

If `audience=customer` AND the active pack defines voice gates (`resolve_pack_field voice.gates_active`; none by default):
- Run the pack's voice gates (already done in REVIEW Stage 3, but final verification)
- If new edits since REVIEW: re-run
- Threshold: ≥85% known-good match against the pack's voice corpus (`resolve_pack_field voice.corpus`)

Only for requested customer-deliverable production, load
[format generation and gates](../../../skills/ship/references/customer-delivery.md#format-generation-and-gates).
That owner retains all four categories (voice, brand, honest-limitations and
provenance) and their mandatory/advisory/N/A classification. A current reviewed
artifact is not regenerated by default; changed content renews Step 1's context,
review and read-only QA before delivery.

### Step 5 — Provenance tracking (if the active pack requires it)

If the active pack activates a provenance gate (`resolve_pack_field compliance.hooks`; none by default):
- Log AI-assistance provenance for the shipped artifact — one line via the unified writer (ts/operator/cycle_id come from the envelope; the audit dir is already repo-scoped in v5 repos, so no `<repo>-` prefix in the filename):

```bash
export LINTEL_SOURCE_ROOT="${LINTEL_SOURCE_ROOT:-${CLAUDE_PLUGIN_ROOT:?trusted Lintel source root unavailable; set LINTEL_SOURCE_ROOT}}"
source "$LINTEL_SOURCE_ROOT/bin/_audit.sh" || exit $?
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
    - prepare the requested artifact through the customer-delivery method and its four gate categories
    - operator distributes via approved channel
    - provenance logged
```

Operator chooses path via flag or auto-detect from artifact_kind.

### Step 7 — PR creation (default path)

Populate the process fields from the actual Step 1 gate result: the latest applicable
decision, its exact record/context, and observed QA/coverage limitations. Do not
infer a pass from entering SHIP, a report heading or an earlier decision. An absent,
stale, blocked or unreadable review remains explicitly **unverified/blocked** in any
draft summary; it cannot proceed through this path. Preserve advisory and unrun
coverage even when readiness passes. Readiness is not publication permission; use
the adapter's actual authorized publication operation.

```bash
# Use gh CLI
gh pr create --title "<short title>" --body "$(cat <<'EOF'
## Summary
[1-3 bullets from design doc]

## Design + Plan
- Design: <.claude/engineering/design-archive/lintel-*-design-*.md>
- Plan: <plan.md>
- Review report: <review-report.md>
- Compliance report: <compliance-report.md if applicable>

## Test plan
[Bulleted checklist from plan.md acceptance criteria]

## Process
Phases run: <actually observed phases for this work>
Review: <actual latest applicable verdict; unverified/blocked when not established>
Review evidence: <exact record and reviewed context/result identity>
Review limitations: <actual advisory findings, unrun coverage and remaining gates>
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

Only for an actual requested customer artifact, demo handoff, customer-copy
review or post-demo plan, load the
[customer-delivery method](../../../skills/ship/references/customer-delivery.md). It owns source
selection discovery, actual available authorized role/tool binding, format
variants, empathy-review and follow-up briefs. Apply only the selected part under
the verified applicable profile; do not automatically spawn personas.

Timing comes from the agreed plan, not a preset cadence. Missing agreement,
writer or required independent review remains explicit and blocks only its
dependent output. No source selection grants permission, sends communications
or makes a commitment. Retain all normal SHIP review/QA/publication checks.

### Step 10 — Release notes (if version tag)

For an explicitly authorized release or PR summary, use the release-report step in
`/li-capture --release-summary`. Select the actual commit/tag range, link delivered work, distinguish
features/fixes/migrations and state unresolved limits. Generate a `CHANGELOG.md` entry
and a separate release-notes file only when those outputs are requested. A report
does not create a tag, release or deployment. Apply configured customer-facing voice
checks where relevant; neither this prose nor a pack label proves a hook fired.
For requested changelog formatting, apply CAPTURE's
[Keep a Changelog method](../../../skills/capture/SKILL.md#keep-a-changelog-output) in the current
context, reusing the same selected evidence. ChangelogMaintainer remains a compatible
entrypoint, not another default dispatch or a reason to repeat the release report.

### Step 11 — 00-state.md append

Mechanical since v5.0 (ADR-0008) — one command, not a YAML obligation. `hard_rule_violations` must be 0 to reach here; gate detail lives in the compliance/provenance logs:

```bash
export LINTEL_SOURCE_ROOT="${LINTEL_SOURCE_ROOT:-${CLAUDE_PLUGIN_ROOT:?trusted Lintel source root unavailable; set LINTEL_SOURCE_ROOT}}"
source "$LINTEL_SOURCE_ROOT/lib/state.sh" || exit $?
state_append SHIP <DONE|DONE_WITH_CONCERNS|BLOCKED> next=CAPTURE ship_path=<pr|direct_main|demo> pr_url=<url-if-PR> commit_range=<sha>..<sha> hard_rule_violations=0
```

## Reusable patterns

Follow the [reusable pattern consumer contract](../../../skills/pattern/references/consumer-contract.md). If
the delivery has a pattern lock, re-run the clause review (`li-pattern review`, which verifies
the lock against the current context at use) immediately before the shared SHIP gate. A stored
review output is not enough, and a non-`ok` lock blocks. List the failed, waived and unverified
mandatory clauses from that review by clause ID, with any exception reference, in the delivery
summary.
State the limits: patterns are data checked for structure and declared provenance, not platform
enforcement, and clause coverage is not review clearance. A missing or stale clause review
blocks that claim; it does not silently pass.

## Status protocol

- **DONE** — PR opened / deployed / handoff complete, all applicable mandatory controls verified
- **DONE_WITH_CONCERNS** — shipped with caveats (e.g., voice gate at 85%, P3 deferred)
- **BLOCKED** — applicable mandatory failure/error/unverified result or required policy unresolved
- **NEEDS_CONTEXT** — deploy target unclear, or PR template not configured

## Pause-points (MANDATORY)

1. Before PR open: confirm commit messages + branch state + base branch
2. On an applicable mandatory failure/error/unverified control: stop the affected
   action. Surface advisory findings without promoting them to hard stops.
3. Per customer-deliverable: the pack-configured gates (voice + brand + honest-limitations + provenance) each fire
4. PR creation confirmation: ask_user "Open PR now?" — last chance to cancel
5. If direct-main path: ask_user explicit per-batch authorization required (per CLAUDE.md)

## Hop-in support

YES — operator can `/li-ship` on existing branch outside full cycle.

Skip-conditions: intent=research-only, intent=local-dev-only, intent=draft-only.

## Integration

**Reads:**
- the active pack's compliance gates (`resolve_pack_field compliance.hooks`; none by default)
- latest applicable structured review decision, selected expected context and independent corroboration
- same-context QA record with actual executed/failed/skipped coverage
- review-report.md (human-readable supporting evidence, not standalone clearance)
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

**Requested customer/communication/doc-gen work:**
Use the [conditional capability views](../../../skills/ship/references/customer-delivery.md#compatible-capability-views)
only after Step 2 establishes the actual outcome/profile. Existing public roles
remain discoverable; this list is not an automatic dispatch or availability claim.

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

- **Mandatory compliance control unresolved at pre-ship**: stop the affected action,
  repair and re-run from Step 3. Log to audit. Advisory findings remain visible advice.
- **gh CLI unavailable**: surface command, operator runs manually. Save state for resume.
- **Voice control fails after edits**: mandatory failure blocks and requires repair
  or an authorized policy re-plan; advisory findings may remain documented concerns.
- **Brand assets missing AND default templates failed**: surface, operator either pulls brand or accepts text-only output.
- **Pack deploy validation fails**: BLOCKED. Fix infra config. Re-run.
- **Customer wants to delay deliverable**: SHIP completes commit/PR but skips customer-handoff. Resume customer-handoff later via the doc-gen path (`/li-generate-ppt` / `-word` / `-web`).

## Voice tier behavior

`voice: mixed`. PR body + release notes follow the active pack's voice tier (`resolve_pack_field voice.default_tier`; default: internal). Customer-facing artifacts go through the pack's voice gates (`resolve_pack_field voice.gates_active`; none by default). Internal handoff (engineering team) uses internal voice.

## Cycle-position footer

Close your report with the shared position footer so the operator always knows where they are in the
cycle and the one logical next action — whether this phase ran standalone or inside `/li-cycle`:

```bash
footer_source="${LINTEL_SOURCE_ROOT:-${CLAUDE_PLUGIN_ROOT:-}}"
if [ -n "$footer_source" ] && [ -f "$footer_source/lib/cycle-footer.sh" ]; then
  source "$footer_source/lib/cycle-footer.sh" || exit $?
  render_cycle_footer
else
  printf '%s\n' "UNVERIFIED: shared cycle-position footer is unavailable" >&2
fi
```

Skipped phases render `⊘`; ASCII via `LINTEL_ASCII=1`. See [ADR-0003](../../../.claude/decisions/0003-cycle-position-footer.md).
