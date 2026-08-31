---
slug: caip-pack-extraction
date: 2026-06-03
cycle_id: v4.7-caip-extraction
operator: jokerman89
affected_paths:
  - packs/
  - skills/
  - agents/
  - hooks/
  - scaffolding/
  - lib/
  - roles/
  - seeds/
  - AGENT-INSTRUCTIONS.md
  - README.md
  - LAYERS.md
  - CLAUDE.md
risk_class: high
breaking_change: true   # extracts ms-internal + caip-se packs to a separate repo; de-biases the spine
---

# Structure change: CAIP pack extraction to a standalone distributable repo

> Gate M1 (structure-impact analysis) artifact for the CAIP extraction initiative.
> This is the master cut-list. **No files move until the operator approves this manifest
> and names the target repo.** Line numbers in the DE-BIAS table are Explore-agent claims
> and MUST be re-verified at execution time per L-003.

## Context — what this finishes

The v4.0 reframe ([lintel-v4.0-reframe-design.md](../../design/lintel-v4.0-reframe-design.md))
designed Lintel as "a generic harness with CAIP-SE as one pack." It shipped the **pack
manifests** (`packs/_default`, `packs/ms-internal`, `packs/caip-se`) but **never executed the
Phase-2 spine extraction**: the `caip-se/pack.yaml` references content dirs (`voice/`,
`persona/`, `roles/`, `brand/`, `knowhow/`, `lessons/`, `opinions/`,
`brief-forge/evaluators/`) that **do not exist on disk** under `packs/caip-se/`. The content
still lives in `scaffolding/03-ms-team/`, `skills/`, `agents/ms-specific/`, `hooks/`, and
~48 hardcoded references remain in the "generic" spine.

This initiative does two things:
1. **Completes FR-D** — physically co-locates CAIP content into the pack structure.
2. **Extracts the packs to their own repo** as a distributable pack-on-top of Lintel.

## Operator decisions (locked 2026-06-03)

| # | Decision | Choice |
|---|---|---|
| D1 | New-repo relationship | **Distributable pack on top of Lintel.** New repo = packs + CAIP content only; installs alongside generic Lintel via the pack/plugin system. Lintel keeps spine + `_default`. |
| D2 | Extraction scope | **`ms-internal` + `caip-se` both leave.** Lintel becomes company-neutral; only `_default` remains. |
| D3 | Spine purity | **Aggressive — all MS-branded artifacts leave.** Generic equivalents (Terraform/K8s/GDPR/SOC2/EU-AI-Act) stay. |

## What changed (shape)

- Lintel `packs/` goes from 3 packs → 1 (`_default` only).
- ~26 MS skills, ~22 MS agents, 5 MS hooks, `scaffolding/02-sdl/`, `scaffolding/03-ms-team/`
  leave the tree.
- The spine is de-biased: hardcoded `Trailblazer`/`RAIS`/`WorkProfile`/`first-party`/`Azure`
  assumptions become pack-resolved (`resolve_pack_field …`) or are removed.
- A new sibling repo gains its own per-CLI plugin manifests and becomes installable as
  `ms-internal` + `caip-se` packs.

---

## Bucket A — MOVE to the CAIP repo

### A1 · Packs (manifests)
- `packs/ms-internal/`
- `packs/caip-se/`

### A2 · Agents (22)
**Whole dirs:**
- `agents/ms-specific/` (15): AIStartupAdvisor, ARMTemplateReviewer, AzureArchitect,
  AzureOpenAIAdvisor, BicepReviewer, CAIPEngagementCoach, CloudTestSuiteAuthor,
  FieldCTOAdvisor, FirstPartyMigrator, GraphAPIAdvisor, HybridScenarioArchitect,
  KeyVaultAuditor, M365CopilotAdvisor, OneCSAuditor, ProvenanceVerifier
- `agents/voice/` (1): TrailblazerVoiceCritic

