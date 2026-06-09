# Todo — cycle-position footer (v4.10, meta-infra)

**Initiative:** Every official-skill report ends with a dynamic "you are here → next is this →
say `go` / run `/li:<cmd>`" footer, so an operator entering the 9-step cycle at any point (start,
middle, end) always knows their position and the logical next action. Born from the `/li:cycle`
research-dive run (2026-06-09) that delivered a big report but never told the operator where they
stood or what to do next.

**Mode:** `meta-infra` (touches the spine: a new `lib/` helper + the output convention across the
9 phase skills + the `.lintel/state` read contract). Gates M1–M4 active. Soft cap 600k.

## Design decisions (recommended defaults — confirmable at the pre-BUILD gate)

- **D1 — Two renders.** Full block at phase boundaries / end of a report; compact one-liner for
  short single-answer replies. `render_cycle_footer [--compact]`.
- **D2 — Emoji stepper primary, ASCII fallback.** Matches `/li:welcome`'s visual language.
  `LINTEL_ASCII=1` (or `--ascii`) renders `[x] SENSE [~] SCOPE [>] DISCOVER [ ] PLAN` for terminals
  that mangle emoji — honest cross-platform (a convergent lesson from superpowers #275 / spec-kit #1946).
- **D3 — Every official-skill report, at the end.** Not every micro-message; the closing of a
  user-facing report. Phase skills always; other official skills (welcome/jobs/resume/status) in Phase 3.
- **D4 — Question-mode.** When a phase awaits operator input, footer flips to
  `▶ Awaiting your answer:` + how to reply, instead of a next-command. `render_cycle_footer --awaiting "<hint>"`.

## Plan

### Phase 1 — MVP, demoable on one surface
- [x] `lib/cycle-modes.sh` — canonical 9-phase order + mode→skipped map, defined once (shared by
      footer + cycle presets). `bash -n` clean.
- [x] `lib/cycle-footer.sh` — `render_cycle_footer`, 3 tiers (full/compact/**thin ambient**),
      auto-detect in-cycle vs ambient, `--ascii` fallback, `--awaiting` question-mode. Reads the
      `00-state.md` append-log (CRLF-safe, no jq).
- [x] `tests/unit/cycle-footer.sh` — 30 assertions, ALL PASS (tiers, skip precedence, positional
      done, ascii, state-parse, question-mode, complete→thin).
- [x] ADR `docs/adr/0003-cycle-position-footer.md`.
- [x] M1 structure-changes `docs/v4.x/structure-changes/2026-06-09-cycle-position-footer.md`.
- [x] Wire into `skills/cycle/SKILL.md` orchestrator (closing-step instruction at phase boundary).
- [x] **P0-1 folded in:** `skills/code-review/SKILL.md` `name: review` → `name: code-review`
      (restores it to the catalog). Name-uniqueness now clean across all skills.
- [x] M2 compat audit: YELLOW (2 affected = only the intentional code-review rename; Q4 helper
      changes = 0). M3 full suite: **66/66 PASS** (was 65; +1 = cycle-footer unit test).

## Review (Phase 1)

Shipped the cycle-position footer end-to-end on one surface. `render_cycle_footer` is one helper with
three auto-selected tiers — **full** (legend + 9-phase stepper + you-are-here/next/say-this), **compact**
(one-liner), and **thin ambient** (the lightweight line for normal Q&A outside the cycle, the mid-build
add). Mode-aware (skipped phases → `⊘`, positional done-state), ASCII fallback, question-mode, reads the
existing `00-state.md` append-log with no schema change. Mode→skip map extracted to `lib/cycle-modes.sh`
(shared schema — kills a latent duplication). 30-assertion unit test, full suite 66/66, meta-infra gates
M1/M2(YELLOW-benign)/M3 green. Folded in P0-1 (code-review name collision) since it was a 10-min win on
the same catalog surface. **Deferred to Phase 2/3** (tracked above): wire the 9 phase skills + presence
shape-test; extend to welcome/jobs/resume/status; orchestrator to write `cycle_mode:` into state.

### Phase 2 — wire the 9 phases  ✅ DONE
- [x] Appended a byte-identical "Cycle-position footer" closing section to all 9 phase skills
      (`sense scope define discover plan build review ship capture`). Orchestrator reconciled to
      NOT double-render (renders only at its own gates + completion).
- [x] `tests/shape/cycle-footer-present.sh` — asserts all 9 phase skills + the orchestrator reference
      the footer, and the helper + ADR exist. ALL PASS.

### Pre-existing fix folded in (authorized "do everything") ✅ DONE
- [x] **review-log gate fix:** `no-merge-without-review/run.sh` now reads `~/.lintel/audit/reviews.jsonl`
      (was the dead legacy path) and matches the **short** HEAD (was full). HOOK.md updated.
      `tests/integration/no-merge-without-review.sh` proves clear/warn/path-regression/non-merge. ALL PASS.
- [x] **orientator routing (P2-C) — DECISION: no change.** "review" intent stays routed to `/li:review`
      (Phase-6, the canonical cycle review). Rerouting PR-review phrasing to `/li:code-review` would
      surprise users who expect "review" → cycle REVIEW; the diff-scoped skill is a deliberate standalone.
      Reversible if PR-specific routing is later wanted. Documented, not changed.

### Phase 3 — polish + reach
- [ ] `--ascii` fallback (D2) + `--awaiting` question-mode (D4), with unit coverage.
- [ ] Extend to non-phase official skills: `welcome, jobs, resume, status`.
- [ ] M2 `bin/li-compat-audit` (expect GREEN/YELLOW — additive helper, no contract change) + M3 shape
      green + M4 capture/migration note.

## REVIEW round (independent CodeReviewer, verdict SHIP-WITH-FIXES → all fixed)
Adversarial review found 1 P0 + 4 P1 + 5 P2. Acted on all in-scope:
- [x] **P0-A** infinite-loop hang on a trailing value-flag (`shift 2` with no value) — guarded
      (`shift; [ $# -gt 0 ] && shift`). Regression-tested across all 5 value-flags (timeout guard).
- [x] **P1-A** unknown `--here` → silent all-pending footer → now a visible "position unresolved" line.
- [x] **P1-B** case-sensitivity (lowercase `phase:` in state broke the stepper) → tokens normalized
      to first-word UPPER-CASE (also fixes **P2-D** multi-word `--next`).
- [x] **P1-C** `code-review` rename was frontmatter-only → fixed body `/review` refs + log tag
      `"skill":"review"`→`"code-review"`. **Verified safe:** merge-hook keys on commit+`status:CLEARED`,
      NOT the skill tag; Phase-6 `/review` doesn't log — so no gate break, no live collision (reviewer
      slightly overstated the collision; the fix is still correct hygiene + future-proofing).
- [x] **P1-D** added 11 regression tests for the fail-open paths the ADR claimed but didn't test
      (hang, unknown here, lowercase state, garbage state, derive-next, multi-word next). 30→41 assertions.
- [x] **P2-A** "9-phase" vs orchestrator's "8-phase" drift → standardized on "9-step (8 core + SCOPE)".
- [x] **P2-E** known-but-non-terminal `here` with no `next` → derives next from canonical order
      (was mislabelling "cycle complete").
- _P2-B (CATALOG.md stale): self-heals on push via `.github/workflows/catalog.yml` — noted, no action._

## Surfaced — pre-existing, OUT OF THIS FEATURE'S AUTHORITY (operator decision)
- **review-log path mismatch (P1, real):** `hooks/shared/no-merge-without-review/run.sh:17` reads
  `~/.lintel/review-log/entries.jsonl`, but `bin/li-review-log` writes `~/.lintel/audit/reviews.jsonl`
  (line 24). The merge-gate likely never finds review entries → effectively dead. Not introduced here;
  flagging for a fix decision.
- **orientator "review" routing (P2-C):** `lib/orientator-routing.sh:49` maps the `review` intent
  ("review my PR") to `/li:review` (Phase-6), not the diff-scoped `/li:code-review` that PR-review
  arguably wants. Pre-existing; the rename is a natural moment to decide. Surfaced, not changed.

## Parked backlog (from the 2026-06-09 audit — tracked, not this build)
- **P0-1** `/li:code-review` dropped from CATALOG — `skills/code-review/SKILL.md:2` `name: review`
  collides with `skills/review`. Fix `name: code-review` + add a frontmatter-uniqueness assertion to
  `install/verify.sh`. *(10-min win — fold into Phase 1 if cheap.)*
- **Convergent #5** BUILD two-stage review must fail-closed on a no-op tree (superpowers #1701).
- **Convergent #6** add an `/analyze`-style DEFINE↔PLAN↔BUILD consistency gate (spec-kit's biggest steal).
- **Convergent #2** make `/li:lessons-surface` mandatory+automatic at SENSE (written-but-never-read).
- **P1-1/P1-2** frontmatter-contract drift in CLAUDE.md; `cli_support` 131-flat/38-structured split.
- **P1-3** empty `tests/e2e/` runs vacuously green; **P1-4/P1-5** backfill structure-changes + v4.x ADRs;
  **P1-6** reconcile stale five-lens checklist; **P1-7** orphaned `hooks/entropy-secret-check.sh`;
  **P1-8** 10 broken internal doc links.

## Cost estimate
- Phase 1: ~15–25k tokens (1 helper + 1 extract + 1 test + ADR + M1 + 1 wire).
- Full (P1–P3): ~40–60k tokens. Within meta-infra soft cap (600k).

## Review
_(to be filled at task end)_
