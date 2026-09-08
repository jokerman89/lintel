# Work index — current initiative and historical plans

## Copilot enterprise launch — 2026-09-08

Active initiative: [plan and build cards](copilot-enterprise-launch/plan.md), [spec](copilot-enterprise-launch/spec.md), [handoff](copilot-enterprise-launch/prompt.md). Branch: codex/copilot-enterprise-launch. Operator authorized execution through main integration. See initiative plan for live progress and review evidence.

Active committed work map: [copilot-enterprise-launch/work.json](copilot-enterprise-launch/work.json).

## Historical plans — superseded as current work

The entries below preserve earlier decisions and execution history. Their headings, unchecked
boxes and old operator authorizations are historical snapshots, not current assignments or
standing permission. In particular, do not repeat old force-push, history-rewrite, tag, release
or PR operations. Inspect the current initiative above and actual Git/GitHub state first.
Only a current operator request can reactivate a historical task with the necessary authority.

---

## Beta release — public docs + history sanitation (2026-08-28, cycle beta-release-docs, branch feat/launch-readiness)

Mode meta-infra (M1/M3/M4). Ground truth @ this run: **125 skills · 69 agents · 33 hooks ·
90 tests (36 shape / 48 unit / 4 integration / 1 behavior / 1 e2e) · 1 pack · 21 bin · 8 CLIs**.
Operator decisions at the DEFINE gate: (1) rewrite all 250 commit messages in place,
(2) move internal engineering artifacts out of the public tree into `.claude/`,
(3) release as **v0.9.0-beta**.

### W1 — cut the L-023 trap, then relocate internal docs
- [x] W1.1 Inventory every live reference into `.claude/engineering/audits/`, `docs/v4.x/` (28 known callsites)
- [x] W1.2 Repoint `tests/shape/uniformity-coverage.sh` + `tests/shape/no-swedish.sh` to new paths
- [x] W1.3 Repoint `skills/uniformity/SKILL.md`, `lib/auto-decide.sh`, `lib/state.sh`
- [x] W1.4 Repoint 9 ADRs + `.claude/memory/*` + `CHANGELOG.md` + 3 `docs/concepts/*`
- [x] W1.5 `git mv .claude/engineering/audits/` (28) → `.claude/audit/`
- [x] W1.6 `git mv .claude/engineering/compat-audits/` (13) → `.claude/audit/compat/`
- [x] W1.7 `git mv .claude/engineering/evolution/` (22) → `.claude/evolution/`
- [x] W1.8 `git mv` superseded design docs (v2/v3/v3.5/v3.6/v3.7/v4.0) → `.claude/design/archive/`
- [x] W1.9 Retire `.claude/engineering/audits/lintel-state-of-the-harness.md` (v4.9 internal audit, stale counts) → `.claude/audit/`
- [x] W1.10 Shape suite green (36/36) — proof the relocation broke nothing

### W2 — the landing page + the documentation tree
- [x] W2.1 Rewrite `README.md` — hero, thesis, 60-second install, the cycle showcased, honest tables, nav tree
- [x] W2.2 New `docs/README.md` — the documentation index (the tree of connections)
- [x] W2.3 New `docs/the-cycle.md` — the 9 phases broken down, gate by gate, with a worked example
- [x] W2.4 New `docs/architecture.md` — public replacement for state-of-the-harness (spine/pack/nav/depth)
- [x] W2.5 Refresh `docs/getting-started.md` — counts, paths, beta framing
- [x] W2.6 Refresh `docs/multi-cli.md` + `docs/faq.md` + `docs/power-user.md` + `docs/GLOSSARY.md`
- [x] W2.7 Fix `docs/showcase/README.md` (83→69 agents, remove Swedish "Fas D", L-001 internalese)
- [x] W2.8 Sweep every relative link in the public tree; zero dead links
- [x] W2.9 Refresh `CONTRIBUTING.md` + `SECURITY.md` + `CODE_OF_CONDUCT.md` for a public beta

