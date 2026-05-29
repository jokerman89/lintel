# Cohort 4 findings — domain-specialist agents in cycle phases

**Cohort:** 4 (agents)
**Scope:** 83 agents in `agents/<category>/<Name>.md` across 10 categories
(engineering 25, ms-specific 15, customer 8, security 8, devops 7, compliance 6,
communication 5, frontend 5, doc-gen 3, voice 1).
**Method:** template-level D1-D14 once (agents share a template); per-agent only
where an agent deviates; full agent→phase/skill invocation mapping; orphan +
should-delegate analysis against `docs/concepts/agent-dispatch-rules.md`.
**Status:** complete.

> Operator directive honored: **NO-CUT.** Every orphan is a *wire-it-in*
> recommendation, never a delete. The motto — *kraftfullt från start och
> ständigt evolverande* — means thin/unreached components get raised, not removed.

---

## Part A — Template-level D1-D14 record (the agent shape)

Agents share one common Markdown shape: YAML frontmatter
(`name, category, [v1_alias], color, tools, voice, cli_support, [tier]`) followed
by a body with these sections in near-identical order across all 83:
`What this agent does` → `When to invoke` → `When NOT to invoke` → `Workflow` →
`Report format` → `Edge cases / what to do when blocked` → `Voice tier behavior`.
The review correctly flagged that per-agent D1-D14 is boilerplate, so this single
record covers the shape; per-agent records below appear ONLY for deviations.

