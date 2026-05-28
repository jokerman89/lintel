---
name: resume
layer: foundation
description: Resume Lintel cycle from prior session — reads 00-state.md, picks up at next-recommended phase or operator-specified. Handles cross-session continuity.
color: cyan
tools: Read, Bash, Grep, Glob
voice: internal
cli_support: [claude-code, codex]
---

You are the RESUME skill — cross-session continuity for Lintel cycle.

## What this skill does

Reads `.lintel/state/00-state.md` from cwd, determines where the prior session ended, and routes operator to the next-recommended phase (or operator-specified override). Handles:
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

```bash
STATE_FILE=".lintel/state/00-state.md"
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
```

If still no state: surface "No prior state found. Run `/li:cycle` for new work or `/li:sense` for diagnostic."

### Step 1.5 — Integrity check (v3.6 cohort 1 item 6.3)

Before trusting 00-state.md, validate it. Defensive guard against state-drift / wrong-branch / stale state.

```bash
# Read recorded branch + commit + timestamp from 00-state.md (parse YAML-frontmatter or top entry)
state_branch=$(grep -m1 '^branch:' "$STATE_FILE" | awk '{print $2}')
state_commit=$(grep -m1 '^commit:' "$STATE_FILE" | awk '{print $2}')
state_ts=$(grep -m1 '^ts:' "$STATE_FILE" | awk '{print $2}')

# Current state
current_branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo unknown)
current_commit=$(git rev-parse HEAD 2>/dev/null || echo unknown)

issues=()

# Check 1: branch match (or warn if state is from other branch)
if [ -n "$state_branch" ] && [ "$state_branch" != "$current_branch" ]; then
  issues+=("branch-drift: state recorded on '$state_branch', currently on '$current_branch'")
fi

# Check 2: commit reachable (state's commit should be in current branch's history)
if [ -n "$state_commit" ] && [ "$state_commit" != "$current_commit" ]; then
  if ! git merge-base --is-ancestor "$state_commit" HEAD 2>/dev/null; then
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

Read `00-state.md`, find the LAST entry:
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
- plan.md exists and APPROVED ✓
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
- If yes: write 00-state.md entry "resume from cross-machine import, source: <machine-id or path>"

### Step 6 — Invoke chosen phase

Based on operator's choice (Step 3 + 4):
- If A (next recommended): `/li:<recommended-phase>`
- If B (restart prior): `/li:<last-phase>` (re-runs from start)
- If C (specific): `/li:<chosen-phase>`
- If D (full cycle): `/li:cycle` (from start, ignoring prior state)
- If E (abort): write `cycle_aborted: true` to 00-state.md, archive to `~/.lintel/archive/`

### Step 7 — 00-state.md append

```yaml
phase: RESUME (utility, not cycle phase)
ts: <timestamp>
prior_state_age: <duration>
prior_last_phase: <phase>
operator_choice: <A | B | C | D | E>
next_invoked: <phase>
cross_machine: <yes/no>
status: DONE
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
- `.lintel/state/00-state.md` (PRIMARY)
- `~/.lintel/lessons-vault/00-state-<repo>-*.md` (cross-machine fallback)
- `plan.md`, `spec.md`, `review-report.md` (for precondition checks)
- recent git log

**Writes:**
- `.lintel/state/00-state.md` (RESUME entry)
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
- **No state found**: NOT a failure — gracefully redirect to `/li:sense` or `/li:cycle`
- **Cross-machine state mismatch (different branch)**: surface diff, ask operator to switch branch or proceed with caveat
- **Precondition fails 3x**: stop trying to resume that phase, suggest alternative

## Voice tier behavior

`voice: internal`. Resume output is operator-coordination.
