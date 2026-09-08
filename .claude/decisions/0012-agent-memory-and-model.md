# ADR-0012: agent persistent memory + model routing as frontmatter

**Status:** Accepted (2026-06-12)
**Decided by:** operator — battletest, competitor-gap question: what do comparable harnesses do that this one does not
**Implements:** .claude/engineering/audits/2026-06-12-battletest-synthesis.md (H4, H12)

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
- Memory + tools contract (corrected after the v5.2 review flagged a contradiction): setting
  `memory:` makes Claude Code auto-enable Write/Edit **for the agent to manage its own
  `.claude/agent-memory/<name>/MEMORY.md`** — it is not a license for the agent to modify the
  repo; the agent's task stays whatever its prompt + tools list say (our review/audit agents
  remain read-only reviewers that additionally keep a memory file). So `memory: project` IS
  correct on the read-only-tooled reviewers/auditors — that is the entire point (a reviewer that
  remembers this repo's prior findings). The earlier draft of this ADR wrongly said "do NOT add
  to read-only agents"; that exclusion only applies to an agent whose PROMPT must guarantee
  zero side effects of any kind (none of our reviewers make that guarantee — they were always
  spawned per-task and discarded). Pure search agents (Explorer, ReadOnly) are excluded from
  `memory:` for a different reason: they have nothing to compound, and get `model:` instead.
