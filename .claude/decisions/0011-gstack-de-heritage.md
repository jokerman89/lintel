# ADR-0011: gstack de-heritage — grow fully into our own system

**Status:** Accepted (2026-06-12)
**Decided by:** operator ("gör en refactor på allt som är gstack … bli egna … aldrig sämre")
**Implements:** .claude/engineering/audits/2026-06-12-battletest-synthesis.md (gstack section)

## Context

Lintel grew out of the operator's prior harness "gstack" (GSD heritage). 73 references across
38 files remained: attribution prose ("adopted from gstack"), live couplings to gstack paths/
binaries (`~/.gstack/projects`, `gstack-slug`, `GSTACK_HOME`, a `## GSTACK REVIEW REPORT`
heading the ship-gate greps), and inherited prompt-patterns (AUTO_DECIDE, founder framing,
tier-tracking). Borrowed identity reads as unfinished; some couplings are silently broken for
any user without gstack installed.

## Decision

Refactor every gstack residue into native Lintel mechanism — never losing functionality, never
making anything worse, never renaming for its own sake. Three classes, five waves:

- **A — attribution (20):** rewrite each to state Lintel's own rationale (what the mechanism
  does + why), not its provenance. Provenance, where worth keeping, lives in this ADR.
- **B — live coupling (17):** replace gstack paths/binaries with native helpers —
  `~/.gstack/projects` → `~/.lintel/projects`; `gstack-slug` → `_context_repo_slug`
  (bin/_context.sh); checkpoint discovery → `context_latest`; `GSTACK_HOME` review log → a
  one-time import into `.claude/runtime/audit/reviews.jsonl`. Three carry loss-risk, each with
  a zero-loss mitigation: the `## REVIEW REPORT` heading rename **dual-accepts** the old heading
  through the 2026-09-12 grace window; the frontend-design-surface disable-file migrates once
  via li-doctor; the legacy review log imports once before removal. `maintenance` marker cleanup
  (B15) is functionality already lost (no hook ever cleaned `~/.lintel/sessions/`) — the refactor
  restores it.
- **C — prompt-patterns reinvented (3):** `--auto` becomes "auto-decide reversible gates, always
  ask one-way doors" on plan-tune's preference ledger (safer than blanket-YES); the dead
  operator-profile/tier-tracking remnant is removed (ADR-0006 already deleted the write);
  `plan-ceo-review`'s "founder signal" framing becomes operator-signal, pack-driven where a
  strategy role exists.

## Consequences

- No user without gstack hits a broken path again (Wave 2 repairs were fixing already-broken
  behavior for fresh installs).
- The ship-gate accepts both review-report headings until 2026-09-12 (migration row added);
  legacy review history imported once so the 7-day window stays complete.
- gstack demoted to reference-only in upstream-sources (install.sh is a list-only stub — no
  install path breaks). gbrain already pruned (ADR-0009).
- Identity is now wholly Lintel's; the only gstack mentions that remain are in this ADR, the
  CHANGELOG, and historical docs.
