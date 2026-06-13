# todo — active initiatives

## v5.4 design DNA — consume UI/UX Pro Max + anthropic-default profile (2026-06-13, branch feat/v5.4-design-dna)

Design: docs/design/lintel-v5.4-design-dna-design.md (ADR-0015 + ADR-0016). Mode: meta-infra (M1-M4).
Research: .claude/runtime/research/{A1,A2,B,C}*.md. Upstream: nextlevelbuilder/ui-ux-pro-max-skill @ MIT.

- [ ] B1 corpus — skills/design-dna/{data,scripts}: copy UUPM canonical tree (minus google-fonts.csv/draft.csv/_sync_all.py), patch domain registry, attribution headers, ATTRIBUTION.md, smoke-run search + design-system compose
- [ ] B2 profile — profiles/anthropic-default.yaml (7 canonical tokens + derived gap-fills, source-marked)
- [ ] B3 skill — skills/design-dna/SKILL.md (module dispatch: search|system|persist|validate|profile; python-absent grep fallback documented)
- [ ] B4 validator — scripts/validate_design.py adapted from UUPM html-token-validator.py (forbidden patterns + profile contrast pairs, exit 1)
- [ ] B5 integration — frontend-design Step 1.5 (required DNA pass) + spec additive fields (palette/style/design_dna); frontend-typography + frontend-motion corpus-query steps; generate-web/generate-app stack-search + validate; frontend-design-review/design-review mandatory checklist
- [ ] B6 agents — FrontendArchitect (two-pass doctrine + anti-cliché), TypographyCurator, MotionDirector, DesignSystemAuditor (validator-first) — judgment not bloat, ADR-0014 style
- [ ] B7 tests — tests/shape/design-dna-corpus.sh + tests/unit/design-dna-search.sh + tests/unit/design-validator.sh; full suite green on committed tree (L-010)
- [ ] B8 docs — ADR-0015 (consume UUPM, L-001 exception) + ADR-0016 (anthropic-default) + M1 structure-changes entry + M2 li-compat-audit + CHANGELOG
- [ ] REVIEW — independent CodeReviewer on real diff (L-007); act on P1/P2
- [ ] SHIP — push branch, PR against main; CAPTURE — working-state + lessons

## v5.2 battletest — newcomer-clarity doc fixes J1-J6 (2026-06-12, branch feat/v5.2-battletest)

Source: docs/audit/2026-06-12-battletest-synthesis.md (JAB rows) + noob first-hour findings.
SCOPE: README.md, docs/getting-started.md, skills/welcome/SKILL.md, CLAUDE.md, install/install.sh, NEW docs/GLOSSARY.md ONLY. Do NOT touch other skills/ or agents/.

- [x] J1 — canonical hook-activation matrix added to getting-started ("How hook activation works", ADR-0008). README:5, welcome Step 4, install.sh header all point at it. No "inert" without "(bare install only)"; no "zero-setup" without "(plugin install)" — verified by grep.
- [x] J2 — "168 skills" de-hardcoded in welcome (frontmatter + body) → "the full skill set". README/getting-started counts already 124/69 (correct); getting-started finding-skills section de-hardcodes (compute at runtime).
- [x] J3 — CLAUDE.md:31 stale `adr/` listing → points at .claude/decisions/ + names docs/adr as redirect stub. 4-root "Where things live" map added to README + getting-started. (CLAUDE.md state map + ritual were already v5-correct — confirmed, not manufactured.)
- [x] J4 — getting-started "Finding skills" section: /li:help + /li:catalog + 7-bucket prose purpose-grouping.
- [x] J5 — install.sh: /tier-stamp-agents line removed; entra/+rai/dpia/dsb mkdir removed (pack concern); header honest about upstream stub (lists, does not clone); upstream-step message says "listed only". README+getting-started got the "Windows: install\install.ps1" line.
- [x] J6 — docs/GLOSSARY.md created (12 terms, one screen); linked from README first section + getting-started top; "the 9-step cycle: 8 core phases + SCOPE" phrasing used consistently.
- [x] VALIDATE — grep clean (no 168 / inert always qualified / no stale docs/adr mis-pointers); no-swedish.sh RC=0.

### Review (J1-J6)

Six fixes landed across 5 files + 1 new (GLOSSARY). Canonical hook matrix lives ONCE at
docs/getting-started.md#how-hook-activation-works; README/welcome/install.sh all point at it
rather than restating. Found the branch's CLAUDE.md was already largely v5-correct (state map +
ritual cited .claude/decisions and .claude/runtime/state) — the J3 instruction assumed more drift
than exists; corrected only the one genuinely stale ref (line 31) and did not manufacture changes.
DEVIATION FLAGGED: install.ps1:53 still creates the Microsoft-specific entra/ dir (same ghost
removed from install.sh) — install.ps1 was NOT in authorized scope, so surfaced not fixed; the
new Windows line points newcomers at it, so it should get the same J5 treatment in a follow-up.

## v5.1 subtraction — ADR-0009 sub-skill collapse (2026-06-12, branch feat/v5.1-subtraction)

