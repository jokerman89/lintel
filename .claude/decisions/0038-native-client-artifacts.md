# ADR-0038: Self-contained native client artifacts and host hook adapters

- **Status:** Accepted, 2026-09-28 (increment 1, GitHub Copilot). Increment 2 (Claude, Codex,
  Cursor) amends this record before it ships.
- **Date:** 2026-09-28
- **Deciders:** the operator ("implement this richly for these clients, go 100% support or as far
  as possible ... Start with Copilot, then get that to main first, then the rest"). Design:
  `.claude/plans/native-client-parity/design.md`. Independent design review: R1 (1 Critical,
  5 High, 4 Medium, all resolved) and R2.
- **Supersedes (in part):** ADR-0024, specifically these clauses:
  - "Generate a small native Copilot entry surface in `.github/skills` and `.github/agents`";
  - "never import Claude hook JSON" (it still holds: Copilot gets Copilot-format registrations);
  - "Lintel's hooks remain Claude-specific".

  The rest of ADR-0024 stays in force: canonical definitions, `li-copilot init|check` with a
  managed inventory, the committed `.github/lintel/` bundle, the explicit `.github/plugin/`
  manifest, and Spec Kit reuse.
- **Superseded by:** —

## Context

A `/li-cycle` session on Copilot (2026-09-25) read only 40% of the canonical cycle workflow and
skipped cycle identity, the phase chain and every gate. The generated Copilot skill was a
518-byte pointer, and the `view` tool refuses single reads over about 20 KB. Eight canonical skills
exceed that limit.

Live Copilot CLI probes on 2026-09-28 (1.0.87 and 1.0.89) showed several things:

- The native skill tool injects a whole 63 KB body.
- Plugin skills list by plain name.
- Plugin hooks receive `CLAUDE_PLUGIN_ROOT`, `CLAUDE_PLUGIN_DATA` and `CLAUDE_PROJECT_DIR`, and
  run with the plugin root as their working directory.
- Top-level `additionalContext`, `modifiedTransformedPrompt` and a JSON `permissionDecision: deny`
  take effect.

Spec Kit and gstack both ship complete generated skill bodies per host. Pointer adapters make each
session re-derive the method at runtime, and models do not reliably do that.

## Decision

We generate complete native artifacts from the unchanged canonical sources:

- **Skills:** one self-contained skill per canonical skill (`li-<name>`), with a short host
  preamble and deterministic transforms (invocation spelling, host tool names, link rebasing with
  the bundle's public-URL policy for unbundled targets).
- **Agents:** one native agent per canonical agent, keeping canonical names, with an allowlisted
  frontmatter, the same body transforms, and recorded degradations for dropped fields.
- **Hooks:** a host hook adapter (`hooks/adapters/`) that runs the unchanged canonical `run.sh`
  scripts behind each host's documented hook input and output.
  - On Copilot it registers camelCase events with runtime tool-name matchers and adds a
    PowerShell dialect to the git gate.
  - It emits Copilot top-level fields together with a `hookSpecificOutput` mirror.
  - It never exits non-zero after launch. Stop and prompt hooks never block.
- **Activation:** the Copilot plugin is the default and recommended route. Its hooks execute only
  the plugin's own tree (ADR-0008). Repository hook registration (`.github/hooks/lintel.json`) is an
  explicit `li-copilot init --hooks` opt-in, recorded in the kit inventory, because it executes
  repository-committed code, including in cloud-agent jobs.
- **Version:** every plugin-loaded change bumps all four manifests together (0.13.0 for this
  increment; L-020).

## Alternatives considered

- **Keep pointer wrappers with stronger prose.** Rejected: observed sessions do not follow it
  (L-016).
- **Trim canonical skills under 20 KB and keep pointers.** Rejected as the fix: the indirection
  remains and Claude behavior changes. It stays a possible later optimization.
- **Hand-port hooks per host** (PowerShell/Copilot-specific scripts). Rejected: duplicated security
  logic drifts. Instead, one adapter translates the host I/O around the canonical scripts.
- **Enable repository hooks by default.** Rejected at design review R1: it would execute
  repository-supplied code for every trusted session without an explicit decision.

## Consequences

- **Positive:**
  - Copilot sessions receive the same method text and guardrails as Claude Code.
  - Increment 2 adds host profiles, not new mechanisms.
  - Registry observations record what was actually verified per surface.
- **Negative:**
  - The repository carries about 1 MB of generated native files, and CI must drift-check them
    (`li-copilot.py check`).
  - Updating the plugin activates blocking hooks (a behavior change with a migration guide).
  - Windows pays a PowerShell plus Bash spawn per matched tool call.
- **Neutral:**
  - VS Code Local, the Copilot App and the cloud agent stay `conditional` until each is observed.
  - The Claude plugin layout is unchanged in increment 1.

## References

- ADR-0008 (activation contract), ADR-0013 (fail-closed block gates), ADR-0022/0023 (continuity
  hooks), ADR-0024 (partly superseded), ADR-0028 (evidence contract), ADR-0035 (four families).
- `.claude/plans/native-client-parity/` (design, discover report, research, plan trio).
- `.claude/engineering/evolution/2026-09-28-native-client-parity.md`.
- GitHub Copilot hooks, plugin and custom-agent references (retrieved 2026-09-28).
