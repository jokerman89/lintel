# Launch-readiness register v2 — public launch (2026-06-18)

> Cycle `launch-readiness` (meta-infra), branch `feat/launch-readiness`. Inventory @ v5.7.1:
> 125 skills · 69 agents · 33 hooks · 14 lib · 21 bin · 25 ADRs · 93 tests (89/89 green).
> Built from a 10-agent read-only audit (A1–A8 internal + B1–B2 external research). Severity:
> **P0** = broken/embarrassing for a new user (launch blocker) · **P1** = significant gap ·
> **P2** = depth/quality · **P3** = polish. Supersedes nothing — extends the v5.x register
> (2026-06-12).

## 0. The strategic picture (from external research B1/B2)

Lintel's closest analogue is **obra/superpowers** (231k★, same shape: skills + hooks + subagent
TDD + multi-CLI). The whole "structured AI dev workflow" class (superpowers, github/spec-kit,
GSD) has documented, consistent failure modes. The four that bear directly on launch:

1. **Silent hook breakage on Windows / non-Claude CLIs is the #1 launch killer.** superpowers
   shipped inert hooks for ~7 versions (single-quoted `${CLAUDE_PLUGIN_ROOT}`, a `-l` login-shell
   wrapper) with no error surfaced. For Lintel a silently-dead hook means the **safety layer**
   (secret-scan-block, customer-data-block) becomes a no-op. → We use escaped double-quotes in
   `hooks.json` (verified good) and invoke `.sh` directly (no `.cmd`/`-l` wrapper) — but we have
   **no test that a hook actually FIRES on a clean install**, and `/li:doctor` only checks
   registration + audit records. **Mitigation: a clean-install hook-fires smoke test + doctor
   firing assertion.**
2. **Always-on context cost.** Every skill `description:` + agent frontmatter is loaded at session
   start (bodies are lazy). At-rest proxy measured today: ~27 KB of skill descriptions + ~14 KB of
   agent descriptions = a large standing surface (125 + 69 + 33). superpowers' single most
   reassuring launch stat was "core <2k tokens, ~100k for a big project." **Mitigation: measure +
   publish Lintel's at-rest token cost; keep descriptions terse; route heavy work through subagents
   (already the discipline).**
3. **"Too heavy for small tasks" is the #1 abandonment reason for the entire class** (spec-kit
   "10x slower" on small changes; "kept ~30%" on HN). Lintel has the escape hatches — `/li:fix`,
   SCOPE staying silent on small work, phase-hopping, mode presets — but a first-run user who types
   `/li:catalog` and sees **125 skills + 69 agents will bounce.** **Mitigation: this is
   packaging/perception, not capability — tier the surface (core vs experimental) and make the
   5-minute light path the loud default in `/li:welcome`.**
4. **Maintenance optics + update safety.** A solo-maintained 125-skill surface invites "is this
   maintained?" (spec-kit's visible backlog drove defections). GSD's `/update` wiped user patches.
   **Mitigation: smaller obviously-maintained core + honest experimental labels; verify a plugin
   update can NEVER clobber a repo's `.claude/memory` or `~/.lintel/`.**

What we already do well vs the field (lead with these in launch messaging): subagent-isolation
("reports, main agent decides") is the textbook fix for context rot; CAPTURE write-back beats
spec-kit's one-way stale specs; editable plan-as-a-file; the continuity trifecta we just shipped
directly targets "agents ignore the workflow mid-task."

## 1. P0 — launch blockers (mechanical, in-scope to fix directly)

**Broken commands / dead cross-refs a new user hits day one:**
- `skills/autoplan/SKILL.md` — entirely un-namespaced (`/office-hours`, `/plan-ceo-review`,
  `/ship`, …), references `~/.lintel/projects/`, hardcoded "17-task" + dead Layer-2 compliance model.
