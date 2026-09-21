---
name: status
layer: foundation
description: Use to quickly check where you are in flight — shows what's open right now, an alias for listing jobs. The fast "what was I doing?" check at session start or any time you need orientation.
color: yellow
tools: Read, Bash
voice: internal
cli_support:
  - cli: claude-code
    level: full
  - cli: codex
    level: full
---

You are the `status` skill — quick read of in-flight Lintel jobs (v3.8 Feature 1).

## What this skill does

Reads actual records from the selected repository's job helper and cycle ledger.
The derived `_active.md` can be absent/stale; auto-spawn is dormant (ADR-0008).
No job records means **unobserved**, not "no ongoing work". Also show an explicitly
selected [work map](../spec-kit/references/work-map.md) with
`bin/li-work-artifacts.py --view context`. Preserve blocked/overdue/unknown items.
This is the everyday alias for `/li:jobs list`, not another task authority.

## When to use

- "Where am I right now?" — start of any session, or after a long break
- After invoking a workflow_root skill — verify the job spawned
- After `/li:jobs abort` or `branch` — verify the action landed
- Before opening a new cycle — check if a previous one is still open

## When NOT to use

- For task-level progress within a phase (read the phase's own audit log)
- For external system status (cloud-provider or vendor status pages)

## Inputs

No required args. Optional `--all` to include archived jobs in output.

## Workflow

```bash
export LINTEL_JOBS_NO_INIT=1
source "${LINTEL_SOURCE_ROOT:?select trusted source}/bin/_jobs.sh"
list_jobs --read-only || exit $?
stale_jobs 24 || exit $?
ARCHIVE="$LINTEL_JOBS_ARCHIVE"

if [ "${1:-}" = "--all" ] && [ -d "$ARCHIVE" ]; then
  echo ""
  echo "## Recorded archive (selected repository)"
  while IFS= read -r f; do
      id=$(_jobs_field "$f" job_id)
      status=$(_jobs_field "$f" status)
      archived_at=$(_jobs_field "$f" archived_at)
      echo "- $id ($status, $archived_at)"
  done < <(find "$ARCHIVE" -maxdepth 3 -name "job.yaml" -type f -print)
fi
```

## Voice tier behavior

`voice: internal`. Operator-only diagnostic.

## Status protocol

- **DONE** — output printed
- **NEEDS_CONTEXT** — `_active.md` malformed (rare; user should run `/li:jobs list` to regenerate)

## Hop-in support

YES — always solo-invocable. Most-used Lintel command in the wild.

## Integration

**Reads:**
- `.claude/runtime/jobs/_active.md` (repo-local)
- `~/.lintel/jobs/_active.md` (cross-repo registry — one line per open job across all repos)
- `.claude/runtime/jobs/_archive/` (with `--all`)

**Writes:**
- nothing

**Calls into:**
- `bin/_jobs.sh` read-only view and stale/unknown-age observations
- Shared selected-map/cycle readers; global registry only when explicitly selected

## Anti-patterns

- Do not use a missing/stale `_active.md` as proof that there is no open work
- Don't poll in a loop — the file changes only when `bin/_jobs.sh` runs, not periodically

## See also

- `/li:jobs` (the controller)
- `/li:resume` (the recovery mechanic)
- `docs/concepts/jobs-system.md`

## Cycle-position footer

Close your report with the shared position footer. Outside an active cycle it renders the thin
ambient line; inside one it shows the operator's position + next step:

```bash
source "${LINTEL_SOURCE_ROOT:?select trusted source}/lib/cycle-footer.sh"
render_cycle_footer                               # auto: thin when no cycle, full/--compact when in one
```

See [ADR-0003](../../.claude/decisions/0003-cycle-position-footer.md).
