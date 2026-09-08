# ADR-0025: Self-contained session protocol across agent entry files

**Status:** Accepted — 2026-09-08

## Context

The operator asked that the reusable disciplines in their user-global engineering protocol be
present at repository/project level, including fresh Copilot sessions without that personal
machine configuration. A pointer-only entry cannot provide that guarantee. Existing root
CLAUDE.md repeated six workflow rules but omitted parts of the fuller protocol; AGENTS.md was
mostly navigation. Their precedence statements also disagreed about whether generic user-global
or repository-specific context wins.

## Decision

Maintain the complete reusable protocol once in
`scaffolding/01-foundation/SESSION-PROTOCOL.md`. Materialize identical content inside marked
blocks in root AGENTS.md, root CLAUDE.md, and both scaffold entry templates. The markers are
`LINTEL:SESSION-PROTOCOL:START` and `LINTEL:SESSION-PROTOCOL:END`. `bin/li-instructions.py sync`
updates those blocks; `check` detects drift. Keep unique repository context outside the block.

Consumer Copilot installation carries the same block into repository entry files while preserving
project-owned prose. Its managed inventory must distinguish block ownership from whole-file
ownership, and refuse local edits to an owned block instead of silently erasing them. Copilot's
short repository-wide instruction file can summarize the six core disciplines and link to the
full AGENTS.md entry; it need not duplicate the entire long protocol inside the code-review input.

The full protocol covers document authority, scope, planning, read-before-write, risks, autonomous
authorized fixes, verification, subtraction, agent reporting/permissions, shared schemas, coding
style, structured comments, delivery, authorization, deviation handling, recovery, disagreement,
lessons and fresh-session continuity. Host-specific installation assumptions are adapted for a
shared Copilot repository kit. Personal machine paths, marketplace approvals and migration history
are not copied. The coverage map records every source heading's disposition.

Repository-specific context wins over generic user-global defaults. Working notes and lessons
never override accepted architecture, constitution or specifications. Explicit user authorization
persists for its stated scope; a new unresolved decision is surfaced without manufacturing another
approval for work the user already authorized.

## Alternatives

1. **Pointers only:** smallest output, but fails the user's self-contained startup requirement.
2. **Independent handwritten copies:** self-contained but creates drift between clients and projects.
3. **Shared source plus repeated generated blocks:** self-contained with a testable synchronization
   contract. Selected; accepts deliberate cross-file repetition while consolidating duplicates
   inside a single entry file.

## Consequences and verification

This supersedes ADR-0019's staged proposal to reduce CLAUDE.md to a pointer. It preserves its aim
of one source of truth through generation rather than one physical entry file. Existing project
ownership, commands, memory maps, frozen zones and pack rules remain outside the shared block.

Verify exact block equality in all four repository/template targets, byte-preservation of prose
outside markers, idempotent sync, drift detection, malformed-marker refusal, and clean consumer
installation with no user-global instruction file. Record actual outcomes in the build review;
no structural check alone proves a model follows the protocol.

Coverage: `.claude/engineering/audits/2026-09-08-session-protocol-coverage.md`.
