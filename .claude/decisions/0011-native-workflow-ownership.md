# ADR-0011: Native workflow ownership

**Status:** Accepted (2026-06-12)
**Decided by:** operator — refactor every inherited pattern into something native, without losing capability
**Implements:** .claude/engineering/audits/2026-06-12-battletest-synthesis.md (native ownership section)

**Historical scope:** this records the accepted 2026-06-12 decision. Names and
external path descriptions were neutralized on 2026-09-25 without changing its
number, date, rationale or original counts. Its temporary heading/import migration
is not current clearance: ADR-0028 owns review evidence, ADR-0029 owns profiles,
and [ADR-0034](0034-native-workflow-consolidation.md) owns the current command surface.

## Context

The source inherited workflow patterns from an earlier external harness. The audit
counted 73 references across 38 files: attribution prose, live couplings to external
project roots, slug helpers and review-log locations, a provider-prefixed review
heading, and inherited prompt patterns (AUTO_DECIDE, founder framing, tier tracking).
Some couplings were silently broken for users without that external tool installed.

## Decision

Refactor inherited couplings into native Lintel mechanisms — never losing functionality, never
making anything worse, never renaming for its own sake. Three classes, five waves:

- **A — attribution (20):** rewrite each to state Lintel's own rationale (what the mechanism
  does + why), not its provenance. Provenance, where worth keeping, lives in this ADR.
- **B — live coupling (17):** replace external paths/binaries with native helpers —
  external project roots → `~/.lintel/projects`; external slug helper → `_context_repo_slug`
  (bin/_context.sh); checkpoint discovery → `context_latest`; external review log → a
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

- Users without the former external provider no longer hit those broken paths (Wave 2 repairs fixed already-broken
  behavior for fresh installs).
- The ship-gate accepts both review-report headings until 2026-09-12 (migration row added);
  legacy review history imported once so the 7-day window stays complete.
- The former provider was demoted to reference-only provenance, not an installation
  dependency. The unused external memory add-on was already removed (ADR-0009).
- Current native identity does not erase required legal notices or original observed
  provenance. Historical counts and migration outcomes above are not a claim that
  today's repository has no archival references.
