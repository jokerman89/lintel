# Handoff: Copilot enterprise launch

Read [spec.md](spec.md) and [plan.md](plan.md), then inspect current Git status and build-card
checkboxes before resuming. The user requested a whole-repo review, Copilot-first implementation,
enterprise-facing documentation, plan/spec/build-card execution and integration to main.

Use the existing `codex/copilot-enterprise-launch` branch until final integration. Preserve
pre-existing commits 017dc24 and 6b10a84 and unrelated local settings. Follow canonical Lintel
instructions, but the user's explicit execution/main authorization already satisfies approval
within this scope. No force pushes, production policy changes or release publication are requested.

Canonical source remains in skills/, agents/, bin/, lib/, scaffolding/. The Copilot adapter has
an explicit file inventory and portable consumer runtime; see ADR-0024. Do not blindly copy
Claude tool names or hook schemas to Copilot. Research current primary GitHub and VS Code docs
when a host capability is uncertain. Spec Kit projects retain their own authoritative artifacts.

Run Git Bash as `C:/Program Files/Git/bin/bash.exe -lc` on this Windows workspace. Read the
release audit for environment/tool prerequisites. Do not trust a partial or all-skipped test run.
Review spec compliance then quality; repair findings, regenerate derived artifacts and run the
full suite before commits/integration. Keep evidence and live-model limitations in the plan review.

The operator also required the complete reusable engineering startup protocol at project level.
Its source is `scaffolding/01-foundation/SESSION-PROTOCOL.md`; ADR-0025 and the coverage audit
explain the no-loss mapping. AGENTS.md, CLAUDE.md and both templates contain generated inline
copies. Preserve project-specific surrounding prose and do not copy private machine state.

Use [work.json](work.json) as the explicit artifact map and [review.md](review.md) for actual
verification evidence. When the map is COMPLETE and main integration is recorded, this handoff
is a historical completion record: do not repeat the build or treat old batch authorization
as permission for new pushes, releases or data transfers. Any unexecuted client/tenant acceptance
must be handled with the current operator's environment and authority.
