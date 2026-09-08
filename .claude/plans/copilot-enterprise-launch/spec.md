# Specification: Copilot enterprise launch

**Status:** APPROVED for implementation by the operator's 2026-09-08 instruction.
**Scope:** Lintel repository, GitHub Copilot CLI, VS Code agent mode and GitHub cloud agent.
**Design decision:** [ADR-0024](../../decisions/0024-copilot-native-adapter.md).

## Problem and outcome

Lintel exposes a mature Claude-oriented workflow but its Copilot onboarding, capability claims,
installation artifacts and enterprise documentation disagree with current host capabilities.
Deliver a reproducible, reviewable Copilot session experience and an honest public beta release
surface. Preserve working Claude Code behavior and the company-neutral pack contract.

## Requirements

| ID | Requirement | Acceptance evidence |
|---|---|---|
| R1 | Review the full repository by runtime, public surface and release quality | Three dated audits with findings and dispositions |
| R2 | Copilot discovers native skills and focused custom agents, with concise repository instructions | Generated .github artifacts and validated Copilot plugin manifest |
| R3 | Downstream repositories work after a fresh clone without an absolute path to the maintainer's machine | Self-contained committed source bundle and temporary-repo integration test |
| R4 | Installation is deterministic, repeatable, offline and preserves existing user content | init/check, inventory hashes, conflict and traversal/symlink regression coverage |
| R5 | Runtime capability and skill metadata are honest | Copilot subagents native; Lintel Claude hooks explicitly not ported; generated table in sync |
| R6 | Existing Spec Kit projects can use Lintel without duplicate authoritative specs | Explicit spec/plan/tasks ownership mapping and portable workflow entry |
| R7 | Enterprise evaluators can understand value, prerequisites, governance, rollout and limitations | Copilot-first README, quickstart, adoption and security docs; source citations |
| R8 | All required validation runs in CI and locally where available | Full structural/unit/integration/e2e/behavior suite plus installer and generated-artifact checks |
| R9 | Work is planned, built, reviewed, committed and integrated to main | Plan/spec/prompt trio, checked build cards, review evidence and Git refs |
| R10 | Preserve the personal engineering startup disciplines in self-contained project entry files, generated from one neutral source | Complete section coverage map, mirrored protocol parity and empty-home consumer test |

## Architecture and contracts

- Canonical skills, agents, Bash helpers, memory and pack schema stay in their existing roots.
- Copilot receives host-native .github/skills/li-*/SKILL.md and .github/agents/*.agent.md adapters.
- `bash bin/li-copilot init|check --target PATH [--source PATH]` materializes and verifies an
  owned inventory. Consumer source lives in `.github/lintel/`; this repository refers to its
  existing source tree. No symlinks, machine-global installation or network access is required.
- `li-scaffold init --copilot` composes the existing foundation with the adapter.
- Copilot plugin metadata selects adapter directories explicitly. Claude hook JSON is never
  treated as Copilot hook JSON. Repository settings, rulesets and CI remain the enforcement boundary.
- Spec Kit's own spec.md, plan.md, tasks.md and constitution remain authoritative when present.
  Lintel adds execution checkpoints, evidence and session memory by reference.

## Constraints and release boundary

The user authorized branch creation, implementation, commits and integration to main. Preserve the
two pre-existing local commits and the unrelated `.claude/settings.local.json` file. Do not force
push, change organization policies, create a release tag or claim marketplace acceptance.
The existing version remains 0.9.0 beta unless a separately justified versioning decision is made.
No paid live-model task, tenant policy check or GUI smoke result may be claimed from structural tests.

## Verification strategy

Exercise real generated files in a temporary consumer repo, repeat initialization, introduce drift
and conflicts, verify clean failures without partial writes, validate source-relative links, and
run the complete existing suite. Cross-review spec compliance before correctness/security quality.
Record local tool limitations and remote CI results separately. Known staged ADRs are not promises
that their full implementation ships in this initiative.
