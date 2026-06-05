# Lintel — five-lens office-hours audit

**Mode:** reflection / due-diligence (advisory — propose, never execute).
**Snapshot:** stable `main @ 0f4aa16`. **Method:** six read-only auditors, one per cohort, all five lenses each.
**Disciplines:** intention before critique · evidence (path:line) · never remove capability (raise weak to strongest peer) · lift strengths as deliberately as weaknesses.
**Measured ground truth this run:** 168 skills · 65 agents · 30 hook dirs (31 scripts) · 1 pack (`_default`).

---

## Executive reflection

Lintel coheres, and its engineering floor is genuinely high. The 8-phase cycle is legible (every phase its own skill, one `00-state.md`, a `gap_if_skipped` on each), the SCOPE phase was inserted as a real first-class phase rather than bolted on, state was unified to one canonical `docs/plans/<slug>/`, and the routing core honors its own mechanical-first principle (the LLM path is a deliberate, honest stub). The bin/lib runtime is careful work — fork-free audit writer, cached uniformity matrix, replay guards. This is not a toy.

The system's biggest weakness is not structural. It is **drift between the system and its own self-description.** The runtime moved on to a pack-neutral, v4.6, `Azureflipper/jokerman-session-setup` reality; the shipping surface around it did not. The 8 plugin manifests, `install/`, `.opencode/INSTALL.md`, and `docs/session-harness.md` are frozen at the old identity (`jokerman89/jokerman-lintel`, `3.5.0-dev`, `@microsoft.com`, MS-CAIP-as-baseline, v3 counts). The generated showcase claims 192 skills / 92 agents / 3 packs against a real 168 / 65 / 1 — and it is the artifact whose own doc promises it "always reflects what's in the repo." The system that ships drift-detection has drifted on its own counts.

The second pattern, familiar from the prior uniformity audit, is **building capability ahead of wiring it**: the 500k cap is documented in three places but invoked at no handoff; `handoff-size-check` is named in prose, called by nothing; six agents and `instruction-parity-check` are reachable only by hand; the warn-hooks read `$1` while Claude Code delivers JSON on stdin, so they no-op exactly as documented. None of this is a capability problem — every piece exists and is well-built. It is a connection problem.

The single biggest hygiene issue: **Swedish text pervades the shipped surface** — ~27 skill files, 5 frontend agents, hooks, both CI workflows, the Codex manifest's user-facing prompts, `install.sh`, and (inherited) `CATALOG.md` — in direct violation of the repo's own English mandate. It is concentrated in the v3.5–v3.7 cohort; the v4.x engineering modules (ta/da/sc/dh/tq) are clean English and are the dialect everything else should be raised to.

Where the vision is most ahead of the wiring: the **multi-CLI promise** (8 CLIs) and the **company-neutral repositioning** (v4.7). Both are real and well-designed; both are undercut by an un-swept shipping surface, not by missing capability. Everything in this report is translation, wiring, and doc-regeneration. Nothing here recommends cutting anything.

---

## Strengths worth preserving

Named deliberately — these are well-conceived and should be the standard the weaker parts are raised toward.

1. **State unification.** One canonical `docs/plans/<slug>/`; three legacy `plan.md` paths formally deprecated (`docs/concepts/jobs-system.md:129-145`). Real subtraction. Lift this discipline to any future state kind.
2. **The engineering-module contract (ta/da/sc/dh/tq).** Clean English, uniform 3-granularity (`full/loop/single`), 6-dim rubrics, `necessity` + `gap_if_skipped`, and **zero dead agent references** (all "(NEW)" agents resolve). This is the bar.
3. **`depth_schema` as a single downstream signal** SCOPE→PLAN — no duplicated sizing logic.
4. **Composite shortcuts as pure delegators** (`fix`/`research`/`plan-and-build`/`review-and-ship` → `/li:cycle --from/--to`). Zero logic duplication; resist adding behavior to them.
5. **Mechanical-first routing + honest LLM stub + audit log.** `classify_intent`/`classify_size`/`assess_risk` are pure shell; every routing decision is inspectable in `orientator-decisions.jsonl`. The system practices its own principle.
6. **`gap_if_skipped` on every phase** — makes "why this exists" machine-checkable and operator-visible.
7. **L-001 lazy-load discipline** — `generate-*` template-only slots, `context-warm-*` base-skill delegation, `role-activate`/`role-deep-dive` tiering. Genuine cost wins; the right pattern.
8. **`subagent_spawn` dispatch convention** + **shared `_audit.sh` writer** + **graceful degradation** (ta-complexity exits cleanly on missing tooling). Clean, greppable, safe.
9. **Honest opt-in hook model** — inert at `~/.lintel/hooks/`, explicit symlink, "never surprise the operator."
10. **High bin/lib floor** — fork-free `_audit.sh` escaping, single-pass `li-uniformity` cache, `li-envelope-replay` dry-run-by-default guards, `pack-resolver` explicit failure semantics + neutral fallbacks.
11. **`LAYERS.md`'s SUPERSEDED-banner pattern** — leads with what changed and why, then documents current reality. This is the model every stale doc below should copy.
12. **`docs/concepts/{jobs-system,orientator}.md`** — dense, accurate, every referenced symbol verified; honest about the LLM stub vs wired reality.

