# Todo — CAIP pack extraction to standalone repo

**Initiative:** Lift `ms-internal` + `caip-se` packs (and all CAIP/MS-branded content) out of
Lintel into a separate distributable pack-on-top repo. Finishes the deferred v4.0 FR-D /
Phase-2 spine extraction.

**Manifest (cut-list):** [docs/v4.x/structure-changes/2026-06-03-caip-pack-extraction.md](../docs/v4.x/structure-changes/2026-06-03-caip-pack-extraction.md)

**Decisions locked:** pack-on-top · ms-internal+caip-se both out · aggressive de-MS.

## P0 — Approve + scaffold (current)
- [x] Map packs concept + verify CAIP inventory on disk
- [x] Surface + lock the 3 strategic decisions
- [x] Write extraction manifest (M1 artifact)
- [ ] **Operator approves manifest**
- [ ] **Operator names target repo + location**
- [ ] Init target repo; `git tag pre-caip-extraction` in Lintel; create feature branch

## P1 — FR-D co-location (in Lintel first)
- [ ] Create `packs/caip-se/{voice,persona,roles,brand,knowhow,lessons,opinions,brief-forge}/`
- [ ] `git mv` scaffolding/03-ms-team/voice → packs/caip-se/voice
- [ ] Move MS doc-gen templates → packs/caip-se/brand/templates
- [ ] Move tasks/personas.md sales-eng template → packs/caip-se/persona/operator.md
- [ ] Extract SDL + trailblazer evaluators from lib/ → packs/caip-se/brief-forge/evaluators
- [ ] Pack-resolver test harness green

## P2 — De-bias spine (Bucket B)
- [ ] Re-verify each Bucket B file:line (L-003) before editing
- [ ] Replace hardcoded refs with resolve_pack_field / remove
- [ ] `grep` sweep: no execution-path CAIP matches in skills/agents/hooks/lib
- [ ] Confirm Bucket C borderline items (roles/, seeds/brand, customer/, config/aliases)

## P3 — Extract to new repo
- [ ] History-preserving move (git filter-repo / git mv) of Bucket A → target repo
- [ ] Target repo: own per-CLI plugin manifests; pack.yaml shareable:true
- [ ] Lintel packs/ = _default only

## P4 — Identity rewrite
- [ ] Lintel README/AGENT-INSTRUCTIONS/LAYERS/CLAUDE → company-neutral
- [ ] CAIP repo README → install-on-top docs

## P5 — Verify both repos
- [ ] Lintel: neutral, tests green, /li:pack-list = _default
- [ ] CAIP repo: installs on top; /li:pack-switch caip-se restores today's behavior
- [ ] Structure-change + migration entries; CHANGELOG

## Review
_(filled at task end)_
