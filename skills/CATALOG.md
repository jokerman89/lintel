# Lintel Skill Catalog

Generated from skill frontmatter. Run `python3 bin/li-catalog.py` after changing a skill.
CI checks this file for drift; edit the source SKILL.md to change a description.

Use `/li:<name>` in a Lintel plugin, or ask Copilot to run the named Lintel skill.

Total skills: 126

## foundation layer (126 skills)

| Skill | Description |
|---|---|
| [`/li:adr-new`](adr-new/SKILL.md) | Use when a non-trivial decision needs recording to bootstrap a new Architecture Decision Record from the template, aski… |
| [`/li:analyze`](analyze/SKILL.md) | Use to check that PLAN and BUILD still match the approved DEFINE design — run when a plan was revised or a build deviat… |
| [`/li:audit`](audit/SKILL.md) | Read the unified Lintel audit trail — surface .claude/runtime/audit/ (repo events) and ~/.lintel/audit/ (operator event… |
| [`/li:autoplan`](autoplan/SKILL.md) | Use to run a problem statement through the full planning pipeline in one shot — chains the design doc, strategy review,… |
| [`/li:brief-forge`](brief-forge/SKILL.md) | Use whenever work hands off across a boundary — spawning a subagent, transitioning a phase, passing to a cold executor,… |
| [`/li:browse`](browse/SKILL.md) | Drive a headless Chromium to a URL — screenshot, extract DOM, click, fill forms, verify UI. |
| [`/li:build`](build/SKILL.md) | Use to implement an approved plan task by task. Trigger after PLAN is approved and a plan.md exists with code to write … |
| [`/li:capture`](capture/SKILL.md) | Use after SHIP, at the end of a task, to make what was learned durable — updates lessons, drafts an ADR for any non-tri… |
| [`/li:careful`](careful/SKILL.md) | Slow-down mode for high-stakes work — extra gates, double-confirm before mutations. |
| [`/li:catalog`](catalog/SKILL.md) | Use to discover Lintel skills by name, purpose or family, or regenerate the committed skill catalog after frontmatter c… |
| [`/li:clean`](clean/SKILL.md) | Manual self-maintenance trigger. Suggests /context-save + restart when session feels heavy. |
| [`/li:cli-fingerprint`](cli-fingerprint/SKILL.md) | Detect which CLI is running Lintel — env-var → process → tool-probe → config fallback. |
| [`/li:code-freeze`](code-freeze/SKILL.md) | Mark paths as DO-NOT-MODIFY for this session — other skills check + refuse to touch. |
| [`/li:code-review`](code-review/SKILL.md) | Use before landing a change to review just the diff — focused on the changed code only, lighter than a full engineering… |
| [`/li:code-unfreeze`](code-unfreeze/SKILL.md) | Remove a path from session freeze — other skills can write to it again. |
| [`/li:codex`](codex/SKILL.md) | Outside-voice second opinion via Codex CLI. Independent review of diff, plan, or hypothesis. |
| [`/li:compliance-gate`](compliance-gate/SKILL.md) | Compliance-gate aggregator — runs all gates the active pack declares (compliance.hooks) as ONE green/red verdict. Embar… |
| [`/li:context-budget`](context-budget/SKILL.md) | Show current context utilization, recommend warm/cool, surface budget breakdown by source. `--watch` runs the threshold… |
| [`/li:context-cool`](context-cool/SKILL.md) | Selectively drop context from session — free budget for further warming. Operator picks what to keep. |
| [`/li:context-restore`](context-restore/SKILL.md) | Use at the start of a fresh session that continues prior work to restore session state from a checkpoint file. Reach fo… |
| [`/li:context-save`](context-save/SKILL.md) | Use before the context window fills up or before clearing the session to save the current state to a checkpoint file. R… |
| [`/li:context-warm`](context-warm/SKILL.md) | Use to deliberately load specific files into context before working on them, reporting tokens added and budget impact. … |
| [`/li:context-warm-adrs`](context-warm-adrs/SKILL.md) | Load topic-relevant ADRs into context — design constraints + prior decisions surfaced for current work. |
| [`/li:context-warm-customer`](context-warm-customer/SKILL.md) | Load customer-engagement repo state into context — their infrastructure-as-code, their CLAUDE.md, their ADRs, recent co… |
| [`/li:context-warm-from-url`](context-warm-from-url/SKILL.md) | Fetch URL + dump into context. Useful for loading documentation, blog posts, external references on-demand. |
| [`/li:context-warm-related`](context-warm-related/SKILL.md) | Heuristic context warm — search codebase for files related to a topic, load top N most-relevant. |
| [`/li:context-warm-sessions`](context-warm-sessions/SKILL.md) | Load last N session saves on current branch — cross-session continuity for resumed work. |
| [`/li:cycle`](cycle/SKILL.md) | Use to run a real multi-step task through the full SENSE-to-CAPTURE pipeline, or a chosen subset of phases. Supports mo… |
| [`/li:da`](da/SKILL.md) | Use for data-architecture depth — schema design, migrations, sharding and partitioning, query-pattern audits, retention… |
| [`/li:define`](define/SKILL.md) | Use after SCOPE, before DISCOVER, to turn a sized request into an approved design — clarifies intent, locks premises, f… |
| [`/li:design-consultation`](design-consultation/SKILL.md) | Conversational design-system advisor — answer systems-level questions with grounded recommendations. |
| [`/li:design-dna`](design-dna/SKILL.md) | Curated design knowledge + retrieval — BM25 search over 84 UI styles, 161 WCAG-audited palettes, 161 product reasoning … |
| [`/li:design-html`](design-html/SKILL.md) | Generate a single-file static HTML mockup from a brief — opens with /open-managed-browser. |
| [`/li:design-review`](design-review/SKILL.md) | 6-pillar visual review of frontend changes — screenshot via /browse, scored findings. |
| [`/li:design-shotgun`](design-shotgun/SKILL.md) | Parallel design exploration — spawn N variants of a seed HTML, present side-by-side. |
| [`/li:devex-review`](devex-review/SKILL.md) | Review the built developer experience — scripts, onboarding, error messages, time-to-hello-world. |
| [`/li:dh`](dh/SKILL.md) | Use for devops and hosting depth — deployment plans, rollback strategy, observability specs, SLI/SLO budgets, capacity … |
| [`/li:discover`](discover/SKILL.md) | Use after DEFINE, before PLAN, to gather context before planning — maps the codebase, surfaces relevant ADRs and lesson… |
| [`/li:doctor`](doctor/SKILL.md) | Use when something seems off with the Lintel install, or to confirm it's healthy, to run a cross-CLI health check — ver… |
| [`/li:document-generate`](document-generate/SKILL.md) | Generate documentation from code — engineering reference, customer guides, or onboarding tutorials. |
| [`/li:eval`](eval/SKILL.md) | Run the active pack's voice TEST against its voice CORPUS — per-cell accuracy → CALIBRATION.md. |
| [`/li:fix`](fix/SKILL.md) | Use for a known bug with a clear fix path that needs to ship now — runs the abbreviated SENSE, BUILD, REVIEW, SHIP path… |
| [`/li:frontend-design`](frontend-design/SKILL.md) | Frontend design-director orchestrator. Chains typography + motion (+ shader in Phase A2) → frontend-design-spec.json → … |
| [`/li:frontend-design-review`](frontend-design-review/SKILL.md) | Quality gate for produced frontend designs. 6-dimension audit (typography hierarchy + motion coherence + shader perf-bu… |
| [`/li:frontend-motion`](frontend-motion/SKILL.md) | Frontend design-director sub-skill — picks motion-language (GSAP/Lenis/Theatre/Rive/Motion-One) + scroll-trigger-config… |
| [`/li:frontend-shader`](frontend-shader/SKILL.md) | Frontend design-director sub-skill — picks shader library (Paper Shaders / OGL / react-three-fiber / Lygia) + visual th… |
| [`/li:frontend-style-extract`](frontend-style-extract/SKILL.md) | Pattern-level extraction sister to generate-style-learn. Reads artifacts (URLs, screenshots, .tsx files) → extracts lay… |
| [`/li:frontend-typography`](frontend-typography/SKILL.md) | Frontend design-director sub-skill — picks font-family-stacks + variable-axes-config + size-scale + line-heights + font… |
| [`/li:full-engineering-pass`](full-engineering-pass/SKILL.md) | Use for a customer engagement or major release that needs the whole engineering picture at once — composes all five dom… |
| [`/li:generate`](generate/SKILL.md) | Use to produce a finished document or deliverable from a brief — drives outline, writing, design, and QA through to a b… |
| [`/li:generate-app`](generate-app/SKILL.md) | Full-app scaffold-orchestrator. Reads frontend-design-spec.json + generates vite-react/next-app/svelte-kit project skel… |
| [`/li:generate-design`](generate-design/SKILL.md) | Produce design-spec.json (per-format layout-mappings + palette + fonts + asset placements) from content.md. Shared cont… |
| [`/li:generate-outline`](generate-outline/SKILL.md) | Produce outline.md (structured presentation/document skeleton) from a brief. Shared content-pipeline sub-skill, solo-in… |
| [`/li:generate-pdf`](generate-pdf/SKILL.md) | ⚠ TEMPLATE ONLY — Slot for PDF document generation. Content not curated. AI generates fresh at invocation per L-001. |
| [`/li:generate-ppt`](generate-ppt/SKILL.md) | Produce brand-compliant PowerPoint deck via pptxgenjs, 4-gate quality pipeline. |
| [`/li:generate-qa`](generate-qa/SKILL.md) | Validate generated artifacts (any format) against brand, voice, readability, and structure standards. Auto-fixes where … |
| [`/li:generate-style-learn`](generate-style-learn/SKILL.md) | Analyze .pptx/.docx/web-examples and extract a reusable style palette. v3.5 Phase 3 of the doc-generation-pipeline. |
| [`/li:generate-visio`](generate-visio/SKILL.md) | ⚠ TEMPLATE ONLY — Slot for Visio diagram generation (architecture sketches, network topologies, process flows). Content… |
| [`/li:generate-web`](generate-web/SKILL.md) | Produce brand-compliant static HTML or Next.js scaffold for demo/landing page. |
| [`/li:generate-word`](generate-word/SKILL.md) | Produce brand-compliant Word doc via docxtemplater — technical / customer-summary / transparency-note variants. |
| [`/li:generate-write`](generate-write/SKILL.md) | Produce content.md (slide/section bodies + bullets + titles) and speaker-notes.md from outline.md. Applies voice corpus… |
| [`/li:generate-xlsx`](generate-xlsx/SKILL.md) | ⚠ TEMPLATE ONLY — Slot for Excel spreadsheet generation (data + estimates + tables). Content not curated. AI generates … |
| [`/li:handoff-size-check`](handoff-size-check/SKILL.md) | Handoff-size warning tied to the 500k cap. Per v3.6 backlog 3.2 — elephant-hint and token-cap as the same mechanism fro… |
| [`/li:health`](health/SKILL.md) | Lintel install + upstream status check. Verifies layers, manifest, hooks, upstream pins, CLI shims. |
| [`/li:help`](help/SKILL.md) | List the Lintel skills + agents + hooks available in this session. Filter by category, voice tier, or CLI support. |
| [`/li:hooks-status`](hooks-status/SKILL.md) | Reader for hooks.jsonl — surface active-vs-dead hooks + override patterns + trigger counts. Closes the hooks-observatio… |
| [`/li:instruction-parity-check`](instruction-parity-check/SKILL.md) | Verifies substance-parity across 6 instruction files (root CLAUDE/AGENTS/GEMINI + shims). The multi-CLI promise's weak … |
| [`/li:investigate`](investigate/SKILL.md) | Use when something is broken and you don't yet know why — drives a hypothesis-led investigation that builds a minimum r… |
| [`/li:jobs`](jobs/SKILL.md) | Use to see and steer in-flight Lintel jobs — list what's open, continue, replan, abort, or branch a job. The single sou… |
| [`/li:landing-report`](landing-report/SKILL.md) | Post-ship report — what landed in a window, in engineering or customer-voice format. |
| [`/li:learn`](learn/SKILL.md) | Use after a correction, insight, or recurring pattern worth remembering to record it as a lesson the next session will … |
| [`/li:lessons`](lessons/SKILL.md) | Mid-session review of accumulated lessons from .claude/memory/lessons.md — surfaces relevant ones for current task. |
| [`/li:lessons-promote`](lessons-promote/SKILL.md) | Promote a repo-local lesson from .claude/memory/lessons.md to Lintel's global lessons (scaffolding/01-foundation/.claud… |
| [`/li:lessons-surface`](lessons-surface/SKILL.md) | Use before or during a task to pull up prior lessons relevant to it — searches the lessons store by keyword and context… |
| [`/li:maintenance`](maintenance/SKILL.md) | On-demand maintenance — force-compact + static-path monitoring + token-cost simulation. Operator-request 5.3. Builds on… |
| [`/li:make-pdf`](make-pdf/SKILL.md) | Convert URL, markdown file, or HTML to PDF via managed Chromium. |
| [`/li:migrations`](migrations/SKILL.md) | Surface pending v4.x migrations at SENSE. Sister to /li:status. Read-only — surfaces operator-callsites still on deprec… |
| [`/li:office-hours`](office-hours/SKILL.md) | Use to turn a rough problem statement into a structured, decision-gated design doc ready for engineering review. Reach … |
| [`/li:open-managed-browser`](open-managed-browser/SKILL.md) | Open the Lintel-managed Chromium in headed mode — interactive operator session. |
| [`/li:orientator`](orientator/SKILL.md) | Phase 3 v4.0 — lightweight routing agent invoked at SENSE. Reads operator prompt + active pack's navigation policy, rec… |
| [`/li:pack-create`](pack-create/SKILL.md) | Scaffolds a new Lintel pack — copies _default pack.yaml as starting point, optionally sets extends parent, validates re… |
| [`/li:pack-list`](pack-list/SKILL.md) | Lists every pack discoverable in ~/.lintel/packs/ and repo packs/ — shows name, extends, voice tier, compliance mode, a… |
| [`/li:pack-switch`](pack-switch/SKILL.md) | Use to change which pack is active — switching the identity that drives voice, compliance, persona, and roles. Validate… |
| [`/li:pack-validate`](pack-validate/SKILL.md) | Validates a pack manifest against lib/pack-schema.yaml — required fields, extends-chain, version compatibility. Reports… |
| [`/li:pair-agent`](pair-agent/SKILL.md) | Pair with a named subagent in the loop — explicit two-mind collaboration on a focused task. |
| [`/li:perf-mode`](perf-mode/SKILL.md) | Activate the 1M context-budget mode for a session — the high-intensity preset for long, heavy phases. |
| [`/li:perfbench`](perfbench/SKILL.md) | Measure performance — runtime, memory, cold-start — and detect regressions vs baseline. |
| [`/li:personas-rotate`](personas-rotate/SKILL.md) | Load persona context from .claude/memory/personas.md for demo-prep, workshop-facilitation, or audience-aware writing. |
| [`/li:plan`](plan/SKILL.md) | Use after DISCOVER, or standalone when you have a design doc and need to break it into executable work, to produce the … |
| [`/li:plan-and-build`](plan-and-build/SKILL.md) | Use when you already have an approved design doc and just need to plan and implement it — runs PLAN then BUILD and skip… |
| [`/li:plan-ceo-review`](plan-ceo-review/SKILL.md) | Use before architecture lands to review a plan's strategy and scope — surfaces the product and business assumptions bak… |
| [`/li:plan-design-review`](plan-design-review/SKILL.md) | UI/UX gaps review for plans with a frontend surface. Skip for backend/infra/CLI-only work. |
| [`/li:plan-devex-review`](plan-devex-review/SKILL.md) | Developer experience gaps review. Slow CI, painful deploys, bad local dev, attrition signals. |
| [`/li:plan-eng-review`](plan-eng-review/SKILL.md) | Use to review a plan or change for engineering soundness before it ships — covers architecture, code quality, test cove… |
| [`/li:plan-tune`](plan-tune/SKILL.md) | Adjust which AskUserQuestion prompts auto-decide vs ask. Per-question preference tuning. |
| [`/li:profile-switch`](profile-switch/SKILL.md) | Toggle the Lintel install on/off fast + swap to a previous setup without touching the repo. Operator-request 5.2. |
| [`/li:qa`](qa/SKILL.md) | Use when you need to know whether the code works and to get the test suite green — runs the full suite, parses failures… |
| [`/li:qa-only`](qa-only/SKILL.md) | Read-only test run — reports failures, never edits. For ship-gate verification. |
| [`/li:research`](research/SKILL.md) | Composite shortcut for research-dive — runs SENSE + DEFINE + DISCOVER, no BUILD/SHIP. For "understand before commit" mo… |
| [`/li:resume`](resume/SKILL.md) | Use at the start of a fresh session to pick up work left in flight — reads 00-state.md and resumes the cycle at the nex… |
| [`/li:retro`](retro/SKILL.md) | Session retrospective — what shipped, what got stuck, what to /learn from. |
| [`/li:review`](review/SKILL.md) | Use after BUILD, before SHIP, to adversarially review what was built — checks spec compliance, code quality, the active… |
| [`/li:review-and-ship`](review-and-ship/SKILL.md) | Composite shortcut REVIEW + SHIP + CAPTURE — for when BUILD is done and operator wants to finalize, ship, capture in on… |
| [`/li:role`](role/SKILL.md) | Use to take on or change a working role — activate one for a lightweight lens, turn it off, swap mid-session, apply its… |
| [`/li:role-new`](role-new/SKILL.md) | Scaffold a new role file from template via guided interview — IDENTITY, COLD KNOWLEDGE, DECISION CRITERIA, OUTCOME LENS… |
| [`/li:roles-list`](roles-list/SKILL.md) | List all available roles (public + private, if accessible). Shows id, display name, scope, sensitivity, last-updated. |
| [`/li:safe-install`](safe-install/SKILL.md) | Safe-install wrapper for Lintel — version-before-every-change + uninstall-with-restore + visible-announce backup. Opera… |
| [`/li:sc`](sc/SKILL.md) | Use for security and compliance depth — threat models, auth flows, secret management, dependency-security audits, compl… |
| [`/li:scaffold`](scaffold/SKILL.md) | Use when setting up a new or existing repo to work with Lintel to install the base templates interactively — the repo i… |
| [`/li:scaffold-internal-tool`](scaffold-internal-tool/SKILL.md) | Initialize an internal-tooling repo — CI, README, pack compliance hooks, no customer surface. |
| [`/li:scaffold-mvp`](scaffold-mvp/SKILL.md) | Initialize a product-MVP repo — full structure + pack-driven compliance/voice/deploy wiring. |
| [`/li:scope`](scope/SKILL.md) | Use after SENSE, before DEFINE, when a request's size is ambiguous — turns a raw ask into a sized, disambiguated scope … |
| [`/li:scrape`](scrape/SKILL.md) | Extract structured data from one or more pages — declarative selector schema, JSON output. |
| [`/li:sense`](sense/SKILL.md) | Use at the very start of a task to read the situation before deciding how to work — detects operator intent, the active… |
| [`/li:setup-browser-cookies`](setup-browser-cookies/SKILL.md) | Bootstrap auth cookies for the managed Chromium profile — operator-driven, one-time per service. |
| [`/li:ship`](ship/SKILL.md) | Use after REVIEW passes, when reviewed work is ready to land, to open a PR, deploy, or hand off to a customer — runs th… |
| [`/li:skill-router`](skill-router/SKILL.md) | Semantic skill router — given free-text user intent, suggests top 3 matching Lintel skills with rationale. |
| [`/li:skillify`](skillify/SKILL.md) | Turn a recurring task or pattern into a new Lintel skill — scaffolds SKILL.md from TEMPLATE. |
| [`/li:spec-kit`](spec-kit/SKILL.md) | Use when a repository has GitHub Spec Kit artifacts and needs Lintel planning, build-card execution, review or session … |
| [`/li:status`](status/SKILL.md) | Use to quickly check where you are in flight — shows what's open right now, an alias for listing jobs. The fast "what w… |
| [`/li:ta`](ta/SKILL.md) | Use for technical-architecture depth — service boundaries, API contracts, dependency graphs, scaling plans, complexity … |
| [`/li:tq`](tq/SKILL.md) | Use for testing and QA-strategy depth — test-pyramid review, coverage audits, contract-test design, regression suites, … |
| [`/li:uniformity`](uniformity/SKILL.md) | Read-only uniformity-contract dashboard — runs the Gate-M3 floor shape-test and points at the regenerable coverage matr… |
| [`/li:usage-log`](usage-log/SKILL.md) | Append-only usage log for skill/agent invocations — manual writer (one audit_log line) plus reader reports. One log, no… |
| [`/li:v4-migrate`](v4-migrate/SKILL.md) | Walks operator through v3.x → v4.0 migration — detects v3.x usage signals, recommends pack activation, optionally write… |
| [`/li:welcome`](welcome/SKILL.md) | Use on first run, or when someone is new to Lintel, for guided onboarding — detects the CLI, shows its honest capabilit… |
