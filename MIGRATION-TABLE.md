# JStack v2 Migration Table

Full enumeration of all 65 skills + 40 agents in v1 with v2 rename status. Source of truth consumed by Phase A migration script.

**Naming rule:** mirror MS internal process terminology where one exists. Generic engineering vocabulary stays unchanged. Aliases retained until v2.5 (operator data-driven retirement decision).

---

## Layer 1 — Foundation skills (43)

| v1 name | v2 name | Status | Rename reason |
|---------|---------|--------|---------------|
| `/context-save` | `/context-save` | unchanged | Generic enough; no MS equivalent |
| `/context-restore` | `/context-restore` | unchanged | Same |
| `/clean` | `/clean` | unchanged | Generic |
| `/help` | `/help` | unchanged | Universal |
| `/health` | `/health` | unchanged | Generic |
| `/plan-ceo-review` | `/plan-ceo-review` | unchanged | Already CEO-canonical |
| `/plan-eng-review` | `/plan-eng-review` | unchanged | Already eng-canonical |
| `/plan-design-review` | `/plan-design-review` | unchanged | Already design-canonical |
| `/plan-devex-review` | `/plan-devex-review` | unchanged | Already DX-canonical |
| `/plan-tune` | `/plan-tune` | unchanged | Generic |
| `/ship` | `/release-ev2` | RENAMED | EV2 = Express V2 MS safe-deploy system |
| `/land-and-deploy` | `/release-deploy-ev2` | RENAMED | Same EV2 anchor |
| `/review` | `/review` | unchanged | Generic; pre-landing diff review |
| `/autoplan` | `/autoplan` | unchanged | Orchestrator name is fine |
| `/qa` | `/qa` | unchanged | Universal QA term |
| `/qa-only` | `/qa-only` | unchanged | Same |
| `/investigate` | `/investigate` | unchanged | Universal debug term |
| `/codex` | `/codex` | unchanged | Codex CLI ref |
| `/careful` | `/careful` | unchanged | Generic mode-wrapper |
| `/browse` | `/browse` | unchanged | Generic browser-control |
| `/scrape` | `/scrape` | unchanged | Generic |
| `/make-pdf` | `/make-pdf` | unchanged | Generic |
| `/setup-browser-cookies` | `/setup-browser-cookies` | unchanged | Generic |
| `/open-gstack-browser` | `/open-managed-browser` | RENAMED | Drop "gstack" branding internally |
| `/design-review` | `/design-review` | unchanged | Generic; visual pillar review |
| `/design-consultation` | `/design-consultation` | unchanged | Generic |
| `/design-html` | `/design-html` | unchanged | Generic |
| `/design-shotgun` | `/design-shotgun` | unchanged | Generic |
| `/devex-review` | `/devex-review` | unchanged | Generic |
| `/benchmark` | `/perfbench` | RENAMED | Closer to MS perf-bench term |
| `/canary` | `/safe-deploy-ring` | RENAMED | MS ring-based deploy terminology |
| `/freeze` | `/code-freeze` | RENAMED | Standard MS engineering term |
| `/unfreeze` | `/code-unfreeze` | RENAMED | Same |
| `/setup-deploy` | `/setup-ev2-targets` | RENAMED | EV2-anchored |
| `/learn` | `/learn` | unchanged | Generic |
| `/office-hours` | `/office-hours` | unchanged | Generic |
| `/retro` | `/retro` | unchanged | Generic |
| `/pair-agent` | `/pair-agent` | unchanged | Generic |
| `/skillify` | `/skillify` | unchanged | JStack-specific |
| `/landing-report` | `/landing-report` | unchanged | Generic |
| `/setup-gbrain` | `/setup-brain` | RENAMED | Drop gstack-brain branding |
| `/sync-gbrain` | `/sync-brain` | RENAMED | Same |
| `/document-generate` | `/document-generate` | unchanged | Generic; doc-gen is MS-specific in Layer 3 |

**Layer 1 changes: 11 renames / 32 unchanged (out of 43)**

---

## Layer 3 — Personal advanced (MS-specific) skills (22)

