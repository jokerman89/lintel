---
name: capture
layer: foundation
description: Use after SHIP, at the end of a task, to make what was learned durable — updates lessons, drafts an ADR for any non-trivial decision, appends the evolution log, and reaffirms the cold-executor handoff trio against build evidence. The cycle's last step; carries continuity to the next session.
color: cyan
tools: Read, Write, Edit, Bash, Grep, Glob
voice: internal
cli_support: [claude-code, codex, copilot]
necessity: STRONGLY_RECOMMENDED
gap_if_skipped: "Lessons, ADRs, and EVOLUTION-LOG entries are never written and the cold-executor trio is never reaffirmed against build evidence; cross-session continuity is lost and the next operator re-derives everything."
---

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

Follow the [shared work-map contract](../spec-kit/references/work-map.md), including
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

Invoke `/li:lessons-add` (or inline):

For each correction operator made during the cycle:
- Was this correction GENERAL (would apply to future work) or SPECIFIC (one-time)?
- If GENERAL: candidate for the project lessons store (`lintel_lessons_file`; `.claude/memory/lessons.md` on the v5 layout)
- If SPECIFIC: keep in this cycle's notes only

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

AskUserQuestion per candidate lesson: "Capture as <classification>? (yes / no / edit-first)"

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

For each NEW lesson captured, AskUserQuestion: "Promote to the Lintel scaffolding baseline (scaffolding/01-foundation/.claude/memory/lessons.md in an explicitly named Lintel work tree)? — applies to future scaffolded repos."

If yes: invoke `/li:lessons-promote` (which runs `bin/li-lessons-promote` with an explicit destination and source label).

This is how operator-discovered patterns become team-wide knowledge.

### Step 4 — ADR draft (if non-trivial decision)

Scan cycle history for non-trivial decisions:
- Architectural picks (alternative A vs B chosen)
- Pattern adoptions (new pattern introduced)
- Trade-off decisions (accepted P3 finding, deferred P2)
- Scope changes (descoped feature, added scope)

For each candidate, AskUserQuestion: "Draft ADR for this decision?"

If yes: invoke `/li:adr-new "<decision title>"`:
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
- Status: APPROVED (from PLAN) — unchanged unless drift detected

**Mapped `tasks` reaffirm**:
- Annotate the original tasks with actual verified status, preserving IDs and parser
  structure. Missing/blocked/deferred work stays open; CAPTURE does not approve it
- Acceptance criteria post-verification (which actually passed)
- The mapped `plan` receives design reconciliation, never a duplicate task list

**`prompt.md` reaffirm** (born in PLAN, v3.8 Feature 2.2 moved birth to PLAN):
- Verify prompt.md still describes the work accurately
- Add any "What you DON'T need to know" entries discovered during BUILD
- Path: the map's original `prompt` value, including non-sibling Spec Kit handoffs

**Why moved to PLAN:** standalone `/li:plan <design.md>` (workflow_root post-v3.8) needs to produce the complete trio at PLAN-time. CAPTURE-only generation broke that — operator running PLAN solo got 2/3 of a handoff. Trio born together fixes this.

AskUserQuestion: "Want to dogfood the trio? Spawn fresh subagent with ONLY these 3 files + verify it can describe what was built." (Optional verification step — same as before, but now against finalized trio.)

**Handoff-size check (advisory).** Invoke `/li:handoff-size-check --map <same map>`
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

For meta-infra M4, the future-operator recap must name:

- the explicit opt-in fields and coordination path;
- the actual host tier used (`native`, `sequenced`, or `none`) and whether writers really ran
  concurrently;
- the isolation/attribution method and deterministic integration order;
- lane reports/reviews plus final integrated review evidence;
- any lost attempts, sequenced fallback, migration, deprecation, or unverified host behavior.

Never claim independent review when the same identity implemented and reviewed a lane. Honest
degradation is part of the durable outcome, not a concern to hide.

### Step 7 — Role debrief (if role was active)

If role was active during cycle:
- Review role's OUTCOME LENS per phase against actual outcomes
- Did role lens add value? Where did it conflict with engineering reality?
- Update role file with any new INSIGHTS learned (operator confirms)
- Sensitivity-aware: if role is private, updates stay in `~/.lintel/roles/private/<role-id>.md`

### Step 7b — Vault sink (session summary → knowledge vault)

Config-gated, optional, NEVER blocking. Writes a short human-readable session summary to an
external knowledge vault (e.g. an Obsidian vault) so the vault becomes the cross-repo memory
layer. The repo's own capture artifacts (Steps 1–7) are unaffected — this is an additional
sink, not a move. Nothing is ever read back from the vault into the repo.

