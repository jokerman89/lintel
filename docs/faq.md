# Frequently asked questions

## What is Lintel?

A repository-based session workflow for AI coding agents: instructions, skills, specialist roles,
plans, lessons and decisions. The core workflow takes a request through scope, specification,
planning, implementation, review, delivery and capture. Local helpers support the workflow;
there is no hosted Lintel service. See [architecture](architecture.md).

## Is GitHub Copilot a first-class adoption route?

Yes. The [Copilot repository kit](copilot.md) supplies native `li-*` core workflow skills,
planner/builder/reviewer profiles and portable resources. Start with [getting started](getting-started.md).
Client discovery and enterprise policies still need validation in your environment.

The CLI plugin is optional. Installing it locally does not provision a GitHub cloud agent or
other developers; commit the repository kit for shared adoption.

## Do I need Claude Code?

No. Copilot, Claude Code and Codex have different integration paths. The generated
[capability table](../README.md#multi-cli-support) and [multi-CLI guide](multi-cli.md) state what
Lintel's adapters provide. `.claude/` is the shared knowledge/state directory name, including
on Copilot; it does not require a Claude subscription.

## What does beta mean?

The current line is 0.9.0 beta. Interfaces, generated artifacts and pack schema may change before
1.0. Local tests cover structural and behavioral contracts; they do not prove every model follows
every instruction or every Copilot surface has passed a live pilot. Review
[release notes](../CHANGELOG.md) and [migration notes](migrations/_INDEX.md) on upgrade.

## What is a pack?

A separate set of organisation-owned context and policy settings: voice, roles, standards and
references. `_default` provides neutral advisory settings. A private company pack is optional;
its owner must arrange distribution to each execution environment. A local profile is not
inherited by a cloud agent. See [pack resolution](concepts/pack-resolver.md).

## Does it enforce our compliance policy?

A pack can tell workflow skills which checks to perform. Mandatory controls still need independent
implementation and verification. Lintel is not a certification or data-loss-prevention system.
Its pattern scanners have bounded coverage, and its local audit files are editable.
See [compliance](compliance.md) and [enterprise adoption](enterprise-adoption.md).

## Does Copilot get Lintel's safety hooks?

No. Copilot supports native hooks, but this release does not translate Lintel's Claude Code hooks
into Copilot's protocol. The repository kit installs no hooks. Use GitHub policies, CI and
organisation controls for checks that must hold independently of agent instructions.

The Claude Code plugin registers selected hooks; bare installs leave hook files inert until
configured. [Hook activation](getting-started.md#how-hook-activation-works) explains the boundary.

## Does Lintel send data anywhere?

There is no hosted Lintel collector. Your agent client, connected tools and invoked workflows
control external activity: browsing, dependency downloads, Git operations and optional sync/export
can use external services. Review those permissions and your provider's data-handling policy.
Do not interpret a local-first installation as network isolation. See [SECURITY.md](../SECURITY.md).

## Can I put customer data in this repository?

No. This public repository is tooling. Keep customer artifacts in an approved, scoped environment;
sanitize reports, examples and lessons before sharing them upstream. Lintel's scanner is not a
complete classifier for sensitive data.

## Where does project knowledge live?

Committed `.claude/memory/`, `.claude/plans/` and `.claude/decisions/` keep the lessons, plan and
decisions with the project. Gitignored `.claude/runtime/` holds local session state. The Copilot
kit's managed resources live under `.github/`. See
[the path map](getting-started.md#where-things-live).

## Does it work with Spec Kit?

Yes, through an optional [workflow bridge](spec-kit.md). Keep existing `spec.md`, `plan.md` and
`tasks.md` authoritative, with one active executor. Lintel records the artifact mapping and session
handoff; it should not create a second competing task list or reinitialize an existing feature.

## How do I update or roll back?

For the Copilot kit, use an upgrade branch, run `li-copilot init` from the next approved source,
then `check` and your pilot checks. Locally edited managed files cause a conflict instead of silent
overwrite. Review the diff before merging. Roll back the adoption/upgrade with a reviewed Git
change, preserving project knowledge.

For plugins, use the installed client's plugin manager. For bare installations, review the
installer's machine-level paths and backups. There is no universal uninstall command. Never
remove whole `.github/`, `.claude/` or `~/.lintel/` directories without checking the project
knowledge, private packs and local edits they contain.

## Does it bundle third-party content?

Some design resources do. Their notices are retained in
[design-dna attribution](../skills/design-dna/ATTRIBUTION.md). Lintel's original code is MIT;
retained upstream license terms still apply. Spec Kit is not bundled by this workflow bridge.

## Which skills should I use first?

Start with `/li-welcome`, `/li-plan`, `/li-build`, `/li-review` and `/li-resume` in the portable
Copilot kit. Use `/li-cycle` for the broader workflow. Explore the
[full catalog](../skills/CATALOG.md) when you need specialist depth. A native `li-*` name differs
from the `/li:*` notation used by existing Claude plugin workflows.

## What if the agent ignores the instructions?

Verify the exact client/version, repository trust and customization policy. Check that the entry
file and referenced resources exist, then ask the agent to cite the instructions and active plan.
Check for conflicting repository or user-level instructions. If discovery or behavior still fails,
report a sanitized reproduction with the installation route and actual file path.

## Can two agents use the same repository?

The knowledge is shared files; Lintel does not mediate concurrent writes. Assign separate file
ownership, branches or worktrees. Keep one writer responsible for the active task list and session
ledger, especially when mixing Spec Kit and Lintel workflows.

## How do I customize or contribute?

Keep project-specific guidance in project-owned instruction files, and shared company context in
a private pack. Propose reusable fixes upstream through a pull request. Generated catalogs and
managed adapter files should be changed through their sources, not patched as final output.
[CONTRIBUTING.md](../CONTRIBUTING.md) covers contracts and verification.

Two lesson utilities have different purposes: `li-lessons-promote` promotes a lesson into the
scaffolding baseline; `li-lessons-sync` synchronizes an operator's lessons through a configured
private Git repository. Review the destinations before using either.
