#!/usr/bin/env bash
# bin/_jobs.sh — sourced helper for jobs system (v3.8 Feature 1)
#
# Lifecycle:
#   job_create <workflow> <mode>     → creates ~/.lintel/jobs/<id>/{job.yaml,outputs,inputs} + regenerates _active.md
#   job_update <id> <step> <status>  → updates job.yaml current_step + step status + last_touched
#   job_archive <id> <result>        → moves to _archive/<date>/<id>/ + applies cleanup
#   regenerate_active                → rebuilds _active.md from all jobs/<id>/job.yaml
#   list_jobs                        → reads _active.md (or rebuilds if missing)
#   job_path <id>                    → echoes absolute job-dir path
#   stale_jobs <hours>               → lists jobs untouched > N hours
#
# Source-once-and-call pattern (matches bin/_aliases.sh):
#   source "$(dirname "$0")/_jobs.sh"
#   job_create cycle internal-tool
#
# Scope (v5, ADR-0005): in a repo carrying the v5 layout marker, job data lives
# in <repo>/.claude/runtime/jobs/ and ~/.lintel/jobs/_active.md becomes a thin
# cross-repo REGISTRY (one line per job, pointing at the owning repo) so
# /li:resume and /li:status keep their "what's open anywhere" view. Un-migrated
# repos keep the historical global layout unchanged.

LINTEL_HOME="${LINTEL_HOME:-$HOME/.lintel}"

# v5 scope resolution — explicit LINTEL_JOBS_DIR env always wins (tests).
_JOBS_REPO_ROOT="${LINTEL_REPO_ROOT:-$(git rev-parse --show-toplevel 2>/dev/null)}"
_JOBS_SCOPE="global"
if [ -z "${LINTEL_JOBS_DIR:-}" ] && [ -n "$_JOBS_REPO_ROOT" ] \
   && [ -f "$_JOBS_REPO_ROOT/.claude/lintel-layout.yaml" ]; then
  _jobs_layout_v=$(grep -E '^layout_version:' "$_JOBS_REPO_ROOT/.claude/lintel-layout.yaml" 2>/dev/null \
                   | head -1 | awk '{print $2}' | tr -d '\r')
  if [ "${_jobs_layout_v:-0}" -ge 5 ] 2>/dev/null; then
    LINTEL_JOBS_DIR="$_JOBS_REPO_ROOT/.claude/runtime/jobs"
    _JOBS_SCOPE="repo"
  fi
fi

LINTEL_JOBS_DIR="${LINTEL_JOBS_DIR:-$LINTEL_HOME/jobs}"
LINTEL_JOBS_ACTIVE="${LINTEL_JOBS_ACTIVE:-$LINTEL_JOBS_DIR/_active.md}"
LINTEL_JOBS_ARCHIVE="${LINTEL_JOBS_ARCHIVE:-$LINTEL_JOBS_DIR/_archive}"
LINTEL_JOBS_REGISTRY="${LINTEL_JOBS_REGISTRY:-$LINTEL_HOME/jobs/_active.md}"
LINTEL_AUDIT_DIR="${LINTEL_AUDIT_DIR:-$LINTEL_HOME/audit}"

# Unified audit writer (sibling in bin/). Idempotent source.
command -v audit_log >/dev/null 2>&1 || source "$(dirname "${BASH_SOURCE[0]}")/_audit.sh"

# LINTEL_JOBS_NO_INIT=1 -> read-only source (the session digest sources this
# just to call job_ready; a digest must not create directories as a side effect)
if [ -z "${LINTEL_JOBS_NO_INIT:-}" ]; then
  mkdir -p "$LINTEL_JOBS_DIR" "$LINTEL_JOBS_ARCHIVE" "$LINTEL_AUDIT_DIR" 2>/dev/null || true
fi

_jobs_iso_now() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }
_jobs_epoch_now() { date +%s; }

# Generate a job-id: <workflow>-<YYYYMMDD-HHMM>-<short-hash>
job_id() {
  local workflow="$1"
  local stamp
  stamp=$(date +"%Y%m%d-%H%M")
  local hash
  hash=$(printf '%s' "$RANDOM-$$-$(_jobs_epoch_now)" | shasum 2>/dev/null | cut -c1-6 || \
         printf '%06x' $((RANDOM * RANDOM)) | cut -c1-6)
  printf '%s-%s-%s' "$workflow" "$stamp" "$hash"
}

