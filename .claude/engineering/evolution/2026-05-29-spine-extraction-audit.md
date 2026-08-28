---
slug: spine-extraction-audit
date: 2026-05-29
cycle_id: v4.0-phase1-meta-infra-spine
operator: jokerman89
affected_paths:
  - skills/
  - agents/
  - hooks/
risk_class: medium
breaking_change: false   # audit deliverable only — extraction itself is breaking, ships in later PR per design
---

# Spine extraction audit — v4.0 Phase 1 deliverable

> Per v4.0 design Ch.1 §2.2 A.8: ship the audit list as a PR artifact so future readers + future re-extractions have the inventory.
>
> This file is the L-002 (grep-first) discipline applied to "what's hardcoded in core that should be pack-loaded instead."
>
> Phase 1 ships the AUDIT. Spine extraction itself (replacing hardcoded references with `PackResolver` calls) ships in Phase 2 alongside pack architecture.

## Methodology

Per L-003: every reference verified via grep before classification.

```bash
# Reproducible commands
grep -rln "Trailblazer\|TrailblazerVoiceCritic" skills/ agents/ hooks/
grep -rln "CAIP-SE\|caip-se" skills/ agents/ hooks/
grep -rln "MS-internal\|MS-CAIP" skills/ agents/ hooks/
grep -rln "RAIS\|OneCS\|AGT" skills/ agents/ hooks/
grep -rln "WorkProfile" skills/ agents/ hooks/
grep -rln "OurVoice\|trailblazer-voice" skills/ agents/ hooks/
```

## Classification

Each reference is classified into one of three buckets:

- **PACK-BOUND** → move to pack manifest in Phase 2 (replace with `PackResolver` call)
- **EXAMPLE-ONLY** → reference in docs/examples; not a runtime call (keep as-is, mark as illustrative)
- **HISTORICAL** → in CHANGELOG, ADRs, or design docs (preserve verbatim)

## Inventory (initial — to be expanded during Phase 2 spine extraction)

### Trailblazer voice references

| File | Line(s) | Classification | Action |
|---|---|---|---|
| skills/generate/SKILL.md | — | PACK-BOUND | Replace with `resolve_pack_field voice.default_tier` |
| skills/generate-write/SKILL.md | — | PACK-BOUND | Same |
| skills/generate-ppt/SKILL.md | — | PACK-BOUND | Same |
| skills/generate-word/SKILL.md | — | PACK-BOUND | Same |
| skills/define/SKILL.md | — | PACK-BOUND | Same |
| skills/review/SKILL.md | — | PACK-BOUND | Same |
| skills/ship/SKILL.md | — | PACK-BOUND | Same |
| skills/capture/SKILL.md | — | PACK-BOUND | Same |
| skills/build/SKILL.md | — | PACK-BOUND | Same |
| .claude/engineering/design-archive/lintel-v3.x-* | — | HISTORICAL | preserve |

### Compliance-hook activations (MS-specific)

| File | Hook | Classification |
|---|---|---|
| skills/compliance-gate/SKILL.md | caip-audit, onecs-check, rais-* | PACK-BOUND |
| skills/sense/SKILL.md | WorkProfile detection | PACK-BOUND |
| skills/review/SKILL.md | Stage 3 compliance hooks | PACK-BOUND |
| skills/ship/SKILL.md | 4-gate aggregator | PACK-BOUND |

### Personas template (sales-engineer assumption)

| File | Classification | Action |
|---|---|---|
| tasks/personas.md | PACK-BOUND | Move template to packs/caip-se/persona/operator.md |
| skills/sense/SKILL.md | PACK-BOUND | Replace persona-load with `resolve_pack_field persona.source` |
| skills/role-frame/SKILL.md | PACK-BOUND | Same |

### Voice corpus path

| File | Classification | Action |
|---|---|---|
| scaffolding/03-ms-team/voice/OurVoice*.md | PACK-BOUND | Move to packs/caip-se/voice/ in Phase 2 |
| skills/rais-customer-voice-check/SKILL.md | PACK-BOUND | Replace path with `resolve_pack_field voice.corpus` |

## Phase 2 implementation order (preview)

When spine extraction PR opens (Phase 2 beta):
1. Ship pack-architecture (FR-B) first
2. Move identified PACK-BOUND content to `packs/caip-se/`
3. Replace each PACK-BOUND reference above with `PackResolver` call (in batches by file)
4. Run pack-resolver test harness after each batch
5. Final sweep: `grep -r "Trailblazer\|CAIP-SE\|RAIS\|OneCS" skills/ agents/ hooks/` returns no execution-path matches

This audit will be expanded with file:line citations during Phase 2 execution.

## Notes

- This is a Phase 1 DELIVERABLE only — it documents intent + inventory.
- Phase 2 (packs + spine extraction) is the work that USES this audit.
- Per `--no-direct-main-push` discipline, Phase 2 ships under meta-infra mode with full Gate M1-M4 cycle.