---

## Findings by lens

### 1. CEO — intention & coherence

| What | Where | Intention | Severity | Recommendation |
|---|---|---|---|---|
| Shipping surface frozen at old identity while bin/ moved on | manifests (×8), `install/install.sh:288-292`, `.opencode/INSTALL.md`; vs `bin/li-doctor`/`li-scaffold`/`li-update` | the multi-CLI install/update promise | significant | Pick one slug/version/email; sweep all manifests+install+opencode to match `bin/`. |
| `session-harness.md` presents a v3 MS-CAIP fossil as "read this first" | `docs/session-harness.md:3,21,147,152` (dead `scaffolding/02-sdl`, `03-ms-team`; MS-SSO baseline) | the canonical mental-model doc | significant | Rewrite to the foundation+packs model, or stamp `SUPERSEDED` like LAYERS.md. |
| `AGENT-INSTRUCTIONS.md` cycle section omits SCOPE; lists pack-modes as built-in | `AGENT-INSTRUCTIONS.md:166-191` vs `cycle/SKILL.md:99-107` | the doc CLAUDE.md points operators to first | significant | Regenerate to include SCOPE (1.5) + mark customer-engagement/demo-prep pack-contributed. |
| Under-wired utilities ("why does this exist if nothing routes to it") | `uniformity`(1 ref), `usage-log`/`hooks-status`/`catalog`/`skill-router`(0 refs) | discoverability/observability dashboards | minor | Surface them from `/li:maintenance` + `/li:doctor`; advertise `skill-router` at SENSE. |

**Strength:** the cycle coheres and SCOPE wired in correctly (`cycle/SKILL.md:183-193` reads `route_override`; `plan:69` reads `depth_schema`).

### 2. Engineering-blocking — what is broken or disconnected

