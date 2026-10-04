# Lintel Skill Catalog

Generated from skill frontmatter. Run `python3 bin/li-catalog.py` after changing a skill.
CI checks this file for drift; edit the source SKILL.md to change a description.

Use `/li:<name>` in a Lintel plugin, or ask Copilot to run the named Lintel skill.

Total skills: 97

## foundation layer (97 skills)

| Skill | Description |
|---|---|
| [`/li:adr-new`](adr-new/SKILL.md) | Use when a non-trivial decision needs recording to bootstrap a new Architecture Decision Record from the template, aski… |
| [`/li:analyze`](analyze/SKILL.md) | Use to check that PLAN and BUILD still match the approved DEFINE design — run when a plan was revised or a build deviat… |
| [`/li:audit`](audit/SKILL.md) | Use to read selected audit records and diagnostics, including hook or usage observations, without inferring execution f… |
| [`/li:brief-forge`](brief-forge/SKILL.md) | Use when a workflow explicitly hands work across a boundary — spawning a subagent, transitioning a phase, passing to a … |
| [`/li:build`](build/SKILL.md) | Use to execute an approved plan in bounded work packages, preserving short task IDs and acceptance evidence while revie… |
| [`/li:capture`](capture/SKILL.md) | Use after SHIP, at the end of a task, to make what was learned durable — updates lessons, drafts an ADR for any non-tri… |
| [`/li:catalog`](catalog/SKILL.md) | Use to discover Lintel skills and agents by intent, name, purpose, category, voice or declared client support, or regen… |
| [`/li:clean`](clean/SKILL.md) | Use for an honest context-weight readout and a pause/fresh-session/resume path when the current session feels heavy. |
| [`/li:cli-fingerprint`](cli-fingerprint/SKILL.md) | Use to identify the current CLI, desktop, IDE or cloud surface and inspect its actual tools without inferring capabilit… |
| [`/li:code-freeze`](code-freeze/SKILL.md) | Use to add, list or lift advisory session freeze paths; preserves project policy and never grants or removes host write… |
| [`/li:code-review`](code-review/SKILL.md) | Use before landing a change to review just the diff — focused on the changed code only, lighter than a full engineering… |
| [`/li:compliance-gate`](compliance-gate/SKILL.md) | Use when evaluating declared controls with mandatory, advisory, unverified and no-applicable outcomes; this is not host… |
| [`/li:context-budget`](context-budget/SKILL.md) | Use before a large read or handoff, or when context headroom and resource advice are needed; keep observed usage, sourc… |
| [`/li:context-cool`](context-cool/SKILL.md) | Exclude explicitly selected files from future context reads without claiming to remove already-sent conversation conten… |
| [`/li:context-warm`](context-warm/SKILL.md) | Use to load bounded files, topic-related sources, ADRs or prior sessions with safe selection and honest input-size esti… |
| [`/li:context-warm-customer`](context-warm-customer/SKILL.md) | Load customer-engagement repo state into context — their infrastructure-as-code, their CLAUDE.md, their ADRs, recent co… |
| [`/li:context-warm-from-url`](context-warm-from-url/SKILL.md) | Retrieve bounded external reference text only through explicit host policy and redirect checks, preserving source prove… |
| [`/li:cross-check`](cross-check/SKILL.md) | Use for an independent second opinion on a diff, plan, code or hypothesis through an actually available authorized revi… |
| [`/li:cycle`](cycle/SKILL.md) | Use to run a real multi-step task through the full SENSE-to-CAPTURE pipeline, or a chosen subset of phases. Supports mo… |
| [`/li:da`](da/SKILL.md) | Use for data-architecture depth — schema design, migrations, sharding and partitioning, query-pattern audits, retention… |
| [`/li:define`](define/SKILL.md) | Use to turn a rough idea or scoped request into a source-grounded design with outcomes, constraints, alternatives, risk… |
| [`/li:design-dna`](design-dna/SKILL.md) | Use when a frontend or presentation task needs corpus-backed style, palette, typography or stack guidance, selected des… |
| [`/li:dh`](dh/SKILL.md) | Use for devops and hosting depth — deployment plans, rollback strategy, observability specs, SLI/SLO budgets, capacity … |
| [`/li:diagnose`](diagnose/SKILL.md) | Use when something is broken and you don't yet know why — drives a hypothesis-led investigation that builds a minimum r… |
| [`/li:discover`](discover/SKILL.md) | Use after DEFINE, before PLAN, to gather context before planning — maps the codebase, surfaces relevant ADRs and lesson… |
| [`/li:doctor`](doctor/SKILL.md) | Use to diagnose source, target, profile and installed-file integrity while keeping actual host activation explicitly un… |
| [`/li:eval`](eval/SKILL.md) | Run the active pack's voice TEST against its voice CORPUS — per-cell accuracy → CALIBRATION.md. |
| [`/li:fix`](fix/SKILL.md) | Use for a known bug with a clear fix path that needs to ship now — runs the abbreviated SENSE, BUILD, REVIEW, SHIP path… |
| [`/li:frontend-design`](frontend-design/SKILL.md) | Use to direct frontend design, advise on a design-system choice or compare bounded variants while preserving the shared… |
| [`/li:frontend-design-review`](frontend-design-review/SKILL.md) | Use to review built UI or produced frontend designs with actual route/viewport evidence, six canonical advisory dimensi… |
| [`/li:frontend-motion`](frontend-motion/SKILL.md) | Use when a frontend brief needs an animation, scrolling or reduced-motion strategy, including no-animation and CSS-only… |
| [`/li:frontend-shader`](frontend-shader/SKILL.md) | Use when a frontend visual brief needs a shader or no-shader decision, source-backed library choices, performance limit… |
| [`/li:frontend-style-extract`](frontend-style-extract/SKILL.md) | Use to extract reusable layout, motion, interaction and component patterns from selected sites, screenshots or frontend… |
| [`/li:frontend-typography`](frontend-typography/SKILL.md) | Use when a frontend brief needs font stacks, a type scale, variable-font axes or a loading strategy with source and lic… |
| [`/li:full-engineering-pass`](full-engineering-pass/SKILL.md) | Use for a customer engagement or major release that needs the whole engineering picture at once — composes all five dom… |
| [`/li:generate`](generate/SKILL.md) | Use to produce a finished document or deliverable from a brief — drives outline, writing, design, and QA through to a b… |
| [`/li:generate-app`](generate-app/SKILL.md) | Use when a resolved frontend design needs a Next.js, Vite-React or SvelteKit application scaffold that preserves the se… |
| [`/li:generate-design`](generate-design/SKILL.md) | Use when existing content needs layout mappings, a selected palette, fonts and asset placements for one or more documen… |
| [`/li:generate-docs`](generate-docs/SKILL.md) | Use to generate source-grounded reference documentation, customer guides or onboarding tutorials while retaining API be… |
| [`/li:generate-outline`](generate-outline/SKILL.md) | Use to turn a presentation or document brief into a structured outline before drafting its content. |
| [`/li:generate-pdf`](generate-pdf/SKILL.md) | Use to produce a PDF from selected source content through an available converter or accepted browser print operation; L… |
| [`/li:generate-ppt`](generate-ppt/SKILL.md) | Use to create an editable PowerPoint deck from a brief or shared pipeline, retaining source detail in notes and inspect… |
| [`/li:generate-qa`](generate-qa/SKILL.md) | Use to inspect generated or supplied artifacts against source, brand, readability and structure requirements without mo… |
| [`/li:generate-style-learn`](generate-style-learn/SKILL.md) | Use to extract a reusable palette and typography reference from selected presentation, document or web artifacts withou… |
| [`/li:generate-visio`](generate-visio/SKILL.md) | Use when a request calls for architecture, network or process-flow diagrams through the Visio scaffolding slot; no cura… |
| [`/li:generate-web`](generate-web/SKILL.md) | Use to render a static HTML mockup, a profile-aware single-file page or a Next.js scaffold from a brief or the existing… |
| [`/li:generate-word`](generate-word/SKILL.md) | Use to create an editable Word document from selected source material through available native tools or a declared libr… |
| [`/li:generate-write`](generate-write/SKILL.md) | Use when a presentation or document outline needs full section content and speaker notes in the selected voice. |
| [`/li:generate-xlsx`](generate-xlsx/SKILL.md) | Use to create an editable workbook from selected source data through available native tools, with formula, recalculatio… |
| [`/li:handoff-size-check`](handoff-size-check/SKILL.md) | Use for the retained handoff-budget entry point; delegates selected artifacts and supplied observations to context-budg… |
| [`/li:hooks-status`](hooks-status/SKILL.md) | Use to inspect recorded hook outcomes, overrides or unobserved hooks through the shared audit reader; absence is not an… |
| [`/li:inspect`](inspect/SKILL.md) | Use to inspect a selected plan or repository through engineering, design and developer-experience lenses. Preserve orig… |
| [`/li:instruction-parity-check`](instruction-parity-check/SKILL.md) | Use to verify shared session protocol equality and client-entry links without overwriting project prose or confusing si… |
| [`/li:jobs`](jobs/SKILL.md) | Use when listing or steering repository-local jobs; job lifecycle observations do not replace selected work-map authori… |
| [`/li:lessons-add`](lessons-add/SKILL.md) | Use after a correction, insight, or recurring pattern worth remembering to record it as a lesson the next session will … |
| [`/li:lessons-promote`](lessons-promote/SKILL.md) | Promote one ID-managed project lesson into an explicitly named Lintel work tree's scaffolding baseline, with recorded p… |
| [`/li:lessons-surface`](lessons-surface/SKILL.md) | Use before or during a task for keyword-ranked lessons, the complete index or an exact lesson ID, without changing the … |
| [`/li:maintenance`](maintenance/SKILL.md) | Use for on-demand storage/context guidance, scoped path diagnostics and labeled usage estimates without treating partia… |
| [`/li:mars`](mars/SKILL.md) | Use when a problem, plan, spec, implementation or review deserves a deliberate multi-model adversarial second look — ru… |
| [`/li:migrations`](migrations/SKILL.md) | Read the installed-source migration catalog against the selected target, preserving overdue, unknown and historical rec… |
| [`/li:orientator`](orientator/SKILL.md) | Use for entry-time method guidance through catalog, preserving SENSE's existing pack navigation and high-risk confirmat… |
| [`/li:pack-create`](pack-create/SKILL.md) | Use to create a blank, inherited, or cloned Lintel pack and validate it before activation. |
| [`/li:pack-list`](pack-list/SKILL.md) | List configured-store, repository and installed-source packs with resolver precedence, validation results and the actua… |
| [`/li:pack-switch`](pack-switch/SKILL.md) | Use to explicitly switch the effective pack through the structured profile lifecycle, preserving required policy, confi… |
| [`/li:pack-validate`](pack-validate/SKILL.md) | Validate a pack before activation or after editing its manifest. Checks effective required fields and inheritance with … |
| [`/li:pattern`](pattern/SKILL.md) | Use when recurring expectations (deployment baselines, dashboard behavior, document structure, visual language) should … |
| [`/li:pause`](pause/SKILL.md) | Use before the context window fills up or before clearing the session to save the current state to a checkpoint file. R… |
| [`/li:perf-mode`](perf-mode/SKILL.md) | Use for the retained resource-advice entry point on heavy work; delegates to context-budget without changing model capa… |
| [`/li:perfbench`](perfbench/SKILL.md) | Measure performance — runtime, memory, cold-start — and detect regressions vs baseline. |
| [`/li:plan`](plan/SKILL.md) | Use after DISCOVER, or standalone with an approved design, to produce the cold-executor trio (plan.md + spec.md + promp… |
| [`/li:profile-switch`](profile-switch/SKILL.md) | Inspect host install state and guide explicitly supported activation or owned snapshot recovery, without inventing plug… |
| [`/li:research`](research/SKILL.md) | Use when the operator wants to understand a domain, codebase or option space before committing to implementation. Runs … |
| [`/li:resume`](resume/SKILL.md) | Use when returning in a fresh session to resume selected committed work, a cycle or a job, or read an owned checkpoint … |
| [`/li:review`](review/SKILL.md) | Use after BUILD, before SHIP, to adversarially review what was built — checks spec compliance, code quality, the active… |
| [`/li:role`](role/SKILL.md) | Use to take on or change a working role — activate one for a lightweight lens, turn it off, swap mid-session, apply its… |
| [`/li:role-new`](role-new/SKILL.md) | Use to create a durable role through a guided interview or update its expertise with a reviewed-digest, sensitivity-awa… |
| [`/li:roles-list`](roles-list/SKILL.md) | Use to list configured role metadata and the current selection, with explicit consent before including private roles. |
| [`/li:safe-install`](safe-install/SKILL.md) | Protect explicitly owned installation files with verified snapshots and conflict-preserving restore; announce recovery … |
| [`/li:sc`](sc/SKILL.md) | Use for security and compliance depth — threat models, auth flows, secret management, dependency-security audits, compl… |
| [`/li:scaffold`](scaffold/SKILL.md) | Use to initialize or inspect repository foundations through the owned scaffold helper, preserving existing instructions… |
| [`/li:scaffold-internal-tool`](scaffold-internal-tool/SKILL.md) | Use for the retained internal-tool scaffold entry; delegates the selected CLI, service, dashboard or script intent to s… |
| [`/li:scaffold-mvp`](scaffold-mvp/SKILL.md) | Use for the retained MVP scaffold entry; delegates real-user and first-journey intent to scaffold's owned method in mvp… |
| [`/li:scope`](scope/SKILL.md) | Use after SENSE, before DEFINE, to interpret scale hints against actual requirements, ownership, uncertainty and rollba… |
| [`/li:sense`](sense/SKILL.md) | Use at the very start of a task to read the situation before deciding how to work — detects operator intent, the active… |
| [`/li:ship`](ship/SKILL.md) | Use after REVIEW passes, when reviewed work is ready to land, to open a PR, deploy, or hand off to a customer — runs th… |
| [`/li:skill-new`](skill-new/SKILL.md) | Use to turn an authorized recurring task or pattern into a new Lintel skill draft using the existing scaffold and front… |
| [`/li:skill-router`](skill-router/SKILL.md) | Use to find a relevant Lintel method from free-text intent through catalog's metadata-first shortlist. |
| [`/li:spec-kit`](spec-kit/SKILL.md) | Use when a repository has GitHub Spec Kit artifacts and needs Lintel planning, build-card execution, review or session … |
| [`/li:status`](status/SKILL.md) | Use when inspecting selected work, recorded cycle state and supplementary job observations read-only; this does not run… |
| [`/li:swarm`](swarm/SKILL.md) | Use when an approved plan has multiple dependency-independent work domains and the operator wants coordinated multi-age… |
| [`/li:ta`](ta/SKILL.md) | Use for technical-architecture depth — service boundaries, API contracts, dependency graphs, scaling plans, complexity … |
| [`/li:tq`](tq/SKILL.md) | Use for testing and QA-strategy depth — test-pyramid review, coverage audits, contract-test design, regression suites, … |
| [`/li:uniformity`](uniformity/SKILL.md) | Use in a Lintel contributor source checkout or CI to inspect the uniformity floor and recorded matrix; missing trusted … |
| [`/li:usage-log`](usage-log/SKILL.md) | Use to record an explicitly requested invocation or inspect authorized usage records through the shared audit reader; m… |
| [`/li:verify`](verify/SKILL.md) | Use to check whether a change works without changing it. Runs applicable tests or document checks, reports failures and… |
| [`/li:web-session`](web-session/SKILL.md) | Use to browse, extract pages, open an owned browser or validate user-managed sign-in through an actual provider with ex… |
| [`/li:welcome`](welcome/SKILL.md) | Use on first run to choose a useful task, inspect the actual client surface and take a proportionate plan, build, revie… |
