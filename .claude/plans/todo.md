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

- [x] `.claude/memory/MEMORY.md` index format (≤200 lines) + convergence contract doc
- [x] `lib/memory.sh`: lessons_surface (mechanical, called from SENSE Step 0a)
- [x] CAPTURE update-phase: add/update/supersede/no-op classification vs existing lessons
- [x] Supersede-don't-delete convention (`superseded_by:` markers) in lessons/memory templates
- [x] Block-budget warn hook (MEMORY.md ≤200, lessons threshold)
- [x] Consolidate context-* family 8→3 skills + `bin/_context.sh` (save/list/restore)
- [x] Brief-forge: implement completeness evaluator (bash), delete unimplemented promises — L-003 RE-VERIFIED: evaluators (security/completeness/stale) ALREADY exist in lib/brief-forge-evaluators.sh (213 lines); audit claim was wrong; no build needed
- [x] Subtract operator-profile.jsonl write from CAPTURE Step 9
- [x] gbrain SKILL.md honest labeling
- [x] `.claude/rules/` path-scoped rules support + digest index lines
- [x] AGENTS.md emission in scaffold
- [x] Ready-work view in digest (blocked_by in job.yaml)
- [x] Memory-map rewrite in CLAUDE.md/AGENT-INSTRUCTIONS + scaffolding
- [x] ADR-0006 memory v2

## Phase C — Obsidian patterns (PR: feat/obsidian-patterns)

- [x] Locked session-note frontmatter schema (type/date/repo/branch/outcome/tags)
- [x] `templates/obsidian/sessions.base` + `bin/li-vault-init` (base + repo hub note)
- [x] CAPTURE Step 7b: 00-index.md regeneration + wikilinks (hub + predecessor)
- [x] Pack keys `obsidian.*` (flat two-level) + unit tests — DESIGN SIMPLIFICATION: reused existing capture.vault_sink_* keys, no new surface (subtraction)
- [x] docs/concepts: repo-as-read-vault workflow (.claude/ as mini-vault)
- [x] ADR-0007 Obsidian integration scope

## Review (2026-06-12 — initiative complete in one session)

All three phases + Phase 0 shipped as a stacked PR chain: **#62** (vault sink, rebased clean)
→ **#63** (.claude/ home, ADR-0005) → **#64** (memory v2, ADR-0006) → **#65** (Obsidian
patterns, ADR-0007). Suite 74/74 on every pushed HEAD. Every phase went through the full
L-007 loop — three independent reviews, three SHIP-WITH-FIXES verdicts, every P1/P2 acted on
same-session. The reviews earned their keep: the registry-clobber race (A), the /li:learn
grammar drift that would have made new lessons invisible to the new mechanical layer (B), and
a unit test that could pollute the operator's real vault + a red committed suite my pre-commit
run missed (C → L-010). Notable verification wins: the brief-forge evaluators turned out to
ALREADY exist (the memory audit overclaimed the gap — L-003 again), and the .claude/rules
native-loading claim was softened to documented reality after checking the actual docs/issues.
Memory map, instruction files and scaffolding all moved in lockstep; the factory ran on
itself (L-006): this repo is migrated, and the session note you are reading about landed in
the operator's vault through the new schema + hub + index, installed by li-vault-init.

Operator next: merge the chain in order (re-target #63 to main after #62), run
li-migrate-claude-home on other repos, re-enable the vault sink in a personal pack override.
