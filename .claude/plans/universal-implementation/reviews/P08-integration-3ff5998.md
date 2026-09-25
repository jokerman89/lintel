# P08 whole-package integration review

- Reviewer: SAME9db (session `9dbf0a9b-750d-45c2-968c-41a5acb11c92`). Distinct independent reviewer; implemented none of P08, A13, the conflict resolutions or reconciliations 1–7.
- Authority: coordinator88 integration brief and revised target (P08 card, "F06 accepted", "P08 integration preview", "P08 integration branch and reconciliation 6").
- Mode: read-only against the repository. No product, test, plan, memory or ADR change; no branch or commit (the coordinator preserves this file byte-exact). Own executions ran in an allowlisted synthetic environment under a short disposable root, with the source worktree verified unchanged before and after.

## Target and coverage

| Item | Value |
|---|---|
| Reviewed product target | recovery `3ff599847452509d154339fa34bceae7cebbce1b` (tree `f6778633`) |
| Original integration target | `9f351a008ad19ab4cdc87dc8972464f946bb43d7` (tree `915298bf`), superseded for INT-S01 |
| Head this verdict applies to | recovery `6a6d95d067a88da6239dd9747e07f39e68e28d33`, for the P08 scope below |
| Joined-run head | `3d7f1284` (fin2), whose P08 and product content equals `3ff59984` plus the presentation-only merge `fe9e6284` and version stamp `99443cf8` |

Head applicability: every A13 product path (48) is byte-identical to the accepted `650fafab` at `6a6d95d0`, and every one of P08's 46 authored paths and every reconciliation path is byte-identical to `3ff59984`. Between `3ff59984` and `6a6d95d0`, six inherited test/runner files differ that sit in P08's dependency-join range but are not P08-authored: `universal-profile-context.py`, `context-safety.py`, `profile-path-identity.py` and `snapshot-ownership.py` change only `skipUnless` reason strings to `platform: windows-only; …` (`89131723`); `run-all.sh` and `test-runner-contract.sh` add the off-Windows N/A report (`917d7125`). They belong to P15/A23.5. fin3-targeted on `14ab496e` shows all six entries exit 0; I did not review them.

## Verdicts

| Gate | Result |
|---|---|
| Whole-P08 integration SPEC | **PASS**, with the carried limits below |
| Whole-P08 integration QUALITY | **PASS with advisories**: P1 0 · P2 0 · P3 3 new (plus the five recorded P3 known limits) |
| A13.1 / A13.2 / A13.3 / A13.4 parents on the integrated tree | **Preserved**: accepted A13.a and A13.1.b/.4.b bytes are unchanged and their tests pass joined |
| Initiative, release or publication acceptance | **Not given**; A23.5 and the PR's strict CI remain separate gates |

Finding INT-S01 (P2, the missing P08 status job reader on `9f351a00`) is **resolved** on `3ff59984` by the integrated P13 fan-in, and was not a P08 or merge defect.

## SPEC evidence by scope item

### (1) Preview merge `3c7ce67e` and skillify port

- `git merge-tree --write-tree 0e1746a8 400c0316` reproduces exactly the 14 predicted conflicts.
- Resolutions compared by blob against both parents:
  - recovery side: `MEMORY.md`, `handoff.md`, `plan.md`, `bin/li-copilot.py`, `bin/li-work-artifacts.py`, `skills/status`, `skills/welcome`, `copilot-kit.py`, `pack-source-target-resolution.sh`, `test-runner-contract.sh`;
  - A13 side: `lib/state.sh`, `lib/cycle-footer.sh`;
  - neither: `skills/skillify/SKILL.md` (the port) and `universal-work-lifecycle.py` (recovery plus the `setdefault` reconciliation).