# Create a new job folder + job.yaml + regenerate _active.md
# Args: <workflow> <mode> [<step-spec> ...]
#
# Each optional <step-spec> is a pipe-delimited per-step contract (same grammar
# as job_set_steps below). When none are given, job.yaml is written with an
# empty `steps: []` block (back-compat — the historical behaviour) and the
# caller can populate it later via job_set_steps.
job_create() {
  local workflow="${1:-cycle}"
  local mode="${2:-internal-tool}"
  shift 2 2>/dev/null || true
  local id
  id=$(job_id "$workflow")
  local dir="$LINTEL_JOBS_DIR/$id"
  mkdir -p "$dir/outputs" "$dir/inputs" 2>/dev/null || true

  local ts
  ts=$(_jobs_iso_now)
  cat > "$dir/job.yaml" <<EOF
workflow: $workflow
job_id: $id
called_by: ${CALLED_BY:-operator}
mode: $mode
started_at: $ts
last_touched: $ts
current_step: SENSE
status: ACTIVE
cleanup_policy:
  keep: [adr, lessons, plan.md, spec.md, prompt.md]
  discard: [scratch/*]
steps: []
EOF

  # Touch a placeholder 00-state.md inside the job
  : > "$dir/00-state.md"

  # Audit (unified writer → ~/.lintel/audit/jobs.jsonl)
  audit_log "jobs" "job_begin" "job_id=$id" "workflow=$workflow" "mode=$mode"

  # Optional inline step contracts (design §3.4 — per-step consumes/produces).
  if [ "$#" -gt 0 ]; then
    job_set_steps "$id" "$@"
  fi

  regenerate_active

  printf '%s\n' "$id"
}

# ── Per-step contracts (design §3.4 / docs/concepts/jobs-system.md "Mechanics") ──
#
# A <step-spec> is a single pipe-delimited record describing one WBS leaf/phase:
#
#   NAME|consumes=a.md,b.md|produces=c.md,d.md|status=PENDING|blocked_until=PLAN.status == DONE
#
#   - field 1 (positional) is the step NAME. For flat/phased plans this is a
#     phase token (PLAN, BUILD); for tree plans it is a WBS node-path (1.1.a).
#   - consumes / produces are comma-separated artifact lists (rendered as YAML
#     inline sequences). Omit → [].
#   - status defaults to PENDING.
#   - blocked_until is a predicate over OTHER steps' status (grammar below).
#
# Field order after NAME is free; unknown keys are ignored.
#
# blocked_until predicate grammar (kept deliberately small — see job_can_start):
#   <predicate> := <clause> ( "&&" <clause> )*
#   <clause>    := <STEP>.status == DONE
# i.e. a conjunction of "this named step has reached DONE" tests. Empty/absent
# means "never blocked". No OR, no negation, no other status values — by design.

# Render one step-spec to indented YAML on stdout.
_jobs_render_step() {
  local spec="$1"
  local name consumes produces status blocked field key val
  name=""; consumes=""; produces=""; status="PENDING"; blocked=""

  # First pipe-field is the name; the rest are key=value.
  name="${spec%%|*}"
  local rest="${spec#"$name"}"
  rest="${rest#|}"

  # Split remaining fields on '|'
  local IFS_SAVE="$IFS"
  IFS='|'
  # shellcheck disable=SC2206
  local fields=($rest)
  IFS="$IFS_SAVE"
  for field in "${fields[@]}"; do
    [ -n "$field" ] || continue
    key="${field%%=*}"
    val="${field#*=}"
    case "$key" in
      consumes) consumes="$val" ;;
      produces) produces="$val" ;;
      status)   status="$val" ;;
      blocked_until) blocked="$val" ;;
    esac
  done

  # Comma-list → YAML inline sequence "[a, b]"
  _jobs_yaml_seq() {
    local csv="$1"
    [ -n "$csv" ] || { printf '[]'; return; }
    local out="" item
    local IFS=','
    # shellcheck disable=SC2206
    local items=($csv)
    for item in "${items[@]}"; do
      item="${item# }"; item="${item%% }"
      [ -n "$item" ] || continue
      [ -n "$out" ] && out="$out, $item" || out="$item"
    done
    printf '[%s]' "$out"
  }

  printf '  - name: %s\n' "$name"
  printf '    consumes: %s\n' "$(_jobs_yaml_seq "$consumes")"
  printf '    produces: %s\n' "$(_jobs_yaml_seq "$produces")"
  printf '    status: %s\n' "$status"
  if [ -n "$blocked" ]; then
    printf '    blocked_until: %s\n' "$blocked"
  fi
}

# Write the steps[] block of a job from one-or-more step-specs.
# Args: <id> <step-spec> [<step-spec> ...]
# Replaces any existing steps[] block (everything from the `steps:` line to EOF).
job_set_steps() {
  local id="$1"; shift || true
  local dir="$LINTEL_JOBS_DIR/$id"
  [ -f "$dir/job.yaml" ] || return 1

  local body
  body=$(
    for spec in "$@"; do
      [ -n "$spec" ] || continue
      _jobs_render_step "$spec"
    done
  )

  # Reprint job.yaml up to (not including) the `steps:` line, then re-emit steps.
  # The steps block is always the trailing block (job_create writes it last),
  # so dropping from `^steps:` to EOF and re-appending is safe and idempotent.
  awk '
    /^steps:/ { found=1 }
    !found { print }
  ' "$dir/job.yaml" > "$dir/job.yaml.tmp"

  if [ -z "$body" ]; then
    printf 'steps: []\n' >> "$dir/job.yaml.tmp"
  else
    printf 'steps:\n' >> "$dir/job.yaml.tmp"
    printf '%s\n' "$body" >> "$dir/job.yaml.tmp"
  fi

  mv "$dir/job.yaml.tmp" "$dir/job.yaml"

  audit_log "jobs" "job_set_steps" "job_id=$id" "count=$#"
}

# Read one named step's status. Echoes the status (e.g. DONE) or empty if absent.
# Args: <id> <step-name>
job_step_status() {
  local id="$1"
  local step="$2"
  local dir="$LINTEL_JOBS_DIR/$id"
  [ -f "$dir/job.yaml" ] || return 1

  awk -v want="$step" '
    /^  - name:/ { cur=$3; next }
    /^    status:/ && cur==want { print $2; exit }
  ' "$dir/job.yaml"
}

# Update a job step + status (touches last_touched too)
# Args: <id> <step> <status>
job_update() {
  local id="$1"
  local step="$2"
  local status="${3:-IN_PROGRESS}"
  local dir="$LINTEL_JOBS_DIR/$id"
  [ -f "$dir/job.yaml" ] || return 1

  local ts
  ts=$(_jobs_iso_now)

  # Does <step> name an actual entry in steps[]? If so, <status> is a STEP-level
  # transition and the job's top-level `status:` must NOT be flipped (the job
  # stays ACTIVE until job_archive sets a terminal status). If <step> is not a
  # populated step (the legacy flat/un-stepped case), preserve the historical
  # behaviour: <status> writes to top-level `status:`. This keeps the existing
  # `job_update <id> PLAN IN_PROGRESS` contract intact while making per-step
  # updates safe.
  local step_exists=0
  if [ -n "$(job_step_status "$id" "$step")" ]; then
    step_exists=1
  fi

  # In-place update of last_touched + current_step + the named step's nested
  # status inside steps[] (portable awk).
  #
  # Top-level keys are anchored at column 0 (^last_touched:/^current_step:/^status:);
  # the nested step status is indented ("    status:") so it never collides with
  # the ^status: matcher. `cur` tracks which step block we are inside so the
  # right nested status line is rewritten. The top-level `status:` is only
  # rewritten when the step is NOT a populated steps[] entry (see above).
  awk -v ts="$ts" -v step="$step" -v status="$status" -v step_exists="$step_exists" '
    BEGIN { updated_lt=0; updated_cs=0; updated_st=0; cur="" }
    /^last_touched:/ && !updated_lt { print "last_touched: " ts; updated_lt=1; next }
    /^current_step:/ && !updated_cs { print "current_step: " step; updated_cs=1; next }
    /^status:/ && !updated_st && step_exists=="0" { print "status: " status; updated_st=1; next }
    /^  - name:/ { cur=$3; print; next }
    /^    status:/ && cur==step { print "    status: " status; next }
    { print }
  ' "$dir/job.yaml" > "$dir/job.yaml.tmp" && mv "$dir/job.yaml.tmp" "$dir/job.yaml"

  audit_log "jobs" "job_update" "job_id=$id" "step=$step" "status=$status"

  regenerate_active
}

# Archive a job + apply cleanup
# Args: <id> <result>  result in: DONE / ABORTED / FAILED
job_archive() {
  local id="$1"
  local result="${2:-DONE}"
  local dir="$LINTEL_JOBS_DIR/$id"
  [ -d "$dir" ] || return 1

  local date_stamp
  date_stamp=$(date +"%Y-%m-%d")
  local archive_dir="$LINTEL_JOBS_ARCHIVE/$date_stamp"
  mkdir -p "$archive_dir" 2>/dev/null || true

  # Apply cleanup-policy: discard scratch/*
  if [ -d "$dir/scratch" ]; then
    rm -rf "$dir/scratch" 2>/dev/null || true
  fi

  # Mark final status + ts in job.yaml
  local ts
  ts=$(_jobs_iso_now)
  awk -v ts="$ts" -v result="$result" '
    BEGIN { updated_lt=0; updated_st=0; appended_arc=0 }
    /^last_touched:/ && !updated_lt { print "last_touched: " ts; updated_lt=1; next }
    /^status:/ && !updated_st { print "status: " result; updated_st=1; next }
    { print }
    END { print "archived_at: " ts }
  ' "$dir/job.yaml" > "$dir/job.yaml.tmp" && mv "$dir/job.yaml.tmp" "$dir/job.yaml"

  # Move to archive (mv across paths)
  mv "$dir" "$archive_dir/" 2>/dev/null || true

  audit_log "jobs" "job_end" "job_id=$id" "result=$result"

  regenerate_active
}

# Regenerate the active-jobs view.
# Repo scope: detailed repo-local _active.md + registry line sync.
# Global scope: the global _active.md IS the registry — write registry format
# there too, preserving migrated repos' lines (mixed-scope grace window must
# not clobber either side's entries).
regenerate_active() {
  if [ "$_JOBS_SCOPE" = "repo" ]; then
    local out="$LINTEL_JOBS_ACTIVE"
    {
      printf '# Active Lintel jobs (this repo)\n'
      printf '\n'
      printf '> Generated by bin/_jobs.sh at %s. Do not edit by hand.\n' "$(_jobs_iso_now)"
      printf '\n'

      local count=0
      for d in "$LINTEL_JOBS_DIR"/*/; do
        [ -d "$d" ] || continue
        local f="$d/job.yaml"
        [ -f "$f" ] || continue
        local id workflow mode current_step status started last_touched
        id=$(grep '^job_id:' "$f" | head -1 | awk '{print $2}')
        workflow=$(grep '^workflow:' "$f" | head -1 | awk '{print $2}')
        mode=$(grep '^mode:' "$f" | head -1 | awk '{print $2}')
        current_step=$(grep '^current_step:' "$f" | head -1 | awk '{print $2}')
        status=$(grep '^status:' "$f" | head -1 | awk '{print $2}')
        started=$(grep '^started_at:' "$f" | head -1 | awk '{print $2}')
        last_touched=$(grep '^last_touched:' "$f" | head -1 | awk '{print $2}')

        printf '## %s\n' "$id"
        printf -- '- workflow: `%s`\n' "$workflow"
        printf -- '- mode: `%s`\n' "$mode"
        printf -- '- current_step: `%s`\n' "$current_step"
        printf -- '- status: `%s`\n' "$status"
        printf -- '- started: %s\n' "$started"
        printf -- '- last_touched: %s\n' "$last_touched"
        printf '\n'
        count=$((count + 1))
      done

      if [ "$count" -eq 0 ]; then
        printf '_No active jobs._\n'
      fi
    } > "$out"
    _registry_sync "$_JOBS_REPO_ROOT"
  else
    # Global/legacy scope: write OUR jobs as registry lines into the shared
    # file, keeping every line owned by other scopes (migrated repos).
    LINTEL_JOBS_REGISTRY="$LINTEL_JOBS_ACTIVE" _registry_sync "global"
  fi
}

