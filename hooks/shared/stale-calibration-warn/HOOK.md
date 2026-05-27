---
name: stale-calibration-warn
tier: warn-only
event: PreToolUse (Bash | Edit | Write) when target involves trailblazer-tagged content
fires_on: trailblazer-voice operation while TRAILBLAZER-CALIBRATION is >30 days old
override: pass --ignore-stale-calibration to invoking skill (logged)
audit: ~/.jstack/audit/hooks.jsonl
---

# stale-calibration-warn

Warns when a trailblazer-voice operation (rewrite, voice-check, demo-deliverable-gen, etc.) is about to run while the voice calibration is older than 30 days.

Calibration drifts as MS Our Voice guide evolves, as the team's interpretation refines, and as new edge cases surface. Old calibration = decreasing confidence in voice-check verdicts.

## Detection

- Reads `OurVoice-calibration.md` last-updated timestamp (frontmatter or file mtime fallback)
- Compares to current time
- If > 30 days: WARN

## Why warn-only

Operator may have a deadline and need to ship with stale calibration. Don't block, but make the staleness visible. The downstream voice-check verdict carries the UNCALIBRATED-or-STALE stamp, which downstream `/release-ev2` reads.

## Override path

Skills that respect this warning (`/rais-customer-voice-check`, `/msvoice-rewrite`, `/demo-deliverable-gen`) accept `--ignore-stale-calibration` flag that surfaces a reason field. Reason logged to audit.