### W3 — commit-history sanitation (one-way door; force-push is operator-authorized)
- [x] W3.1 Export all 250 messages to a working file; snapshot `git rev-parse --all` for rollback
- [x] W3.2 Tag `archive/pre-beta-history` on current main as an escape hatch
- [x] W3.3 Build the rewrite map: mechanical strip of the AI-authorship trailer lines
- [x] W3.4 Hand-author replacement subjects for the 41 flagged commits (Swedish, veto/dirigering, gstack/JStack, company-identity markers, "weapon")
- [x] W3.5 Sweep bodies for `Per operator directive`, `operator-veto`, review-scoreboards
- [x] W3.6 Apply with `git filter-branch --msg-filter` over `--all`
- [x] W3.7 VERIFY: `git diff <old-head> <new-head>` must be EMPTY (content byte-identical)
- [x] W3.8 VERIFY: re-scan rewritten history for every marker class; zero hits
- [ ] W3.9 GATE — operator force-pushes `main` (or authorizes it explicitly)

### W4 — release mechanics
- [x] W4.1 Version → 0.9.0 across `.claude-plugin/plugin.json` + all per-CLI manifests + `gemini-extension.json`
- [x] W4.2 CHANGELOG restart: `v0.9.0-beta` section + v3–v5 history compressed to one "Pre-beta" block
- [x] W4.3 Regenerate `skills/CATALOG.md`
- [x] W4.4 M1 structure-change entry for the docs relocation
- [x] W4.5 Full suite green (90 tests) + `li-doctor`
- [x] W4.6 Tag `v0.9.0-beta`
- [x] W4.7 CAPTURE — lessons, M4 future-operator recap, working-state

### Review

Done: 33 of 34 tasks. The one open item is W3.9 — the force-push — which was never mine to run.

**What the plan did not anticipate.** Three things the recon found that the plan had no task for:
- Generator WRITE paths into the directories being moved (`bin/li-uniformity`, `bin/li-compat-audit`
  from two branches). The plan only listed readers. Recorded as L-024.
- `skills/ship/SKILL.md` instructing every future PR to carry an AI-authorship trailer. Cleaning the
  history without this would have been undone by the next ship. Recorded as L-025.
- `.gitignore` silently untracking `.claude/plans/` — found by a subagent auditing a claim in a doc
  it was rewriting, not by any planned check.

**What cost the most time.** A naive repo-wide sed (17 patterns x ~1400 files) timed out at two
minutes on Windows Git Bash; grep-then-sed ran in seconds. And two test suites ran concurrently for
a while before I noticed I was reproducing L-022 myself.

**Scope grew, correctly.** The widened English-only guard surfaced 87 hits in directories the guard
had never scanned. Cleaning them was not in the plan but was clearly in the spirit of the request.

---


## Launch readiness — PUBLIC launch (2026-06-18, cycle launch-readiness, branch feat/launch-readiness)

Mode meta-infra (M1–M4). Inventory @ v5.7.1: 125 skills, 69 agents, 33 hooks, 14 lib, 21 bin,
25 ADRs, 93 tests. Goal: audit everything, learn from comparable repos (obra/superpowers,
github/spec-kit, GSD/gstack), enhance depth/quality, apply subtraction to the command surface,
bring all publishing (README/guides/help/wiki/marketplace) current. Extends — does not replace —
the v5.x register at .claude/engineering/audits/2026-06-12-launch-readiness-register.md.

- [x] SENSE — inventory captured; on feat/launch-readiness; cycle ledger written
- [x] DISCOVER — 10-agent read-only fan-out complete (A1–A8 internal + B1–B2 external)
- [x] DEFINE — register v2 written: .claude/engineering/audits/2026-06-18-launch-readiness-register-v2.md
- [ ] GATE — 3 strategic decisions + build authorization (awaiting operator)
- [ ] PLAN/BUILD — waves W1–W7 (W1-W4,W7 mechanical; W5-W6 scoped by gate)
- [ ] PLAN — prioritized fix waves
- [ ] BUILD — execute waves (operator gate before)
- [ ] REVIEW — M2 compat audit + M3 shape tests + independent review (L-007)
- [ ] SHIP — PR to main · CAPTURE — lessons + migrations index (M4)

---

## Launch readiness — v5.x old-school ready (2026-06-12/13, cycle launch-readiness-20260612)

Register: .claude/engineering/audits/2026-06-12-launch-readiness-register.md (bar §1, evidence §2, blockers §3-A,
dated deferrals §3-B, waves §4). Mode meta-infra, --auto, founder gate at PLAN. Single-writer:
the dead v5.3 session must not be resumed while BUILD runs.

- [ ] Wave 0 — land 713388d (I1 hooks + 2 test files + auto-decide) + propagate manifest deletion
      (plugin-manifests-valid, verify.sh:330, manifest-identity, SHIP-GATE:20, README:27, cli-tiers)
      + ADR-0013 + truthful CHANGELOG 5.3.0 + atomic commits + suite green on COMMITTED tree (L-010)
