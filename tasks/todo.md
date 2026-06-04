# Todo — Lintel dogfoods its own scaffolding (v4.8)

**Initiative:** Lintel was the scaffolding factory but never ran the factory on itself — no `.claude/`,
no `docs/adr/`, thin v3 CLAUDE.md. That's why ADRs/lessons didn't happen during the CAIP work. Fix it,
and prevent it for other adopters.

**Decisions (operator):** full self-contained repo CLAUDE.md · ADR infra now, no backfill · full scope
(dogfood + template refresh + reconcile v0.5 + doctor-check). See [ADR-0001](../docs/adr/0001-lintel-dogfoods-its-own-scaffolding.md).

## Done
- [x] Diagnose: compared deeplex (works) vs Lintel (no .claude/docs/adr/thin CLAUDE.md) vs claude-scaffolding v0.5
- [x] Dogfood root: copy `.claude/agents/` + SUBAGENT-GUIDE into Lintel root
- [x] Dogfood root: create `docs/adr/` (README + TEMPLATE)
- [x] Rewrite root `CLAUDE.md` → self-contained scaffolded form + Lintel project sections + dogfood note
- [x] ADR-0001 (the first future ADR — the dogfooding decision itself)
- [x] L-006 lesson (the factory must run on itself)
- [x] Template refresh: JStack → Lintel; self-contained note
- [x] Reconcile v0.5: deprecation banner in claude-scaffolding/README.md (uncommitted in that repo — operator to commit)
- [x] Prevention: `bin/li-doctor` "this repo's scaffolding adoption" check (warns when a repo lacks its own .claude/docs-adr/scaffolded-CLAUDE.md)
- [x] Verify: li-doctor check PASSES for Lintel now; bash -n clean

## Review

Lintel now eats its own dog food. Root has a self-contained, scaffolded CLAUDE.md, `.claude/agents/`,
and `docs/adr/`; the ADR/lessons ritual is wired in and enforced going forward. The `li-doctor` check
makes the "factory never ran on this repo" failure visible to every adopter, not just here.

**Not backfilled (per operator):** the v4.7 CAIP-era decisions were not retroactively written as ADRs —
discipline applies from ADR-0001 forward.

**Carries forward / for operator:**
- claude-scaffolding/README.md deprecation banner is an uncommitted edit in that separate repo.
- Consider whether deeplex's `docs/06-decisions/` and Lintel's `docs/adr/` conventions should unify.
- Old `v3.6.x/v3.7.0-dev` tags still present if a tag cleanup is wanted.
