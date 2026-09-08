# Evolution Log

Changelog for the scaffolding system. Most recent first.

Different from the top-level `CHANGELOG.md` (which tracks the `jokerman-lintel` repo itself): this log travels with the scaffolding when it lands in a target repo. It captures changes to the canonical instructions, the subagent set, the task-file conventions, and other patterns that affect how the assistant operates.

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

## 2026-09-08 — short leaves with work packages

**Type:** TEMPLATE
**What changed:** The plan template groups short tasks into bounded packages and records owner,
requirements, dependencies and acceptance evidence. BUILD executes one package with one owner
and reviews every leaf plus integration in spec/quality stages (Lintel ADR-0026).
**Why:** The operator selected hybrid execution to reduce repeated setup while retaining traceability.
**Impact on existing repos:** Existing leaf IDs and job state remain valid. An ungrouped plan uses
singleton packages. No migration, new scheduler or automatic company policy is introduced.

## 2026-06-12 — v5 `.claude/` home for scaffolded state

**Type:** TEMPLATE
**What changed:** The per-repo state templates moved under `.claude/` (ADR-0005 in the Lintel repo):
`tasks/{lessons,memory,personas}.md` → `.claude/memory/{lessons,working-state,personas}.md`,
`tasks/todo.md` → `.claude/plans/todo.md`, `docs/adr/` → `.claude/decisions/`, and
`docs/personas/EXAMPLE.md` → `.claude/memory/personas-example.md`. Runtime state (cycle state,
context-saves, job data, repo event log) lives gitignored at `.claude/runtime/{state,sessions,jobs,audit}/`.
`CLAUDE.md.template` carries the updated session-start ritual + memory map.
**Why:** One circle of control — everything Lintel generates for a repo lives under `.claude/`,
knowledge committed and runtime gitignored. Operator identity stays in `~/.lintel/`.
**Impact on existing repos:** Already-scaffolded repos keep working — skills resolve legacy paths via
`lib/paths.sh` fallbacks. Migrate a repo with `bin/li-migrate-claude-home`, which moves the files and
stamps `.claude/lintel-layout.yaml` (`layout_version: 5`).

---

## 2026-05-26 — Initial release

**Type:** TEMPLATE
**What changed:** Scaffolding initialized as part of `jokerman-lintel`. Contains:

- `CORE-PRINCIPLES.md`, `EVOLUTION.md`, this `EVOLUTION-LOG.md`.
- `tasks/` — `lessons.md`, `memory.md`, `personas.md`, `todo.md` as templates.
- `docs/adr/` — `README.md` describing ADR process, `TEMPLATE.md` for new ADRs.
- `docs/personas/` — `EXAMPLE.md` showing the persona format.
- `.claude/agents/` — `ReadOnly`, `CodeReviewer`, `TestRunner`, `SanityChecker` as base subagents.
- `.claude/SUBAGENT-GUIDE.md` — how to add new subagents.

**Why:** First snapshot of the scaffolding. Future changes start here and accumulate as entries above.

**Impact on existing repos:** None — this is the starting point. Subsequent template changes will note impact on already-scaffolded repos here.
