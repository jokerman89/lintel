---
name: job-begin
tier: lifecycle
event: PreToolUse (Skill /li:<name> where SKILL.md has workflow_root: true)
fires_on: invocation of workflow_root skill
override: pass --no-job flag (operator-internal sub-call without spawning job)
audit: .claude/runtime/audit/jobs.jsonl
---

# job-begin

Spawns a Lintel job when the operator invokes a skill with `workflow_root: true` in its frontmatter.

Per v3.8 Feature 1: jobs are the single source of truth for curated flows in flight. JOB_BEGIN is the entry-side hook.

## What it does

1. Reads the invoked skill's frontmatter for `workflow_root: true`.
2. Sources `bin/_jobs.sh`.
3. Calls `job_create <workflow> <mode>` — creates `.claude/runtime/jobs/<job-id>/{job.yaml, outputs/, inputs/, 00-state.md}`.
4. Regenerates the repo-local `.claude/runtime/jobs/_active.md` + syncs the cross-repo registry `~/.lintel/jobs/_active.md` (one line per open job across all repos, pointing at the owning repo).
5. Audit-logs `{"kind":"job_begin", "job_id":..., "workflow":..., "mode":...}` to `.claude/runtime/audit/jobs.jsonl`.

## Why surface-only

Job creation must never block. If a workflow_root skill fires, a job IS created — the hook is fire-and-forget. Override path: `--no-job` flag (used by internal sub-calls so the operator doesn't see nested jobs).

## Override path

- `--no-job` on the skill invocation (skill body checks `${NO_JOB:-}`)
- `~/.lintel/.jobs-disabled` marker (rare — operator disables jobs entirely)

## What's NOT in scope

- Hook does not VERIFY the skill exists; that's the plugin dispatcher's job
- Hook does not GATE the skill from running; jobs is observability, not enforcement
- Hook does not write code; only state-file creation
