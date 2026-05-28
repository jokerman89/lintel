---
name: no-customer-data-in-message
tier: warn-only
event: UserPromptSubmit
fires_on: every operator prompt
override: not applicable (warn only)
audit: ~/.lintel/audit/hooks.jsonl
---

# no-customer-data-in-message

Scans the operator's prompt for customer-data tells before it lands in the conversation. Warns inline; does NOT block.

## What patterns it catches

- Email addresses (regex)
- Phone numbers (various formats)
- Common Swedish personnummer format (YYMMDD-NNNN)
- Names paired with case identifiers ("Anna Andersson, case 4421")
- Address lines with street + number

## What it does NOT catch (false-negative tolerance)

- Sanitized placeholders ("Customer A", "Acme Corp") — by design
- Test fixtures clearly marked
- Public-domain references (CEO names from press releases)

## Why warn-only

Customer-data tells in operator prompts are often legitimate (operator typing context that's already been disclosed elsewhere in the conversation). A block would be too aggressive. Warn lets operator self-correct without friction.

## Audit log

```jsonl
{"hook": "no-customer-data-in-message", "tier": "warn", "ts": "...", "pattern_matched": "email", "sanitized_prompt_preview": "..."}
```

Prompt content itself is NOT logged — only pattern type. (Logging the content would be a customer-data leak.)
