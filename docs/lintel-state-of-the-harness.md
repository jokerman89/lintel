# Lintel — State of the Harness

> A comprehensive technical documentation of what Lintel is, how every part works, and an
> honest readiness assessment. Produced from a six-agent read-only sweep of `main @ 591925b`
> (post-v4.9). Ground truth this run: **168 skills · 65 agents tracked (+5 untracked, see §19) ·
> 30 hooks · 1 pack (`_default`) · version 4.9.0** consistent across all manifests.

---

## 0. Executive summary & readiness verdict

Lintel is a **company-neutral, pack-driven session harness for agent-based development** — markdown
and bash scaffolding that any modern AI CLI loads as a plugin. It has no runtime and no daemons; the
CLI executes, Lintel supplies the disciplines: an 8-phase development cycle, an engineering-module
fleet, opt-in compliance/workflow hooks, an identity-as-a-pluggable-pack system, and a "factory"
(`bin/li-scaffold`) that installs those same disciplines into other repos. It dogfoods itself — the
repo's own root `CLAUDE.md` is the instantiated form of the template it ships.

The engineering floor is genuinely high: a legible phase model, unified state, mechanical-first
routing with an honest LLM stub, a careful fork-free runtime, 26 structural-contract tests + 34 unit
tests, and CI green on real runners (Ubuntu + Windows). The v4.9 "five-lens" remediation closed the
dominant systemic problem the codebase had — **drift between the system and its own self-description**
(mixed-language source, a frozen shipping identity, stale self-counts, hooks that silently no-op'd).

**Readiness verdict in one line: GA-ready for Claude Code specifically; beta for the other CLIs;
hold a clean public launch until a short doc/identity punch-list is closed.** The harness is
architecturally sound and CI-guarded against regression. The remaining blockers are not structural —
they are credibility-damaging documentation/identity residue (a `getting-started.md` still written for
"a new MS Sweden CAIP SE," a maintainer email that still reads `@microsoft.com`, manifest descriptions
still branded "MS-CAIP-SE," a documented-but-absent `li-forge-stats`) plus the inherent, honestly-stated
reality that "multi-CLI" means **full on three CLIs, degraded on the rest, and hooks are Claude-Code-only**.
The full punch-list is §18.

---

## 1. What Lintel is

**Thesis** (`README.md:3`, `CLAUDE.md:18`): a company-neutral, pack-driven session harness — markdown +
bash that any AI CLI loads as a plugin. No runtime, no daemons; the CLI handles execution, Lintel
supplies the patterns + scaffolding.

It is **not** an ad-hoc skill library. It is the harness *around* an agent's whole session, shaping
behaviour from the first prompt to the last commit: a session-start ritual → mid-session interventions
(hooks, voice gates, compliance) → end-of-session capture (lessons, ADRs, an evolution log) →
cross-session continuity (memory, lessons-sync). It is also the **factory** that installs its own
disciplines into other repos via `bin/li-scaffold` — `li-scaffold init --mode internal-tool --pack
_default` produces a `CLAUDE.md`, `CORE-PRINCIPLES.md`, `tasks/`, `docs/adr/`, and `.claude/agents/`
in about thirty seconds.

Two content categories ship in the one repo (`README.md:15-25`):

- **Category A — agent-invokable** (what a CLI sees through the plugin manifest): `skills/`, `agents/`,
  `hooks/shared/`.
- **Category B — repo-scaffolding** (copied INTO other repos by `li-scaffold`): `scaffolding/01-foundation/`.

The defining architectural choice: **identity is not hardcoded**. Voice, compliance, persona, brand, and
roles are resolved at runtime from the *active pack* via a single accessor, `resolve_pack_field
<dotted.path>` (`lib/pack-resolver.sh`). The repo ships only the neutral `_default` pack, which enforces
nothing. The Microsoft CAIP-SE identity (Trailblazer voice, RAIS/OneCS/AGT/SDL compliance, EV2/OneBranch)
was extracted in v4.7 into an external pack, `lintel-caip-pack`.

---

## 2. Architecture — the four layers

The v4.0 reframe (`docs/design/lintel-v4.0-reframe-design.md`) frames the system as "one architecture,
not five features." The load-bearing model:

1. **SPINE** — the generic execution engine, neutral on content. The 8-phase cycle, the skills, the
   agents, and the hooks live here. Framing (L-004): *spine = execution engine; packs = decision layer.*
2. **PACK** — identity, loaded in at session-start (voice / compliance / persona / brand / roles /
   navigation / brief-forge policy), resolved through `lib/pack-resolver.sh`. `_default` is neutral;
   company packs install externally. Packs support `extends:` inheritance (wholesale block-replace,
   not deep-merge), versioning, and validation.
3. **NAVIGATION** — entry/exit declarations on every `workflow_root: true` skill, plus an *orientator*
   at SENSE that reads request + pack + open jobs and picks workflow / entry-phase / risk-level
   (token-budgeted, `orientator_budget_tokens` ≈ 2k, pack-overridable).
4. **ENGINEERING-DOMAIN MODULES (DEPTH)** — five first-class composable modules (TA / DA / SC / DH / TQ),
   each a `workflow_root` skill with sub-skills + agents + hooks + gates + loops and three invocation
   granularities (full / loop / single).

Two cross-cutting constructs sit across these: **Brief Forge / Envelope** (a universal hand-off gate at
every phase/subagent boundary producing a standardized HEAD/BODY/TAIL envelope; §11) and **Meta-Infra**
(infrastructure-for-infrastructure discipline — Gates M1–M4 governing structural changes to the harness
itself).

> Caveat for readers: the v4.0 design doc still carries a `DRAFT_FOR_REVIEW` status line and describes
> some pieces (parts of Brief Forge, a `/li:migrations` skill, the full module fleet) as planned. Treat
> it as design intent; this report distinguishes shipped from aspirational throughout.

---

## 3. The development cycle — 8 phases (+ SCOPE)

Orchestrated by `skills/cycle/SKILL.md` (a `workflow_root` that spawns a job). The full path is
**SENSE → SCOPE → DEFINE → DISCOVER → PLAN → BUILD → REVIEW → SHIP → CAPTURE**. Branding calls it the
"8-phase cycle"; SCOPE (added in v4.9) is numbered 1.5 — a light, skippable phase between SENSE and
DEFINE — so the pipeline is really nine phases. Each phase is its own skill writing
`.lintel/state/00-state.md`, and each declares a machine-checkable `gap_if_skipped`.

| Phase | Purpose | Produces | Cost of skipping (`gap_if_skipped`, condensed) |
|---|---|---|---|
| **SENSE** | One-screen silent diagnostic: intent, pack compliance mode, active role, mode recommendation, prior state, context budget | SENSE report + scale pre-read | every downstream phase is mis-scoped |
| **SCOPE** (1.5) | Scale-parametric sizing + disambiguation; one clarifying gate only when bimodal; can override a confidently-wrong route | `scope.md` (size, depth_schema, chosen_reading, route_override) | scale ambiguity never resolved; PLAN has no depth_schema |
| **DEFINE** | Office-hours forcing questions; lock premises; force alternatives; pick the wedge; hard gate until APPROVED | APPROVED design doc | PLAN/BUILD consume ad-hoc prose with no locked premises |
| **DISCOVER** | Read-only map of codebase, ADRs, lessons, reusable skills/agents touching the wedge | `discover-report.md` | PLAN flies blind; work reinvents or contradicts prior decisions |
| **PLAN** | Cold-executor trio born together; ≤5-min/task granularity hard-check; cost estimate; founder approval gate | `plan.md` + `spec.md` (draft) + cost estimate | BUILD runs against an unwritten/unreviewed plan |
| **BUILD** | Execute via TDD + subagent-driven-development; fresh subagent per task with two-stage review | implemented code, atomic commits | no implementation is produced |
| **REVIEW** | Adversarial 3-stage: spec compliance → code quality → pack compliance; P1 blocks SHIP | review + compliance reports | unreviewed code reaches SHIP with no signal |
| **SHIP** | PR (default) / deploy / customer handoff; final compliance hard-stops; voice gates; CI validation | PR, release notes, audit log | no deploy validation, rollback, or audit log |
| **CAPTURE** | Durable close: lessons, ADR, evolution-log; reaffirm the trio against build evidence; profile append | lessons/ADR/log entries; annotated trio | cross-session continuity lost; next operator re-derives everything |

**Mode presets** (`skills/cycle/SKILL.md`): `hotfix` (SENSE+BUILD+REVIEW+SHIP), `internal-tool` (all),
`research-dive` (SENSE+DEFINE+DISCOVER), `meta-infra` (all, heavier REVIEW/CAPTURE, activates Gates
M1–M4, 600k soft / 900k hard cap), `auto`. **Composite shortcuts** are pure delegators: `/li:fix`,
`/li:research`, `/li:plan-and-build`, `/li:review-and-ship`. Always-enforced gates: cost estimate before
BUILD; mandatory founder approval at end of PLAN; 3-stage REVIEW; compliance hard-stop in SHIP; per-task
two-stage subagent review in BUILD (complexity-gated since v4.9 — mechanical leaves review inline).

---

## 4. Skills — 168, by cluster

All 168 skills are `layer: foundation`, namespaced `/li:<name>`, catalogued in the auto-generated
`skills/CATALOG.md`. By logical cluster:

- **Cycle + orchestrator + shortcuts (~16)** — the nine phase skills (the most polished in the repo,
  289–471 lines), the `cycle` orchestrator (393 lines), the four composite delegators, plus
  `resume`/`status`/`jobs` (the lifecycle controller) and `migrations`/`v4-migrate`.
- **Engineering-domain modules (5 + 33 sub-skills)** — `ta-*` (architecture), `da-*` (data), `sc-*`
  (security), `dh-*` (devops), `tq-*` (testing): each module = 1 orchestrator + 7 sub-skills, rigorously
  uniform (full/loop/single granularity, each sub-skill dispatching to named agents). `full-engineering-pass`
  (367 lines) composes all five in DAG order TA → DA‖SC → DH → TQ.
- **Generate-* family (~14)** — `generate` chains a shared content pipeline (outline → write → design → qa)
  into per-format renderers: `generate-ppt`, `generate-word`, `generate-web`, `generate-app`,
  `generate-style-learn`. The clearest *deliberate* stubs in the repo live here: `generate-pdf`/`-xlsx`/`-visio`
  are self-labeled "⚠ TEMPLATE ONLY — content not curated."
- **Frontend-* family (6)** — `frontend-design` orchestrator → `frontend-typography`/`-motion`/`-shader`
  sub-skills (each emitting a JSON contract), `frontend-design-review` (6-dimension gate),
  `frontend-style-extract`.
- **Context-* family (~16)** — warm (load-in): `context-warm[-adrs|-related|-customer|-sessions|-from-url]`,
  `context-warmup`; budget/cool: `context-budget` (+`--watch`), `context-budgetwatch` (removed 2026-06-10 — consolidated into `context-budget --watch`), `context-cool`,
  `perf-mode`; persist: `context-save`/`-restore`/`-snapshot`/`-dump`. This cluster carries the repo's
  main naming inconsistencies (see §17).
- **Session-harness / ops (~30)** — `doctor`, `health`, `safe-install`, `scaffold[-mvp|-internal-tool]`,
  `catalog`, `maintenance`, `uniformity`, `learn`/`lessons`/`lessons-surface`/`lessons-promote`,
  `adr-new`, `capture`, `personas-rotate`, `retro`, `usage-log`, `audit`, `code-freeze`/`-unfreeze`,
  `browse`/`scrape`/`pair-agent`/`codex`/`qa`/`investigate`/`brief-forge`/`compliance-gate`,
  `instruction-parity-check`.
- **Pack + role (~14)** — `pack-create`/`-list`/`-switch`/`-validate`; `role-activate`/`-deactivate`/
  `-deep-dive`/`-frame`/`-new`/`-rotate`/`-update`/`roles-list` (a clean lazy-load + deep-dive tier design).
- **Plan-review + ideation (~7)** — `office-hours`, `plan-ceo-review`, `plan-eng-review` (the required
  pre-ship gate), `plan-design-review`, `plan-devex-review`, `plan-tune`, `autoplan`.

---

## 5. Agents — 65 (tracked), eight categories

One markdown role-definition per agent under `agents/<category>/`, with uniform frontmatter
(`name`, `category`, `description`, `color`, `tools`, `voice: internal`, `tier: permissive`,
`cli_support: claude-code+codex full`). Categories: **communication (4)**, **compliance (3)** (EU-AI-Act /
GDPR / SOC2), **customer (3 tracked)**, **devops (5)**, **doc-gen (3)**, **engineering (33 — the fleet)**,
**frontend (5)**, **security (9)**.

The engineering category splits into general-purpose roles (CodeReviewer, Architect, Refactorer,
DebugForensics, Planner, TestRunner, ReadOnly, …) and **module-spawned specialists** (SchemaArchitect,
SystemArchitect, DeploymentEngineer, ObservabilityArchitect, PerfBudgetEnforcer, …) — the agent half of
the ta/da/sc/dh/tq modules.

**Dispatch model** — three paths, one canonical convention:

1. **`/li:brief-forge subagent_spawn <from-skill> <AgentName> brief "$brief_file"`** — the canonical
   one-shot spawn. A skill writes a brief (task / context_pointers / constraints / acceptance) to a
   tempfile and routes it through Brief Forge (which scores completeness, writes an envelope to the
   audit log, and gates on score). Used by the module sub-skills, `ship`, `discover`, `generate-ppt`.
2. **`/li:pair-agent --agent <Name>`** — a two-mind, in-the-loop alternation between the main agent and
   a named subagent, with an operator gate each turn. Claude-Code-only (Agent-tool dependency).
3. **Inline vs dedicated** — `docs/concepts/agent-dispatch-rules.md`: spawn when open-ended or
   adversarial; run inline when cheap + deterministic or needs accumulated context.

The six agents the v4.9 audit flagged as orphans (CustomerEmpathyCheck, PostDemoFollowup,
SlideNarrationCritic, DevOpsToolchain, ReadOnly, ResearchSynthesizer) now all have real dispatch lines —
the finding is closed.

---

## 6. Hooks — 30, opt-in enforcement

Each hook is a directory with `HOOK.md` (frontmatter: name / tier / event / fires_on / override / audit)
and `run.sh`. Tier breakdown (the README still says 29 — stale): **23 warn-only**, **2 JUSTIFIED-BLOCK**
(`secret-scan-block`, `customer-data-block` — `exit 1` on a high-confidence match in staged content,
override only via an audited env var), **2 surface-only**, **2 lifecycle** (`job-begin`/`job-end`),
**1 context-inject** (`session-digest`).

**Event model** (Claude Code's hook events): `PreToolUse(Edit|Write)` — the module hooks +
`no-secrets-in-edit` + `frozen-zone-warn`; `PreToolUse(Bash)` — the git/command gates (`secret-scan-block`,
`customer-data-block`, `no-direct-main-push`, `no-merge-without-review`, `no-production-mutation-without-auth`);
`UserPromptSubmit` — `no-customer-data-in-message`; `PostToolUse` — `no-customer-data-in-screenshot`,
`job-end`; `SessionStart` — `session-digest`, `job-stale-warn`.

**Shared infrastructure** (the v4.9 hardening):

- **`hooks/shared/_input.sh`** — the dual-mode stdin adapter. Claude Code delivers tool data as JSON on
  *stdin*; the hooks originally read `$1`, so they silently no-op'd (the audit's headline "blocking"
  finding). `hook_input <field>` reads stdin once (bounded 0.2s, TTY-skipping so it can't hang in CI),
  extracts command/file_path/prompt/payload via `jq`, and **falls back to `$1`** when there's no
  stdin — so the original call path is preserved and the stdin path is purely additive.
- **`hooks/shared/_patterns.sh`** — shared secret/PII detection, defined once, composed per hook
  *without* flattening the tier split: `scan_secrets tier1` (high-confidence, safe to BLOCK) vs `all`
  (tier1 + false-positive-prone heuristics, WARN-only); `scan_customer` (email / phone / Swedish
  `personnummer` / name+case-id incl. `ärende`). The file is the one place functional Swedish PII regex
  now lives, and is explicitly allowlisted in the English tripwire.
- **`bin/_audit.sh`** — the unified `audit_log` writer. Append-only JSONL to `~/.lintel/audit/<category>.jsonl`,
  fork-free JSON escaping (an out-variable, no subprocess per key) tuned for the per-edit hot path.

**Install model** — hooks ship **inert** at `~/.lintel/hooks/` and are never auto-installed. The operator
symlinks each chosen hook into `~/.claude/hooks/` and registers it in `~/.claude/settings.json`. This
"honest opt-in" means hooks never surprise the operator — but it also means the *entire* enforcement
layer is Claude-Code-only (other CLIs don't fire hooks).

---

## 7. The pack system — identity as a resolved field

`resolve_pack_field <dotted.path>` (`lib/pack-resolver.sh`) is the single accessor for all identity. It
reads the active pack name from `~/.lintel/packs/active-pack` (default `_default`), validates the
manifest (requires name/version/voice/compliance/navigation; rejects `extends:` cycles), resolves the
inheritance chain root→leaf into a per-session cache, and extracts the field (handling both block and
inline-flow YAML). Failure semantics are explicit and never silent: parse error → hard-fail with audit;
invalid active pack → fall back to `_default` + warn; even a cache-priming failure has a last-resort
hardcoded-neutral default so `voice.default_tier` still yields `internal`. The cached value is immutable
for the cycle (a mid-cycle pack-switch applies next cycle).

`packs/_default/pack.yaml` is the neutral baseline — `voice.enforce: none`, `compliance.mode: advisory`,
persona/roles/brand all null. **This is wired, not aspirational: `resolve_pack_field` has 136 call sites
across 46 skills** (heaviest in `ship`, `review`, `cycle`, `sense`, `build`). The pack contract lives in
`lib/pack-schema.yaml` (v1).

---

## 8. Runtime — mechanical-first, honest LLM stub

Every lib helper is pure bash; no LLM runs inside the lib (the agent *is* the LLM). The libs do a
mechanical first pass and emit a signal (`escalate: yes`) the skill's prose hands to the agent.

- **`scale-estimator.sh`** — the size axis: `classify_size` → XS…XL from breadth/depth/surface lexicons;
  `scale_ambiguous` detects the bimodal case; `size_to_depth_schema` → flat/phased/tree;
  `scale_calibrated_prior` reads CAPTURE's `granularity.jsonl` and takes the *median* actual per size
  (the calibration loop), falling back to hardcoded priors (XS≈4k … XL≈120k).
- **`orientator-routing.sh`** — mechanical SENSE routing: `classify_intent` (keyword case-match →
  build/fix/review/research/ship/deploy/scaffold/resume/unclear, with Swedish aliases), `match_workflow`,
  `assess_risk`, `score_confidence`. **`invoke_llm_orientation` is an explicit Phase-4 stub** that
  returns `{"source":"mechanical",...}` with no LLM call — honestly documented.
- **`brief-forge.sh` + `brief-forge-evaluators.sh`** — envelope construction + scoring. The neutral spine
  ships 3 mechanical evaluators (security / completeness / stale, all regex/field-presence placeholders);
  the doc's other two (sdl_compliance, trailblazer_alignment) live in external packs. Aggregate score =
  the *minimum* evaluator score (worst-evaluator-wins).
- **`bin/_jobs.sh`** — the jobs engine: `job_create`/`job_set_steps` (per-step `consumes`/`produces`/
  `status`/`blocked_until` contracts), `job_can_start` (evaluates a tiny `blocked_until` predicate
  grammar), `job_resume_point` (first incomplete-AND-startable step in WBS order — a node-path `1.1.a`
  for tree plans), `regenerate_active`, `job_archive`.
- **Schemas** — `lib/pack-schema.yaml` and `lib/envelope-schema.yaml` (the single-source contracts the
  shared-schema discipline requires).

---

## 9. Scale-parametric planning (v4.8/v4.9)

The planning machinery threads a **size axis** through SENSE → SCOPE → PLAN → CAPTURE:

- **The clarifying gate** — `skills/scope/SKILL.md` (Phase 1.5). When a request is bimodal-ambiguous
  ("deploy a website to azure" — static page or landing zone?), SCOPE fires *exactly one*
  AskUserQuestion. Clear small requests run silent (ceremony is the failure mode). Degraded fallback
  (no AskUserQuestion): take the conservative larger reading and note the assumption rather than block.
  SCOPE has **route-override authority** — a `deploy→ship` route that's actually an L/XL greenfield build
  gets rewritten to a full cycle from DEFINE (the "smoking-gun fix"; `deploy` became a distinct intent in v4.9).
- **`depth_schema`** — XS/S→flat, M→phased, L/XL→tree. This single `scope.md` field is the only signal
  PLAN reads to choose its WBS shape (flat task table / phased / phase→task→subtask tree).
- **The cold-executor trio** — PLAN emits `plan.md` + `spec.md` + `prompt.md` *simultaneously*, from
  versioned templates under `scaffolding/01-foundation/templates/plan/`. A fresh AI session reading only
  the trio can re-execute the work.
- **Granularity** — every leaf is 2–5 minutes of implementer time; `plan-eng-review` keeps a BLOCKING
  per-leaf check.
- **The calibration loop** — CAPTURE records `actual_tokens` per size; the estimator reads the median
  back as the corrected prior. Estimates self-correct from recorded actuals.

---

## 10. Brief Forge, Envelope, Wiki generation

- **Brief Forge** (`skills/brief-forge/SKILL.md`, `docs/concepts/brief-forge.md`) — the universal
  hand-off gate. Every subagent spawn / phase transition / cold-executor birth passes through it: it
  resolves pack policy (which evaluators), checks cold-path-bypass (always audited), constructs the
  envelope, runs evaluators, sets `completeness_score = min(scores)`, writes the audit, and decides on
  score (<40 escalate/block, 40–59 warn, ≥60 proceed). **Wiring status:** it's a sourced library that
  skills invoke via the `/li:brief-forge subagent_spawn` convention, but the `brief-forge-pre-spawn`/
  `-pre-phase` hooks that would make it *mandatory* on every handoff do not yet exist — the gate is
  available-and-called, not yet hook-enforced everywhere.
- **Envelope** (`lib/envelope-schema.yaml` v1) — the HEAD/BODY/TAIL contract every hand-off carries.
  Every envelope is appended to `~/.lintel/audit/envelopes-<date>.jsonl`; `bin/li-envelope-replay <id>`
  dry-runs by default (`--apply` to re-invoke, gated on `replay_safe`); `bin/li-envelope-validate` checks
  the schema. Both bins are shipped.
- **Wiki + showcase** — `bin/li-wiki-gen` deterministically regenerates both the markdown wiki
  (`docs/wiki/`) and the operator-facing single-file showcase (`docs/showcase/lintel-the-harness.html`)
  from the same sources (skill/agent frontmatter, pack.yaml, schemas), closing the historic
  "showcase drifts from code" gap. `--check` enforces idempotency. **`bin/li-forge-stats` is documented
  but absent** — correctly marked "(planned — not yet shipped)."

---

## 11. The factory & dogfooding

`scaffolding/01-foundation/` is the factory — everything `bin/li-scaffold init` copies into another repo:
`CLAUDE.md` (rendered from `CLAUDE.md.template` via `sed` substitution), `CORE-PRINCIPLES.md` (the 10
load-bearing rules), `EVOLUTION.md` + `EVOLUTION-LOG.md` (the change-governance process),
`tasks/{lessons,memory,personas,todo}.md`, `docs/adr/{README,TEMPLATE}.md`, `.claude/agents/` (4 baseline
subagents: ReadOnly, CodeReviewer, TestRunner, SanityChecker), and the plan/spec/prompt templates.
`li-scaffold` is collision-safe (every copy guarded by `[ ! -f ]`; re-running never clobbers operator
edits). **Dogfooding:** the repo-root `CLAUDE.md` *is* the instantiated template — and it openly records
the gap that motivated it (until v4.8 Lintel built the factory but never ran it on itself: no `.claude/`,
no `docs/adr/`, a thin CLAUDE.md).

---

## 12. bin/ tooling — 14 operator tools + 3 sourced helpers

`li-scaffold` (factory entrypoint), `li-doctor` (cross-CLI health check), `li-update` (update the plugin
across CLIs), `li-wiki-gen` (regen wiki + showcase), `li-uniformity` (regen the D1–D14 coverage matrix),
`li-compat-audit` (Gate-M2 mechanical compatibility audit), `li-envelope-validate` / `li-envelope-replay`,
`li-lessons-promote` (lift a repo lesson into the factory) / `li-lessons-sync` (cross-machine, opt-in),
`li-roles-sync`, `li-adr-new`, `li-review-log` / `li-review-read` (native review-gate log, replacing an
external dependency). Sourced helpers: `_aliases.sh` (deprecated-name grace period), `_audit.sh` (the
audit writer), `_jobs.sh` (the jobs engine).

---

## 13. State & memory — the snowball

| Store | Holds | Lifecycle |
|---|---|---|
| `tasks/lessons.md` | lessons from corrections (`L-NNN`) | append after ANY correction |
| `tasks/memory.md` | durable cross-session working state | update on durable change |
| `tasks/personas.md` | structured operator calibration | read at session-start |
| `docs/adr/NNNN-*.md` | decision records | one per non-trivial decision |
| `docs/v4.x/structure-changes/` | evolution log (Gate M1 artifacts) | per structural change |
| `.lintel/state/00-state.md` (+ module state) | per-repo cycle state | written by cycle/module skills |
| `~/.lintel/profile.yaml` | active pack · mode · role | operator-global |
| `~/.lintel/jobs/_active.md` | open workflow_root jobs | `/li:resume`/`/li:status` read it |
| `~/.lintel/sessions/` | context-save snapshots | `/li:context-restore` reads them |
| `~/.lintel/audit/*.jsonl` | append-only audit (reviews, overrides, envelopes, hooks) | via `bin/_audit.sh` |

**Jobs system** — `workflow_root` flows (cycle, plan) spawn a job under `~/.lintel/jobs/<id>/` holding
`job.yaml` (per-step contracts with mechanical `blocked_until` gates), `00-state.md`, `outputs/`,
`inputs/`. Three hooks drive it (`job-begin`/`job-end`/`job-stale-warn`); `job-end` promotes keep-items
(ADRs → `docs/adr/`, lessons → `tasks/lessons.md`, the trio → `docs/plans/<slug>/`) and archives the
rest. Explicitly **no daemon** — `_active.md` is regenerated on writes only.

**Session-start ritual** — read CLAUDE.md + AGENT-INSTRUCTIONS.md + CORE-PRINCIPLES.md; read recent
lessons *before acting*; skim memory; load personas + profile; list ADRs + structure-changes. For Claude
Code, the `session-digest` SessionStart hook (ADR-0002) auto-injects a ≤400-token digest of the top rows;
non-hook CLIs read the files explicitly.

---

## 14. Testing & CI

**Layout:** `tests/shape/` (26 structural-contract tests), `tests/unit/` (34), `tests/integration/` (1),
`tests/behavior/` (1), `tests/conventions/`, `tests/e2e/` (**empty**). Runner `tests/runner/run-all.sh`
discovers `*.sh` per scope and runs each with stdin from `/dev/null` (so hook-invoking tests can't consume
the runner's control FD — a v4.9 fix).

**Shape tests are the guardrails** — the 5 module contracts + `full-engineering-pass-contract`;
`frontmatter-lint-all`, `agents-categorized`, `manifest-identity` (single-source identity sync);
`workflow-root-has-navigation`, `every-handoff-uses-envelope`, `handoff-cap-wired`,
`schema-versioned-contracts`; `pack-resolver-fallbacks` (9 failure scenarios), `audit-writes-via-helper`
(no inline JSONL writers), `bin-scripts-executable` (git mode 100755 — guards Windows non-exec commits);
the idempotency guards `catalog-regenerates-clean` / `wiki-regenerates-clean` / `uniformity-coverage`;
and the English-only tripwire **`no-swedish.sh`**.

**CI (`.github/workflows/ci.yml`):** `verify.sh` per subcommand; `install.sh`/`install.ps1` into a test
home on Ubuntu + Windows; `unit-tests` on both OSes; `shape-tests`; `e2e-claude-code-only`; `shellcheck`
(warn-only); `compliance-check` (placeholder, `if: false`). **`catalog.yml`** auto-regenerates
`skills/CATALOG.md` from frontmatter on push to main.

---

## 15. Multi-CLI portability (the honest tiers)

One canonical instruction source (`AGENT-INSTRUCTIONS.md`) + thin per-CLI manifests, all pointing at the
same `./skills/` and `./agents/`. Capability is explicitly tiered (`README.md`, `docs/multi-cli.md`):

- **Full:** Claude Code (native, `/li:<skill>`, first-class subagents + hooks + plan mode), Codex, Cursor.
- **Supported:** Gemini (context-file/GEMINI.md), OpenCode (manual fetch), Copilot CLI + Factory Droid
  (manifests still marked "schema verified post-launch").
- **Best-effort:** GitHub Copilot Enterprise (instructions file only, no skill mechanism), Cline /
  Continue / Aider (manual custom instructions, no plugin discovery).

Degradation is stated honestly: **hooks are a Claude-Code-only mechanism**; subagents degrade to
sequenced runs on Codex; skills depending on either "degrade to operator-runs-manually." The single most
important caveat for any user-facing claim: *"multi-CLI" is full on three, degraded on the rest, and the
entire enforcement layer is Claude-Code-only.*

---

## 16. Governance & the v4.9 remediation

**ADRs** (`docs/adr/`): ADR-0001 (dogfood the scaffolding) and ADR-0002 (session-digest auto-load), both
Accepted; the README codifies "ADR for any non-trivial, hard-to-reverse choice, not for bug fixes."
**Evolution log** (`docs/v4.x/structure-changes/`): Gate-M1 artifacts for structural changes (phase2-packs-
envelope, phase3-nav-forge-wiki, spine-extraction-audit, caip-pack-extraction).

**The v4.9 five-lens remediation** (audit + engineering-reviewed plan in `docs/audit/`) was the most
recent quality pass — 19 tasks driven by a six-auditor, five-lens read. It found a high engineering floor
undermined by *drift between the system and its own description*, and shipped: the English sweep (with a
permanent CI tripwire), identity reconciliation (one slug/version/email + a sync test), regenerated
counts, the hook stdin adapter + shared patterns, `deploy` as a distinct intent, the 500k-cap wiring,
and orphan-agent wiring — all merged, CI green on Ubuntu + Windows. (The CHANGELOG 4.9.0 entry slightly
*under*-claims the work: it describes the hygiene pass but not the deeper Phase-3 wiring that also landed.)

---

## 17. Known inconsistencies (cosmetic / naming)

- **Hook README stale** — `hooks/shared/README.md` says "29 hooks: 27 warn-only"; real tally is 30
  (23 warn + 2 block + 2 surface + 2 lifecycle + 1 inject).
- **Naming** — `context-budgetwatch` breaks the `context-*` hyphenation convention (should be
  `context-budget-watch`); `context-warm` vs `context-warmup` overlap; `context-snapshot`/`-dump`/`-restore`
  are an under-differentiated three-way; the catalog appears to map two distinct purposes to `/li:review`.
- **Two 6-axis review-rubric families** are divergent — `design-review`/`plan-design-review` score 1–10,
  `frontend-design-review` scores 0–100. Alignment is a deliberate design-judgment call, left open.
- **`scale-estimator.sh` comment lag** — an inline comment still says L/XL tree "falls back to phased
  until Slice 2" while `plan/SKILL.md` documents full tree rendering as shipped.

---

## 18. Readiness assessment — is it ready, is it polished?

### Solid (production-grade)
- The engineering core: the phase model, the five engineering modules (uniform, zero dead agent refs),
  `full-engineering-pass`.
- Runtime hygiene: fork-free audit writer, cached uniformity, dry-run-by-default replay, pack-resolver
  explicit-failure semantics — and pack-resolver is a *real* dependency (136 call sites / 46 skills).
- Test coverage of critical paths: 26 shape + 34 unit; the four CRITICAL v4.9 regression tests all landed
  (hook-input-adapter, mechanical-routing, handoff-cap-wired, the English tripwire). CI green on real
  runners including Windows.
- Honest LLM posture: the orientator LLM arm and the brief-forge evaluators are *labeled* stubs, not
  hidden cost.

### Rough (known, documented — close before a clean GA)
1. **`docs/getting-started.md` is an un-swept MS-CAIP fossil** — opens "Step-by-step for a new MS Sweden
   CAIP SE," requires "Microsoft SSO," uses the old slug. This is the *primary onboarding doc* and it
   directly contradicts the company-neutral front page. **Highest-impact remaining inconsistency.**
2. **`@microsoft.com` email still leaks** — `README.md:168`, `SECURITY.md:7` (vs the git identity's
   `@gmail.com`). The `manifest-identity` tripwire passes but **does not scan README/SECURITY**, so the
   guard gives false confidence here.
3. **Manifest descriptions still branded "MS-CAIP-SE"** with `microsoft`/`caip`/`azure` keywords — the
   v4.9 identity fix corrected slug/version/email but deliberately left brand wording as an operator call.
4. **`bin/li-forge-stats`** — documented as shipped in three concept docs, absent on disk. Ship or de-claim.
5. **Hollow e2e** — `tests/e2e/` is empty, yet a CI job runs against it (a green job asserting nothing);
   `integration/` and `behavior/` have one test each.
6. **`context-budgetwatch`** — the planned `context-budget --watch` consolidation (T19) shipped a `--watch`
   mode + alias, but the old skill remains; a thin residual.

### Missing / honest-degradation for GA
- **Multi-CLI is tiered** (full on 3, degraded on the rest); **hooks are Claude-Code-only**. Documented
  honestly, but any GA announcement must state it plainly.
- **One pack only** (`_default`); pack-resolver adoption and second-pack validation are out of scope
  "until a second pack exists." The CAIP identity lives in an external repo not verified here.
- **Brief Forge is callable but not hook-enforced** on every handoff; evaluators are mechanical, not LLM.

### Verdict
**GA-ready for Claude Code; beta for the other CLIs.** Architecturally the harness is sound, well-tested
on its critical paths, and now CI-guarded against the drift that plagued it. It is *polished enough to
use* — the operator does, every session, and it dogfoods itself green. It is **not yet polished enough
for a clean public launch** until the doc/identity punch-list above (#1–#4 especially) is closed and the
"multi-CLI = full-on-Claude-Code, degraded-elsewhere, hooks-Claude-only" caveat is stated up front.
Recommended framing for a release: *"a session harness for Claude Code (with best-effort support for
seven other CLIs)."*

---

## 19. Appendix — the agent-count discrepancy & open decisions

**Count:** `find agents` reports **70** in a full working tree but only **65 are tracked on `main`**. The
5 untracked files are legitimate customer-engagement agents — `DemoNarratorJunior`, `ExecutiveBriefingDrafter`,
`ProposalDrafter`, `RFPResponseDrafter`, `WorkshopFacilitator` — with no sensitive data, the same kind as
the 3 tracked customer agents. They were **silently dropped from commits by a broad `.gitignore` rule**
(`customer/`, a customer-*data* tripwire that false-positively shadowed the customer-*agents* directory).
The v4.9 work fixed the shadow (`!agents/customer/`), so they are now committable. **Open decision:** ship
them (count → 70, regenerate counts) or keep them local. Not auto-shipped — committing to a public repo
is an external act and the operator's call.

**Other open operator-decisions** (surfaced, not bugs): the manifest MS-CAIP brand wording (§18 #3); the
maintainer email value (§18 #2); the two divergent review rubrics (§17); whether to align the "8-phase"
branding with the real nine phases including SCOPE.

---

*Generated by a six-agent read-only sweep of `main @ 591925b` (v4.9). Counts and file references reflect
that commit. This document is itself a candidate for the dogfooded doc discipline — keep it in sync via
`bin/li-wiki-gen` once the showcase absorbs a "state of the harness" view.*