**Individual files (MS-branded, dir otherwise stays):**
- `agents/compliance/RAIReviewer.md`, `SDLReviewer.md`, `AGTReviewer.md`
- `agents/devops/OneBranchReviewer.md`, `EV2PipelineAuditor.md`
- `agents/communication/NordicSwedishCopyCheck.md`

### A3 · Skills (~26)
`rais-customer-voice-check`, `rais-impact-assessment`, `rais-sensitive-use`,
`rais-transparency-note`, `onecs-check`, `onerai-submit-draft`, `dpia-submit-draft`,
`dsb-submit-draft`, `entra-agent-id-submit-draft`, `agent-tier-stamp`, `caip-audit`,
`first-party-check`, `provenance-track`, `onebranch-validate`, `cloudtest-eval-suite`,
`msvoice-rewrite`, `brand-update`, `scaffold-engagement-demo`, `demo-deliverable-gen`,
`az-discover-presale`, `az-tldr`, `release-ev2`, `release-deploy-ev2`, `setup-ev2-targets`,
`safe-deploy-ring`, `security-genomlysning`, `asset-search`

### A4 · Hooks (5)
`no-trailblazer-without-corpus`, `no-en-vocab-in-trailblazer`, `stale-calibration-warn`,
`brand-staleness-warn`, `non-first-party-warn`

### A5 · Scaffolding / corpus / templates
- `scaffolding/02-sdl/` (entire — SDL/AGT/RAIS/compliance reference) → CAIP repo `compliance/`
- `scaffolding/03-ms-team/` (entire — OurVoice corpus + MS doc-gen templates)
  → CAIP repo `packs/caip-se/voice/` + `packs/caip-se/brand/templates/`

### A6 · Pack-resolved content (finishes FR-D co-location)
- `tasks/personas.md` sales-engineer template → `packs/caip-se/persona/operator.md`
- SDL + `trailblazer_alignment` evaluators from `lib/brief-forge-evaluators.sh`
  → `packs/caip-se/brief-forge/evaluators/`

---

## Bucket B — STAYS in Lintel, requires DE-BIAS

Hardcoded CAIP/MS references in generic files. **Line numbers from Explore agent — re-verify
before editing (L-003).** Action: replace with `resolve_pack_field …` or remove.

| File | Line(s) (verify) | What | Action |
|---|---|---|---|
| AGENT-INSTRUCTIONS.md | 72, 82, 171, 187, 225, 235, 243, 259 | WorkProfile, RAIS voice-check, MS modes, first-party | genericize / pack-resolve |
| README.md | 3, 31, 101, 102, 116, 117, 148 | "MS-CAIP-SE harness", CAIP audience, 5+7+8 tiering, OurVoice, first-party | rewrite neutral |
| LAYERS.md | 14, 18, 37 | voice tier internal/trailblazer, MS-policy Layer 2 | genericize |
| CLAUDE.md | 11, 46 | "MS-CAIP-SE harness", OneCSAuditor example | rewrite neutral |
| skills/cycle/SKILL.md | 63, 77 | customer-engagement / MS-internal mode assumptions | pack-resolve mode presets |
| skills/generate-ppt/SKILL.md | 47, 90, 181 | trailblazer default, Azure icons, Nordic example | pack-resolve voice/brand |
| skills/generate-word/SKILL.md | 25, 170 | RAIS transparency-note target, onerai/rais refs | pack-resolve targets |
| skills/generate-web/SKILL.md | 49, 426 | `--azure-theme` default | neutral default; theme via pack |
| skills/document-generate/SKILL.md | 24, 100, 307-309 | Trailblazer tier, OurVoice blocklist, RAIS | pack-resolve |
| skills/compliance-gate/SKILL.md | (audit) | hardcodes caip-audit/onecs/rais | pack-resolve `compliance.hooks` |
| lib/brief-forge-evaluators.sh | 152-176, 183-214 | SDL + Trailblazer evaluators inline | move to pack (A6); keep generic |
| scaffolding/01-foundation/TEMPLATE-skill.md | 45-49 | Trailblazer + rais gating in template | neutral template |

