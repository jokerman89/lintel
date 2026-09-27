# Cold-executor prompt: reusable patterns

> **Implementation release (2026-09-28).** BUILD is authorized; see
> [implementation-release.md](implementation-release.md) and
> [reconciliation.md](reconciliation.md). The repository work map is
> `.claude/plans/reusable-patterns/work.json` (APPROVED). The frozen public interface is
> [contract.md](contract.md); lane ownership is in [topology.md](topology.md). Statements
> below about a planning-only delivery and deferred integration describe the original
> bundle and are superseded for this feature by the release.

Read [spec.md](spec.md) completely, then [plan.md](plan.md) and [review.md](review.md).
These files are self-contained; the prior chat and original proposal are not
required. [work.json](work.json) selects the authoritative artifacts in this bundle.

## Context

Lintel should discover applicable established expectations before generating work:
team deployment architecture, dashboard behavior, organizational visual design or
other recurring deliverables. Implement one local data-only pattern contract,
explicit target bindings and reviewed sharing across repo/pack/personal scopes.
Patterns complement accepted policy; they neither grant authority nor execute code.

This bundle was prepared against Lintel `00136c9d` on an isolated feature worktree.
Other sessions were not inspected or changed. It is a planning delivery, not a
partially implemented runtime. No build tests are claimed. The spec supplies exact
contracts, default choices, limitations and compatibility requirements.

## Authority and startup

1. Confirm the operator has authorized BUILD of this bundle. Its current DRAFT
   status is not execution authority; a new explicit implementation request is.
   Do not ask again if that current request already supplies the authority.
2. Read the working checkout's AGENTS.md, AGENT-INSTRUCTIONS.md, adapter, principles,
   relevant memory and accepted ADRs. The spec lists the architectural decisions
   read during planning. Resolve actual changes in the target checkout.
3. Work only in the authorized feature worktree. Do not list, message, switch,
   modify or interrupt other sessions. No personal pack activation, remote tenant
   scan, direct-main push, deployment or automatic merge.
4. The current bundle is session-scoped because the user requested scratch planning
   outside the repo. After BUILD is authorized, promote the complete reviewed bundle
   into `.claude/plans/reusable-patterns/` in the implementation checkout.
   Preserve any existing initiative at that path; a conflicting existing plan
   requires an explicit different initiative name or reconciliation, not overwrite.
5. Rewrite ONLY work.json's spec/plan/tasks/prompt values to repository-relative
   paths for that initiative. Keep the canonical existing work-map v1 shape.
   Set status APPROVED only with recorded current BUILD authority. Add one explicit
   link to the initiative in todo.md without replacing other initiatives.
6. Set `LINTEL_WORK_MAP` to this exact map. Validate using
   `python bin\li-work-artifacts.py --repo . --map .claude\plans\reusable-patterns\work.json`.
   In a downstream kit, use the installed source root's helper, not a guessed path.

## Execution

Use li-build for the authorized cards. Execute P0-P6 in order, retaining IDs and
dependencies. Each leaf has scoped files, requirement IDs, expected behavior and
a repeatable verification key. Create the named test classes as part of their
cards; they do not exist at planning time. If a leaf is too large, split with suffix
IDs and retain the requirement mapping instead of weakening acceptance.

One implementer owns a coherent package. Use independent lintel-reviewer for
substantive package spec and quality review. Reviewers report, implementer repairs.
Record test results per leaf in build-log.md; unrun tests are pending.

Do not copy profile/pack parsing into Python. Extend public pack origin/context
accessors with tests and preserve current semantics. Never treat existing
frontend-design-roundtrip.sh as rendered UI proof: it currently tests schema shape.

Use one canonical generic validator; Python stdlib suffices. Scripts receive roots
from the source/target-aware launcher. Tests supply hermetic home/runtime roots,
never modify a real user's packs or inspect other sessions' locks.

## Acceptance

- Metadata selection reads zero unrelated bodies/assets.
- Explicit required bindings survive ranking and budgets; unknown targets block
  only dependent work rather than triggering guessed architecture.
- Pack origin, lifecycle, pins and source failure are explicit and reproducible.
- Captures are drafts; approved content is immutable; import does not import trust.
- Cycle and direct invocation use the same helper and carry requirement evidence.
- Visual extraction and named legacy patterns remain compatible; Design DNA remains.
- Fresh source/target-separated kit works; tests are actually registered in runner.
- All R01-R16 have verified evidence; no skipped requirement masquerades as pass.

## Delivery and integration

Run targeted checks before strict full-suite validation. Host/model acceptance is
separate and requires appropriate permissions; record deferral if unavailable.
Stop short of claiming cross-host/enterprise enforcement without that evidence.

Before integration, compare the current target branch with the recorded base and
reconcile overlapping pack, paths, workflow, generator and frontend changes. Do not
inspect other sessions to do so. Never merge or publish automatically from this
handoff: the operator explicitly reserved integration for later.

Update only this initiative's status, review/evidence and durable pointers. Preserve
old pattern versions and legacy input files. No surprise migrations or cleanup of
other people's working state.
