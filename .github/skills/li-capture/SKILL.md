---
name: li-capture
description: Use after delivery to record evidence, durable lessons and the next-session handoff.
---

> **Lintel on GitHub Copilot.** Generated from `skills/capture/SKILL.md`; edit the canonical file, then run
> `li-copilot init`.
> - **Resource root:** `../../..` from this skill's base directory (the Lintel source with `bin/`,
>   `lib/`, `skills/`). Write plans, state and evidence into the working repository's `.claude/`
>   tree, never into the resource root.
> - **Skill-relative paths:** this skill's own `scripts/`, `references/` and `data/` folders (and a
>   `<base>` that the workflow defines as its own directory) mean
>   `../../../skills/capture/` in the Lintel source, not this generated folder.
>   `${LINTEL_SKILLS_DIR:-skills}` means the skills root, `../../../skills`. A `bin/li-run` step
>   runs in the working repository, so use `$LINTEL_SKILLS_DIR/capture/` there.
> - **Shell steps:** run Bash snippets with Bash (Git for Windows' `bash.exe` on Windows, never
>   `System32\bash.exe`). Save a snippet to a temporary `.sh` file and run
>   `bash "<resource root>/bin/li-run" <file>`; it prepares `LINTEL_SOURCE_ROOT`, `LINTEL_REPO_ROOT`
>   and the profile context.
> - **Tools:** Read=`view`, Write=`create`, Edit=`edit`, Bash=`bash`/`powershell`, Grep=`grep`,
>   Glob=`glob`, AskUserQuestion=`ask_user`, TodoWrite=the plan checklist, Task or a named role=`task`
>   with that custom agent, WebFetch=`web_fetch`.
> - **Other Lintel workflows** are native skills: invoke `/li-<name>` rather than reading their
>   files. Named roles such as `CodeReviewer` are custom agents.

You are the CAPTURE skill — Phase 8 (final) of the Lintel cycle.

## What this skill does

Preserve durable outcomes and unresolved work so another session can continue without
re-deriving the task. A capture can follow delivery, an unfinished cycle or an explicitly
requested retrospective; none of those implies publication or review clearance.

Four core artifact categories:
1. **Lessons** — corrections from BUILD/REVIEW → the project lessons store resolved by `lintel_lessons_file` (`.claude/memory/lessons.md` on the v5 layout; filtered, durable patterns only)
2. **ADR** — non-trivial decisions → `.claude/decisions/NNNN-<slug>.md`
3. **EVOLUTION-LOG** — CLAUDE.md changes → log entry
4. **Cold-executor handoff trio** — reaffirm `spec.md` + `plan.md` + `prompt.md` against build evidence (trio BORN in PLAN per v3.8 Feature 2.2; CAPTURE only annotates with actual-build outcomes)

Plus role debrief when applicable, an optional retrospective and a release summary.

## When to use

- After SHIP completes successfully
- After failed cycle (BLOCKED state) for capturing what was learned even without ship
- Standalone post-implementation reflection
- Pre-handoff to teammate or to your future-self

## When NOT to use

- Mid-cycle (premature)
- For trivial single-file edits (no lessons/ADR worth capturing)
- intent=research-only ended (light capture only — retro + maybe lessons)

## Inputs and report-only modes

Normal cycle CAPTURE follows the full workflow below. Two standalone views retain the
reflection and release-report methods without silently running the mutation steps:

- `--retrospective`: session/day/week reflection (Step 8). Accept `--since <ref|time>`,
  `--scope <session|day|week>`, `--emit-lessons` and `--out <owned-path>`.
- `--release-summary`: delivered-work report (Step 8b). Accept `--since <ref|time>`,
  `--until <ref|time>`, `--scope <area>`, `--voice <internal|customer>`,
  `--include-stats` and `--out <owned-path>`.

Choose one report mode. Output defaults to the conversation, not a new file. `--out`
requires an authorized destination and preservation of existing content. Report-only
requests do not append cycle completion, change a work map, create/tag a release, commit,
publish a file or distribute a customer draft. Return after the selected report. With
`--emit-lessons`, propose individual add/update/supersede/no-op classifications; write
only the specifically authorized lessons through Step 2.

