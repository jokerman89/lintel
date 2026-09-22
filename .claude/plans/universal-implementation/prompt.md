# MasterSession continuation

Read [spec.md](spec.md), [plan.md](plan.md) and [handoff.md](handoff.md).
Select [work.json](work.json); plan.md alone owns implementation checkbox state.
The 2026-09-20 operator authorized execution of all audited A01-A26 outcomes, not just
another audit. Preserve all useful methods, entry points and Swarming history.
The 2026-09-21 continuation authorizes final reviewed PR delivery/merge to main and
scoped cleanup for this initiative, not unrelated work or relaxed acceptance gates.
The full cycle remains SENSE -> SCOPE -> DEFINE -> DISCOVER -> PLAN -> BUILD ->
REVIEW -> SHIP -> CAPTURE. Resume is a utility that returns to that cycle, not a
phase or a replacement lifecycle. Preserve documented presets and entry points.

Follow AGENTS.md, AGENT-INSTRUCTIONS.md, the Copilot adapter when on Copilot,
accepted ADRs, and memory lessons L-030 through L-032. Original audit evidence is
committed under `.claude/engineering/audits/2026-09-20-universal-quality/`.
The original source audit and Swarming worktrees must not be overwritten or reset.

MasterSession owns the plan, dependency decisions, shared schemas' assignment, common
state, integration and generated outputs. Use app-native isolated child worktrees for
writers; name one accountable owner and a separate read-only reviewer per package.
Overlapping paths are sequential even when worktrees would permit textual conflicts.
Do not use unrepaired Swarming machinery as a scheduling mechanism.

Dispatch contract: package goal; source A-/finding IDs and paths; required predecessor
revision; owned paths and exclusions; preserved use cases; exact observable acceptance;
negative and regression scenarios; report path; local commit/patch and verification
requirements. A worker does not mark shared tasks done or publish remotely. Reviewers
report findings and severity with file/line/evidence; they do not implement repairs.

Integrate P04's real merge first to retain Git ancestry. Other workers' independently
reviewed commits then join in dependency order. Verify scope before fan-in. Regenerate
protocol, catalog, adapters and other shared outputs only from their combined sources.
After a correction, re-review affected content; do not reuse a PASS for another tree.

Do not claim all 26 actions done from a subset of passing tests. Each item needs both its
audited acceptance and evidence of retained value. A24 is actual scenario evidence, not
manufactured productivity metrics. No client lacking a real run becomes "verified".

Use only the explicitly authorized `jokerman89` GitHub account. The injected credentials
were rejected earlier; do not use them for reads, pushes or PR tools. The operator's
new login was verified through an explicitly account-selected CLI credential and
`/user` on 2026-09-21. Verify the actor for the actual publishing path, then deliver
through the feature PR with review/CI and preserved ancestry. Merge authorization is
only for this accepted initiative batch. Clean only verified completed owned artifacts/
workspaces after preserving commits, reports and history; retain unrelated/unmerged work.
No release/tag, production/deployment mutation, private synchronization or dormant
hook activation is authorized. A morning target is not evidence of completion.

Before yielding, update the handoff, plan review section and durable working state with
exact commits, active child IDs, verification status and the next dependency-ready package.