| v1 name | v2 name | Status | Rename reason |
|---------|---------|--------|---------------|
| `/customer-voice-check` | `/rais-customer-voice-check` | RENAMED | RAIS = Responsible AI Standard anchor |
| `/msvoice-rewrite` | `/msvoice-rewrite` | unchanged | Already MS-canonical |
| `/compliance-gate` | `/onecs-check` | RENAMED | 1CS = One Compliance System |
| `/first-party-check` | `/first-party-check` | unchanged | Already canonical MS term |
| `/provenance-track` | `/provenance-track` | unchanged | Generic |
| `/onerai-prep` | `/onerai-submit-draft` | RENAMED | OneRAI canonical; "submit-draft" makes flow explicit |
| `/dsb-prep` | `/dsb-submit-draft` | RENAMED | DSB canonical |
| `/dpia-prep` | `/dpia-submit-draft` | RENAMED | DPIA canonical |
| `/sensitive-use-report` | `/rais-sensitive-use` | RENAMED | RAIS-anchored |
| `/rai-impact-assessment` | `/rais-impact-assessment` | RENAMED | RAIS-anchored |
| `/scaffold-customer-demo` | `/scaffold-engagement-demo` | RENAMED | "Engagement" is CAIP-SE canonical |
| `/scaffold-internal-tool` | `/scaffold-internal-tool` | unchanged | Generic enough |
| `/scaffold-mvp` | `/scaffold-mvp` | unchanged | Generic enough |
| `/demo-deliverable-gen` | `/demo-deliverable-gen` | unchanged | Generic |
| `/transparency-doc-gen` | `/rais-transparency-note` | RENAMED | Maps to RAIS transparency principle |
| `/tier-stamp-agents` | `/agt-tier-stamp` | RENAMED | AGT = Agent Governance Framework |
| `/entra-agent-id-prep` | `/entra-agent-id-submit-draft` | RENAMED | Already Entra-canonical; "submit-draft" makes flow explicit |
| `/caip-audit` | `/caip-audit` | unchanged | Already CAIP-canonical |
| `/context-tokenwatch` | `/context-budgetwatch` | RENAMED | Refocus on budget not raw token-count |
| `/eval-suite-gen` | `/cloudtest-eval-suite` | RENAMED | CloudTest = MS scalable test infra |
| `/jstack-test` | `/onebranch-validate` | RENAMED | OneBranch = governed pipeline matrix-test |
| `/jstack-eval` | `/jstack-eval` | unchanged | JStack-specific |

**Layer 3 changes: 14 renames / 8 unchanged (out of 22)**

---

## New skills introduced in v2 (Phases B-F)

| New skill | Phase | Purpose |
|-----------|-------|---------|
| `/jstack-cli-fingerprint` | B | CLI detection runtime (operator manual override too) |
| `/context-budget` | C | View/modify current phase budget |
| `/context-warmup` | C | Explicit preload of high-leverage context |
| `/perf-mode` | C | Activate 1M context-budget mode for the session |
| `/brand-update` | E | Manual pull from MS brand portal with version tracking |
| `/asset-search` | E | Search `~/.jstack/brand/azure-assets/` |
| `/generate-ppt` | F | Produce branded PowerPoint deck |
| `/generate-word` | F | Produce branded Word doc (variants: technical/customer/transparency) |
| `/generate-web` | F | Produce static demo web page or landing scaffold |
| `/jstack-deprecation-status` | v2.1 backlog | Show alias usage by skill |

---

## Agents — Layer 3 promoted (15)

| v1 name | v2 name | Status | Rename reason |
|---------|---------|--------|---------------|
| `MSComplianceAuditor` | `OneCSAuditor` | RENAMED | 1CS-anchored |
| `RAIReviewer` | `RAIReviewer` | unchanged | Already canonical |
| `TrailblazerVoiceCritic` | `TrailblazerVoiceCritic` | unchanged | Already MS-canonical |
| `CAIPEngagementCoach` | `CAIPEngagementCoach` | unchanged | Already CAIP-canonical |
| `FirstPartyMigrator` | `FirstPartyMigrator` | unchanged | Already canonical |
| `EvalSuiteAuthor` | `CloudTestSuiteAuthor` | RENAMED | CloudTest anchor |
| `ProvenanceVerifier` | `ProvenanceVerifier` | unchanged | Generic |
| `CustomerEmpathyCheck` | `CustomerEmpathyCheck` | unchanged | Domain-specific |
| `DemoNarrativeArc` | `DemoNarrativeArc` | unchanged | Domain-specific |
| `NordicSwedishCopyCheck` | `NordicSwedishCopyCheck` | unchanged | Domain-specific |
| `PrivacyBoundaryAudit` | `PrivacyBoundaryAudit` | unchanged | Domain-specific |
| `HybridScenarioArchitect` | `HybridScenarioArchitect` | unchanged | Domain-specific |
| `FieldCTOAdvisor` | `FieldCTOAdvisor` | unchanged | Domain-specific |
| `AIStartupAdvisor` | `AIStartupAdvisor` | unchanged | Domain-specific |
| `PostDemoFollowup` | `PostDemoFollowup` | unchanged | Domain-specific |

**Layer 3 agent changes: 2 renames / 13 unchanged (out of 15)**

---

