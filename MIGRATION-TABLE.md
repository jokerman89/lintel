# JStack v2 Migration Table

Full enumeration of all 65 skills + 40 agents in v1 with v2 rename status. Source of truth consumed by Phase A migration script.

**Naming rule:** mirror MS internal process terminology where one exists. Generic engineering vocabulary stays unchanged. Aliases retained until v2.5 (operator data-driven retirement decision).

**Reading note:** v1 names below use `<v1>token</v1>` markup to prevent global rename scripts from accidentally rewriting the v1 column. The token shows what existed in v1; the v2 column shows the canonical v2 name.

---

## Layer 1 — Foundation skills (43)

| v1 name | v2 name | Status | Rename reason |
|---------|---------|--------|---------------|
| `<v1>context-save</v1>` | `/context-save` | unchanged | Generic enough; no MS equivalent |
| `<v1>context-restore</v1>` | `/context-restore` | unchanged | Same |
| `<v1>clean</v1>` | `/clean` | unchanged | Generic |
| `<v1>help</v1>` | `/help` | unchanged | Universal |
| `<v1>health</v1>` | `/health` | unchanged | Generic |
| `<v1>plan-ceo-review</v1>` | `/plan-ceo-review` | unchanged | Already CEO-canonical |
| `<v1>plan-eng-review</v1>` | `/plan-eng-review` | unchanged | Already eng-canonical |
| `<v1>plan-design-review</v1>` | `/plan-design-review` | unchanged | Already design-canonical |
| `<v1>plan-devex-review</v1>` | `/plan-devex-review` | unchanged | Already DX-canonical |
| `<v1>plan-tune</v1>` | `/plan-tune` | unchanged | Generic |
| `<v1>ship</v1>` | `/release-ev2` | RENAMED | EV2 = Express V2 MS safe-deploy system |
| `<v1>land-and-deploy</v1>` | `/release-deploy-ev2` | RENAMED | Same EV2 anchor |
| `<v1>review</v1>` | `/review` | unchanged | Generic; pre-landing diff review |
| `<v1>autoplan</v1>` | `/autoplan` | unchanged | Orchestrator name is fine |
| `<v1>qa</v1>` | `/qa` | unchanged | Universal QA term |
| `<v1>qa-only</v1>` | `/qa-only` | unchanged | Same |
| `<v1>investigate</v1>` | `/investigate` | unchanged | Universal debug term |
| `<v1>codex</v1>` | `/codex` | unchanged | Codex CLI ref |
| `<v1>careful</v1>` | `/careful` | unchanged | Generic mode-wrapper |
| `<v1>browse</v1>` | `/browse` | unchanged | Generic browser-control |
| `<v1>scrape</v1>` | `/scrape` | unchanged | Generic |
| `<v1>make-pdf</v1>` | `/make-pdf` | unchanged | Generic |
| `<v1>setup-browser-cookies</v1>` | `/setup-browser-cookies` | unchanged | Generic |
| `<v1>open-gstack-browser</v1>` | `/open-managed-browser` | RENAMED | Drop "gstack" branding internally |
| `<v1>design-review</v1>` | `/design-review` | unchanged | Generic; visual pillar review |
| `<v1>design-consultation</v1>` | `/design-consultation` | unchanged | Generic |
| `<v1>design-html</v1>` | `/design-html` | unchanged | Generic |
| `<v1>design-shotgun</v1>` | `/design-shotgun` | unchanged | Generic |
| `<v1>devex-review</v1>` | `/devex-review` | unchanged | Generic |
| `<v1>benchmark</v1>` | `/perfbench` | RENAMED | Closer to MS perf-bench term |
| `<v1>canary</v1>` | `/safe-deploy-ring` | RENAMED | MS ring-based deploy terminology |
| `<v1>freeze</v1>` | `/code-freeze` | RENAMED | Standard MS engineering term |
| `<v1>unfreeze</v1>` | `/code-unfreeze` | RENAMED | Same |
| `<v1>setup-deploy</v1>` | `/setup-ev2-targets` | RENAMED | EV2-anchored |
| `<v1>learn</v1>` | `/learn` | unchanged | Generic |
| `<v1>office-hours</v1>` | `/office-hours` | unchanged | Generic |
| `<v1>retro</v1>` | `/retro` | unchanged | Generic |
| `<v1>pair-agent</v1>` | `/pair-agent` | unchanged | Generic |
| `<v1>skillify</v1>` | `/skillify` | unchanged | JStack-specific |
| `<v1>landing-report</v1>` | `/landing-report` | unchanged | Generic |
| `<v1>setup-gbrain</v1>` | `/setup-brain` | RENAMED | Drop gstack-brain branding |
| `<v1>sync-gbrain</v1>` | `/sync-brain` | RENAMED | Same |
| `<v1>document-generate</v1>` | `/document-generate` | unchanged | Generic; doc-gen is MS-specific in Layer 3 |

