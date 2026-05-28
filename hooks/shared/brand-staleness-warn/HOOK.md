---
name: brand-staleness-warn
tier: warn-only
event: PreToolUse (Skill /generate-ppt|/generate-word|/generate-web)
fires_on: ~/.lintel/brand/brand-version.txt older than 90 days
override: pass --ignore-stale-brand flag (operator decision, logged)
audit: ~/.lintel/audit/hooks.jsonl
---

# brand-staleness-warn

Surfaces when doc-gen runs against brand assets older than 90 days. Brand portal updates regularly; stale brand may mean outdated logo, deprecated icon set, retired color palette.

## What it does

- Reads `~/.lintel/brand/brand-version.txt`
- Computes age vs current time
- If >90 days: WARN

## Why warn-only

Operator may have legitimate reasons to ship with stale brand (archival deliverable, comparison demo, customer constraint). Block would be too aggressive. Warn lets operator decide.

## Override path

`/generate-ppt --ignore-stale-brand "reason"` (and equivalent on /generate-word, /generate-web). Reason logged to audit.

## What's NOT in scope

- Detecting brand version mismatch with portal (would require auth + portal API access)
- Auto-pulling latest brand (operator-driven per BRAND-INTEGRATION.md)
- Visual diff between current and last brand (out of scope; manual operator review)

## Audit format

```jsonl
{"hook":"brand-staleness-warn","tier":"warn","ts":"...","brand_age_days":127,"brand_version":"2026-Q1","skill_invoked":"/generate-ppt"}
```