```yaml
component: agents/<category>/<Name>.md   # the COMMON agent template
kind: agent
cohort: 4
dimensions:
  D1_head:
    state: partial
    nano: "body section 'When to invoke' + 'Workflow' step 1 (Read context/state)"
    macro: agent spawned by a skill via Agent/Task tool, or recommended by DISCOVER Step 6
    high: "dedicated-vs-inline dispatch rule (agent-dispatch-rules.md)"
    finding: >
      Head is a prose 'When to invoke' list, not a declared/validated input
      contract. No frontmatter expected_inputs. Inputs (diff, scope, brief, flags)
      are described in body Workflow but never validated at head — agent assumes
      caller passed the right shape.
    proposed: >
      Add an `expected_inputs:` frontmatter block (or a standard '## Inputs
      (required/optional)' body section) mirroring the strongest peers
      (ShaderEngineer declares --brief required, --visual-thesis/--perf-budget
      optional with defaults). Make input validation step 1 of every Workflow.
    why: >
      Goal: agents become contract-bound, callable uniformly by any skill or by
      DISCOVER dynamic dispatch. Elegant form = one frontmatter field, not prose.
      gstack subagents declare typed briefs; superpowers SDD passes curated briefs.
      ShaderEngineer already does this inside Lintel — raise the other 82 to it.
  D2_tail:
    state: partial
    nano: "body section 'Report format' (a fenced block); voice/security agents emit YAML"
    macro: agent returns a report to the spawning skill
    high: "subagent reports, main agent decides (separation of concerns)"
    finding: >
      Every agent declares a Report format (good), but the EXIT STATUS protocol is
      inconsistent. Some declare DONE/BLOCKED/NEEDS_CONTEXT verdicts
      (ShaderEngineer: NEEDS_CONTEXT; OneCSAuditor: 'Overall verdict'); most use a
      free-text 'Verdict:' or 'Summary' line. No uniform DONE/BLOCKED protocol like
      the phase skills use.
    proposed: >
      Standardize a tail status vocabulary across all agents
      (DONE | BLOCKED | NEEDS_CONTEXT | DEGRADED) as the last line of every Report
      format, matching the phase-skill status protocol. Keep each agent's rich
      report body; just add the machine-readable terminal status.
    why: >
      Goal: callers (skills, autoplan) can branch on agent outcome without parsing
      prose. More elegant than per-agent free text. speckit/GSD gate on explicit
      status; Lintel's own phase skills already do — agents should match.
  D3_objects:
    state: partial
    nano: "body Workflow (in) + Report format (out); shape is prose, not declared"
    macro: in/out contract between skill and agent
    high: "shared-schema discipline (define once, both sides import)"
    finding: >
      In/out contract is written as prose, not a declared schema. Where an agent
      emits a structured artifact (ShaderEngineer shader.json schema_version:1;
      voice agent YAML), the schema lives in the consuming SKILL.md — good, single
      source. But text-report agents have no out-schema at all.
    proposed: >
      For agents that emit parseable artifacts, cite the schema location in
      frontmatter (`emits: shader.json (frontend-shader SKILL.md)`). For
      text-report agents, keep prose but pin the report headers as the contract.
    why: >
      Goal: no double-definition drift. ShaderEngineer's 'emits shader.json per
      SKILL.md contract' is the model — reference, don't duplicate.
  D4_entrypoints:        # THE key dimension for this cohort
    state: partial
    nano: "skills/discover/SKILL.md:110-125 (Step 6 dynamic scan) + per-skill 'Use the X agent' mentions"
    macro: who can reach this agent — static skill mentions vs dynamic DISCOVER scan
    high: "every capability is reachable from some entry-point (no dead agents)"
    finding: >
      Two dispatch paths exist and they DISAGREE on coverage.
      (1) STATIC: individual skills name agents ('Use the AzureArchitect agent').
      (2) DYNAMIC: DISCOVER Step 6 scores ALL agents by description-keyword match
      against the wedge, then PLAN dispatches the top picks. BUT the Step 6 loop
      enumerates only 9 categories and OMITS `frontend` (see F-401) — so the
      dynamic path cannot reach 5 agents, and 11 agents are named by no skill at
      all (see F-402). Net: D4 coverage is NOT uniform; some agents are reachable
      by both paths, some by one, some by neither.
    proposed: >
      (a) Fix the DISCOVER Step 6 category list to include all 10 categories.
      (b) Treat 'reachable by DISCOVER dynamic scan' as the baseline contract: any
      agent whose description keyword-matches a wedge is reachable. Then the only
      true orphans are agents whose description never matches because no skill
      domain exercises that wedge — wire those into a phase explicitly.
    why: >
      Goal: no agent is unreachable. DISCOVER's dynamic scan is the elegant
      mechanism (one loop reaches all agents) — but it must enumerate every
      category. This is a one-line fix with system-wide reach.
  D5_checkpoints:
    state: absent
    nano: "not declared in any agent"
    macro: agents run inside a phase; the PHASE writes checkpoints, not the agent
    high: "resume/replay can reconstruct what ran"
    finding: >
      Agents write no checkpoint of their own. The spawning phase logs that an
      agent ran (via discover-report agents_recommended / PLAN dispatch), but the
      agent itself leaves no 00-state/envelope entry. For short-lived review agents
      this is acceptable (D6 below); for long BUILD-implementer agents it is a gap.
    proposed: >
      Long-running implementer/migrator agents (FrontendBuilder, Migrator,
      Refactorer, CloudTestSuiteAuthor) should emit a one-line checkpoint to the
      phase envelope on completion (agent, scope, verdict, artifacts). Review/audit
      agents need none — their Report IS the checkpoint.
    why: >
      Goal: resume after interruption mid-BUILD knows which task-agent finished.
      Elegant = reuse the phase envelope, don't invent per-agent state files.
  D6_recovery:
    state: partial
    nano: "body 'Edge cases / what to do when blocked' + 'Failure recovery' (ShaderEngineer)"
    macro: what happens when the agent can't proceed
    high: "stub-doc-and-continue vs halt-pipeline consistency"
    finding: >
      Recovery is well-covered as prose ('Edge cases' is present in all 83) but the
      RECOVERY VOCABULARY is inconsistent: some say STOP (OneCSAuditor on
      customer-data), some 'degraded mode' (OneCSAuditor on missing rules), some
      NEEDS_CONTEXT (ShaderEngineer), some 'note as low-confidence' (Architect,
      CodeReviewer). No uniform mapping to the D12 failure-mode taxonomy.
    proposed: >
      Map every 'Edge cases' bullet to one of four recovery verbs:
      STOP-AND-SURFACE | DEGRADE-AND-CONTINUE | NEEDS-CONTEXT | LOW-CONFIDENCE-NOTE.
      Keep the prose; tag each bullet with its verb.
    why: >
      Goal: callers handle agent failure uniformly. OneCSAuditor's STOP-on-customer
      -data is the gold standard for hard stops — generalize the taxonomy from it.
  D7_pack_influence:
    state: absent
    nano: "no agent references pack/WorkProfile in frontmatter or body"
    macro: active pack should narrow which agents DISCOVER recommends
    high: "pack-driven behavior promise"
    finding: >
      No agent declares pack/WorkProfile sensitivity. DISCOVER Step 6 scores by
      description-keyword only — the active pack does NOT bias which agents are
      recommended. An ms-specific pack and a generic-OSS pack get the same agent
      recommendations for the same wedge keywords.
    proposed: >
      Add an optional `packs:` affinity hint to agent frontmatter (e.g.
      AzureArchitect packs:[ms-azure]; SecurityAuditor packs:[*]). DISCOVER Step 6
      boosts/filters by active pack. Backward-compatible: no `packs:` = always
      eligible.
    why: >
      Goal: make the pack promise measurable at the agent layer. Elegant = a
      frontmatter affinity tag consumed by the existing Step 6 loop, not a new
      resolver. This is the single biggest cross-cohort lever for pack-driven UX.
  D8_frontmatter:
    state: partial
    nano: "frontmatter block; see F-403 (two cli_support dialects), F-404 (tier missing)"
    macro: frontmatter is the machine-readable contract for every consumer
    high: "frontmatter completeness / cli portability"
    finding: >
      Frontmatter is mostly uniform but has TWO concrete deviations (full per-agent
      lists in Part C): (1) cli_support has two incompatible dialects —
      compact `[claude-code, codex]` (most) vs structured list `- cli: x level:
      full` (all 5 frontend, all 3 doc-gen, ContextBudgetAdvisor = 9 agents).
      (2) `tier:` present on 59 agents, ABSENT on 24 (mostly engineering + 2
      devops). No agent declares expected_inputs/outputs, necessity, or
      brief_forge_handoffs (cohort-wide gap, consistent with other cohorts).
    proposed: >
      Pick ONE cli_support dialect (recommend the structured list — it carries
      per-cli `level`, which the compact form loses) and normalize all 83. Add
      `tier:` to the 24 that lack it. Defer necessity/expected_inputs to the
      framework-wide schema decision (raised in cohorts 1-3).
    why: >
      Goal: one parseable frontmatter schema. The structured cli_support form is
      strictly more expressive (it has `level`), so normalize UP to it, not down.
  D9_brief_forge:
    state: absent
    nano: "no agent references Brief Forge"
    macro: hand-off into/out of an agent is a Brief Forge candidate
    high: "Brief Forge at hand-offs promise"
    finding: >
      No agent fires Brief Forge at its boundaries. Agent spawning IS a hand-off
      (main → subagent → main) — by the dedicated-vs-inline rule the subagent
      'should be given a curated brief (Architect-style)'. Today the brief is
      ad-hoc, assembled by whichever skill spawns the agent.
    proposed: >
      Flag agent-spawn as a Brief Forge hand-off point. When a phase dispatches a
      dedicated agent (DISCOVER/REVIEW/BUILD per dispatch rules), Brief Forge
      should compose the curated brief. Declare `brief_forge_handoffs: [in]` on
      agents that benefit from a curated brief (Architect, the BUILD implementers,
      adversarial reviewers).
    why: >
      Goal: realize the 'curated brief, not raw context' rule the dispatch doc
      already mandates. Brief Forge is the designed mechanism — wire agent-spawn to
      it rather than leaving each skill to hand-roll the brief.
  D10_knowledge_lessons:
    state: partial
    nano: "Architect Workflow step1 'recent ADRs'; CodeReviewer step2 'recent ADRs'; most agents: absent"
    macro: agents should consult lessons.md / ADRs / knowhow tag-funnel at read step
    high: "cross-session memory promise (lessons accumulate AND are consulted)"
    finding: >
      Consultation is uneven. Architect and CodeReviewer read 'recent ADRs';
      OneCSAuditor reads rules files. The majority of agents do NOT consult
      lessons.md or the tag-funnel even when relevant (e.g. RegressionDetective,
      DebugForensics would benefit from prior-incident lessons). Consultation is
      prose-implicit, never declared in frontmatter.
    proposed: >
      Add a `consults:` frontmatter hint (lessons | adrs | knowhow) and make 'read
      lessons/ADRs relevant to scope' an explicit Workflow step for agents whose
      work benefits (reviewers, debuggers, architects, migrators).
    why: >
      Goal: the operator-relation learning thread is consulted, not just written
      (X3 concern). Architect's ADR-read is the model — generalize it.
  D11_subagent_delegation:
    state: n/a
    nano: "agents ARE the delegation target; they generally do not re-spawn"
    macro: agent is the leaf of the dispatch tree
    high: "context cleanliness"
    finding: >
      Uniform and correct: agents are leaves — they read broadly, return narrowly,
      and do not spawn further subagents. No deviation. (Tools lists are scoped to
      mostly Read/Grep/Glob with Write/Bash/Edit only where the role needs it,
      consistent with minimal-tools discipline.)
    proposed: "no change — uniform with cohort and with SUBAGENT-GUIDE minimal-tools rule"
    why: "Goal already met: separation of concerns is clean at the agent layer."
  D12_failure_mode:
    state: partial
    nano: "body 'Edge cases' / 'Failure recovery' / 'Anti-patterns'"
    macro: agent failure semantics
    high: "failure-mode consistency with peers"
    finding: >
      Same root issue as D6 — the failure VERBS vary. Additionally only some agents
      (ShaderEngineer) have a dedicated 'Failure recovery' + 'Anti-patterns'
      section; most fold failure into 'Edge cases'. Depth is uneven: ShaderEngineer
      is the strongest peer (Edge cases + Failure recovery + Anti-patterns +
      L-001/2/3 application); a typical engineering agent has only Edge cases.
    proposed: >
      Raise thinner agents toward the ShaderEngineer shape: add an 'Anti-patterns'
      section where one is load-bearing, and tag failures with the D6 verb
      taxonomy. Do not remove the lean form where the agent is genuinely simple.
    why: "Goal: uniform failure taxonomy. ShaderEngineer sets the bar — raise toward it."
  D13_observability:
    state: absent
    nano: "no agent writes to usage log / envelope / hooks.jsonl"
    macro: operator should see an agent ran, what it cost
    high: "jobs visibility promise"
    finding: >
      Agents leave no observability trail of their own. The operator sees an agent
      ran only via the spawning skill's output / discover-report
      agents_recommended. No per-agent entry in the usage log or envelope; no cost
      attribution. Uniform across all 83 — uniformly ABSENT.
    proposed: >
      Have the spawning skill (not the agent) write a one-line envelope/usage-log
      entry per agent dispatch: agent, scope, verdict, token-cost. Keeps the agent
      a pure leaf while making dispatch observable.
    why: >
      Goal: jobs visibility extends to subagent work. CostAnalyzer already reasons
      about per-step cost — feed agent dispatches into the same log.
  D14_necessity:
    state: absent
    nano: "no agent declares necessity / gap_if_skipped"
    macro: is this agent REQUIRED/RECOMMENDED/OPTIONAL for its phase
    high: "necessity declaration promise"
    finding: >
      No agent declares necessity or gap-if-skipped. 'When to invoke' / 'When NOT
      to invoke' approximate this in prose but give no REQUIRED/RECOMMENDED/OPTIONAL
      grade and no 'what breaks if you skip me'. Consistent cohort-wide gap.
    proposed: >
      Add `necessity:` + `gap_if_skipped:` to frontmatter. Most domain agents are
      OPTIONAL/RECOMMENDED; a few are STRONGLY-RECOMMENDED at specific gates
      (SecurityAuditor before ship, OneCSAuditor before release-ev2).
    why: >
      Goal: operator can reason about skipping. Architect (the design tool, not the
      agent) declares per-section necessity — adopt the same pattern for agents.
peer_comparison:
  strongest_peer_in_cohort: agents/frontend/ShaderEngineer.md
  this_component_depth: below-bar (typical agent)
  uplift_needed: >
    ShaderEngineer is the deepest agent (declared flag-inputs with defaults, emits
    a versioned schema, explicit 'none' short-circuit, Anti-patterns, Failure
    recovery, L-001/2/3 application, auto-invoke entry-points named). Bring the
    typical agent up to: declared inputs (D1), terminal status verb (D2), failure
    verb taxonomy (D6/D12), and named entry-points (D4).
operator_decision_required: yes   # cli_support dialect choice + pack-affinity design + brief-forge wiring
priority: high
```

