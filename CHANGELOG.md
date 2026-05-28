# Changelog

All notable changes to this repo are tracked here. Format is loose — date headings + bulleted changes. Major behavior changes to the canonical instructions are also logged in `scaffolding/EVOLUTION-LOG.md` (which travels with each scaffolded repo).

## 2026-05-28 — v3.5.0-dev (on `lintel-rebrand` branch)

**Lintel v3.5: 8-phase cycle + role-lifting + context-warming + rebrand from JStack.**

JStack v3.0 → Lintel v3.5. Repo renamed to `jokerman-lintel` under `jokerman89` namespace. Plugin namespace `lintel:`. Skill prefix `li-*`. All 343 JStack mentions + 636 jstack identifiers + 54 Azureflipper references replaced atomically across 200+ files.

### Phase A — Atomic rename

- GitHub repo: `Azureflipper/jokerman-session-setup` → `jokerman89/jokerman-lintel`
- Branch: `lintel-rebrand` from `v3-dev` (preserves 2 prior design-doc commits)
- Plugin manifests: 7 manifests (`.claude-plugin/`, `.codex-plugin/`, `.cursor-plugin/`, `.opencode/`, `gemini-extension.json`, `.copilot-plugin/`, `.droid-plugin/`) updated to `name: lintel`
- All 81 v3 skills got `li-` prefix in frontmatter (v3 cli_support arrays preserved)
- Bin scripts renamed: `bin/jstack-*` → `bin/li-*` (6 files)
- Skill folders renamed: `skills/jstack-*` → `skills/li-*` (4 dirs)
- Env vars: `JSTACK_HOME` → `LINTEL_HOME`, `~/.jstack/` → `~/.lintel/`
- 188 files in single atomic commit

### Phase B — 8 phase-skills (cycle backbone)

Full Lintel cycle backbone, each skill at design-doc depth:

- `skills/li-sense/SKILL.md` (230 lines) — auto-detect intent, WorkProfile, role, prior 00-state
- `skills/li-define/SKILL.md` (261 lines) — office-hours forcing questions + role-lens + adversarial spec review
- `skills/li-discover/SKILL.md` (260 lines) — codebase map + ADR scan + lessons + agent/skill recommendations
- `skills/li-plan/SKILL.md` (308 lines) — task breakdown + cost-estimate gate + founder approval + 2-stage subagent review
- `skills/li-build/SKILL.md` (286 lines) — TDD + Subagent-Driven Development + 2-stage per-task review + hard-rule hooks
- `skills/li-review/SKILL.md` (315 lines) — 3-stage review (spec/quality/compliance) + cross-artifact analyze
- `skills/li-ship/SKILL.md` (333 lines) — HARD-RULES + voice + 4-gate doc-gen + EV2/OneBranch + PR creation
- `skills/li-capture/SKILL.md` (364 lines) — lessons + ADR + EVOLUTION-LOG + cold-executor handoff trio + operator profile

~2357 lines total. Each skill specs: sub-skills invoked, recommended agents, artifacts produced, gates, status protocol, pause-points, hop-in support, integration (reads/writes/triggers), anti-patterns, failure recovery, voice tier behavior.

### Phase C — Cycle orchestrator + resume

- `skills/li-cycle/SKILL.md` (~210 lines) — chains 8 phases with gates, 5 mode presets + auto + custom flags
- `skills/li-resume/SKILL.md` (~180 lines) — reads `.lintel/state/00-state.md`, picks resume phase, cross-machine sync fallback

### Phase D — Composite shortcuts (~100 lines each)

- `skills/li-fix/SKILL.md` — hotfix workflow (SENSE+BUILD+REVIEW+SHIP)
- `skills/li-research/SKILL.md` — research-dive (SENSE+DEFINE+DISCOVER, no build)
- `skills/li-plan-and-build/SKILL.md` — PLAN+BUILD for split-session resumability
- `skills/li-review-and-ship/SKILL.md` — REVIEW+SHIP+CAPTURE close-out

### Phase E — Role-lifting infrastructure

NEW concept: bring expert personas into session as lightweight context layers.

