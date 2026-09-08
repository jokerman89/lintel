---
name: customer-data-block
tier: JUSTIFIED-BLOCK
event: PreToolUse (Bash) for git commit/push
fires_on: staged content contains Tier 1 customer-data pattern
override: LINTEL_OVERRIDE_CUSTOMER_DATA=1 + LINTEL_OVERRIDE_REASON env vars
necessity: REQUIRED
gap_if_skipped: "Tier-1 customer-data patterns leak into git history; compliance incident requiring repo remediation."
audit: .claude/runtime/audit/hooks.jsonl
---

# customer-data-block (JUSTIFIED-BLOCK)

Companion to `no-customer-data-in-message` (warn). Blocks recognized commit/push tool calls
when inspected additions contain Tier 1 customer-data patterns or inspection fails.

## Why justified-block

Customer data in repo history = compliance incident. Even immediate-revert leaves artifacts in reflog and any fetched mirror. Per Premise: "No customer data in this repo, ever."

## Detection

Same Tier 1 customer-data patterns:
- Email addresses (regex)
- Phone numbers (intl + Swedish)
- Swedish personnummer (YYMMDD-NNNN)
- Names paired with case identifiers

Commit checks inspect staged and unstaged tracked additions. Push checks inspect every
selected source commit, including later-removed and merge-resolution additions. Git read
errors and unsupported commands block. Binary content and commit/tag messages are outside
the scanner; see [control boundaries](../../../docs/compliance.md).

## Override

`LINTEL_OVERRIDE_CUSTOMER_DATA=1 LINTEL_OVERRIDE_REASON="explanation" git commit ...`

Use only when:
- Operator confirms data is public-domain (e.g. example email in docs)
- Data is sanitized placeholder that LOOKS like real but isn't
- Test fixture explicitly marked

The override flag permits the exception. A supplied reason is recorded but is not mechanically
required. Audit writes are best effort; a missing record does not prove no operation occurred.

## Audit

```jsonl
{"hook": "customer-data-block", "tier": "BLOCK", "ts": "...", "patterns": "...", "blocked": true}
{"hook": "customer-data-block", "tier": "OVERRIDDEN", "ts": "...", "patterns": "...", "reason": "...", "blocked": false}
```
