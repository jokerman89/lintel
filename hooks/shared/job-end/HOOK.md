---
name: job-end
tier: lifecycle
event: PostToolUse (Skill status=DONE/ABORTED) OR explicit /li:jobs abort
fires_on: workflow_root skill reaching terminal status, OR operator abort
override: --no-cleanup flag (rare, debugging)
audit: ~/.lintel/audit/jobs.jsonl
---

# job-end

Closes a Lintel job: applies cleanup policy, promotes durable artifacts, moves to archive.

Per v3.8 Feature 1: terminating jobs cleanly via this hook removes the "abandoned plan-files lying around" failure mode.

## What it does

1. Reads `job.yaml` cleanup_policy.
2. **Keep:** promote durable artifacts to their permanent homes:
   - `adr/*` → `docs/adr/` (via existing `lessons-promote` skill pattern)
   - `lessons.md` → append to `tasks/lessons.md` (via existing `lessons-promote`)
   - `plan.md` + `spec.md` + `prompt.md` → `docs/plans/<slug>/` OR operator-configured path
3. **Discard:** delete `scratch/*` and other matching paths from policy.
4. Moves the job folder to `~/.lintel/jobs/_archive/<YYYY-MM-DD>/<job-id>/`.
5. Regenerates `~/.lintel/jobs/_active.md`.
6. Audit-logs `{"kind":"job_end", "job_id":..., "result": "DONE|ABORTED|FAILED"}`.

## Why surface-only

JOB_END is post-status. It cannot block the operator (the work is done). The hook's job is to enforce the cleanup contract so the next session-start doesn't surface a stale job.

## Override path

- `--no-cleanup` flag (debugging — keeps job folder in `jobs/` post-completion)
- Manual: operator can `mv` from `_archive/` back to `jobs/` to revive

## What's NOT in scope

- Hook does not commit/push changes to the repo
- Hook does not run tests
- Hook does not modify the operator's git state
