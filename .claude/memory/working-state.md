# Memory — Lintel working-state

Cross-session working state (ej durable rules — that's [[lessons.md]]; ej persona-frames — that's
[[personas.md]]). Surface at session-start so operatorn ser var arbetet pausade.

> Format per entry: short title, then `Status:`, then `What's pending:`. Update at session-end
> or at major checkpoints. Stale entries (>30 days) bör städas.

---

## CURRENT — independent enterprise value review (2026-09-08)

**Status:** delivered as [draft PR #84](https://github.com/jokerman89/lintel/pull/84)
from `codex/enterprise-value-review`,
inspected at `6b10a84`, in `.claude/worktrees/enterprise-value-review`. For publication, only
the review commits were rebased onto main `9a024c0`; the implementation is unchanged.
The concurrent `codex/copilot-enterprise-launch` checkout
was read only; do not overwrite or merge its uncommitted work from this task.

The operator chose hybrid planning: short leaves, coherent package execution/review,
per-leaf acceptance and evidence (ADR-0026). Pack inheritance, list/nested extraction,
validation, risk routing and loaded identity are corrected. PLAN links applicable company
requirements to existing work IDs and verification. No private profile or installation changed.

**Evidence:** aggregate 93/93 scripts passed before final parser/cache repairs; final focused
results are in `.claude/engineering/audits/2026-09-08-enterprise-value-review.md`. Independent
pack and hybrid scenario reviewers closed their findings. No measured productivity claim or
verified universal hook enforcement follows from these checks.

**What's pending:** the operator explicitly approved the documented M2 exception for
feature-branch push and draft-PR publication on 2026-09-08. The mechanical RED remains.
Eight targeted scripts passed after the rebase; CI and integration review remain in the draft PR.
Publication evidence is recorded in the review report. Two baseline P1 Git
collection defects (F05/F06) remain release-control blockers; prioritize them before an
enterprise rollout. Older onboarding/installation/work-selection work overlaps the other task.

**Next action:** PR #83 merged into main during publication; GitHub reports conflicts
for draft PR #84. Reconcile overlapping files and release versions, reassess baseline
findings against those Copilot fixes, then run verification on the combined tree.
No direct main push, deployment or personal setup is authorized.

## Prior release context (reconciled 2026-08-28)

**Beta release (2026-08-28, branch `feat/launch-readiness`, cycle `beta-release-docs`, mode meta-infra):**
the repo is prepared for its FIRST PUBLIC RELEASE as **v0.9.0-beta**. Five commits on top of the
launch-readiness work, then a full commit-message rewrite. Suite 90/90 (shape 36, unit 48,
integration 4, behavior 1, e2e 1). **NOT pushed.**

What landed:
- **Published/internal split.** `docs/` is now the adopter surface only (130 → 44 files); audits,
  Gate M1/M2 records and superseded design docs moved to `.claude/engineering/`. All 233 inbound
  references repointed — including two CI-gating resolvers and three generator WRITE paths that
  would have recreated the public dirs (see [[L-024]], the half [[L-023]] missed).
- **Documentation rebuilt.** New `docs/README.md`, `docs/architecture.md`, `docs/the-cycle.md`;
  README reframed as a landing page; 8 docs rewritten against verified ground truth; 74 stale claims
  corrected; `LAYERS.md`, `docs/session-harness.md` retired and `SHIP-GATE.md` moved internal;
  `docs/promoted-agents.md` deleted (described a vendoring mechanism the installer does not have).
  257 links resolve, zero broken.
- **Two real bugs, not doc bugs.** `.gitignore` was ignoring `.claude/plans/`, so every new plan and
  trio was silently untracked. `skills/ship/SKILL.md` instructed every PR to carry an AI-authorship
  trailer — the source of the leak, not just the symptom ([[L-025]]).
- **History rewritten.** All 255 commits across 5 branches: AI-authorship trailers stripped, 144
  messages hand-rewritten (Swedish, operator-direction phrasing, review scoreboards, heritage
  references). Proven safe: trees byte-identical, `git diff` old↔new HEAD empty, commit counts
  preserved, zero leaks in six classes. Old heads in `refs/original/`; full pre-rewrite history in
  `../lintel-pre-beta-history.bundle` (verified complete).

**Tag hazard: CLEARED (2026-08-28).** The four `v3.*-dev` tags and the two `archive/*` tags all
pointed at pre-rewrite commits and would have republished the leaky messages on a `--tags` upload.
All six are deleted. Only `v0.9.0-beta` remains, on the rewritten HEAD. The complete pre-rewrite
history is safe in `../lintel-pre-beta-history.bundle` (verified), which cannot be uploaded by accident.

**Remote auth: FINE.** Active `gh` account is `azureflipper` with `repo` + `workflow` scopes; the
remote is reachable. The earlier note about the wrong account was stale.

**SHIPPED (2026-08-29).** `origin/main` now carries the rewritten history at `ce8665d`, and
`feat/launch-readiness` is up at `442b8ef`. **PR #82** is open: v0.9.0-beta — first public release.

Verified on the remote after the upload, not just locally:
- `origin/main` — 234 commits, **zero** leaks across all six classes
- `origin/feat/launch-readiness` — 257 commits, **zero** leaks
- `origin/main` tree is `6daac65d…`, byte-identical to the pre-rewrite tree. Messages changed;
  content did not.

Still to do: merge PR #82, then upload the `v0.9.0-beta` tag (it points at `442b8ef` on the branch,
so a squash-merge would leave it off `main` — upload it after the merge, or re-tag the merge commit).

