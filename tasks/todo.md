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

## P1 — FR-D co-location (built directly in CAIP repo)  ✅
- [x] Create packs/caip-se/{voice,persona,roles,brand,...} in lintel-caip-pack
- [x] voice corpus → packs/caip-se/voice; MS doc-gen templates → brand/templates
- [x] personas.md sales-eng template → packs/caip-se/persona/operator.md
- [x] pack.yaml shareable:true, requires_lintel >=4.7.0

## P2 — De-bias spine (Bucket B)  ✅
- [x] Comprehensive grep sweep (two waves — see L-005); ~437 refs across ~130 files
- [x] Replace hardcoded refs with resolve_pack_field / remove (10 subagents + identity docs by hand)
- [x] Final sweep: 0 dangling CAIP refs in staying tree
- [x] Bucket C resolved: roles/→pack, seeds/brand→stays, customer/→stays, config/aliases agt-alias dropped
- [x] layer: ms-team → foundation (22 skills); CATALOG + generator updated

## P3 — Extract to new repo  ✅
- [x] lintel-caip-pack initial commit bd9b210 (99 files; clean-copy + provenance note, not filter-repo)
- [x] Own .claude-plugin manifest + marketplace; README documents install-on-top
- [x] Lintel packs/ = _default only (commit 04337f6)

## P4 — Identity rewrite  ✅
- [x] Lintel README/AGENT-INSTRUCTIONS/LAYERS/CLAUDE/AGENTS/GEMINI/SHIP-GATE → company-neutral
- [x] CAIP repo README → install-on-top docs

## P5 — Verify  ✅ (local) / ⏳ (operator)
- [x] Lintel: shape 19/0, unit 29/0; bash -n clean; 0 dangling refs; packs/=_default
- [x] Tests updated for new boundary (8 unit + 1 shape; 2 obsolete tests removed)
- [ ] OPERATOR: install lintel-caip-pack on top + /li:pack-switch caip-se → confirm parity
- [ ] OPERATOR: decide push / PR (not pushed — awaiting authorization)

## Deferred (separate doc-refresh, flagged not blocking)
- [ ] README/SHIP-GATE v3→v4 count drift (pre-existing, not caused by extraction)
- [ ] LAYERS.md full rewrite to foundation+packs model (banner added; historical body kept)
- [ ] CAIP repo: mirror remaining 6 per-CLI manifests; populate knowhow/lessons/opinions

## Review

CAIP successfully lifted out as a distributable pack-on-top (lintel-caip-pack),
completing the v4.0 reframe's deferred FR-D + Phase-2 spine extraction. Lintel is
now company-neutral (only _default pack). Three atomic commits on
v4.7-caip-extraction; main untouched; tag pre-caip-extraction is the restore point.
NOT pushed — awaiting operator authorization for push/PR.

Surprise: de-bias surface was ~10x the manifest estimate (the v4.0 spine extraction
was never actually run). Handled via 10 parallel de-bias subagents + hand-edited
identity docs. Lesson L-005 recorded (grep-token completeness).