- Dead skill refs: `/li:dependency-audit` (review:117 — it's an agent), `/li:tdd-cycle` (build:92),
  `/li:hotfix` (cycle:19 navigation frontmatter + orientator:32), `/release-ev2` ×8 (qa-only,
  perfbench:22/79/103/124, plan-tune:71 — real gate is `/li:ship`).
- Hyphen-form invocations `/li-fix`, `/li-cycle`, `/li-plan-and-build` (fix, plan-and-build,
  review-and-ship) — separator is `:` not `-`.
- `skills/handoff-size-check/SKILL.md:28,43,138` reads `PLAN.md` but PLAN writes lowercase
  `plan.md` → the post-PLAN cycle gate is silently DEAD.

**Honesty / brand / correctness:**
- `skills/doctor/SKILL.md:60` emits `JSTACK-DOCTOR` (pre-rebrand) + `skills/scaffold/SKILL.md:84`
  `JSTACK-SCAFFOLD` banner.
- `skills/catalog/SKILL.md:140,149` documents `skills/catalog/bin/regenerate.sh` that does not exist
  (real generator is inlined in `.github/workflows/catalog.yml`).
- `skills/help/SKILL.md:34,78-81,116` is built on the dead pre-plugin install model (`install.sh`,
  manual symlinks, "hooks INACTIVE") — wrong first-run instructions.
- **Global-lessons path broken 3 ways** — `learn:34` writes `~/.lintel/lessons.jsonl`, `lessons:37`
  reads `~/.lintel/lessons/global.md`, `li-lessons-sync:11` uses `$LINTEL_HOME/lessons/`. Lessons
  written by `/learn` are **never surfaced** — the one mechanism Lintel calls "the only thing that
  compounds learning" is broken.
- `skills/scaffold/SKILL.md:59,63,100` tells the agent to `cp scaffolding/01-foundation/docs/personas/*`
  — that source dir does NOT exist; the real `bin/li-scaffold` copies to `.claude/memory/`. Two
  implementations disagree; the literal SKILL.md path fails.

**Substrate (can silently break real cycles):**
- **`set -uo pipefail` leaks into the caller shell** from 4 SOURCED libs —
  `lib/orientator-routing.sh:14`, `lib/scale-estimator.sh:37`, `lib/brief-forge.sh:19`,
  `lib/brief-forge-evaluators.sh:23`. Skills source them inline on the near-universal SENSE/SCOPE
  path; a later unset-var aborts the block. `pack-resolver.sh` already documents the fix (omit the
  global set). **Highest-blast-radius P0.**

**Dependencies / output:**
- `generate-ppt:23,174` + `generate-word:27,118` name `pptxgenjs`/`docx-templater` (wrong name
  "pptx-genjs") with **no install path + no degradation** — two flagship deliverable skills can't
  run for a fresh user.

**Publishing face (a GitHub visitor sees these):**
- `CONTRIBUTING.md` — stale v3 Microsoft-CAIP artifact ("Microsoft Sweden CAIP-SE", `layer: ms-team`,
  `scaffolding/02-sdl/`, dead `tasks/lessons.md`). The first doc a contributor reads.
- `.claude/engineering/audits/` (25 files, this register's own dir) + `.claude/engineering/design-archive/` + much of `.claude/engineering/design-archive/`
  — Swedish + Microsoft-internal residue + harsh self-critique; **should not be in the public tree.**
- `.claude/engineering/design-archive/PLUGIN-FORMAT-RESEARCH.md` + `docs/session-harness.md` +
  `.claude/engineering/audits/lintel-state-of-the-harness.md` — v3 MS fossils; the per-cli one teaches the WRONG slug
  (`lintel@` not `li@`). README links three of these as "the architecture / mental model."
- **`gh repo view jokerman89/lintel` could not resolve the repo** — confirm the public repo exists
  at that path and CODEOWNERS `@Azureflipper` is a valid collaborator (every install command +
  homepage URL depends on it). [NEEDS OPERATOR CONFIRMATION]

## 2. P1 — significant gaps

- README: "124 skills" (→125), Status "v5.3" + ":198 current line is v5.3" (→5.7.1).
- CHANGELOG stops at 5.7.0 (no 5.7.1). `.codex-/.cursor-plugin/plugin.json` + `gemini-extension.json`
  at 5.7.0 while plugin.json/marketplace.json at 5.7.1 — **align all manifests.**
- SECURITY.md support table lists only v3/v2/v1. SHIP-GATE.md "v3.5.0", counts 124/31.
- No `.github/ISSUE_TEMPLATE`, no `PULL_REQUEST_TEMPLATE.md` (CONTRIBUTING tells users to fill one),
  no `CODE_OF_CONDUCT.md`.
- `ta/sc/tq` write module audit to `$LINTEL_HOME/audit/` (operator-global) vs `da/dh` correctly
  repo-local via `audit_log` — ADR-0005 violation, self-contradictory.
- 10 module warn-hooks reference `$LINTEL_REPO_ROOT` unguarded under `set -u` → fail-CLOSED (exit 1)
  on a normal edit if opted in. `sc-auth-bypass-warn` `grep -c || echo 0` double-zero arithmetic
  crash on its own happy path.
- `hooks/shared/README.md` — stale counts (31 vs 33, "Warn-only (27)", duplicate 13/14 numbering)
  + documents only the legacy manual-symlink activation, contradicting ADR-0008 auto-registration.
- 2 Microsoft leaks in neutral spine agents: `SOC2Reviewer.md:124` (ServiceTrust.microsoft.com),
  `JWTSecurityReviewer.md:130` (Microsoft.IdentityModel). Also `compliance.md`/`faq.md` MS-internal
  text; `personas-example.md:6` "internal MS account names".
- Scaffolding promises non-existent assets — `scaffolding/01-foundation/README.md:14` "4 baseline
  agents in .claude/agents/" + `:10` `scaffold-repo.sh` (real: `li-scaffold`); `TEMPLATE-agent.md:82`
  stale `tasks/lessons.md`.
- `bin/li-doctor:82` version glob `break`s on first (oldest) match → reports wrong installed version.
- Over-promises presented as working: `context-cool` writes `context-ignore.md` nobody reads;
  `context-budget --watch` reads telemetry nothing writes; `instruction-parity-check` substance-diff
  is pseudocode; `brief-forge` references 2 missing hooks; `safe-install` `--uninstall` doesn't exist;
  `plan-eng-review` "Review Readiness Dashboard" is dangling.
- CI `.github/workflows/ci.yml:180` `/onecs-check` (OneCS = Microsoft) job — disabled but visible.

## 3. P2 — depth / quality

- **Agent depth split:** only 20/69 got the v5.3 craft raise. 4 customer-facing categories left
  behind — **customer (0/7), communication (0/4), devops (0/5), doc-gen (0/3)** ≈ 19 agents thin
  (one-liner descriptions, no Core-principles/Behavioral-traits) + ~21 engineering stragglers.
- `capture` retro template emits `cost_estimate_dollars` / `Cost: $<X>` — contradicts the
  load-bearing "Lintel has no pricing table, never invent a $ figure" (cycle:378, plan honest-signals).
- `ta/da/sc/dh/tq` are ~80% identical boilerplate (five copies drift independently — that's why the
  audit-path fix landed in da/dh but not ta/sc/tq).
- Swedish + internal-roadmap leaks in user-facing skill bodies (frontend-design "Fas B",
  generate-style-learn:41, generate-web:76, "Phase A2 ships in…", "resolves M-3").
- Stale counts everywhere (help "3 hooks", doctor "<N>/15", health "14 hooks", discover "78 agents").
- `eval`/perf-mode cite "Claude Opus 4.7" (→4.8); dangling doc refs (CONTEXT-ENGINE.md, SHIP-GATE.md).
- `_default` ships zero roles/personas → `/li:roles-list` etc. dead-end for a fresh user (seed a sample).
- `docs/wiki/` generated 2026-06-12 (pre-5.7.1, "v4.0/v4.1" note); `docs/v4.x/` dir name reads as
  drift while shipping v5.7 (rename needs an ADR — cross-linked 6×).

## 4. Subtraction — the command-surface decision (KEY, strategic)

External evidence is unanimous: the 125-skill / 9-phase surface is a **perception** launch risk, not
a capability one. The fix is **tiering + targeted merges**, not mass removal. Concrete merge
candidates surfaced by the audit (all preserve capability):

| Merge | From→To | Rationale |
|---|---|---|
| context-warm family | 7 → ~3 | `-related/-adrs/-sessions` are identical wrappers differing only in corpus → flags on base `context-warm`. Keep `-customer` (audit gate) + `-from-url` (different tool). **Biggest single win.** |
| doctor + health | 2 → 1 | Both check install/hooks/frontmatter/version. One `/li:doctor [--upstream\|--fast]`. |
| lessons + lessons-surface | 2 → 1 | Near-dupes; `lessons-surface` is the real (scored) one, auto-invoked from SENSE. Retire `lessons`. |
| generate-pdf/xlsx/visio | 3 slots → `generate --format` | Admitted "TEMPLATE ONLY", no body, route through same pipeline. |
| design-review + frontend-design-review | 2 → 1 | 6-axis visual gates, ~70% overlapping axes; `--scope changes\|artifact` flag. |
| make-pdf + generate-pdf | 2 → 1 | make-pdf is the working renderer; generate-pdf the pipeline caller — one with a renderer step. |
| frontend-style-extract + generate-style-learn | 2 → 1 | Same inputs, sister disciplines; `--level palette\|pattern\|both`. |
| office-hours → /li:define standalone | alias | Near-total overlap with DEFINE; also fixes its divergent output path. |
| ta/da/sc/dh/tq bodies | 5 copies → 1 shared impl | Keep 5 entry points; collapse the 80%-identical body (ADR-0009 precedent). |

Net realistic: ~125 → ~108–112 skills + a **core/experimental tier label** so `/li:catalog` and
`/li:welcome` lead with ~8–10 "start here" skills. **Decision needed: how aggressive?**

## 5. What's genuinely healthy (don't touch)

Frontmatter contracts 100% clean (all 125 skills, all 69 agents). The cycle gate structure is sound
(no missing gates beyond the dead handoff-size-check). The 2 BLOCK hooks are correctly fail-closed
with hardened overrides + hostile-repo git flags. No orphan agents. install.sh/install.ps1 are
mirror-faithful and the Microsoft-dir regression is fixed. verify.sh --all + 89/89 suite green.
LICENSE is clean MIT. AGENT-INSTRUCTIONS / GLOSSARY / getting-started / concepts / CATALOG current.
Subagent-isolation discipline is the field's best-practice answer to context rot.

## 6. Proposed fix waves (PLAN)

- **W1 — broken-command sweep** (P0 §1 commands): namespace autoplan/careful, kill dead cross-refs,
  hyphen→colon, handoff-size-check path. All mechanical, test after.
- **W2 — substrate + honesty** (P0 §1 substrate/honesty): set -u leak in 4 libs, global-lessons path,
  scaffold↔li-scaffold, brand leftovers, ta/sc/tq audit path, module-hook unbound-var, sc-auth crash.
- **W3 — output deps**: PPT/Word dep doc + degradation + package-name fix.
- **W4 — publishing face** (P0/P1 §1-2): CONTRIBUTING/SECURITY/SHIP-GATE neutral+current; README
  counts/version; CHANGELOG 5.7.1; manifest version alignment; issue/PR/CoC templates; CI onecs;
  Microsoft leaks in agents/docs; public-tree scoping (audit/feature-requests/design-historical).
- **W5 — subtraction + tiering** (§4, scoped to operator decision): merges + core/experimental tier
  + `/li:welcome` light-path-first + measure & publish at-rest token cost.
- **W6 — agent craft-raise** (§3, scoped to operator decision): ~19 customer-facing agents (or defer).
- **W7 — continuity hardening**: clean-install hook-fires smoke test + `/li:doctor` firing assertion
  (the #1 external launch risk); verify plugin-update can't clobber `.claude/memory`/`~/.lintel`.
- **REVIEW** (M2 compat + M3 shape + independent L-007) → **SHIP** (PR) → **CAPTURE** (lessons, M4).