- Losing-side line survival (every line the losing side added over base `5c3e7533`, checked against the result):
  - A13's `state.sh`/`cycle-footer.sh` lose only the review date; recovery's truncated-entry branch survives as an `else if` beside the new UNTRUSTED and legacy diagnoses.
  - `li-work-artifacts.py`: the seven lines A13 carried from P08 are replaced by recovery's reviewed superset `aa5cf0e4`, which adds explicit coordination-map selection and still refuses a different work map.
  - `welcome`: one wrapped line is extended, not lost.
  - `skillify`: the port adds exactly A13's three remaining changes (`--from-lesson <L-NNN>`, the `li-lessons.py get --id L-NNN` step with exits 1/2, and the failure-mode exits); recovery already carries `L-042`. The port file hash `466fd24d…` matches.
  - `status`: every P08 line was absent at the preview; see (7), resolved on the target.
- Non-conflict delta between the merge-tree result and `3c7ce67e` is exactly: the three test reconciliations, reconciliation 4, and regenerated `skills/CATALOG.md` and `docs/wiki/skills.md`.

### (2) Test reconciliations

- `tests/shape/cycle-footer-present.sh:34-41` (clause at 35-40) now follows the real persistence path: `workflow_begin "…" "$mode"` in the cycle skill, `state_cycle_begin "$id" "$mode"` in `lib/workflow.sh`, and `"cycle_mode=$mode"` in `lib/state.sh`. All three greps must match.
- `tests/integration/universal-work-lifecycle.py:47-48` uses `setdefault("LINTEL_PYTHON", sys.executable)`, so an explicit caller selection wins.
- `tests/shape/no-swedish.sh` allowlists exactly `tests/unit/intent-operation-boundary.sh` in both its header and its case list, with a functional reason.
- All three pass in my isolated runs and in fin2.

### (3)/(4) Reconciliations 4 and 5

- The patch `p08-event-catalog-reconciliation.patch` (SHA-256 `f0724329…`, 3,398 B) applies cleanly to A13's catalog, and its result equals `3c7ce67e`'s catalog after EOL normalization.
- Catalog counts 30/75 → 24/69 → 23/66. The removed set is exactly `{da,dh,sc,ta,tq}-decisions`, `full-engineering-pass`, `pack-lifecycle` and `migration/claude_home_migrated`. `migration/surfaced` and every other category are JSON-equal to A13's.
- No `audit_log` producer of a removed kind remains in `bin`, `lib`, `hooks`, `skills`, `agents` or `scaffolding`.
- `hooks/hooks.json`: only `_comment` changed. Its nine hook commands and all other keys are identical, and all use double-quoted `${CLAUDE_PLUGIN_ROOT}`. The new wording matches `bin/li-lifecycle.py:707`, which reports only `audit_log_present`.
- `event-catalog-producers.sh` passes (my runs and fin2).

### (5) Reconciliations 6 and 7

- `ad1045b8` adds `bin/li-events.py`, `lib/event-catalog.json` and `bin/li-lessons.py` to `ADAPTER_RESOURCES`, and adds `bin/li-lessons.py` to the core selection's resources.
  - The core members `capture` and `discover` call `li-lessons.py`.
  - The event reader's consumers (`audit`, `hooks-status` and others) are in no selection, so declaring them there would claim a false requirement.
- `ac216479` adds `lib/memory.sh`, which `li-lessons.py:237-246` sources as its single store resolver.
- The kit's missing-resource refusal (`copilot-kit.py:1437-1455`, data-driven over `ADAPTER_RESOURCES`) therefore covers the new entries; fin2-kit ran 50 tests, OK. Installed-kit completeness for A13's reader, catalog and lessons helper holds.
- `li-events.py` otherwise loads only `lib/native_paths.py`, which is declared.

### (6) A13 parents on the integrated tree

