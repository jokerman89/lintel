# ADR-0009: the subtraction release — same capability, 60% of the surface

**Status:** Accepted (2026-06-12)
**Decided by:** operator — approved the fit-audit P1 recommendation
**Implements:** .claude/engineering/audits/2026-06-12-fable5-fit-audit.md (P1 track)

## Context

The surface audit measured: 166 skills / 27k lines where 30-38% is per-skill template ceremony
(the same status enum, hop-in note, voice section restated 110-166 times); 35 engineering
sub-skills with exactly ONE caller each (~4.4k lines encoding a 35-row dispatch table as
files); a 0-reference tail (gbrain-setup/sync, WorkshopFacilitator); and a role family of 8
slash commands for CRUD. Surface area is cost: tokens at load, drift at every contract change,
discoverability noise. Lintel had no subtraction mechanism — it only grew.

## Decision

1. **Protocol stated once.** docs/concepts/skill-protocol.md defines the defaults (statuses,
   hop-in, voice, pause-points, failure recovery, compliance, state ledger). Skills carry
   these sections ONLY on deviation. The cycle spine (9 phases + cycle/resume/jobs/status/
   welcome/brief-forge/analyze) keeps its protocol inline — there it IS the contract.
   New optional frontmatter field: `hop_in: no` (only when not solo-invokable).
2. **Engineering sub-skills collapse into dispatch tables.** The 35 ta-/da-/sc-/dh-/tq-*
   sub-skill files fold into their module's SKILL.md as a dispatch table (capability | agents
   | output | raise-help). Invocation becomes `/li:ta api-design`; the old names alias to the
   module (grace to 2026-09-12). Nobody solo-invoked them — the reference graph proved it.
3. **0-ref pruning.** gbrain-setup + gbrain-sync removed (capability was honest-labeled
   "query loop not integrated"; nothing referenced them — the aliases pointing at them retire
   with a comment recording what they pointed at, the same way the WS-4b renames were handled). WorkshopFacilitator agent removed
   (zero dispatchers).
4. **Role family 8 → 3.** `role` (lifecycle: activate/deactivate/rotate/frame/deep-dive),
   `role-new` (creation + update), `roles-list` (discovery). Six aliases.
5. **Not touched in this release:** personas-rotate (overlap with role-rotate noted; decide
   with usage data), the context-warm-* variants (heavily referenced), Anti-patterns/
   Examples/Integration sections (content-bearing), agents/ (already disciplined).

## Consequences

- Target: ~27.0k → ~17k skill lines, 166 → 124 skills, same capability. Every removal has an
  alias or a successor; module contract tests assert the dispatch tables instead of the dirs.
- Token cost per skill invocation drops; the catalog gets honest; drift surface shrinks at
  every future contract change.
- Risk accepted: a future operator who DID want to solo-invoke a sub-skill types the old name
  and gets routed to the module with the capability as argument — one extra word.
- The diet is judgment-applied per file (keep deviations, strip restatements) — the protocol
  doc is the arbiter of "default".
