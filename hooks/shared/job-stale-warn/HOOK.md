---
name: job-stale-warn
tier: surface-only
event: SessionStart (first /li:cycle, /li:resume, /li:sense, OR /li:status of session)
fires_on: jobs untouched > N hours (default 24)
override: ~/.lintel/.jobs-stale-warn-disabled marker
audit: ~/.lintel/audit/jobs.jsonl
budget: <100ms for typical operator-vault of <20 jobs
---

# job-stale-warn

Surfaces forgotten jobs at session-start. Pattern follows `brand-staleness-warn` (90-day default) — read-only surfacing, never blocks.

Per v3.8 Feature 1: closes the "lost thread mid-flow" failure mode.

## What it does

1. Reads `~/.lintel/jobs/_active.md`.
2. For each active job, checks `last_touched` field vs current time.
3. Surfaces a 1-line warning per stale job: `⚠ Job <id> open, untouched <N>h. /li:jobs continue <id> · abort · branch`.
4. Audit-logs `{"kind":"job_stale_warn", "job_id":..., "age_hours":...}`.

## Why surface-only

Stale jobs are operator-state, not error-state. The operator may have intentionally paused a long-running flow. Hook surfaces, operator decides.

## Configurable threshold

Default 24 hours. Operator can configure via `~/.lintel/profile.yaml`:

```yaml
jobs_stale_threshold_hours: 72  # 3 days
```

Or via env: `LINTEL_JOBS_STALE_HOURS=72`.

## Override path

- `--no-stale-warn` flag on session-entry skills
- `~/.lintel/.jobs-stale-warn-disabled` marker (rare)

## What's NOT in scope

- Hook does not auto-archive stale jobs (operator decision)
- Hook does not fire mid-cycle (only at session-start)
- Hook does not modify any job state
