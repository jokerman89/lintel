---
name: customer-data-block
tier: JUSTIFIED-BLOCK
event: PreToolUse (Bash) for git commit/push
fires_on: staged content contains Tier 1 customer-data pattern
override: JSTACK_OVERRIDE_CUSTOMER_DATA=1 + JSTACK_OVERRIDE_REASON env vars
audit: ~/.jstack/audit/hooks.jsonl
---

# customer-data-block (JUSTIFIED-BLOCK)

Companion to `no-customer-data-in-message` (warn). Fires at COMMIT time and BLOCKS the commit if Tier 1 customer-data patterns are in the staged content.

## Why justified-block

Customer data in repo history = compliance incident. Even immediate-revert leaves artifacts in reflog and any fetched mirror. Per Premise: "No customer data in this repo, ever."

## Detection

Same Tier 1 customer-data patterns:
- Email addresses (regex)
- Phone numbers (intl + Swedish)
- Swedish personnummer (YYMMDD-NNNN)
- Names paired with case identifiers

## Override

`JSTACK_OVERRIDE_CUSTOMER_DATA=1 JSTACK_OVERRIDE_REASON="explanation" git commit ...`

Use only when:
- Operator confirms data is public-domain (e.g. example email in docs)
- Data is sanitized placeholder that LOOKS like real but isn't
- Test fixture explicitly marked

Reason logged to audit. Pattern + override pair surfaces in next `/caip-audit`.

## Audit

```jsonl
{"hook": "customer-data-block", "tier": "BLOCK", "ts": "...", "patterns": "...", "blocked": true}
{"hook": "customer-data-block", "tier": "OVERRIDDEN", "ts": "...", "patterns": "...", "reason": "...", "blocked": false}
```
