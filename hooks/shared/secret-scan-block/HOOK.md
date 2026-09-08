---
name: secret-scan-block
tier: JUSTIFIED-BLOCK
event: PreToolUse (Bash) for git commit/push commands
fires_on: staged content contains Tier 1 secret pattern
override: operator must commit with explicit LINTEL_OVERRIDE_SECRET=1 env var + reason
necessity: REQUIRED
gap_if_skipped: "Tokens/keys leak into history; credentials must be rotated; mirrors already have copies."
audit: .claude/runtime/audit/hooks.jsonl
---

# secret-scan-block (JUSTIFIED-BLOCK)

The companion to `no-secrets-in-edit` (warn). This hook blocks recognized commit/push tool calls when inspected added content contains Tier 1 secret patterns or collection fails.

## Why this is justified-block

Once a secret is committed, it leaks into git history. Even immediate force-push-removal leaves traces (reflog, cached objects, anyone who fetched in between). The cost of going through far exceeds the cost of stopping.

## Detection

Same Tier 1 pattern set as `no-secrets-in-edit`:
- GitHub / OpenAI / Slack / AWS / Azure / Anthropic tokens
- Private key headers
- Hardcoded passwords (heuristic)

Commit checks inspect staged and unstaged tracked additions. Push checks inspect the full
selected source history, including content later removed and merge-resolution additions.
Local tracking refs and replacement objects cannot hide original source content. Unsupported
command forms and Git read failures block explicitly. Binary content and commit/tag messages
remain outside this pattern scanner. See [control boundaries](../../../docs/compliance.md).

## Override

`LINTEL_OVERRIDE_SECRET=1 LINTEL_OVERRIDE_REASON="explanation" git commit ...`

Use an explicit operator decision with a reason for a known false positive. The flag permits
the override; the implementation records a supplied reason but does not mechanically require
it. Local audit writes are best effort, not immutable authorization evidence.

## Audit

```jsonl
{"hook": "secret-scan-block", "tier": "BLOCK", "ts": "...", "patterns_matched": "...", "blocked": true}
{"hook": "secret-scan-block", "tier": "OVERRIDDEN", "ts": "...", "patterns_matched": "...", "reason": "...", "blocked": false}
```
