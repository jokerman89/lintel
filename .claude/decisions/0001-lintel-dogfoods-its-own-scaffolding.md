# ADR-0001: Lintel dogfoods its own scaffolding

- **Status:** Accepted
- **Date:** 2026-06-04
- **Deciders:** jokerman89 (operator), Claude Code (implementer)
- **Supersedes:** —
- **Superseded by:** —

## Context

Lintel is the *factory* that installs a session-discipline scaffold (CLAUDE.md, `.claude/agents/`,
`tasks/lessons.md`, `docs/adr/`, CORE-PRINCIPLES, EVOLUTION-LOG) into other repos via `bin/li-scaffold`.
Sister repos that received it (e.g. `deeplex-backend`, `deeplex-story-teller`) carry a living,
scaffolded CLAUDE.md, a populated `.claude/`, decision records (`docs/06-decisions/`), and a
`tasks/lessons.md` that snowballs across sessions — exactly the "remember across sessions, compound over
time" outcome the scaffolding exists to produce.

Lintel itself never ran the factory on itself. Before this change its root had **no `.claude/`,
no `docs/adr/`, no root CORE-PRINCIPLES/EVOLUTION-LOG, and a thin 61-line v3-era CLAUDE.md** that was
plugin-developer notes pointing at `AGENT-INSTRUCTIONS.md` — not the scaffolded instruction set. The
consequence surfaced during the large v4.7 CAIP-extraction initiative: major decisions (pack-on-top vs
fork, aggressive de-MS, clean-copy vs `filter-repo`) were executed without ADRs, because there was no
ADR infrastructure in the repo and nothing in CLAUDE.md enforcing the ritual. The operator caught this
and asked why the meta-process that works elsewhere did not work in Lintel's own workshop.

Non-negotiable constraint: the operator's global `~/.claude/CLAUDE.md` mandates ADRs for non-trivial
decisions, lessons capture after corrections, and plan-before-non-trivial-work. The repo must make that
the default, not an aspiration.

## Decision

Lintel adopts its own scaffolding at the repo root: a self-contained scaffolded `CLAUDE.md`,
`.claude/agents/` + `SUBAGENT-GUIDE.md`, and `docs/adr/`. The root CLAUDE.md is **self-sufficient**
(restates the load-bearing protocol inline) so the repo works without the operator's global config —
per the operator's choice of the self-contained model over a thin "reference-the-global" model. ADRs are
required from this decision forward (no retroactive backfill of pre-v4.8 decisions, per operator).

## Alternatives considered

- **Thin repo CLAUDE.md that references the global protocol.** Rejected: the operator wants the repo to
  work standalone (cloned without `~/.claude`), so the protocol is restated inline instead of referenced.
- **Leave Lintel un-scaffolded; rely on `AGENT-INSTRUCTIONS.md`.** Rejected: AGENT-INSTRUCTIONS is the
  cross-CLI session ritual, not the per-repo discipline doc, and it did not produce ADRs/lessons in
  practice. The gap was real, not theoretical.
- **Backfill ADRs for the whole CAIP initiative.** Rejected by operator: set up the infrastructure and
  apply the discipline going forward, rather than reconstructing past decisions retroactively.

## Consequences

- **Positive:** Lintel now eats its own dog food; the discipline that works in sister repos applies here.
  Decisions get recorded; lessons snowball; future sessions start with real context. The dogfooded root
  doubles as a worked example of what `li-scaffold` produces.
- **Negative:** Two instruction surfaces now coexist — the root CLAUDE.md and `AGENT-INSTRUCTIONS.md`.
  They must stay coherent (CLAUDE.md owns the per-repo discipline; AGENT-INSTRUCTIONS owns cross-CLI
  bootstrap). Modest ongoing overhead: an ADR per non-trivial decision.
- **Neutral:** Lintel's evolution log remains `docs/v4.x/structure-changes/` (the meta-infra Gate-M1
  artifacts), not a separate root `EVOLUTION-LOG.md`, to avoid a third parallel log.

## Implementation notes

- `scaffolding/01-foundation/CLAUDE.md.template` is the canonical source; the root CLAUDE.md is its
  instantiation. The standalone `claude-scaffolding` repo (v0.5) is superseded by
  `scaffolding/01-foundation/` and is marked as such.
- A `bin/li-doctor` check warns when a repo that uses Lintel lacks its own scaffolding (`.claude/`,
  `docs/adr/`, a scaffolded CLAUDE.md) — so the "factory never ran on the repo" failure is caught for
  other adopters, not just here.

## References

- `scaffolding/01-foundation/` (the foundation templates)
- `~/.claude/CLAUDE.md` (operator global protocol — the source of the ADR/lessons mandate)
- `docs/v4.x/structure-changes/2026-06-03-caip-pack-extraction.md` (the initiative that exposed the gap)
