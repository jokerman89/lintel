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
1. **Lessons** — corrections from BUILD/REVIEW → `.claude/memory/lessons.md` (filtered, durable patterns only)
2. **ADR** — non-trivial decisions → `.claude/decisions/NNNN-<slug>.md`
3. **EVOLUTION-LOG** — CLAUDE.md changes → log entry
4. **Cold-executor handoff trio** — reaffirm `spec.md` + `plan.md` + `prompt.md` against build evidence (trio BORN in PLAN per v3.8 Feature 2.2; CAPTURE only annotates with actual-build outcomes)

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

Read entire cycle's `.claude/runtime/state/00-state.md` log. Extract:
- Phases completed + their durations + token cost
- Corrections operator made during BUILD/REVIEW (from build-log)
- Decisions taken (alternatives chosen in DEFINE, scope changes in PLAN)
- Reviewer concerns from REVIEW
- Compliance gates that fired + outcomes

This is the source data for capture artifacts.

### Step 1b — Granularity calibration record (scale-estimator feedback)

Close the calibration loop (design §3.5): record this cycle's **actual** outcome against the SCOPE estimate so `lib/scale-estimator.sh` can correct its token/size priors next time. Today the estimate is born in SCOPE but never compared to reality — this step is the missing feedback edge.

Mechanical, non-blocking. Read the planned scale from `scope.md` (or the cycle's `00-state.md` SCOPE entry) and the actuals from the cycle history aggregated in Step 1, then append one record via the unified `audit_log` writer — the same call pattern every other Lintel producer uses (e.g. `skills/migrations`):

```bash
# A skill body has no reliable $0/BASH_SOURCE — resolve the repo root the way
# every other skill does ($LINTEL_REPO_ROOT), with a git fallback if it is unset.
# Using $(dirname "$0") here made this calibration write silently no-op.
REPO_ROOT="${LINTEL_REPO_ROOT:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"
source "$REPO_ROOT/bin/_audit.sh"

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

If any field is unavailable (e.g. SCOPE was silent on an XS request, or tokens weren't tracked), pass what you have and omit the rest — `audit_log` records whatever k=v pairs it's given; a partial record is still useful history. Never block the cycle on this; a failed write is silent by design (`_audit.sh` swallows write errors).

The estimator's `scale_calibrated_prior <size>` reads exactly this log: it takes the median `actual_tokens` for a size as the corrected prior, falling back to the mechanical default when no history exists. One record per cycle here is what makes the next estimate sharper.

### Step 2 — Lessons capture (filtered)

Invoke `/li:learn` (or inline):

For each correction operator made during the cycle:
- Was this correction GENERAL (would apply to future work) or SPECIFIC (one-time)?
- If GENERAL: candidate for `.claude/memory/lessons.md`
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
source "$LINTEL_REPO_ROOT/lib/memory.sh"
lessons_find_related <candidate keywords>    # all related active lessons, ranked
```

Classify against the hits:
- **add** — nothing related exists → new `## L-NNN — <title>` entry
- **update** — an existing lesson covers it but the candidate sharpens it → extend THAT lesson's
  How-to-apply (note the cycle id), no new entry
- **supersede** — the candidate CONTRADICTS an existing lesson → write the new entry, then add
  `superseded_by: L-<new> (<date>)` as the first body line of the old one. Never delete or edit
  the old lesson away — git holds ingestion history, the marker holds validity
  (supersede-don't-delete).
- **no-op** — an existing lesson already says this → skip, mention the existing id

AskUserQuestion per candidate lesson: "Capture as <classification>? (yes / no / edit-first)"

If add: append to `.claude/memory/lessons.md`:
```markdown
## L-NNN — <lesson title>
<lesson body: Rule / Why / How to apply>
<-- Captured from cycle <cycle-id> by <operator>. -->
```

### Step 3 — Promote lesson check (NEW)

For each NEW lesson captured, AskUserQuestion: "Promote to Lintel global lessons (scaffolding/01-foundation/.claude/memory/lessons.md)? — applies to ALL future scaffolded repos."

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
- Path: `.claude/plans/<slug>/prompt.md` (born by PLAN, lives there)

**Why moved to PLAN:** standalone `/li:plan <design.md>` (workflow_root post-v3.8) needs to produce the complete trio at PLAN-time. CAPTURE-only generation broke that — operator running PLAN solo got 2/3 of a handoff. Trio born together fixes this.

AskUserQuestion: "Want to dogfood the trio? Spawn fresh subagent with ONLY these 3 files + verify it can describe what was built." (Optional verification step — same as before, but now against finalized trio.)

**Handoff-size check against the 500k cap (NON-BLOCKING).** The reaffirmed trio is the durable cold-executor handoff — the artifact a fresh cold session reads to re-execute. Run the existing cap check so the finalized trio (now annotated with build evidence, possibly larger than at PLAN-time) plus any warming context can't silently exceed the 500k cap. This closes the second un-gated handoff the v4.9 audit flagged (Promise 6: cap logic existed but was invoked at no handoff).

Invoke the existing mechanism — do **not** rebuild it:

`/li:handoff-size-check` (a portable skill call; reads the reaffirmed trio + `.claude/runtime/state/warming-manifest.md`, applies the mode-aware cap from `/li:context-budget` mode_envelopes, default `customer-engagement: 500k soft / 750k hard`).

- **SURFACE, don't block.** A yellow/red verdict warns ("finalized trio yields ~Nk handoff, near cap") and notes the durable handoff is large — the operator decides whether to trim before it becomes the cross-session record. It does NOT halt CAPTURE.
- **Off-switch:** `--skip-handoff-size-check` (or `SKIP_HANDOFF_SIZE_CHECK=1`) skips the gate entirely. Silent when skipped, and silent on a green pass.

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
source "$LINTEL_REPO_ROOT/lib/pack-resolver.sh"
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
Frontmatter must parse. After writing: `audit_log capture vault_sink_written "file=<filename>"`.

### Step 8 — Retro (optional, light)

Append to `.claude/memory/retros/<date>-<cycle-id>.md`:
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

### Step 9 — (removed in v5, ADR-0006)

The operator-profile append (`~/.lintel/state/operator-profile.jsonl`) was a dead write — the
promised SENSE read-back never existed. Subtracted. The granularity calibration record (Step 1b)
is the real feedback loop and stays.

### Step 10 — 00-state.md final entry

Mechanical since v5.0 (ADR-0008) — one command, not a YAML obligation. No `next=`: the cycle is complete (`/li:resume` keys off `cycle_complete: true`); the full artifact list lives in the Step 11 closing message:

```bash
source "$LINTEL_REPO_ROOT/lib/state.sh"
state_append CAPTURE DONE cycle_complete=true outcome=<DONE|DONE_WITH_CONCERNS|BLOCKED> lessons_captured=<count> adrs_drafted=<count> total_tokens=<N> cost_estimate=<$X>
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
- All `.claude/runtime/state/00-state.md` entries from cycle
- `.claude/runtime/state/build-log.md`
- `.claude/runtime/state/review-report-*.md`
- `.claude/runtime/state/compliance-report-*.md` (if the active pack defines compliance gates)
- design doc, plan.md (DRAFT), spec.md (DRAFT)
- Cycle's git diff for change scope
- role file (if active)

**Writes:**
- `.claude/memory/lessons.md` (append per captured lesson)
- `.claude/decisions/NNNN-<slug>.md` (new ADR if drafted)
- `EVOLUTION-LOG.md` (if CLAUDE.md changed)
- `spec.md` (FINALIZED from PLAN's draft)
- `plan.md` (FINALIZED with post-verification status)
- `prompt.md` (NEW — cold-executor handoff)
- `.claude/memory/retros/<date>-<cycle-id>.md` (optional)
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
- **Forgetting to update operator profile** — gstack pattern for cross-session tier tracking
- **Long retro write-up when cycle was small** — retro is optional + light

## Failure recovery

- **lessons.md missing**: create via `bin/li-scaffold` template, then proceed
- **.claude/decisions/TEMPLATE.md missing**: prompt operator to run `bin/li-scaffold init` first
- **operator can't decide on lesson capture**: capture as PROVISIONAL (low confidence flag), they can promote/remove later
- **CLAUDE.md changed but operator says "not significant"**: skip EVOLUTION-LOG, but log audit-trail note

## Voice tier behavior

`voice: internal`. CAPTURE artifacts are mostly engineering-internal. Customer-facing release notes (if shipped from CAPTURE) follow the active pack's voice tier (`resolve_pack_field voice.default_tier`; default: internal).

## Cycle-position footer

Close your report with the shared position footer so the operator always knows where they are in the
cycle and the one logical next action — whether this phase ran standalone or inside `/li:cycle`:

```bash
source "$LINTEL_REPO_ROOT/lib/cycle-footer.sh"   # fallback: "$(git rev-parse --show-toplevel)/lib/cycle-footer.sh"
render_cycle_footer                               # reads .claude/runtime/state/00-state.md; --compact for short replies
```

Skipped phases render `⊘`; ASCII via `LINTEL_ASCII=1`. See [ADR-0003](../../.claude/decisions/0003-cycle-position-footer.md).
