# MARS status

**Updated:** 2026-09-25
**Branch:** `jokerman-microsoft-mars-integration` (from `origin/main` `80002ed4` plus the seven
prototype commits of `jokerman-microsoft-mmars-development-plan`, which is unchanged)
**Coordinator:** Finish work / Go Live `88aecc43-40f9-41d4-8947-6c2fb0a55481` owns merge timing,
version assignment and delivery. No PR has been opened from this branch.
**Decision:** [ADR-0034](../../decisions/0034-mars-multi-model-review.md). Plan and evidence:
[plan.md](plan.md), [RM9 re-pilot](pilot-2026-09-25-rm9.md).

MARS = **Multi-Model Adversarial Review & Screening**.

## Integrated

| Item | Path |
|---|---|
| Canonical skill, protocol, integration points | `skills/mars/` |
| Shared Review Method (packet text, rubric, evidence levels) | `skills/review/references/method.md` |
| Standing questions with stable IDs and advisory tag rules | `lib/review-questions.json` |
| Method library and packet CLI | `lib/review_method.py`, `lib/review-method-schema.json`, `bin/li-review-packet.py` |
| Panel helper with method meta, input snapshot, overlap refusal, profile, inspection | `lib/mars_contract.py`, `lib/mars-schema.json`, `lib/mars-defaults.json`, `bin/li-mars.py` |
| Workflow hooks | cycle Step 5, plan Step 10 (option E), review Stage 1/2 and Step 6b, code-review |
| Distribution | `bin/li-copilot.py` (`WORKFLOWS`, `MARS_RESOURCES`), `.github/skills/li-mars/SKILL.md`, trigger list, catalog |
| Tests | `tests/unit/review-method.sh`, `tests/unit/mars-contract.sh`, `tests/unit/mars-hooks.sh` |
| Records | ADR-0034, `.claude/engineering/evolution/2026-09-25-mars-integration.md`, L-056 |

## Pending (needs the in-flight legacy cleanup base)

- MARS hooks for the consolidated planning inspection (replacing `plan-eng-review`),
  `define`'s spec review, `cross-check` and `CodeReviewer`: specified in
  `skills/mars/references/integration.md`, not applied to files that lane removes or rewrites.
- Repository-wide drift guard (no rubric outside the method) after that consolidation.
- CAPTURE wiring for the opt-in calibration log (RM8); today it is the CLI and method §7.
- Operator confirmation of D1 (ADR-0034) at merge.

## Verification (details in plan.md "Review")

Unit 78/78 and shape 41/41 (one `jq`-absent partial each); focused MARS/method tests 62;
copilot-kit 19 of 21 run cases pass, and the 2 failures reproduce on the base; generator and
bundle closure checked; RM9 live pilot; two independent review rounds, all findings fixed.
`universal-adapters.sh` was stopped after 3 of 17 cases passed in about two hours, and
`catalog-installed.sh` was not run; CI on a Linux runner is the faster place to finish them.

## Advisory P3 notes from the independent recheck

- Path case folding follows `normcase`; case-insensitive macOS volumes are not folded.
- `coverage_complete` means "complete and consistent under the method", documented in the
  protocol rather than renamed.
- The branch is based on `80002ed4`; `origin/main` has since gained six commits, none in
  files this branch changes except three lines in ADR-0033.

## Known limits

- Identity evidence is host-specific: Copilot App `assistant_usage_events` per child session or
  subagent `agent_id`. Other hosts need their own observation route or stay `requested-only`.
- "Latest" relies on version numbers in model IDs and the family preferences in defaults.
- Live runs so far: Copilot App only; one synthetic subject; no challenge round in RM9.
