---
name: no-trailblazer-without-corpus
tier: warn-only
event: PreToolUse (Edit | Write)
fires_on: writing a file with frontmatter `voice: trailblazer` while T0 corpus empty/incomplete
override: pass --uncalibrated flag to invoking skill (logged)
audit: ~/.jstack/audit/hooks.jsonl
---

# no-trailblazer-without-corpus

Warns when an Edit/Write produces a file with `voice: trailblazer` (or `voice: trailblazer-draft`) while T0 corpus calibration is incomplete (CALIBRATION-MD shows <90% per cell × <10 cells).

## Why warn-only

Operator may have a deadline + need to produce trailblazer-tagged DRAFT before full calibration. Output carries UNCALIBRATED stamp; downstream `/customer-voice-check` refuses to certify.