---

## Bucket C — Borderline (operator confirms during execution)

| Item | Default | Rationale |
|---|---|---|
| `roles/` (engineering-manager, field-cto, solution-architect) | **flag** | File names ≠ caip-se pack's declared role inventory (sales_engineer…). May be generic operator roles. Confirm before moving. |
| `seeds/brand/design-patterns/` | **STAYS** | "ultra-modern-lovable-style" is generic design seed, not MS brand. Keep unless operator says otherwise. |
| `agents/customer/` (8) | **STAYS** | Sales-engineering generic, not MS-branded. Operator may pull into pack if CAIP-coupled. |
| `compliance-gate` skill | **STAYS + de-bias** | Generic pack-driven gate mechanism; the MS hooks it calls move. |
| customer-data / secret-scan hooks | **STAYS** | Generic privacy/safety, not MS-specific. |
| `config/aliases.yaml` | **verify** | Check for MS aliases before deciding. |

---

## Target repo shape (D1 — pack on top)

```
<caip-repo>/
├── .claude-plugin/plugin.json        # own per-CLI manifests (not Lintel's)
├── .codex-plugin/ .cursor-plugin/ …  # gemini-extension.json, .droid-plugin, .opencode
├── packs/
│   ├── ms-internal/pack.yaml
│   └── caip-se/
│       ├── pack.yaml                 # shareable: true; requires_lintel: ">=4.7"
│       ├── voice/                    # ← scaffolding/03-ms-team/voice/
│       ├── persona/                  # ← tasks/personas.md template
│       ├── roles/                    # ← roles/ (if C-confirmed)
│       ├── brand/                    # ← MS doc-gen templates + color tokens
│       ├── knowhow/  lessons/  opinions/
│       └── brief-forge/evaluators/   # ← SDL + trailblazer evaluators
├── skills/                           # A3 (~26)
├── agents/                           # A2 (22)
├── hooks/                            # A4 (5)
├── compliance/                       # ← scaffolding/02-sdl/
└── README.md
```

## Sequencing (under meta-infra discipline)

1. **P0 — Approve manifest + name target repo + init it.** (this gate)
2. **P1 — FR-D co-location in-place.** Create `packs/caip-se/{voice,persona,roles,brand,…}/`
   inside Lintel; `git mv` Bucket A5/A6 content in. Pack-resolver test harness green.
3. **P2 — De-bias spine (Bucket B).** Replace hardcoded refs with `resolve_pack_field`.
   Re-verify each line first. `grep` sweep returns no execution-path CAIP matches.
4. **P3 — Extract.** `git mv`/`git filter-repo` Bucket A → new repo (history-preserving).
   New repo gets own plugin manifests. Lintel `packs/` = `_default` only.
5. **P4 — Rewrite Lintel identity.** README/AGENT-INSTRUCTIONS/LAYERS/CLAUDE neutral.
   CAIP repo README documents install-on-top.
6. **P5 — Verify both repos.** Lintel: company-neutral, tests green, `/li:pack-list` shows
   `_default`. CAIP repo: installs on top, `/li:pack-switch caip-se` restores today's behavior.

## Backward-compat

**Breaking for any operator using Lintel for CAIP work.** Restored by installing the CAIP
repo + `/li:pack-switch caip-se` — identical behavior to today, per v4.0 design §1.6.

## Rollback procedure

Each phase is an atomic commit on a feature branch. Revert = `git revert <range>` or reset the
branch; `main` untouched until P5 verification passes. The extraction (P3) is the only
irreversible step (cross-repo history split) — gate it behind a clean P1+P2 and a tagged
pre-extraction snapshot (`git tag pre-caip-extraction`).

## Open question for operator

- **Target repo name + location.** Suggestions: `jokerman-caip-pack`, `lintel-caip-se`,
  `jokerman-caip-se`. Where on disk / which GitHub org?
