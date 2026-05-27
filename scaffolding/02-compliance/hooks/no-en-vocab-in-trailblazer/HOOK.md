---
name: no-en-vocab-in-trailblazer
tier: warn-only
event: PreToolUse (Edit | Write)
fires_on: trailblazer-tagged content with Tier 1 AI-tell vocab
override: not applicable (operator should regenerate, not bypass)
audit: ~/.jstack/audit/hooks.jsonl
---

# no-en-vocab-in-trailblazer

Scans Edit/Write payload for Tier 1 AI-tell vocab when the target file has `voice: trailblazer` frontmatter. Tier 1 vocab is hard-blocked from any Our Voice output.

## Tier 1 vocab (from TRAILBLAZER-CORPUS.md)

`delve`, `crucial`, `robust`, `comprehensive`, `multifaceted`, `nuanced`, `intricate`, `paradigm`, `harness`, `navigate the landscape`, `at the forefront`, `cutting-edge`, `game-changing`, `revolutionize`, `transformative`, `synergy`, `holistic`, `best-in-class`, `world-class`, `state-of-the-art`.

## Why warn-only (in this layer)

The companion enforcement happens at `/customer-voice-check` (which blocks distribution) and `/msvoice-rewrite` (which regenerates paragraphs hitting Tier 1). This hook surfaces at edit-time for fast feedback.

## What it does

For each Tier 1 word detected: surface which paragraph index + which word. Operator reviews + rewrites.
