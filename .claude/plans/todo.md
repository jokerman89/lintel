# todo — v5.0 claude-home + memory v2 + Obsidian (2026-06-12)

Design: [docs/design/lintel-v5-claude-home-memory-obsidian-design.md](../docs/design/lintel-v5-claude-home-memory-obsidian-design.md)
Mode: meta-infra (Gates M1–M4). Decisions D1–D4 locked by operator 2026-06-12.
(Previous initiative v4.11 closed 2026-06-10 — see git history of this file.)

## Phase 0 — unblock

- [x] Open PR for `feat/capture-vault-sink` against main (vault sink ships first)
- [x] Branch `feat/claude-home` off `feat/capture-vault-sink`

## Phase A — `.claude/` home + migration (PR: feat/claude-home)

Independent review (L-007): SHIP-WITH-FIXES — 3 P1 (registry war, marker-on-partial-failure, neutral-pack vault default) + 9 P2 + 7 P3; all P1 + silent-degradation P2s fixed same-session. PR #62 opened for vault-sink; its neutral-pack default fix is folded here + cherry-picked to #62.

- [x] `lib/paths.sh` — single source for all Lintel paths, legacy fallback
- [x] Shape test: no skill/hook/bin hardcodes legacy paths outside lib/paths.sh
- [x] `bin/li-migrate-claude-home` — idempotent: git mv knowledge, create runtime/, .gitignore, redirect stubs, settings.json autoMemoryDirectory
- [x] Widest-token-set sweep (L-005) of all legacy path refs across skills/hooks/lib/bin/agents/scaffolding/AGENT-INSTRUCTIONS/CLAUDE.md.template
- [x] `bin/_audit.sh` scope routing (repo → .claude/runtime/audit/, global → ~/.lintel/audit/)
- [x] `bin/_jobs.sh` — job data in-repo, ~/.lintel/jobs/_active.md becomes cross-repo registry
- [x] session-digest hook reads new paths (+ legacy fallback)
- [x] li-doctor layout check + un-migrated warning
- [x] Scaffolding templates install new layout
- [x] Run migration on Lintel itself (dogfood)
- [x] Gate M1 structure-changes entry + M2 compat audit + M3 shape tests green
- [x] ADR-0005 claude-home layout

## Phase B — memory v2 (PR: feat/memory-v2)

- [ ] `.claude/memory/MEMORY.md` index format (≤200 lines) + convergence contract doc
- [ ] `lib/memory.sh`: lessons_surface (mechanical, called from SENSE Step 0a)
- [ ] CAPTURE update-phase: add/update/supersede/no-op classification vs existing lessons
- [ ] Supersede-don't-delete convention (`superseded_by:` markers) in lessons/memory templates
- [ ] Block-budget warn hook (MEMORY.md ≤200, lessons threshold)
- [ ] Consolidate context-* family 8→3 skills + `bin/_context.sh` (save/list/restore)
- [ ] Brief-forge: implement completeness evaluator (bash), delete unimplemented promises
- [ ] Subtract operator-profile.jsonl write from CAPTURE Step 9
- [ ] gbrain SKILL.md honest labeling
- [ ] `.claude/rules/` path-scoped rules support + digest index lines
- [ ] AGENTS.md emission in scaffold
- [ ] Ready-work view in digest (blocked_by in job.yaml)
- [ ] Memory-map rewrite in CLAUDE.md/AGENT-INSTRUCTIONS + scaffolding
- [ ] ADR-0006 memory v2

## Phase C — Obsidian patterns (PR: feat/obsidian-patterns)

- [ ] Locked session-note frontmatter schema (type/date/repo/branch/outcome/tags)
- [ ] `templates/obsidian/sessions.base` + `bin/li-vault-init` (base + repo hub note)
- [ ] CAPTURE Step 7b: 00-index.md regeneration + wikilinks (hub + predecessor)
- [ ] Pack keys `obsidian.*` (flat two-level) + unit tests
- [ ] docs/concepts: repo-as-read-vault workflow (.claude/ as mini-vault)
- [ ] ADR-0007 Obsidian integration scope

## Review (fylls i vid task-slut)

- [ ] Per-phase: shape + unit green, independent CodeReviewer subagent on real diff (L-007), footer discipline (L-008), no `| tail` on runners (L-009)
