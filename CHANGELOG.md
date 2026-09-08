# Changelog

Notable changes to Lintel. Behaviour changes to the canonical agent instructions are also logged in
`scaffolding/01-foundation/EVOLUTION-LOG.md`, which travels with each scaffolded repo.

---

## 0.10.0 — unreleased

- Preserve enterprise controls through block-list parsing, team-pack inheritance, required-field
  validation and risk classification. Session digests show the actually loaded pack.
- Keep short tasks while executing and reviewing bounded work packages (ADR-0026). Plans trace
  applicable profile requirements to task acceptance and evidence; blocked BUILD resumes in BUILD.
- Correct sizing false positives and expose whole-cycle estimate provenance without multiplying
  the estimate by leaf count. New integration cases exercise actual helpers and skill snippets.
- Inspect complete selected push history and block collection failures, unsupported wrappers and
  replacement-object bypasses. Preserve checkpoints by repository and serialize registry updates.
- Select explicit work artifacts and keep review/scope state in the target repository, including
  installed-source workflows. Document profile value and pilot metrics without claiming certification.

### Added

- A portable GitHub Copilot repository kit with native core workflow skills, planner/builder/reviewer
  profiles, self-contained resources, managed-file integrity checks and conflict-safe updates.
- A dedicated Copilot plugin manifest for the native core adapters, preserving the existing Claude
  Code integration and keeping the wider canonical catalog available as source content.
- An optional Spec Kit workflow bridge that references existing specifications, plans and task IDs
  while preserving a single authoritative task list.
- Copilot onboarding, enterprise pilot and rollout guidance, and an evidence-based release checklist.

### Changed

- Copilot-first public positioning and documentation, with explicit distinctions between host
  capabilities, installed Lintel adapters and live client validation.
- Security and compliance documentation now states scanner limitations, unsupported Copilot hook
  translation, best-effort maintenance and retained third-party license notices.
- Generated catalogs and integration checks are part of launch verification; inventory counts are
  no longer repeated as fixed promises throughout adopter documentation.

These changes extend the beta line for adoption. They do not claim a completed
enterprise pilot, compliance certification or a published 1.0 release.

---
## 0.9.0-beta — 2026-08-28

**First public release.** Lintel had been developed and used privately for three months before this
point; `0.9.0-beta` is where it becomes a public project. The version number restarts to signal
honestly what this is: a stable, tested surface that is not yet API-frozen. The development history
that preceded it is summarised below.

### Added
- **`docs/architecture.md`** — the public architecture reference: spine and pack, the mechanical
  helper layer, navigation, the five depth modules, where state lives, and what the test tiers
  actually guarantee.
- **`docs/the-cycle.md`** — the nine phases in depth. What each does, what it produces, where the
  gates are, and the declared cost of skipping each one.
- **`docs/README.md`** — a documentation index organised by what the reader is trying to do.

### Changed
- **The public documentation surface was rebuilt.** `README.md` is now a landing page rather than a
  technical reference. Every published document was audited claim by claim against the live repo;
  74 stale or incorrect claims were corrected, including counts, version lines, capability claims,
  and paths that predated the `.claude/` home layout.
- **Internal engineering artifacts moved out of the public tree** into `.claude/engineering/`:
  audit records, Gate M1 evolution-log entries, Gate M2 compatibility audits, and superseded design
  documents. The public `docs/` tree went from 130 files to the documents an adopter actually reads.
  All 233 inbound references were repointed, including two that would have broken CI on Ubuntu and
  Windows and two generator write-paths that would have silently recreated the public directories.
- **`docs/precedence.md`** — precedence level 3 is now *pack-promoted agents*, matching the model
  `AGENT-INSTRUCTIONS.md` has always described.

### Removed
- **`docs/promoted-agents.md`** — it described a mechanism for installing and tracking third-party
  agent packs that does not exist. `install/install.sh` clones nothing; the file made a licensing
  and supply-chain claim the code contradicted.
- **`LAYERS.md`, `docs/session-harness.md`** — both carried explicit superseded banners and stale
  architecture. Replaced by `docs/architecture.md`.
- **`SHIP-GATE.md`** moved to `.claude/engineering/` — it is an internal release checklist, not
  adopter documentation.

### Fixed
- `install/verify.sh` referenced two design documents by a path that the relocation would have
  broken, in a check that runs in three CI jobs on two operating systems.
- `tests/shape/no-swedish.sh` had two allowlist branches exempting whole directories from the
  English-only guard. Both are gone; the guarantee now holds without exception across the public
  tree.
- Three design documents quoted operator dialogue verbatim in a non-English language. They are no
  longer part of the published surface.

### Known limitations
For current support boundaries and limitations, see the [FAQ](docs/faq.md).

- Enforcement hooks are a Claude Code mechanism and do not fire on the other seven supported CLIs.
- `/li:generate-pdf`, `/li:generate-xlsx` and `/li:generate-visio` are template-only slots.
- 24 of the 33 hooks ship opt-in rather than auto-registered.
- The token estimator reports `UNCALIBRATED` until actuals have been recorded for a given work size.
- There is no uninstall script.
- The neutral `_default` pack ships no roles and no personas, so role and persona commands have
  nothing to list on a stock install.

### Upgrade note
Anyone who installed a pre-beta build from the plugin marketplace should uninstall and reinstall
once. The version number moves down from the internal `5.x` line, so an in-place update will not
pick this release up.

---

## Pre-beta development — 2026-05-26 to 2026-06-18

Condensed. The full per-release detail lives in the repository history.

| Line | What it established |
|---|---|
| **v1** | The four-layer scaffolding model and the first skill, agent and hook set. |
| **v2** | The portability shim runtime, the per-CLI support schema, and the context-budget engine. |
| **v3** | The plugin-manifest pattern — write skills and agents once, ship thin per-CLI manifests. The agent fleet was built out across eight domains, and the project was renamed to Lintel. |
| **v3.5** | The nine-phase cycle itself: eight phase skills plus the orchestrator, role-lifting, context warming, and the composite shortcuts. |
| **v3.6–v3.7** | The observation spine (usage log, hook status, lesson surfacing, generated catalog), the alias mechanism, and the frontend design family. |
| **v4.0** | The reframe: one architecture rather than five features — spine, pack, navigation, depth. Packs became the identity layer, resolved through a single accessor. |
| **v4.1–v4.6** | The five engineering-domain modules (architecture, data, security, devops, testing) and the pass that composes them in dependency order. |
| **v4.7** | The company identity was extracted out of the spine into a separate installable pack. This is what made a public release possible at all. |
| **v4.8–v4.12** | The repo began dogfooding its own scaffolding. Session-digest auto-load, the cycle-position footer, scope-scaled planning, and the cross-artifact consistency gate. |
| **v5.0** | The `.claude/` home layout: everything Lintel generates for a repo under one root, knowledge committed and runtime gitignored. |
| **v5.1–v5.2** | Subtraction — the same capability with 23% less surface — followed by a security hardening pass on the block gates. |
| **v5.3–v5.5** | Multi-CLI hardening, trigger-form prompt craft across the skill and agent surface, and the retrieval-backed design system. |
| **v5.6–v5.8** | Self-healing cycle continuity (the three hooks that keep position across a compaction), the extension-pack contract, and a full launch-readiness audit. |

The disciplines this project holds itself to were learned the hard way over that period, and most of
them exist because something went wrong first. Two are worth stating outright: *if a guarantee is
only prose, it is not a guarantee* — which is why the one-way-door check, the memory operations and
the capability table are code rather than convention; and *the system must not drift from its own
description* — which is why 36 structural-contract tests fail the build when it does.
