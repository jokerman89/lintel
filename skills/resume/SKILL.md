---
name: resume
layer: foundation
description: Use at the start of a fresh session to pick up work left in flight — reads 00-state.md and resumes the cycle at the next recommended phase, or one you name. The cross-session continuity entry point when a prior task was interrupted mid-cycle.
color: cyan
tools: Read, Bash, Grep, Glob
voice: internal
cli_support: [claude-code, codex, copilot]
---

You are the RESUME skill — cross-session continuity for Lintel cycle.

## What this skill does

Reads `.claude/runtime/state/00-state.md` from cwd, determines where the prior session ended, and routes operator to the next-recommended phase (or operator-specified override). Handles:
- Resume mid-cycle (paused/aborted before)
- Resume new cycle starting from CAPTURE artifacts of prior cycle
- Cross-session continuity when operator returns days/weeks later

Not a true phase — utility skill that lands the operator in the right phase.

## When to use

- Operator returns to repo after break and wants to pick up
- Cross-machine continuation (operator on machine A yesterday, machine B today)
- After session crash / abort
- Operator types `/li:resume`

## When NOT to use

- Brand-new cycle in clean repo (use `/li:cycle` or `/li:sense`)
- Within active cycle (no need to resume what's in progress)
- Operator already knows which phase they want (just invoke directly)

## Workflow

### Step 1 — Locate state

First honor an operator-selected work map or unambiguous committed active-work links using
Step 1c, even when local runtime files exist. A checkpoint/ledger from a different initiative
cannot override that selection. Reconcile the selected task source and evidence with the
checkout before using its runtime resume hints. Helpers load from `LINTEL_SOURCE_ROOT`;
all selected work-artifact paths resolve inside `LINTEL_REPO_ROOT`.

RESUME has **three** prior-work sources: committed work maps/plans, local cycle ledgers and checkpoints. The committed fallback below survives a fresh clone. Historically there were only two sources, and historically it only saw one of them: the
cycle ledger (`00-state.md`). The other is a `/li:context-save` **checkpoint** — written
to `.claude/runtime/sessions/<branch>/`. A session that ended with `/li:context-save` (not
mid-cycle) leaves a checkpoint but no `00-state.md` entry; resume must discover it and
hand off to `/li:context-restore` rather than misdirect the operator to a fresh cycle.

```bash
resume_source="${LINTEL_SOURCE_ROOT:-${LINTEL_REPO_ROOT:-$(git rev-parse --show-toplevel 2>/dev/null)}}"
source "$resume_source/lib/paths.sh"
resume_working_repo="$(lintel_repo_root)"
STATE_FILE="${LINTEL_STATE_DIR:-$(lintel_state_dir)}/00-state.md"
if [ ! -f "$STATE_FILE" ]; then
  # No state from this repo
  echo "NO_PRIOR_STATE_LOCAL"
  
  # Check cross-machine sync
  if [ -d "~/.lintel/lessons-vault" ]; then
    # Try to find this repo's state in synced lessons vault
    repo_slug=$(basename "$(git rev-parse --show-toplevel 2>/dev/null)")
    cross_state=$(find ~/.lintel/lessons-vault -name "00-state-$repo_slug-*.md" 2>/dev/null | head -1)
    [ -n "$cross_state" ] && {
      echo "CROSS_MACHINE_STATE_FOUND: $cross_state"
      cp "$cross_state" "$STATE_FILE"
    }
  fi
fi

# ALSO discover the newest context-save checkpoint for this branch. The mechanical
# core owns path + discovery (no raw glob); fall back to a bare glob if it's absent.
_ctx="${LINTEL_SOURCE_ROOT:-${LINTEL_REPO_ROOT:-$(git rev-parse --show-toplevel 2>/dev/null)}}/bin/_context.sh"
[ -f "$_ctx" ] || _ctx="$HOME/.lintel/bin/_context.sh"
checkpoint=""
if [ -f "$_ctx" ]; then
  # shellcheck disable=SC1090
  source "$_ctx"
  checkpoint="$(cd "$resume_working_repo" && context_latest 2>/dev/null || true)"   # current target branch only
else
  branch="$(git -C "$resume_working_repo" rev-parse --abbrev-ref HEAD 2>/dev/null || echo no-branch)"
  checkpoint="$(ls -t "$(lintel_sessions_dir)/$branch/"*-context-save.md 2>/dev/null | head -1 || true)"
fi
```

Then branch on what exists:

- **`00-state.md` present** → proceed to Step 1.5 (the cycle-ledger path, unchanged).
- **No `00-state.md` but `$checkpoint` set** → do **not** misdirect to `/li:cycle`. Surface the
  checkpoint and **offer `/li:context-restore <path>`**:

  ```
  No cycle ledger found, but a session checkpoint exists for this branch:
    <checkpoint path>  (<age>)
  Restore it to pick up where you left off:
    /li:context-restore <checkpoint path>
  (Or start fresh: /li:cycle for new work · /li:sense for a diagnostic.)
  ```

- **Neither local source present** → first run Step 1c below. Only if it finds no committed work, surface "No prior state found. Run `/li:cycle` for new work or
  `/li:sense` for diagnostic."

> **Paired with `/li:context-save`.** Resume discovers the checkpoints that `/li:context-save`
> writes; `/li:context-restore` is the skill that reads one back in. Resume *routes* to restore —
> it does not re-implement checkpoint parsing.

### Step 1c — Resume from committed work in a fresh clone

The local ledger and session saves are gitignored. Their absence is expected on another
machine and does not mean the initiative is new. Follow the
[shared work-map contract](../spec-kit/references/work-map.md): use an operator-named map,
then an unambiguous active map linked from `.claude/plans/todo.md` or working-state.md.
Validate it with `bin/li-work-artifacts.py --repo <working-repo> --map <selected-path>`.

If no map exists, inspect explicit links to committed plan/spec/prompt artifacts in todo.md
and working-state.md. Follow one unambiguous unfinished initiative; ask when several remain.
Never choose by newest timestamp. Read its real tasks, decisions and recorded authorization;
write a map when useful within scope. For Spec Kit, tasks.md owns checkbox state and task IDs.

Compare completed cards against committed code and referenced verification evidence. Identify
the first unfinished card whose dependencies are satisfied, or REVIEW if all cards are built.
Report any missing evidence rather than converting checked boxes into a claim that tests ran.
Recreate only local runtime bookkeeping after reconciling the selected work with the checkout.
An APPROVED map records prior scope; verify current user authority before external actions.
Continue at the selected BUILD/REVIEW phase using the mapped artifacts, without requiring an
old machine's 00-state.md, private checkpoint or a duplicate Lintel task list.
### Step 1.5 — Integrity check (v3.6 cohort 1 item 6.3)

Before trusting 00-state.md, validate it. Defensive guard against state-drift / wrong-branch / stale state.

```bash
# Read recorded branch + commit + timestamp from the CURRENT cycle's segment.
# The ledger is append-only across many cycles: a first-match (-m1) grep read
# the OLDEST cycle, so resume false-warned "stale" on any week-old file.
# state_cycle_segment (lib/state.sh) scopes to the last CYCLE block; the
# last match inside it is the current truth. The CYCLE entry records
# branch/commit since v5.3 (skills/cycle Step 4) — empty on older ledgers,
# and an empty value skips that check rather than warning.
seg="$(source "${LINTEL_SOURCE_ROOT:-$(git rev-parse --show-toplevel)}/lib/state.sh" 2>/dev/null && state_cycle_segment "$STATE_FILE")"
state_branch=$(printf '%s\n' "$seg" | grep '^branch:' | tail -1 | awk '{print $2}')
state_commit=$(printf '%s\n' "$seg" | grep '^commit:' | tail -1 | awk '{print $2}')
state_ts=$(printf '%s\n' "$seg" | grep '^ts:' | tail -1 | awk '{print $2}')

# Current state
current_branch=$(git -C "$resume_working_repo" rev-parse --abbrev-ref HEAD 2>/dev/null || echo unknown)
current_commit=$(git -C "$resume_working_repo" rev-parse HEAD 2>/dev/null || echo unknown)

issues=()

# Check 1: branch match (or warn if state is from other branch)
if [ -n "$state_branch" ] && [ "$state_branch" != "$current_branch" ]; then
  issues+=("branch-drift: state recorded on '$state_branch', currently on '$current_branch'")
fi

# Check 2: commit reachable (state's commit should be in current branch's history)
if [ -n "$state_commit" ] && [ "$state_commit" != "$current_commit" ]; then
  if ! git -C "$resume_working_repo" merge-base --is-ancestor "$state_commit" HEAD 2>/dev/null; then
    issues+=("commit-unreachable: state's commit $state_commit not in current branch history")
  fi
fi

# Check 3: staleness (warn if >7 days)
if [ -n "$state_ts" ]; then
  state_age_days=$(( ($(date +%s) - $(date -d "$state_ts" +%s 2>/dev/null || echo 0)) / 86400 ))
  if [ "$state_age_days" -gt 7 ]; then
    issues+=("stale: state is $state_age_days days old (>7d threshold)")
  fi
fi

# Surface to operator
if [ ${#issues[@]} -gt 0 ]; then
  echo "⚠ Resume integrity warnings:"
  printf '  - %s\n' "${issues[@]}"
  echo ""
  echo "Continue anyway? Reply YES to proceed, NO to abort and run /li:sense for diagnostic."
  # Block on operator confirm — do not auto-continue
fi
```

If integrity passes silently OR operator confirms continue → proceed to Step 2.
If operator aborts → exit BLOCKED with recommendation to run `/li:sense` for fresh diagnostic.

### Step 2 — Parse last state entry

Read `00-state.md`, find the LAST entry. Mechanical read via `lib/state.sh`: `state_last` prints the whole last block, `state_last <field>` (e.g. `state_last status`, `state_last next_recommended`) prints one field:
- Last phase completed
- Last phase status (DONE / DONE_WITH_CONCERNS / BLOCKED / paused)
- Next recommended phase
- Cycle ID + timestamp

```yaml
# Example parsed
last_phase: PLAN
last_status: DONE_WITH_CONCERNS
next_recommended: BUILD
cycle_paused: false
cycle_complete: false
cycle_id: 2026-05-27-1432-azure-toolbox
last_ts: 2026-05-27T22:00:00Z
duration_since_pause: 12 hours
```

### Step 2.5 — Resume granularity: node-path for tree plans (design §3.4)

A flat/phased plan resumes to a **phase** (`current_step`). A `tree`-schema
plan (L/XL, from the scale-parametric WBS) resumes to a **WBS node-path**
(`1.1.a`) — the deepest incomplete leaf — so a half-done big plan picks up at
the exact subtask, not the top of a phase.

When resuming a job (`/li:resume --job <id>`, the path `/li:jobs continue`
delegates to), ask `bin/_jobs.sh` for the resume point. It returns the first
incomplete-and-startable step `name`; for a tree job that name *is* the
node-path:

```bash
resume_source="${LINTEL_SOURCE_ROOT:-${LINTEL_REPO_ROOT:-$(git rev-parse --show-toplevel)}}"
source "$resume_source/bin/_jobs.sh"
resume_job_dir="$(job_path "${JOB_ID:?select the job to resume}")"
# SCOPE writes inside the selected job, never in the shared jobs parent directory.
# An explicitly linked scope path may override it; absence must not select another job.
resume_scope="${LINTEL_SCOPE_PATH:-$resume_job_dir/scope.md}"
case "$resume_scope" in
  /*|[A-Za-z]:/*) : ;;
  *) resume_scope="${LINTEL_REPO_ROOT:-$(git rev-parse --show-toplevel)}/$resume_scope" ;;
esac
if [ -n "${LINTEL_SCOPE_PATH:-}" ] && [ ! -s "$resume_scope" ]; then
  echo "RESUME BLOCKED: selected scope is missing or empty: $resume_scope" >&2
  exit 1
fi
schema=$(awk '/^depth_schema:/ { sub(/\r$/, ""); print $2; exit }' "$resume_scope" 2>/dev/null || true)

if [ "$schema" = "tree" ]; then
  node=$(job_resume_point "$JOB_ID")           # e.g. "1.1.a"  (deepest incomplete leaf)
  if [ -n "$node" ]; then
    resume_target="$node"                       # land on the exact subtask
  else
    resume_target=$(awk '/^current_step:/ { sub(/\r$/, ""); print $2; exit }' "$resume_job_dir/job.yaml")
  fi
else
  # flat / phased (or no scope.md): unchanged — resume to current_step.
  resume_target=$(awk '/^current_step:/ { sub(/\r$/, ""); print $2; exit }' "$resume_job_dir/job.yaml")
fi
```

`job_resume_point` skips any leaf still gated by its `blocked_until` predicate,
so the target is always both incomplete **and** startable. If it returns empty
(all leaves DONE, or no populated `steps[]`), fall back to `current_step` —
this keeps **flat/phased resume identical to before**. Surface the node-path in
the resume options (Step 3) so the operator sees "resume at 1.2.a — <subtask>"
instead of just the phase.

### Step 3 — Surface resume options

```
LINTEL RESUME — <cycle-id>

Last activity: <timestamp> (12 hours ago)
Last phase: PLAN (DONE_WITH_CONCERNS)
Cycle state: in-progress (4 of 8 phases done)

Phases done: ✓ SENSE ✓ DEFINE ✓ DISCOVER ✓ PLAN
Phases remaining: BUILD REVIEW SHIP CAPTURE

Concerns from last phase:
  - 2 reviewer concerns left in plan.md (line 142, line 187)
  
Estimated to complete: ~45 min, ~25k tokens, ~$2

Options:
  A) Resume at recommended next phase: BUILD
  B) Restart prior phase: PLAN (address concerns first)
  C) Jump to specific phase: pick one
  D) Re-run full cycle from start
  E) Abort cycle, archive state

What's your choice?
```

AskUserQuestion to operator.

### Step 4 — Validate resume context

Before invoking next phase, verify resume preconditions:

For BUILD resume:
- The explicitly selected map validates and its original spec/design/tasks are approved for
  the authorized scope, or an explicitly selected legacy native plan is approved. Spec Kit's
  implementation plan does not require Lintel's APPROVED heading.
- Resume the ready original leaf and its package; preserve completed evidence and recheck the
  affected package. An absent package table means singleton packages, not a duplicated backlog.
- Branch state OK (no surprise commits) ✓
- Test suite passes baseline ✓

For REVIEW resume:
- BUILD output exists (commits since last DEFINE phase) ✓

For SHIP resume:
- REVIEW PASS ✓
- Voice gate passed (if customer-engagement mode) ✓

For CAPTURE resume:
- SHIP DONE or operator explicit override ✓

If precondition fails: surface why, suggest correction or different phase.

### Step 5 — Cross-machine state handling (if applicable)

If state came from another machine (cross-machine sync via lessons-vault or operator manually copied):
- Surface: "State imported from machine <other>. Branch may differ. Verify before proceeding."
- AskUserQuestion: "Continue with imported state? (Y/n)"
- If yes: `state_append RESUME IMPORTED source="<machine-id or path>"`

### Step 6 — Invoke chosen phase

Based on operator's choice (Step 3 + 4):
- If A (next recommended): `/li:<recommended-phase>`
- If B (restart prior): `/li:<last-phase>` (re-runs from start)
- If C (specific): `/li:<chosen-phase>`
- If D (full cycle): `/li:cycle` (from start, ignoring prior state)
- If E (abort): `state_append RESUME ABORTED cycle_aborted=true`, archive to `~/.lintel/archive/`

### Step 7 — 00-state.md append

RESUME is a utility, not a cycle phase. Mechanical since v5.0 (ADR-0008) — one command, not a YAML obligation:

```bash
_sl="${LINTEL_SOURCE_ROOT:-${LINTEL_REPO_ROOT:-$(git rev-parse --show-toplevel 2>/dev/null)}}/lib/state.sh"
[ -f "$_sl" ] || _sl="$HOME/.lintel/lib/state.sh"; source "$_sl"   # installed by install.sh in consumer repos
state_append RESUME DONE prior_last_phase=<phase> operator_choice=<A|B|C|D|E> next_invoked=<phase> cross_machine=<yes|no>
```

## Status protocol

- **DONE** — operator chose, next phase invoked
- **NEEDS_CONTEXT** — state file corrupt or missing, can't determine resume point
- **BLOCKED** — precondition for chosen phase not met, AND operator can't fix immediately

## Pause-points

- After surfacing options: AskUserQuestion for choice
- If cross-machine state: confirm before adopting
- If precondition fails: AskUserQuestion alternative phase or fix-first

## Hop-in support

n/a — RESUME is itself the hop-in mechanism.

## Integration

**Reads:**
- `.claude/runtime/state/00-state.md` (PRIMARY)
- `.claude/runtime/sessions/<branch>/*-context-save.md` (checkpoint discovery via `context_latest` — routes to `/li:context-restore`)
- `~/.lintel/lessons-vault/00-state-<repo>-*.md` (cross-machine fallback)
- `.claude/runtime/jobs/<id>/job.yaml` `steps[]` (job-scoped resume — node-path via `job_resume_point`)
- The explicitly linked `LINTEL_SCOPE_PATH`, else the selected job's `scope.md` (the SCOPE
  writer's path); no jobs-parent or newest-directory lookup
- `plan.md`, `spec.md`, `review-report.md` (for precondition checks)
- recent git log

**Calls into:**
- `bin/_jobs.sh` — `job_resume_point` (tree node-path), `job_can_start` (skip blocked leaves), `job_path`
- `bin/_context.sh` — `context_latest` (newest checkpoint for the branch; offers `/li:context-restore`)

**Writes:**
- `.claude/runtime/state/00-state.md` (RESUME entry)
- `~/.lintel/archive/<cycle-id>/` (if operator aborts)

**Triggers:**
- Invokes operator's chosen phase-skill

## Anti-patterns

- **Auto-resume without confirmation** — always show prior state, let operator decide
- **Loading full prior session conversation history** — read just 00-state.md, not the whole context
- **Ignoring stale state** (>30 days old) — surface age, ask operator if still valid
- **Resuming with corrupt state file silently** — explicit error, don't guess

## Failure recovery

- **State file corrupt**: surface, suggest manual reconstruction OR start fresh with `/li:cycle`
- **No state found**: NOT a failure — first check for a context-save checkpoint (Step 1) and offer `/li:context-restore <path>`; only if none exists, gracefully redirect to `/li:sense` or `/li:cycle`
- **Cross-machine state mismatch (different branch)**: surface diff, ask operator to switch branch or proceed with caveat
- **Precondition fails 3x**: stop trying to resume that phase, suggest alternative

## Voice tier behavior

`voice: internal`. Resume output is operator-coordination.

## Cycle-position footer

Close your report with the shared position footer — resume's whole job is re-orienting the operator,
so the "you are here → next" block is the natural closing line (inside a cycle it shows the resumed
position; with none active, the thin ambient line):

```bash
source "${LINTEL_SOURCE_ROOT:-$LINTEL_REPO_ROOT}/lib/cycle-footer.sh"   # fallback: "${LINTEL_SOURCE_ROOT:-$(git rev-parse --show-toplevel)}/lib/cycle-footer.sh"
render_cycle_footer                               # auto: thin when no cycle, full/--compact when in one
```

See [ADR-0003](../../.claude/decisions/0003-cycle-position-footer.md).
