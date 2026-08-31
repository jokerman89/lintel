# Lintel v3 — plan (revised)

**Datum:** 2026-05-27
**Föregående:** [lintel-v2-design.md](lintel-v2-design.md) (v2 spec-complete)
**Status:** PLAN — approved by operator 2026-05-27. Execution started on `v3-dev` branch.
**Författare:** Claude Code (Opus 4.7) på begäran av jokerman89 (MS Sweden CAIP-SE).

> Den första v3-planen rekommenderade MCP-server + per-CLI compile. Den var överarbetad. Operatör pekade på [obra/superpowers](https://github.com/obra/superpowers) som visar att varje modern AI-CLI redan har plugin/extension-system inbyggt — vi behöver bara små per-CLI manifest-filer som pekar på samma `skills/`-katalog. Denna version reflekterar det.

---

## TL;DR

v3 = **Lintel som komplett session-harness** för MS Sweden CAIP-SE — inte bara en skill-katalog.

Tre arkitektoniska beslut som driver allt:

1. **Plugin-manifest-pattern.** Skills och agents skrivs en gång i `skills/` och `agents/`. Varje CLI har en pytteliten plugin-manifest (`.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, `.cursor-plugin/plugin.json`, etc.) som pekar på samma katalog. Inget MCP, ingen compile, ingen runtime. Varje CLI:s native plugin-system hanterar discovery + invocation native.

2. **Bygg ut, inte trimma.** v2:s 44 agents → v3:s ~60-70, organiserade per domän (`agents/ms-specific/`, `agents/engineering/`, `agents/security/`, etc.). v2:s 74 skills → konsoliderade där dubbletter finns (~60), inte radikalt trimmade.

3. **Session-harness är Lintel:s identitet.** Inte en skill-leverantör — en komplett harness som hanterar hela sessionens livscykel: session-start ritual → mid-session interventions (hooks, voice gates, compliance) → end-of-session capture (lessons, ADR, evolution-log) → cross-session continuity (memory, lessons-sync). Repo-scaffolding för andra projekt är en del av detta.

**Resultat:** En operatör som arbetar i Claude Code, Codex, Cursor, Gemini, OpenCode, Copilot CLI eller Factory Droid får samma Lintel-upplevelse via varje CLI:s native plugin-marketplace. Och varje nytt MS-engagement-repo får komplett scaffolding (CORE-PRINCIPLES, lessons.md, ADR-templates, EVOLUTION-LOG) via `lintel scaffold init`.

---

## 1. Premiss — varför vi gör om

### 1.1 v2:s fynd från /devex-review

Återanvänds från första v3-planen:

| Område | v2 status | v3 åtgärd |
|---|---|---|
| 25 Layer-4 agents | "Bloat — gstack-duplikat" — felaktig framing | KEEP + organisera per domän + bygg ut |
| 11 top-level .md i root | För många | Flytta 5 design-docs till `.claude/engineering/design-archive/` |
| 3 v2 "engines" utan runtime | Spec utan implementation | Antingen verklig runtime via plugin (där tillämpligt) eller `STATUS: SPEC ONLY`-banner |
| Multi-CLI claim | Claude-first, andra ~25-30% | Plugin-manifest per CLI ger ~80-100% per modern CLI |
| Voice corpus | NOT_CALIBRATED | Operator-driven calibration i Phase 8 |
| README out-of-sync | Säger "intentionally minimal" trots 11 root .md | Honest rewrite |
| Saknar CODEOWNERS/CONTRIBUTING/SECURITY | Repo-standards saknas | Lägg till |
| Inget outcome-tracking | Vet inte vilka skills som används | Telemetri-skill (opt-in) |

### 1.2 Mina två fel i första v3-planen

**Fel #1: MCP-server som kärnan.** Övertekniskt. Lintel:s skill-bodies är statisk markdown — en runtime-server tillför inget. Plugin-manifest räcker.

**Fel #2: "Trim 25 Layer-4 agents → docs/USE-TASK-TOOL.md".** Felaktig framing — agenterna är Lintel-kurerat värde, inte gstack-duplikat. v3 BYGGER UT agenterna istället, organiserade per domän.

**Fel #3: Glömde att scaffolding/01-foundation/ är templates, inte skills.** CORE-PRINCIPLES, EVOLUTION-LOG, tasks/lessons.md, ADR-mallar — de kopieras IN i andra repos via `install.sh`. Måste bevaras + moderniseras.

Operatör korrigerade alla tre i sessionen. v3-planen reflekterar nu rätt arkitektur.

---

## 2. Tesen — session-harness, inte skill-katalog

### 2.1 Vad är en "session-harness"?

Lintel är inte ett skill-bibliotek man råkar invokera. Lintel är **harness-en runt agentens session** — den fil-strukturen, dokumentationen och de mekanismerna som tillsammans formar HUR agenten beter sig, från första prompt till sista commit.

**Sessionens livscykel som Lintel hanterar:**

```
SESSION START
├─ Personas review (tasks/personas.md)
├─ Compliance check (5 always-on hard rules)
├─ Memory load (tasks/memory.md)
├─ ADR scan (docs/adr/)
├─ Lessons review (tasks/lessons.md)
├─ Agent precedence resolution (~/.claude/agents/ vs repo-local)
└─ Voice tier set (internal | trailblazer | mixed)

MID-SESSION (continuous)
├─ Hook enforcement (15 hooks: customer-data-block, secret-scan-block, etc.)
├─ Skill invocation (60+ skills via plugin-system)
├─ Subagent spawning (60-70 agents via plugin-system)
├─ Compliance gates (RAIS, OneCS, AGT, voice-check, brand-conformance)
├─ Auto-mode boundary checks
└─ Pause-report at decision points

SESSION END
├─ Lessons capture (corrections → tasks/lessons.md)
├─ ADR drafting (non-trivial decisions → docs/adr/)
├─ EVOLUTION-LOG append (CLAUDE.md changes)
├─ Memory commit (durable state → tasks/memory.md)
└─ Todo handoff (tasks/todo.md updated)

CROSS-SESSION (persistent)
├─ Memory persistence (across sessions in same repo)
├─ Lessons sync (across repos via li-lessons-sync, opt-in)
├─ Brand/voice corpus sync (~/.lintel/brand/, ~/.lintel/voice/)
└─ Cross-machine state (gstack-brain pattern)
```

Varje fas har Lintel-komponenter som styr beteendet. **Det är därför v3 inte är "bara skills".**

### 2.2 Vad det betyder för v3-design

- **Skills + agents** = mid-session toolkit (Kategori A)
- **Scaffolding-templates** = repo-init + start-of-session-baseline (Kategori B)
- **Hooks** = mid-session enforcement (Kategori A)
- **Voice corpus, compliance docs, ADR-mallar** = referensmaterial harness:en konsulterar
- **bin/ scripts** (li-scaffold, li-lessons-sync, li-doctor) = operator-side utilities som binder samman

Vi designar för hela livscykeln, inte bara `/qa`-kommandot.

### 2.3 Per-CLI native equivalence (re-verifierad mot superpowers)

| CLI | Plugin-mekanism | Installer-kommando | Status |
|---|---|---|---|
| Claude Code | `.claude-plugin/plugin.json` + marketplace.json | `/plugin install lintel@li-marketplace` | ✓ native via Anthropic marketplace |
| Codex CLI | `.codex-plugin/plugin.json` med `interface{}` block | `/plugins` search + install | ✓ native via OpenAI marketplace |
| Codex App | Samma plugin.json | sidebar → Plugins → `+` | ✓ native |
| Cursor | `.cursor-plugin/plugin.json` med skills+agents+commands+hooks | `/add-plugin lintel` | ✓ native via Cursor marketplace |
| Gemini CLI | `gemini-extension.json` + GEMINI.md | `gemini extensions install <repo-url>` | ✓ native via Gemini extensions |
| OpenCode | `.opencode/INSTALL.md` + `.opencode/plugins/` | Fetch INSTALL.md instructions | ✓ native, dokumenterad workflow |
| Copilot CLI | `copilot plugin marketplace add` + `install` | `copilot plugin install` | ✓ native (verified by superpowers) |
| Factory Droid | `droid plugin marketplace add` + `install` | `droid plugin install` | ✓ native |
| Cline | VSCode extension settings | Custom Instructions | ~ degraded (no native plugin API yet) |
| Continue | `config.json` customCommands | Manual setup | ~ degraded |
| Aider | `.aider.conf.yml` | Manual setup | ~ degraded (single-agent, no subagents) |

**8 CLIs full-native via plugin-marketplaces, 3 degraded.** Det är vad "multi-CLI" faktiskt betyder.

---

## 3. Arkitektur — v3 repo-struktur

### 3.1 Två kategorier

**Kategori A — Agent-invokable** (vad CLI:n ser via plugin-manifest):
- `skills/` — slash-kommandon
- `agents/` — subagent-roller, organiserade per domän
- `hooks/` — pre/post-hooks

**Kategori B — Repo-scaffolding** (kopieras IN i andra repos):
- `scaffolding/01-foundation/` — base CLAUDE.md, CORE-PRINCIPLES, EVOLUTION, tasks/, docs/adr/
- `scaffolding/02-sdl/` — compliance referens
- `scaffolding/03-ms-team/` — MS-specifika templates (voice corpus, doc-gen templates)

### 3.2 Layoutdiagram

```
jokerman-lintel/
│
├── README.md                          ← honest v3-sync
├── LICENSE
├── CHANGELOG.md
├── LAYERS.md                          ← uppdaterad för 2-kategori-modell
├── AGENT-INSTRUCTIONS.md              ← canonical session-ritual (oförändrad i ande)
├── SHIP-GATE.md                       ← v3 gates
├── CODEOWNERS                         ← NEW
├── CONTRIBUTING.md                    ← NEW
├── SECURITY.md                        ← NEW
│
├── CLAUDE.md                          ← Claude Code entrypoint (points → AGENT-INSTRUCTIONS.md)
├── AGENTS.md                          ← Codex entrypoint
├── GEMINI.md                          ← Gemini entrypoint
│
├── .claude-plugin/
│   ├── plugin.json                    ← {name, version, license}
│   └── marketplace.json               ← Anthropic marketplace registration
├── .codex-plugin/
│   └── plugin.json                    ← {..., "skills": "./skills/", "interface": {...}}
├── .cursor-plugin/
│   └── plugin.json                    ← {..., skills, agents, commands, hooks}
├── .opencode/
│   ├── INSTALL.md                     ← OpenCode setup instructions
│   └── plugins/                       ← per-skill OpenCode plugin shims if needed
├── gemini-extension.json              ← Gemini extension manifest
├── .copilot-plugin/                   ← if Copilot CLI plugin format applies
│   └── plugin.json
├── .droid-plugin/                     ← Factory Droid
│   └── plugin.json
│
├── skills/                            ← Kategori A: ~60 skills, flat list
│   ├── qa/SKILL.md
│   ├── qa-only/SKILL.md
│   ├── release-ev2/SKILL.md
│   ├── release-deploy-ev2/SKILL.md
│   ├── safe-deploy-ring/SKILL.md
│   ├── rais-customer-voice-check/SKILL.md
│   ├── rais-sensitive-use/SKILL.md
│   ├── rais-impact-assessment/SKILL.md
│   ├── rais-transparency-note/SKILL.md
│   ├── onecs-check/SKILL.md
│   ├── onerai-submit-draft/SKILL.md
│   ├── dsb-submit-draft/SKILL.md
│   ├── dpia-submit-draft/SKILL.md
│   ├── agt-tier-stamp/SKILL.md
│   ├── entra-agent-id-submit-draft/SKILL.md
│   ├── first-party-check/SKILL.md
│   ├── provenance-track/SKILL.md
│   ├── caip-audit/SKILL.md
│   ├── cloudtest-eval-suite/SKILL.md
│   ├── onebranch-validate/SKILL.md
│   ├── li-eval/SKILL.md
│   ├── scaffold-engagement-demo/SKILL.md
│   ├── scaffold-internal-tool/SKILL.md
│   ├── scaffold-mvp/SKILL.md
│   ├── demo-deliverable-gen/SKILL.md
│   ├── brand-update/SKILL.md
│   ├── asset-search/SKILL.md
│   ├── generate-ppt/SKILL.md
│   ├── generate-word/SKILL.md
│   ├── generate-web/SKILL.md
│   ├── msvoice-rewrite/SKILL.md
│   ├── browse/SKILL.md
│   ├── scrape/SKILL.md
│   ├── make-pdf/SKILL.md
│   ├── setup-browser-cookies/SKILL.md
│   ├── open-managed-browser/SKILL.md
│   ├── design-review/SKILL.md
│   ├── design-consultation/SKILL.md
│   ├── design-html/SKILL.md
│   ├── design-shotgun/SKILL.md
│   ├── devex-review/SKILL.md
│   ├── plan-ceo-review/SKILL.md
│   ├── plan-eng-review/SKILL.md
│   ├── plan-design-review/SKILL.md
│   ├── plan-devex-review/SKILL.md
│   ├── plan-tune/SKILL.md
│   ├── autoplan/SKILL.md
│   ├── office-hours/SKILL.md
│   ├── investigate/SKILL.md
│   ├── codex/SKILL.md
│   ├── careful/SKILL.md
│   ├── review/SKILL.md
│   ├── perfbench/SKILL.md
│   ├── learn/SKILL.md
│   ├── retro/SKILL.md
│   ├── pair-agent/SKILL.md
│   ├── skillify/SKILL.md
│   ├── document-generate/SKILL.md
│   ├── context-save/SKILL.md
│   ├── context-restore/SKILL.md
│   ├── context-budget/SKILL.md
│   ├── context-warmup/SKILL.md
│   ├── perf-mode/SKILL.md
│   ├── help/SKILL.md
│   ├── health/SKILL.md
│   ├── clean/SKILL.md
│   ├── code-freeze/SKILL.md
│   ├── code-unfreeze/SKILL.md
│   ├── setup-ev2-targets/SKILL.md
│   ├── setup-brain/SKILL.md
│   ├── sync-brain/SKILL.md
│   ├── landing-report/SKILL.md
│   │
│   │  # NEW v3 session-harness skills:
│   ├── lessons-promote/SKILL.md       ← NEW: promote repo lesson → Lintel global
│   ├── adr-new/SKILL.md               ← NEW: bootstrap ADR from template
│   ├── personas-rotate/SKILL.md       ← NEW: load persona context
│   ├── match/SKILL.md                 ← NEW: semantic skill router
│   ├── li-doctor/SKILL.md         ← NEW: cross-CLI health check
│   └── li-scaffold/SKILL.md       ← NEW: invoke repo scaffolding
│
├── agents/                            ← Kategori A: ~60-70 agents, organized per domain
│   ├── ms-specific/                   ← MS-team-specifika
│   │   ├── OneCSAuditor.md
│   │   ├── RAIReviewer.md
│   │   ├── CAIPEngagementCoach.md
│   │   ├── FirstPartyMigrator.md
│   │   ├── CloudTestSuiteAuthor.md
│   │   ├── ProvenanceVerifier.md
│   │   ├── CustomerEmpathyCheck.md
│   │   ├── DemoNarrativeArc.md
│   │   ├── NordicSwedishCopyCheck.md
│   │   ├── PrivacyBoundaryAudit.md
│   │   ├── HybridScenarioArchitect.md
│   │   ├── FieldCTOAdvisor.md
│   │   ├── AIStartupAdvisor.md
│   │   ├── PostDemoFollowup.md
│   │   │
│   │   │  # NEW v3:
│   │   ├── AzureArchitect.md          ← NEW
│   │   ├── AzureOpenAIAdvisor.md      ← NEW
│   │   ├── M365CopilotAdvisor.md      ← NEW
│   │   ├── GraphAPIAdvisor.md         ← NEW
│   │   ├── BicepReviewer.md           ← NEW
│   │   ├── ARMTemplateReviewer.md     ← NEW
│   │   └── KeyVaultAuditor.md         ← NEW
│   │
│   ├── voice/                         ← Voice tier
│   │   └── TrailblazerVoiceCritic.md
│   │
│   ├── doc-gen/                       ← doc generation
│   │   ├── PPTNarrativeArchitect.md
│   │   ├── WordTechnicalEditor.md
│   │   └── WebExperienceCritic.md
│   │
│   ├── engineering/                   ← Layer 4-equivalent — KEEP, build out
│   │   ├── CodeReviewer.md
│   │   ├── ReadOnly.md
│   │   ├── SanityChecker.md
│   │   ├── TestRunner.md
│   │   ├── Architect.md
│   │   ├── Refactorer.md
│   │   ├── Migrator.md
│   │   ├── APIDesigner.md
│   │   ├── DatabaseDesigner.md
│   │   ├── DocWriter.md
│   │   ├── ADRDrafter.md
│   │   ├── ChangelogMaintainer.md
│   │   ├── DebugForensics.md
│   │   ├── Planner.md
│   │   ├── Explorer.md
│   │   ├── ResearchSynthesizer.md
│   │   ├── ReleaseEngineer.md
│   │   ├── BackendArchitect.md
│   │   ├── FrontendBuilder.md
│   │   ├── DevOpsToolchain.md
│   │   ├── DataPipelineDesigner.md
│   │   ├── ContextBudgetAdvisor.md
│   │   │
│   │   │  # NEW v3:
│   │   ├── LatencyAnalyzer.md         ← NEW
│   │   ├── CostAnalyzer.md            ← NEW
│   │   └── RegressionDetective.md     ← NEW
│   │
│   ├── security/                      ← NEW v3 domain
│   │   ├── SecurityAuditor.md         ← moved from engineering/
│   │   ├── DependencyAuditor.md       ← moved
│   │   │
│   │   │  # NEW v3:
│   │   ├── ThreatModelDrafter.md      ← NEW
│   │   ├── SecretsScanReviewer.md     ← NEW
│   │   ├── SBOMAuditor.md             ← NEW
│   │   ├── OAuthFlowReviewer.md       ← NEW
│   │   └── JWTSecurityReviewer.md     ← NEW
│   │
│   ├── compliance/                    ← NEW v3 domain
│   │   │  # NEW v3:
│   │   ├── GDPRReviewer.md            ← NEW
│   │   ├── SDLReviewer.md             ← NEW
│   │   ├── AGTReviewer.md             ← NEW
│   │   ├── EUAIActReviewer.md         ← NEW
│   │   └── SOC2Reviewer.md            ← NEW
│   │
│   ├── devops/                        ← NEW v3 domain
│   │   ├── PerformanceAnalyzer.md     ← moved from engineering/
│   │   │
│   │   │  # NEW v3:
│   │   ├── OneBranchReviewer.md       ← NEW
│   │   ├── EV2PipelineAuditor.md      ← NEW
│   │   ├── GHActionsReviewer.md       ← NEW
│   │   ├── TerraformReviewer.md       ← NEW
│   │   └── K8sManifestReviewer.md     ← NEW
│   │
│   ├── customer/                      ← NEW v3 domain
│   │   │  # NEW v3:
│   │   ├── ProposalDrafter.md         ← NEW
│   │   ├── RFPResponseDrafter.md      ← NEW
│   │   ├── ExecutiveBriefingDrafter.md ← NEW
│   │   ├── WorkshopFacilitator.md     ← NEW
│   │   └── DemoNarratorJunior.md      ← NEW
│   │
│   └── communication/                 ← NEW v3 domain
│       │  # NEW v3:
│       ├── BlogPostDrafter.md         ← NEW
│       ├── LinkedInPostDrafter.md     ← NEW
│       ├── EmailCustomerDrafter.md    ← NEW
│       └── SlideNarrationCritic.md    ← NEW
│
├── hooks/                             ← Kategori A: 15 hooks + nya
│   ├── shared/                        ← markdown HOOK.md specs (CLI-agnostic)
│   │   ├── customer-data-block/
│   │   ├── secret-scan-block/
│   │   ├── no-customer-data-in-message/
│   │   └── ... (15 idag)
│   ├── claude-code/                   ← Claude Code settings.json snippets
│   ├── cursor/                        ← Cursor hooks-cursor.json
│   └── runtime/                       ← shared bash hook-implementations
│
├── scaffolding/                       ← Kategori B: copied INTO other repos
│   ├── 01-foundation/                 ← base scaffolding template
│   │   ├── CLAUDE.md.template
│   │   ├── CORE-PRINCIPLES.md
│   │   ├── EVOLUTION.md
│   │   ├── EVOLUTION-LOG.md
│   │   ├── tasks/
│   │   │   ├── lessons.md             ← seeded with template lessons
│   │   │   ├── memory.md
│   │   │   ├── personas.md
│   │   │   └── todo.md
│   │   ├── docs/
│   │   │   ├── adr/
│   │   │   │   ├── README.md
│   │   │   │   └── TEMPLATE.md
│   │   │   └── personas/
│   │   │       └── EXAMPLE.md
│   │   ├── .claude/
│   │   │   ├── agents/                ← per-repo subagent overrides
│   │   │   └── SUBAGENT-GUIDE.md
│   │   ├── TEMPLATE-skill.md
│   │   └── TEMPLATE-agent.md
│   │
│   ├── 02-sdl/                        ← SDL/compliance reference for target repo
│   │   ├── HARD-RULES.md
│   │   ├── ON-DEMAND-RULES.md
│   │   ├── REFERENCE-RULES.md
│   │   ├── DATA-CLASSES.md
│   │   ├── LICENSE-TIERS.md
│   │   ├── AGT-OVERVIEW.md
│   │   └── COMPLIANCE-OVERVIEW.md
│   │
│   └── 03-ms-team/                    ← MS team templates
│       ├── voice/
│       │   ├── OurVoice-corpus.md     ← 60-paragraph calibration corpus
│       │   ├── OurVoice-test.md       ← eval rubric
│       │   ├── OurVoice-calibration.md
│       │   ├── OurVoice-techniques.md
│       │   ├── OurVoice-tier-guidelines.md
│       │   └── OurVoice-mode-guidelines.md
│       └── doc-gen/
│           └── default-templates/
│               ├── default-ppt-template.json
│               ├── default-word-template.json
│               └── default-web-template.html
│
├── install/
│   ├── install.sh                     ← installs plugin + copies scaffolding to ~/.lintel/
│   ├── install.ps1                    ← PowerShell variant
│   ├── verify.sh                      ← extended for v3 plugin-manifest checks
│   └── upstream-sources.yaml
│
├── bin/                               ← operator-side utilities
│   ├── li-scaffold                ← copy scaffolding/01-foundation/ → target repo
│   ├── li-lessons-sync            ← cross-repo lessons sync (gstack-brain-style)
│   ├── li-lessons-promote         ← promote repo lesson → global Lintel
│   ├── li-doctor                  ← cross-CLI health check
│   ├── li-update                  ← update plugin from latest tag
│   └── li-adr-new                 ← bootstrap ADR
│
├── docs/
│   ├── getting-started.md
│   ├── multi-cli.md                   ← honest per-CLI table
│   ├── compliance.md
│   ├── precedence.md
│   ├── power-user.md
│   ├── promoted-agents.md
│   ├── faq.md
│   ├── session-harness.md             ← NEW: explains lifecycle framing
│   ├── per-cli/                       ← NEW: per-CLI install guides
│   │   ├── claude-code.md
│   │   ├── codex.md
│   │   ├── cursor.md
│   │   ├── gemini.md
│   │   ├── opencode.md
│   │   ├── copilot-cli.md
│   │   └── droid.md
│   ├── agents/                        ← NEW: category index
│   │   ├── README.md
│   │   ├── ms-specific.md
│   │   ├── engineering.md
│   │   ├── security.md
│   │   ├── compliance.md
│   │   ├── devops.md
│   │   ├── customer.md
│   │   ├── communication.md
│   │   ├── voice.md
│   │   └── doc-gen.md
│   └── design/
│       ├── li-v2-design.md        ← historical
│       ├── li-v3-plan.md          ← THIS FILE
│       ├── MIGRATION-TABLE-v2.md      ← moved from root
│       ├── CONTEXT-ENGINE.md          ← moved from root + STATUS marker
│       ├── BRAND-INTEGRATION.md       ← moved from root
│       ├── T0-CALIBRATION-WORKFLOW.md ← moved from root
│       └── UPSTREAM-SIMILARITY.md     ← moved from root
│
├── tests/
│   ├── README.md
│   ├── unit/
│   │   ├── phase-a-naming-migration.sh
│   │   ├── plugin-manifests-valid.sh  ← NEW
│   │   ├── scaffolding-copy.sh        ← NEW
│   │   └── agents-categorized.sh      ← NEW
│   ├── integration/
│   │   ├── li-scaffold-init.sh    ← NEW
│   │   └── lessons-sync.sh            ← NEW
│   ├── e2e/
│   │   ├── claude-code-headless.sh
│   │   ├── codex-headless.sh          ← NEW
│   │   ├── cursor-smoke.md            ← NEW (manual)
│   │   └── gemini-smoke.md            ← NEW (manual)
│   ├── fixtures/
│   ├── runner/
│   └── conventions/
│
└── .github/
    ├── workflows/ci.yml               ← extended for v3
    ├── ISSUE_TEMPLATE/
    └── PULL_REQUEST_TEMPLATE.md
```

### 3.3 Plugin-manifest-exempel

**`.claude-plugin/plugin.json`:**
```json
{
  "name": "lintel",
  "description": "MS-CAIP-SE session harness — skills, agents, hooks, compliance",
  "version": "3.0.0",
  "author": {
    "name": "jokerman89",
    "email": "johannes.akerman@gmail.com"
  },
  "homepage": "https://github.com/jokerman89/jokerman-lintel",
  "repository": "https://github.com/jokerman89/jokerman-lintel",
  "license": "MIT",
  "keywords": ["microsoft", "caip", "compliance", "rais", "trailblazer-voice", "session-harness"]
}
```

**`.codex-plugin/plugin.json`:**
```json
{
  "name": "lintel",
  "version": "3.0.0",
  "description": "MS-CAIP-SE session harness for OpenAI Codex",
  "homepage": "https://github.com/jokerman89/jokerman-lintel",
  "repository": "https://github.com/jokerman89/jokerman-lintel",
  "license": "MIT",
  "skills": "./skills/",
  "interface": {
    "displayName": "Lintel",
    "shortDescription": "MS-CAIP-SE session harness — RAIS, OneCS, Trailblazer voice",
    "longDescription": "Lintel är en session-harness för Microsoft Sweden CAIP solution engineers. Inkluderar RAIS-gates, OneCS-checks, Trailblazer voice rubric, doc-gen för PPT/Word/Web, och repo-scaffolding för nya engagements.",
    "developerName": "jokerman89",
    "category": "Coding",
    "capabilities": ["Interactive", "Read", "Write"],
    "defaultPrompt": [
      "Hjälp mig med ett nytt customer engagement.",
      "Kör /qa på min branch."
    ],
    "brandColor": "#0078D4"
  }
}
```

**`.cursor-plugin/plugin.json`:**
```json
{
  "name": "lintel",
  "displayName": "Lintel",
  "description": "MS-CAIP-SE session harness",
  "version": "3.0.0",
  "license": "MIT",
  "skills": "./skills/",
  "agents": "./agents/",
  "hooks": "./hooks/cursor/hooks-cursor.json"
}
```

**`gemini-extension.json`:**
```json
{
  "name": "lintel",
  "description": "MS-CAIP-SE session harness for Gemini",
  "version": "3.0.0",
  "contextFileName": "GEMINI.md"
}
```

Tiny per-CLI manifests, all pointing at the same content. **Det är hela "multi-CLI"-mekanismen.**

---

## 4. Agent build-out — vad det betyder

### 4.1 Agentökning per domän

| Domän | v2 (idag) | v3 (mål) | Nya |
|---|---|---|---|
| ms-specific | 14 | 21 | +7 (Azure*, M365Copilot, GraphAPI, Bicep, ARM, KeyVault) |
| voice | 1 | 1 | 0 |
| doc-gen | 3 | 3 | 0 |
| engineering | 22 | 25 | +3 (LatencyAnalyzer, CostAnalyzer, RegressionDetective) |
| security | 2 (utspridda) | 7 | +5 (Threat, Secrets, SBOM, OAuth, JWT) |
| compliance | 0 | 5 | +5 (GDPR, SDL, AGT, EUAIAct, SOC2) |
| devops | 1 | 6 | +5 (OneBranch, EV2, GHActions, Terraform, K8s) |
| customer | 0 | 5 | +5 (Proposal, RFP, ExecBriefing, Workshop, DemoNarrator) |
| communication | 0 | 4 | +4 (BlogPost, LinkedIn, EmailCustomer, SlideNarration) |
| **Total** | **44** | **77** | **+33** |

**77 agents** låter mycket. Filtrera till de operatör faktiskt vill ha — minst 20 av de 33 förslagen behövs konkret för dagligt MS-CAIP-arbete.

### 4.2 Agent frontmatter v3

```yaml
---
name: AzureArchitect
description: Designs Azure-native architectures with cost + security awareness from MS Well-Architected Framework
color: blue
tools: [Read, Bash, Grep, Glob]
voice: internal
category: ms-specific            # NEW v3 — for plugin discovery
cli_compat:
  claude-code: full
  codex: full
  cursor: full
  gemini: full
tier: permissive
depends_on: []                   # for skill dependency graph
---
```

Categorin används av plugin-manifests för att exponera per-domän subagent-listor i CLI:n.

---

## 5. Session-harness mekanismer (Kategori B + cross-cutting)

### 5.1 Repo-scaffolding (Kategori B)

`bin/li-scaffold init` kopierar `scaffolding/01-foundation/` → target repo:
- `CLAUDE.md` (renderad från template med repo-specifik metadata)
- `CORE-PRINCIPLES.md`
- `EVOLUTION.md`, `EVOLUTION-LOG.md`
- `tasks/{lessons,memory,personas,todo}.md` (seeded med template-content)
- `docs/adr/{README,TEMPLATE}.md`
- `.claude/agents/` (för per-repo overrides)
- `TEMPLATE-skill.md`, `TEMPLATE-agent.md`

Plus interactive prompts:
- Repo-typ (customer-engagement / internal-tool / mvp)
- MS-team
- Voice tier default (internal / trailblazer / mixed)
- Compliance level (full SDL / standard / minimal)

Resultat: ny repo har sane defaults inom 30 sekunder.

### 5.2 Lessons mekanism

**Tre nivåer:**

1. **Per-repo `tasks/lessons.md`** — lessons från corrections i det specifika repot. Reviewas vid session-start.

2. **Cross-repo sync via `li-lessons-sync`** — opt-in. Lessons från Repo A sync:as till `~/.lintel/lessons/<repo-slug>.md` så Repo B kan referera. Gstack-brain-style — privat per operatör.

3. **Global Lintel lessons via `li-lessons-promote`** — när en lesson är generell (inte repo-specific), promote till Lintel global. Hamnar i `scaffolding/01-foundation/tasks/lessons.md` så alla framtida scaffolded repos får den som baseline.

**Mid-session lessons-review skill:** `/lessons` slash-command laddar relevanta lessons (filtrerade på keywords från current task) som kontext.

### 5.3 ADR mekanism

`/adr-new` skill:
- Frågar context-frågor (decision title, alternatives considered, decision, consequences)
- Genererar `docs/adr/NNNN-<slug>.md` från template
- Auto-commit på feature branch
- Notification att include i nästa PR

`ADRDrafter` agent: subagent som spawnas när non-trivial decision detekteras mid-session.

### 5.4 EVOLUTION-LOG mekanism

Hook: när CLAUDE.md modifieras → auto-append entry i EVOLUTION-LOG.md med commit-info, datum, rationale. Operatör kan disabla per-repo.

### 5.5 Persona mekanism

`/personas-rotate` skill: laddar persona-context från `tasks/personas.md` för demo-prep eller workshop-facilitation. Persona-data ärvs av subagents om de spawnas under sessionen.

### 5.6 Memory mekanism

`tasks/memory.md` är durable cross-session storage per repo. Strukturerad med typer (user / feedback / project / reference) — samma format som Claude Code's built-in memory.

`/context-save` skill skriver, `/context-restore` läser. Plus auto-update vid relevanta corrections.

### 5.7 Voice corpus mekanism

`scaffolding/03-ms-team/voice/OurVoice-corpus.md` finns kvar (60 paragraphs, 12 cells). Calibration via `/li:eval`. När calibrated, `/rais-customer-voice-check` skill använder den som referens.

### 5.8 Compliance mekanism

5+7+8 tiering oförändrad. `scaffolding/02-sdl/` innehåller HARD-RULES, ON-DEMAND-RULES, REFERENCE-RULES. Hooks i `hooks/shared/` enforcear hard-rules. On-demand-skills (`/rais-*`, `/onecs-check`, `/agt-tier-stamp`) invokeras av operator vid behov.

---

## 6. Per-CLI deep-dive

### 6.1 Claude Code

**Plugin install:**
```bash
/plugin marketplace add jokerman89/jokerman-lintel
/plugin install lintel@jokerman-lintel
```

**Vad operatör får:**
- Alla skills som slash-commands (`/qa`, `/release-ev2`, etc.)
- Alla agents tillgängliga via Task tool
- Hooks installade via settings.json (operatör opt-in per hook)
- AGENT-INSTRUCTIONS som CLAUDE.md context

### 6.2 Codex CLI

**Plugin install:**
```bash
codex
> /plugins
> search lintel
> Install Plugin
```

**Vad operatör får:**
- Skills synliga som Codex-commands
- AGENTS.md som context-fil
- Subagents via `codex exec` subprocess-spawning (Codex Cloud)

### 6.3 Cursor

**Plugin install:**
```
In Cursor Agent chat:
/add-plugin lintel
```

**Vad operatör får:**
- Skills som agent-requested rules
- Subagents via Background Agents
- Hooks via hooks-cursor.json (om Cursor stödjer det)

### 6.4 Gemini CLI

**Extension install:**
```bash
gemini extensions install https://github.com/jokerman89/jokerman-lintel
```

**Vad operatör får:**
- GEMINI.md som context
- Skills som Gemini agent rules

### 6.5 OpenCode

**Install:**
```
Fetch and follow instructions from https://raw.githubusercontent.com/jokerman89/jokerman-lintel/main/.opencode/INSTALL.md
```

### 6.6 GitHub Copilot CLI

**Plugin install:**
```bash
copilot plugin marketplace add jokerman89/jokerman-lintel
copilot plugin install lintel@jokerman-lintel
```

### 6.7 Factory Droid

**Plugin install:**
```bash
droid plugin marketplace add https://github.com/jokerman89/jokerman-lintel
droid plugin install lintel@lintel
```

---

## 7. Migration v2 → v3

### 7.1 Branch-strategi

- Behåll `main` på v2.0.x
- `v3-dev` branch för all v3-utveckling
- Merge → `main` vid v3.0.0-tag
- v1-aliases retas i v3.5

### 7.2 Skill/agent-migration

**Mass-move (`git mv` preserves history):**

```bash
# Skills: scaffolding/01-foundation/skills/* + scaffolding/03-personal-advanced/skills/* → skills/
git mv scaffolding/01-foundation/skills/* skills/
git mv scaffolding/03-personal-advanced/skills/* skills/

# Agents: scaffolding/03-personal-advanced/agents/* → agents/<category>/
# + scaffolding/04-power-user/agents/* → agents/<category>/
# Categorization done by operator-driven script that reads agent frontmatter
```

**Scaffolding/04-power-user/ → agents/engineering/** (inte borttagen, omorganiserad).

**Compliance:** `scaffolding/02-sdl/` BEVARAS — det är templates för andra repos. Hooks separeras: `scaffolding/02-sdl/hooks/` → `hooks/shared/`, scaffolding-versionen är referens.

### 7.3 Frontmatter-update

Per skill + agent, lägg till:
- `category: <domain>` (för agents)
- `cli_compat: {claude-code: full, codex: full, ...}` (ersätter v2 cli_support array)
- `depends_on: []` (för dependency graph)

Bulk-script via sed (`bin/li-migrate-v2-to-v3` engångsskript).

### 7.4 Backward-compat

- `v1_alias` fields preserves
- `scaffolding/01-foundation/skills/` symlink → `skills/` (för operatörer som har vant sig vid v2-paths)
- `verify.sh --legacy-paths` validerar att alla v2-references fortfarande resolverar

---

## 8. Fas-uppdelning (executable)

### Phase 0 — Audit + branch + research (1 dag)

- [ ] `bash install/verify.sh --all` grön
- [ ] `bash tests/runner/run-all.sh` grön
- [ ] Create `v3-dev` branch
- [ ] Commit denna plan på branch
- [ ] **Research per-CLI plugin format** — verifiera mot superpowers + senaste docs för varje CLI:
  - Claude Code marketplace requirements
  - Codex plugin.json schema (`interface{}` block details)
  - Cursor plugin.json full schema
  - Gemini extensions format
  - OpenCode INSTALL.md pattern
  - Copilot CLI plugin format
  - Factory Droid plugin format
- [ ] Document findings i `.claude/engineering/design-archive/PLUGIN-FORMAT-RESEARCH.md`

### Phase 1 — Organize + flatten (2 dagar)

- [ ] `git mv` skills från `scaffolding/*/skills/` → `skills/`
- [ ] `git mv` agents från `scaffolding/03-personal-advanced/agents/` → `agents/<category>/`
- [ ] `git mv` agents från `scaffolding/04-power-user/agents/` → `agents/<category>/`
- [ ] Add `category: <domain>` frontmatter to each agent (bulk sed)
- [ ] Add `layer: <foundation|sdl|ms-team>` frontmatter to each skill
- [ ] Keep `scaffolding/02-sdl/` BEVARAD som compliance-template
- [ ] Hooks: `scaffolding/02-sdl/hooks/` → `hooks/shared/`, behåll symlinks i scaffolding/
- [ ] Move 5 design-docs root → `.claude/engineering/design-archive/`
- [ ] `verify.sh` grön efter omorganisation
- [ ] Commit per logisk grupp

### Phase 2 — Plugin manifests (2 dagar)

- [ ] `.claude-plugin/plugin.json` + marketplace.json
- [ ] `.codex-plugin/plugin.json` med `interface{}` block
- [ ] `.cursor-plugin/plugin.json`
- [ ] `.opencode/INSTALL.md` + `.opencode/plugins/`
- [ ] `gemini-extension.json` + `GEMINI.md`
- [ ] `.copilot-plugin/plugin.json`
- [ ] `.droid-plugin/plugin.json`
- [ ] Per-CLI entrypoint context files (`CLAUDE.md`, `AGENTS.md`, `GEMINI.md`) — länkar till canonical AGENT-INSTRUCTIONS.md
- [ ] `tests/unit/plugin-manifests-valid.sh` — JSON-schema validation per manifest

### Phase 3 — Build out agents (3 dagar)

- [ ] Write 33 new agent .md files (full TEMPLATE-agent.md compliance)
- [ ] Add `category` frontmatter to all
- [ ] `tier: permissive` for all new (operator IP, MIT)
- [ ] `cli_compat: {claude-code: full, codex: full, cursor: full, gemini: full}` per-CLI declaration
- [ ] Update `docs/agents/README.md` + per-category indexes

### Phase 4 — Build out new session-harness skills (2 dagar)

- [ ] `/lessons-promote` (promote repo lesson → global)
- [ ] `/adr-new` (bootstrap ADR from template)
- [ ] `/personas-rotate` (load persona context)
- [ ] `/match` (semantic skill router)
- [ ] `/li:doctor` (cross-CLI health check)
- [ ] `/li:scaffold` (invoke repo scaffolding)
- [ ] `/lessons` (mid-session lessons-review)

### Phase 5 — Bin scripts + install updates (2 dagar)

- [ ] `bin/li-scaffold` — scaffolding/01-foundation/* → target repo
- [ ] `bin/li-lessons-sync` — cross-repo lessons sync (gstack-brain-style)
- [ ] `bin/li-lessons-promote` — promote to global
- [ ] `bin/li-doctor` — health check
- [ ] `bin/li-update` — update plugin from latest tag
- [ ] `bin/li-adr-new` — bootstrap ADR
- [ ] `install/install.sh` — extended for v3 (plugin install per detected CLI + scaffolding copy)
- [ ] `install/verify.sh` — new subcommands: --plugin-manifests, --scaffolding, --agents-categorized, --lessons-mechanism

### Phase 6 — Honest docs (1 dag)

- [ ] README.md rewrite — v3 honest claims, per-CLI install table
- [ ] `docs/session-harness.md` — NEW explainer
- [ ] `docs/per-cli/*.md` — per-CLI install guides (7 filer)
- [ ] `docs/agents/*.md` — per-category indexes (8 filer)
- [ ] CHANGELOG.md — v3.0.0 entry
- [ ] LAYERS.md — 2-kategori-modellen (Agent-invokable + Repo-scaffolding)
- [ ] SHIP-GATE.md — v3 gates

### Phase 7 — Tests + CI (2 dagar)

- [ ] `tests/unit/plugin-manifests-valid.sh`
- [ ] `tests/unit/scaffolding-copy.sh`
- [ ] `tests/unit/agents-categorized.sh`
- [ ] `tests/integration/li:scaffold-init.sh`
- [ ] `tests/integration/lessons-sync.sh`
- [ ] `tests/e2e/claude-code-headless.sh`
- [ ] `tests/e2e/codex-headless.sh`
- [ ] CI matrix utökas med plugin-validate-job

### Phase 8 — Voice cal + marketplace submission (operator-driven, 2-4 dagar)

- [ ] Operator runs T0 calibration → corpus status: CALIBRATED
- [ ] Submit to Anthropic marketplace (Claude Code)
- [ ] Submit to OpenAI marketplace (Codex)
- [ ] Submit to Cursor marketplace
- [ ] Submit to Gemini extensions
- [ ] Manual smoke tests in each CLI

### Phase 9 — Ship gate v3 + tag (1 dag)

- [ ] SHIP-GATE.md grön (10 gates v3)
- [ ] CI green
- [ ] Operator final review
- [ ] `git tag v3.0.0 && git push origin v3.0.0`

**Total estimat: ~14-18 work-days.**

---

## 9. Success criteria — v3 vs v2

| Metric | v2 (idag) | v3 (mål) |
|---|---|---|
| Overall DX score | 5.8/10 | ≥8.5/10 |
| TTHW Claude Code | <5min | <5min |
| TTHW Codex CLI | ~30min | <5min (native plugin install) |
| TTHW Cursor | n/a | <5min |
| TTHW Gemini | n/a | <5min |
| TTHW Copilot CLI | n/a | <5min |
| Skill count | 74 | ~60 (konsolidering) |
| Agent count | 44 | ~70-77 (BUILD OUT) |
| Multi-CLI native | claim only | proven via plugin marketplaces |
| Per-CLI install | manual shim copy | `<cli> plugin install lintel` |
| Voice corpus | NOT_CALIBRATED | CALIBRATED |
| Session-harness framing | implicit | explicit (docs/session-harness.md) |
| Scaffolding-templates | i scaffolding/01-foundation/ | bevarade + moderniserade |
| README accuracy | 6/10 | 9/10 |
| Repo standards | saknar 3 | CODEOWNERS + CONTRIBUTING + SECURITY |

---

## 10. Risk register

| Risk | Sannolikhet | Impact | Mitigation |
|---|---|---|---|
| Per-CLI plugin format ändras post-research | Medium | Medium | Phase 0 research timestamp + per-CLI version-pinning i plugin.json |
| Marketplace-submission tar lång tid (Anthropic curated) | Hög | Låg | Submit tidigt, plugin fungerar redan via "add marketplace from repo" pattern |
| MS-internal blocker att publicera till public marketplace | Medium | Hög | Verify Phase 0 — MS legal check krävs innan public submission |
| 33 nya agents = bloat-recidiv | Medium | Medium | Filtrera till de 20 operatör verkligen vill ha innan Phase 3 |
| Plugin-manifest divergence mellan CLIs | Hög | Låg | Acceptera — varje manifest är 20-50 rader, billigt att underhålla |
| Voice corpus calibration kostar pengar | Medium | Låg | $1.80-6 per round, budget för 3-5 rounds = $5-30 |
| Scaffolding-template-drift mot live agents/skills | Medium | Medium | `verify.sh --scaffolding-coherence` checkar att template-paths fortfarande pekar rätt |

---

## 11. Vad v3 medvetet INTE gör

- ❌ MCP-server (overkill för markdown-skills)
- ❌ Per-CLI compile (plugin-manifests räcker)
- ❌ Custom UI/dashboard (telemetri = CLI-output)
- ❌ Trim agents (build out istället)
- ❌ Förstör scaffolding-templates (bevara + modernisera)
- ❌ Auto-running 1M context engine (det är mönster, inte engine)
- ❌ Lova cross-CLI parity där det fundamentalt skiljer (hooks är Claude-only)

---

## 12. Beslut redan tagna av operatör

1. ✓ Approve v3 plan (Big Bang approach på `v3-dev` branch)
2. ✓ Plugin-manifest-pattern istället för MCP+compile
3. ✓ BUILD OUT agents, inte trim
4. ✓ Bevara scaffolding-templates + modernisera
5. ✓ Session-harness framing som Lintel:s identitet
6. ✓ Kör på alla faser non-stop

---

## 13. Operatör-value gain v2 → v3

**v3 levererar utöver v2:**
- Plugin-install i 8 major CLIs via deras native marketplaces
- ~30 nya agents organiserade per domän (säkerhet, compliance, devops, customer, communication)
- Session-harness explicit som Lintel:s identitet — docs, lifecycle, mekanismer
- Scaffolding-templates moderniserade med `li-scaffold` + cross-repo lessons sync
- 6 nya session-harness skills (lessons-promote, adr-new, personas-rotate, match, li-doctor, li-scaffold)
- Honest README med per-CLI portability-table
- Repo-standards (CODEOWNERS, CONTRIBUTING, SECURITY)

**v3 levererar INTE:**
- Cross-CLI subagent parity (varje CLI har eget subagent-system)
- Cross-CLI hook-stöd (Claude-Code-only mekanism)

---

*Plan färdigställd 2026-05-27 av Claude Code (Opus 4.7).*
*Execution started immediately på `v3-dev` branch per operator-approve.*
