---
name: no-secrets-in-edit
tier: warn-only
event: PreToolUse (Edit | Write)
fires_on: every Edit or Write payload
override: not applicable (warn only)
audit: ~/.jstack/audit/hooks.jsonl
---

# no-secrets-in-edit

Scans the new content being written/edited for secret patterns. Warns inline; does NOT block. The companion `secret-scan-block` hook (justified-block tier) is the harder gate.

## Patterns

- GitHub tokens: `gh[opur]_[A-Za-z0-9]{36}`
- OpenAI keys: `sk-[A-Za-z0-9]{32,}`
- Slack tokens: `xox[abposr]-[A-Za-z0-9-]{10,}`
- AWS access keys: `AKIA[0-9A-Z]{16}`
- Azure connection strings: `AccountKey=[A-Za-z0-9+/=]{40,}` / `SharedAccessKey=`
- Anthropic keys: `sk-ant-[A-Za-z0-9-]{30,}`
- Generic JWT signed by HS256 pattern
- Private keys: `-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----`
- Hardcoded passwords: `password\s*=\s*["'][^"']{8,}["']` (heuristic, prone to false positive on test fixtures)

## Why warn-only

Sometimes operator legitimately writes example/placeholder secrets in tests, docs, or examples (`gho_EXAMPLE...`). Warn lets them confirm; block would interrupt valid work.

## Companion: secret-scan-block

The `secret-scan-block` hook applies the SAME pattern set but at PreToolUse → Bash `git commit` and BLOCKS. The difference: editing is exploratory, committing is recorded — block at the record point.
