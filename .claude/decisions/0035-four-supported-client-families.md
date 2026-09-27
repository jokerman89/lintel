# ADR-0035: Support four client families — Copilot, Claude, Codex and Cursor

- **Status:** Accepted, 2026-09-25
- **Date:** 2026-09-25
- **Deciders:** the operator ("It's enough with Copilot, Claude, Codex and Cursor to start
  with. Please clean out the rest")
- **Supersedes:** —
- **Superseded by:** —

## Context

The Universal initiative (ADR-0028) turned `lib/cli-tiers.yaml` into a registry of 38
records: 37 client surfaces in 14 families, most with dated vendor sources, plus the manual
`other` route. Every family added records, discovery roots, installer cases, tests and guide
text, and some added entry files (`GEMINI.md`, `gemini-extension.json`, `.opencode/INSTALL.md`)
and update routes in `bin/li-update`. Apart from limited Copilot App observations, every surface
was source research only (`not_run`). The operator asked to cut this to the clients the team
uses, to reduce friction in the system and the time CI spends on it.

Support is registry-driven: the installer, shell compatibility API, catalog, onboarding
and the generated README table read the same records. Removing a record removes its
route without changing those code paths.

## Decision

Lintel supports four client families, with every surface record they already had:

- Claude: `claude-code`, `claude-desktop`
- GitHub Copilot: `copilot-cli`, `copilot-app`, `copilot-vscode`, `copilot-cloud`
- Codex: `codex-cli`, `codex-desktop`, `codex-ide`, `codex-cloud`
- Cursor: `cursor-cli`, `cursor-ide`, `cursor-cloud`

We removed Gemini, OpenCode, Factory (Droid), Antigravity, Kiro, Devin/Cascade (formerly
Windsurf), Junie, Cline, Continue and Aider: 24 surfaces, 20 sources and 8 aliases; the
Gemini extension and `GEMINI.md`; the OpenCode install guide; the Gemini and Droid update
routes; the doctor's probes for their executables; their `cli_support` hints; and the tests
and documentation that named them. For these ten families only, this overrides the
Universal specification's R03 ("without reducing existing client value") and L-031's
preservation default, at the operator's explicit direction.

`other`, the explicit manual canonical-file route, stays. Unknown IDs already degrade to
it in the legacy tier reader, and the validator requires it. It is a fallback for hosts
outside the four families, not a supported integration. The Universal operation contract
(`shims/universal/ADAPTER.md`) also stays: the Claude, Codex and Cursor wrappers link to it.

The registry schema, validator, installer and inventory semantics are unchanged. An
unreleased kit that selected a removed surface is refused before any write, as for any
unknown surface; the migration guide rebuilds it with its supported surfaces or `other`.
We added no compatibility layer for retired IDs: the multi-client installer was never in a
tagged release.

## Alternatives considered

- **Keep the records and mark them unsupported.** Rejected: the records, roots, tests and
  guides would still need upkeep, which is the friction the operator wants removed.
- **Also remove `other` and the Universal operation contract.** Rejected: `other` is one
  record that keeps unknown hosts on an explicit manual route instead of an error, and the
  operation contract is shared by the kept wrappers. Removing them would change validator
  and installer behavior for no reduction in client support.
- **Selected: delete the ten families' records and routes, keep `other`.**

## Consequences

- **Positive:** 14 registry records instead of 38 and 4 native discovery roots instead of
  12. Tests that iterate the registry do less work: the shell tier test spawns one helper
  per surface, and the adapter test installs every surface's wrappers. Fewer guides and
  entry files to keep current.
- **Negative:** users of the Gemini extension, the Droid plugin or the OpenCode guide lose
  that route. They can still use a repository kit with `other`, which is a manual handoff,
  not native discovery. Re-adding a family needs new source research, a record, tests and a
  pilot.
- **Neutral:** the CI matrix and shards (ADR-0032) are unchanged. Accepted ADRs, audits,
  plans, reports and the dated presentation deck keep describing the earlier set as history.

## References

- ADR-0028 (Universal operations), ADR-0032 (CI shards), L-031 (preservation default,
  overridden here by explicit operator direction).
- `.claude/plans/supported-clients/` (spec, plan, handoff and review).
- `docs/migrations/2026-09-25-supported-clients-four-families.md` and its `docs/migrations/_INDEX.md` row.