---

## Part B — Full 83-agent → phase/skill invocation mapping

Legend for **invoked?**:
`static` = at least one skill names the agent as a dispatch hint or 'Use the X
agent'. `dynamic-only` = reachable solely via DISCOVER Step 6 keyword scan (no
static mention). `ORPHAN` = no skill names it AND (for frontend) the dynamic scan
omits its category. Counts are skill-files referencing the agent name.

> Caveat: counts include incidental mentions (e.g. az-tldr service templates
> reference 'Architect' as a word). The high-count generalists (Architect 28,
> SecurityAuditor 13, AzureArchitect 12) are genuinely wired into multiple phase
> skills; counts of 1-3 are usually a single real dispatch hint.

### engineering (25)
| Agent | refs | invoked? | primary phase(s)/skill(s) |
|---|---|---|---|
| Architect | 28 | static | sense, define, discover, plan, build, review, ship, capture, pair-agent, adr-new |
| Planner | 2 | static | plan |
| Explorer | 0 | **ORPHAN** | (intended DISCOVER role; named only in design docs) |
| ReadOnly | 0 | **ORPHAN** | (core safe-read role; named only in concept/precedence docs + shims) |
| ResearchSynthesizer | 0 | **ORPHAN** | (intended research composite; design docs only) |
| CodeReviewer | 8 | static | plan, build, review, define, code-review |
| SecurityAuditor | 13 | static | plan, build, review (+ security skills) |
| TestRunner | 2 | static | plan, build |
| RegressionDetective | 2 | static | build, review |
| Refactorer | 2 | static | build |
| DebugForensics | 2 | static | review (debug path) |
| SanityChecker | 1 | static | review |
| ReleaseEngineer | 2 | static | ship |
| ChangelogMaintainer | 1 | static | capture |
| ADRDrafter | 2 | static | adr-new / capture |
| APIDesigner | 1 | static | plan/build (design hint) |
| BackendArchitect | 2 | static | plan/build |
| DatabaseDesigner | 1 | static | plan/build (data) |
| DataPipelineDesigner | 1 | static | plan/build (data) |
| DocWriter | 2 | static | capture / doc-gen |
| FrontendBuilder | 2 | static | build (frontend) |
| AccessibilityChecker | 3 | static | review/build (frontend a11y) |
| ContextBudgetAdvisor | 2 | static | context-warm skills |
| CostAnalyzer | 9 | static | plan/ship cost gates |
| Migrator | 2 | static | build (migrations) |

