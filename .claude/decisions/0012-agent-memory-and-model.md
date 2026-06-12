# ADR-0012: agent persistent memory + model routing as frontmatter

**Status:** Accepted (2026-06-12)
**Decided by:** operator (battletest — "vad gör andra som vi inte gör")
**Implements:** docs/audit/2026-06-12-battletest-synthesis.md (H4, H12)

## Context

Memory is Lintel's brand, yet 0 of 69 agents declared `memory:` — Claude Code's per-subagent
persistent memory (`.claude/agent-memory/<name>/`, MEMORY.md auto-injected per invocation,
shipped v2.1.33) was unused. The CodeReviewer that double-reviews every BUILD task relearned
the repo from scratch each dispatch. Separately, BUILD prescribed Haiku/Sonnet/Opus tiers as
PROSE to the orchestrator; 0 agents declared `model:`, so mechanical agents (Explorer,
TestRunner, ChangelogMaintainer) inherited the flagship model — a standing token tax.

## Decision

1. **Persistent memory** (`memory: project`) on the agents whose value compounds with repo
   knowledge: CodeReviewer, SecurityAuditor, TestRunner, and the cross-cutting reviewers.
   `project` scope writes to `<repo>/.claude/agent-memory/<name>/` — committed, shareable,
   visible. CAPTURE becomes the librarian: at cycle close it may prune/supersede agent-memory
   MEMORY.md the same way it curates lessons (the curation discipline Lintel already owns).
   Degrades to nothing on non-Claude CLIs.
2. **Model routing** (`model:`) on mechanical agents that don't need flagship reasoning —
   Explorer/ReadOnly/TestRunner/ChangelogMaintainer/DocWriter → a cheaper tier; architecture/
   security/review agents stay on the inherited (flagship) model. Routing becomes structural,
   not a prose instruction the orchestrator may forget.

## Consequences

- Reviewers accumulate repo-specific findings across sessions ("third off-by-one in this
  parser — L-0NN applies") — the memory thesis fused with the platform primitive.
- Mechanical dispatches bill at the right tier without orchestrator vigilance.
- New frontmatter fields are optional and Claude-Code-honored; the frontmatter-lint contract
  gains `memory` + `model` as recognized optional keys (not required).
- Risk: `memory:` auto-enables Read/Write/Edit for the agent (platform behavior) — fine for
  reviewers; we do NOT add it to agents that must stay read-only by contract.
