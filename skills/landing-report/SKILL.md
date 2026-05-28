---
name: landing-report
layer: foundation
description: Post-ship report — what landed in a window, in engineering or customer-voice format.
color: blue
tools: Read, Bash, Grep, Glob, Write
voice: mixed
cli_support: [claude-code, codex]
---

# /landing-report

Synthesizes what shipped in a given window into a structured report. Engineering-voice by default (changelog-style), customer-voice on opt-in (`--voice trailblazer` runs the output through customer-voice gates).

Use to brief teammates, draft release notes, or seed an external announcement.

## When to use

- End of sprint, deploy, or significant batch — want a clean recap
- Drafting release notes for a deliverable that's about to leave the building
- Internal status update for stakeholders
- Customer-facing what's-new content (with `--voice trailblazer` and `/rais-customer-voice-check` gate)

## When NOT to use

- Session-internal reflection — use `/retro` instead (lighter weight, lessons-focused)
- Single-commit change — git log -1 is sufficient
- Customer copy generation from scratch — use `/design-html --copy-tier trailblazer-draft` to seed, then `/msvoice-rewrite`

## Inputs

- Optional `--since <ref|time>` — start of window (default: last tag or 7 days ago)
- Optional `--until <ref|time>` — end of window (default: HEAD)
- Optional `--voice <internal|trailblazer>` — output voice tier (default: internal)
- Optional `--scope <area>` — filter to commits touching specific paths
- Optional `--include-stats` — add lines-changed / files-touched / contributors
- Optional `--out <path>` — write to file (default: stdout)

## Workflow

1. **Determine window.** Resolve `--since` and `--until`.
2. **Gather signals.** `git log <range>` — commits, authors, messages. `gh pr list --search "merged:<range>"` if gh available.
3. **Group commits.** By type (feat/fix/chore/docs/refactor) using Conventional Commits prefixes. Within each type, group by scope.
4. **Sanity scan.** Layer 2 patterns on every commit message + every PR title/body. Block on hit.
5. **Generate report:**
   - **Internal voice (default):** structured changelog with bullets per type. Concrete, terse, file:line where relevant.
   - **Trailblazer voice (`--voice trailblazer`):** narrative form, mode-tagged per paragraph (Reveal / Inspire / Provoke). Auto-flags as DRAFT — must pass `/rais-customer-voice-check` before distribution.
6. **Stats (optional).** Aggregate stats appended.
7. **Output.** Stdout or file per `--out`.

## Report format (internal)

```
Landing Report: 2026-05-20 → 2026-05-27 (main, 7 days)

## Features (9)
- skills: Phase 2 batch 5 — qa, qa-only, investigate, codex, careful (3a18068)
- skills: Phase 2 batch 6 — browse, scrape, make-pdf, setup-browser-cookies, open-gstack-browser (547768c)
- skills: Phase 2 batch 7 — design-review, design-consultation, design-html, design-shotgun, devex-review (a60c46c)
- skills: Phase 2b batch 8 — benchmark, canary, freeze, unfreeze, setup-deploy (f6f8ac3)
- skills: Phase 2b batch 9 — learn, office-hours, retro, pair-agent, skillify (2dfdb55)

## Voice (1)
- T0 corpus populated, all 12 cells, 60 sanitized paragraphs (7255bfc)

## Stats
- 6 commits, 6 PRs (squash-merged), 4,283 insertions, 71 deletions
- Files touched: 39
- Contributors: jokerman + Claude Opus 4.7

## Not shipped (still open)
- Phase 3 (20 MS-specific skills) — blocked on /li:eval, T0 corpus now ready
- Phase 4 (40 agents) — pending
```

## Report format (trailblazer DRAFT)

```
Landing Report: <window>
Status: DRAFT — requires /rais-customer-voice-check before distribution

## What changed (Reveal/Curtain)
The work of the last seven days isn't in any single new feature. It's in the
machinery underneath — a corpus of voice exemplars, a discipline for shipping
batches without losing context, a way for the next session to start where this
one ended.

## What's now possible (Inspire/Marvel)
[draft text — verify via /rais-customer-voice-check]

## What we'd say next (Provoke/Exception)
[draft text — verify via /rais-customer-voice-check]
```

## Compliance integration

- Layer 2 sanity-scan on EVERY commit message ingested. If a commit message contains a secret/customer-data pattern: report STOP, surface the offending commit, refuse to render the report (a leak in a commit message is now leaked to the report too).
- `--voice trailblazer` output marked DRAFT and gated: distribution downstream MUST run `/rais-customer-voice-check` (Phase 3) first.
- Stats reveal contributors — sanity-scan checks for any unexpected non-MS or non-public author (e.g. a contractor's personal email). Surface as a warning.

## Voice tier note

`voice: mixed`. Default internal. Trailblazer on opt-in produces DRAFT that requires the customer-voice gate.

## Failure modes

- **Empty window:** report "no commits in window" + exit cleanly. No fabrication.
- **Layer 2 hit on commit message:** STOP, surface offending commit hash + line, do not render. Operator decides — sanitize history (dangerous) or remove from window.
- **`gh` not available:** fall back to git-log-only, note in report.
- **Trailblazer-voice requested but T0 corpus empty:** WARN — generation will be best-effort but UNCALIBRATED. Recommend running `/li:eval` against corpus before downstream distribution.
- **Window spans pre-conventional-commits history:** group by author instead of type, note degraded categorization.

## Examples

**Default weekly:**
```
> /landing-report --since 7-days-ago
[Internal-voice report]
6 commits, 39 files. Ready for stand-up.
```

**Release notes draft:**
```
> /landing-report --since v1.0.0 --voice trailblazer --out release-notes-draft.md
[Trailblazer DRAFT to file]
DRAFT written. Run /rais-customer-voice-check before distribution.
```

**Scoped to skills:**
```
> /landing-report --scope scaffolding/01-foundation/skills/
[Filters to skill-related commits only]
```

## See also

- `/retro` — session-internal reflection (vs ship-facing report)
- `/rais-customer-voice-check` (Phase 3) — required gate for trailblazer-voice output
- `/msvoice-rewrite` (Phase 3) — rewrite internal-voice output to trailblazer
- `/release-ev2` — generates a per-PR body that this skill can aggregate
