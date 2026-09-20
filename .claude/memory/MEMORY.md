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
- **Universal implementation ACTIVE (2026-09-20):** [work map](../plans/universal-implementation/work.json) and [handoff](../plans/universal-implementation/handoff.md) own all A01-A26. P01-P03 and owned P04-P07 are accepted and integrated, including P05 Q01 and the P07 long-path repair. P08 is ready; P10 is active. Installation remains without Python (ADR-0030/L-035); existing PowerShell 7 is explicitly approved for local tests, not policy override. A22.7, P08-P14 and final delivery remain open; only `jokerman89` may authenticate.
- **Universal audit COMPLETE (2026-09-20):** all126 skills/69 agents reviewed; [26 proposed actions](../engineering/audits/2026-09-20-universal-quality/action-plan.md). Preserve valuable capabilities and all Swarming work as far as feasible (L-030–L-032). Audit is local in the isolated review worktree; product fixes/merge are pending separately.
- **Copilot enterprise launch COMPLETE (2026-09-08, PR #83 merged):** native portable kit, explicit Spec Kit work map, complete shared startup protocol and 101/101 hosted tests on Ubuntu/macOS/Windows. Delivery evidence and beta acceptance boundaries: [launch plan](../plans/copilot-enterprise-launch/plan.md) and [review](../plans/copilot-enterprise-launch/review.md). Completed plans and older publication/history notes are records, not live instructions or standing authorization.
- v5.x history: launch-readiness folded into PR #73; v5.0 chain #62→#65 merged. Audit records now at `.claude/engineering/audits/`.
- Conventions in force: supersede-don't-delete (`superseded_by:`), update-before-append (CAPTURE/learn), L-NNN grammar only, MEMORY.md ≤200 lines.
- Helpers: lib/paths.sh (all paths), lib/memory.sh (lessons), bin/_context.sh (checkpoints), bin/li-migrate-claude-home, bin/li-vault-init.
