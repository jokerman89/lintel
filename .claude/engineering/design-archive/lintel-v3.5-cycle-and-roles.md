# Lintel v3.5 — Cycle, Roles, Context Warming, Modes

**Date:** 2026-05-28
**Branch:** `v3-dev` (will become `lintel-rebrand` post-approval)
**Status:** DRAFT — awaiting operator approval before rename execution
**Supersedes:** li-v3-plan.md (architectural depth layer)
**Companion:** li-v3.5-azure-toolbox-plan.md (still applies, becomes lintel-v3.5-azure-toolbox.md after rename)

> Deep cycle design + role-lifting + context warming + multi-mode invocation. No thin patterns. Each phase = sub-skills + dedicated agents + artifacts + gates. Built on gstack, learns from superpowers + speckit, adds what neither has: compliance-tiered, MS-internal-aware, role-lifted, multi-CLI.

---

## §0 — Why this exists

`/devex-review` ranked v3 at 5.8/10 honest. The fix landed (78 agents organized, plugin manifests, session-harness framing). But the CYCLE itself was implicit — a series of skills invoked ad-hoc by the operator, no named end-to-end path.

This doc fills that gap. The Lintel cycle becomes the explicit skeleton, with depth comparable to superpowers' per-skill richness, speckit's phase structure, and gstack's process discipline — plus what neither has: compliance tiering, voice corpus, role-lifting, multi-CLI portability.

We refine and beef. We do not bloat.

---

## §1 — Comparative methodology study

Three deeply-studied competitors. What each does well, where each is limited, and what Lintel takes from each.

### 1.1 obra/superpowers — depth via per-skill richness

**What they do well:**
- **14 skills, each FAT** — brainstorming alone has visual-companion sub-tool, scope-assessment pre-questions, design-isolation principle, spec self-review, ending-criteria gate. Not "ask a question." A 200-line workflow.
- **Subagent-Driven Development as signature pattern** — fresh subagent per task + two-stage review (spec compliance THEN code quality). Implementer status protocol (DONE / DONE_WITH_CONCERNS / NEEDS_CONTEXT / BLOCKED).
- **Hard gate enforcement** — "Do NOT invoke any implementation skill until design approved" — applies to even simple projects. "Simple projects are where unexamined assumptions cause the most wasted work."
- **Model selection by complexity** — fast cheap for mechanical, capable for architecture.
- **Skill integration requirements** — using-git-worktrees, writing-plans, requesting-code-review, finishing-a-development-branch. Skills name their companions.
- **TDD baked in** — test-driven-development is a foundational skill, not a phase.
- **Spec self-review before user review** — placeholders, contradictions, scope issues caught inline.

**What's limited:**
- Single-operator framing. No team modes, no compliance tiers.
- Claude-Code-only implicit. No multi-CLI.
- No domain specialization — Section Agent is generic.
- No voice calibration / customer-facing artifact gate.
- No cross-session continuity (lessons file, ADR, EVOLUTION-LOG).

**Lintel takes:**
- Per-skill richness — every phase-skill MUST have sub-procedures, anti-patterns, examples, status protocol
- Two-stage review pattern (spec compliance → code quality)
- Subagent-Driven Development as our /li:build sub-pattern
- Status protocol vocabulary (DONE / DONE_WITH_CONCERNS / NEEDS_CONTEXT / BLOCKED)
- Model selection strategy
- Hard gates between phases

### 1.2 github/spec-kit — depth via phase pipeline + artifacts

**What they do well:**
- **7 named phases** — Constitution → Specify → Clarify → Plan → Tasks → Analyze → Implement. Each produces an explicit artifact.
- **Constitution document** — `.specify/memory/constitution.md` — governing principles loaded at every phase.
- **Multi-step refinement vs one-shot** — spec-driven, not prompt-driven.
- **Cross-artifact consistency check (Analyze phase)** — coverage gaps surfaced before Implement.
- **Slash command per phase** — `/speckit.specify`, `/speckit.clarify`, `/speckit.plan`, `/speckit.implement`. Composable.
- **30+ CLI integration** — portability is first-class.
- **Intent vs technical separation** — Specify is what+why, Plan is how. Forces clean handoff.

**What's limited:**
- No agent specialization. Generic phase-executor.
- No voice or compliance dimensions.
- No role-lifting.
- Implementation phase is the only "building" phase — no built-in TDD, no review-loops.
- Constitution is project-level but not session-level (no per-session profile).

**Lintel takes:**
- 8-phase pipeline (Speckit has 7; we add CAPTURE for cross-session continuity)
- Per-phase artifacts (each phase produces a named file)
- Constitution analog — we already have CORE-PRINCIPLES.md + HARD-RULES.md, elevate to phase-load
- Cross-artifact consistency scan (we add /li:analyze as REVIEW sub-skill)
- Composable slash command pattern — `/li:sense`, `/li:define`, etc.
- Intent vs technical separation in DEFINE vs PLAN

### 1.3 gstack (parent project, we build on top)

**What they do well:**
- **AskUserQuestion as decision-brief primitive** — D-numbered, ELI10, recommendation, stakes, options with ≥40-char pros/cons, completeness score, net line. Highly structured.
- **Office-hours forcing questions** — six adapted by mode (Startup/Builder/Intrapreneurship), one-at-a-time, push until specific.
- **Builder profile** — tier tracking across sessions (introduction / welcome_back / regular / inner_circle). Resources adapt to tier.
- **Confusion protocol** — ambiguous = stop, present options, ask.
- **Premise check phase** — before alternatives, lock baseline assumptions.
- **Cross-model second opinion** — Codex outside-voice or Claude subagent for independence.
- **Founder signal synthesis** — observe + reflect specific signals after design.
- **Boil-the-lake principle** — completeness when marginal cost low; flag oceans.
- **Continuous checkpoint mode** — auto-commit WIP with context blocks.
- **Voice section per model** — Garry-shaped builder-to-builder, no AI vocabulary, no em dashes.
- **Telemetry built-in but opt-in** — local-only by default.

**What's limited:**
- Startup-founder centric framing. Intrapreneurship adaptation exists but is a tone-shift, not a structural mode.
- No domain-specific compliance (no RAIS, no OneCS, no EV2).
- No customer-facing voice gate.
- No role-lifting concept.

**Lintel takes:**
- ALL of gstack's process discipline (we already inherit)
- AskUserQuestion format = mandatory for every phase decision gate
- Builder profile evolves to operator profile (cross-session tier tracking)
- Premise check + Cross-model second opinion = preserved per phase as optional
- Voice rules: "no AI vocabulary, no em dashes" — already in CLAUDE.md
- Continuous checkpoint mode = orthogonal toggle, off by default

### 1.4 Lintel (us, current v3) — what we already do better

- **Plugin manifest pattern across 8 CLIs** — superpowers via plugin marketplaces too, but Lintel adds Codex/Cursor/Gemini/OpenCode/Copilot/Droid in one repo
- **78 specialized agents per domain** — none of the three has this. Architect image had generic "Section Agent."
- **5+7+8 compliance tiering** — HARD-RULES (always-on), ON-DEMAND, REFERENCE
- **Trailblazer voice corpus** (60 paragraphs, 12 cells, calibratable) — beyond what any of them has
- **Repo scaffolding via bin/li-scaffold** (becomes bin/li-scaffold) — Speckit has memory/, none has full repo bootstrap
- **MS-internal aware** — RAIS, OneCS, AGT, EV2, OneBranch, 1ESPT
- **Cross-session continuity** — lessons.md, EVOLUTION-LOG.md, ADR template, /li:context-save/restore
- **Doc-gen 4-gate** — /li:generate-ppt, /li:generate-word, /li:generate-web with voice + brand + honest-limitations + provenance

### 1.5 What Lintel ADDS that none has

- **WorkProfile toggle** — env-level switch that controls compliance, voice-default, telemetry, first-party-first enforcement
- **Role-lifting mechanism** — bring expert personas into a session as lightweight context layers
- **Context warming** — on-demand 1M utilization beyond session-start
- **Multi-mode presets** — hotfix / customer-engagement / internal-tool / demo-prep / research-dive
- **Hop-in support** — enter cycle at any phase, /li:resume routes intelligently
- **Cold-executor handoff trio** — plan.md + spec.md + prompt.md self-contained at CAPTURE phase