### ms-specific (15)
| Agent | refs | invoked? | primary phase(s)/skill(s) |
|---|---|---|---|
| AzureArchitect | 12 | static | discover/plan (Azure wedge), az-* skills |
| AzureOpenAIAdvisor | 5 | static | plan (AOAI), az-* |
| BicepReviewer | 9 | static | review (IaC), az-* |
| ARMTemplateReviewer | 1 | static | review (IaC) |
| KeyVaultAuditor | 6 | static | review/security (secrets) |
| GraphAPIAdvisor | 4 | static | plan/build (Graph) |
| M365CopilotAdvisor | 1 | static | plan (M365) |
| ProvenanceVerifier | 2 | static | ship/compliance |
| OneCSAuditor | 3 | static | review/release-ev2 (onecs-check) |
| CAIPEngagementCoach | 1 | static | engagement skills |
| FieldCTOAdvisor | 3 | static | strategy/advisory skills |
| FirstPartyMigrator | 1 | static | build (first-party-first) |
| AIStartupAdvisor | 0 | **ORPHAN** | (design docs only) |
| CloudTestSuiteAuthor | 0 | **ORPHAN** | (design docs + CHANGELOG only) |
| HybridScenarioArchitect | 0 | **ORPHAN** | (design docs only) |

### security (8) — all wired
| Agent | refs | invoked? | primary phase(s)/skill(s) |
|---|---|---|---|
| SecurityAuditor | 13 | static | plan/build/review/security |
| ThreatModelDrafter | 5 | static | plan/security |
| SecretsScanReviewer | 3 | static | review/security |
| DependencyAuditor | 2 | static | review/security |
| SBOMAuditor | 2 | static | review/security |
| OAuthFlowReviewer | 2 | static | review (auth) |
| JWTSecurityReviewer | 2 | static | review (auth) |
| PrivacyBoundaryAudit | 2 | static | review/compliance |

