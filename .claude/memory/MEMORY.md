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
- **Isolation incident (2026-09-21):** P08's unisolated cycle-continuity run is invalid evidence; possible real-home effects remain unknown. The operator approved only verified synthetic-path continuation, not real-home inspection/rollback. A13 remains independently gated; see L-037 and the active handoff.
- **Universal implementation ACTIVE (updated 2026-09-23):** [work map](../plans/universal-implementation/work.json) and [handoff](../plans/universal-implementation/handoff.md) own all A01-A26; recovery88 is the sole coordinator, 79/113 original acceptance items closed. P08 MAIN's local selected cycle is verified through CAPTURE; its original delivery-refusal pair and final selected-subset review remain. A24's three-profile native experiment is accepted through separate reviews, actual consumption/capture and final cross-profile verification. Broader A23/P14, P10 and recorded tool/format/CI boundaries stay open or blocked, not waived. Installation remains without Python; only `jokerman89` may authenticate.
- **Universal audit COMPLETE (2026-09-20):** all126 skills/69 agents reviewed; [26 proposed actions](../engineering/audits/2026-09-20-universal-quality/action-plan.md). Preserve valuable capabilities and all Swarming work as far as feasible (L-030–L-032). Audit is local in the isolated review worktree; product fixes/merge are pending separately.
- **Copilot enterprise launch COMPLETE (2026-09-08, PR #83 merged):** native portable kit, explicit Spec Kit work map, complete shared startup protocol and 101/101 hosted tests on Ubuntu/macOS/Windows. Delivery evidence and beta acceptance boundaries: [launch plan](../plans/copilot-enterprise-launch/plan.md) and [review](../plans/copilot-enterprise-launch/review.md). Completed plans and older publication/history notes are records, not live instructions or standing authorization.
- v5.x history: launch-readiness folded into PR #73; v5.0 chain #62→#65 merged. Audit records now at `.claude/engineering/audits/`.
- Conventions in force: supersede-don't-delete (`superseded_by:`), update-before-append (CAPTURE/learn), L-NNN grammar only, MEMORY.md ≤200 lines.
- Helpers: lib/paths.sh (all paths), lib/memory.sh (lessons), bin/_context.sh (checkpoints), bin/li-migrate-claude-home, bin/li-vault-init.