8 role-skills:
- `skills/li-role-activate/SKILL.md` — load IDENTITY + VOICE + OUTCOME-LENS (~500 tokens)
- `skills/li-role-deep-dive/SKILL.md` — full role-file (~2-3k tokens, sensitivity-aware)
- `skills/li-role-frame/SKILL.md` — apply role's lens to an artifact
- `skills/li-role-rotate/SKILL.md` — swap active role mid-session
- `skills/li-role-deactivate/SKILL.md` — clear role-overlay
- `skills/li-roles-list/SKILL.md` — enumerate available roles
- `skills/li-role-new/SKILL.md` — scaffold new role via guided interview
- `skills/li-role-update/SKILL.md` — incremental updates, PII soft-scan

3 default public roles shipped:
- `roles/field-cto.md` — customer-facing, sales-tech, trailblazer voice
- `roles/solution-architect.md` — enterprise IT, security-conscious, mixed voice
- `roles/engineering-manager.md` — process, team coordination, internal voice

Each role file structure: frontmatter (sensitivity field) + IDENTITY + COLD KNOWLEDGE (top 10) + DECISION CRITERIA + VOICE + OUTCOME LENS per cycle phase + ROLE-SPECIFIC INSIGHTS + COMPANION SKILLS + SENSITIVE CONTEXT (private roles only).

Private roles sync via `bin/li-roles-sync` (per-operator opt-in, private git repo, never public marketplace, NEVER team-wide). Mirrors `bin/li-lessons-sync` pattern.

### Phase F — Context-warming infrastructure

NEW capability: on-demand 1M-context utilization beyond session-start.

10 context-warming skills:
- `skills/li-context-warm/SKILL.md` — base file load with budget tracking
- `skills/li-context-warm-related/SKILL.md` — heuristic load by topic
- `skills/li-context-warm-sessions/SKILL.md` — load last N session saves
- `skills/li-context-warm-adrs/SKILL.md` — load topic-relevant ADRs
- `skills/li-context-warm-customer/SKILL.md` — customer-engagement repo load (audit-logged)
- `skills/li-context-warm-from-url/SKILL.md` — WebFetch + dump, WorkProfile URL gate
- `skills/li-context-dump/SKILL.md` — load specific prior session save
- `skills/li-context-snapshot/SKILL.md` — operator-named mid-session save
- `skills/li-context-budget/SKILL.md` — utilization visibility + breakdown
- `skills/li-context-cool/SKILL.md` — selective IGNORE marker (Claude Code context append-only)

Session-start stays lightweight (~5-15k tokens). Warming is explicit operator action with budget confirmation for >20k loads.

### Counts (post-Phase F)

- Skills: 113 (81 v3 + 32 new in v3.5)
- Agents: 78 (unchanged from v3)
- Hooks: 15 (unchanged)
- Plugin manifests: 7 (rebranded to lintel)
- Root entrypoint files: 3 (CLAUDE.md, AGENTS.md, GEMINI.md — rebranded)
- Bin scripts: 7 (6 v3 + li-roles-sync new)
- Default public roles: 3
- Cycle phases: 8 (named paths: SENSE, DEFINE, DISCOVER, PLAN, BUILD, REVIEW, SHIP, CAPTURE)
- Mode presets: 5 (hotfix, customer-engagement, internal-tool, demo-prep, research-dive) + auto
- Composite shortcuts: 4 (li-fix, li-research, li-plan-and-build, li-review-and-ship)

### Remaining for v3.5.0 tag (Phases G-K)

- Phase G: Cold-executor handoff trio dogfood verification (CAPTURE writes spec.md + plan.md + prompt.md; verify operator can re-execute from those alone)
- Phase H: Doc rewrite (README + SHIP-GATE + LAYERS + AGENT-INSTRUCTIONS fully updated for v3.5)
- Phase I: Tests (phase-skill smoke tests + cycle E2E)
- Phase J: Operator dogfood (`/lintel:li-cycle --mode internal-tool` on internal extension)
- Phase K: PR + tag v3.5.0-dev

### Methodologies studied (per design phase)

- **obra/superpowers**: per-skill richness, two-stage review (spec→quality), Subagent-Driven Development, status protocol vocabulary
- **github/spec-kit**: 7-phase pipeline (we adopt + add CAPTURE), Constitution analog, cross-artifact analyze
- **gstack (parent)**: AskUserQuestion decision-brief, forcing questions, premise-check, voice rules, continuous checkpoint, boil-the-lake
- **Architect Agent image (operator-shared)**: cold-executor handoff trio, 00-state.md, cost-estimate gate, founder approval gate, failure recovery protocol