# ── cross-repo registry (v5) ─────────────────────────────────────────────────
# ~/.lintel/jobs/_active.md holds one line per open job across ALL scopes.
# Each line carries an HTML-comment marker with the owning scope (a repo root,
# or "global" for legacy ~/.lintel/jobs data); syncing = drop this scope's
# lines, re-append the current ones, preserve everyone else's.
# Args: <scope-tag> (repo root path, or "global")
_registry_sync() {
  local scope_tag="${1:-$_JOBS_REPO_ROOT}"
  local reg="$LINTEL_JOBS_REGISTRY"
  mkdir -p "$(dirname "$reg")" 2>/dev/null || true

  local marker="<!-- repo:$scope_tag -->"
  local tmp="$reg.tmp.$$"
  {
    if [ -f "$reg" ] && grep -q '^# Lintel jobs registry' "$reg" 2>/dev/null; then
      grep -vF "$marker" "$reg" | grep -v '^_No open jobs' || true
    else
      # Fresh registry (or first write over a legacy-format file — legacy
      # entries reappear on that scope's next regenerate_active).
      printf '# Lintel jobs registry (cross-repo)\n\n'
      printf '> One line per open job; data lives in each repo'"'"'s .claude/runtime/jobs/.\n'
      printf '> Generated by bin/_jobs.sh. Do not edit by hand.\n\n'
    fi
    local d f id workflow status current_step
    for d in "$LINTEL_JOBS_DIR"/*/; do
      [ -d "$d" ] || continue
      f="$d/job.yaml"
      [ -f "$f" ] || continue
      id=$(grep '^job_id:' "$f" | head -1 | awk '{print $2}')
      workflow=$(grep '^workflow:' "$f" | head -1 | awk '{print $2}')
      status=$(grep '^status:' "$f" | head -1 | awk '{print $2}')
      current_step=$(grep '^current_step:' "$f" | head -1 | awk '{print $2}')
      printf -- '- `%s` · %s · %s · step:%s · %s %s\n' \
        "$id" "$workflow" "$status" "$current_step" "$scope_tag" "$marker"
    done
  } > "$tmp"

  # No job lines at all? Keep an explicit empty marker line for readers.
  if ! grep -qE '^- ' "$tmp" 2>/dev/null; then
    printf '_No open jobs anywhere._\n' >> "$tmp"
  fi
  mv "$tmp" "$reg" || echo "[lintel/_jobs] WARN: registry sync failed for $reg" >&2
}

# Print all jobs
list_jobs() {
  [ -f "$LINTEL_JOBS_ACTIVE" ] || regenerate_active
  cat "$LINTEL_JOBS_ACTIVE"
}

# Find jobs untouched > N hours
# Args: <hours> (default 24)
stale_jobs() {
  local hours="${1:-24}"
  local now_epoch
  now_epoch=$(_jobs_epoch_now)
  local threshold=$((hours * 3600))

  for d in "$LINTEL_JOBS_DIR"/*/; do
    [ -d "$d" ] || continue
    local f="$d/job.yaml"
    [ -f "$f" ] || continue
    local id last_touched
    id=$(grep '^job_id:' "$f" | head -1 | awk '{print $2}')
    last_touched=$(grep '^last_touched:' "$f" | head -1 | awk '{print $2}')
    [ -z "$last_touched" ] && continue

    # Convert ISO-8601 to epoch (portable-ish via date -d / -j)
    local lt_epoch
    lt_epoch=$(date -d "$last_touched" +%s 2>/dev/null || \
               date -j -f "%Y-%m-%dT%H:%M:%SZ" "$last_touched" +%s 2>/dev/null || \
               echo "$now_epoch")
    local age=$((now_epoch - lt_epoch))
    if [ "$age" -gt "$threshold" ]; then
      local age_hours=$((age / 3600))
      printf '%s\t%dh\n' "$id" "$age_hours"
    fi
  done
}

# Resolve job_id to abs path
job_path() {
  local id="$1"
  printf '%s' "$LINTEL_JOBS_DIR/$id"
}

# ── blocked_until enforcement (design §3.4) ──────────────────────────────────
#
# job_can_start <id> <step> → echoes "yes" or "no" (and returns 0/1 respectively).
#
# Reads the named step's blocked_until predicate and evaluates it against the
# CURRENT status of the referenced steps. Grammar (see job_set_steps header):
#
#   <predicate> := <clause> ( "&&" <clause> )*
#   <clause>    := <STEP>.status == DONE
#
# A step with no blocked_until (or an empty one) is always startable. Every
# clause must hold (logical AND) for the step to start. A clause referencing a
# step whose status is anything other than DONE (including a missing/unknown
# step) evaluates false → blocked. Anything outside the grammar is treated
# conservatively as unsatisfiable (blocked) so a malformed predicate never
# silently unblocks a gate.
job_can_start() {
  local id="$1"
  local step="$2"
  local dir="$LINTEL_JOBS_DIR/$id"
  [ -f "$dir/job.yaml" ] || { printf 'no\n'; return 1; }

  # Extract the blocked_until line for the named step.
  local pred
  pred=$(awk -v want="$step" '
    /^  - name:/ { cur=$3; next }
    /^    blocked_until:/ && cur==want {
      sub(/^    blocked_until:[ \t]*/, "")
      print
      exit
    }
  ' "$dir/job.yaml")

  # No predicate → not blocked.
  if [ -z "$pred" ]; then
    printf 'yes\n'; return 0
  fi

  # Split on '&&' and require every clause to hold.
  local clause dep got
  local IFS_SAVE="$IFS"
  IFS='&'
  # shellcheck disable=SC2206
  local raw=($pred)
  IFS="$IFS_SAVE"
  for clause in "${raw[@]}"; do
    # Empty fragments arise from splitting on the doubled '&&'; skip them.
    clause="${clause#"${clause%%[![:space:]]*}"}"   # ltrim
    clause="${clause%"${clause##*[![:space:]]}"}"    # rtrim
    [ -n "$clause" ] || continue

    # Clause must be exactly: <STEP>.status == DONE
    case "$clause" in
      *.status\ ==\ DONE)
        dep="${clause%%.status*}"
        got=$(job_step_status "$id" "$dep")
        if [ "$got" != "DONE" ]; then
          printf 'no\n'; return 1
        fi
        ;;
      *)
        # Outside the supported grammar → conservatively blocked.
        printf 'no\n'; return 1
        ;;
    esac
  done

  printf 'yes\n'; return 0
}

# ── Node-path resume (design §3.4 — tree-schema plans) ───────────────────────
#
# job_resume_point <id> → echoes the deepest incomplete WBS node-path.
#
# Steps are authored in WBS order (1, 1.1, 1.1.a, 1.2, 2, …), so the FIRST step
# whose status is not DONE is the resume point. For a tree plan the step `name`
# IS the node-path (1.1.a) and that node-path is returned; for flat/phased plans
# the name is a phase token (BUILD) and that is returned instead — the resume
# skill falls back to current_step in that case (see skills/resume/SKILL.md).
#
# A blocked step (its blocked_until predicate does not yet hold) is skipped — it
# is not yet resumable — so the resume point is the first step that is both
# incomplete AND startable. If every step is DONE, echoes empty (job complete).
# If no steps[] are populated at all, echoes empty (caller falls back to
# current_step).
job_resume_point() {
  local id="$1"
  local dir="$LINTEL_JOBS_DIR/$id"
  [ -f "$dir/job.yaml" ] || return 1

  # Collect (name, status) pairs in document order.
  local names statuses
  names=$(awk '/^  - name:/ { print $3 }' "$dir/job.yaml")
  [ -n "$names" ] || return 0   # no steps → empty (fall back to current_step)

  local name st can
  while IFS= read -r name; do
    [ -n "$name" ] || continue
    st=$(job_step_status "$id" "$name")
    if [ "$st" != "DONE" ]; then
      can=$(job_can_start "$id" "$name")
      if [ "$can" = "yes" ]; then
        printf '%s\n' "$name"
        return 0
      fi
    fi
  done <<< "$names"

  # All steps DONE (or all remaining ones blocked) → empty resume point.
  return 0
}

# Is a job READY to continue? (bd-prime steal, ADR-0006)
# Ready = top-level ACTIVE and either no steps[] populated, or the first
# incomplete step is startable (its blocked_until predicate holds).
# Echoes "yes"/"no"; rc 0/1.
job_ready() {
  local id="$1"
  local dir="$LINTEL_JOBS_DIR/$id"
  [ -f "$dir/job.yaml" ] || { printf 'no
'; return 1; }
  local status
  status=$(grep '^status:' "$dir/job.yaml" | head -1 | awk '{print $2}' | tr -d '
')
  [ "$status" = "ACTIVE" ] || { printf 'no
'; return 1; }
  local names
  names=$(awk '/^  - name:/ { print $3 }' "$dir/job.yaml")
  if [ -z "$names" ]; then printf 'yes
'; return 0; fi
  local rp
  rp=$(job_resume_point "$id")
  if [ -n "$rp" ]; then printf 'yes
'; return 0; fi
  # steps exist, none startable: either done or fully blocked → not ready
  printf 'no
'; return 1
}

# Self-test mode
if [ "${BASH_SOURCE[0]}" = "$0" ]; then
  echo "_jobs.sh self-test:"
  echo "  LINTEL_JOBS_DIR = $LINTEL_JOBS_DIR"
  echo "  Active jobs:"
  list_jobs | sed 's/^/    /'
fi
