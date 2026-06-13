---
slug: design-parity-slides-tokens
date: 2026-06-13
cycle_id: v5.5-design-parity
operator: jokerman
affected_paths:
  - skills/design-dna/data/slides/ (NEW — 8 slide-decision CSVs)
  - skills/design-dna/references/ (NEW — token-architecture docs)
  - skills/design-dna/scripts/core.py (SLIDE_CONFIG + search_slide)
  - skills/design-dna/scripts/search.py (--slide flag)
  - skills/design-dna/scripts/emit_tokens.py (NEW)
  - skills/design-dna/scripts/validate_design.py (2 token-discipline warnings)
  - skills/design-dna/SKILL.md (slide + tokens dispatch rows)
  - skills/generate-ppt/SKILL.md (Step 2b slide-DNA pass)
  - tests/unit/design-tokens-emit.sh (NEW)
  - tests/unit/design-dna-search.sh (slide assertions)
  - tests/shape/design-dna-corpus.sh (slides + emitter assertions)
risk_class: low
breaking_change: false
---

# Structure change: design-parity-slides-tokens

> Gate M1 (structure-impact analysis) artifact for ADR-0017.

## What changed (shape)

1. NEW data subtree `skills/design-dna/data/slides/` (8 CSVs) + `references/` (4 token docs),
   both vendored from UUPM (MIT, attributed).
2. `core.py` gains `SLIDE_CONFIG` + `AVAILABLE_SLIDE_DOMAINS` + `search_slide()`; `search.py`
   gains a `--slide <domain>` flag. PURELY ADDITIVE — existing `--domain`/`--stack`/`--design-system`
   paths unchanged.
3. NEW script `emit_tokens.py` (a new capability, no prior equivalent).
4. `validate_design.py` gains two **warnings** (var() usage, hardcoded font). No new ERROR class —
   the exit-1 gate behavior is unchanged; warnings are advisory.
5. `generate-ppt` gains an internal Step 2b (query the slide engine). No CLI/flag change.

## Backward-compat

- Every existing design-dna invocation works unchanged (slide/tokens are new sub-commands).
- generate-ppt's `--brief` and `--from-pipeline` modes unchanged; Step 2b is internal.
- The validator's hard-gate (exit 1) set is identical to v5.4 — new findings are warnings only,
  so nothing that passed before now blocks. (The test's good.html fixture was updated to use
  tokens, demonstrating the new advisory, not because behavior regressed.)

## Migration path

No migration needed — additive change.

## Forward-compat

Enables: retrieval-grounded slide design across generate-ppt (and any future deck skill); a
profile→CSS token pipeline that packs inherit for free; future profiles emit layered tokens with
no extra code. Forecloses nothing — the slide subtree + emitter can be removed by deleting the
files + reverting the core.py/search.py additions (no other coupling).

## Verification

- Shape: `tests/shape/design-dna-corpus.sh` extended (8 slide CSVs, token-architecture ref,
  emit_tokens.py present, SLIDE_CONFIG registered)
- Behavior: `tests/unit/design-dna-search.sh` (slide color/layout/strategy + negative),
  `tests/unit/design-tokens-emit.sh` (three layers, canonical tokens flow, alias contract,
  fail-closed on missing profile), `tests/unit/design-validator.sh` (token-discipline warnings
  stay warnings; good.html now tokenized)
- Full suite green on committed tree (L-010) before push

## Rollback procedure

`git revert` the v5.5 commit range on feat/v5.5-design-parity. No state migrations. Vendored CSVs
+ references + emit_tokens.py are inert data/scripts; removing them reverts to v5.4 behavior.
