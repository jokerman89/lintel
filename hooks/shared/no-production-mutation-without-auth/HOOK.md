---
name: no-production-mutation-without-auth
tier: warn-only
event: PreToolUse (Bash)
fires_on: command appears to mutate production resources
override: explicit per-call auth confirmation in conversation
necessity: REQUIRED
gap_if_skipped: "Production data modified without per-call operator confirmation; no audit trail."
audit: ~/.lintel/audit/hooks.jsonl
---

# no-production-mutation-without-auth

Detects Bash commands that mutate production resources and reminds operator about Layer 2 per-call auth requirement.

## Patterns (heuristic — operator can extend via `~/.lintel/production-mutation-patterns.txt`)

- `az ... --subscription <prod-name>` patterns
- `kubectl ... -n production`
- `terraform apply` (when in known prod workspace)
- `gh workflow run deploy.yml` with prod target
- `psql` / `pg_dump` against prod hostname
- `aws ... --region <prod>` with mutating verbs

## Why warn-only

Production mutations are sometimes legitimately needed (incident response). Block would interrupt urgent recovery. Warn + audit surfaces the action.

## Override

In conversation, operator says "yes, this is the prod mutation I authorize for this batch". Hook fires either way; auto-confirm replies the warning in audit.
