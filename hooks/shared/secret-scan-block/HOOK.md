---
name: secret-scan-block
tier: JUSTIFIED-BLOCK
event: PreToolUse (Bash) for git commit/push commands
fires_on: staged content contains Tier 1 secret pattern
override: operator must commit with explicit LINTEL_OVERRIDE_SECRET=1 env var + reason
audit: ~/.lintel/audit/hooks.jsonl
---

# secret-scan-block (JUSTIFIED-BLOCK)

The companion to `no-secrets-in-edit` (warn). This hook fires at COMMIT time and BLOCKS the commit if Tier 1 secret patterns are in the staged content.

## Why this is justified-block

Once a secret is committed, it leaks into git history. Even immediate force-push-removal leaves traces (reflog, cached objects, anyone who fetched in between). The cost of going through far exceeds the cost of stopping.

## Detection

Same Tier 1 pattern set as `no-secrets-in-edit`:
- GitHub / OpenAI / Slack / AWS / Azure / Anthropic tokens
- Private key headers
- Hardcoded passwords (heuristic)

Reads staged content via `git diff --cached`.

## Override

`LINTEL_OVERRIDE_SECRET=1 LINTEL_OVERRIDE_REASON="explanation" git commit ...`

Both env vars required. Reason logged to audit log. Use only when: known-false-positive (placeholder secret in docs/tests), explicit operator decision with reason.

## Audit

```jsonl
{"hook": "secret-scan-block", "tier": "BLOCK", "ts": "...", "patterns_matched": "...", "blocked": true}
{"hook": "secret-scan-block", "tier": "OVERRIDDEN", "ts": "...", "patterns_matched": "...", "reason": "...", "blocked": false}
```