| What | Where | Intention | Severity | Recommendation |
|---|---|---|---|---|
| Warn-hooks read `$1`; Claude Code delivers tool data as JSON on **stdin** → they no-op as documented | `hooks/shared/no-secrets-in-edit/run.sh:7`, `ta-complexity-budget-warn/run.sh:14`, `frozen-zone-warn`, … + `hooks/shared/README.md:19` | hooks should inspect the real edit/command payload | **blocking** | Add a stdin-JSON adapter shim at the top of each `run.sh` (`payload=$(cat); jq -r '.tool_input.file_path'`), sourced once like `_audit.sh`. |
| 7 module hooks declare `event: PreCommit` — a non-existent Claude Code event; unreachable via the documented install | `da-migration-irreversible-warn/HOOK.md:4`, `dh-cost-budget-warn/HOOK.md:4`, `tq-coverage-drop-warn/HOOK.md:4`, `ta-complexity-budget-warn/HOOK.md:4`, … | fire on commit of risky changes | significant | Map to `PreToolUse` matching `Bash`+`git commit`, or add a documented git-hook install path. |
| 6 agents wired to nothing (no `subagent_spawn`, no mapping, no narrative) | `SlideNarrationCritic`, `CustomerEmpathyCheck`, `PostDemoFollowup`, `DevOpsToolchain`, `ReadOnly`, `ResearchSynthesizer` | each meant to be dispatched by a skill | significant | Wire to natural callers (customer trio→`ship` demo block; SlideNarrationCritic→`generate-ppt`; ReadOnly/ResearchSynthesizer/DevOpsToolchain→`pair-agent` registry). |
| SCOPE override `deploy` arm is dead — `classify_intent` maps `deploy`→`ship`, never emits `deploy` | `skills/scope/SKILL.md:102` vs `lib/orientator-routing.sh:28` | re-route greenfield "deploy to azure" from SHIP to build | significant | Teach `classify_intent` to separate `deploy` from `ship` so both readings stay distinguishable (the smoking-gun still works via the `ship` arm today). |
| CAPTURE sources `_audit.sh` via `$(dirname "$0")` (invalid for a skill body) → calibration write silently no-ops | `skills/capture/SKILL.md:61` (peers use `$LINTEL_REPO_ROOT`) | record actual-vs-estimated for the calibration loop | significant | Use `$LINTEL_REPO_ROOT/bin/_audit.sh` to match peers. |
| `lessons-surface` invoked via a Claude-Code-only `~/.claude/skills/...` path at 4 phase entries (multi-CLI repo) | `sense:50`, `plan:63`, `build:61`, `review:47` | surface lessons at phase entry | significant | Invoke `/li:lessons-surface` the way every other inter-skill call does. |
| `bin/li-forge-stats` documented as a shipped tool; absent | `wiki-generation.md:4`, `brief-forge.md:137`, `envelope.md:138` | forge telemetry | significant | Ship it, or downgrade prose to "(planned)". |
| `handoff-size-check` + the 500k cap named in prose, invoked by nothing | `plan/SKILL.md:419`, `jobs-system.md:142` | warn when trio+scope exceeds 500k | significant | Make PLAN/CAPTURE actually call it at trio-emit (see Cost #1). |
| `instruction-parity-check` is a true orphan (tests/wiki/memory refs only) | `skills/instruction-parity-check/` | verify substance-parity across the 6 CLI instruction files | minor-significant | Wire into CI or `/li:doctor` drift surface — the capability is valuable, the wiring is missing. |
| `LINTEL_REPO_ROOT` consumed by 12 skills, set only in `_aliases.sh`/`pack-resolver.sh` | sense/scope/plan/… `source "$LINTEL_REPO_ROOT/lib/..."` | sourcing libs from skills | minor (inference) | Add a derive-root fallback guard (peer pattern at `lib/brief-forge.sh:25`). |

### 3. Design — elegance & better ways

| What | Where | Severity | Recommendation (consolidate, preserve capability) |
|---|---|---|---|
| Duplicated secret + customer-data regexes across 3+3 hooks (drift independently) | `no-secrets-in-edit/run.sh:19-32`, `secret-scan-block`, `entropy-secret-check.sh`; + the 3 customer hooks | significant | Extract one `hooks/shared/_patterns.sh` (sourced like `_audit.sh`); keep warn-vs-block tiers; lift the strongest pattern set. |
| Three near-identical "surface lessons" blocks | `plan:57-64`, `build:55-62`, `review:41-48` | minor | One shared helper invoked with a phase keyword. |
| `context-budget` vs `context-budgetwatch` overlap | both read session-estimate+budget; only verdict differs | minor | Fold watch into a `--watch`/`--thresholds` mode; keep both names as aliases. |
| `context-warm-*` boilerplate (~110 lines × 7) | the warm family | minor | Shared doc-fragment include; keep all 7 source-resolvers (the delegation is already a strength). |
| Two parallel `*-review` families with divergent rubric formats | `plan-*-review` vs `code-review`/`devex-review`/`design-review` | minor | Align both to the engineering-module 6-dim scored rubric. |
| `cli_support` shape divergence (4 agents inline-array vs 61 list-of-objects) | `BlogPostDrafter`/`EmailCustomerDrafter`/`LinkedInPostDrafter`/`CustomerEmpathyCheck` | minor | Normalize the 4 up to the list-of-objects shape. |

### 4. DevEx — hygiene & experience

Headline: **Swedish across the shipped surface** (full list in the Hygiene Manifest). Plus:

| What | Where | Severity | Recommendation |
|---|---|---|---|
| `bin/li-adr-new` help text says `jstack-adr-new`/`jstack-scaffold` (don't exist) | `bin/li-adr-new:2,6,16,21,26,42,43` | minor | Rename to `li-*` (the only un-renamed bin script). |
| Hard-coded absolute personal paths | `CLAUDE.md:164`, `README.md:88`, `bin/li-lessons-promote:10,29`, `lintel-v3.5-azure-toolbox-plan.md:290` | minor | Parameterize to `$HOME`/repo-relative/placeholder. |
| `@microsoft.com` author email on the public shipping surface (disagrees with git identity `@gmail.com`) | all 6 author-bearing manifests + README:168 + SECURITY:7 | minor | Decide on a neutral maintainer address. |
| `"operator":"jokerman"` in 17 HOOK.md examples + 4 docs | sc-/da-/dh-/tq-/ta- HOOK.md, orientator.md:159 | cosmetic | Replace with `"<operator>"` in examples. |
| Mojibake (broken UTF-8) | `skills/CATALOG.md:94` (`tv�`) | minor | Auto-clears once the source skill description is fixed + CATALOG regenerated. |

**Confirmed non-issue:** no `/Users/jokerman` (or any `/Users/`, `/home/<user>`, `C:\Users`) absolute-path leak exists. The "~4 skills leak /Users/jokerman" belief does **not** match current state. What leaks is the bare username in doc examples + the absolute `E:/Workspace` paths above.

### 5. Cost — token economy

See the highlighted section below. Net posture is **strong**; one real gap.

---

## Cross-cutting observations (these matter more than any single instance)

1. **Drift between the system and its own description is the dominant systemic issue.** It appears as: stale counts in 5+ places that disagree with each other (README 165/70/29, showcase 192/92/3, session-harness 15/81/78, design 141/18/83 — real 168/65/30); a generated showcase that violates its own "always reflects reality" contract; doc-vs-code naming drift (module hooks documented unprefixed, shipped `ta-`/`tq-`/etc.); `li-forge-stats` documented-as-shipped-but-absent; README v4.7 vs CHANGELOG v4.6. *The drift-detection machinery (wiki-gen, uniformity, instruction-parity) exists but isn't run/wired — so the system can't see its own drift.*
2. **"Build ahead of wiring" recurs** (same shape as the prior uniformity audit's "built-but-unwired" cluster): 500k cap, `handoff-size-check`, 6 orphan agents, `instruction-parity-check`, hooks that no-op as written, `pack-resolver` (known). Capability is high; connection is the gap.
3. **Identity schism** runs through manifests + install + email + slug + version — one un-swept "old self" surface beneath a renamed runtime.
4. **Swedish is a single-author-era artifact**, concentrated in the v3.5–v3.7 cohort; the v4.x dialect is clean. A targeted sweep of that batch clears most of it.
5. **A shared-helper opportunity repeats** — `_audit.sh` is the model (one sourced helper, idempotent guard). The same move fixes the duplicated hook patterns, the stdin adapter, the lessons-surface blocks.

---

## Token-cost findings (highlighted)

Ranked by impact. Every recommendation preserves capability (off-switch / wire-the-existing-gate / mechanical-first).

1. **500k cap is documented but not wired at handoffs (the one real cost gap).** Cap logic lives in `context-budget/SKILL.md:49-76`; the repo's own audit confirms it never fires at plan/build cold-executor handoffs (`...cross-X2-promise-verification.md:136-143`). The trio + warming-context can silently exceed it. **Fix:** have PLAN/CAPTURE actually invoke the existing `context-budget` payload check at trio-emit (`plan:419` already names it — make it executable, not documentary). Off-switch already exists; just connect the gate.
2. **BUILD's per-task two-stage review has no complexity off-switch.** Every task fires ≥1 spec + ≥1 quality reviewer subagent (~5–15k warmup each per `agent-dispatch-rules.md:97`), even mechanical Haiku leaves; on a large `tree` plan that is N×2 subagents. **Fix:** gate the dedicated reviewer by task complexity (mechanical/Haiku leaves → inline, per the dispatch doc's own rule c). Raises BUILD to the standard the dispatch doc already states.
3. **LLM-where-mechanical: clean.** Orientator LLM path is a deterministic stub (`orientator-routing.sh:132-138`); Brief Forge's 5 evaluators are shell-mechanical and explicitly "Mechanical-first; LLM upgrade hooks documented but not active" (`brief-forge-evaluators.sh:6`). No violations. Keep the single per-handoff `budget_tokens` knob (default 5000) as the off-switch when Phase 4 wires real evaluators.
4. **Always-loaded payloads are bounded.** `session-digest` ≤~400 tokens with off-switch (`~/.lintel/.digest-disabled`/`NO_DIGEST=1`); `context-warm` warns >80% headroom + forces confirm ≥20k; `full-engineering-pass` (500k soft) ships `--skip-module`/`--resume`/dry-run. Well-controlled.

**Net:** the only cost hole is the unwired cap (#1) and the un-gated BUILD reviewer (#2). Everything else already has a toggle, a budget, or a mechanical-first default.

---

## Hygiene manifest (exhaustive)

### Swedish text (repo must be English) — by file, representative lines

**Shipped skills (customer-installable — highest priority):**
`skills/catalog/SKILL.md` (22: :4,15,19,29,30,36,62,92,96,126,128,140) · `skills/safe-install/SKILL.md` (21) · `skills/frontend-design/SKILL.md` (21: :19,23,25,31-34,46,81,94,95,172,178,202,225,232) · `skills/usage-log/SKILL.md` (20) · `skills/generate-style-learn/SKILL.md` (20: :15,23,25,35-37,42,60,69,201,206,223-229) · `skills/lessons-surface/SKILL.md` (19) · `skills/hooks-status/SKILL.md` (19) · `skills/handoff-size-check/SKILL.md` (18: :15,19,21) · `skills/frontend-design-review/SKILL.md` (18: :18,24,27,31,89,90,105,106) · `skills/maintenance/SKILL.md` (17) · `skills/profile-switch/SKILL.md` (16) · `skills/compliance-gate/SKILL.md` (15: :4,15,19,21,25,28,33,37,47,75,137,143,144,167,168,184) · `skills/frontend-motion/SKILL.md` (14) · `skills/instruction-parity-check/SKILL.md` (13) · `skills/generate-app/SKILL.md` (12) · `skills/generate-web/SKILL.md` (11: :53,66,68) · `skills/frontend-shader/SKILL.md` (10) · `skills/frontend-typography/SKILL.md` (9) · `skills/generate-ppt/SKILL.md` (7: :53,60,64,67,69,71) · `skills/frontend-style-extract/SKILL.md` (6) · `skills/sense/SKILL.md` (5: :32,45,48,53,71-75) · `skills/generate-word/SKILL.md` (4) · `skills/cycle/SKILL.md` (3: :135,158,254) · `skills/generate/SKILL.md` (:27) · `skills/ship/SKILL.md` (:130) · `skills/generate-pdf/SKILL.md` (:21) · `skills/CATALOG.md` (14, inherited from skill `description:` frontmatter — auto-clears when sources fixed; also mojibake at :94).

**Shipped agents:** `agents/frontend/DesignSystemAuditor.md` (13: :4,55,90,91,104,105,114,117,132,148,176) · `FrontendArchitect.md` (11: :4,22,50,65,71,79,102,138) · `ShaderEngineer.md` (9) · `MotionDirector.md` (6) · `TypographyCurator.md` (4).

**Shipped hooks / seeds:** `hooks/shared/frontend-design-surface/HOOK.md` (4: :24-27,80) · `hooks/entropy-secret-check.sh:4-5` · `seeds/brand/design-patterns/ultra-modern-lovable-style/component-imports.json` (2), `pattern.json` (1).

**CI workflows + manifests (run/shown every push):** `.github/workflows/catalog.yml:26-28` · `.github/workflows/ci.yml:142` · `install/install.sh:1,110` · `install/verify.sh:421,507` ("Kategori B") · `.codex-plugin/plugin.json:34-36` (3 user-facing example prompts).

**Concept + design docs (English bar applies, lower portability priority):** `docs/concepts/agent-dispatch-rules.md:7-8` · `jobs-system.md:121-122,246-250` · `planner-as-module.md:121-122` · `orientator.md:84` (routing keywords — acceptable) · `lintel-v4.0-reframe-design.md:648` (verbatim operator quote) · design docs `lintel-v3.5-doc-generation-plan.md` (83), `lintel-v3.6-backlog-sequencing.md` (81), `lintel-v3.7-frontend-design-system.md` (65), `lintel-v3-plan.md` (60), `lintel-v3.5-azure-toolbox-plan.md` (29), `lintel-v3.6-alias-mechanism.md` (24) · 8 `docs/audit/*` files (single-digit). Documented bilingual anti-pattern noted at `skills/generate-write/SKILL.md:209`.

### Leaked local/personal paths

Absolute personal paths (`/Users/`, `/home/<user>`, `C:\Users`): **none.** (Only `/home/runner` CI paths, which are correct.)
Portability-breaking hard-coded paths: `CLAUDE.md:164` (`E:/Workspace/jokerman-session-setup`) · `README.md:88` (`$HOME/Workspace/jokerman-lintel/bin`) · `bin/li-lessons-promote:10,29` (`$HOME/Workspace/jokerman-session-setup` default) · `docs/design/lintel-v3.5-azure-toolbox-plan.md:290` (`E:/Workspace/jokerman-lintel`).
Username `jokerman` in examples: 17 HOOK.md (`sc-auth-bypass-warn:43`, `da-retention-violation-warn:40`, `tq-perf-regression-warn:32`, … full list in infra-audit) + `orientator.md:159` + `lintel-v3.5-cycle-and-roles.md:170` + 2 structure-change docs (`jokerman89`) + `agents/engineering/DocWriter.md:56` (`@jokerman/gstack`).
`@microsoft.com` email: `.claude-plugin/plugin.json:7`, `marketplace.json:5`, `.codex-plugin:7`, `.cursor-plugin:8`, `.copilot-plugin:7`, `.droid-plugin:7`, `README.md:168`, `SECURITY.md:7`, `PLUGIN-FORMAT-RESEARCH.md:23`, `lintel-v3-plan.md:509`.

### Cringe / rot comments

**None found.** No joking/unprofessional comments, no commented-out code, no misleading/stale comments. The ~60 `placeholder`/`stub`/`TODO`/`WIP` hits are all intentional + documented (scaffolding slots, the deliberate Phase-4 LLM stub at `orientator-routing.sh:129-138`, WIP-commit machinery). Two honest "for now" deferrals (`frontend-design:225`, `code-freeze:75`). The only defect-as-text is the **mojibake** at `skills/CATALOG.md:94`.

---

## Prioritized next steps (options for the operator — not a mandate)

**Quick wins (high value, low effort):**
1. **English sweep of the v3.5–v3.7 cohort** (~27 skills + 5 frontend agents + hooks + 2 CI workflows + Codex manifest prompts). Fixing skill `description:` frontmatter auto-clears `CATALOG.md` Swedish + the mojibake. Target dialect: the v4.x modules.
2. **Reconcile the shipping identity** — one slug/version/email across 8 manifests + install + opencode to match `bin/`; rename `li-adr-new` `jstack-*`→`li-*`.
3. **Regenerate the generated artifacts** — run `bin/li-wiki-gen` (fixes the 192/92/3 showcase + counts); reconcile README v4.7 vs CHANGELOG v4.6.
4. **Parameterize the 4 hard-coded absolute paths.**

**Deeper work (wiring the built-but-unwired):**
5. **Fix the hook input model** — one stdin-JSON adapter shim so warn-hooks actually fire; reconcile the `PreCommit` event vocabulary.
6. **Wire the 500k cap** at PLAN/CAPTURE handoffs (the gate exists; call it). Gate BUILD's two-stage review by task complexity.
7. **Wire the 6 orphan agents + `instruction-parity-check` + `handoff-size-check`** to their natural callers / CI.
8. **Fix the doc-vs-reality contracts** — SCOPE in AGENT-INSTRUCTIONS, module-hook names in the concept docs, `li-forge-stats` ship-or-de-claim, `session-harness.md` rewrite-or-banner, CAPTURE's `_audit.sh` source path, the SCOPE `deploy` arm + `classify_intent`.
9. **Extract shared helpers** — `_patterns.sh` for the duplicated hook regexes; one lessons-surface helper.

None of the above removes capability. Every item is translation, wiring, doc-regeneration, or consolidation that preserves what exists.
