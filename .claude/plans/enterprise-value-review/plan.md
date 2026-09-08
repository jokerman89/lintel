# Enterprise value review plan

Status: operator authorized review and compatible improvements. Size: L. Estimates unmeasured; no invented currency or token precision.

| Card | Outcome | Dependencies | Owner | Acceptance |
|---|---|---|---|---|
| E1 | Isolate baseline and read architecture | none | coordinator | Separate worktree at 6b10a84 |
| E2 | Whole-system findings and priorities | E1 | three read-only reviewers + coordinator | File:line evidence and limitations |
| E3 | Repair pack/profile chain | E2 | scoped implementer | Before/after regressions, contract checks |
| E4 | Repair planning and pack traceability | E2 | scoped implementer + coordinator | Consistent templates/skills, validation |
| E5 | Enterprise scenario and decision options | E2-E4 | coordinator | Synthetic comparison, pilot metrics |
| E6 | Independent review and delivery | E3-E5 | independent reviewer + coordinator | Relevant tests, atomic commits, PR if checks permit |

These are coordination cards, not five-minute cold-subagent leaves. Exact implementation ownership is assigned after E2. No parallel agents write this ledger.

## Review

This section records the earlier draft milestone. The operator's subsequent instruction to
complete every finding and merge to main is tracked in [completion.md](completion.md), with
current dispositions in [the completion review](../../engineering/audits/2026-09-08-enterprise-value-completion.md).

E1–E6 are complete through publication as [draft PR #84](https://github.com/jokerman89/lintel/pull/84).
Independent reviews are complete with no remaining findings on the
changed implementation; aggregate verification passed 93/93 scripts. Final edge regressions
also pass, with evidence recorded in the whole-system review. The operator explicitly
approved the M2 exception for draft-PR publication on 2026-09-08. Eight targeted scripts
passed again after the rebase; CI and final integration review remain with the draft PR.
PR #83 merged into main during publication, creating conflicts for #84. Resolving the
overlap and validating the combined tree is the next integration action before merge.

The concurrent checkout has substantial uncommitted Copilot changes. This branch starts from
the inspected baseline `6b10a84`; its review commits are rebased onto main `9a024c0` so the
two earlier unpublished commits are excluded. Conflicts must be reviewed before combining
efforts. No private pack, personal setup or production service was changed by this review.

The broad review found 22 initial issues: 12 addressed, one partially addressed in the new
guide, and nine open or separate work. Five further implementation/scenario findings and a
whitespace variant were closed after independent review. Two baseline P1 Git collection issues
remain important rollout blockers. The report names their exact limits and next actions.