```bash
source "${LINTEL_SOURCE_ROOT:?select trusted source}/lib/pack-resolver.sh"
sink_enabled=$(resolve_pack_field capture.vault_sink_enabled)
sink_path=$(resolve_pack_field capture.vault_sink_path)    # relative to repo root

if [ "$sink_enabled" != "true" ]; then
  : # disabled — skip silently
elif { case "$sink_path" in /*|[A-Za-z]:*) sink_dir="$sink_path" ;; *) sink_dir="$REPO_ROOT/$sink_path" ;; esac; [ ! -d "$sink_dir" ]; }; then
  echo "[lintel/capture] WARN: vault_sink path not found: $sink_path — skipping vault export"
  audit_log capture vault_sink_skipped "reason=path_missing" "path=$sink_path"
fi
# A missing or disabled vault must NEVER fail CAPTURE — one-line warn, then move on.
```

When enabled and the path exists, write exactly ONE file per session,
`<sink_path>/YYYY-MM-DD-<repo>-<short-slug>.md`:

```markdown
---
created: YYYY-MM-DD
tags: [session]
type: session
repo: <repo-name>
branch: <git-branch>
outcome: shipped | in-progress | blocked | exploration
session: <cycle-id-if-available>
---
# <one-line session title>

## What was done
<3–8 lines, plain language, no code dumps>

## Decisions
<decisions taken, one line each; "None" if none>

## Open threads
<unfinished items / next steps; "None" if none>

## Pointers
- <repo-relative paths to the key files/PRs touched>

## Links
- [[<repo-name>]] <- the repo hub note (backlinks = per-repo session history)
- [[<previous session note name>]] <- predecessor, if one exists for this repo
```

The frontmatter is a LOCKED flat schema (ADR-0007) — `sessions.base` (the Bases dashboard
installed by `bin/li-vault-init`) and the vault's own skills query these exact properties.
`outcome` uses the controlled vocabulary above, nothing else.

**After writing the note, maintain the two navigation surfaces (same sink dir):**
1. **Hub note** `<sink_path>/<repo-name>.md` — create a minimal one if missing (frontmatter:
   `created:`, `tags: [hub]`, `type: repo-hub`, `repo:`; one line of prose — same shape
   bin/li-vault-init writes). Never overwrite an existing hub.
2. **Index** `<sink_path>/00-index.md` — create it if missing (frontmatter `type: session-index`
   + one intro line), then maintain the list under its heading: carry the existing entries
   forward, PREPEND this session's line, truncate to 15:
   `- [[<note-name>]] - <one-line title> (<repo>)`. Keep frontmatter + intro intact; touch only
   the list. (Carrying forward the index's own lines is the one sanctioned vault read — never
   read other notes back.)

Source the content from the Step 1 cycle aggregation. **Hard rules:** no secrets or tokens, no
customer or employer-internal data, no full file contents — repo-relative pointers instead of
payloads. Render the headings AND body in the session's working language (the template above is
the canonical English form — translate it wholesale when the session ran in another language).
Frontmatter must parse.

**MANDATORY pre-write scan (battletest K4 — the vault note lands OUTSIDE the repo, where no
git-commit hook sees it).** The "hard rules" above are not enough on their own — scan the
rendered note body programmatically before writing, and ABORT the export (warn, never fail
CAPTURE) on any hit:

```bash
source "${LINTEL_SOURCE_ROOT:?select the trusted source}/hooks/shared/_patterns.sh"
note_body="$(cat "$rendered_note")"
sec_hits="$(scan_secrets all "$note_body")"
pii_hits="$(scan_customer "$note_body")"
if [ -n "$sec_hits$pii_hits" ]; then
  echo "[lintel/capture] WARN: vault export ABORTED — ${sec_hits:+secrets: $sec_hits }${pii_hits:+pii: $pii_hits}"
  audit_log capture vault_sink_skipped "reason=sensitive_content" "secrets=$sec_hits" "pii=$pii_hits"
  # skip the write entirely — do NOT sanitize-and-ship; an aborted export is correct
else
  # write the note, then:
  audit_log capture vault_sink_written "file=<filename>"
fi
```

### Step 8 — Retrospective (--retrospective)

Reflect on a concrete window using actual observations. Explicit `--since` wins; otherwise
`--scope day` means the prior 24 hours, `week` seven days, and `session` uses the latest
owned checkpoint timestamp when available, else a labelled 24-hour fallback. Validate
checkpoint provenance through `context_latest` / `context_checkpoint`, not a raw home scan.
A supplied revision is resolved to a real commit/time before reading history.

Gather only signals relevant to the selected work/window:

- Git commits and current task status, without calling local commits deployed or merged.
- Audit files named by `audit_read_files <category>` and read through `bin/li-events.py`
  with `--since`; retain diagnostics and name any additional legacy source not read.
- Recorded skill invocations in `usage-*.jsonl` under `audit_dir usage-skill`, when
  authorized and available. Recording is optional; absence is unobserved, not disuse.
- `state_cycle_segment` for the selected original cycle, not an unrelated ledger segment.

