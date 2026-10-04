# Selected state and job recovery

These conditional procedures belong to [Resume](../SKILL.md). Read the selected
section after its producing step supplies the validated inputs. A reference read
does not select another initiative, authorize execution or transfer a profile.

## Swarm-aware committed resume

**Inputs from Step 1c:** the selected `selected_map` and its `coordination` path,
the working `LINTEL_REPO_ROOT`, and the trusted `LINTEL_SOURCE_ROOT` or supported
`CLAUDE_PLUGIN_ROOT`. Retain the selected work/profile authority. Missing or
unreconciled inputs return to the main selection procedure; never guess another map.

If the selected map declares `execution_mode: "swarm"` and `coordination`, use the same committed
artifacts rather than reconstructing lane state from chat or the local ledger:

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
[ -f "$source_root/bin/li-work-artifacts.py" ] && [ -f "$source_root/bin/li-swarm.py" ] || {
  echo "NEEDS_CONTEXT: Lintel resume helpers missing under trusted source root" >&2
  exit 1
}
python3 "$source_root/bin/li-work-artifacts.py" --repo "$repo" --map "$selected_map"
python3 "$source_root/bin/li-swarm.py" status --repo "$repo" --coord "$coordination"
python3 "$source_root/bin/li-swarm.py" wave --repo "$repo" --coord "$coordination"
```

Claude may provide `CLAUDE_PLUGIN_ROOT`; other adapters substitute/export their installed bundle as
`LINTEL_SOURCE_ROOT`. Tests and self-checks set it explicitly. The working repo is only `--repo` and
never a trusted helper source.

Surface the lane states, earliest incomplete wave, ready task IDs, and actual host execution tier.
`awaiting_review` resumes at the lane's independent review, while `rework_required` returns to the
same card. A complete frontier routes to the integrated REVIEW close gate.

Runtime loss cancels attempts, not committed work. Treat an unreported worker process as unfinished.
If an isolated worktree or patch survives, preserve it, derive its exact changed paths, run
`check-scope`, and finish the declared report/review. If the change cannot be attributed to one lane,
surface the discrepancy and sequence a clean retry; never infer completion or silently discard it.
Do not select another initiative by modification time.

## Ledger integrity

**Inputs from Step 1:** `STATE_FILE` and `resume_working_repo`, plus the selected
`LINTEL_CYCLE_ID` when supplied. Run the actual Step 1 setup and this recipe in
the same Bash invocation; separate tool calls do not retain shell variables.
Only inspect the selected ledger. Missing or unreconciled inputs return to
selection instead of choosing another ledger.

Before trusting 00-state.md, validate it. Defensive guard against state-drift / wrong-branch / stale state.

```bash
# Read recorded branch + commit + timestamp from the CURRENT cycle's segment.
# The ledger is append-only across many cycles: a first-match (-m1) grep read
# the OLDEST cycle, so resume false-warned "stale" on any week-old file.
# state_cycle_segment (lib/state.sh) scopes to the last CYCLE block; the
# last match inside it is the current truth. The CYCLE entry records
# branch/commit since v5.3 (skills/cycle Step 4) — empty on older ledgers,
# and an empty value skips that check rather than warning.
seg="$(state_cycle_segment "$STATE_FILE" "${LINTEL_CYCLE_ID:-}")" || exit $?
state_branch=$(printf '%s\n' "$seg" | grep '^branch:' | tail -1 | awk '{print $2}')
state_commit=$(printf '%s\n' "$seg" | grep '^commit:' | tail -1 | awk '{print $2}')
state_ts=$(printf '%s\n' "$seg" | grep '^ts:' | tail -1 | awk '{print $2}')

# Current state
current_branch=$(git -C "$resume_working_repo" rev-parse --abbrev-ref HEAD 2>/dev/null || echo unknown)
current_commit=$(git -C "$resume_working_repo" rev-parse HEAD 2>/dev/null || echo unknown)

issues=()
age_warning=""

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
  if state_epoch=$(date -d "$state_ts" +%s 2>/dev/null ||
      date -j -u -f "%Y-%m-%dT%H:%M:%SZ" "$state_ts" +%s 2>/dev/null); then
    state_age_days=$(( ($(date +%s) - state_epoch) / 86400 ))
    [ "$state_age_days" -le 7 ] || age_warning="old observation: $state_age_days days; reconcile current evidence"
  else
    age_warning="timestamp unparsed: age unknown; retain this work in the report"
  fi
fi

# Surface to operator
if [ -n "$age_warning" ]; then
  printf 'Resume observation warning: %s\n' "$age_warning"
fi
if [ ${#issues[@]} -gt 0 ]; then
  echo "⚠ Resume integrity warnings:"
  printf '  - %s\n' "${issues[@]}"
  echo ""
  echo "Reconcile these mismatches against the selected work before continuation."
  # Ask only for an unresolved recovery/selection decision; confirmation is not policy evidence.
fi
```

Proceed to Step 2 only when integrity is established or the specific discrepancy
has been reconciled within authority, with evidence retained. An unresolved
mismatch blocks the dependent continuation. If the operator aborts, exit BLOCKED
and offer `/li:sense` for a diagnostic.
An age-only warning does not require re-approval or change the selected work.
Continue the existing content/profile preconditions; a real selection or integrity
mismatch still needs reconciliation through the host's actual question channel.

## Tree and job resume

**Inputs from the selected job:** validated `JOB_ID`, trusted `LINTEL_SOURCE_ROOT`,
the working `LINTEL_REPO_ROOT`, and optional explicitly selected `LINTEL_SCOPE_PATH`.
Step 1c and the main input classifier retain the original work/job and any
`--from` override. Keep that selection and the main Step 3/4 preconditions;
this procedure is not permission to select another job or skip dependencies.

A flat/phased plan resumes to a **phase** (`current_step`). A `tree`-schema
plan (L/XL, from the scale-parametric WBS) resumes to a **WBS node-path**
(`1.1.a`) — the deepest incomplete leaf — so a half-done big plan picks up at
the exact subtask, not the top of a phase.

When resuming a job (`/li:resume --job <id>`, the path `/li:jobs continue`
delegates to), ask `bin/_jobs.sh` for the resume point. It returns the first
incomplete-and-startable step `name`; for a tree job that name *is* the
node-path:

```bash
resume_source="${LINTEL_SOURCE_ROOT:?select trusted source}"
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

An existing `--from <step>` override chooses that exact step in the already selected
job rather than the computed recommendation. Check it through the existing
`job_can_start` and mapped-work prerequisites; do not invent a step, skip a blocked
dependency or discard prior evidence. A phase override keeps Step 4's requirements.