**Do not upload `docs-lintel-report`** (separate worktree at `E:/Workspace/lintel-report`). It was
deliberately left un-rewritten and still holds pre-rewrite commits; `origin` already has an old copy
at `3bc8e47`.

**Deferred, deliberately:** the `tasks/` root stubs stay until their documented 2026-09-12 window
closes. `.claude/engineering/SHIP-GATE.md` moved internal but its gates are still largely broken —
worth a rewrite, tracked as its own job. Version drops 5.8.0 → 0.9.0, so a marketplace install needs
uninstall/reinstall rather than an update.

---

<!--
## entry-id — short title

**Status:** active / paused / blocked / completed

**What's pending:**
- <pending item 1>
- <pending item 2>

**Last touched:** YYYY-MM-DD
-->

## launch-readiness — v5.x "old-school ready", folded into PR #73 2026-06-13

**Status:** active — merged into `feat/v5.3-cli-and-craft` (PR #73), suite 82/82 on the merged tree.

**What this drive added (waves 3–7, on top of the v5.3-cli-and-craft work below):** an 8-audit
launch-readiness register (.claude/engineering/audits/2026-06-12-launch-readiness-register.md — bar §1, evidence §2,
blockers §3-A, dated deferrals §3-B, waves §4) + the remediation it found.
- **Security (ADR-0013):** newline-class gate bypasses closed (line-continuation matcher evasion +
  newline-forged `-m` override — L-012 class), each with an adversarial test; gate diffs textconv-safe;
  push scans the outgoing range; macOS bash-3.2 `read -t` fallback. (Converged with the other session's
  fail-closed positioning in the merge.)
- **State (register B4):** `state_cycle_segment` — the footer/resume/`cycle_id` were poisoned by
  prior-cycle entries in the append-only ledger; now scoped to the current cycle. Multi-cycle + loop-back
  regression tests.
- **Windows/portability (B5):** install.ps1 full parity (seed identity + lib/bin copy + shared/ hooks);
  li-doctor bash-3.2-safe; `.opencode/INSTALL.md` rewritten neutral; `lintel@`→`li@` everywhere;
  fingerprint↔tiers id-normalization; exec bits.
- **Docs truth (B6):** ~30 files swept (v3-plan/`tasks/`/`docs/adr`/gstack/v5.0 residue); dormancy
  qualifiers; no-swedish now covers docs+README; CATALOG generator char-safe (flake fixed).
- **Mechanism honesty (B7):** usage-log/telemetry/compliance prose → real `audit_log`; pack-resolver
  set-leak + cache-key fixes; 4 new behaviour tests.
- **Release (B8):** truthful CHANGELOG 5.3.0, migration date reconcile, M1 artifact
  (.claude/engineering/evolution/2026-06-13-launch-readiness.md). CODEOWNERS de-CAIP'd.

**What's pending:**
- Operator: merge PR #73 → main (the git-push-to-main gate stays yours).
- Public-launch-tier items remain DATED-not-blocking in the register §3-B: real git pre-commit/pre-push
  install (by 2026-07-15, supersedes the command-string matcher), ADR-0019 AGENTS.md-primary, ADR-0020
  MCP, ADR-0021 eval-harness, H17/H18, marketplace (post legal). v6 shrink-to-kernel decided after the eval.
- `gh` couldn't auth to jokerman89/lintel from the build session — PR view/merge is operator-side.

**Last touched:** 2026-06-13

## v5.3-cli-and-craft — PR #73 OPEN 2026-06-13

**Status:** active — PR #73 to main (independent; #69 already merged). launch-waves wave folded in.

**What shipped (one meta-infra cycle, three operator workstreams):**
- **Multi-CLI (subtraction):** deleted the two fabricated manifests (.copilot-plugin, .droid-plugin
  — both ride .claude-plugin via interop); fixed cli-tiers.yaml (codex.subagents native, Copilot
  install li@, Cursor stays tier full); repointed instruction-parity-check off 3 ghost files;
  README CLI-TIERS table regenerated; li-doctor gained a Windows SessionStart-no-fire warn (#59072).
- **Issue-mining → fixes:** .claude/engineering/audits/2026-06-13-cli-issues-craft-synthesis.md (16 findings).
  CRITICAL I1 — both BLOCK hooks ran `set -euo pipefail` with the blocking exit 2 LAST, so an
  upstream non-zero exited first and silently downgraded the block (claude-code #60490). Fixed:
  `set -uo pipefail` + a fail-closed scanner guard positioned after matcher+override + a behavioral
  regression test driving the real hook with a scanner-less stub. I3 — lib/auto-decide.sh mechanical
  one-way-door keyword guard + unit test.
- **Prompt craft v2 (ADR-0014):** docs/concepts/prompt-house-style.md — description-as-trigger (not
  workflow summary) + dial-back ALL-CAPS imperatives (current models overtrigger; Anthropic yellow
  flag). 42 skill descriptions rewritten to trigger form; 20 agents gained Core-principles +
  Behavioral-traits + tool-scoping rationale. New tests/shape/skill-descriptions-trigger.sh ratchet.

**Honesty notes (in ADR-0014):** auto-decide is a real unit-tested function the cycle is TOLD to
call, not yet a mechanical gate on the --auto path; the trigger-guard enforces opening-verb +
no-archaeology, not trigger SUBSTANCE. Both staged with the eval-harness.

**Suite:** 79/79. Reviewed by independent CodeReviewer (L-007): 1 P1 (PLAN trio gate undefined
$slug → L-014) + 2 P2 + 6 P3, all acted on. Captured **L-013** (make-it-ours = reinvent, not
de-heritage) + **L-014** (no unbound vars in illustrative skill bash — recurred from v5.2).

**Folded in (merge 02e916e, per "don't discard anything"):** the launch-waves wave forked from
0042312 in parallel and had unique COMMITTED work this branch lacked — **ADR-0013** (fail-closed
block gates, fills the empty 0013 slot) + **5 security hardenings** (macOS bash-3.2 fail-open
fallback, push outgoing-range scan, --no-ext-diff/--no-textconv textconv-RCE guard, newline-flatten
anti-forgery, audit-on-scanner-unavailable) + the **state-ledger scoping fix** (7ece1f4). Hook
conflict resolved to the override-reachable fail-closed position (after matcher+override) + their
audit/message/CMD_FLAT; security behavior tests prove the union still blocks. Cursor-full revert
auto-merged to a no-op. Suite 79/79 on the merged tree.

**What's pending:**
- Merge PR #73 to main.
- OPERATOR DECISION (unchanged): the `worktree-launch-waves` worktree still holds a **58-file
  UNCOMMITTED craft-sweep WIP** (+690/−464: ~16 skills, a new tests/shape/no-swedish.sh, AGENTS/
  CLAUDE/README/li-doctor). A merge can't capture uncommitted work — preserved untouched, fragile.
  Decide: commit-on-branch (durable) or fold into a follow-up cycle. NOT discarded.
- STAGED (own ADRs already written): AGENTS.md-primary (ADR-0019), lintel-state MCP server
  (ADR-0020), eval-harness (ADR-0021), per-CLI command-stub generator, field-wide
  description-trigger + aggressive-language sweep of the remaining ~80 skills.
## v5.4-design-dna — PR OPEN 2026-06-13

**Status:** active — branch feat/v5.4-design-dna (worktree E:\Workspace\_wt-design-dna), rebased on main@5.2.1

**What shipped:** ADR-0015 (consume nextlevelbuilder/ui-ux-pro-max-skill v2.5.0, MIT — corpus of
84 styles, 161 palettes, 161 reasoning rules, 73 font pairings, 99 UX rules, 16 stack files + BM25
stdlib search; explicit L-001 exception: third-party reference data) + ADR-0016 (anthropic-default
design profile — 7 canonical tokens + Poppins/Lora, Apache-2.0 attributed, derived gap-fills
source-marked; pack seam `design.profile`, contract untouched). New module skill
`skills/design-dna/` (search|system|stack|persist|validate|profile) + `validate_design.py` hard
gate; retrieval wired into frontend-design (required Step 1.5), typography/motion, generate-web/app
(Gate 0), both review skills; doctrine into 4 frontend agents. 3 new tests; L-007 independent
review SHIP-WITH-FIXES — P0 (emoji false-positive on arrows) + 4 P1 all fixed + 4 negative
regression assertions (L-012). M2 GREEN. Manifests 5.4.0.

**What's pending:**
- Merge PR; CATALOG regen is automatic on main push
- Known pre-existing red: tests/shape/skill-descriptions-trigger.sh fails 43x on clean main
  (owned by the in-flight v5.3 craft branch) — zero failures reference v5.4 files
- Follow-ups parked: slide decision-engine (emotion-to-layout CSVs) for generate-ppt; upstream
  corpus re-sync per ATTRIBUTION.md; pack-schema-level `design.profile` validation if a second
  profile consumer appears

**Last touched:** 2026-06-13

---

## v5.2-battletest — PR #69 OPEN 2026-06-12

**Status:** active — PR #69 to main (independent chain; #62-#68 already merged)

**What shipped:** 6-persona adversarial battletest (.claude/engineering/audits/2026-06-12-battletest-synthesis.md,
6 KO + 24 HARD). ADR-0010 security (block-hook bypass + modern tokens + vault PII scan + sed RCE
+ CR/LF-safe audit/state), ADR-0011 gstack de-heritage (44 edits/30 files, zero loss, grace
2026-09-12), ADR-0012 agent memory:/model: (23+4). Friction: resume↔context-restore, honest cost
gates, DEFINE feature fast-path, SENSE marker-gate. New behavior tests caught 3 real bugs incl. a
P0 forgeable-override I introduced (L-012). Suite 76/76. Manifests 5.2.0.

**What's pending:**
- Merge #69 to main; then verify li-doctor proof-of-life on a fresh session
- STAGED (own ADRs): eval-harness (H1/H5 — the measurement every persona demanded), BUILD
  parallelism (H9), module-YAML enforcement (H10), MCP server (H11), AGENTS.md portability
  collapse (H13), pack provenance (H17), plugin pinning (H18), real git pre-commit/pre-push
  install (supersedes ADR-0010 command-string match), v6 shrink-to-kernel positioning
- The strategic verdict (competitor + grumpy): moat = pack contract + corpus, not the 124 skills;
  direction is shrink-to-kernel + packs-as-product + AGENTS.md, decided AFTER the eval exists

**Last touched:** 2026-06-12

---

## v5.1-subtraction — PR #67 MERGED 2026-06-12

**Status:** active — chain now #62→#63→#64→#65→#66→#67

**What shipped:** ADR-0009 — skill-protocol.md (defaults stated once), 35 sub-skills →
5 dispatch tables, roles 8→3, gbrain + WorkshopFacilitator pruned, 41 aliases.
166→124 skills, 27.0k→20.8k lines (−23%), suite 75/75. Review: zero lost thresholds.
L-011 captured (structural estimates are ceilings).

**Last touched:** 2026-06-12

---

## v5.0-claude-home — three stacked PRs OPEN 2026-06-12

**Status:** active — awaiting PR merges

**What shipped (one session, full cycle SENSE→CAPTURE):**
- **D1–D4 locked** by operator: knowledge committed/runtime ignored · everything Lintel-owned → `.claude/` · native auto-memory converged · 4 Obsidian patterns
- **PR #62** vault sink (rebased clean; neutral-pack default OFF after review)
- **PR #63** v5 `.claude/` home (ADR-0005): lib/paths.sh, scope-routed audit/jobs + cross-repo registry, li-migrate-claude-home, ~210-file sweep, dogfooded on this repo
- **PR #64** memory v2 (ADR-0006): lib/memory.sh + bin/_context.sh + memory-budget-warn hook, update-phase + supersede convention, context family 8→3 (aliases), AGENTS.md + rules emission, subtractions (operator-profile, gbrain over-claims)
- **PR #65** Obsidian patterns (ADR-0007): locked schema, sessions.base + li-vault-init, hub/predecessor wikilinks, 00-index
- All three phases passed independent L-007 review (SHIP-WITH-FIXES; every P1/P2 acted on)

**What's pending:**
- ALSO open: **PR #66** (activation pass, ADR-0008) — stacked on #65. Fit audit
  (.claude/engineering/audits/2026-06-12-fable5-fit-audit.md) found ~3/14 mechanisms firing; #66 ships plugin
  hook auto-registration + state ledger (lib/state.sh) + behavior tests + the exit-2 fix for
  the block hooks (they never actually blocked). After merge: verify li-doctor proof-of-life
  on first fresh session (digest audit record must appear).
- Merge chain: #62 → #63 (re-target to main) → #64 → #65
- Operator: run `li-migrate-claude-home` on other Lintel-connected repos (grace to 2026-09-12)
- Operator: re-enable vault sink in a personal pack override (~/.lintel/packs/_default) — the shipped neutral default is now OFF
- Follow-ups parked: marker-parse consolidation (5 copies → paths.sh), basic-memory-style index if grep ever scales out

**Last touched:** 2026-06-12

---

## v4.0-reframe — design doc DRAFT_FOR_REVIEW 2026-05-29

**Status:** design phase — awaiting operator pass

**Scope:** Master design consolidating 3 operator-supplied FRs + 1 text-form engineering-depth request + 1 meta-process note into 5-chapter reframe of what Lintel IS. Becomes v4.0.

**5 chapters in one architecture:**
1. **Spine + Packs + Navigation** — generic spine, pack-loaded identity, mandatory navigation declarations, orientator at SENSE (honors `lintel-feature-spine-packs-navigation.md`)
2. **Brief Forge + Envelope + Wiki** — universal hand-off gate, standardized payload, generated 1:1 documentation (honors `lintel-feature-brief-forge.md`)
3. **Engineering Depth** — 5 domain modules (tech-architecture · data-architecture · security-compliance · devops-hosting · testing-qa) with full/loop/single granularities, per-module checkpoints + recovery + iteration loops (NEW — interprets operator text-form FR)
4. **Meta-infra Discipline** — `meta-infra` mode envelope + 4 mandatory gates (structure-impact, compatibility-audit, regression-shape-tests, future-operator validation) for harness-on-harness work (NEW — interprets operator meta-process note)
5. **Composition** — ship sequencing, cross-chapter deps, risks, operator validation criteria

**Estimates:** ~17-27 CC-days for v4.0 ship (alpha/beta/rc), ~10-15 CC-days for engineering-depth rollout (v4.1-4.5).

**Open decisions:** 14 numbered (C1-D1 through C5-D2). All recommendations included; operator confirms or vetoes per-line.

**Files:**
- `.claude/engineering/design-archive/lintel-v4.0-reframe-design.md` (master doc)
- `.claude/engineering/design-archive/lintel-feature-spine-packs-navigation.md` (canonical reference)
- `.claude/engineering/design-archive/lintel-feature-brief-forge.md` (canonical reference)

**Last touched:** 2026-05-29

---

## v3.5-close — Generate-pipeline COMPLETE

**Status:** completed

**What's pending:**
- ~~Fas 2: --from-pipeline support~~ ✅ SHIPPED (PR #17)
- ~~Fas 3: generate-style-learn skill~~ ✅ SHIPPED (PR #19)
- v3.6.0-dev + v3.6.1-dev tags pushed (signal milestone instead of v3.5.0-dev)

**Last touched:** 2026-05-28 (v3.5 doc-gen-pipeline COMPLETE)

---

## v3.8-jobs-and-planner — Curated-flow tracking + planner-as-module SHIPPED 2026-05-29

**Status:** ready for merge (PR open)

**What shipped:**
- **Feature 1 (jobs system):** ~/.lintel/jobs/_active.md as single source of truth. 3 hooks (job-begin, job-end, job-stale-warn). 2 skills (`/li:jobs`, `/li:status`). `workflow_root: true` frontmatter flag on cycle + plan. Helper bin/_jobs.sh.
- **Feature 2.1:** plan declares workflow_root: true (spawns its own job when invoked standalone).
- **Feature 2.2:** prompt.md generation moved from CAPTURE to PLAN. Trio (plan.md + spec.md + prompt.md) born together. CAPTURE now reaffirms (annotates with build evidence), doesn't regenerate.
- **Feature 2.3:** granularity hard check in plan-eng-review Step 0 — per-task ≤5min (operator-LOCKED). Tasks >5min trigger decompose-or-accept AskUserQuestion.
- **Feature 2.4:** plan/SKILL.md documents Module-callable section. Three invocation modes documented (inside cycle, standalone, sub-module called by another workflow_root skill). --no-job flag for nested calls.

**Concept docs:** docs/concepts/jobs-system.md + docs/concepts/planner-as-module.md.

**Tests:** tests/unit/jobs-system-present.sh + tests/unit/workflow-root-and-trio.sh. 20/20 PASS local. Behavior smoke: job_create → job_update → job_archive end-to-end verified with audit-log writes.

**Last touched:** 2026-05-29

---

## v3.7-close — Frontend-design family COMPLETE

**Status:** completed

**What's pending:**
- ~~Fas A1: foundation core~~ ✅ SHIPPED (PR #22)
- ~~Fas A2: extension + canonical pattern~~ ✅ SHIPPED (PR #23)
- ~~Fas B: generate-web --from-frontend-design + new generate-app skill (M-2)~~ ✅ SHIPPED (PR #24)
- ~~Fas C: frontend-design-surface hook + vault loop closure~~ ✅ SHIPPED (PR #25)
- v3.7.0-dev tag ✅ pushed 2026-05-29
- **Fas D** (operator-only) — real-engagement dogfood + L-004 canonical-pattern re-evaluation pending

**Stats:** 9 net-new skills + 5 new agents (78→83) + 1 hook + canonical pattern + L-004 lesson durable. M-1/M-2/M-3/M-4/M-5/M-6 + m-1/m-3 all resolved. 17/17 tests pass.

**Last touched:** 2026-05-29 (v3.7.0-dev milestone)

---

## v3.6-cohorts — Backlog execution NEARLY COMPLETE

**Status:** active (Cohort 4 operator-only kvar)

**What's pending:**
- ~~Cohort 1 (truth-fixes + frontmatter-lint + resume-integrity + shellcheck)~~ ✅ MERGED PR #10
- ~~Cohort 2 (observation spine + behavior-test pilot)~~ ✅ MERGED PR #11
- ~~Cohort 3 (design locks per default-recs)~~ ✅ MERGED PR #16
- ~~Cohort 5-partial (operator requests + second wave)~~ ✅ MERGED PR #13
- ~~Cohort 5-expansion (profile-switch + maintenance + entropy)~~ ✅ MERGED PR #18
- ~~Cohort 6 (instruction-parity-check)~~ ✅ MERGED PR #19
- **Cohort 4a (alias-mekanism design pass)** — PR #14 OPEN (intentional, väntar WS-4a/b)
- **Cohort 4 implementation** — depends på operator working-sessions WS-4a (gstack-collisions) + WS-4b (orphan-names)

**Last touched:** 2026-05-28 (~95% v3.6 backlog completed)

---

## reviewer-concerns — Open från tidigare PRs (M-1 tracking per v3.6 backlog)

**Status:** active

**What's pending:**

### PR #7 (lintel-v3.5-doc-generation-plan) — ALL 4 MAJORs RESOLVED (2026-05-29 sweep)

1. ~~**Voice-gate terminology mismatch**~~ ✅ CLOSED. Audit confirmed generate-* family uses `/li:rais-customer-voice-check` consistently (no `TrailblazerVoiceCritic` references in skills/). Terminology unified — design doc had stale name.
2. ~~**4-gate explicit home**~~ ✅ CLOSED. `skills/generate/agent-mapping.yaml` has `voice_gate_owner: orchestrator` + `format_gate_owner: format-builder` explicit. Validated at v3.5 Fas 2 merge (PR #17).
3. ~~**`--keep-runs <N>` YAGNI**~~ ✅ CLOSED. Documented as YAGNI in `skills/generate/SKILL.md` "Deferred flags" section. Operator can request implementation when run-dir size becomes friction.
4. ~~**Voice-blocklist-customer-share-gate interaction**~~ ✅ CLOSED. Full interaction chain documented in `skills/generate/SKILL.md` "Voice-blocklist ↔ customer-share-gate interaction" section: --customer-share → voice-tier=trailblazer-draft → blocklist enforced via OurVoice corpus → rais-customer-voice-check verifies + compliance-gate aggregates.

### PR #9 (lintel-v3.6-backlog-sequencing) — 7 of 7 concerns RESOLVED (2026-05-29 sweep)

MAJORs (#1, #2): coverage matrix shipped inline; 4.1 alias-mekanism CLOSED via PR #14 (design) + PR #27 (implementation 2026-05-29).

MINORs (#3-#7): all CLOSED via cohort-execution paths:
- ~~#3 5.6 distribution targets~~ enumerated at Cohort 1 PR-open (truth-fixes + 6.3+6.4+6.6 went there)
- ~~#4 6.3 resume integrity spec~~ implemented in Cohort 1 PR #10 (resume Step 1.5)
- ~~#5 6.6 shellcheck estimate~~ shipped warn-only in Cohort 1 (PR #10) per recommendation
- ~~#6 L-002 grep-evidence for 4.3~~ context-family pair-by-pair verified in PR #27 WS-4a section (33 collisions enumerated)
- ~~#7 M-3 docs/architecture.md pre-baking~~ link-not-content approach used: docs/architecture.md got L-001/L-002/L-003 (Cohort 1) + L-004 (v3.7 closeout) as durable principles with reference to lessons.md for incident-driven rationale

### PR #21 (lintel-v3.7-frontend-design-system) — 7 of 9 concerns RESOLVED via implementation

Eng-review run 2026-05-28. v3.7 Fas A1+A2+B+C shipped i PR #22-#25, all merged 2026-05-29. Status update för 9 concerns:

**MAJORs — alla 6 RESOLVED:**
1. ~~M-1 design-spec.json schema collision~~ ✅ RESOLVED i PR #21 (filename → `frontend-design-spec.json`) + PR #24 (generate-web reader)
2. ~~M-2 frontend-app-scaffold boundary violation~~ ✅ RESOLVED i PR #21 (renamed till generate-app) + PR #24 (skill shipped i generate-* family)
3. ~~M-3 Fas A monolithic-PR risk~~ ✅ RESOLVED i PR #21 (split till A1 + A2)
4. ~~M-4 sequential sub-skill chain 3× latency~~ ✅ RESOLVED i PR #22 (orchestrator Workflow Step 2-4 parallel-dispatch documented)
5. ~~M-5 schema-versioning missing~~ ✅ RESOLVED i PR #22/#23 (`schema_version: 1` på alla contract JSON)
6. ~~M-6 roundtrip integration test deferred~~ ✅ RESOLVED i PR #22 (`tests/integration/frontend-design-roundtrip.sh`)

**MINORs — 2 of 3 RESOLVED, 1 deferred:**
7. ~~m-1 FrontendArchitect ↔ FrontendBuilder non-overlap~~ ✅ RESOLVED i PR #22 (explicit non-overlap section)
8. **m-2 SKILL.md DRY pattern** — ⏳ DEFERRED. 9 frontend-* + generate-* skills now exist; pattern-anatomy doc not yet authored. Low-priority — drift signal-to-noise är låg så länge antalet är manageable. Address when next family adds.
9. ~~m-3 --overwrite flag inheritance~~ ✅ RESOLVED i PR #23 (frontend-style-extract documents flag)

**Additional concern surfaced post-shipment (#7 perf-budget):** vault-lookup latency budget documented i PR #25 frontend-design-surface hook (<200ms MVP target for vault of 1-3 patterns, scaling-index deferred till vault > 10).

**Status:** PR #21 reviewer-concerns 7-of-9 closed via implementation. Remaining m-2 carries over till next family-design occasion. Entry can close after m-2 addressed or operator dismisses som YAGNI.

**Last touched:** 2026-05-29 (v3.7.0-dev milestone)

---

## operator-only-remaining — Items som kräver operator beyond AI-execution

**Status:** active

**What's pending:**

1. ~~**WS-4a + WS-4b naming-sessions**~~ ✅ AUTO-EXECUTED with operator-veto path 2026-05-29. WS-4a: NO renames (prefix-only disambiguation principle adopted). WS-4b: 4 renames (match→skill-router, setup-brain→gbrain-setup, sync-brain→gbrain-sync, agt-tier-stamp→agent-tier-stamp). Alias-mekanism + bin/_aliases.sh + tests shipped. Operator vetoes any line if disagreement.
2. ~~**6.7 internal-voice consistency check** (D-5a)~~ ✅ INVESTIGATED 2026-05-29 — verdict: INTENDED, not drift. 125 internal / 14 mixed / 2 trailblazer distribution coherent. See [decisions-67-68 doc](.claude/engineering/design-archive/lintel-v3.6-decisions-67-68.md). Operator vetoes by reply "drift" if disagree.
3. ~~**6.8 3-role validation** (D-5b)~~ ✅ INVESTIGATED 2026-05-29 — verdict: PATTERN VALIDATED. 3 role files structurally consistent (7/7 sections, 78-81 lines). Ready for role #4 — recommended `frontend-designer` to anchor v3.7 family. Operator vetoes by reply "not yet" or "go with X".
4. **T0 voice corpus calibration** ($1.80-6 × 3-5 rundor)
5. **Real-work `/li:cycle` dogfood** på faktisk Azure-engagement — synthetic pre-validation done 2026-05-29 (4 validations passed, 3 soft-findings logged). See [.claude/engineering/design-archive/lintel-v3.7-fas-d-dogfood-protocol.md](../.claude/engineering/design-archive/lintel-v3.7-fas-d-dogfood-protocol.md) for the 7-step operator checklist (15-30 min). Reduces operator-effort from multi-hour evaluation to focused validation.
6. **Marketplace submission** (post MS legal review)
7. **PR #14 merge** efter WS-4a/b + alias-implementation

**Last touched:** 2026-05-29