### compliance (6) — all wired
| Agent | refs | invoked? |
|---|---|---|
| RAIReviewer | 3 | static (rais-* skills) |
| EUAIActReviewer | 3 | static |
| GDPRReviewer | 2 | static |
| SDLReviewer | 2 | static |
| SOC2Reviewer | 1 | static |
| AGTReviewer | 1 | static (entra-agent-id) |

### devops (7)
| Agent | refs | invoked? |
|---|---|---|
| TerraformReviewer | 3 | static (review IaC) |
| K8sManifestReviewer | 3 | static |
| OneBranchReviewer | 2 | static |
| PerformanceAnalyzer | 2 | static |
| EV2PipelineAuditor | 1 | static (release-ev2) |
| GHActionsReviewer | 1 | static |
| DevOpsToolchain | 0 | **ORPHAN** (design docs only; also missing `tier:`) |

### customer (8)
| Agent | refs | invoked? |
|---|---|---|
| ExecutiveBriefingDrafter | 3 | static |
| DemoNarrativeArc | 2 | static |
| DemoNarratorJunior | 2 | static |
| ProposalDrafter | 2 | static |
| RFPResponseDrafter | 1 | static |
| WorkshopFacilitator | 1 | static |
| CustomerEmpathyCheck | 0 | **ORPHAN** (design docs only) |
| PostDemoFollowup | 0 | **ORPHAN** (design docs only) |