- The 48 A13 product paths (A13.a `229656cf..400c0316` and A13.b `14b0b51c..650fafab`) are byte-identical to `650fafab` at both `3ff59984` and `6a6d95d0`.
- Against `400c0316`, the only differences are the five accounted ones: the A13.b reader and test additions, `hooks-status`, reconciliations 4/5 in the catalog, and the skillify port.
- The A13-accepted rewrites of P08-touched files (`code-freeze`, `code-unfreeze`, `maintenance`, `observation-learning.py`) are retained. Both P08 observation tests remain among the module's 48.
- `observation-learning.sh` (312 s), `event-catalog-producers.sh`, `audit-writes-via-helper.sh` and `hooks-registration-safe.sh` pass in fin2.

### (7) Status job reader (A08.4 status part, INT-S01)

- On `3ff59984` (and `6a6d95d0`), `skills/status/SKILL.md:157-178`:
  - keeps the absent-registry case reported as unobserved;
  - exports `LINTEL_JOBS_NO_INIT=1` with an explicit repo-local `LINTEL_JOBS_DIR`, `_ACTIVE`, `_ARCHIVE` and `_REGISTRY`;
  - sources the trusted source's `bin/_jobs.sh`, runs `list_jobs --read-only` and `stale_jobs 24`;
  - reports `UNVERIFIED` and exits with the real reader code on failure.
- `tests/unit/catalog-consumers.py` adds four discriminating tests:
  - no layout marker, with inherited foreign selectors ignored;
  - partial reads keep unknown records and stale age visible, with exit 1;
  - the target's own `_jobs.sh` is never executed, and nothing is initialized;
  - an injected reader error keeps the other observations and returns the real exit code.
- It passes in my isolated run `int-r2` and in fin2 (143 s).
- The merge `cd877232` equals `merge-tree(2b7dc115, d12bbf6d)`; the P13 product is its reviewed `d12bbf6d` (review by 30146eab, not re-reviewed here).

### Merge purity

`3ee142e8`, `b38b4b3e`, `9f351a00`, `cd877232`, `edb0a00a` and `70bdcd69` each equal `git merge-tree --write-tree` of their parents. `8912d53f` keeps `3ee142e8`'s tree.

### Joined checks (coordinator fin2 on `3d7f1284`, launcher `d288e74b`, PowerShell 7 only)

- **fin2-kit:** `copilot-kit.sh` exit 0, "Ran 50 tests in 12578.357s", OK. Log SHA-256 `531d4491…6afb`, verified.
- **fin2-rest-a:** 72/73 pass. The failure `domain-installed-consumers.sh` is the test's own short-path budget ("Fixture exceeded the short-path budget: 262", then a WinError 145 cleanup at the launcher root). fin2-dic-short passes it with `--work-dir E:/Workspace/w9/d`. This is the environment class already diagnosed for A13 and not P08.
- **fin2-rest-b:** 74/75 pass. The failure `catalog-installed.sh` is F-INT-6: its worst-case guard reports 302 ≥ 220 after counting gitignored runtime. This is P13-owned; the fix `1e362b3c` is integrated in `7ec02092`, reviewed by 30146eab and not by me.
- **Unions:** 148 unique entries plus the kit; both preflights show head `3d7f1284`, a clean source and the PowerShell 7 selector only.
- **P08-relevant entries, all exit 0:**
  - `universal-work-lifecycle` (672 s) and `universal-lifecycle`;
  - `universal-profile-context`, `observation-learning` and `review-evidence`;
  - `intent-operation-boundary`, `orientator-mechanical-routing` and `review-source-target`;
  - `catalog-consumers` and `jobs-system-present`;
  - `cycle-footer-present`, `no-swedish` and `event-catalog-producers`;
  - `managed-transaction` (the F-INT-5 repair);
  - the load-sensitive pair `cycle-footer` (39.6 s) and `frontend-design-surface-hook` (4.5 s).
- **Own isolated runs:** receipts `int-r1` on `9f351a00` and `int-r2` on `3ff59984`. Both use a fixture that is checkout-equivalent and verified clean, a source worktree unchanged before and after, and every home, temp, Git and LINTEL path inside the synthetic root.
  - int-r1: 11 of 12 targets exit 0. `hooks-registration-safe` fails only through its `node`-absent grep fallback, which misreads the escaped quotes in the comment; a direct JSON projection confirms all nine commands. With `node` on PATH it passes in fin2.
  - int-r2: all 7 targets exit 0.

