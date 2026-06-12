---
name: no-customer-data-in-screenshot
tier: warn-only
event: PostToolUse (Bash | Skill /browse)
fires_on: screenshot file produced
override: not applicable (post-fact informational)
audit: .claude/runtime/audit/hooks.jsonl
---

# no-customer-data-in-screenshot

Surfaces when a screenshot is produced from `/browse` that may contain customer-data patterns. Performs OCR-lite (text in image cannot be Bash-scanned, so this hook relies on the URL hostname + DOM-snapshot text).

## Detection

- Trigger when a file matching `*.png` lands under `~/.lintel/browse-runs/<ts>/`
- Read the corresponding `dom.html` in the same dir
- Scan DOM for customer-data patterns (same regexes as `no-customer-data-in-message`)

## Why warn-only (not block)

The screenshot/DOM already landed when this fires — block is post-fact. The hook surfaces so operator can quarantine + delete BEFORE the artifact moves anywhere.

## Action surfaced

If a hit: "Screenshot at ~/.lintel/browse-runs/<ts>/screenshot.png may contain customer-data — quarantine before sharing."