---

## §2 — The Lintel cycle (8 phases, named paths)

Cycle invocation: `/li:cycle [--mode <preset>] [--from <phase>] [--to <phase>] [--skip <phases>]`

Individual phase invocation: `/li:<phase>` (each phase is also a standalone skill)

```
SENSE → DEFINE → DISCOVER → PLAN → BUILD → REVIEW → SHIP → CAPTURE
  ↑                                                                  ↓
  └──────────────  /li:resume reads 00-state.md  ←──────────────────┘
```

Each phase = a slash command + sub-skills + dedicated agents + artifact + gates + status protocol + integration requirements. Below: full depth per phase.

---

### §2.1 — Phase 1: SENSE (~500-1k tokens, ~30 sec)

**Purpose:** auto-detect operator intent, current WorkProfile state, recommended mode, active role (if any), 00-state from previous session.

**Slash:** `/li:sense` (also invoked at start of /li:cycle)

**Sub-skills invoked:**
- `/li:detect-intent` — parse operator's last message + cwd state, classify intent (build / fix / review / research / ship / scaffold-new)
- `/li:detect-workprofile` — read `~/.lintel/profile.yaml`, surface state
- `/li:detect-role` — if role active, surface role identity (lightweight, not full)
- `/li:detect-state` — read 00-state.md from cwd if exists, surface phase + last commit
- `/li:detect-context-budget` — current context window utilization, recommend warm/cool

**Agents:**
- **ContextBudgetAdvisor** (engineering/) — token utilization analysis
- **Explorer** (engineering/) — codebase scope detection
- *None of these are heavily invoked at SENSE — read-only, cheap*

**Artifacts produced:**
- `00-state.md` (root of cwd) — single-file rolling state, appended each phase

```yaml
# .lintel/state/00-state.md
cycle_id: 2026-05-28-1432-azure-toolbox-build
operator: jokerman89
workprofile: on
mode: customer-engagement
role: field-cto (active)
voice_tier: trailblazer
azure_focus: on
context_budget_at: 38k / 1M (4%)
phases_completed: []
current_phase: SENSE
next_recommended: DEFINE
intent_detected: build (Azure-toolbox v3.5)
last_session: 2026-05-27-2200 (capture-only, voice-cal-not-run)
```

**Gates:** none. SENSE is pure read.

**Status protocol:**
- DONE — sense report written, recommended mode/phase surfaced
- BLOCKED — cannot read state files (permissions, missing dirs)
- NEEDS_CONTEXT — workprofile.yaml malformed or first run

**Pause-points:** none (SENSE runs to completion silently or surfaces report).

**Hop-in:** SENSE is always the first phase, regardless of entry. /li:resume calls SENSE first.

**Integration:**
- Reads: `~/.lintel/profile.yaml`, `00-state.md`, recent git log, `tasks/lessons.md`, `tasks/memory.md`, role-files
- Writes: `00-state.md` (new phase entry)
- Triggers: nothing automatically — surface recommendation only

**Anti-patterns:**
- Loading full role-file content (heavy) — only identity + voice summary
- Running expensive grep/glob — operator can manually invoke `/li:discover` if deep mapping needed
- Asking questions — SENSE is read-only diagnostic

**Output example:**

```
LINTEL SENSE — 2026-05-28 14:32

Operator: jokerman89
Mode: customer-engagement (from ~/.lintel/profile.yaml default)
WorkProfile: ON — HARD-RULES enforced, MS SSO required
Role: field-cto activated
Voice tier: trailblazer (mode default + role)
Azure focus: ON

Intent detected: build — extending v3.5 Azure-toolbox
Recommended phase: DEFINE (no design doc for /li:az-tldr meeting-prep yet)
Alt recommendation: hop to BUILD (design from prior session APPROVED)

00-state.md from last session: 2026-05-27-2200 (CAPTURE phase, no rollover)

Context budget: 38k / 1M (4%) — plenty of headroom

Next: /li:cycle --from DEFINE  OR  /li:define standalone  OR  /li:build
```

---

### §2.2 — Phase 2: DEFINE (~2-5k tokens, 3-15 min)

**Purpose:** clarify intent, lock premises, pick wedge, name first artifact. Office-hours-style forcing questions. Inherited from gstack; deepened with role-lift + WorkProfile-aware framing.

**Slash:** `/li:define` (or `/li:office-hours` legacy alias)

**Sub-skills invoked:**
- `/li:context-gather` — read CLAUDE.md, TODOS, recent git log, recent design docs (phase 1 of office-hours)
- `/li:related-design-scan` — grep design docs for keyword overlap (phase 2.5 of office-hours)
- `/li:landscape-search` — optional WebSearch for conventional wisdom (phase 2.75; gated)
- `/li:forcing-questions` — six adapted questions per mode (the heart of office-hours)
- `/li:premise-check` — lock baseline assumptions
- `/li:cross-model-opinion` — Codex/subagent independence check (optional)
- `/li:alternatives` — 2-3 implementation approaches MANDATORY
- `/li:role-lens` — if role active, apply role's outcome-lens to the problem (NEW)
- `/li:design-doc-write` — write design doc to `.claude/engineering/design-archive/lintel-*.md`
- `/li:spec-review` — adversarial subagent review of doc

**Agents:**
- **Architect** (engineering/) — primary, design judgment
- **FieldCTOAdvisor** (ms-specific/) — if role=field-cto or customer-engagement mode
- **AIStartupAdvisor** (ms-specific/) — if intent looks startup-y
- **DemoNarrativeArc** (customer/) — if mode=customer-engagement
- **TrailblazerVoiceCritic** (voice/) — if voice_tier=trailblazer (final design doc voice gate)
- **CodeReviewer** (engineering/) — for spec-review subagent dispatch

**Artifacts produced:**
- `.claude/engineering/design-archive/lintel-<branch>-design-<datetime>.md` — the design doc
- `00-state.md` entry — DEFINE phase complete, design doc path

**Gates:**
- **Forcing-questions gate** — premise-check and alternatives MANDATORY (per gstack /office-hours), even if user says "skip"
- **Design doc APPROVED via AskUserQuestion** — A) approve, B) revise, C) start over

**Status protocol:**
- DONE — design doc written, reviewed, APPROVED
- DONE_WITH_CONCERNS — approved but open questions logged
- BLOCKED — premise disagreement requires loop-back
- NEEDS_CONTEXT — operator hasn't given enough to define wedge

**Pause-points:**
- After context gather + intent: confirm understanding via 1-sentence prose
- After each forcing question: STOP, wait for response
- After premise check: AskUserQuestion to lock
- After alternatives: AskUserQuestion to pick (MANDATORY)
- After design doc: AskUserQuestion approve/revise/start-over

**Hop-in:** YES, if context is already clear. Can be skipped if operator provides a fully-formed spec OR if previous session ended with APPROVED design doc.

**Skip-conditions:** intent=hotfix (skip directly to BUILD), intent=ship-only (skip to SHIP), explicit operator override.

**Integration:**
- Reads: CLAUDE.md, TODOS.md, lessons.md, memory.md, related design docs, role file (if active)
- Writes: design doc, 00-state.md
- Triggers: /li:plan next (if not /li:cycle), or proceeds to DISCOVER in /li:cycle

**Anti-patterns:**
- Skipping forcing questions because operator seems impatient — gstack's escape-hatch (after 1 push, ask 2 more critical Qs)
- Asking >1 question per AskUserQuestion call (gstack rule)
- Letting design doc be approved before adversarial spec review
- Cross-contaminating role-lens onto premises if role is sensitivity=private (sanitize)

**Role-lens overlay (NEW):**
If role active, BEFORE writing alternatives:
1. Read role-file's "DEFINE — what this role wants" outcome section
2. Frame the 3 alternatives in terms of how each scores against role's decision criteria
3. Note in design doc: "Role lens applied: <role-id>"
4. Sensitivity-filter: if role is private, role-specific outcome-lens stays in `.lintel/state/role-lens-notes.md` (gitignored), not the public design doc

---