## Carried limits (not waived; not counted as passes)

- Historical `shell27`/`q02` remain INVALID evidence, and their actual-home effects remain UNKNOWN. Nothing was inspected or rolled back.
- The 704/aa5 selected-reader seam remains revision-qualified.
- The inherited P03/P07 14/18 preservation and 22/23 context-safety groups at deep roots are not re-executed at their failing depth by any run here. fin2 runs under short synthetic roots, which is not preservation acceptance. P08 changed none of the implicated P03/P07 bytes, and an unchanged control reproduced them. They are attributed outside P08 and stay with their owner and A23.5; this review makes no long-path acceptance claim.
- The two cycle authority and confirmation sentences are reviewed as instruction text. The universal-work-lifecycle and resume suites passing is not live-host execution of them.
- Live host activation, native role registration, paid-model behavior and Python 3.9 runtime remain unverified, as `reports/final.md` records.
- The fin2 failures `domain-installed-consumers` and `catalog-installed` are non-P08. The latter's joined rerun on the final head was still running when this review closed.

## QUALITY (integration-scoped)

Scope: the conflict resolutions, the skillify port, the three test reconciliations, reconciliations 4–7 and the status union's P08 contract. P08-authored code was already judged in recheck 624.

Strengths:
- Every resolution loses no reviewed behavior.
- Catalog removals are exact and leave historical kinds reported as `unknown_kind` rather than attributed to a dead producer.
- The shape reconciliation now asserts the real persistence chain, not stale text.
- Resource declarations are data-driven into refusal tests.
- The status union fails visibly with the reader's real exit code.

New advisory findings (P3):

| # | File:line | Finding | Suggestion |
|---|---|---|---|
| QI-1 | `bin/li-lessons.py:380-381`, `845-853` | `template_bytes()` reads `scaffolding/01-foundation/.claude/memory/lessons.md` with no `OSError` handling, and `main` catches only `LessonError`. A missing template in a new store's `add` ends in a traceback (exit 1) instead of a typed refusal. The template ships as a whole component, and the installed check refuses first, so this is robustness only. | Map `OSError` there to `LessonError(3, …)`. |
| QI-2 | `bin/_audit.sh:53` (gated) | `_AUDIT_GLOBAL_CATEGORIES` still names `pack-lifecycle` after reconciliation 5 removed the category. This is a routing residue with no producer and no behavior change. | Drop it when the gated writer is next revised. |
| QI-3 | `tests/shape/hooks-registration-safe.sh:41` (not P08-authored) | The `node`-absent fallback greps `"command":"…"` and truncates at the first escaped quote, producing false failures. | Parse with Python, or skip escaped quotes. |

Known limits carried from recheck 624 (recorded, not re-raised):
- `lib/state.sh:32`: drive-relative and UNC path handling.
- `lib/workflow.sh:114-122`: an unset profile reference is re-exported as empty.
- `bin/li-work-artifacts.py`: imports P04's private `_task_sources`.
- The routing scan's worst-case O(n²) and byte-wise lowercasing.
- Repeated whole-ledger rescans.

## Evidence identities

The private directory `.claude/runtime/reviewer-9db/p08-integration-review-01/` holds:
- `run-int.ps1` and `int_checks.py`/`int_checks2.py`;
- the `int-r1`/`int-r2` receipts (`*.environment.json`, `*.process.json`, `*.stdout`, `*.stderr`, `*.driver.bin`), the `r1-record.json`/`r2-record.json` summaries and the `logs-r1`/`logs-r2` test logs;
- `interim-findings.md` and `host-note-l049.md`.

The coordinator's evidence is in `…88aecc43…/files/verification/fin2-{kit,rest-a,rest-b,dic-short}` and `fin3-targeted`.