All modes keep selected-work/profile precedence and original task IDs. Respect frozen
memory/decision paths: report proposed captures for their owner instead of writing there.

## Workflow

### Step 1 — Cycle history aggregation

Follow the [shared work-map contract](../../../skills/spec-kit/references/work-map.md), including
actual P07 verification via `workflow_resume`, and read
`bin/li-work-artifacts.py --repo <target> --map <selected> --view context`.
Use `state_cycle_segment <ledger> <original-cycle-id>`, not the whole ledger or a
newest-file guess. Read only reports/build-log entries linked to that work and its
original package/leaf IDs. Extract:
- Actual phase statuses and measured durations/usage where recorded; otherwise unknown
- Corrections operator made during BUILD/REVIEW (from build-log)
- Decisions taken (alternatives chosen in DEFINE, scope changes in PLAN)
- Reviewer concerns from REVIEW
- Compliance gates that fired + outcomes

This is the source data for capture artifacts.

### Step 1b — Granularity calibration record (dormant by decision, ADR-0008 — activate with a behavior test when scale-estimator calibration is wanted)

This step is NOT part of the default CAPTURE run. ADR-0008 lists granularity writes as dormant-by-decision: zero records exist and none are expected until the loop is deliberately activated (the activation gate is a behavior test, not prose). Skip to Step 2 unless the operator has activated it.

The design it would close (§3.5): record this cycle's **actual** outcome against the SCOPE estimate so `lib/scale-estimator.sh` can correct its token/size priors next time. `scale_calibrated_prior` already reads the log and falls back to mechanical defaults while it stays empty — readers are shipped, the writer is dormant.