- [x] 5 modules (ta/da/sc/dh/tq): add `## Sub-capability dispatch` table + short load-bearing subsections; `/li:<module> <capability>` shorthand; direct dispatch in single granularity; shed Pause-points/Hop-in/Voice boilerplate per docs/concepts/skill-protocol.md
- [x] git rm -r the 35 sub-skill dirs
- [x] config/aliases.yaml: 35 entries (deprecated 2026-06-12 → removal 2026-09-12, ADR-0009)
- [x] Repoint live refs: hooks (HOOK.md + run.sh messages), agents/ (9 files), docs/concepts/{ta,da,sc,dh,tq}-module.md + engineering-modules.md + full-engineering-pass.md (NOT docs/design, docs/audit, CATALOG.md, docs/wiki [generated], CHANGELOG)
- [x] Rewrite tests/shape/{ta,da,sc,dh,tq}-module-contract.sh (dispatch-table assertions) + fix tests/unit/{ta,da,sc,dh,tq}-routing.sh Scenario 3 + sc/dh Scenario 9 (grepped deleted files)
- [x] Green: 5 shape + 5 routing + frontmatter-lint-all = rc 0 each, 0 FAIL lines; no commit

### Review (sub-skill collapse)

Modules net SHRANK while absorbing the 35 files: ta -8, da -5, sc -5, dh -6, tq -8 lines
(boilerplate shed > dispatch-table growth; budget allowed +80-120 growth). ~4,420 sub-skill
lines deleted. Load-bearing uniques preserved in tables/subsections: all numeric raise-help
thresholds (≥3 consumers, 100k rows, 365d retention conflict, $10k/mo, 99% SLO floor,
critical-path 100%, flake threshold 3 / 14d cap), validation checklists, per-language tool
maps, verdict taxonomies. Hidden dependency found + fixed: tests/unit routing Scenario 3 (all
5) and sc/dh Scenario 9 grepped the deleted files. docs/wiki/skills.md + CATALOG.md left for
their generators. Known drift (pre-existing): docs/concepts/ta-module.md still lists
CodeReviewer for complexity-audit though the workflow never spawned it; module table now says
Architect only (matches reality).

# todo — v5.0 claude-home + memory v2 + Obsidian (2026-06-12)

## Initiative 2 — P0 activation pass (2026-06-12, operator: "kör")

- [x] hooks/hooks.json — plugin auto-registration (digest + 4 safety + memory-budget-warn), exec form, schema verified against official docs
- [x] session-digest.settings.json path fixed (missing shared/) + repositioned as non-plugin fallback
- [x] install.sh seeds profile.yaml + packs/active-pack (identity stated, not fallen back to)
- [x] li-doctor: hook-drift check + auto-registration check + digest wired-via detection
- [x] shims de-staled (AGENTS tasks/todo, copilot tasks/memory) · all 6 manifests → 5.0.0
- [x] lib/state.sh: state_append/state_last — ledger costs one command; 11 skills wired (9 phases + cycle + resume)
- [x] tests/integration/session-leaves-traces.sh — 31 behavior assertions (digest fires + audit record, ledger roundtrip + footer, budget hook, hooks.json valid + scripts 100755) — caught all 31 hook scripts at 100644 (fixed in index)
- [x] prod audit pollution cleaned (capture.jsonl, backup kept)
- [x] ADR-0008 + M1 entry + migration row (manual-entries dedup guidance)
- [ ] Operator: update plugin, remove 4 manual hook entries from ~/.claude/settings.json, re-run install.sh, verify with li-doctor


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

## v5.2 gstack de-heritage — ADR-0011 (branch feat/v5.2-battletest)

Classes A (attribution rewrites) / B (live coupling repairs) / B12 (REVIEW REPORT dual-accept).
Reserved files (capture/context-save/-restore/resume/define/sense/plan/cycle SKILLs, bin/li-scaffold,
bin/_audit.sh, lib/state.sh, secret/customer hooks, _patterns.sh, _input.sh) are NOT touched.

- [x] A: office-hours:15 sibling sentence; open-managed-browser:4 v1_alias + :16 rationale; plan-{ceo,design,devex,eng}-review:16 own-purpose; bin/li-review-log header; bin/li-lessons-sync:3; 8x (legacy alias) deletes; agent-dispatch-rules:106; planner-as-module:55; scaffolding README:23; landing-report:58; DocWriter:55-56; scaffold-internal-tool:66/68/74/109; profile-switch:23/24
- [x] B: autoplan:36/54 + 5 plan-review project paths gstack->lintel; clean:46/66/127 context_latest; plan-tune:140-141 delete; li-review-read one-time import (via audit_log, idempotent — tested); frontend-design-surface migrate disable-file; upstream-sources demote; layer-config disable; tests gstack-binaries-required tag removal (no test carries it)
- [x] B12: heading rename writers (plan-eng-review:82, office-hours:104, autoplan:42) + dual-accept gate (plan-eng-review:116, grace 2026-09-12) + prose refs
- [x] Validate: grep -i gstack over edited files (remaining hits all intentional); frontmatter-lint-all.sh rc=0 + no-swedish.sh rc=0; full shape suite green; audit-writes-via-helper rc=0

### Review (gstack de-heritage)
44 edits across 30 files. li-review-read import reworked to route through audit_log() after
audit-writes-via-helper.sh caught a raw-append contract violation (the only test I broke; now green).
One deviation flagged for operator: plan-design-review:75 external gstack `design` binary — NOT in the
ADR row list, already guarded/optional/off the required path; left intact pending decision.
