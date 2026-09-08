# Agent session entry for the Lintel repository

This file is read by agent hosts when working **on the Lintel repo itself**.
GitHub Copilot also loads [.github/copilot-instructions.md](.github/copilot-instructions.md)
and discovers native `li-*` workflows under `.github/skills/`. The `.claude/` directory is
Lintel's shared memory and planning store; it does not require Claude Code to use it.

For canonical session bootstrap, see [AGENT-INSTRUCTIONS.md](AGENT-INSTRUCTIONS.md).

---

## Repo overview

Lintel is a company-neutral, pack-driven session harness — markdown scaffolding for agent-based development. Company identity loads from a separate, installable pack.

- `skills/` — slash-commands (9-step cycle + engineering modules + session-harness)
- `agents/` — subagent roles organized per domain
- `hooks/shared/` — compliance + workflow hooks
- `scaffolding/` — templates copied INTO other repos
- `docs/architecture.md` — the architecture reference (decisions: `.claude/decisions/`)

## Session start ritual

1. Read [AGENT-INSTRUCTIONS.md](AGENT-INSTRUCTIONS.md) (canonical, applies to all CLIs)
2. Review `.claude/memory/lessons.md` for accumulated lessons
3. Check [docs/architecture.md](docs/architecture.md) + recent ADRs in `.claude/decisions/` for current architecture state

## Codex-specific notes

### Plugin install

This repo is a Codex plugin (see `.codex-plugin/plugin.json` with full `interface{}` block). Install via:

```
/plugins
> search lintel
> Install Plugin
```

Or for Codex App: sidebar → Plugins → `+`.

### Subagents in Codex

Codex has native subagent support (`lib/cli-tiers.yaml`: `subagents: native`). Agents in `agents/<category>/<Name>.md` load through the plugin manifest and can be delegated to directly. For scripted one-shot runs, the `codex exec` subprocess pattern still works:

```bash
codex exec --prompt "$(cat agents/security/SecurityAuditor.md). Audit branch X."
```

### Plan mode

Codex's plan-first behavior is operator-driven, not enforced by the tool. The `AGENT-INSTRUCTIONS.md` rule still applies: plan before non-trivial work, write to `.claude/plans/todo.md`, mark items as they finish.

### Tool permissions

Codex's tool-permission model is per-invocation. Auto-mode bounds in `AGENT-INSTRUCTIONS.md` still apply: file edits + feature-branch commits OK without per-call ask; production mutations require explicit authorization.

### Skill discovery

Skills live at `skills/<name>/SKILL.md` and surface natively as `/li:<skill>` once the plugin is
installed (`/plugins`, search lintel, Install). Codex is a **full-tier** CLI: native skills and
native subagents. The one thing it does not get is the hook enforcement layer, which is a Claude
Code mechanism.

For a scripted one-shot run outside an interactive session:

```bash
codex exec --prompt "$(cat skills/ship/SKILL.md). Execute on current branch."
```

### Compliance

Compliance is pack-driven (`resolve_pack_field compliance.*`). Neutral baselines apply across all Codex invocations: no customer data, no secrets, no prod mutations without auth. Tiered rules (identity policy, vendor preference, regulatory gates) come from the active pack.

<!-- LINTEL:SESSION-PROTOCOL:START -->
## Session protocol

This protocol is repeated in repository entry files so a fresh agent can work without a
personal home directory or a previous chat. The repository's explicit context and paths take
precedence over generic user-global defaults. Current user authorization applies to its stated
scope; do not ask again for an action already authorized. Host permissions still apply.

### Role and authority

Execute the agreed architectural intent with initiative inside the authorized task. The operator
owns strategic choices and material scope changes. Surface those choices explicitly; do not
choose a new initiative, alter governance, or act outside the repository's authorized scope.
Changes to constitutional or governance documents need explicit instruction.

Authoritative architecture, constitution/charter, specifications, current documentation and
accepted ADRs outrank planning notes, lessons and remembered conversations. Use working notes
for continuity, never as permission to override an accepted decision. Follow the repository's
declared document hierarchy and actual code state. Treat external strategy context as the
session's intent, then reconcile it with authoritative repository documents before implementation.