If — and only if — the loop is activated: read the planned scale from `scope.md` (or the cycle's `00-state.md` SCOPE entry) and the actuals from the cycle history aggregated in Step 1, then append one record via the unified `audit_log` writer:

```bash
# A skill body has no reliable $0/BASH_SOURCE — resolve the repo root the way
# every other skill does ($LINTEL_REPO_ROOT), with a git fallback if it is unset.
# Using $(dirname "$0") here made this calibration write silently no-op.
REPO_ROOT="${LINTEL_REPO_ROOT:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"
source "${LINTEL_SOURCE_ROOT:?select the trusted source}/bin/_audit.sh"

# From scope.md / SCOPE state entry (the plan's estimate):
size="$SCOPE_SIZE"                 # XS | S | M | L | XL
est_tokens="$SCOPE_EST_TOKENS"     # the estimator's prior at plan time
depth_schema="$SCOPE_DEPTH_SCHEMA" # flat | phased | tree
# From this cycle's actuals (Step 1 aggregation):
actual_tokens="$CYCLE_TOKENS_USED" # measured token cost this cycle
task_count="$CYCLE_TASK_COUNT"     # leaf tasks actually executed

audit_log granularity actual_vs_estimated \
  "size=$size" \
  "est_tokens=$est_tokens" \
  "actual_tokens=$actual_tokens" \
  "task_count=$task_count" \
  "depth_schema=$depth_schema"
# → appends one JSONL line to .claude/runtime/audit/granularity.jsonl
```

When active: if any field is unavailable (e.g. SCOPE was silent on an XS request, or tokens weren't tracked), pass what you have and omit the rest — `audit_log` records whatever k=v pairs it's given; a partial record is still useful history. Never block the cycle on this: a failed write is advisory — `audit_log` warns on stderr and returns 0 (some hooks discard that stderr), so a missing record stays unobserved.

The estimator's `scale_calibrated_prior <size>` reads exactly this log: it takes the median `actual_tokens` for a size as the corrected prior, falling back to the mechanical default when no history exists (the UNCALIBRATED label is honest while this stays dormant).

### Step 2 — Lessons capture (filtered)

Invoke `/li-lessons-add` (or inline):

For each correction operator made during the cycle:
- Was this correction GENERAL (would apply to future work) or SPECIFIC (one-time)?
- If GENERAL: candidate for the project lessons store (`lintel_lessons_file`; `.claude/memory/lessons.md` on the v5 layout)
- If SPECIFIC: keep in this cycle's notes only

Apply the shared [lesson benefit and recurrence method](../../../skills/lessons-add/references/benefit.md).
For relevant existing lessons, ask what later application actually helped, whether
the failure recurred, and what remains unknown. Cite the selected dated outcome;
do not infer prevention from keyword hits or the absence of a reported failure.
Use that reasoning for the update-phase below, including proposed merge or
supersession of ineffective/obsolete guidance without deleting history.

Examples of LESSON-worthy:
- "Don't mock the vendor SDK in tests — last 3 cycles' tests passed but prod failed because mocks diverged from real API"
- "Always map the codebase first when planning infra work — saved 90 min on this engagement"

Examples NOT lesson-worthy:
- "Use specific port 8443 in this customer's deployment" — too specific
- "Forgot to update README" — operational, not a pattern

**Update-phase (ADR-0006) — classify BEFORE appending.** Append-only capture is the documented
failure mode of file-based memory. For each candidate, grep what already exists:

```bash
source "${LINTEL_SOURCE_ROOT:?select trusted source}/lib/memory.sh"
lessons_find_related <candidate keywords>    # all related active lessons, ranked
```

Classify against the hits:
- **add** — nothing related exists → new lesson; `bin/li-lessons.py add` allocates the next `L-NNN`
- **update** — an existing lesson covers it but the candidate sharpens it → `bin/li-lessons.py
  update --id L-NNN` rewrites THAT lesson's body (note the cycle id) and keeps its ID
- **supersede** — the candidate CONTRADICTS an existing lesson → `bin/li-lessons.py supersede
  --id L-OLD` adds the new lesson with `supersedes: L-OLD` and stamps the old one with
  `superseded_by: L-<new> (<date>)` in one conditional write. Never delete or edit the old
  lesson away — git holds ingestion history, the marker holds validity (supersede-don't-delete).
- **no-op** — an existing lesson already says this → skip, mention the existing id

ask_user per candidate lesson: "Capture as <classification>? (yes / no / edit-first)"

Write through the helper so allocation, the lock and the conditional write stay mechanical
(without Python 3.9+ the shim refuses visibly and nothing is written):
```bash
source "${LINTEL_SOURCE_ROOT:?select trusted source}/lib/memory.sh"
lessons_helper add --title "<lesson title>" --body-file "$body_file"   # prints the new L-NNN
```
The body carries Rule / Why / How to apply and a `Captured from cycle <cycle-id>` note. The
helper appends at the end, creates a missing store from the scaffolding template inside a
repository, and records an advisory `lessons` audit line after the write.

### Step 3 — Promote lesson check (NEW)

For a lesson with observed benefit and a generalizable scope, offer promotion to
the scaffolding baseline in an explicitly named Lintel work tree. A new lesson with
no later application has **unknown** benefit; keep it local pending observation,
rather than automatically offering every new entry as a proven team-wide rule.
Only an actual unresolved promotion choice needs the question.

If yes: invoke `/li-lessons-promote` (which runs `bin/li-lessons-promote` with an explicit destination and source label).

This is how operator-discovered patterns become team-wide knowledge.

### Step 4 — ADR draft (if non-trivial decision)

Scan cycle history for non-trivial decisions:
- Architectural picks (alternative A vs B chosen)
- Pattern adoptions (new pattern introduced)
- Trade-off decisions (accepted P3 finding, deferred P2)
- Scope changes (descoped feature, added scope)

For each candidate, ask_user: "Draft ADR for this decision?"

If yes: invoke `/li-adr-new "<decision title>"`:
- Reads `.claude/decisions/TEMPLATE.md`
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

Read roles from the validated map, not fixed filenames or guessed siblings. For
Spec Kit, `tasks.md` remains the original task source and `plan.md` remains design.
The following familiar names describe roles, not a second native backlog.

**Mapped `spec` reaffirm** (born in PLAN or owned by the original specification system):
- Verify requirements still match actual implementation
- Report implementation/spec drift; amend a requirement only within explicit scope
  authorization, with affected review/QA evidence renewed
- Preserve the actual selected status and applicable authorization. A DRAFT
  remains DRAFT; CAPTURE does not approve drafts or create a grant. An existing
  approval is not erased by reaffirmation. Scope drift requires the existing
  re-plan/review process, not a silent promotion or rewritten acceptance.

**Mapped `tasks` reaffirm**:
- Annotate the original tasks with actual verified status, preserving IDs and parser
  structure. Missing/blocked/deferred work stays open; CAPTURE does not approve it
- Link observed evidence to the original acceptance and verification references.
  Planned or unrun checks remain explicit; a listed command is not a passed result
- The mapped `plan` receives design reconciliation, never a duplicate task list

**`prompt.md` reaffirm** (born in PLAN, v3.8 Feature 2.2 moved birth to PLAN):
- Verify prompt.md still describes the work accurately
- Add any "What you DON'T need to know" entries discovered during BUILD
- Path: the map's original `prompt` value, including non-sibling Spec Kit handoffs

**Why moved to PLAN:** standalone `/li-plan <design.md>` (workflow_root post-v3.8) needs to produce the complete trio at PLAN-time. CAPTURE-only generation broke that — operator running PLAN solo got 2/3 of a handoff. Trio born together fixes this.

ask_user: "Want to dogfood the trio? Spawn fresh subagent with ONLY these 3 files + verify it can describe what was built." (Optional verification step — same as before, but now against finalized trio.)

**Handoff-size check (advisory).** Invoke `/li-context-budget --handoff --map <same map>`
with explicitly selected P03 warming inputs. It measures the actual distinct
artifacts and uses `context_budget`, not a fictional 500k mode capacity. Unknown
capacity/usage stays unknown. An unavailable input is INCOMPLETE, not a zero-byte
success. This advisory estimate does not halt CAPTURE. The retained
`--skip-handoff-size-check` / `SKIP_HANDOFF_SIZE_CHECK=1` records that the estimate
was not run; it does not waive a declared required limit or host refusal.

### Step 6a — Reaffirm swarm evidence and future-operator clarity

When the selected work map opts into swarming, resolve helpers only from explicit
`LINTEL_SOURCE_ROOT`, then Claude's `CLAUDE_PLUGIN_ROOT`; other adapters export their known installed
bundle. Without either trusted root return `NEEDS_CONTEXT`. Run `li-work-artifacts.py` and
`li-swarm.py verify` with the working repo only as `--repo`. Tests/self-checks export
`LINTEL_SOURCE_ROOT` explicitly. Preserve the work map, charter, briefs, worker reports, and
independent reviews with the trio; they are the cold-resume evidence for topology and ownership.
Do not copy task text, dependencies, status, or acceptance into coordination.

Only the coordinator may set the work-map status to `COMPLETE`, and only after all lane evidence,
serial integration, final integrated REVIEW, and SHIP evidence pass. Local runtime attempt files and
abandoned worktrees are not durable completion evidence.

When `mode=meta-infra` also applies, load the required
[M4 swarm recap](../../../skills/cycle/references/maintainer.md#m4-swarm-recap) from the
maintainer method. It retains every future-operator field without adding this
maintainer procedure to an ordinary consumer capture.

Never claim independent review when the same identity implemented and reviewed a lane. Honest
degradation is part of the durable outcome, not a concern to hide.

### Step 7 — Role debrief (if role was active)

If role was active during cycle:
- Review role's OUTCOME LENS per phase against actual outcomes
- Did role lens add value? Where did it conflict with engineering reality?
- Propose any INSIGHTS update; retain the operator's confirmation for that exact change.
- Apply confirmed updates through the [shared role lifecycle](../../../skills/role/references/lifecycle.md),
  using the actual resolved destination and reviewed digest, not a guessed home path.
  Private role metadata/body access and transfer require their explicit consent.
  Keep an unapproved update as a proposal; do not write a second role file or
  turn debrief approval into permission to read, replace or export another role.

### Step 7b — Vault sink (session summary → knowledge vault)

Config-gated, optional, NEVER blocking. Only when the current verified profile
resolves `capture.vault_sink_enabled` to `true`, load the
[vault method](../../../skills/capture/references/vault.md). If disabled, do not load the procedure,
look up a destination or write. If resolution is unavailable, warn that export
was not performed; continue the independent capture.

The method owns the existing selected-repository/audit preflight, authorized
destination, locked note schema, hub/index maintenance and mandatory sensitive-data
check. Export still requires an existing authorized destination and acceptable
content; enabling a field or loading the method is not transfer permission.
Repo capture remains in place, with no vault-to-repo ingestion or personal scan.

### Step 8 — Retrospective (--retrospective)

Only for `--retrospective`, or when the operator selects a useful retrospective
for a substantial cycle, load the
[retrospective method](../../../skills/capture/references/reports.md#step-8--retrospective---retrospective).
It owns the existing window defaults, evidence selection, observation shape and
per-lesson authorization. Otherwise skip this optional view. The standalone
report returns without cycle-completion or other CAPTURE mutation steps.

### Step 8b — Release report (--release-summary)

Only for `--release-summary` or a requested SHIP release report, load the
[release-report method](../../../skills/capture/references/reports.md#step-8b--release-report---release-summary).
It owns the original revision/time/scope selection, delivered-work evidence,
statistics, draft voice and sensitive-data boundaries. A report creates no
release, tag, commit, publication or approval, and does not invoke the other
CAPTURE mutation steps.

#### Keep a Changelog output

This compatibility anchor for ChangelogMaintainer and SHIP selects the
[Keep a Changelog method](../../../skills/capture/references/reports.md#keep-a-changelog-output) only
when that format/output was requested. Apply it in the current context with the
same release evidence; do not dispatch a duplicate report or run other CAPTURE
mutation steps.

### Step 9 — (removed in v5, ADR-0006)

The operator-profile append (`~/.lintel/state/operator-profile.jsonl`) was a dead write — the
promised SENSE read-back never existed. Subtracted. The granularity calibration record (Step 1b)
is the real feedback loop and stays.

### Step 10 — 00-state.md final entry

Capture can record an unfinished cycle without marking it complete. Set the actual
outcome from verified evidence; preserve its original unfinished phase when blocked:

```bash
source "${LINTEL_SOURCE_ROOT:?select the trusted source}/lib/state.sh"
case "${capture_outcome:?set actual objective outcome}" in
  DONE|DONE_WITH_CONCERNS)
    state_append CAPTURE DONE cycle_complete=true "outcome=$capture_outcome" ;;
  BLOCKED|IN_PROGRESS)
    state_append CAPTURE DONE cycle_complete=false "outcome=$capture_outcome" \
      "next=${capture_resume_phase:?set original unfinished phase}" ;;
  *) echo "CAPTURE: unknown outcome; completion not recorded" >&2; exit 1 ;;
esac
```

### Step 11 — Closing message

Tight closing — terse artifact list + operator-pattern observations, no motivational filler:

```
LINTEL CAPTURE — <wedge title and actual objective status>

Duration: <hours human / <minutes> CC
Usage: <observed/estimated value with source, or unknown>
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
- /li-resume picks up next cycle from here
```

## Reusable patterns

Follow the [reusable pattern consumer contract](../../../skills/pattern/references/consumer-contract.md).
CAPTURE may propose new patterns or changes that emerged in the cycle. Write them as drafts with
`bash "$LINTEL_SOURCE_ROOT/bin/li-pattern" capture --scope repo|personal`, keeping operator
statements separate from observations and recording confidence, reuse rights and unknowns
honestly. Never approve, publish over, re-bind or edit an existing pattern or lock; approval is
a separate reviewed `approve` step. Handoff notes name the lock, task map and context files so a
fresh session can reconstruct and verify the selection.

## Status protocol

- **DONE** — authorized capture artifacts persisted; cycle completion is reported
  separately and requires actual objective evidence, not a profile mutation
- **DONE_WITH_CONCERNS** — captured but operator deferred ADR draft or lessons capture
- **BLOCKED** — only if filesystem unavailable (rare)

## Pause-points (mostly operator-confirms)

- Per candidate lesson: ask_user capture / skip / edit
- Per candidate ADR: ask_user draft now / draft later / skip
- After trio drafted: ask_user "Verify with dogfood subagent?" (optional)
- Role debrief (if active): ask_user "Update role file with these insights?"

## Hop-in support

YES — standalone post-implementation reflection. Useful if operator forgot CAPTURE in prior session.

## Integration

**Reads:**
- All `.claude/runtime/state/00-state.md` entries from cycle
- `.claude/runtime/state/build-log.md`
- `.claude/runtime/state/review-report-*.md`
- `.claude/runtime/state/compliance-report-*.md` (if the active pack defines compliance gates)
- selected design/spec/plan/prompt artifacts with their actual recorded status
- selected work.json and optional swarm coordination/charter/brief/report/review evidence
- Cycle's git diff for change scope
- role file (if active)

**Writes:**
- The project lessons store from `lintel_lessons_file` (conditional append/update/supersede per captured lesson through `bin/li-lessons.py`)
- `.claude/decisions/NNNN-<slug>.md` (new ADR if drafted)
- `EVOLUTION-LOG.md` (if CLAUDE.md changed)
- Mapped `spec`/`plan` (reconciled only within original authority)
- Mapped `tasks` (original IDs and evidence-backed status; unresolved work stays open)
- Mapped `prompt` (reaffirmed, not recreated)
- swarm work map and evidence artifacts (reaffirmed when the execution profile was selected)
- `.claude/memory/retros/<date>-<cycle-id>.md` (optional normal-cycle retrospective)
- Explicit `--out` report destination (standalone views only when authorized)
- `~/.lintel/roles/<id>.md` (update if role active + insights to add)
- `.claude/runtime/state/00-state.md` (CAPTURE final entry)
- `.claude/runtime/audit/cycle-completion.jsonl`
- `.claude/runtime/audit/granularity.jsonl` (append — actual-vs-estimated calibration record, via `audit_log`; read by `lib/scale-estimator.sh` `scale_calibrated_prior`)
- `<capture.vault_sink_path>/YYYY-MM-DD-<repo>-<slug>.md` (optional — vault sink, Step 7b; only if `capture.vault_sink_enabled: true` and the path exists)

**Triggers:**
- Nothing automatically — cycle complete
- `/li-resume` available for next cycle
- If part of multi-cycle engagement: next cycle starts at SENSE or DEFINE

## Recommended agents

- **ADRDrafter** (engineering/) — primary, ADR drafting
- **ChangelogMaintainer** (engineering/) — optional format-specific view of Step 8b;
  use the same method in the current context, not a second default release-summary pass
- **DocWriter** (engineering/) — synthesize cold-executor trio prose
- The active pack's voice gates (`resolve_pack_field voice.gates_active`; none by default) — if any CAPTURE artifact ships outside (rare)

## Anti-patterns

- **Auto-adding every correction to lessons.md** — filter for durable patterns only (operator confirms each)
- **Drafting ADR for trivial decisions** — ADR has overhead, reserve for decisions worth preserving
- **Skipping cold-executor trio because "we shipped already"** — the trio is the durable artifact, more valuable than the PR after months pass
- **Polluting role-file with session-specific data** — role files are persistent identity, not session log
- **Activating granularity writes as bookkeeping** — Step 1b stays dormant without
  its own authorization/behavior evidence; unknown usage is not an invented sample
- **Long retro write-up when cycle was small** — retro is optional + light
- **Reducing a swarm to runtime history** — preserve committed topology, briefs, reports, reviews,
  integration order, and honest host limitations for cold resume

## Failure recovery

- **lessons store missing**: `bin/li-lessons.py add` creates it from the scaffolding template with the same conditional write (inside a repository only), then proceeds
- **.claude/decisions/TEMPLATE.md missing**: prompt operator to run `bin/li-scaffold init` first
- **operator can't decide on lesson capture**: capture as PROVISIONAL (low confidence flag), they can promote/remove later
- **CLAUDE.md changed but operator says "not significant"**: skip EVOLUTION-LOG, but log audit-trail note

## Voice tier behavior

`voice: internal`. CAPTURE artifacts are mostly engineering-internal. Customer-facing release notes are drafts until their required gates and distribution
authority are satisfied. `--voice customer` follows the active pack's configured policy;
the default release-summary voice remains internal.

## Cycle-position footer

Close your report with the shared position footer so the operator always knows where they are in the
cycle and the one logical next action — whether this phase ran standalone or inside `/li-cycle`:

```bash
source "${LINTEL_SOURCE_ROOT:?select trusted source}/lib/cycle-footer.sh"
render_cycle_footer                               # reads .claude/runtime/state/00-state.md; --compact for short replies
```

Skipped phases render `⊘`; ASCII via `LINTEL_ASCII=1`. See [ADR-0003](../../../.claude/decisions/0003-cycle-position-footer.md).