### §2.3 — Phase 3: DISCOVER (~1-3k tokens, 2-8 min)

**Purpose:** map codebase + context surface relevant to the wedge. Find what we already have so we don't reinvent. Surface ADRs, lessons, related patterns.

**Slash:** `/li:discover`

**Sub-skills invoked:**
- `/li:codebase-map` — Grep/Glob for relevant files based on DEFINE keywords
- `/li:adr-scan` — read `docs/adr/` for relevant prior decisions
- `/li:lessons-scan` — apply /li:lessons skill (relevance-filtered)
- `/li:dependency-audit` — surface dependencies that touch the wedge area
- `/li:related-skill-scan` — check if existing skills in `skills/` overlap (avoid duplicates)
- `/li:related-agent-scan` — match wedge to existing agents that should be subagent-pulled in PLAN/BUILD
- `/li:context-warmup` — operator can request additional context loaded (NEW — see §5)

**Agents:**
- **Explorer** (engineering/) — primary, codebase mapping
- **ResearchSynthesizer** (engineering/) — consolidates findings
- **DependencyAuditor** (security/) — when wedge touches third-party
- **ReadOnly** (engineering/) — for deep-read of suspect files

**Artifacts produced:**
- `discover-report.md` (in cwd, ephemeral) — codebase map, ADRs found, lessons applied, agents recommended for PLAN
- `00-state.md` entry — DISCOVER complete + report path

**Gates:** none (DISCOVER is read-only).

**Status protocol:**
- DONE — report written, agents/skills identified for PLAN
- DONE_WITH_CONCERNS — gaps in codebase (missing tests, stale docs)
- BLOCKED — too large to map cheaply (>1000 files) → operator must scope
- NEEDS_CONTEXT — wedge unclear, return to DEFINE

**Pause-points:** optional — operator can ask "show me what you found" mid-phase.

**Hop-in:** YES — can be invoked standalone for "tell me what we have on X."

**Skip-conditions:** intent=hotfix (skip), intent=ship-existing-branch (skip), known territory (operator override).

**Integration:**
- Reads: cwd codebase, docs/adr/, tasks/lessons.md, skills/, agents/<category>/
- Writes: discover-report.md, 00-state.md
- Triggers: PLAN with discover-report.md context

