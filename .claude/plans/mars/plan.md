# MARS integration plan

**Date:** 2026-09-25
**Branch:** `jokerman-microsoft-mars-integration`, from `origin/main` at `80002ed4`
(PR #93, Universal 0.11.0) plus the seven MARS prototype commits.
**Authority:** operator instruction of 2026-09-25: open a branch and integrate MARS per the
plan in [status.md](status.md) ("Remaining", items 0-5). The CyberGym benchmark is paused.
**Sources:** [spec.md](spec.md) (R01-R17), [review-method-design.md](review-method-design.md)
(RM1-RM9), [integration.md](../../../skills/mars/references/integration.md).
**Coordinator:** Finish work / Go Live (`88aecc43-40f9-41d4-8947-6c2fb0a55481`) owns merge
timing, version assignment and delivery. Go Live published the branch as PR #105; merge pending.

## Assumptions (autopilot, stated rather than asked)

- **D1** (review-method-design.md) is adopted as designed: in panel mode REVIEW records its
  decision through the existing content-bound path from the adjudicated panel result.
  MARS alone never clears anything; standalone MARS stays advisory.
- `define` and `plan-eng-review` are being rewritten or removed by the in-flight native
  planning consolidation lane, and `CodeReviewer` by the quality lane. Their MARS hooks are
  specified in integration.md for the consolidated files instead of edited here.
- The drift guard is scoped to REVIEW's reviewer prompts. A repository-wide "no rubric
  outside method.md" sweep would rewrite files owned by active cleanup lanes.

## Build cards

- [x] **I1 Review Method library** (RM1-RM4, RM7, RM7b; R01, R07, R15)
  `lib/review_method.py`, `lib/review-method-schema.json`, `bin/li-review-packet.py`,
  accepted `method.md` and `review-questions.json` (tag rules, supersede validation).
  Accept: catalog validation, selection by kind/tags/stage, one body renderer, report
  coverage parsing (missing or evidence-free `checked` is incomplete), and a parity test:
  single-review and MARS request bodies are byte-identical apart from the header.
- [x] **I2 MARS evidence binding** (item 3, RM6; R09, R11, R12)
  Optional `panel init --select/--base` binds a `review_contract.snapshot` under immutable
  `inputs/`; records overlapping the selection are refused before any write
  (`output_overlaps_selection`); `panel verify-input` detects a changed input;
  the selected profile reference is recorded; `panel inspection` emits an inspection
  record with `release_clearance: false`. Round-1 bodies must match the frozen brief hash.
  One decision rule maps single and adjudicated panel reports to the same stage outcome.
- [x] **I3 Workflow hooks** (integration.md 1, 2, 3, 6; R03-R06, R14)
  cycle Step 5 full-route offer, plan Step 10 option E, review Stage 1/2 via the method
  packet plus Step 6b panel mode, code-review optional offer. Declining changes nothing.
- [x] **I4 Distribution** (R13) `mars` in `bin/li-copilot.py` `WORKFLOWS` with a required
  resource closure, `MIGRATED` trigger list, regenerated native entry and catalog, docs lists.
- [x] **I5 Decision and records** (R17) ADR-0034 (renumbered ADR-0036 on 2026-09-25), evolution entry, concept doc, status,
  lesson for today's correction.
- [x] **I6 Calibration loop** (RM8) opt-in per-question outcome log and summary.
- [x] **I7 Verification** unit, shape and integration checks; independent spec then quality
  review; RM9 re-pilot through the subagent transport (live evidence labelled separately).

## Out of scope

Default hook activation, Swarm changes, provider APIs or credentials, a model catalog,
recursive panels, automatic fixes, version bumps and PR creation.

## Review

**Evidence (2026-09-25, Windows host, Python 3.11, Git Bash):**

- Unit: `tests/runner/run-all.sh --scope unit` 78/78 pass (1 partial: `jq` absent), run with the
  host's inherited `GIT_CONFIG_*` variables removed. With them present, 11 native-path cases in
  `review-evidence.sh` fail on their own fixture guard; identical on the base.
- Shape: `--scope shape` 41/41 pass (1 partial: `jq` absent).
- Focused: `review-method.sh` 21, `mars-contract.sh` 40, `mars-hooks.sh` 2 (all OK; the
  junction alias and case-variant cases ran).
- Integration: copilot-kit 21 of 50 cases run: 19 pass, including the six generation and
  closure cases after updating the catalog total to 197 (0e0e0452). Two caller-policy cases
  fail on a fixture HOME assertion here and identically on the base `80002ed4`. The other 29
  cases were not run (the file takes hours on this host). `universal-adapters.sh` and
  `catalog-installed.sh`: see status.md.
- Generator: committed `.github/skills/li-mars/SKILL.md` equals the generator output; a
  portable bundle carries every `MARS_RESOURCES` path.
- Live: RM9 re-pilot, four host-verified models, [pilot-2026-09-25-rm9.md](pilot-2026-09-25-rm9.md).
- Independent review (`lintel-reviewer`, two rounds): first pass CHANGES REQUESTED (Stage 1:
  2 P1, 1 P2, 1 P3; Stage 2: 3 P2, 2 P3). All nine resolved in 76142944 and 7daffd00; the
  recheck found one new P2 (omitted deviation count), fixed with a test. A changed-scope review
  of `cb39cedc` (reviewer `586563af`) passed with four P3s, addressed in the next commit; see
  status.md.

**Deviations from the cards:** the cycle offer moved entirely to PLAN's approval gate (cycle
Step 5 only surfaces it), so a full cycle has exactly one offer point. RM8 exists as the CLI and
method §7; CAPTURE is not edited because an active lane owns it. Commit 7daffd00's message
also credits the P1 rubric note, which landed earlier in 5a89b4c5; history was not rewritten.

**Next:** the operator ordered an immediate merge; ADR-0034 (with D1; renumbered ADR-0036 on 2026-09-25) is accepted and the
changelog updated. Go Live published PR #105 as `jokerman89` (this session's GitHub actor is
barred by L-053); merge pending, #105 first, then #104 converges. The pending consolidated
hooks follow #104.