### communication (5)
| Agent | refs | invoked? |
|---|---|---|
| BlogPostDrafter | 1 | static |
| EmailCustomerDrafter | 1 | static |
| LinkedInPostDrafter | 1 | static |
| NordicSwedishCopyCheck | 0 | **ORPHAN** (design docs only) |
| SlideNarrationCritic | 0 | **ORPHAN** (design docs + CHANGELOG only) |

### frontend (5) — UNREACHABLE via dynamic scan (category omitted in DISCOVER Step 6)
| Agent | refs | invoked? |
|---|---|---|
| FrontendArchitect | 1 | static (frontend-design) — dynamic path blind |
| MotionDirector | 1 | static (frontend-motion) — dynamic path blind |
| TypographyCurator | 1 | static (frontend-type) — dynamic path blind |
| ShaderEngineer | 1 | static (frontend-shader) — dynamic path blind |
| DesignSystemAuditor | 3 | static (frontend-* + review) — dynamic path blind |

### doc-gen (3) — all wired (and all use structured cli_support dialect)
| Agent | refs | invoked? |
|---|---|---|
| WordTechnicalEditor | 5 | static (generate-* skills) |
| WebExperienceCritic | 5 | static |
| PPTNarrativeArchitect | 4 | static (generate-ppt) |

### voice (1)
| Agent | refs | invoked? |
|---|---|---|
| TrailblazerVoiceCritic | 8 | static (rais-customer-voice-check + voice skills) |

---

## Part C — Findings (orphans, should-delegate, template deviations)

