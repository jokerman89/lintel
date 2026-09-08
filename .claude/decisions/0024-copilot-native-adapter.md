# ADR-0024: Native Copilot adapters over one canonical harness

- **Status:** Accepted
- **Date:** 2026-09-08
- **Scope:** Copilot enterprise launch

## Context

Copilot CLI, VS Code and GitHub cloud agent discover skills and custom agents in host-specific
locations. Lintel's current shim and metadata understate support, while its Claude tool/hook
formats cannot simply be relabeled. Consumers need a repeatable installation that survives a
fresh clone and respects existing customization.

## Decision

Keep canonical skill/agent/runtime definitions. Generate a small native Copilot entry surface
in `.github/skills` and `.github/agents`, with explicit tool/delegation and source-root guidance.
Use a deterministic `li-copilot init|check` adapter with a managed inventory. Consumer repositories
receive a committed `.github/lintel/` source bundle; Lintel itself uses the existing root source.
Use an explicit `.github/plugin/` manifest for CLI distribution and never import Claude hook JSON.
This is additive to the existing installer and scaffold; no global profile or organization policy
is changed. Spec Kit integration references existing artifacts instead of generating a second spec.

## Alternatives

Copying the existing shim alone leaves missing runtime dependencies and skill discovery unresolved.
Vendoring the whole Git repository duplicates history/private material and creates unnecessary churn.
Moving all durable state away from `.claude/` now would break the path contract and expand scope;
the directory remains historical storage shared by all hosts. ADR-0019's canonical-content move
and ADR-0021's broad model eval harness remain staged, not silently claimed as implemented.

## Consequences

Copilot onboarding becomes reviewable and deterministic, including updates and conflicts.
Generated files need a drift check in CI. Lintel's hooks remain Claude-specific even though
Copilot supports its own hook mechanism; enterprise enforcement belongs in host policy and CI.
Structural validation is distinct from live-model and tenant acceptance, which remain explicit
release evidence categories.

## Sources checked

- [GitHub CLI plugin reference](https://docs.github.com/en/copilot/reference/cli-plugin-reference)
- [GitHub agent skills](https://docs.github.com/en/copilot/concepts/agents/about-agent-skills)
- [VS Code agent skills](https://code.visualstudio.com/docs/agent-customization/agent-skills)
- [GitHub Spec Kit](https://github.com/github/spec-kit)