## Agents — Layer 4 power-user (25)

All Layer 4 agents are gstack-equivalent generic engineering helpers. No MS-specific terminology mapping applies — these stay unchanged.

| Agent | Status |
|-------|--------|
| `CodeReviewer` | unchanged |
| `ReadOnly` | unchanged |
| `SanityChecker` | unchanged |
| `TestRunner` | unchanged |
| `Architect` | unchanged |
| `Refactorer` | unchanged |
| `Migrator` | unchanged |
| `SecurityAuditor` | unchanged |
| `PerformanceAnalyzer` | unchanged |
| `DependencyAuditor` | unchanged |
| `APIDesigner` | unchanged |
| `DatabaseDesigner` | unchanged |
| `DocWriter` | unchanged |
| `ADRDrafter` | unchanged |
| `ChangelogMaintainer` | unchanged |
| `DebugForensics` | unchanged |
| `Planner` | unchanged |
| `Explorer` | unchanged |
| `ResearchSynthesizer` | unchanged |
| `ReleaseEngineer` | unchanged |
| `BackendArchitect` | unchanged |
| `FrontendBuilder` | unchanged |
| `DevOpsToolchain` | unchanged |
| `DataPipelineDesigner` | unchanged |
| `AccessibilityChecker` | unchanged |

**Layer 4 agent changes: 0 renames / 25 unchanged (out of 25)**

---

## New agents introduced in v2 (Phase F)

| New agent | Phase | Purpose |
|-----------|-------|---------|
| `PPTNarrativeArchitect` | F | Designs slide arc + per-slide content goal before generation |
| `WordTechnicalEditor` | F | Reviews technical Word output for accuracy + voice + structure |
| `WebExperienceCritic` | F | Applies 6-pillar critique to generated web output |
| `ContextBudgetAdvisor` | C | Layer 4 agent that suggests phase declarations for unstructured tasks |

---

## Concept renames (architecture-level, not skill/agent names)

| v1 concept | v2 concept | Why |
|------------|------------|-----|
| "5-level agent precedence" | "AGT identity precedence" | Maps to MS AGT framework |
| "Layer 2 always-on" | "SDL always-on" | SDL = canonical MS framing |
| "Layer 2 on-demand" | "SDL on-demand" | Same |
| "Layer 2 reference docs" | "SDL reference" | Same |
| Directory `scaffolding/02-compliance/` | `scaffolding/02-sdl/` | Match SDL framing |
| `TRAILBLAZER-CORPUS.md` | `OurVoice-corpus.md` | "Our Voice" is the actual MS guide title |
| `TRAILBLAZER-TEST.md` | `OurVoice-test.md` | Same |
| `TRAILBLAZER-CALIBRATION.md` | `OurVoice-calibration.md` | Same |
| `TRAILBLAZER-VOICE.md` | `OurVoice.md` | Same |
| `TRAILBLAZER-EXAMPLES.md` | `OurVoice-examples.md` | Same |
| `voice: trailblazer` (frontmatter) | `voice: ourvoice` | Reflect canonical MS term |

**Note:** "Trailblazer" remains the INTERNAL-ONLY persona name per CELA restrictions — never appears in customer-bound output. Internal docs/code references the MS canonical "Our Voice" framework. Voice tier frontmatter switches but the persona term as a CELA-protected concept stays.

---

## Total counts

- **v1 skills:** 43 (Layer 1) + 22 (Layer 3) = 65
- **v1 agents:** 15 (Layer 3) + 25 (Layer 4) = 40
- **v2 skills:** 65 (existing) + 10 (new) = 75
- **v2 agents:** 40 (existing) + 4 (new) = 44
- **Renames in v2 (skills):** 25
- **Renames in v2 (agents):** 2
- **Unchanged in v2:** 38 skills + 38 agents
- **New in v2:** 10 skills + 4 agents

---

## Phase A migration script

Phase A consumes this table to perform the rename. Migration script reads the table, for each RENAMED row:

1. Update skill's `name:` frontmatter (or agent's, respectively)
2. Add `v1_alias:` array containing the old name(s)
3. Rename directory (skills only — `scaffolding/<layer>/skills/<old>/` → `scaffolding/<layer>/skills/<new>/`)
4. Update inter-skill references (`See also` blocks)
5. Update content docs that reference old names (HARD-RULES.md, ON-DEMAND-RULES.md, etc.)

Plus directory rename: `scaffolding/02-compliance/` → `scaffolding/02-sdl/`

Plus voice-doc renames: `TRAILBLAZER-*.md` → `OurVoice-*.md` (5 files in `scaffolding/03-personal-advanced/voice/`).

The migration is mechanical but extensive. ~6h CC time when executed cleanly.
