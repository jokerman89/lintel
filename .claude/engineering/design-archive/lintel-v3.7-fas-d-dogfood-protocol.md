# v3.7 Fas D — Dogfood Protocol + Synthetic Pre-Validation

**Generated:** 2026-05-29
**Status:** ACTIVE — synthetic pre-validation done; real-engagement dogfood operator-pending
**Audience:** operator (real-dogfood checklist) + future AI (resume Fas D)

> Fas D was originally "operator-only" because it requires a real customer engagement to dogfood `/li:frontend-design` end-to-end + capture L-004 canonical-pattern re-evaluation findings. This document does two things: (1) synthetic pre-validation that AI can perform without real customer data, and (2) explicit checklist for the operator's real-engagement run when it happens.

---

## Why Fas D matters

Per [v3.7 design doc Implementation Phases](lintel-v3.7-frontend-design-system.md#implementation-phases):

> **Fas D: Real-app dogfood (operator-only)**
> - Operator picks real engagement, runs `/li:frontend-design` end-to-end
> - Capture insights → L-004 if durable pattern emerges
> - Extract first non-canonical pattern via `/li:frontend-style-extract` → validates vault loop
> - L-001 canonical-pattern re-evaluation: demote till `docs/samples/` om operator-extracted dominerar

Two specific outcomes Fas D validates:

1. **The vault-loop works.** Extract a pattern from a real artifact, use it via `/li:frontend-design --pattern <name>`, observe whether the output matches operator's intuition.
2. **L-001 canonical re-evaluation.** If operator-extracted patterns > 3 and they dominate over `ultra-modern-lovable-style` in actual use, demote the canonical to `docs/samples/`. If canonical stays the most-reused, keep as bundled seed.

---

## Synthetic pre-validation (AI-actionable, done 2026-05-29)

### Validation 1 — schema flexibility under non-Lovable contexts

The canonical pattern (`ultra-modern-lovable-style`) is editorial-grade modern + GSAP + Lovable-feel. Concern: schemas may have implicit assumptions that break for other aesthetics.

**Synthetic check:** walk through a hypothetical `minimal-techy-portfolio` invocation (no actual file emit per L-001 — extras canonical patterns risk doubling content rot):

- typography role=mono dominant (JetBrains Mono everywhere). Schema requires 3 stacks (heading, body, mono). Setting all 3 to mono-variants works — schema doesn't reject.
- motion `energy_level: subtle`, libraries `["motion-one"]`, no GSAP. Schema requires `key_animations[]` minimum 1. Filling with a single 50ms-fade satisfies.
- shader `null` is documented in canonical schema. Schema flexes.
- component_libraries can be `[{"name": "park-ui", "kind": "primitive"}]` with no Aceternity. Schema flexes.
- layout_grammar `grid: "freeform"` not in the canonical's `["12-col", "8-col", "bento"]` set. **FINDING:** the layout_grammar.grid enum is implicit, not documented. Consider explicit enum OR allow free string. **Recommendation:** allow free string (operator extracts may surface novel grids). Update `seeds/brand/design-patterns/ultra-modern-lovable-style/pattern.json` docs (next Fas D2 PR if dogfood confirms).

**Verdict:** schema flexes for non-Lovable aesthetics. One soft-finding on layout_grammar.grid (defer until operator-dogfood confirms).

### Validation 2 — vault collision-handling

`frontend-style-extract` documents `--overwrite` flag inheritance from `generate-style-learn` (m-3 resolution from PR #23). Synthetic test of collision-path:

```
operator runs: /li:frontend-style-extract ./linear-clone --name minimal-techy
  → ~/.lintel/brand/design-patterns/minimal-techy/ created
operator re-runs same command → exit code 3, message "Pattern minimal-techy already exists at $out_dir."
operator runs with --overwrite → replaces + logs previous_pattern_hash to audit
```

This is documented behavior per skill body. Synthetic-verified by reading frontend-style-extract SKILL.md Step 1.

### Validation 3 — hook firing on different file extensions

`frontend-design-surface` hook fires on `.tsx|.jsx|.svelte|.vue|.css|.scss`. Throttle is per-file-per-session.

Synthetic test (run via `tests/unit/frontend-design-surface-hook.sh`):
- `.tsx` triggers surface ✓
- `.svelte` triggers ✓
- `.vue` triggers ✓
- `.css` triggers ✓
- `.md` silent ✓
- Throttle prevents double-surface ✓

**Verdict:** hook behavior validated. Real-dogfood will stress-test the vault-matching logic (currently MVP keyword-grep on `component-imports.json`; brief-hash matching deferred to Fas C+1).

### Validation 4 — generate-web `--from-frontend-design` schema handshake

Per PR #24 (Fas B), generate-web's `--from-frontend-design` mode reads `frontend-design-spec.json` (not the pipeline's `design-spec.json`) and verifies `source: "frontend-design"` + `schema_version: 1` before consuming.

Synthetic test (run via `tests/integration/frontend-design-roundtrip.sh`):
- Mock spec with correct schema_version + source: validates ✓
- Mock spec missing schema_version: skill body documents handshake check
- Mock spec with wrong source: skill body documents discriminator check

**Verdict:** schema-version handshake documented + tested. Real-dogfood will validate end-to-end HTML emission (currently asserted only at schema-shape level).

---

## Real-engagement dogfood checklist (operator-pending)

When operator picks a real customer engagement (or strong synthetic substitute), run this checklist:

### Pre-dogfood

- [ ] Pick target site/repo. Either:
  - (a) Real customer engagement (per operator schedule)
  - (b) Strong synthetic substitute — a public site operator wants to learn from (Linear, Vercel, Aceternity templates etc — extract pattern from public live URL)
- [ ] Set mode: `/li:profile-switch --mode customer-engagement` if real (gets 500k cap); else `internal-tool`
- [ ] Confirm `~/.lintel/brand/design-patterns/ultra-modern-lovable-style/` is intact (install.sh seeded it)

### Step 1 — Extract pattern (validates vault entry path)

```bash
/li:frontend-style-extract <artifact-or-URL> --name <descriptive-name>
```

Expected:
- `~/.lintel/brand/design-patterns/<name>/` populated with pattern.json + typography.json + motion.json + component-imports.json + shader-snippets/
- extraction_confidence field reported (low/medium/high)
- audit-log entry in `~/.lintel/audit/frontend-style-extract-runs.jsonl`

**Capture findings:**
- Did the schema accommodate the source's design language?
- Any soft-findings (like the layout_grammar.grid enum)?
- extraction_confidence — did it match operator's intuition?

### Step 2 — Use pattern in fresh design (validates orchestrator path)

```bash
/li:frontend-design "<fresh brief — e.g., 'AI app for legal professionals'>" --pattern <name>
```

Expected:
- `~/.lintel/frontend-runs/<run-id>/typography.json` + motion.json + frontend-design-spec.json emitted
- Parallel sub-skill dispatch documented in orchestrator's audit log
- visual_thesis synthesizes brief + chosen pattern coherently

**Capture findings:**
- Did the agent take liberties with pattern OR strictly inherit?
- Did parallel typography+motion+shader dispatch actually run concurrently (timing log)?
- Frontend-design-spec.json structure — any missing fields operator wanted?

### Step 3 — Render via generate-web (validates rendering-engine handshake)

```bash
/li:generate-web --from-frontend-design ~/.lintel/frontend-runs/<run-id>/
```

Expected:
- HTML emitted that references typography (font @import / preload), motion (gsap/lenis imports), component-library (shadcn init lines)
- WebExperienceCritic agent reviews emitted HTML
- prefers-reduced-motion fallback present per motion.perf_budget

**Capture findings:**
- Did the emitted HTML actually use the pattern's choices? (font family, motion library, shadcn primitives)
- L-002 boundary respected? (no design-decisions snuck into generate-web)

### Step 4 — Review with DesignSystemAuditor (validates 6-dimension audit)

```bash
/li:frontend-design-review ~/.lintel/frontend-runs/<run-id>/
```

Expected:
- 6-dimension scored audit (typography hierarchy, motion coherence, shader perf-budget, accessibility WCAG AA, brand conformance, responsive fidelity)
- Per-dimension verdict (green ≥80, yellow 60–79, red <60)
- Overall verdict aggregating per-dimension

**Capture findings:**
- Was the scoring rubric actionable?
- Any dimensions where the rubric proved miscalibrated?

### Step 5 — Hook surfacing (validates passive mode)

Open one of the produced .tsx files in another worktree. Expected:

- frontend-design-surface hook fires with: `INFO [Lintel]: design-patterns relevant to ...: <name>. Reuse: /li:frontend-design --pattern <name>`
- Throttle prevents double-surface on same file in same session

### Step 6 — Capture insights → L-004 enrichment

If a durable pattern emerges (something the operator will want to remember across sessions):

- Update `tasks/lessons.md` L-004 entry with the specific insight
- If it transcends frontend-* family: graduate to LAYERS.md durable principle
- If just a fix: log to repo issues / next PR

### Step 7 — Canonical pattern re-evaluation

Count `~/.lintel/brand/design-patterns/` entries. If operator-extracted patterns > 3 AND operator reuses them more than the bundled `ultra-modern-lovable-style`:

- File a `v3.7-canonical-demotion` PR moving `seeds/brand/design-patterns/ultra-modern-lovable-style/` → `docs/samples/ultra-modern-lovable-style/`
- Update install.sh to stop seeding (it becomes documentation)
- Update memory.md v3.7-close entry

If canonical stays the most-reused: KEEP. Re-evaluate quarterly.

---

## Findings from synthetic pre-validation (open for Fas D real-run to confirm/deny)

1. **layout_grammar.grid enum is implicit** — schema accepts free string but canonical pattern uses `"12-col"`. Operators extracting may use `"freeform"` / `"bento"` / `"asymmetric"`. Recommendation: document the field as free-string explicitly in canonical pattern.json (deferred until operator-dogfood confirms friction).

2. **extraction_confidence rubric not specified** — `frontend-style-extract` emits `extraction_confidence: high|medium|low` but the rubric (when is something low vs medium vs high) is implicit. Recommendation: add to skill body if real-dogfood shows operator uncertain how to interpret.

3. **Brief-hash matching for hook is MVP** — currently keyword-grep on component-imports.json. Real-dogfood with vault > 3 patterns will reveal whether MVP is adequate or vault-index.json optimization needed sooner.

---

## What's still genuinely operator-only

After this synthetic pre-validation:

- **Real customer voice judgment** — only operator can score whether typography/motion choices match customer brand intuition (T0 calibration territory)
- **The "feel" verdict** — does the produced site feel right? Subjective; needs operator
- **L-004 canonical demotion** — depends on actual usage stats, not synthetic

Everything else has been pre-validated. Real-dogfood is now a 15-30 min operator session, not a multi-hour evaluation.