### F-401 — DISCOVER dynamic-dispatch scan omits the `frontend` category (HIGH)
- **nano:** `skills/discover/SKILL.md:116` — the Step 6 loop enumerates
  `ms-specific engineering security compliance devops customer communication voice
  doc-gen` (9 categories). `frontend` is missing.
- **macro:** DISCOVER → PLAN dynamic agent-dispatch hint generation.
- **high:** breaks "every capability is reachable from some entry-point". All 5
  frontend agents (FrontendArchitect, MotionDirector, TypographyCurator,
  ShaderEngineer, DesignSystemAuditor) are invisible to the dynamic dispatch path;
  they are reachable ONLY if the operator runs a frontend-* skill by name.
- **proposed:** add `frontend` to the Step 6 category list (one-word fix). Then
  add a shape-test that asserts the Step 6 loop enumerates `ls -d agents/*/`
  (every category) so the list can't drift again.
- **why:** elegant + load-bearing: one mechanism (Step 6) is supposed to reach all
  agents; the bug is a hardcoded list that fell behind the v3.7 frontend category.
  A directory-driven loop (`for cat in agents/*/`) removes the drift class entirely
  — Subtraction Bias: delete the hardcoded list, derive it.
- **operator_decision_required:** no (clear bug-fix). **priority:** high.

### F-402 — 11 orphan agents never named by any skill (HIGH, NO-CUT → wire in)
Orphans (0 skill references; appear only in design docs / catalog / CHANGELOG):
`Explorer, ReadOnly, ResearchSynthesizer` (engineering);
`AIStartupAdvisor, CloudTestSuiteAuthor, HybridScenarioArchitect` (ms-specific);
`DevOpsToolchain` (devops); `CustomerEmpathyCheck, PostDemoFollowup` (customer);
`NordicSwedishCopyCheck, SlideNarrationCritic` (communication).
- **macro / high:** these are built capabilities the cycle never invokes — wasted
  surface that breaks the "no dead agents" promise.
