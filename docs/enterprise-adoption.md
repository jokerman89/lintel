# Enterprise adoption

Use Lintel to standardize how a team starts, plans, builds, reviews and resumes work with
GitHub Copilot. The adoption unit is a reviewed repository change plus a team-owned operating
agreement. Start with a pilot; expand when the evidence meets your team's bar.

Lintel is a public beta maintained as an open-source project. It does not supply enterprise
support contracts, availability guarantees, regulatory certification or a hosted policy service.
It can help your existing platform team make engineering practice repeatable and inspectable.

## What your team adopts

| Component | Team value | Owner |
|---|---|---|
| Repository instructions and native skills | A common entry point and development workflow | Platform engineering with repository maintainers |
| Specification and build cards | Scope, acceptance criteria and progress visible in code review | Product/technical owner |
| Lessons and decisions | Context survives staff changes and new sessions | Repository maintainers |
| Private company pack | Reusable standards, terminology and policy references | Designated pack owner and policy reviewers |
| CI and repository policies | Controls independent of agent cooperation | Security/platform administrators |

The Copilot kit is a focused starting point. Specialist architecture, data, security, operations
and testing workflows can be introduced after the core workflow earns its place.

## Pilot one repository

Choose a non-production-impacting change with clear acceptance criteria. Use an approved Copilot
client, a reviewed Lintel commit, ordinary repository permissions and your existing CI.

1. **Record the baseline.** Capture how the team currently plans a comparable change, reviews it,
   verifies it and transfers work to another session. Decide which friction the pilot should reduce.
2. **Install on an adoption branch.** Follow [getting started](getting-started.md). Record the source
   commit, run `li-copilot check`, and inspect every generated instruction, agent and executable.
3. **Do a bounded task.** Discover the skills, write a specification and build cards, implement them,
   review against the specification, and capture a decision or lesson where warranted.
4. **Hand off cold.** Start a new session, ideally with another developer, and use `/li-resume`.
   It should identify the completed work, remaining cards and verification evidence from files.
5. **Review the evidence.** Compare against the agreed baseline and decide whether to adopt, adjust
   or remove the kit. Keep the decision in the repository.

## Acceptance criteria

Choose thresholds before the pilot. Suggested criteria are observable outcomes, not a promise
that adopting a harness creates a particular productivity gain.

| Check | Evidence to retain |
|---|---|
| Installation is reproducible | Approved Lintel commit; successful check; reviewed artifact inventory |
| Client discovers the workflow | Exact client/version and observed skill/agent names |
| Planning is useful | Specification, acceptance criteria, build cards and review comments |
| Execution matches scope | Completed card references, changed files and targeted test output |
| Review is independent when supported | Reviewer identity/context, actionable findings and resolutions |
| A fresh session resumes correctly | Handoff result citing the right plan, completed work and next action |
| Existing controls still hold | Required CI checks, review policy and authorization behavior verified by owners |
| The added process is proportionate | Time and interaction overhead compared with the agreed baseline |

Do not include customer information, secrets or raw sensitive prompts in a public issue. Keep
pilot transcripts and internal measurements under your organisation's data-handling rules.

## Keep policy ownership clear

A pack is the shared company context layer. Start with `_default`, then add the minimum policy
references and roles that your pilot actually needs. Keep private corpora and internal policy
content in a private pack repository. Review a pack update like a code change: source, owner,
license, affected workflows and rollback.

The active pack configuration in `~/.lintel/profile.yaml` is machine-local. A cloud agent or a
new teammate will not inherit it from another developer's workstation. Decide how approved pack
content and the active pack setting reach each execution environment, and verify that setup in
the pilot. Do not assume installing the repository kit distributes a private company pack.

`compliance.mode: hard` tells workflow skills to stop when the pack's declared gates fail; it is
not a host permission control. Data-residency metadata does not configure where a model runs.
Map policy requirements to platform settings, CI checks, or independently tested controls. Read
[compliance](compliance.md) and [security](../SECURITY.md) before relying on a mechanism.

## Review the data boundary

Lintel has no central service that receives sessions. Its scripts and generated resources run in
your chosen environment; your Copilot and tool configuration governs what is sent to external
services. Invoked workflows can ask an agent to browse, use tools, fetch dependencies or push
changes. Review those capabilities under existing organisation policies.

Committed plans, lessons and decisions travel with the repository. Runtime session data stays
under gitignored `.claude/runtime/`. Local audit records are editable by their owner; they are
operational evidence, not tamper-evident compliance records. Treat optional external exports,
private pack sources and synchronization as separate integrations with their own owners.

Lintel's Claude Code hooks are not adapted for Copilot in this release. Copilot rollout therefore
needs your existing merge protections, CI, access controls and secret scanning to carry the
mandatory controls. See the [Copilot guide](copilot.md#hooks-and-security-controls).

## Scale through reviewed changes

After the pilot, choose a small cohort with similar workflows. Give each repository a named owner,
an adoption PR and a reproducible source revision. Share pack standards across the cohort while
leaving project-specific build commands with each repository.

Avoid editing generated managed files independently in every project. Propose a shared source
change, or keep project-specific guidance outside the managed files. Review upgrade diffs before
merging; the installer refuses to overwrite local edits silently.

For upgrades, use an isolated branch, rerun installation from the approved version, run integrity
and project checks, and repeat the discovery/resume smoke test. Roll back through a reviewed Git
change. Preserve lessons and decisions produced by the project; remove only unchanged artifacts
introduced by the kit if you decide to stop using it.

## Release decision record

A concise adoption decision should name:

- Scope: repositories, client versions, environments and approved Lintel revision.
- Owners: rollout, repository maintenance, private pack, security controls and support escalation.
- Evidence: installation checks, pilot artifacts, verification and fresh-session handoff.
- Limits: untested surfaces, unsupported hooks, required manual review and known beta changes.
- Maintenance: next review date, upgrade policy and rollback procedure.

Use [GitHub issues](https://github.com/jokerman89/lintel/issues) for sanitized reproductions and
feature requests. Sensitive vulnerabilities follow [SECURITY.md](../SECURITY.md). Existing
Spec Kit teams can retain their artifact structure using the [workflow bridge](spec-kit.md).
