# ADR-0019: AGENTS.md as the primary cross-CLI instruction layer

> Renumbered 0015 → 0019 (2026-06-14): 0015 collided with the design-dna ADR created
> 4 min earlier (first claimant keeps the number); 0018 reserved for extension-pack-contract.

**Status:** Accepted-direction, build staged (2026-06-13)
**Implements:** docs/audit/2026-06-13-cli-issues-craft-synthesis.md (workstream 1, H13)

## Context

AGENTS.md is a verified Linux-Foundation standard (Agentic AI Foundation, donated by OpenAI Dec
2025), read natively by Codex, Cursor, Copilot CLI, Droid, Gemini (opt-in), opencode, Zed, and
Windsurf. Lintel maintains 6 drifting instruction files + bespoke manifests; the parity-check
exists precisely because they drift. The portability work AGENTS.md now does for free is the
thing Lintel hand-maintains.

## Decision

Make root AGENTS.md the canonical instruction substance; CLAUDE.md becomes a thin pointer that
defers to it (Claude reads both; CLAUDE.md wins on conflict, so it must defer). The scaffold
already emits AGENTS.md-as-pointer — invert it. This collapses the 6-file parity surface to ~2.

## Consequences (when built)

- One canonical file read by 8+ CLIs; parity-check becomes trivial.
- Staged, not done this cycle: it's a careful content move (substance from CLAUDE.md → AGENTS.md
  without losing the Claude-specific bits) that deserves its own focused change + review.
