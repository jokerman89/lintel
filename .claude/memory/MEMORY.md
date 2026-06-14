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
- v5.3 (2026-06-13): launch-readiness drive folded into PR #73 (feat/v5.3-cli-and-craft → main); suite 82/82. Public-launch items DATED in docs/audit/2026-06-12-launch-readiness-register.md §3-B. Repo migrated — knowledge here, runtime gitignored. v5.0 chain #62→#65 merged.
- Conventions in force: supersede-don't-delete (`superseded_by:`), update-before-append (CAPTURE/learn), L-NNN grammar only, MEMORY.md ≤200 lines.
- Helpers: lib/paths.sh (all paths), lib/memory.sh (lessons), bin/_context.sh (checkpoints), bin/li-migrate-claude-home, bin/li-vault-init.