**Anti-patterns:**
- Reading every file ("comprehensive map") — pick top 20 most relevant
- Re-running grep for keywords DEFINE already established
- Ignoring ADRs that contradict the proposed approach (flag, don't bury)

---

### §2.4 — Phase 4: PLAN (~3-8k tokens, 5-20 min)

**Purpose:** convert design + discovery into executable task breakdown. Cost estimate. Founder/operator approval gate. Cold-executor handoff prep starts here.

**Slash:** `/li:plan`

**Sub-skills invoked:**
- `/li:plan-eng-review` — engineering plan, alternatives if scope changed
- `/li:plan-design-review` — design system / UX implications (if frontend)
- `/li:plan-devex-review` — operator-DX implications (always run)
- `/li:plan-tune` — iterative refinement based on review findings
- `/li:tasks-write` — task list with file paths + complete code (where prescriptive) + verification steps
- `/li:dependency-graph` — task ordering, blocking deps surfaced
- `/li:cost-estimate` — tokens × phase × model = $-estimate (NEW — adopted from Architect image)
- `/li:cross-section-analyze` — coverage check (NEW — adopted from speckit Analyze phase)
- `/li:plan-checkpoint` — write to `.planner-checkpoint.md` (state for resume)

**Agents:**
- **Planner** (engineering/) — primary, task decomposition
- **Architect** (engineering/) — sanity-check tech choices
- **BackendArchitect / FrontendBuilder / DataPipelineDesigner** — per domain
- **APIDesigner** (engineering/) — if API surface
- **DatabaseDesigner** (engineering/) — if schema changes
- **BicepReviewer / TerraformReviewer / K8sManifestReviewer** (devops/) — if infra
- **AzureArchitect / AzureOpenAIAdvisor** (ms-specific/) — if Azure
- **ADRDrafter** (engineering/) — if non-trivial decisions surface
- **SecurityAuditor** (security/) — sensitive-data flow check
- **RAIReviewer** (ms-specific/) — if AI/ML scenario
- **EUAIActReviewer** (compliance/) — if EU customers + AI

**Artifacts produced:**
- `plan.md` (canonical, in cwd or `docs/plans/`) — task list, milestones, dependencies, cost estimate
- `.planner-checkpoint.md` — state for /li:resume
- `spec.md` (early draft) — spec.md is finalized in CAPTURE, drafted here
- `00-state.md` entry

**Gates:**
- **Cost-estimate gate** — AskUserQuestion: "Estimated cost: $X / Y tokens / Z min. Proceed?" (NEW)
- **Founder approval gate** — MANDATORY PAUSE per Architect image. AskUserQuestion: approve / redirect / pause / abort.

**Status protocol:**
- DONE — plan APPROVED with cost-estimate accepted
- DONE_WITH_CONCERNS — approved with caveats logged
- BLOCKED — cost exceeds operator budget OR alternatives undecided
- NEEDS_CONTEXT — DESIGN missing details PLAN can't fill

**Pause-points:**
- After plan-eng-review: confirm review findings addressed
- After cost-estimate: AskUserQuestion gate
- After full plan: AskUserQuestion approval gate

**Hop-in:** YES — if design exists, can /li:plan standalone.

**Skip-conditions:** intent=hotfix (light plan only), intent=trivial-edit (skip entirely).

**Integration:**
- Reads: design doc (DEFINE), discover-report.md (DISCOVER), CORE-PRINCIPLES.md, HARD-RULES.md
- Writes: plan.md, .planner-checkpoint.md, spec.md (draft), 00-state.md
- Triggers: BUILD with plan.md as canonical source

**Two-stage subagent review (adopted from superpowers):**
After plan draft:
1. **Spec-compliance review** subagent: does plan match design doc requirements exactly?
2. **Quality review** subagent: are tasks well-decomposed, deps correct, costs realistic?

Fix between stages, re-review if needed. Stop after 3 iterations or convergence.

**Anti-patterns:**
- Plan that's a vague to-do list instead of file:line:verb instructions
- No cost-estimate (operator commits to unknown burn)
- Skipping the two-stage review because "it's a simple plan"
- Ignoring ADRs found in DISCOVER — they're constraints

---

### §2.5 — Phase 5: BUILD (~variable, depends on plan)

**Purpose:** execute plan via TDD + subagent-driven development pattern (adopted from superpowers). Each task = fresh subagent + two-stage review.

**Slash:** `/li:build`

**Sub-skills invoked:**
- `/li:tdd-cycle` — red-green-refactor for each task (foundational)
- `/li:dispatch-implementer` — spawn subagent per task with full task text + context
- `/li:two-stage-review` — spec-compliance review THEN code-quality review per task
- `/li:fix-loop` — address review findings, re-dispatch
- `/li:pair-agent` — operator pair-programming mode (interactive)
- `/li:continuous-checkpoint` — auto-commit WIP if checkpoint_mode=continuous (gstack-inherited)
- `/li:use-git-worktrees` — parallel branch dev (superpowers-inherited)
- `/li:verification-before-completion` — confirm task actually works before marking done
- `/li:context-warm-build` — operator can warm context with related files mid-BUILD (NEW)

**Agents (heavy depending on domain):**
- **TestRunner** (engineering/) — TDD red phase + verification
- **Refactorer** (engineering/) — refactor phase
- **Migrator** (engineering/) — schema/API migrations
- **BackendArchitect / FrontendBuilder** — per task domain
- **BicepReviewer / ARMTemplateReviewer** (ms-specific/) — IaC tasks
- **K8sManifestReviewer / TerraformReviewer** (devops/) — infra tasks
- **CostAnalyzer / LatencyAnalyzer / RegressionDetective** (engineering/) — perf-related tasks
- **SecurityAuditor / SecretsScanReviewer / ThreatModelDrafter** (security/) — security tasks
- **AzureArchitect / AzureOpenAIAdvisor / KeyVaultAuditor / GraphAPIAdvisor** (ms-specific/) — Azure tasks

**Artifacts produced:**
- Source code commits (TDD-driven)
- WIP checkpoints (if continuous mode)
- `build-log.md` (ephemeral) — task-by-task results
- `00-state.md` entry per task

**Gates:**
- **Per-task two-stage review** (spec → quality) — MANDATORY
- **TDD red-before-green** — code without failing test first = block
- **Hard-rule hooks** — customer-data-block, secret-scan-block, no-direct-main-push fire automatically (if hook activated)
- **Voice gate** — if audience=customer, trailblazer voice on customer-facing artifacts

**Status protocol per task:**
- DONE — task complete + both reviews PASS
- DONE_WITH_CONCERNS — done but quality concerns logged
- NEEDS_CONTEXT — implementer asked, provide + re-dispatch
- BLOCKED — task can't be implemented, escalate to operator

**Pause-points:**
- After each task review-pass: TodoWrite mark complete (no pause unless concerns)
- After every Nth task: optional summary report
- On BLOCKED: pause, root-cause hypothesis, operator decision
- On HARD-RULE hook fire: hard stop, never silently proceed

**Hop-in:** YES — operator can /li:build with existing plan.md.

**Skip-conditions:** intent=review-only, intent=research-only, intent=plan-only.

**Integration:**
- Reads: plan.md, CORE-PRINCIPLES.md, HARD-RULES.md, role-file (if active for voice/tone)
- Writes: source code, commits, build-log.md, 00-state.md
- Triggers: REVIEW after all tasks DONE

**Model selection (adopted from superpowers):**
- Mechanical/isolated tasks → Haiku (fast, cheap)
- Multi-file integration → Sonnet
- Architecture/design judgment → Opus

**Anti-patterns (per superpowers):**
- Starting on main without explicit consent
- Skipping reviews
- Proceeding with unfixed issues
- Dispatching multiple implementers in parallel within one phase (sequential ✓)
- Making subagent read plan file (give them the task text directly)
- Skipping scene-setting context for implementer
- Accepting "close enough" on spec compliance
- Letting implementer self-review replace actual review
- Starting code quality review before spec compliance is ✅

---

### §2.6 — Phase 6: REVIEW (~2-5k tokens, 3-10 min)

**Purpose:** adversarial review of the BUILD output. Cross-artifact consistency. Compliance gates fire here (if WorkProfile=on). Two stages: spec compliance, then quality, then compliance.

**Slash:** `/li:review`

**Sub-skills invoked:**
- `/li:review-spec-compliance` — does built code match plan.md requirements exactly?
- `/li:review-code-quality` — quality dimensions (per CodeReviewer agent)
- `/li:review-design-coverage` — design system / UX (if frontend)
- `/li:cross-artifact-analyze` — coverage gaps across spec/plan/build (NEW — from speckit)
- `/li:caip-audit` — MS CAIP-SE compliance audit (if WorkProfile=on)
- `/li:onecs-check` — 1CS compliance (if WorkProfile=on + customer-facing)
- `/li:rais-customer-voice-check` — Trailblazer voice gate (if voice_tier=trailblazer)
- `/li:agt-tier-stamp` — Agent Governance Framework (if AI agentic system built)
- `/li:provenance-track` — track AI-assisted-generation provenance
- `/li:first-party-check` — first-party-first compliance
- `/li:dependency-audit` — CVE/license/supply-chain
- `/li:codex` — outside-voice code review (optional)

**Agents (concentrated review pool):**
- **CodeReviewer** (engineering/) — primary
- **SanityChecker** (engineering/) — cross-component architectural sanity
- **SecurityAuditor / SecretsScanReviewer / OAuthFlowReviewer / JWTSecurityReviewer / SBOMAuditor / ThreatModelDrafter** (security/) — full security pass
- **GDPRReviewer / SDLReviewer / AGTReviewer / EUAIActReviewer / SOC2Reviewer** (compliance/) — per applicability
- **RAIReviewer / OneCSAuditor / PrivacyBoundaryAudit / ProvenanceVerifier** (ms-specific/) — MS-internal
- **TrailblazerVoiceCritic** (voice/) — if trailblazer voice
- **WebExperienceCritic / PPTNarrativeArchitect / WordTechnicalEditor** (doc-gen/) — if doc-gen output
- **DebugForensics / RegressionDetective** (engineering/) — if review surfaces bugs/regressions
- **AccessibilityChecker** (engineering/) — if web/UI

**Artifacts produced:**
- `review-report.md` — P1/P2/P3 findings with file:line + suggested fix
- `compliance-report.md` (if WorkProfile=on) — gate-by-gate status
- `00-state.md` entry

**Gates:**
- **P1 findings block SHIP** — must address before next phase
- **Compliance gates fire per WorkProfile config**
- **Voice gate** for customer-facing artifacts

**Status protocol:**
- DONE — all reviews PASS, P1 findings addressed
- DONE_WITH_CONCERNS — P2/P3 findings noted but not blocking
- BLOCKED — P1 findings not fixed OR compliance gate failed
- NEEDS_CONTEXT — review can't proceed without more info

**Pause-points:**
- After spec-compliance review: confirm pass before quality review
- After quality review: confirm before compliance gates
- Per P1 finding: operator decision (fix now / defer with rationale / accept-risk via ADR)

**Hop-in:** YES — operator can /li:review on existing diff/PR. This is the standalone-review case.

**Skip-conditions:** intent=research-only (no code to review), intent=docs-only (lighter review).

**Integration:**
- Reads: BUILD output, plan.md, design doc, CORE-PRINCIPLES.md, HARD-RULES.md, REFERENCE-RULES.md (if WorkProfile=on), voice corpus (if Trailblazer)
- Writes: review-report.md, compliance-report.md, 00-state.md
- Triggers: SHIP after PASS, or loop back to BUILD if BLOCKED

**Two-stage discipline:**
1. **Spec compliance** subagent — code vs plan.md exact match
2. **Quality** subagent — only after spec PASS
3. **Compliance** sub-skills — only after quality PASS

Fix between stages. Don't merge stages.

**Anti-patterns:**
- Running quality before spec-compliance
- Accepting "close enough" on spec
- Letting CodeReviewer be the only reviewer (compliance also fires)
- Skipping voice gate because "operator-internal" — if final artifact is customer-facing, gate fires

---

### §2.7 — Phase 7: SHIP (~1-3k tokens, 2-5 min)

**Purpose:** PR / deploy / handoff. Final compliance hard-stops. Voice + brand gate on customer-facing.

**Slash:** `/li:ship`

**Sub-skills invoked:**
- `/li:release-ev2` — EV2 pre-flight + PR creation (canonical)
- `/li:release-deploy-ev2` — EV2 deploy trigger
- `/li:safe-deploy-ring` — canary rollout
- `/li:onebranch-validate` — 1ESPT validation if 1ES pipeline
- `/li:provenance-track` — log AI-assistance provenance for the shipped artifact
- `/li:rais-customer-voice-check` — final voice gate if customer-facing
- `/li:generate-ppt / -word / -web` — if customer-deliverable doc-gen needed (4-gate pipeline)
- `/li:demo-deliverable-gen` — if engagement demo
- `/li:rais-transparency-note` — if AI-system shipped to customer
- `/li:landing-report` — release notes generation

**Agents:**
- **ReleaseEngineer** (engineering/) — primary
- **EV2PipelineAuditor / OneBranchReviewer / GHActionsReviewer** (devops/) — pipeline-specific
- **OneCSAuditor / ProvenanceVerifier** (ms-specific/) — MS compliance
- **TrailblazerVoiceCritic** (voice/) — final voice check on customer-facing
- **PPTNarrativeArchitect / WordTechnicalEditor / WebExperienceCritic** (doc-gen/) — if generating customer docs
- **DemoNarrativeArc / DemoNarratorJunior** (customer/) — if demo
- **ExecutiveBriefingDrafter / ProposalDrafter / RFPResponseDrafter** (customer/) — customer-engagement deliverables
- **EmailCustomerDrafter / BlogPostDrafter / LinkedInPostDrafter** (communication/) — if announcement

**Artifacts produced:**
- Pushed branch + PR (or direct-push if explicitly authorized)
- `release-notes.md` — generated via /li:landing-report
- `provenance-log.md` — append to repo's provenance log (if WorkProfile=on)
- Customer deliverables (if applicable): .pptx, .docx, .html
- `00-state.md` entry

**Gates:**
- **HARD-RULES hard-stop** — customer-data, secrets, prod-mutations, MS SSO, first-party-first — non-bypassable if WorkProfile=on
- **Voice gate** (final) — customer-facing artifacts must pass
- **Brand gate** — if doc-gen output, brand-conformance check (from v2 4-gate)
- **Honest-limitations gate** — disclaimers on AI-generated content
- **Provenance gate** — AI-assistance tracked
- **PR review check** — no-direct-main-push hook fires unless explicitly authorized for this commit batch

**Status protocol:**
- DONE — PR opened / deployed, all gates PASS
- DONE_WITH_CONCERNS — shipped with noted caveats (e.g., voice gate at 85%)
- BLOCKED — HARD-RULE violation, customer data leak, secret scan fail, etc.
- NEEDS_CONTEXT — deploy target unclear

**Pause-points:**
- Before PR open: confirm commit messages + branch state
- On HARD-RULE block: full stop, never silently proceed (per CLAUDE.md)
- Per customer-deliverable artifact: voice + brand + honest-limitations + provenance gates (4-gate)

**Hop-in:** YES — operator can /li:ship existing branch.

**Skip-conditions:** intent=research-only, intent=local-dev-only.

**Integration:**
- Reads: HARD-RULES.md (mandatory), brand assets (if doc-gen), voice corpus (if customer-facing)
- Writes: PR, release-notes.md, provenance-log.md, customer deliverables, 00-state.md
- Triggers: CAPTURE (final phase)

**Anti-patterns:**
- Direct-push to main without explicit per-batch auth
- Skipping voice gate because "the operator just wrote it themselves"
- Letting honest-limitations be implicit (must be explicit disclaimer)
- Shipping AI-assisted artifacts without provenance log

---

### §2.8 — Phase 8: CAPTURE (~1-2k tokens, 1-3 min)

**Purpose:** durable capture of what was learned. Lessons.md update. ADR draft. EVOLUTION-LOG append. Cold-executor handoff trio. Cross-session continuity material.

**Slash:** `/li:capture`

**Sub-skills invoked:**
- `/li:learn` — capture lesson from corrections during cycle, append to `tasks/lessons.md`
- `/li:adr-new` — bootstrap ADR if non-trivial architectural decision was made
- `/li:lessons-promote` — operator-driven: if lesson is general, promote to Lintel global
- `/li:evolution-log-append` — if CLAUDE.md was modified, log
- `/li:context-save` — write canonical session context for /li:context-restore later
- `/li:retro` — brief retro (what worked / friction / next-time)
- `/li:cold-executor-handoff` — finalize spec.md + plan.md + prompt.md as self-contained trio (NEW — from Architect image)
- `/li:role-debrief` — if role was active, update role-file with anything learned (sensitivity-aware)
- `/li:builder-profile-update` — append session to operator profile (gstack-inherited)

**Agents:**
- **ADRDrafter** (engineering/) — primary, ADR drafting
- **ChangelogMaintainer** (engineering/) — release note polish
- **DocWriter** (engineering/) — synthesize cold-executor trio
- **TrailblazerVoiceCritic** (voice/) — if any captured artifact ships outside

**Artifacts produced:**
- Updated `tasks/lessons.md`
- New `docs/adr/NNNN-<slug>.md` (if decision-worthy)
- `EVOLUTION-LOG.md` append entry
- Cold-executor handoff trio:
  - `spec.md` (canonical master spec — finalized)
  - `plan.md` (final plan.md from PLAN phase, marked DONE)
  - `prompt.md` (self-contained executor prompt — full context, constraints, acceptance criteria, deliverables — so a NEW cold session can re-execute without prior context)
- `retro-<date>.md` (ephemeral, optional)
- Operator profile entry (`~/.lintel/state/operator-profile.jsonl`)
- `00-state.md` final entry — CYCLE COMPLETE

**Gates:** none (CAPTURE is constructive, post-ship).

**Status protocol:**
- DONE — artifacts written, profile updated
- DONE_WITH_CONCERNS — captured but operator deferred ADR draft
- BLOCKED — only if filesystem fails

**Pause-points:**
- Operator confirms lessons.md additions (avoid sycophantic auto-add)
- Operator confirms ADR scope (if decision was small, ADR may be overkill)
- Cold-executor trio: AskUserQuestion "Want to verify trio executes cold?" — optional dogfood

**Hop-in:** YES — operator can /li:capture standalone post-implementation reflection.

**Integration:**
- Reads: cycle history (all 00-state.md entries), corrections from BUILD/REVIEW, CLAUDE.md changes
- Writes: lessons.md, ADRs, EVOLUTION-LOG.md, cold-executor trio, operator profile, 00-state.md final
- Triggers: nothing (cycle complete)

**Anti-patterns:**
- Auto-adding every correction to lessons.md (filter for durable patterns only)
- ADR-writing for trivial decisions
- Skipping cold-executor trio because "we shipped already" — the trio is the durable artifact for future cold sessions
- Polluting role-file with session-specific data (role files = persistent identity, not session log)

---

## §3 — Modes (orthogonal to phases)

5 PRESETS × WorkProfile toggle = matrix of invocation styles.

### 3.1 — Mode presets

Each preset = (phase-subset, audience, voice-tier, compliance-default). Operator picks via flag or default.

```yaml
# Mode preset definitions
hotfix:
  phases: [SENSE, BUILD, REVIEW, SHIP]
  skip: [DEFINE, DISCOVER, PLAN, CAPTURE]
  audience: solo
  voice_tier: internal
  compliance: minimal
  cost_estimate: ~5k tokens, 10-30 min
  use_when: known bug + fix path clear + ship now

customer-engagement:
  phases: ALL_8
  audience: customer
  voice_tier: trailblazer
  compliance: full_SDL  # all 5+7+8 active
  cost_estimate: ~40-80k tokens, 1-3 hours
  use_when: customer-bound deliverable + high-stakes

internal-tool:
  phases: ALL_8 (lighter REVIEW)
  audience: team
  voice_tier: mixed
  compliance: standard  # 5 hard + 3-5 on-demand
  cost_estimate: ~25-50k tokens, 45 min - 2 hours
  use_when: internal tool / MS-internal scaffolding

demo-prep:
  phases: [SENSE, DEFINE, BUILD]
  skip: [DISCOVER, PLAN, REVIEW, SHIP, CAPTURE]
  audience: customer
  voice_tier: trailblazer
  compliance: minimal  # but voice gate active
  cost_estimate: ~15-25k tokens, 30-60 min
  use_when: rapid demo iteration, throwaway code

research-dive:
  phases: [SENSE, DEFINE, DISCOVER]
  skip: [PLAN, BUILD, REVIEW, SHIP, CAPTURE]
  audience: solo
  voice_tier: internal
  compliance: none
  cost_estimate: ~10-20k tokens, 20-40 min
  use_when: explore + understand, no code yet

# Auto-detect mode (NEW)
auto:
  phases: SENSE detects intent + recommends preset
  use_when: operator wants Lintel to pick
```

### 3.2 — WorkProfile toggle (orthogonal)

`~/.lintel/profile.yaml`:

```yaml
# WorkProfile
workprofile: on  # or off

# When ON:
#   - HARD-RULES.md 5 always-on rules ENFORCED (not advisory)
#   - MS SSO required for any external auth in scripts
#   - voice_tier_default: trailblazer (overrides mode default if customer-facing)
#   - first-party-first auto-flagged in plan
#   - telemetry: off (MS-internal default)
#   - voice gate auto-runs on audience=customer
#   - provenance-track auto-runs on AI-assisted artifacts
#   - hook activation: customer-data-block + secret-scan-block + no-direct-main-push by default
#
# When OFF:
#   - Hard-rules advisory only
#   - voice_tier_default: internal
#   - telemetry: opt-in
#   - operator-driven gates only

# Cross-cutting toggles (orthogonal to WorkProfile + mode)
azure_focus: on              # enables /li:az-* toolbox
role_active: field-cto       # or null
default_mode: customer-engagement
checkpoint_mode: explicit    # or continuous
context_warmup_default: standard  # or aggressive / minimal
voice_tier_override: null    # null = use mode default
explain_level: default       # or terse
```

### 3.3 — Active vs passive invocation

**Active mode:** operator types `/li:cycle` and drives.
**Passive mode:** Lintel observes session context and SUGGESTS skill invocation. Operator opt-in via `proactive: true` (gstack-inherited).

```yaml
# ~/.lintel/profile.yaml
proactive: true  # Lintel suggests skill invocation when context matches
# proactive: false  # operator types /commands manually
```

Examples of passive triggers:
- Operator pastes error stack → suggest /li:investigate
- Operator says "ship this" → suggest /li:ship or /li:cycle --from SHIP
- Operator says "let me think about this" → suggest /li:define
- Operator mid-session for >30 turns → suggest /li:context-save

**Auto mode (NEW):** Lintel runs cycle WITHOUT operator confirmation between phases.
```bash
/li:cycle --mode customer-engagement --auto
```
Auto-decides at gates using recommended option (per gstack /plan-tune AUTO_DECIDE opt-in pattern). Operator can intervene at any time.

**Aggressive passive:** Lintel jumps in even without operator prompt at session start, surfaces SENSE report unprompted (`proactive: aggressive`).

---

## §4 — Role-lifting (NEW)

Roles = expert personas with their own knowledge, voice, and outcome-lens that influence the cycle.

### 4.1 — Why role-lifting

A CAIP-SE working with a customer's Field CTO doesn't think the same as one working with a customer's Compliance Officer. Different vocabulary, different success criteria, different what-counts-as-pain. Bringing role context INTO the session lets agents/skills tune outputs to the role they're working with or representing.

Roles are NOT operator personas (that's `tasks/personas.md`). Roles are EXPERT-ROLE persona-lifts — generic or customer-specific personas with deep knowledge.

### 4.2 — Role file structure (AI-optimized)

Storage layer logic:
- **Public roles** (`agents/roles/<role-id>.md`) — generic, MIT, shareable
- **Private roles** (`~/.lintel/roles/private/<role-id>.md`) — customer-specific, gitignored, operator-local
- **Sync** via `bin/li-roles-sync` to private GitHub repo (per-operator, like lessons-sync)

Role file format (AI consumption optimized):

```yaml
---
role_id: field-cto
display_name: Field CTO
scope: customer-facing, sales-tech, enterprise-strategy
audience: customer C-suite, internal sales-eng
voice_tier: trailblazer  # default for this role's outputs
sensitivity: public      # or 'private' for customer-specific
last_updated: 2026-05-28
applies_to_phases: [DEFINE, DISCOVER, PLAN, SHIP, CAPTURE]  # not BUILD (technical phase)
companion_agents: [FieldCTOAdvisor, DemoNarrativeArc, ExecutiveBriefingDrafter]
---

# IDENTITY
[One paragraph. Who they are. What they care about. What gets them promoted. What gets them fired. Read at SENSE phase as lightweight context — load 50 tokens worth, not the full role.]

# COLD KNOWLEDGE (top 10 things they know without thinking)
1. <Cold belief 1 — e.g., "Customers always say 'business outcome' but mean 'cost reduction by Q4'">
2. <Cold belief 2>
...
10. <Cold belief 10>

# DECISION CRITERIA
[What makes them say YES vs NO in a meeting. 3-5 bullets.]

# VOICE + COMMUNICATION
- Tone: <descriptors>
- Preferred phrases: ["business outcome", "we've seen customers like", "shift left"]
- Avoided phrases: ["technically", "in theory", "academically"]
- Energy: <high / measured / curious>

# OUTCOME LENS (per cycle phase)
- SENSE: <what to surface for this role>
- DEFINE: <how this role frames the problem — questions they'd ask>
- DISCOVER: <what this role cares about discovering>
- PLAN: <what this role wants in the plan>
- BUILD: <what this role oversees (often nothing — delegate to engineers)>
- REVIEW: <what this role checks personally>
- SHIP: <what this role demands at handoff to customer>
- CAPTURE: <what this role wants to retain for next time>

# ROLE-SPECIFIC INSIGHTS (durable knowledge)
[Top patterns, common mistakes, what differentiates great from good. Free-form.]

# COMPANION SKILLS (when this role is active, prefer these)
- /li:exec-brief — drafts in this role's voice
- /li:proposal-from-context — uses this role's decision criteria

# SENSITIVE CONTEXT (private roles only)
[For customer-specific roles: details that don't leave operator's machine. Filtered out at session-start. Only loaded explicitly via /li:role-deep-dive.]
```

### 4.3 — Role-lifting skills

```
/li:role-activate <role-id>     # load role for current session (LIGHTWEIGHT — identity + voice + outcome-lens summary, ~500 tokens)
/li:role-deep-dive <role-id>    # load full role-file (heavy, on-demand, ~2-3k tokens)
/li:role-frame <artifact-path>  # apply active role's lens to an artifact
/li:role-rotate <new-role-id>   # swap active role mid-session
/li:role-deactivate             # remove active role
/li:roles-list                  # list available roles + last-updated
/li:role-new <id>               # scaffold new role from template
/li:role-update <id>            # add learning to role file (sensitivity-aware)
```

### 4.4 — Session start awareness (lightweight)

SENSE phase reads:
- `~/.lintel/profile.yaml` → `role_active` field
- If set, loads role's IDENTITY + VOICE summary (~500 tokens) into session context
- Does NOT load COLD KNOWLEDGE, OUTCOME LENS, INSIGHTS unless `/li:role-deep-dive` invoked
- Reports: "Role active: <role-id> (deep-dive available)"

This is the LIGHTWEIGHT principle — role aware doesn't mean role-heavy.

### 4.5 — Privacy + sensitivity

- Private roles (customer-specific) live ONLY in `~/.lintel/roles/private/`, gitignored
- `no-customer-data-in-role-file` hook blocks committing roles with customer-PII patterns
- `/li:role-update` sanity-checks for PII before write
- Sync via `bin/li-roles-sync` to operator's private GitHub repo, NOT public Lintel marketplace
- Public roles (`Field CTO generic`, `Compliance Officer generic`) MIT-licensed, shippable

### 4.6 — Role overlay per phase

When role is active, each phase modifies its behavior:

- **SENSE:** include role identity in surface report
- **DEFINE:** apply role's outcome-lens to alternatives (sensitivity-filter for private)
- **DISCOVER:** prioritize what role cares about (e.g., Field CTO cares about cost, performance, compliance landscape)
- **PLAN:** include role-relevant tasks (e.g., for Field CTO, add "draft customer-facing summary" task)
- **BUILD:** typically pass-through (technical phase, role-overlay light)
- **REVIEW:** invoke role's companion agents (e.g., FieldCTOAdvisor for Field CTO role)
- **SHIP:** voice tier from role (Field CTO → trailblazer); customer-facing artifact gates fire
- **CAPTURE:** role-debrief — update role file with learned patterns (operator confirms)

---

## §5 — Context warming (NEW)

On-demand 1M-context utilization beyond what SENSE loads at session-start.

### 5.1 — Why context warming

Default session-start loads ~5-15k tokens (CLAUDE.md, AGENT-INSTRUCTIONS, lessons.md, memory.md, recent ADRs, active role identity). Plenty for most work.

But some tasks benefit from MUCH more context:
- "Help me redesign this 50-file React app" → load all components
- "Compare our ExpressRoute notes against the customer's current Bicep" → load both
- "What did we decide across the last 5 sessions on this branch?" → load session-saves
- "Walk through 10 ADRs related to networking" → load adr/*.md

This requires explicit context warming — the operator says "load these, then we work."

### 5.2 — Context warming skills

```
/li:context-warm <file-glob> [+ <file-glob>] ...   # load specified files into session
/li:context-warm-related <topic>                    # heuristic load: search + dump relevant files
/li:context-warm-sessions <branch> [<n-sessions>]   # load last N session-saves on branch
/li:context-warm-adrs <topic>                       # load topic-relevant ADRs
/li:context-warm-customer <engagement>              # load customer-engagement repo state
/li:context-warm-from-url <url>                     # fetch + dump (e.g., Microsoft Learn doc)
/li:context-dump <session-id>                       # read previous session's /li:context-save
/li:context-snapshot [--name <name>]                # save current context state for later resume
/li:context-budget                                  # show current utilization, recommend warm/cool
/li:context-cool [--keep <patterns>]                # selective drop of context to free budget
```

### 5.3 — Warming patterns

**Smart load via heuristic:**
```bash
/li:context-warm-related "ExpressRoute"
# → scans cwd + ~/.lintel/scaffolding/ + .claude/engineering/design-archive/ for ExpressRoute mentions
# → loads top 10 most-relevant files
# → reports: "Loaded 8 files, ~12k tokens. Budget: 50k / 1M used."
```

**Multi-repo load:**
```bash
/li:context-warm "~/Workspace/customer-acme/**/*.bicep"
/li:context-warm "~/Workspace/customer-acme/CLAUDE.md"
# loads customer's Bicep + their CLAUDE.md for cross-repo reasoning
```

**Session resume:**
```bash
/li:context-warm-sessions v3-dev 5
# loads last 5 sessions' /li:context-save outputs
# operator now has continuity across days
```

**URL load (with sanity):**
```bash
/li:context-warm-from-url https://learn.microsoft.com/azure/expressroute/expressroute-faqs
# WebFetch + dump to context
# WorkProfile=on: validates URL is MS-domain (no customer-data risk)
```

### 5.4 — Context budget tracking

```
/li:context-budget

Output:
─────────────────────────────────────
Current context: 142k / 1M tokens (14%)
Headroom: 858k

Breakdown by source:
- CLAUDE.md + scaffolding: 8k
- Loaded files (last warm): 45k
- Conversation history: 38k
- Subagent results: 12k
- Other: 39k

Recommendations:
- Plenty of headroom for /li:context-warm
- If you plan to /li:build for next 2-3 hours, consider /li:context-cool --keep "current-task-*"
```

### 5.5 — Context warming as session-start option (OPT-IN)

Operator can configure default warm patterns:
```yaml
# ~/.lintel/profile.yaml
context_warmup_default: standard
# standard: load CLAUDE.md, AGENT-INSTRUCTIONS, lessons.md, memory.md, recent ADRs (default ~15k)
# minimal: only CLAUDE.md + AGENT-INSTRUCTIONS (~3k)
# aggressive: standard + last 3 session-saves + role deep-dive if role active (~50k)
```

NEVER auto-loads heavy content unless operator opts in. Honest session-start.

### 5.6 — Cost awareness

Each `/li:context-warm` operation reports:
- Tokens added
- Total budget used after warm
- Estimated cost ($)
- Cooldown opportunity (what could be dropped if budget needed)

---

## §6 — Layered functionality (composable invocation)

The Lintel cycle is invocable at 6 layers of granularity.

### Layer 1: Sub-skill (atomic)
```
/li:premise-check          # just the premise step from DEFINE
/li:tdd-cycle              # just TDD red-green-refactor from BUILD
/li:cross-artifact-analyze # just the cross-section consistency check
```

### Layer 2: Phase (one full phase)
```
/li:sense
/li:define
/li:discover
/li:plan
/li:build
/li:review
/li:ship
/li:capture
```

### Layer 3: Composite (multi-phase shortcuts)
```
/li:plan-and-build         # PLAN → BUILD (skip review/ship)
/li:review-and-ship        # REVIEW → SHIP
/li:fix                    # SENSE → BUILD → REVIEW → SHIP (hotfix pattern)
/li:research               # SENSE → DEFINE → DISCOVER (no build)
```

### Layer 4: Mode preset (full cycle with preset)
```
/li:cycle --mode hotfix
/li:cycle --mode customer-engagement
/li:cycle --mode internal-tool
/li:cycle --mode demo-prep
/li:cycle --mode research-dive
/li:cycle --mode auto
```

### Layer 5: Custom cycle
```
/li:cycle --from PLAN --to SHIP --skip REVIEW
/li:cycle --phases DEFINE,PLAN,BUILD
```

### Layer 6: Resume
```
/li:resume                 # reads 00-state.md, picks up at next phase
/li:resume --from <phase>  # explicit override
```

---

## §7 — Renaming plan (atomic execution)

When approved, this runs as a discrete branch + commit sequence:

1. **Create branch:** `lintel-rebrand` from `v3-dev`
2. **Path renames (git mv preserves history):**
   - `bin/li-scaffold` → `bin/li-scaffold`
   - `bin/li-doctor` → `bin/li-doctor`
   - `bin/li-lessons-sync` → `bin/li-lessons-sync`
   - `bin/li-lessons-promote` → `bin/li-lessons-promote`
   - `bin/li-update` → `bin/li-update`
   - `bin/li-adr-new` → `bin/li-adr-new`
3. **Skill renames:**
   - `skills/li:cli-fingerprint/` → `skills/li-doctor/` (deprecate cli-fingerprint, replaced by li-doctor)
   - `skills/li:doctor/` → `skills/li-doctor/` (merge)
   - `skills/li:eval/` → `skills/li-eval/`
   - `skills/li:scaffold/` → `skills/li-scaffold/`
   - All `li-*` skill names in frontmatter `name:` field → `li-*`
4. **Plugin manifest changes:**
   - `.claude-plugin/plugin.json` — `name: "lintel"` (full word for marketplace), description starts "Lintel — ..."
   - `.codex-plugin/plugin.json` — same
   - `.cursor-plugin/plugin.json` — same + displayName "Lintel"
   - `gemini-extension.json` — `name: "lintel"`
   - All other plugin manifests
5. **Sed-driven replacements (mass):**
   - `Lintel` → `Lintel` (case-sensitive)
   - `lintel` → `lintel` in prose (be careful with skill prefixes; do skill renames first)
   - `~/.lintel/` → `~/.lintel/`
   - `jokerman-lintel` → `jokerman-lintel`
   - `jokerman89/jokerman-lintel` → `jokerman89/jokerman-lintel`
   - `jokerman89` → `jokerman89` (note: lowercase, since GH username changed)
6. **Skill invocation namespace:**
   - Operator types `/li:qa`, `/li:az-tldr`, `/li:cycle`
   - Wait — the user wants `/li:command` short form. Plugin name = "lintel" gives `/li:` namespace.
   - **DECISION needed:** plugin name "li" (gives `/li:cycle`) vs "lintel" (gives `/li:cycle`). Recommend "li" for ergonomics (3 chars beats 6 chars typed daily). Marketplace display name = "Lintel".
7. **Entrypoint files:**
   - Root `CLAUDE.md` — rewrite for Lintel
   - Root `AGENTS.md` — rewrite for Lintel + Codex
   - Root `GEMINI.md` — rewrite for Lintel + Gemini
8. **Docs:**
   - `README.md` — full rewrite with Lintel branding + cycle overview + role-lifting + context-warming preview
   - `CHANGELOG.md` — v3.5.0-dev entry for rename + cycle + roles + context-warming
   - `SHIP-GATE.md` — update gate names + Lintel references
   - `LAYERS.md` — update 2-kategori-model + cycle phases as third axis
   - `AGENT-INSTRUCTIONS.md` — update to reference Lintel cycle
   - All design docs in `.claude/engineering/design-archive/` — `li-v2-design.md` → `lintel-v2-design.md` (historical), etc.
   - All per-CLI docs in `docs/per-cli/`
9. **GitHub repo rename:**
   - `gh repo rename jokerman-lintel` (from within the repo)
10. **Git remote update:**
    - `git remote set-url origin https://github.com/jokerman89/jokerman-lintel.git`
11. **Tests:**
    - `tests/unit/plugin-manifests-valid.sh` — update name expectations
    - `tests/unit/agents-categorized.sh` — no change (categories same)
    - Add `tests/unit/li-skill-names.sh` — verify all skills have `li-*` name prefix
12. **install.sh + verify.sh updates:**
    - LINTEL_HOME → LINTEL_HOME env var
    - All path references
13. **Verify green:** `bash install/verify.sh --all`
14. **Atomic push:** `lintel-rebrand` branch → operator confirms → merge to `v3-dev` (or replace v3-dev)

Estimated CC-time: ~1-2 hours mechanical execution.

---

## §8 — What's lifting vs what's staying

### Lifting from current v3 (preserved depth):
- All 81 skills — renamed but content preserved
- All 78 agents — renamed if needed, otherwise unchanged
- 15 hooks — paths unchanged (just hooks/shared/)
- Plugin manifest pattern — unchanged (just `name:` updates)
- Multi-CLI portability — unchanged
- 5+7+8 compliance — unchanged
- Trailblazer voice corpus — unchanged content, renamed file refs
- Scaffolding templates — unchanged
- Bin scripts — renamed
- CHANGELOG history — preserved (v2, v3 entries kept)
- ADR + EVOLUTION-LOG mechanisms — preserved

### Adding (new in v3.5+):
- 8-phase Lintel cycle as named pipeline
- 8 phase-skills (/li:sense, /li:define, /li:discover, /li:plan, /li:build, /li:review, /li:ship, /li:capture)
- ~40 sub-skills per phase (some new, many existing renamed)
- /li:cycle orchestrator
- /li:resume
- 5 composite shortcuts (/li:fix, /li:research, /li:plan-and-build, /li:review-and-ship)
- 5 mode presets (hotfix, customer-engagement, internal-tool, demo-prep, research-dive)
- WorkProfile toggle + profile.yaml schema
- Role-lifting (7 skills + role-file format + sync mechanism)
- Context warming (9 skills + budget tracking)
- Cold-executor handoff trio (CAPTURE phase output)
- 00-state.md incremental state file
- Cross-section consistency analyze
- Cost estimate gate

### Removing:
- "Lintel" name (becomes Lintel)
- li-* file prefixes (become li-*)
- jokerman-lintel repo name (becomes jokerman-lintel)
- jokerman89 namespace (becomes jokerman89)
- /li:cli-fingerprint spec-only skill (replaced by runtime /li:doctor)

---

## §9 — Themes preserved (operator's constraints)

Per user: **snabbt, underhållsfritt, smart, effektivt, ifrågasättande, explicit heltäckande.**

- **Snabbt** — Layer 1-3 invocations (sub-skill, phase, composite) give fast paths
- **Underhållsfritt** — Plugin-manifest pattern avoids per-CLI maintenance
- **Smart** — passive proactive suggestions + auto-mode + context-warming heuristics
- **Effektivt** — token budgets + cost estimates + selective phase invocation
- **Ifrågasättande** — premise-check + forcing questions + two-stage review + adversarial spec review
- **Explicit heltäckande** — named phases + named sub-skills + per-phase artifacts + 00-state.md

**Integration, professionalism, velocity, declutter, performance, purpose** — embedded:
- Every skill names its companions (integration)
- Voice rules + adversarial review (professionalism)
- Composite shortcuts + auto-mode (velocity)
- Honest skip-conditions per phase (declutter)
- Model selection by complexity (performance)
- Each phase has clear artifact + gate + integration (purpose)

---

## §10 — Open questions for operator

Before execution:

1. **Plugin namespace prefix:** confirm `/li:` (plugin name "li") vs `/li:` (plugin name "lintel"). Recommend "li" for ergonomics.
2. **Skill renames scope:** ALL 81 skills get `li-` prefix in frontmatter `name:` field, OR only the new cycle-phase skills? Recommend ALL (consistency).
3. **Branch strategy for rename:** new `lintel-rebrand` branch → merge to v3-dev, OR rebase v3-dev directly? Recommend new branch (atomicity + reviewable).
4. **Role storage repo:** Public roles ship in main repo. Private roles sync via separate private git repo via `bin/li-roles-sync` — confirm this pattern (mirrors `bin/li-lessons-sync`).
5. **WorkProfile default:** when operator first runs `/li:cycle`, prompt them to set workprofile? Or default to ON for MS-internal scaffolding-honest? Recommend prompt-first-run (confirm operator's choice explicitly).
6. **00-state.md location:** in cwd of working repo, or in `.lintel/state/` subdirectory? Recommend `.lintel/state/00-state.md` (avoid root clutter, gitignored by default for working repos).
7. **Cold-executor handoff trio scope:** must be self-contained from scratch (true cold), OR may reference `~/.lintel/` resources (cold-but-Lintel-installed). Recommend reference-Lintel-installed (cold-but-tooled) — fully cold means re-bootstrap which is rare.

---

## §11 — Success criteria (post-implementation validation)

This design succeeds if:

1. Operator can invoke `/li:cycle --mode customer-engagement` and the full 8 phases execute with appropriate sub-skills + agents per phase
2. Operator can invoke `/li:fix` for hotfix and skip non-relevant phases automatically
3. Operator can `/li:resume` mid-cycle from a previous session and pick up at the right phase
4. Active role context loads at SENSE in <500 tokens, deep-dive only on demand
5. `/li:context-warm "ExpressRoute"` loads 8-12 relevant files, reports budget impact
6. WorkProfile=on enforces HARD-RULES at SHIP gate (verified via test fixture: secret-containing PR blocked)
7. CAPTURE produces cold-executor trio that a NEW session can re-execute without prior context (verified via dogfood)
8. Existing 81 skills + 78 agents still work via their `li-*` renamed forms (verified via verify.sh --all)
9. Plugin install on Claude Code + Codex + Cursor + Gemini gives same skill catalog
10. Document set (README, CHANGELOG, design docs) is internally consistent with new naming

---

## §12 — Recommended next steps

After approval of this doc:

1. **Operator confirms 7 open questions above** (D9 — combined AskUserQuestion)
2. **Execute rename** (Phase A — atomic branch + sed + git mv + GH rename + remote update)
3. **Build 8 phase-skills** (Phase B — each ~200-400 lines per current depth standard)
4. **Build /li:cycle orchestrator + /li:resume** (Phase C)
5. **Build composite shortcuts** (Phase D — /li:fix, /li:research, etc.)
6. **Build role-lifting infra** (Phase E — 7 skills + role file format + bin/li-roles-sync + 3 default public role files: Field-CTO, Solution-Architect, Engineering-Manager)
7. **Build context-warming infra** (Phase F — 9 skills + budget-tracking)
8. **Add cold-executor handoff** (Phase G — spec.md + plan.md + prompt.md generators in CAPTURE)
9. **Update docs comprehensively** (Phase H — README, CHANGELOG, SHIP-GATE, LAYERS, AGENT-INSTRUCTIONS, all design docs)
10. **Add tests** (Phase I — phase-skill invocation, role-load, context-warm, cycle E2E)
11. **Verify --all green + dogfood** (Phase J — operator runs /li:cycle --mode internal-tool to build a simple internal-tool, validates pattern)
12. **Open PR + tag v3.5.0** (Phase K)

Estimated total: ~3-4 work-days CC-time (mechanical execution + new skill content + tests + docs).

---

## §13 — What I noticed

- **Du sa "djupa i varje cykel steg/fas"** två gånger i samma meddelande. Inte "design the phases" — DJUPA. Verbet på svenska. Du vill inte ha översikt. Du vill ha innehåll. Det är skillnaden mellan en arkitekturskiss och ett bygg-ritning.
- **Du föreslog inte själv lösningen för rollerna.** Du beskrev problemet (sensitive data, voice-impact, lightweight-vs-deep, outcome-from-role-file) och sa "strukturera rollfilen på det sätt som gör den bäst för dig att konsumera." Du gav mig domain + constraints + free hand på shape. Det är ovanligt och produktivt — många operators överspecar.
- **"Snabbt, underhållsfritt, smart, effektivt, ifrågasättande, explicit heltäckande."** Sex ord. Inga och-bindeord. Sex tema-pelare som ska gälla parallellt. Den listan blir kvalitets-checklistan mot vilken jag mäter varje sub-skill jag designer.
- **Du sa "KÖR!" mitt i en mening om kvalitet.** Inte separat. Det är inte en oavsiktlig avlossning — det är operatorns sätt att säga "kvalitet och hastighet är inte motsatser om man har struktur."

---

## Status

**DRAFT** — awaiting operator approval (D9 combined question on the 7 open items in §10).

If approved: Phase A (rename execution) starts immediately.