**Layer 1 changes: 10 renames / 33 unchanged (out of 43)**

---

## Layer 3 — Personal advanced (MS-specific) skills (22)

| v1 name | v2 name | Status | Rename reason |
|---------|---------|--------|---------------|
| `<v1>customer-voice-check</v1>` | `/rais-customer-voice-check` | RENAMED | RAIS = Responsible AI Standard anchor |
| `<v1>msvoice-rewrite</v1>` | `/msvoice-rewrite` | unchanged | Already MS-canonical |
| `<v1>compliance-gate</v1>` | `/onecs-check` | RENAMED | 1CS = One Compliance System |
| `<v1>first-party-check</v1>` | `/first-party-check` | unchanged | Already canonical MS term |
| `<v1>provenance-track</v1>` | `/provenance-track` | unchanged | Generic |
| `<v1>onerai-prep</v1>` | `/onerai-submit-draft` | RENAMED | OneRAI canonical; "submit-draft" makes flow explicit |
| `<v1>dsb-prep</v1>` | `/dsb-submit-draft` | RENAMED | DSB canonical |
| `<v1>dpia-prep</v1>` | `/dpia-submit-draft` | RENAMED | DPIA canonical |
| `<v1>sensitive-use-report</v1>` | `/rais-sensitive-use` | RENAMED | RAIS-anchored |
| `<v1>rai-impact-assessment</v1>` | `/rais-impact-assessment` | RENAMED | RAIS-anchored |
| `<v1>scaffold-customer-demo</v1>` | `/scaffold-engagement-demo` | RENAMED | "Engagement" is CAIP-SE canonical |
| `<v1>scaffold-internal-tool</v1>` | `/scaffold-internal-tool` | unchanged | Generic enough |
| `<v1>scaffold-mvp</v1>` | `/scaffold-mvp` | unchanged | Generic enough |
| `<v1>demo-deliverable-gen</v1>` | `/demo-deliverable-gen` | unchanged | Generic |
| `<v1>transparency-doc-gen</v1>` | `/rais-transparency-note` | RENAMED | Maps to RAIS transparency principle |
| `<v1>tier-stamp-agents</v1>` | `/agt-tier-stamp` | RENAMED | AGT = Agent Governance Framework |
| `<v1>entra-agent-id-prep</v1>` | `/entra-agent-id-submit-draft` | RENAMED | Already Entra-canonical; "submit-draft" makes flow explicit |
| `<v1>caip-audit</v1>` | `/caip-audit` | unchanged | Already CAIP-canonical |
| `<v1>context-tokenwatch</v1>` | `/context-budgetwatch` | RENAMED | Refocus on budget not raw token-count |
| `<v1>eval-suite-gen</v1>` | `/cloudtest-eval-suite` | RENAMED | CloudTest = MS scalable test infra |
| `<v1>jstack-test</v1>` | `/onebranch-validate` | RENAMED | OneBranch = governed pipeline matrix-test |
| `<v1>jstack-eval</v1>` | `/jstack-eval` | unchanged | JStack-specific |

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
| `<v1>MSComplianceAuditor</v1>` | `OneCSAuditor` | RENAMED | 1CS-anchored |
| `<v1>RAIReviewer</v1>` | `RAIReviewer` | unchanged | Already canonical |
| `<v1>TrailblazerVoiceCritic</v1>` | `TrailblazerVoiceCritic` | unchanged | Already MS-canonical (Trailblazer = internal-only persona name per CELA) |
| `<v1>CAIPEngagementCoach</v1>` | `CAIPEngagementCoach` | unchanged | Already CAIP-canonical |
| `<v1>FirstPartyMigrator</v1>` | `FirstPartyMigrator` | unchanged | Already canonical |
| `<v1>EvalSuiteAuthor</v1>` | `CloudTestSuiteAuthor` | RENAMED | CloudTest anchor |
| `<v1>ProvenanceVerifier</v1>` | `ProvenanceVerifier` | unchanged | Generic |
| `<v1>CustomerEmpathyCheck</v1>` | `CustomerEmpathyCheck` | unchanged | Domain-specific |
| `<v1>DemoNarrativeArc</v1>` | `DemoNarrativeArc` | unchanged | Domain-specific |
| `<v1>NordicSwedishCopyCheck</v1>` | `NordicSwedishCopyCheck` | unchanged | Domain-specific |
| `<v1>PrivacyBoundaryAudit</v1>` | `PrivacyBoundaryAudit` | unchanged | Domain-specific |
| `<v1>HybridScenarioArchitect</v1>` | `HybridScenarioArchitect` | unchanged | Domain-specific |
| `<v1>FieldCTOAdvisor</v1>` | `FieldCTOAdvisor` | unchanged | Domain-specific |
| `<v1>AIStartupAdvisor</v1>` | `AIStartupAdvisor` | unchanged | Domain-specific |
| `<v1>PostDemoFollowup</v1>` | `PostDemoFollowup` | unchanged | Domain-specific |