- [ ] Wave 1 — security: flatten-CMD fix in both BLOCK hooks + negative tests (line-continuation,
      multiline override); git diff --no-ext-diff --no-textconv; push-path outgoing scan; read -t
      integer fallback; audit-on-fail-closed exit
- [ ] Wave 2 — footer/state class: state_cycle_segment in lib/state.sh; footer consumes; audit_log
      cycle_id from ledger; resume last-match + CYCLE writes branch/commit; multi-cycle regression tests
- [ ] Wave 3 — Windows/portability: install.ps1 (seed + lib/bin copy + shared/ layout + validation);
      li-doctor bash-3.2 + stale path; verify.sh mapfile + coherence repoint + cli-matrix; lintel@→li@ ×4;
      Cursor demote; fingerprint↔tiers map; .opencode/INSTALL.md rewrite (company-pack leak); exec bits; GEMINI slug
- [ ] Wave 4 — docs truth: README/getting-started/AGENTS/GEMINI/shims/AGENT-INSTRUCTIONS/state-of-
      the-harness/multi-cli/LAYERS/compliance sweep; dormancy qualifiers; Swedish ×3 + no-swedish scope;
      CATALOG UTF-8 generator fix
- [ ] Wave 5 — mechanism honesty: usage-log demote; cycle-runs via audit_log; granularity one-truth;
      jobs claims demoted; 7 compliance streams → audit_log or cut; 6 bespoke >> writers → helper;
      pack-resolver cache key + set -u leak; _audit.sh/state.sh hardening; li-doctor smoke +
      customer-data-block/warn-hook execution tests
- [ ] Wave 6 — release close: Upgrading & uninstalling section; migration-index dates reconciled;
      working-state/MEMORY/TODOS-v2 hygiene; scaffolding tasks/ leftovers; M1 + M2 + M4 gate artifacts
- [ ] Wave 7 — independent review (L-007, real diff) → act on findings → ship gate → PR to main

ADR-0014 (prompt craft v2) + ADR-0012 (agent memory/model). House-style: docs/concepts/prompt-house-style.md "Writing agents".
Goal: beat wshobson/VoltAgent on craft by adding JUDGMENT (Core principles + Behavioral traits + trigger-form descriptions) to ~20 review/audit/architecture agents. Tight — judgment not bloat, ~10-15 net lines each.

Per agent (where missing): (1) trigger `description:` ending `Use proactively when …`/`Use after …`; (2) Core principles 2-4 lines after persona; (3) `## Behavioral traits` 5-8 bullets; (4) tool-scoping one-liner where read-only by contract; (5) memory:project agents → one trait recalls this repo's prior findings. Dial back ALL-CAPS (rule + why). Keep all existing frontmatter + sections.

engineering:
- [x] CodeReviewer (memory) · [x] Architect (Write) · [x] Refactorer (Edit) · [x] DebugForensics (memory) · [x] RegressionDetective (memory) · [x] SanityChecker (memory, ro) · [x] TestRunner (memory, ro) · [x] Explorer (mechanical — LIGHT) · [x] Planner (ro) · [x] SystemArchitect (ro, module) · [x] DatabaseDesigner (Write) · [x] APIDesigner (Write)

security:
- [x] SecurityAuditor (memory, ro) · [x] ThreatModelDrafter (memory) · [x] DependencyAuditor (memory, ro) · [x] JWTSecurityReviewer (memory, ro) · [x] OAuthFlowReviewer (memory, ro)

compliance:
- [x] GDPRReviewer (memory, ro) · [x] SOC2Reviewer (memory, ro) · [x] EUAIActReviewer (memory, ro)

validate:
- [x] frontmatter-lint-all.sh rc=0 · no-swedish.sh rc=0 · agents-categorized.sh rc=0 (all PASS, 0 FAIL lines)

### Review (v5.3 craft raise)
20 agents got Core principles + `## Behavioral traits` + a trigger-form `Use proactively when/before/after …`
clause + a one-line tool-scoping rationale. Deltas +14..+17 each (net ~+15) — inside the "judgment not
bloat" budget. The 10 `memory: project` agents each carry one trait that recalls this repo's prior findings
(the differentiator vs wshobson/VoltAgent). No ALL-CAPS imperative introduced in any added line; existing
STOP/BLOCK in untouched edge-case sections left intact per "keep all existing sections". Explorer got LIGHT
treatment (mechanical, model: haiku, no memory — 4-bullet traits, no repo-memory trait). SystemArchitect
adapted to its non-standard shape (Core principles after persona, traits before Output-shape, tool line by
Voice). Tool-scoping lines distinguish read-only reviewers (no Edit/Write) from the Write/Edit design+migration
agents (Architect/DatabaseDesigner/APIDesigner/Refactorer — scoped to artifacts, not live source/DB).
## v5.4 design DNA — consume UI/UX Pro Max + anthropic-default profile (2026-06-13, branch feat/v5.4-design-dna)

