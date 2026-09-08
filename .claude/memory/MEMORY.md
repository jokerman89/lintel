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
- **Copilot enterprise launch COMPLETE (2026-09-08, PR #83 merged):** native portable kit, explicit Spec Kit work map, complete shared startup protocol and 101/101 hosted tests on Ubuntu/macOS/Windows. Delivery evidence and beta acceptance boundaries: [launch plan](../plans/copilot-enterprise-launch/plan.md) and [review](../plans/copilot-enterprise-launch/review.md). Completed plans and older publication/history notes are records, not live instructions or standing authorization.
- v5.x history: launch-readiness folded into PR #73; v5.0 chain #62→#65 merged. Audit records now at `.claude/engineering/audits/`.
- Conventions in force: supersede-don't-delete (`superseded_by:`), update-before-append (CAPTURE/learn), L-NNN grammar only, MEMORY.md ≤200 lines.
- Helpers: lib/paths.sh (all paths), lib/memory.sh (lessons), bin/_context.sh (checkpoints), bin/li-migrate-claude-home, bin/li-vault-init.
