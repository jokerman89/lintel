---
name: no-customer-data-in-screenshot
tier: warn-only
event: PostToolUse (compatible host adapter after web-session screenshot/DOM capture)
fires_on: screenshot file produced
override: not applicable (post-fact informational)
audit: .claude/runtime/audit/hooks.jsonl
---

# no-customer-data-in-screenshot

Warns about customer-data patterns in a selected screenshot's companion DOM.
Used after `/web-session --mode browse` capture only when an actual compatible
host adapter supplies the owned artifact directory. File presence is not hook
registration, and this script does not inspect pixels or perform OCR.

## Detection

- Receive the explicitly selected artifact directory through the hook input or
  positional argument; it does not watch a global screenshot directory
- Read `dom.html` in that directory only if the caller actually captured it
- Scan DOM for customer-data patterns (same regexes as `no-customer-data-in-message`)
- No companion DOM means no scan. This is not a successful screenshot-data check.

## Why warn-only (not block)

The screenshot/DOM already exists when this optional hook runs. It warns so the
operator can apply an authorized quarantine procedure before sharing. It neither
quarantines nor deletes artifacts and does not replace required P05 data controls.

## Action surfaced

If a hit, report the actual artifact directory and matched pattern identifiers,
not captured personal data. Quarantine requires an explicit owned destination;
no personal-directory move, upload or cleanup is performed automatically.