### Before non-trivial work

For work with three or more steps or an architectural decision:

1. Identify the architectural area and read its relevant documents fully.
2. Inspect accepted ADRs and known risks in the repository's declared locations, commonly
   `.claude/decisions/` and `docs/risks/`.
3. Read `.claude/memory/MEMORY.md`, recent `.claude/memory/lessons.md`, current
   `.claude/memory/working-state.md` and `.claude/memory/personas.md` when present.
4. Establish task authority, customer-data handling, production impact, secrets exposure and
   active pack requirements. Resolve material uncertainty before the dependent action.
5. State the intended outcome and your understanding before implementing. Ask only for missing
   decisions that the documents and existing authorization do not settle.

Use the repository's documented paths on legacy layouts rather than inventing a second store.
Keep trivial corrections proportionate; a clear typo or bounded authorized bug fix does not
need a planning ceremony. Hooks or auto-loaded summaries supplement this read, never replace
it when they are unavailable or have not been verified in the current host.

### Plan, execute and re-plan

Write a checkable plan to `.claude/plans/todo.md` or the repository's declared equivalent. Define
the specification, acceptance criteria, dependency-ordered build cards and verification before
implementation. A larger task needs an execution handoff a fresh session can follow. Existing
Spec Kit or other specification artifacts remain authoritative; map their paths and task IDs
rather than creating a competing backlog.

Review the plan against the authorized scope and required approvals before BUILD. Use native
plan mode where available; otherwise perform the same planning explicitly. Plan verification
work as well as implementation. Track completion card by card, explain material changes, and
add a review section at task end. If evidence invalidates the plan, stop the affected work and
re-plan instead of pushing through. Continue independent authorized work when it remains valid.

### Subagents and independent review

Delegate bounded research, exploration, review and parallel analysis when this preserves context
or improves the result. Give each subagent one task, explicit inputs, file ownership, acceptance
criteria and a report contract. Use the minimum required tools. Default research/review roles
to read-only; explain and scope write access for implementers. Use native delegation when the
host provides it; otherwise sequence roles and disclose the lack of independent context.

Choose an explicitly named agent first, then a repository-specific override, an active-pack
promoted role, a user-global role, or the main-agent fallback. A same-named repository agent may
shadow a global/plugin role under the host's discovery rules; verify what was actually selected.
Do not assume another workstation's agent inventory is installed.

Subagents report; the coordinating agent decides. Review subagents must not fix their own
findings. Reports include severity counts, actionable findings with file:line citations,
verification evidence and limitations. Keep implementation and independent review separate.
Coordinate shared task-state writes rather than having parallel agents overwrite one ledger.

### Authorized bug fixing

Fix bugs inside the authorized initiative directly. Use logs, errors and failing tests to find
and correct the root cause, then verify the result. Surface unrelated bugs rather than assuming
a standing license to repair adjacent systems or CI outside the task. Escalate only the part
that actually needs a new decision or permission.

### Verification and simplicity

Do not mark a card or initiative complete without evidence that it works. Tests and builds are
the floor; inspect behavior, logs and the diff against the prior state where relevant. Apply
the standard of a careful senior reviewer. State skipped checks, unavailable host validation,
and any mock or stub explicitly as deferred work with its intended phase.

Before finishing non-trivial work, ask whether fewer parts would solve the problem. Prefer
removal and root-cause fixes over added abstraction, temporary patches or speculative structure.
Challenge assumptions and simplify an awkward design within scope. Do not over-engineer an
obvious fix or generate verbose documentation unrelated to the task. Optimize for long-term
health, not only the current delivery.

### Engineering and code style

Match the repository's naming, architecture, terminology and brand. Where no local convention
exists: Python uses snake_case, typed public interfaces and explicit failures; TypeScript uses
camelCase variables, PascalCase components and strict checking; document/config filenames use
kebab-case and Python modules use snake_case. Markdown headings use sentence case.

