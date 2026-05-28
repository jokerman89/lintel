# Lintel Skill Catalog

Auto-generated från frontmatter på push till main.
Regenerated av `.github/workflows/catalog.yml` per push när `skills/**/SKILL.md` ändras.
Hand-edits skrivs över — edit frontmatter i source SKILL.md istället.

Total skills: 131
Generated: 2026-05-28T15:52:04Z

## foundation layer (92 skills)

| Skill | Description |
|---|---|
| `/li:adr-new` | Bootstrap a new ADR (Architecture Decision Record) from template, with context-gathering questions. |
| `/li:autoplan` | Chains office-hours → ceo-review → eng-review → design-review. End-to-end plan pipeline. |
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
| `/li:context-budget` | Show current context utilization, recommend warm/cool, surface budget breakdown by source. |
| `/li:context-cool` | Selectively drop context from session — free budget for further warming. Operator picks what to keep. |
| `/li:context-dump` | Read prior session's context-save output and inject into current session. Cross-session memory recovery. |
| `/li:context-restore` | Restore session state from a checkpoint file. Run at start of a fresh session that continues prior work. |
| `/li:context-save` | Save current session state to a checkpoint file. Use before context bloat or before /clean. |
| `/li:context-snapshot` | Save current context state to disk — operator-named snapshot for later resume via /li:context-dump. |
| `/li:context-warm-adrs` | Load topic-relevant ADRs into context — design constraints + prior decisions surfaced for current work. |
| `/li:context-warm-customer` | Load customer-engagement repo state into context — customer's Bicep, their CLAUDE.md, their ADRs, recent commits. |
| `/li:context-warm-from-url` | Fetch URL + dump into context. Useful for loading Microsoft Learn docs, blog posts, external references on-demand. |
| `/li:context-warm-related` | Heuristic context warm — search codebase for files related to a topic, load top N most-relevant. |
| `/li:context-warm-sessions` | Load last N session saves on current branch — cross-session continuity for resumed work. |
| `/li:context-warm` | Load specified files into session context — on-demand 1M-window utilization. Reports tokens added + budget impact. Bas |
| `/li:context-warmup` | Explicit preload of high-leverage context per declared warmup pattern. |
| `/li:cycle` | Lintel cycle orchestrator — runs full 8-phase pipeline (SENSE → CAPTURE) or operator-specified subset. Mode presets, |
| `/li:define` | Phase 2 of Lintel cycle — clarify intent, lock premises, force alternatives, pick wedge. Office-hours-style forcing qu |
| `/li:design-consultation` | Conversational design-system advisor — answer systems-level questions with grounded recommendations. |
| `/li:design-html` | Generate a single-file static HTML mockup from a brief — opens with /open-managed-browser. |
| `/li:design-review` | 6-pillar visual review of frontend changes — screenshot via /browse, scored findings. |
| `/li:design-shotgun` | Parallel design exploration — spawn N variants of a seed HTML, present side-by-side. |
| `/li:devex-review` | Review the built developer experience — scripts, onboarding, error messages, time-to-hello-world. |
| `/li:discover` | Phase 3 of Lintel cycle — map codebase, surface ADRs, apply lessons, identify reusable patterns + agents/skills releva |
| `/li:doctor` | Cross-CLI health check — verifies which CLIs are installed, plugin install status, Lintel version, and surfaces drift. |
| `/li:document-generate` | Generate documentation from code — engineering reference, customer guides, or onboarding tutorials. |
| `/li:fix` | Composite shortcut for hotfix workflow — runs SENSE + BUILD + REVIEW + SHIP, skipping DEFINE/DISCOVER/PLAN/CAPTURE. Fo |
| `/li:health` | Lintel install + upstream status check. Verifies layers, manifest, hooks, upstream pins, CLI shims. |
| `/li:help` | List installed Lintel skills + agents + hooks. Filter by category, voice tier, or CLI support. |
| `/li:hooks-status` | Reader för hooks.jsonl — surface aktiva-vs-döda hooks + override-pattern + trigger-counts. Stänger hooks-observatio |
| `/li:investigate` | Hypothesis-driven bug investigation — minimum repro, eliminate variables, root cause. |
| `/li:landing-report` | Post-ship report — what landed in a window, in engineering or customer-voice format. |
| `/li:learn` | Record an insight, correction, or pattern as a lesson — readable at future session start. |
| `/li:lessons-promote` | Promote a repo-local lesson from tasks/lessons.md to Lintel's global lessons (scaffolding/01-foundation/tasks/lessons.md |
| `/li:lessons-surface` | Surface relevanta lessons.md-entries baserat på keyword/context. STÄNGER L-001/L-002-LOOPEN (lessons skrivs men läses |
| `/li:lessons` | Mid-session review of accumulated lessons from tasks/lessons.md — surfaces relevant ones for current task. |
| `/li:maintenance` | On-demand maintenance — force-compact + static-path monitoring + token-cost simulation. Operator-request 5.3. Bygger p |
| `/li:make-pdf` | Convert URL, markdown file, or HTML to PDF via managed Chromium. |
| `/li:match` | Semantic skill router — given free-text user intent, suggests top 3 matching Lintel skills with rationale. |
| `/li:office-hours` | Generate a design doc from a problem statement — structured, decision-gated, ready for /plan-eng-review. |
| `/li:open-managed-browser` | Open the Lintel-managed Chromium in headed mode — interactive operator session. |
| `/li:pair-agent` | Pair with a named subagent in the loop — explicit two-mind collaboration on a focused task. |
| `/li:perf-mode` | Activate 1M context-budget mode for the session — "tuffa faser" preset. |
| `/li:perfbench` | Measure performance — runtime, memory, cold-start — and detect regressions vs baseline. |
| `/li:personas-rotate` | Load persona context from tasks/personas.md for demo-prep, workshop-facilitation, or audience-aware writing. |
| `/li:plan-and-build` | Composite shortcut PLAN + BUILD — for when DEFINE+DISCOVER are done (have design doc) but PLAN and BUILD still need ex |
| `/li:plan-ceo-review` | Strategy + scope review. Surface product/business assumptions before architecture lands. |
| `/li:plan-design-review` | UI/UX gaps review for plans with a frontend surface. Skip for backend/infra/CLI-only work. |
| `/li:plan-devex-review` | Developer experience gaps review. Slow CI, painful deploys, bad local dev, attrition signals. |
| `/li:plan-eng-review` | Architecture + tests review. The required gate before /release-ev2. Covers arch, code quality, test coverage, performanc |
| `/li:plan-tune` | Adjust which AskUserQuestion prompts auto-decide vs ask. Per-question preference tuning. |
| `/li:plan` | Phase 4 of Lintel cycle — convert design + discovery into executable task breakdown with cost estimate, dependency gra |
| `/li:profile-switch` | Toggle Lintel install on/off fast + swap till previous setup utan att röra repot. Operator-request 5.2. |
| `/li:qa-only` | Read-only test run — reports failures, never edits. For ship-gate verification. |
| `/li:qa` | Run the full test suite, parse failures, fix common ones, re-run until clean or stuck. |
| `/li:release-deploy-ev2` | /release-ev2 + deploy. Adds post-merge deploy trigger. Requires explicit per-call auth. |
| `/li:release-ev2` | Land the current branch — verifies review readiness, squashes WIP commits, opens PR. |
| `/li:research` | Composite shortcut for research-dive — runs SENSE + DEFINE + DISCOVER, no BUILD/SHIP. For "understand before commit" m |
| `/li:resume` | Resume Lintel cycle from prior session — reads 00-state.md, picks up at next-recommended phase or operator-specified.  |
| `/li:retro` | Session retrospective — what shipped, what got stuck, what to /learn from. |
| `/li:review-and-ship` | Composite shortcut REVIEW + SHIP + CAPTURE — for when BUILD is done and operator wants to finalize, ship, capture in o |
| `/li:review` | Phase 6 of Lintel cycle — adversarial review of BUILD output across 3 stages (spec compliance, code quality, complianc |
| `/li:role-activate` | Activate a role for the current session — loads role IDENTITY + voice + outcome-lens (LIGHTWEIGHT ~500 tokens). Deep-d |
| `/li:role-deactivate` | Remove active role from session — clears overlay, voice tier reverts to mode/profile default. |
| `/li:role-deep-dive` | Load full role-file content on-demand — COLD KNOWLEDGE, DECISION CRITERIA, INSIGHTS, OUTCOME LENS per phase. For when  |
| `/li:role-frame` | Apply active role's outcome-lens to an artifact (design doc, proposal, plan). Surfaces what role would notice, recommend |
| `/li:role-new` | Scaffold a new role file from template — guided questions populate IDENTITY, COLD KNOWLEDGE, DECISION CRITERIA, OUTCOM |
| `/li:role-rotate` | Swap active role mid-session — deactivate current, activate new. Preserves session memory but shifts overlay. |
| `/li:role-update` | Add learning to existing role file (sensitivity-aware) — captures new INSIGHT, refines voice phrasing, updates COLD KN |
| `/li:roles-list` | List all available roles (public + private, if accessible). Shows id, display name, scope, sensitivity, last-updated. |
| `/li:safe-deploy-ring` | Gate a deployed feature behind a percentage rollout — ramp up, monitor, abort safe. |
| `/li:safe-install` | Safe-install wrapper för Lintel — version-before-every-change + uninstall-with-restore + visible-announce backup. Ope |
| `/li:scaffold` | Scaffold a new repo with Lintel base templates — CLAUDE.md, tasks/lessons.md, EVOLUTION-LOG, docs/adr/ — interactive |
| `/li:scrape` | Extract structured data from one or more pages — declarative selector schema, JSON output. |
| `/li:sense` | Phase 1 of Lintel cycle — auto-detect operator intent, WorkProfile state, active role, mode recommendation, 00-state f |
| `/li:setup-brain` | Configure gbrain semantic-index integration — initialize config, pin worktree, register sync. |
| `/li:setup-browser-cookies` | Bootstrap auth cookies for the managed Chromium profile — operator-driven, one-time per service. |
| `/li:setup-ev2-targets` | Configure deploy targets for /release-deploy-ev2 — write targets, validate, register. |
| `/li:ship` | Phase 7 of Lintel cycle — PR / deploy / customer handoff. Final compliance hard-stops. Voice + brand + honest-limitati |
| `/li:skillify` | Turn a recurring task or pattern into a new Lintel skill — scaffolds SKILL.md from TEMPLATE. |
| `/li:sync-brain` | Refresh the gbrain index from the current worktree — incremental or full. |
| `/li:usage-log` | Append-only usage log för skill/agent-invocations. Wrapper-pattern per L-001 (en log, ingen per-skill duplikat). Solo-i |

## ms-team layer (38 skills)

| Skill | Description |
|---|---|
| `/li:agt-tier-stamp` | Stamp agents with license tier (permissive/restricted) — enforces 5-level precedence model. |
| `/li:asset-search` | Search ~/.lintel/brand/azure-assets/ for the right icon or diagram primitive. |
| `/li:az-discover-presale` | ⚠ TEMPLATE ONLY — Presale Azure discovery skill (operator-request 5.4 REPLACED per L-001). Scaffolding-slot, content |
| `/li:az-tldr` | Comprehensive on-demand rundown of an Azure service — 15 sections covering what/why/how/pitfalls/customer-questions/co |
| `/li:brand-update` | Pull/register MS brand assets to ~/.lintel/brand/ — version tracking, cache invalidation. |
| `/li:caip-audit` | CAIP-SE-specific readiness audit — engagement state, compliance, voice, deliverables. |
| `/li:cloudtest-eval-suite` | Generate an evaluation suite skeleton for an AI feature — golden set, adversarial set, rubric. |
| `/li:context-budgetwatch` | Manual context-bloat check — token + tool-call thresholds, recommendation to /clean or /context-save. |
| `/li:demo-deliverable-gen` | Generate customer-facing demo deliverables — script, handout, follow-up email — trailblazer-voiced. |
| `/li:dpia-submit-draft` | Prepare a Data Protection Impact Assessment draft — GDPR Article 35, MS Privacy framework. |
| `/li:dsb-submit-draft` | Prepare a Data Sharing Board submission draft — recipients, purpose, data class, retention. |
| `/li:entra-agent-id-submit-draft` | Prepare a Microsoft Entra Agent ID submission — identity, capabilities, governance scope. |
| `/li:eval` | Run TRAILBLAZER-TEST against TRAILBLAZER-CORPUS — per-cell accuracy → CALIBRATION.md. |
| `/li:first-party-check` | Scan for non-first-party dependencies and surface MS alternatives — "first-party first" enforcement. |
| `/li:generate-design` | Produce design-spec.json (per-format layout-mappings + palette + fonts + asset placements) from content.md. Shared conte |
| `/li:generate-outline` | Produce outline.md (structured presentation/document skeleton) from a brief. Shared content-pipeline sub-skill, solo-inv |
| `/li:generate-pdf` | ⚠ TEMPLATE ONLY — Slot for PDF document generation. Content not curated. AI generates fresh at invocation per L-001. |
| `/li:generate-ppt` | Produce brand-compliant PowerPoint deck via pptx-genjs, 4-gate quality pipeline. |
| `/li:generate-qa` | Validate generated artifacts (any format) against brand, voice, readability, and structure standards. Auto-fixes where p |
| `/li:generate-visio` | ⚠ TEMPLATE ONLY — Slot for Visio diagram generation (architecture sketches, network topologies, process flows). Cont |
| `/li:generate-web` | Produce brand-compliant static HTML or Next.js scaffold for demo/landing page. |
| `/li:generate-word` | Produce brand-compliant Word doc via docx-templater — technical / customer-summary / transparency-note variants. |
| `/li:generate-write` | Produce content.md (slide/section bodies + bullets + titles) and speaker-notes.md from outline.md. Applies voice corpus. |
| `/li:generate-xlsx` | ⚠ TEMPLATE ONLY — Slot for Excel spreadsheet generation (data + estimates + tables). Content not curated. AI generat |
| `/li:generate` | Multi-format document generation orchestrator. Chains shared content pipeline (outline → write → design → qa) + pe |
| `/li:msvoice-rewrite` | Rewrite internal-voice content into Microsoft Our Voice (Trailblazer) — 12-cell aware. |
| `/li:onebranch-validate` | Cross-CLI verification — run a smoke matrix across claude-code/codex/copilot per skill cli_support. |
| `/li:onecs-check` | Run the 7 on-demand MS compliance checklist items on-request (vs the 5 always-on auto). |
| `/li:onerai-submit-draft` | Prepare a One RAI submission draft — checklist, capability/limitation, mitigation plan. |
| `/li:provenance-track` | Track artifact provenance — source, transforms, voice tier, calibration state, distribution path. |
| `/li:rais-customer-voice-check` | Gate customer-facing artifacts through 12-cell Trailblazer eval before distribution. |
| `/li:rais-impact-assessment` | Generate an RAI Impact Assessment — fairness, reliability, privacy, inclusiveness, transparency, accountability. |
| `/li:rais-sensitive-use` | Classify an AI feature against MS Sensitive Uses categories — produces structured report. |
| `/li:rais-transparency-note` | Generate transparency note for an AI feature — capabilities, limitations, data, disclosure. |
| `/li:scaffold-engagement-demo` | Initialize a customer-demo repo — sample data, script, slides, recording config, voice gates. |
| `/li:scaffold-internal-tool` | Initialize an internal-tooling repo — CI, README, MS compliance hooks, no customer surface. |
| `/li:scaffold-mvp` | Initialize a product-MVP repo — full compliance + voice + RAI + deploy wiring. |
| `/li:security-genomlysning` | ⚠ TEMPLATE ONLY — Security + risk genomlysning (operator-request 5.5 REPLACED per L-001). Scaffolding-slot, posture- |

## sdl layer (1 skills)

| Skill | Description |
|---|---|
| `/li:compliance-gate` | Compliance-gate aggregator — kör alla relevanta compliance-skills (caip-audit, onecs-check, rais-*, *-submit-draft) s |