Design: .claude/engineering/design-archive/lintel-v5.4-design-dna-design.md (ADR-0015 + ADR-0016). Mode: meta-infra (M1-M4).
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

Source: .claude/engineering/audits/2026-06-12-battletest-synthesis.md (JAB rows) + noob first-hour findings.
SCOPE: README.md, docs/getting-started.md, skills/welcome/SKILL.md, CLAUDE.md, install/install.sh, NEW docs/GLOSSARY.md ONLY. Do NOT touch other skills/ or agents/.

- [x] J1 — canonical hook-activation matrix added to getting-started ("How hook activation works", ADR-0008). README:5, welcome Step 4, install.sh header all point at it. No "inert" without "(bare install only)"; no "zero-setup" without "(plugin install)" — verified by grep.
- [x] J2 — "168 skills" de-hardcoded in welcome (frontmatter + body) → "the full skill set". README/getting-started counts already 124/69 (correct); getting-started finding-skills section de-hardcodes (compute at runtime).
- [x] J3 — CLAUDE.md:31 stale `adr/` listing → points at .claude/decisions/ + names docs/adr as redirect stub. 4-root "Where things live" map added to README + getting-started. (CLAUDE.md state map + ritual were already v5-correct — confirmed, not manufactured.)
- [x] J4 — getting-started "Finding skills" section: /li:help + /li:catalog + 7-bucket prose purpose-grouping.
- [x] J5 — install.sh: /tier-stamp-agents line removed; pack-specific compliance/identity dir mkdirs removed (pack concern); header honest about upstream stub (lists, does not clone); upstream-step message says "listed only". README+getting-started got the "Windows: install\install.ps1" line.
- [x] J6 — docs/GLOSSARY.md created (12 terms, one screen); linked from README first section + getting-started top; "the 9-step cycle: 8 core phases + SCOPE" phrasing used consistently.
- [x] VALIDATE — grep clean (no 168 / inert always qualified / no stale docs/adr mis-pointers); no-swedish.sh RC=0.

### Review (J1-J6)

Six fixes landed across 5 files + 1 new (GLOSSARY). Canonical hook matrix lives ONCE at
docs/getting-started.md#how-hook-activation-works; README/welcome/install.sh all point at it
rather than restating. Found the branch's CLAUDE.md was already largely v5-correct (state map +
ritual cited .claude/decisions and .claude/runtime/state) — the J3 instruction assumed more drift
than exists; corrected only the one genuinely stale ref (line 31) and did not manufacture changes.
DEVIATION FLAGGED at the time: install.ps1 was not in authorized scope, so the pack-specific
identity directory was surfaced rather than fixed. (Re-checked 2026-08-31: resolved — neither
installer creates it any more.)

## v5.1 subtraction — ADR-0009 sub-skill collapse (2026-06-12, branch feat/v5.1-subtraction)

- [x] 5 modules (ta/da/sc/dh/tq): add `## Sub-capability dispatch` table + short load-bearing subsections; `/li:<module> <capability>` shorthand; direct dispatch in single granularity; shed Pause-points/Hop-in/Voice boilerplate per docs/concepts/skill-protocol.md
- [x] git rm -r the 35 sub-skill dirs
- [x] config/aliases.yaml: 35 entries (deprecated 2026-06-12 → removal 2026-09-12, ADR-0009)
- [x] Repoint live refs: hooks (HOOK.md + run.sh messages), agents/ (9 files), docs/concepts/{ta,da,sc,dh,tq}-module.md + engineering-modules.md + full-engineering-pass.md (NOT docs/design, .claude/engineering/audits, CATALOG.md, docs/wiki [generated], CHANGELOG)
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

## Initiative 2 — P0 activation pass (2026-06-12)

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


Design: [.claude/engineering/design-archive/lintel-v5-claude-home-memory-obsidian-design.md](../.claude/engineering/design-archive/lintel-v5-claude-home-memory-obsidian-design.md)
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