Lintel-unique additions vs all 4: WorkProfile toggle, role-lifting, context-warming, 5-mode presets, multi-CLI plugin manifest, MS-internal compliance gates (RAIS/OneCS/AGT/EV2/OneBranch/SDL/1ESPT), Trailblazer voice corpus, 78 specialized agents.

---

## 2026-05-27 — v3.0.0-dev (on `v3-dev` branch)

**Lintel v3: plugin-manifest pattern + agent build-out + session-harness framing.** Big Bang rework following obra/superpowers' multi-CLI plugin pattern. Discards v2's "MCP server + per-CLI compile" plan as over-engineering. Agents BUILD OUT (44 → 78), not trimmed. Scaffolding-templates preserved + modernized.

Design doc: [docs/design/lintel-v3-plan.md](docs/design/lintel-v3-plan.md).
Per-CLI plugin format research: [docs/per-cli/PLUGIN-FORMAT-RESEARCH.md](docs/per-cli/PLUGIN-FORMAT-RESEARCH.md).
Session-harness explainer: [docs/session-harness.md](docs/session-harness.md).

### Architecture shift (Phase 0–2)

- **Plugin-manifest pattern.** Tiny per-CLI manifests (`.claude-plugin/`, `.codex-plugin/`, `.cursor-plugin/`, `.opencode/`, `gemini-extension.json`, `.copilot-plugin/`, `.droid-plugin/`) all point at shared `./skills/` and `./agents/` dirs. Each CLI's native plugin marketplace handles discovery + invocation. NO MCP server, NO per-CLI compile step.
- **Root entrypoint files:** `CLAUDE.md`, `AGENTS.md`, `GEMINI.md` at repo root — read by Claude Code / Codex / Gemini respectively when working ON the Lintel repo. Each links to canonical `AGENT-INSTRUCTIONS.md` + adds CLI-specific notes.

### Reorganization (Phase 1)

- `scaffolding/01-foundation/skills/*` + `scaffolding/03-personal-advanced/skills/*` → `skills/` (74 skills flat at repo root, with `layer: foundation | ms-team` frontmatter)
- `scaffolding/03-personal-advanced/agents/*` + `scaffolding/04-power-user/agents/*` → `agents/<category>/<Name>.md` (organized per domain: ms-specific, engineering, security, compliance, devops, customer, communication, voice, doc-gen)
- `scaffolding/02-sdl/hooks/*` → `hooks/shared/*` (lifted to repo root for plugin-discovery)
- `scaffolding/04-power-user/` removed (content moved to `agents/engineering/`)
- `scaffolding/03-personal-advanced/` renamed to `scaffolding/03-ms-team/`
- Root cleanup: 5 design docs moved from root to `docs/design/` (MIGRATION-TABLE, CONTEXT-ENGINE, BRAND-INTEGRATION, T0-CALIBRATION-WORKFLOW, UPSTREAM-SIMILARITY, TODOS, CLI-SUPPORT-V2-SCHEMA). Root .md count: 11 → 5 (README, CHANGELOG, LAYERS, SHIP-GATE, AGENT-INSTRUCTIONS) + 3 new (CODEOWNERS, CONTRIBUTING, SECURITY).

### Agent build-out (Phase 3) — 44 → 78 agents (+34 new)

Per operator direction: agents are Lintel value, build out instead of trim.

- **ms-specific (+7):** AzureArchitect, AzureOpenAIAdvisor, M365CopilotAdvisor, GraphAPIAdvisor, BicepReviewer, ARMTemplateReviewer, KeyVaultAuditor
- **security (+5):** ThreatModelDrafter, SecretsScanReviewer, SBOMAuditor, OAuthFlowReviewer, JWTSecurityReviewer
- **compliance (+5):** GDPRReviewer, SDLReviewer, AGTReviewer, EUAIActReviewer, SOC2Reviewer
- **devops (+5):** OneBranchReviewer, EV2PipelineAuditor, GHActionsReviewer, TerraformReviewer, K8sManifestReviewer
- **customer (+5):** ProposalDrafter, RFPResponseDrafter, ExecutiveBriefingDrafter, WorkshopFacilitator, DemoNarratorJunior
- **communication (+4):** BlogPostDrafter, LinkedInPostDrafter, EmailCustomerDrafter, SlideNarrationCritic
- **engineering (+3):** LatencyAnalyzer, CostAnalyzer, RegressionDetective