- **Notable sub-cases:**
  - `Explorer` + `ReadOnly` are described as CORE roles in
    `agent-dispatch-rules.md`-adjacent concept docs (`planner-as-module.md`,
    `lintel-v3.5-cycle-and-roles.md`) yet NO skill spawns them. DISCOVER is
    'dedicated (rule a) — open-ended codebase exploration' — that is *exactly*
    Explorer's job, but DISCOVER never names Explorer. Strong should-delegate gap.
  - `ResearchSynthesizer` should be the dedicated agent for the `/li:research`
    composite — verify and wire.
  - `CloudTestSuiteAuthor` should be a BUILD/test dispatch target (it has Write/Edit
    tools — it's a producer, not a reviewer).
- **proposed (NEVER delete):**
  - Wire `Explorer` into DISCOVER Step 6/Step 3 as the default dedicated
    exploration agent (matches dispatch rule a for DISCOVER).
  - Wire `ResearchSynthesizer` into the research composite skill.
  - Wire `CloudTestSuiteAuthor` into BUILD/test phase dispatch hints.
  - For the demo/comms/customer orphans (CustomerEmpathyCheck, PostDemoFollowup,
    NordicSwedishCopyCheck, SlideNarrationCritic), add them as dispatch hints in the
    relevant customer/communication skills and ensure DISCOVER Step 6 surfaces them
    on matching wedges (depends on F-401 + good descriptions).
  - `AIStartupAdvisor, HybridScenarioArchitect, DevOpsToolchain` — name them in the
    matching ms-specific / devops skills.
- **why:** the motto is *evolverande* — built agents must be exercised or they rot
  (description drift, untested reports). Cheapest fix is making each orphan
  reachable by the DYNAMIC path (good description + F-401 fix) rather than
  hand-wiring 11 static mentions; static mention only where a specific gate needs
  a guaranteed dispatch (Explorer in DISCOVER, CloudTestSuiteAuthor in BUILD).
- **operator_decision_required:** yes (which orphans get guaranteed static
  dispatch vs dynamic-only reachability). **priority:** high.

### F-403 — Two incompatible `cli_support` frontmatter dialects (MEDIUM, D8)
- **nano:** compact `cli_support: [claude-code, codex]` (74 agents) vs structured
  list `cli_support:\n  - cli: claude-code\n    level: full` (9 agents: all 5
  frontend, all 3 doc-gen, `engineering/ContextBudgetAdvisor`).
- **macro / high:** per-CLI portability contract; a parser must handle both shapes.
- **proposed:** normalize ALL 83 to the STRUCTURED form (it carries per-cli
  `level:`, which the compact form silently drops — normalize UP, never down).
- **why:** Subtraction Bias on the *parser*, not the data: one shape to parse. The
  structured form is strictly more expressive, so it's the correct survivor.
- **operator_decision_required:** yes (confirm direction = structured).
  **priority:** medium.

### F-404 — `tier:` missing on 24 agents (MEDIUM, D8)
- **nano:** `tier:` absent on 22 engineering agents (ADRDrafter, APIDesigner,
  AccessibilityChecker, Architect, BackendArchitect, ChangelogMaintainer,
  CodeReviewer, ContextBudgetAdvisor, DataPipelineDesigner, DatabaseDesigner,
  DebugForensics, DocWriter, Explorer, FrontendBuilder, Migrator, Planner,
  ReadOnly, Refactorer, ReleaseEngineer, ResearchSynthesizer, SanityChecker,
  TestRunner) + 2 devops (DevOpsToolchain, PerformanceAnalyzer). Present
  (`tier: permissive`) on the other 59.
- **macro / high:** tier gates agent autonomy/permissions; absence = undefined
  default. Note: engineering agents are the cohort that lacks it almost entirely,
  which suggests they predate the tier field and were never back-filled.
- **proposed:** back-fill `tier:` on all 24. Decide the correct tier per agent
  (most engineering reviewers → `permissive`; producers with Write/Bash/Edit like
  FrontendBuilder, Migrator, Refactorer, ReleaseEngineer, DevOpsToolchain may
  warrant a stricter tier — operator call).
- **why:** uniform frontmatter; remove the undefined-default class.
- **operator_decision_required:** yes (per-agent tier for the Write-capable ones).
  **priority:** medium.

### F-405 — Cohort-wide absent dimensions (LOW individually, structural together)
D7 (pack influence), D9 (Brief Forge), D13 (observability), D14 (necessity) are
absent across ALL 83 agents — uniformly. These are not per-agent deviations; they
are framework-level gaps already raised in cohorts 1-3 and tracked at the X-pass
level. Recorded here as the agent-layer instance:
- D7 → add `packs:` affinity hint consumed by DISCOVER Step 6 (highest-leverage).
- D9 → flag agent-spawn as a Brief Forge hand-off (`brief_forge_handoffs: [in]`).
- D13 → spawning skill writes a one-line dispatch entry to the usage/envelope log.
- D14 → add `necessity:` + `gap_if_skipped:`.
- **operator_decision_required:** yes (these are the same framework-schema vote as
  cohorts 1-3 — do not re-vote, fold into the master schema decision).
  **priority:** low (per-agent) / high (as a framework decision).

---

## Cohort 4 summary

- **Agents mapped:** 83 / 83.
- **Orphans (never invoked by any skill):** 11 (F-402) — plus 5 frontend agents
  unreachable via the *dynamic* path due to F-401 (those 5 ARE reachable
  statically, so not counted as full orphans).
- **Template-level deviations (D8):** 2 classes — F-403 (9 agents, cli_support
  dialect) + F-404 (24 agents, missing `tier:`).
- **Strongest peer / bar-setter:** `agents/frontend/ShaderEngineer.md` (declared
  inputs, versioned emit-schema, anti-patterns, failure-recovery, named
  auto-invoke entry-points). Raise the typical agent toward it; cut nothing.
- **Highest-leverage single fix:** F-401 (one-word, restores dynamic reachability
  for the whole frontend category) — convert the hardcoded category list to a
  directory-derived loop to kill the drift class.
- **operator_decision_required count:** 5 (F-402, F-403, F-404, F-405, and the
  template-level pack-affinity/brief-forge wiring in the Part A D7/D9 records).