**Layer 3 agent changes: 2 renames / 13 unchanged (out of 15)**

---

## Agents — Layer 4 power-user (25)

All Layer 4 agents are gstack-equivalent generic engineering helpers. No MS-specific terminology mapping applies — these stay unchanged.

CodeReviewer, ReadOnly, SanityChecker, TestRunner, Architect, Refactorer, Migrator, SecurityAuditor, PerformanceAnalyzer, DependencyAuditor, APIDesigner, DatabaseDesigner, DocWriter, ADRDrafter, ChangelogMaintainer, DebugForensics, Planner, Explorer, ResearchSynthesizer, ReleaseEngineer, BackendArchitect, FrontendBuilder, DevOpsToolchain, DataPipelineDesigner, AccessibilityChecker.

**Layer 4 agent changes: 0 renames / 25 unchanged (out of 25)**

---

## New agents introduced in v2 (Phase F + Phase C)

| New agent | Phase | Purpose |
|-----------|-------|---------|
| `PPTNarrativeArchitect` | F | Designs slide arc + per-slide content goal before generation |
| `WordTechnicalEditor` | F | Reviews technical Word output for accuracy + voice + structure |
| `WebExperienceCritic` | F | Applies 6-pillar critique to generated web output |
| `ContextBudgetAdvisor` | C | Layer 4 agent that suggests phase declarations for unstructured tasks |

---

## Concept renames (architecture-level)

| v1 concept | v2 concept | Why |
|------------|------------|-----|
| "5-level agent precedence" | "AGT identity precedence" | Maps to MS AGT framework |
| "Layer 2 always-on" | "SDL always-on" | SDL = canonical MS framing |
| "Layer 2 on-demand" | "SDL on-demand" | Same |
| "Layer 2 reference docs" | "SDL reference" | Same |
| Directory `scaffolding/<v1>02-compliance</v1>/` | `scaffolding/02-sdl/` | Match SDL framing |
| `<v1>TRAILBLAZER-CORPUS.md</v1>` | `OurVoice-corpus.md` | "Our Voice" is the actual MS guide title |
| `<v1>TRAILBLAZER-TEST.md</v1>` | `OurVoice-test.md` | Same |
| `<v1>TRAILBLAZER-CALIBRATION.md</v1>` | `OurVoice-calibration.md` | Same |
| `<v1>TRAILBLAZER-VOICE.md</v1>` | `OurVoice.md` | Same |
| `<v1>TRAILBLAZER-EXAMPLES.md</v1>` | `OurVoice-examples.md` | Same |

**Note on Trailblazer persona:** The persona name "Trailblazer" remains the CELA-protected internal-only term. It never appears in customer-bound output. The `voice: trailblazer` frontmatter identifier is also retained in v2 — changing every skill's voice tier identifier would create unnecessary churn; the frontmatter value is internal-only and stays Trailblazer-anchored.

---

## Total counts

- **v1 skills:** 43 (Layer 1) + 22 (Layer 3) = 65
- **v1 agents:** 15 (Layer 3) + 25 (Layer 4) = 40
- **v2 skills:** 65 (existing) + 10 (new) = 75
- **v2 agents:** 40 (existing) + 4 (new) = 44
- **Renames in v2 (skills):** 24 (10 Layer 1 + 14 Layer 3)
- **Renames in v2 (agents):** 2
- **Unchanged in v2:** 41 skills + 38 agents
- **New in v2:** 10 skills + 4 agents

---

## Phase A status (executed 2026-05-27)

- 24 skill directories renamed via `git mv`
- 2 agent files renamed
- 5 voice docs renamed (TRAILBLAZER-* → OurVoice-*)
- Compliance directory renamed (`02-compliance/` → `02-sdl/`)
- 26 frontmatter updates: `name:` field updated + `v1_alias:` array added
- ~130 markdown files updated with new references via global sed-based replacement script
- Markup tokens `<v1>name</v1>` in this file protect the v1 column from accidental self-rewrite by the script

**Verification recommended:** run `bash install/verify.sh --counts` + `bash install/verify.sh --frontmatter` after Phase A commit to confirm no orphaned references and frontmatter still valid.
