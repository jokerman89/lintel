# S4L extension-pack initiative — plan

> Set4Life (S4L): an aggressive direct-response marketing/sales skill-pack for digital
> products, built as a first-class Lintel **extension pack** (plugin + pack hybrid) in its
> own repo, consuming the full PaidCreators + Forge System knowledge with **zero know-how loss**.
> Started 2026-06-14. Source: E:\Workspace\s4l-pack\ (2 files, ~19k lines).

## Locked decisions (operator, 2026-06-14)
- **D1 — Packaging:** *Extend Lintel core* so packs can ship skills/agents/hooks/workflows
  (meta-infra), then build S4L on it. (Not the lighter hybrid — the operator wants packs to be
  first-class executable extensions, fully lintel-native.)
- **D2 — Repo + namespace:** build in `E:\Workspace\s4l-pack`, namespace `s4l`; preserve the two
  source files under `source/`. Local git init now; GitHub remote is the operator's to create.
- **D3 — Scope:** full coverage, in waves, starting now. Nothing cut.

## Source → S4L mapping
- **File 2 (Forge System, 7.5k ln) = the workflow.** 12 TABS → cycle phases; "Vault Objects" →
  state ledger + brief-forge envelope; Path A (90-min Quick Start) / B (Curated) / C → mode presets.
- **File 1 (PaidCreators, 11.4k ln) = knowledge + prompts.** Each copy/paste prompt → a skill;
  each "bible"/framework → knowhow an agent wields.

## Two-part structure
- **Part A — Lintel repo (meta-infra):** the extension-pack contract.
- **Part B — s4l-pack repo:** the S4L pack itself.

---

## Waves

### Wave 0 — Extension-pack contract  [META-INFRA · lintel repo · M1–M4 gates]
- [ ] ADR-0018: the extension-pack contract (decision + consequences).
- [ ] Design: an extension pack IS a Claude Code plugin (ships `skills/ agents/ hooks/` via its own
      manifest → native namespacing + hook auto-registration) PLUS a `pack.yaml` with a new optional
      `extension:` block (`is_extension`, `namespace`, `provides.workflow`, `provides.{skills,agents,hooks}`
      declarations for Lintel awareness).
- [ ] Spine changes (ADDITIVE, behind shape tests):
  - [ ] `packs/_default/pack.yaml`: document the optional `extension:` block (null/false default).
  - [ ] `lib/pack-resolver.sh`: resolve + validate `extension.*` (tolerant; identity packs unaffected).
  - [ ] `/li:pack-switch`: activating an extension pack surfaces its provided workflow + knowhow.
  - [ ] `/li:catalog` · `/li:doctor` · `/li:help`: recognize pack-shipped surface (awareness, no dup).
  - [ ] scaffolder: `bin/li-pack-scaffold` (or extend `pack-create`) → extension-pack skeleton.
- [ ] M1 structure-changes doc · M2 `li-compat-audit` · M3 shape test `extension-pack-contract.sh`
      · M4 migration/clarity note. Backward-compat: purely additive.
- [ ] Suite green on committed tree; independent review (L-007); PR to lintel main.

### Wave 1 — S4L repo scaffold  [s4l-pack repo]
- [ ] Move 2 source files → `source/`; keep `build/extraction/`.
- [ ] Scaffold extension-pack skeleton (Wave-0 scaffolder): `.claude-plugin/plugin.json` (+ per-CLI
      manifests), `pack.yaml` (S4L identity, namespace `s4l`, `navigation.default_workflow: s4l-forge`,
      `knowhow.source`), dirs `skills/ agents/ hooks/ knowhow/ lib/ tests/`, README, CLAUDE.md,
      `.claude/` home (plans, decisions, memory).
- [ ] `git init` + `.gitignore`.  (Remote = operator.)

### Wave 2 — S4L forge cycle spine
- [ ] `/s4l:forge` orchestrator: 12 phases, Path A/B/C presets, entry/hop-in/footer parity w/ `/li:cycle`.
- [ ] Vault model: implement "Vault Objects" on the state ledger + brief-forge envelope; define
      vault-object schemas (from extraction E/F/G).
- [ ] Phase skills stubbed + wired into the cycle.

### Wave 3 — Path-A core skills (90-min Quick Start vertical slice)
- [ ] The exact Path-A sequence (extraction E): niche-select · reality-check · product-forge ·
      packaging · deliverables · hero-story · proof-builder · unique-mechanism · signature-naming ·
      ethical-contrast · salespage(NEXUS) · launch-tech · hook-factory · launch-plan ·
      objection-crusher · nurture-email · order-bump · upsell. Each = full lintel-native skill from
      the verbatim prompt + house-style, vault I/O, When-NOT, footer.

### Wave 4 — Remaining skills (Curated path + file-1 library)
- [ ] extraction · niche-score · angle-picker · hero-journey · extended-hero-journey · vsl · upsell-2 ·
      email-series · ad-stories(13) · retargeting(6) · triple-hook · book-creation · content-grid ·
      presell · cro · fill-in-blank-salespage · video-sales-framework · meta-cognition-test.

### Wave 5 — Agents + hooks + knowhow
- [ ] Marketing agents (personas wielding bibles): CopyChief · CROStrategist · NicheOfferAnalyst ·
      SalesPsychologist · ProofClaimsAuditor · OfferArchitect · EmailMarketer · AdCreative (map to
      extraction AGENT-EXPERTISE).
- [ ] Hooks (via pack plugin hooks.json): claim-honesty/proof-substantiation gate · offer-stack
      completeness · aggressive-marketing voice tier.
- [ ] `knowhow/`: 15-section Sales Page Bible · 6 Cognitive Biases · Marketing KB · CRO board ·
      headline formulas — tag-indexed, lintel-native, referenced by skills/agents.

### Wave 6 — Identity + voice + brand
- [ ] pack.yaml voice tier (aggressive direct-response) + corpus · persona · roles · brand
      (Canva/landing templates) · knowhow override-priors.

### Wave 7 — QA + verification
- [ ] Tests: extension-pack-contract (lintel) · s4l manifest valid · skill-descriptions-trigger ·
      cycle wiring · vault-object schema integration test.
- [ ] `/li:doctor` recognizes s4l · `/li:catalog` · instruction parity · independent CodeReviewer (L-007)
      · install dry-run (`claude --plugin-dir`).

### Wave 8 — Ship + capture
- [ ] ADRs (s4l repo): forge-cycle design · vault model · voice tier. README + install docs.
- [ ] Surface to operator: create GitHub remote (operator runs — hard guardrail) + `/plugin install`.
- [ ] CAPTURE: lessons · working-state · vault note.

## Guardrails
- New REMOTE repo / bulk-push to fresh remote = **operator runs it** (hard guardrail). I build + `git init` locally only.
- Wave 0 is meta-infra: ADR + structure-changes + compat audit + shape tests + green suite before merge.
- **Lose-no-know-how:** every prompt → a skill carrying the verbatim IP; every bible → knowhow.
  Verified in Wave 7 against `build/extraction/` maps.

## Status
- [x] SENSE / SCOPE / DEFINE-architecture — decisions locked.
- [x] Digestion dispatched — 7 background subagents → `build/extraction/{01-04 paidcreators, 05-07 forge}.md`.
- [ ] Wave 0 → Wave 8.
