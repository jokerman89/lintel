# Memory index

Knowledge home for this repo (v5 layout, ADR-0005). Keep this file under 200
lines — it auto-loads at session start. Details live in the linked files;
read them on demand.

- [lessons.md](lessons.md) — durable rules from corrections (L-NNN). Read before acting.
- [working-state.md](working-state.md) — cross-session working state (what's in flight).
- [personas.md](personas.md) — operator calibration.
- [../decisions/](../decisions/) — decision records (ADRs).
- [../plans/todo.md](../plans/todo.md) — current plan.

## Hot notes
<!-- agent-maintained: short, load-bearing facts; consolidate or supersede instead of appending forever -->
- **v0.9.0-beta (2026-08-28): first public release prepared, NOT pushed.** Branch `feat/launch-readiness`, suite 90/90. Public docs 130→44 files; internal artifacts now under `.claude/engineering/`. All 255 commits rewritten (messages only — trees proven byte-identical). Pre-rewrite history in `../lintel-pre-beta-history.bundle`. **Four `v3.*-dev` tags still point at pre-rewrite commits — delete before pushing tags.** See [[working-state]] for the full blocker list.
- v5.x history: launch-readiness folded into PR #73; v5.0 chain #62→#65 merged. Audit records now at `.claude/engineering/audits/`.
- Conventions in force: supersede-don't-delete (`superseded_by:`), update-before-append (CAPTURE/learn), L-NNN grammar only, MEMORY.md ≤200 lines.
- Helpers: lib/paths.sh (all paths), lib/memory.sh (lessons), bin/_context.sh (checkpoints), bin/li-migrate-claude-home, bin/li-vault-init.
