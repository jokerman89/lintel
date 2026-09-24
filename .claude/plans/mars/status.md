# MARS status

**Updated:** 2026-09-24
**Branch:** `jokerman-microsoft-mmars-development-plan` (this session's own branch; new files only
except the regenerated `skills/CATALOG.md`)
**Coordinator:** Finish work session `88aecc43-40f9-41d4-8947-6c2fb0a55481` owns integration timing.

MARS = **Multi-Model Adversarial Review & Screening** (renamed from MMARS by the operator).

## Built and verified

| Item | Path | Evidence |
|---|---|---|
| Canonical skill | `skills/mars/SKILL.md` | frontmatter lint, catalog regeneration PASS |
| Reviewer/challenge/synthesis protocol | `skills/mars/references/protocol.md` | used live in the pilot |
| Integration snippets (not applied) | `skills/mars/references/integration.md` | — |
| Defaults | `lib/mars-defaults.json` | latest per family, xhigh, 1M, 4 reviewers, max 8 |
| Header schema (request/report/synthesis) | `lib/mars-schema.json` | unit tests + live refusal of malformed/mismatched reports |
| Contract helper | `lib/mars_contract.py` | 30 unit tests |
| CLI | `bin/li-mars.py` | roster, offer, panel init/origin/add/brief/record/observe/close-plan/mark-closed/summary/synthesis-header |
| Native Copilot entry | `.github/skills/li-mars/SKILL.md` | matches generator format |
| Tests | `tests/unit/mars_contract.py`, `tests/unit/mars-contract.sh` | 30/30 PASS |
| Fixtures | `tests/fixtures/mars/` | pilot brief, Copilot App host snapshot |
| Public doc | `docs/concepts/mars.md` | — |
| Live pilot | `.claude/plans/mars/pilot-2026-09-24.md` | 4 models, 2 rounds, host-verified identity, 8 sessions closed safely |
| MDASH lessons | `.claude/plans/mars/mdash-lessons.md` | — |
| ADR draft | `.claude/plans/mars/adr-draft.md` | number allocated on the released base |
| Shared Review Method design | `.claude/plans/mars/review-method-design.md` | DRAFT; decision D1 open |
| Review Method (draft) | `skills/review/references/method.md` | not wired |
| Standing questions (draft) | `lib/review-questions.json` | 37 questions, unique stable IDs, validated |

## Remaining (coordinator-scheduled, on the released Universal base)

0. Execute the Review Method cards RM1–RM9 in `review-method-design.md` first: REVIEW and
   MARS must send the same reviewer packet. Keep `/li:review` and `/li:mars` independently
   runnable; the method library is the only shared part.
1. Apply `skills/mars/references/integration.md` edits to cycle, plan, review, define,
   plan-eng-review and code-review (shared files, deliberately not touched here).
2. Add `mars` to `bin/li-copilot.py` `WORKFLOWS` and the resource closure; regenerate adapters
   and `skills/CATALOG.md`; add `mars` to the description-trigger `MIGRATED` list.
3. Bind MARS inspection records to the released `review_contract.py` snapshot/inspection
   evidence and `profile_context.py` reference (spec R09/R11); today the brief hash binds
   the frozen brief only.
4. Allocate the ADR number; add an evolution entry.
5. Optional: a subagent-transport pilot to measure the cost difference.

## Known limits

- Identity evidence reader is host-specific (Copilot App local session store); other hosts
  need their own observation route or stay `requested-only`.
- "Latest" relies on version numbers in model IDs and the family preferences in defaults.
- No live run on hosts other than the Copilot App.
