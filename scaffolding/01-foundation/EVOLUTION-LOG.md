# Evolution Log

Changelog for the scaffolding system. Most recent first.

Different from the top-level `CHANGELOG.md` (which tracks the `jokerman-session-setup` repo itself): this log travels with the scaffolding when it lands in a target repo. It captures changes to the canonical instructions, the subagent set, the task-file conventions, and other patterns that affect how the assistant operates.

Entry format:

```
## YYYY-MM-DD — short title

**Type:** TEMPLATE | CORE | PROPOSAL | ARCHIVE
**What changed:**
**Why:**
**Impact on existing repos:**
```

Types:
- **TEMPLATE** — change to the scaffolding template (new file added, file removed, structure shift).
- **CORE** — change to a load-bearing rule (compliance, precedence, auto-mode bounds, etc.).
- **PROPOSAL** — draft / not-yet-adopted change. Move to TEMPLATE or CORE when accepted; move to ARCHIVE when rejected.
- **ARCHIVE** — rejected or superseded entry, kept for history.

---

## 2026-05-26 — Initial release

**Type:** TEMPLATE
**What changed:** Scaffolding initialized as part of `jokerman-session-setup`. Contains:

- `CORE-PRINCIPLES.md`, `EVOLUTION.md`, this `EVOLUTION-LOG.md`.
- `tasks/` — `lessons.md`, `memory.md`, `personas.md`, `todo.md` as templates.
- `docs/adr/` — `README.md` describing ADR process, `TEMPLATE.md` for new ADRs.
- `docs/personas/` — `EXAMPLE.md` showing the persona format.
- `.claude/agents/` — `ReadOnly`, `CodeReviewer`, `TestRunner`, `SanityChecker` as base subagents.
- `.claude/SUBAGENT-GUIDE.md` — how to add new subagents.

**Why:** First snapshot of the scaffolding. Future changes start here and accumulate as entries above.

**Impact on existing repos:** None — this is the starting point. Subsequent template changes will note impact on already-scaffolded repos here.
