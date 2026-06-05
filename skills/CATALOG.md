# Lintel Skill Catalog

Auto-generated från frontmatter på push till main.
Regenerated av `.github/workflows/catalog.yml` per push när `skills/**/SKILL.md` ändras.
Hand-edits skrivs över — edit frontmatter i source SKILL.md istället.

Total skills: 168
Generated: 2026-06-05T08:27:39Z

## foundation layer (168 skills)

| Skill | Description |
|---|---|
| `/li:adr-new` | Bootstrap a new ADR (Architecture Decision Record) from template, with context-gathering questions. |
| `/li:audit` | Read the unified Lintel audit trail — surface ~/.lintel/audit/<category>.jsonl records with optional category / kind / |
| `/li:autoplan` | Chains office-hours → ceo-review → eng-review → design-review. End-to-end plan pipeline. |
| `/li:brief-forge` | Phase 3 v4.0 — universal hand-off gate. Constructs envelopes per lib/envelope-schema.yaml + runs evaluators on every s |
| `/li:browse` | Drive a headless Chromium to a URL — screenshot, extract DOM, click, fill forms, verify UI. |
| `/li:build` | Phase 5 of Lintel cycle — execute plan via TDD + subagent-driven-development. Fresh subagent per task with two-stage r |
| `/li:capture` | Phase 8 of Lintel cycle — durable capture. Lessons updated, ADR drafted, EVOLUTION-LOG appended, cold-executor handoff |
| `/li:careful` | Slow-down mode for high-stakes work — extra gates, double-confirm before mutations. |
| `/li:catalog` | Auto-generate skills/CATALOG.md från frontmatter-parse. Discoverability-fix per Cohort 2 item 1.6 (REPLACED — aldrig  |
| `/li:clean` | Manual self-maintenance trigger. Suggests /context-save + restart when session feels heavy. |
| `/li:cli-fingerprint` | Detect which CLI is running Lintel — env-var → process → tool-probe → config fallback. |
| `/li:code-freeze` | Mark paths as DO-NOT-MODIFY for this session — other skills check + refuse to touch. |
| `/li:review` | Diff-scoped pre-landing code review. Lighter than /plan-eng-review, focused on changed code only. |
| `/li:code-unfreeze` | Remove a path from session freeze — other skills can write to it again. |
| `/li:codex` | Outside-voice second opinion via Codex CLI. Independent review of diff, plan, or hypothesis. |
| `/li:compliance-gate` | Compliance-gate aggregator — kör alla gates som active pack deklarerar (compliance.hooks) som EN green/red verdict. P |
| `/li:context-budget` | Show current context utilization, recommend warm/cool, surface budget breakdown by source. |
| `/li:context-budgetwatch` | Manual context-bloat check — token + tool-call thresholds, recommendation to /clean or /context-save. |
| `/li:context-cool` | Selectively drop context from session — free budget for further warming. Operator picks what to keep. |
| `/li:context-dump` | Read prior session's context-save output and inject into current session. Cross-session memory recovery. |
| `/li:context-restore` | Restore session state from a checkpoint file. Run at start of a fresh session that continues prior work. |
| `/li:context-save` | Save current session state to a checkpoint file. Use before context bloat or before /clean. |
| `/li:context-snapshot` | Save current context state to disk — operator-named snapshot for later resume via /li:context-dump. |
| `/li:context-warm-adrs` | Load topic-relevant ADRs into context — design constraints + prior decisions surfaced for current work. |
| `/li:context-warm-customer` | Load customer-engagement repo state into context — customer's Bicep, their CLAUDE.md, their ADRs, recent commits. |
| `/li:context-warm-from-url` | Fetch URL + dump into context. Useful for loading documentation, blog posts, external references on-demand. |
| `/li:context-warm-related` | Heuristic context warm — search codebase for files related to a topic, load top N most-relevant. |
| `/li:context-warm-sessions` | Load last N session saves on current branch — cross-session continuity for resumed work. |
| `/li:context-warm` | Load specified files into session context — on-demand 1M-window utilization. Reports tokens added + budget impact. Bas |
| `/li:context-warmup` | Explicit preload of high-leverage context per declared warmup pattern. |
| `/li:cycle` | Lintel cycle orchestrator — runs full 8-phase pipeline (SENSE → CAPTURE) or operator-specified subset. Mode presets, |
| `/li:da-analytics-readiness` | DA sub-skill — OLAP path, dimensional model, ETL boundaries. Dispatches to DataPipelineDesigner + SchemaArchitect (NEW |
| `/li:da-data-contract-collision` | DA sub-skill — schema change impact analysis across consumers. Dispatches to DatabaseDesigner + Architect. Raises help |
| `/li:da-migration-plan` | DA sub-skill — reversible migration with zero-downtime path. Dispatches to MigrationPlanner (NEW) + Migrator. Raise-he |
| `/li:da-query-pattern-audit` | DA sub-skill — read/write ratios, hot paths, missing indexes. Dispatches to DatabaseDesigner + Explorer. |
| `/li:da-retention-policy` | DA sub-skill — per-data-class retention + archival + deletion policy. Dispatches to DatabaseDesigner + Architect. Rais |
| `/li:da-schema-design` | DA sub-skill — schema definitions with versioning + relationships. Dispatches to DatabaseDesigner + SchemaArchitect ag |
| `/li:da-sharding-plan` | DA sub-skill — partitioning strategy + rebalancing approach. Dispatches to SchemaArchitect (NEW) + DatabaseDesigner. |
| `/li:da` | Phase 4 v4.2 — data-architecture module. Three granularities (full / loop / single). Sub-skills dispatch to existing d |
| `/li:define` | Phase 2 of Lintel cycle — clarify intent, lock premises, force alternatives, pick wedge. Office-hours-style forcing qu |
| `/li:design-consultation` | Conversational design-system advisor — answer systems-level questions with grounded recommendations. |
| `/li:design-html` | Generate a single-file static HTML mockup from a brief — opens with /open-managed-browser. |
| `/li:design-review` | 6-pillar visual review of frontend changes — screenshot via /browse, scored findings. |
| `/li:design-shotgun` | Parallel design exploration — spawn N variants of a seed HTML, present side-by-side. |
| `/li:devex-review` | Review the built developer experience — scripts, onboarding, error messages, time-to-hello-world. |
| `/li:dh-capacity-headroom` | DH sub-skill — headroom margins + alert thresholds + scaling triggers. Dispatches to CapacityPlanner + LatencyAnalyzer |
| `/li:dh-cost-projection` | DH sub-skill — per-component cost projection + anomaly detection thresholds. Dispatches to CostAnalyzer + CapacityPlan |
| `/li:dh-deployment-plan` | DH sub-skill — deployment pattern + traffic cutover + feature-flag strategy. Dispatches to ReleaseEngineer + Deploymen |
| `/li:dh-observability-spec` | DH sub-skill — metrics + traces + logs + dashboards per component. Dispatches to ObservabilityArchitect (NEW) + Archit |
| `/li:dh-on-call-playbook` | DH sub-skill — per-failure-mode runbook + escalation matrix. Dispatches to ReleaseEngineer + SecurityAuditor agents. |
| `/li:dh-rollback-strategy` | DH sub-skill — rollback mechanics + blast-radius limiting + hot-swap path. Dispatches to ReleaseEngineer + SecurityAud |
| `/li:dh-sli-slo-spec` | DH sub-skill — SLI definitions + SLO budgets + error budget policy. Dispatches to ObservabilityArchitect (NEW) + Syste |
| `/li:dh` | Phase 4 v4.4 — devops-hosting module. Three granularities (full / loop / single). Sub-skills dispatch to existing ops  |
| `/li:discover` | Phase 3 of Lintel cycle — map codebase, surface ADRs, apply lessons, identify reusable patterns + agents/skills releva |
| `/li:doctor` | Cross-CLI health check — verifies which CLIs are installed, plugin install status, Lintel version, and surfaces drift. |
| `/li:document-generate` | Generate documentation from code — engineering reference, customer guides, or onboarding tutorials. |
| `/li:eval` | Run the active pack's voice TEST against its voice CORPUS — per-cell accuracy → CALIBRATION.md. |
| `/li:fix` | Composite shortcut for hotfix workflow — runs SENSE + BUILD + REVIEW + SHIP, skipping DEFINE/DISCOVER/PLAN/CAPTURE. Fo |
| `/li:frontend-design-review` | Quality gate för produced frontend designs. 6-dimension audit (typography hierarchy + motion coherence + shader perf-bu |
| `/li:frontend-design` | Frontend design-director orchestrator. Chains typography + motion (+ shader in Fas A2) → frontend-design-spec.json → |
| `/li:frontend-motion` | Frontend design-director sub-skill — picks motion-language (GSAP/Lenis/Theatre/Rive/Motion-One) + scroll-trigger-confi |
| `/li:frontend-shader` | Frontend design-director sub-skill — picks shader library (Paper Shaders / OGL / react-three-fiber / Lygia) + visual t |
| `/li:frontend-style-extract` | Pattern-level extraction sister till generate-style-learn. Reads artifacts (URLs, screenshots, .tsx files) → extracts  |
| `/li:frontend-typography` | Frontend design-director sub-skill — picks font-family-stacks + variable-axes-config + size-scale + line-heights + fon |
| `/li:full-engineering-pass` | v4.6 (v4.x feature-complete) — composes all 5 engineering-domain modules in DAG order (TA → DA‖SC → DH → TQ).  |
| `/li:gbrain-setup` | Configure gbrain semantic-index integration — initialize config, pin worktree, register sync. |
| `/li:gbrain-sync` | Refresh the gbrain index from the current worktree — incremental or full. |
| `/li:generate-app` | Full-app scaffold-orchestrator. Reads frontend-design-spec.json + generates vite-react/next-app/svelte-kit project skele |
| `/li:generate-design` | Produce design-spec.json (per-format layout-mappings + palette + fonts + asset placements) from content.md. Shared conte |
| `/li:generate-outline` | Produce outline.md (structured presentation/document skeleton) from a brief. Shared content-pipeline sub-skill, solo-inv |
| `/li:generate-pdf` | ⚠ TEMPLATE ONLY — Slot for PDF document generation. Content not curated. AI generates fresh at invocation per L-001. |
| `/li:generate-ppt` | Produce brand-compliant PowerPoint deck via pptx-genjs, 4-gate quality pipeline. |
| `/li:generate-qa` | Validate generated artifacts (any format) against brand, voice, readability, and structure standards. Auto-fixes where p |
| `/li:generate-style-learn` | Analysera .pptx/.docx/web-examples och extrahera reusable style palette. v3.5 Fas 3 av doc-generation-pipeline. |
| `/li:generate-visio` | ⚠ TEMPLATE ONLY — Slot for Visio diagram generation (architecture sketches, network topologies, process flows). Cont |
| `/li:generate-web` | Produce brand-compliant static HTML or Next.js scaffold for demo/landing page. |
| `/li:generate-word` | Produce brand-compliant Word doc via docx-templater — technical / customer-summary / transparency-note variants. |
| `/li:generate-write` | Produce content.md (slide/section bodies + bullets + titles) and speaker-notes.md from outline.md. Applies voice corpus. |
| `/li:generate-xlsx` | ⚠ TEMPLATE ONLY — Slot for Excel spreadsheet generation (data + estimates + tables). Content not curated. AI generat |
| `/li:generate` | Multi-format document generation orchestrator. Chains shared content pipeline (outline → write → design → qa) + pe |
| `/li:handoff-size-check` | Handoff-size-warning tied to 500k cap. Per v3.6 backlog 3.2 — elephant-hint och token-cap som samma mekanism från tv� |
| `/li:health` | Lintel install + upstream status check. Verifies layers, manifest, hooks, upstream pins, CLI shims. |
| `/li:help` | List installed Lintel skills + agents + hooks. Filter by category, voice tier, or CLI support. |
| `/li:hooks-status` | Reader för hooks.jsonl — surface aktiva-vs-döda hooks + override-pattern + trigger-counts. Stänger hooks-observatio |
| `/li:instruction-parity-check` | Verifierar substance-parity över 6 instruktionsfiler (root CLAUDE/AGENTS/GEMINI + shims). Multi-CLI promise's weak poin |
| `/li:investigate` | Hypothesis-driven bug investigation — minimum repro, eliminate variables, root cause. |
| `/li:jobs` | Curated-flow lifecycle controller — list / continue / replan / abort / branch in-flight Lintel jobs. Single source of  |
| `/li:landing-report` | Post-ship report — what landed in a window, in engineering or customer-voice format. |
| `/li:learn` | Record an insight, correction, or pattern as a lesson — readable at future session start. |
| `/li:lessons-promote` | Promote a repo-local lesson from tasks/lessons.md to Lintel's global lessons (scaffolding/01-foundation/tasks/lessons.md |
| `/li:lessons-surface` | Surface relevanta lessons.md-entries baserat på keyword/context. STÄNGER L-001/L-002-LOOPEN (lessons skrivs men läses |
| `/li:lessons` | Mid-session review of accumulated lessons from tasks/lessons.md — surfaces relevant ones for current task. |
| `/li:maintenance` | On-demand maintenance — force-compact + static-path monitoring + token-cost simulation. Operator-request 5.3. Bygger p |
| `/li:make-pdf` | Convert URL, markdown file, or HTML to PDF via managed Chromium. |
| `/li:migrations` | Surface pending v4.x migrations at SENSE. Sister to /li:status. Read-only — surfaces operator-callsites still on depre |
| `/li:office-hours` | Generate a design doc from a problem statement — structured, decision-gated, ready for /plan-eng-review. |
| `/li:open-managed-browser` | Open the Lintel-managed Chromium in headed mode — interactive operator session. |
| `/li:orientator` | Phase 3 v4.0 — lightweight routing agent invoked at SENSE. Reads operator prompt + active pack's navigation policy, re |
| `/li:pack-create` | Scaffolds a new Lintel pack — copies _default pack.yaml as starting point, optionally sets extends parent, validates r |
| `/li:pack-list` | Lists every pack discoverable in ~/.lintel/packs/ and repo packs/ — shows name, extends, voice tier, compliance mode,  |
| `/li:pack-switch` | Switches the active pack — writes ~/.lintel/packs/active-pack, validates the target, audits the switch. |
| `/li:pack-validate` | Validates a pack manifest against lib/pack-schema.yaml — required fields, extends-chain, version compatibility. Report |
| `/li:pair-agent` | Pair with a named subagent in the loop — explicit two-mind collaboration on a focused task. |
| `/li:perf-mode` | Activate 1M context-budget mode for the session — "tuffa faser" preset. |
| `/li:perfbench` | Measure performance — runtime, memory, cold-start — and detect regressions vs baseline. |
| `/li:personas-rotate` | Load persona context from tasks/personas.md for demo-prep, workshop-facilitation, or audience-aware writing. |
| `/li:plan-and-build` | Composite shortcut PLAN + BUILD — for when DEFINE+DISCOVER are done (have design doc) but PLAN and BUILD still need ex |
| `/li:plan-ceo-review` | Strategy + scope review. Surface product/business assumptions before architecture lands. |
| `/li:plan-design-review` | UI/UX gaps review for plans with a frontend surface. Skip for backend/infra/CLI-only work. |
| `/li:plan-devex-review` | Developer experience gaps review. Slow CI, painful deploys, bad local dev, attrition signals. |
| `/li:plan-eng-review` | Architecture + tests review. The required gate before ship. Covers arch, code quality, test coverage, performance. |
| `/li:plan-tune` | Adjust which AskUserQuestion prompts auto-decide vs ask. Per-question preference tuning. |
| `/li:plan` | Phase 4 of Lintel cycle, ALSO callable standalone as a planner module (v3.8 Feature 2). Produces the cold-executor trio  |
| `/li:profile-switch` | Toggle Lintel install on/off fast + swap till previous setup utan att röra repot. Operator-request 5.2. |
| `/li:qa-only` | Read-only test run — reports failures, never edits. For ship-gate verification. |
| `/li:qa` | Run the full test suite, parse failures, fix common ones, re-run until clean or stuck. |
| `/li:research` | Composite shortcut for research-dive — runs SENSE + DEFINE + DISCOVER, no BUILD/SHIP. For "understand before commit" m |
| `/li:resume` | Resume Lintel cycle from prior session — reads 00-state.md, picks up at next-recommended phase or operator-specified.  |
| `/li:retro` | Session retrospective — what shipped, what got stuck, what to /learn from. |
| `/li:review-and-ship` | Composite shortcut REVIEW + SHIP + CAPTURE — for when BUILD is done and operator wants to finalize, ship, capture in o |
| `/li:review` | Phase 6 of Lintel cycle — adversarial review of BUILD output across 3 stages (spec compliance, code quality, the activ |
| `/li:role-activate` | Activate a role for the current session — loads role IDENTITY + voice + outcome-lens (LIGHTWEIGHT ~500 tokens). Deep-d |
| `/li:role-deactivate` | Remove active role from session — clears overlay, voice tier reverts to mode/profile default. |
| `/li:role-deep-dive` | Load full role-file content on-demand — COLD KNOWLEDGE, DECISION CRITERIA, INSIGHTS, OUTCOME LENS per phase. For when  |
| `/li:role-frame` | Apply active role's outcome-lens to an artifact (design doc, proposal, plan). Surfaces what role would notice, recommend |
| `/li:role-new` | Scaffold a new role file from template — guided questions populate IDENTITY, COLD KNOWLEDGE, DECISION CRITERIA, OUTCOM |
| `/li:role-rotate` | Swap active role mid-session — deactivate current, activate new. Preserves session memory but shifts overlay. |
| `/li:role-update` | Add learning to existing role file (sensitivity-aware) — captures new INSIGHT, refines voice phrasing, updates COLD KN |
| `/li:roles-list` | List all available roles (public + private, if accessible). Shows id, display name, scope, sensitivity, last-updated. |
| `/li:safe-install` | Safe-install wrapper för Lintel — version-before-every-change + uninstall-with-restore + visible-announce backup. Ope |
| `/li:sc-audit-path` | SC sub-skill — audit log design with retention + integrity. Dispatches to SecurityAuditor + Architect agents. |
| `/li:sc-auth-flow` | SC sub-skill — auth design with security review verdict. Dispatches to JWTSecurityReviewer + SecurityAuditor agents. |
| `/li:sc-compliance-evidence` | SC sub-skill — per-framework (SOC2/GDPR/HIPAA/etc.) evidence collection. Dispatches to ComplianceOfficer (NEW) + Archi |
| `/li:sc-dependency-security` | SC sub-skill — SCA + license + vulnerability gates. Dispatches to DependencyAuditor + SBOMAuditor agents. |
| `/li:sc-incident-runbook` | SC sub-skill — response runbook for the new surface. Dispatches to SecurityAuditor + ReleaseEngineer agents. |
| `/li:sc-secret-management` | SC sub-skill — secret inventory + rotation policy + secret-scan integration. Dispatches to SecurityAuditor + SBOMAudit |
| `/li:sc-threat-model` | SC sub-skill — STRIDE / attack-tree threat enumeration with mitigations. Dispatches to ThreatModelDrafter + SecurityAu |
| `/li:sc` | Phase 4 v4.3 — security-compliance module. Three granularities (full / loop / single). Sub-skills dispatch to existing |
| `/li:scaffold-internal-tool` | Initialize an internal-tooling repo — CI, README, pack compliance hooks, no customer surface. |
| `/li:scaffold-mvp` | Initialize a product-MVP repo — full structure + pack-driven compliance/voice/deploy wiring. |
| `/li:scaffold` | Scaffold a new repo with Lintel base templates — CLAUDE.md, tasks/lessons.md, EVOLUTION-LOG, docs/adr/ — interactive |
| `/li:scope` | Phase 1.5 of Lintel cycle — runs between SENSE and DEFINE. Turns a raw request into a sized, disambiguated scope via t |
| `/li:scrape` | Extract structured data from one or more pages — declarative selector schema, JSON output. |
| `/li:sense` | Phase 1 of Lintel cycle — auto-detect operator intent, pack compliance mode, active role, mode recommendation, 00-stat |
| `/li:setup-browser-cookies` | Bootstrap auth cookies for the managed Chromium profile — operator-driven, one-time per service. |
| `/li:ship` | Phase 7 of Lintel cycle — PR / deploy / customer handoff. Final compliance hard-stops (the active pack's gates; none b |
| `/li:skill-router` | Semantic skill router — given free-text user intent, suggests top 3 matching Lintel skills with rationale. |
| `/li:skillify` | Turn a recurring task or pattern into a new Lintel skill — scaffolds SKILL.md from TEMPLATE. |
| `/li:status` | Show what's open right now — alias for /li:jobs list. Single command for "where am I in flight?". |
| `/li:ta-api-design` | TA sub-skill — REST/GraphQL/gRPC interface design with versioning + breaking-change analysis. Dispatches to APIDesigne |
| `/li:ta-boundary-review` | TA sub-skill — bounded-context drift detection, leaking-abstraction flags. Dispatches to BackendArchitect + Architect. |
| `/li:ta-complexity-audit` | TA sub-skill — per-component cyclomatic + cognitive complexity scoring. Reads pack/profile thresholds. Dispatches to C |
| `/li:ta-contract-collision` | TA sub-skill — change-impact analysis across consumers of an interface. Dispatches to APIDesigner + Architect. |
| `/li:ta-dependency-graph` | TA sub-skill — module dependency map, circular-detection, layering audit. Dispatches to Architect + Explorer agents. P |
| `/li:ta-quality-attributes` | TA sub-skill — non-functional requirement spec (latency, throughput, reliability, observability). Dispatches to System |
| `/li:ta-scaling-plan` | TA sub-skill — capacity model + bottleneck identification + cost projection. Dispatches to CapacityPlanner (NEW) + Bac |
| `/li:ta` | Phase 4 v4.1 — tech-architecture module. Three granularities (full / loop / single). Sub-skills dispatch to existing a |
| `/li:tq-chaos-plan` | TQ sub-skill — failure injection scenarios + dependency-chaos + recovery validation. Dispatches to SecurityAuditor + S |
| `/li:tq-contract-test-design` | TQ sub-skill — consumer-driven contract tests + schema-versioning tests. Dispatches to APIDesigner + ContractTestArchi |
| `/li:tq-coverage-audit` | TQ sub-skill — critical-path coverage + branch coverage + mutation testing report. Dispatches to TestRunner + Architec |
| `/li:tq-flaky-quarantine` | TQ sub-skill — flaky test detection + quarantine + remediation plan. Dispatches to TestRunner + RegressionDetective. |
| `/li:tq-perf-budget-spec` | TQ sub-skill — per-journey perf budget + regression detection thresholds. Dispatches to LatencyAnalyzer + PerfBudgetEn |
| `/li:tq-regression-suite` | TQ sub-skill — golden-path tests + recent-bug-fix tests curated. Dispatches to RegressionDetective + TestRunner agents |
| `/li:tq-test-pyramid-review` | TQ sub-skill — unit/integration/e2e ratio audit + test-distribution health. Dispatches to Architect + TestRunner. |
| `/li:tq` | Phase 4 v4.5 — testing-qa module. Three granularities (full / loop / single). Sub-skills dispatch to existing test age |
| `/li:uniformity` | Read-only uniformity-contract dashboard — runs the Gate-M3 floor shape-test and points at the regenerable coverage mat |
| `/li:usage-log` | Append-only usage log för skill/agent-invocations. Wrapper-pattern per L-001 (en log, ingen per-skill duplikat). Solo-i |
| `/li:v4-migrate` | Walks operator through v3.x → v4.0 migration — detects v3.x usage signals, recommends pack activation, optionally wr |