Final per-category counts: ms-specific 15, engineering 25, customer 8, security 8, devops 7, compliance 6, communication 5, doc-gen 3, voice 1. Total: 78.

### Session-harness skills (Phase 4) — 74 → 81 skills (+7 new)

- `/lintel:li-lessons-promote` — promote repo lesson → Lintel global
- `/lintel:li-adr-new` — bootstrap ADR from template
- `/lintel:li-personas-rotate` — load persona context for demos/workshops
- `/lintel:li-match` — semantic skill router (free text → top 3 skills)
- `/lintel:li-doctor` — cross-CLI health check (replaces v2 spec-only li-cli-fingerprint)
- `/lintel:li-scaffold` — invoke repo scaffolding into target
- `/lintel:li-lessons` — mid-session lessons.md relevance-filtered review

### Bin/ scripts (Phase 5)

- `bin/li-scaffold` — copy scaffolding/01-foundation/* into target repo with CLAUDE.md template rendering
- `bin/li-doctor` — cross-CLI health check (color-coded output, --verbose, --json)
- `bin/li-lessons-sync` — per-operator opt-in lessons sync across machines (private git repo)
- `bin/li-lessons-promote` — interactive promote of repo lesson → Lintel global
- `bin/li-adr-new` — bootstrap ADR with auto-numbering + commit
- `bin/li-update` — update plugin across detected CLIs

### Docs rewrite (Phase 6)

- README v3-sync with honest multi-CLI table
- `docs/session-harness.md` NEW — full mental model
- `docs/per-cli/PLUGIN-FORMAT-RESEARCH.md` NEW — per-CLI schema findings
- CODEOWNERS, CONTRIBUTING.md, SECURITY.md NEW (repo standards)
- CHANGELOG.md updated with v3.0.0-dev entry

### v2 components retained

- AGENT-INSTRUCTIONS.md (canonical session ritual) — unchanged
- 5+7+8 compliance arch (HARD-RULES + ON-DEMAND + REFERENCE)
- OurVoice corpus (60 paragraphs, 12 cells) — same content, moved to `scaffolding/03-ms-team/voice/`
- Voice tier mechanism (internal / trailblazer / mixed)
- v1_alias frontmatter (retained until v3.5 retire)
- install.sh / install.ps1 / verify.sh (unchanged in this phase — Phase 5b update pending)

### Counts final (post-Phase 5a)

- Skills: 81 (47 foundation + 27 ms-team + 7 new session-harness)
- Agents: 78 (across 9 categories)
- Hooks: 15
- Plugin manifests: 7 (Claude, Codex, Cursor, Gemini, OpenCode, Copilot CLI, Droid)
- Root entrypoint files: 3 (CLAUDE.md, AGENTS.md, GEMINI.md)
- Bin scripts: 6 (scaffold, doctor, lessons-sync, lessons-promote, adr-new, update)
- Scaffolding template tree: 01-foundation (CORE-PRINCIPLES, EVOLUTION, tasks/, docs/adr/, .claude/agents/) + 02-sdl (compliance refs) + 03-ms-team (voice corpus + doc-gen templates)

### Remaining for v3.0.0 tag (Phases 7-9)

- Phase 5b: install.sh + verify.sh extensions for plugin-manifest validation
- Phase 7: tests for plugin-manifests + scaffolding-copy + CI matrix updates
- Phase 8: voice corpus calibration (operator-driven) + marketplace submission
- Phase 9: ship gate v3 + tag v3.0.0

### Operator next steps

1. Push `v3-dev` branch to GitHub
2. Test plugin install in Claude Code via `/plugin marketplace add jokerman89/jokerman-lintel`
3. Test `bin/li-scaffold` in a new repo
4. Run T0 voice calibration
5. Submit to Anthropic + OpenAI + Cursor + Gemini marketplaces (post MS legal review)

---

## 2026-05-27 — v2.0 spec-complete (Big Bang)

**Lintel v2: scaffolding-only harness for MS-CAIP-SE engagements.** No runtime code; the scaffolding ITSELF is Lintel. Operator (or agent reading SKILL.md) executes the work. v1 → v2 is a Big Bang ship with 5 components, eng-review-cleared.

### Naming migration (Phase A)

- 24 skills renamed to mirror MS process: `/ship` → `/release-ev2`, `/compliance-gate` → `/onecs-check`, `/sensitive-use-report` → `/rais-sensitive-use`, `/lintel:li-test` → `/onebranch-validate`, etc. Full table in [MIGRATION-TABLE.md](MIGRATION-TABLE.md).
- 2 agents renamed: `MSComplianceAuditor` → `OneCSAuditor`; `EvalSuiteAuthor` → `CloudTestSuiteAuthor`.
- 5 voice docs renamed: `TRAILBLAZER-*.md` → `OurVoice-*.md` (matches canonical MS guide title).
- Directory rename: `scaffolding/02-compliance/` → `scaffolding/02-sdl/` (matches SDL framing).
- ~130 markdown files updated with v2 references via global sed.
- `v1_alias:` frontmatter field added to all renamed skills + agents. Aliases retained until v2.5.

### Portability shim (Phase B)

- New: [CLI-SUPPORT-V2-SCHEMA.md](scaffolding/01-foundation/CLI-SUPPORT-V2-SCHEMA.md) — formal per-CLI degradation grammar (full / degraded / not-supported × claude-code / codex / copilot-cli / copilot-app).
- New skill: `/lintel:li-cli-fingerprint` — 5-step CLI detection cascade with operator-declarable fallback.
- v1 cli_support arrays still parse correctly (backward compat).

### 1M context budget engine (Phase C)

- New: [CONTEXT-ENGINE.md](CONTEXT-ENGINE.md) — phase-declaration grammar, budget tracker semantics, watcher thresholds (80%/100%), decay policies, warmup-task pattern, outcome scoring, cost tracking. **Soft enforcement only in v2.0** per eng-review P1; hard enforcement deferred to v2.0.5.
- New skills: `/context-budget`, `/context-warmup`, `/perf-mode`.
- Rename: `/context-tokenwatch` → `/context-budgetwatch`.
- New agent: `ContextBudgetAdvisor` (Layer 4) — suggests phase declarations for unstructured tasks.

### T0 voice calibration (Phase D)

- New: [T0-CALIBRATION-WORKFLOW.md](T0-CALIBRATION-WORKFLOW.md) — operator workflow for moving Trailblazer corpus from POPULATED → CALIBRATED. Pre-flight smoke-test recipe + per-cell iteration + cell-drop decision.
- Calibration is operator-driven (requires actual LLM-eval calls); Lintel documents the recipe.

### Brand integration (Phase E)

- New: [BRAND-INTEGRATION.md](BRAND-INTEGRATION.md) — MS brand asset architecture, cache invalidation, staleness watcher.
- New skills: `/brand-update`, `/asset-search`.
- New hook: `brand-staleness-warn` (warn-only at >90 days).
- Default fallback templates (per eng-review P1 fix T3): `scaffolding/03-personal-advanced/doc-gen/default-templates/default-{ppt,word,web}-template.{json,html}`. Doc-gen runtime works regardless of operator brand-pull status.

### MS-proprietary doc-gen (Phase F)

- New skills: `/generate-ppt`, `/generate-word`, `/generate-word`, `/generate-web`. 4-gate quality pipeline per output: voice (`/rais-customer-voice-check`) + brand-conformance + honest-limitations + provenance (`/provenance-track`).
- New agents: `PPTNarrativeArchitect`, `WordTechnicalEditor`, `WebExperienceCritic`.
- Library choices locked (skill-level instructions): pptx-genjs (PPT), docx-templater (Word), native HTML/Next.js (Web).

### Ship gate v2 (Phase G)

- [SHIP-GATE.md](SHIP-GATE.md) extended to **12 gates** (10 v1 + Gate 11 doc-gen quality + Gate 12 context-engine readiness).
- `install/verify.sh` extended with 3 new subcommands: `--portability`, `--context-engine`, `--brand`.
- Backward-compat: `verify.sh --voice` and `--compliance` accept both v1 (TRAILBLAZER-*, 02-compliance/) and v2 (OurVoice-*, 02-sdl/) paths.

### Tests infrastructure (P1 fix T2)

- `tests/{unit,integration,e2e,fixtures,runner,conventions}/` structure created.
- `tests/conventions/bash-test-template.sh` — tagged template with assert helpers (assert_eq, assert_file_exists, assert_contains).
- `tests/runner/{run-all,run-unit,run-e2e}.sh` — discovery + tag-filter dispatch.
- `tests/unit/phase-a-naming-migration.sh` — first test, validates Phase A integrity (currently passes 1/1).
- `.github/workflows/ci.yml` extended with 3 new jobs: `unit-tests-linux`, `unit-tests-windows`, `e2e-claude-code-only`.

### Final counts

- **Skills:** 74 (47 Layer 1 + 27 Layer 3)
- **Agents:** 44 (18 Layer 3 promoted + 26 Layer 4 power-user)
- **Hooks:** 15 (12 warn + 2 BLOCK + 1 v2-new brand-staleness)
- **Compliance/voice docs:** 11
- **Top-level v2 design docs:** 5 (MIGRATION-TABLE, CLI-SUPPORT-V2-SCHEMA, CONTEXT-ENGINE, T0-CALIBRATION-WORKFLOW, BRAND-INTEGRATION)
- **Default doc-gen templates:** 3 (PPT JSON, Word JSON, Web HTML)
- **CI jobs:** 7 (4 v1 + 3 v2)
- **Verify.sh subcommands:** 13 (10 v1 + 3 v2)

### Verify status (post-Phase G)

- `bash tests/runner/run-all.sh` → 1/1 PASS
- `bash install/verify.sh --all` → exit 0, ALL CHECKS PASSED
- T0 calibration: NOT CALIBRATED (operator-driven; recipe in T0-CALIBRATION-WORKFLOW.md)
- Hook activation: 0/15 activated locally (expected; operator-driven symlink opt-in)

### Operator path to v2.0.0 tag

Per [SHIP-GATE.md](SHIP-GATE.md) — 12 gates. Remaining work after this spec-complete commit:
1. Run T0-CALIBRATION-WORKFLOW.md → CALIBRATED status (Gate 3)
2. Pull MS brand assets to `~/.lintel/brand/` (Gate 11 prerequisite)
3. CAIP-SE teammate adoption test (Gate 6)
4. Codex outside-voice review (Gate 5)
5. Upstream similarity check T-303 (Gate 7)
6. CI green on next push (Gate 9)
7. When all green: `git tag v2.0.0 && git push origin v2.0.0`

---

## 2026-05-26 — Initial release

- Repo created at `~/Workspace/jokerman-lintel/` on `main` branch.
- Scaffolding extracted from `claude-scaffolding` and adapted (refs updated to `jokerman-lintel`).
- Multi-CLI shim architecture: canonical `AGENT-INSTRUCTIONS.md` + per-CLI shims under `shims/` for Claude Code, GitHub Copilot Enterprise, and Codex CLI.
- Install scripts for bash (`install/install.sh`) and PowerShell 7+ (`install/install.ps1`).
- `install/upstream-sources.yaml` declares 8 upstream sources across 3 tiers (permissive / restricted / reference-only):
  - **Permissive (MIT):** gstack, GSD Redux, AgentShield, ECC.
  - **Restricted:** Trail of Bits skills (CC-BY-SA-4.0), Anthropic skills (mixed Apache-2.0 + source-available).
  - **Reference-only:** Trail of Bits claude-code-config, Anthropic plugins-official.
- New scaffolding files added on top of the `claude-scaffolding` base: `tasks/memory.md`, `tasks/personas.md`, `docs/adr/README.md`, `docs/adr/TEMPLATE.md`, `docs/personas/EXAMPLE.md`.
- Documentation: `README.md`, `getting-started.md`, `multi-cli.md`, `compliance.md`, `promoted-agents.md`, `precedence.md`, `power-user.md`, `faq.md`.
- MIT license (with `LICENSE` note explaining that installed upstreams keep their own licenses).
- `.gitignore` excludes session data, secrets, customer-data-likely paths, and common dev artifacts.