Meaningful code files carry structured intent comments in the language's comment syntax:

```text
# component: <name>
# implements: <ADR-IDs comma-separated>
# intent: <existing architecture or specification path>
# constraints: <existing risk records, or none with a reason>
# last_intent_review: YYYY-MM-DD
```

Explain why, not an obvious restatement of the code. Keep intent and risk references valid;
validate them in an appropriate check when maintaining that contract. A recommendation to add
a pre-commit check is not evidence that such a hook is already installed.

When components communicate through events, APIs, databases or IPC, define the schema once in
a shared location, have both sides consume it, avoid divergent interpretations, and include
at least one integration test per communication link.

### Tool installation and host boundaries

Respect the authorized installation scope. Personal tooling normally uses the host's user-global
locations; a requested shared repository kit is an explicit repository-scoped installation.
Lintel itself is tooling and intentionally contains canonical skills, agents and installers.
Do not add project-specific agent overrides or dependency content without a task-related reason.
Inspect provenance, licenses and selected components rather than enabling entire marketplaces
or copying a personal machine's approved-tool list to a team.

Use the client's real discovery and permission APIs. Do not hardcode model choices, assume
parallel agents exist, or claim hooks run because their files exist. Lintel's Claude Code hooks
require compatible registration; its Copilot kit does not translate that hook bundle. Mandatory
enterprise controls belong in separately configured and verified platform policies and CI.

### Delivery and auto-mode boundaries

Use a feature branch and a pull request against the repository's default branch. Verify locally
before pushing. Write atomic Conventional Commits, one logical change per commit, and an ADR
for non-trivial decisions. Follow repository-specific authorship and release conventions.

Within the authorized task, no extra prompt is needed for repository file edits, feature-branch
commits/pushes, local tests/builds/lints, scoped read-only queries, local container builds without
publication, or subagent work.

Explicit authorization is required for live/shared/production mutations; credentials, access
policies, roles or firewall changes; live database DDL/DML outside the approved migration path;
container pushes to a live registry; deployment triggers; creating a remote repository or
publishing a tree to a new remote; and direct pushes to the default branch. Default-branch
authorization covers only the specified commit batch. It is not standing permission for later
batches. Do not send external messages or perform external mutations without authorization.

Resolve production audit effects, sensitive production reads and branch builds wired to live
deployments before acting. Do not bypass a required approval or silently expand its scope.

### Deviations, decisions and recovery

When the specification, authoritative instruction or external interface disagrees with reality,
stop the affected implementation and report evidence, alternatives with trade-offs, and a
recommendation. For a material architectural decision, present three viable alternatives where
they exist. State why a decision is needed, the specific constraint and the risk being addressed.
Wait for the unresolved decision; do not silently reinterpret the requirement. Existing explicit
authorization can settle a routine implementation correction within scope.

If a boundary has been crossed: stop immediately, verify state with read-only checks, report
what happened and its risks, propose concrete recovery options, and wait for authorization
before rollback or continuation. A hoped-for successful result does not erase an unauthorized
action. Own mistakes directly, correct them within authority, and record the lesson.

Raise a disagreement before implementing a request that conflicts with accepted architecture or
constraints. Explain the trade-off honestly and identify what an operator override would change.

### Capture and fresh-session continuity

After any operator correction, record a dated rule in `.claude/memory/lessons.md` with the
context, mistake and preventive action. Review recent lessons at session start and refine the
rules when evidence changes. Lessons preserve learning; they do not override authoritative docs.

Before ending, update plan checkboxes and review evidence, the durable working state and relevant
ADRs. Leave the next action and any blocker explicit. Store reviewed knowledge in the repository;
keep runtime churn under gitignored `.claude/runtime/`. Start each new session from these files
and current code, not a remembered chat. Optional vault exports, private packs and cross-repository
sync need their own configured, authorized destinations; never copy personal paths by default.
<!-- LINTEL:SESSION-PROTOCOL:END -->