Report **delivered**, **stuck**, **surprises**, **what worked**, **friction** and
**patterns worth recording**, each with its actual evidence or uncertainty. Keep ledger
`BLOCKED`/`INCOMPLETE`/`UNTRUSTED` separate from a hook decision (`tier=BLOCK`,
`blocked="true"`, `check=performed|not_performed`). A hook block record is not evidence
of host enforcement. No commits does not mean no work; include observed uncommitted
progress without inventing delivery.

`--emit-lessons` proposes one to three useful patterns, with an existing-ID deduplication
check and explicit authorization per candidate before a write. Respect already explicit
approval of named candidates; do not demand a second approval for the same scope.
No durable pattern is a valid result. Audit failure leaves a degraded report with the
remaining real signals, not a healthy empty history.

During normal cycle CAPTURE, an authorized retrospective may be stored at
`.claude/memory/retros/<date>-<cycle-id>.md`. For standalone `--retrospective`, persist
only when `--out` was selected. Retain the compact observation shape:
```yaml
cycle_id: <id>
duration_human: <hours>
duration_cc: <minutes>
tokens_used: <approx>
usage_provenance: observed | estimated | unknown
# billing: <actual supplied billing evidence only; omit when unknown>

what_worked:
  - <thing>
what_friction:
  - <thing>
next_time:
  - <pattern to repeat>
  - <pattern to avoid>
```

Not always written — only if cycle was substantial enough that retro adds value (operator-driven).

### Step 8b — Release report (--release-summary)

Use the actual commit/tag window and delivery evidence to brief teammates or draft release
notes. Explicit `--since`/`--until` win; otherwise use the latest reachable tag to HEAD,
or a labelled seven-day window when no tag exists. Resolve revisions with
`git rev-parse --verify --end-of-options "<ref>^{commit}"`; pass the resulting full IDs
as quoted Git arguments. Pass time filters and optional literal path scope as separate
arguments too. Never evaluate report input as shell code, assume a `main` branch or
invent a release tag.

Gather commit subjects, scopes and actual changes. Local Git is sufficient for a local
change summary, not for claiming a merged PR or deployment. Read selected PR/delivery
evidence only through available authorized tools; absent authorization or tools means a
Git-only report with that limitation. No automatic network query follows from this mode.

Group Conventional Commits by feature/fix/docs/refactor/chore and area; keep other history
in an explicitly labelled uncategorized group rather than dropping it. Preserve these
sections when applicable:

- **Delivered work**: what verifiably landed, with commits/tags/PR evidence.
- **Features and fixes**: capabilities and corrected behavior, not just renamed files.
- **Migration notes**: replaced entry points, retained data/flags and operator actions.
- **Limitations and not shipped**: open original cards, unrun checks and unmet gates.
- **Statistics** (`--include-stats`): actual commit/file/change/contributor counts over
  the same window/scope; no invented PR count or personal contact details.

Default `--voice internal` is a concise engineering report. `--voice customer` produces
a **DRAFT**, preserving source fidelity and using the active pack's configured voice
policy and corpus. Missing corpus is uncalibrated; unavailable required review stays
unverified. The draft is not approved for distribution merely because it was rendered.
Before rendering, apply the actual applicable sensitive-data checks to ingested commit
and PR text. On a hit, name the source without repeating the sensitive payload and stop
that output; do not rewrite history or sanitize-and-publish as a workaround.

An empty selected window is reported as empty. Missing history, denied reads or unknown
delivery are limitations, not success. The report can feed SHIP's existing PR/release
documentation, but it creates no release, tag, commit, publication or approval.

Examples:

```text
/li:capture --retrospective --scope day --emit-lessons
/li:capture --release-summary --since <verified-tag> --until HEAD --include-stats
/li:capture --release-summary --scope skills --voice customer --out <authorized-draft>
```

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
- /li:resume picks up next cycle from here
```

## Status protocol

- **DONE** — authorized capture artifacts persisted; cycle completion is reported
  separately and requires actual objective evidence, not a profile mutation
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
- All `.claude/runtime/state/00-state.md` entries from cycle
- `.claude/runtime/state/build-log.md`
- `.claude/runtime/state/review-report-*.md`
- `.claude/runtime/state/compliance-report-*.md` (if the active pack defines compliance gates)
- design doc, plan.md (DRAFT), spec.md (DRAFT)
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
cycle and the one logical next action — whether this phase ran standalone or inside `/li:cycle`:

```bash
source "${LINTEL_SOURCE_ROOT:?select trusted source}/lib/cycle-footer.sh"
render_cycle_footer                               # reads .claude/runtime/state/00-state.md; --compact for short replies
```

Skipped phases render `⊘`; ASCII via `LINTEL_ASCII=1`. See [ADR-0003](../../.claude/decisions/0003-cycle-position-footer.md).
