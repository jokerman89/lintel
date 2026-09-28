# Build log: native client parity, increment 1

- **cycle_id:** native-client-parity-20260928
- **work_map:** .claude/plans/native-client-parity/work.json
- **tasks_path:** .claude/plans/native-client-parity/plan.md
- **profile:** _default (verified by `workflow_begin`; compliance advisory, voice internal)
- **required_policy:** not required (neutral baseline)
- **Branch:** `jokerman-microsoft-copilot-skill-loading-research` (base `origin/main` 49f2d152)

Entries are appended per package in execution order. Leaf results carry the command and its
observed result. Reviews reference their evidence records.

## Pre-flight (2026-09-28)

- Approved map: `work.json` APPROVED; trio gate PASS (see the PLAN ledger entry).
- Branch: `jokerman-microsoft-copilot-skill-loading-research` (not `main`); tree clean.
- Controls: pack `_default` declares no compliance hooks, so there is no mandatory control. Lintel's
  own hooks are the product under change.
- Code freeze: none declared.
- Deviation: PLAN's "link work.json from todo.md" was not applied. `.claude/plans/todo.md` is a
  byte-bound record (legacy-cleanup `residuals.md` spans), and editing it failed the command-surface
  guard with 550 findings in an LF clone. It was restored in `2a422d2a`, and the guard passes (0
  findings). The initiative is indexed from the working state and MEMORY hot notes at CAPTURE.
- Guard rule for every package: run `bash tests/shape/native-command-surface.sh` in a
  `core.autocrlf=false` clone of the package head (L-061) before review.
- Commit rule: Conventional Commits, no AI-authorship trailer (CONTRIBUTING line 134), new commits
  only (L-055/L-060), and only on this branch (L-059).

## P1: native skills and agents

- **start_ref:** `2a422d2a`

## Interruption and recovery (2026-09-28, detected 18:18)

A runtime restart at about 18:14 cleared all three background implementers. Their agent IDs return
not-found, and no lane process was running (checked read-only with `Get-CimInstance`). Recovery used
the durable evidence below and resumed only the unfinished leaves.

- **P1 (`1ac56994`)**
  - Commits:
    - `b2f31102` (li-run)
    - `d5433e08` (complete native skills and agents)
    - `5347c9f0` (agent preamble)
    - `d58ac2b1` (helper rename)
    - `fa2f95bd` (host spelling in native descriptions)
  - Tree: clean.
  - Targeted run (`li-p1-kit-targeted.log`, 17:31, 6 tests in 2522.8 s): FAILED with 1 failure and
    1 error.
    - The failure was `/li:` in a generated agent description. `fa2f95bd` targets it; verification
      is pending.
    - The error was `read_text()` decoding generated UTF-8 with cp1252 in
      `test_modified_managed_file_refuses_entire_update`. That is a test-portability defect.
    - The same log observed 96 native skills and 72 agents, equal to canonical discovery.
  - Full run (`li-p1-copilot-kit.log`): interrupted at 26 tests (21 ok, 5 ERROR, no summary or
    tracebacks). The errors were:
    - `test_canonical_default_caller_child_keeps_verified_parent_and_unbound_child`
    - `test_canonical_required_caller_policy_refuses_missing_drifted_and_conflicting_context`
    - `test_git_verification_directory_linked_and_plain_folder_controls`
    - `test_installed_scaffold_preserves_seeded_short_and_long_plain_targets`
    - `test_installed_scaffold_refuses_late_long_target_changes`
- **P2 (`ff10758e`)**
  - No commits. Uncommitted work inside its boundary: `hooks/shared/_input.sh` (+161 lines),
    `hooks/adapters/{copilot.sh,_json.sh}`, `tests/fixtures/copilot-hooks/` (11 fixtures and a
    README), `tests/unit/copilot-hook-adapter.sh` (38 KB), and additions to `hook-input-adapter.sh`
    and `hook-gate-content.sh`.
  - The work is preserved in place and also backed up outside the repository in the session folder
    (`p2-interrupted-backup`, tracked patch SHA-256 prefix `6E1B951A32476C78`, 14 untracked files).
- **Preparation lane (`497430ea`)**
  - Commits:
    - `948ab2dc` (P4 `cli_support` hints)
    - `b3063189` (registry sources)
  - Tree: clean. The PR-1a documentation leaves had not started.
- **Coordinator actions on the P1 branch after recovery**
  - `c69c177a`: an ordinary merge of `main` `c3ffa153` (PR #110). No conflict; #110's
    `tests/unit/native-command-surface.py` assertion is kept exactly.
  - `d29a78d4`: the ADR-0039 renumber. 38 decision files, no duplicate number, highest 0039.

## P1 continuation, review and fixes (2026-09-28 to 2026-09-29)

Evidence records live in the coordinator session's evidence folder, outside the repository. They
are cited here by file name and SHA-256 prefix. Old-SHA records stay as observations of those
commits; identical trees carry their content.

- **Continuation (`b786b578`).** `4bfc4e73` gave every text read and write in the P1 Python tests
  an explicit UTF-8 encoding. That was the F2 root cause: the Windows locale codec.
  - Local runs used LF clones, synthetic `HOME` and `TEMP` roots, and PowerShell 7 through
    `LINTEL_POWERSHELL` (ADR-0032). The Windows PowerShell 5.1 default route was denied by
    execution policy and stays unaccepted.
  - On `4bfc4e73`, all seven targeted `copilot-kit.py` cases passed:
    - the six-case runner: OK, 2282.6 s;
    - `test_git_verification_directory_linked_and_plain_folder_controls` alone: OK, 1192.3 s;
    - the canonical and scaffold closures one at a time.

    Two scaffold attempts were stopped by the coordinator as obsolete under the re-plan. They are
    INTERRUPTED with no verdict.
- **Independent review (`e3fe3231`, read-only).**
  - **Stage 1 and 2 at `4bfc4e73`:** Critical 0, High 0, Medium 2 (M1, M2), Low 8.
  - **Delta reviews:**
    - `4c2d1569`: CHANGES-REQUIRED for N1 (Medium) and N2.
    - `68262ccd` (pin `0cbdb59f`): SOURCE-ACCEPTED-PENDING-HOSTED. New Lows N3-N5 were resolved in
      the next batch.
    - Tree `8f995fc5` (pin `941b20c1`): SOURCE-ACCEPTED-PENDING-HOSTED. N6 (`&` and `;` stay literal
      in a rewritten query) and N7 (the placeholder filter covers the query and fragment) are
      advisory Lows, recorded without a fix cycle under MasterCoordinator's rule. Neither has an
      instance today.
  - The reviewer ran response-only after a cleanup incident (L-049 amendment), using only view,
    grep and glob. Its tool receipts were checked for every turn.
- **Fix batches.**

  | Batch | Commits | What they do |
  |---|---|---|
  | M1, M2, L1, L2, L5 | `6b0d3987`, `04a260fa`, `8ef9ea46`, `f612a3de`, `34cc2126`, `a0af0633`, `4c2d1569` | wrapper, `LINTEL_SKILLS_DIR`, preamble bullet, directory links, query strings, agent description limit, regeneration |
  | N1, pin, N2 | `95eb5f99`, `c9105e6c`, `79a8481d`, `68262ccd` | skills-root wording, pinned `LINTEL_SKILLS_DIR`, directory links need `/`, regeneration |
  | N5, N3, N4 | on the new candidate branch (below): `c3fc63b1`, `eaaba346`, `9ee0efbf`, `5957a7ea` | scoped `<base>`, file links refuse `/`, query percent-encoding, regeneration |

  Cheap checks (native-artifacts, `li-run`, adapter-navigation, `check`, 1.6.g and the LF guard)
  exited 0 once on each final head. `final-receipts-941b20c1.txt` (`6dfc0f89`) adds a vendored
  render check: 96 skills, 72 agents and 0 link errors.

  1.6.g at tree `8f995fc5`:
  - `check`: 6.3 s;
  - discovery frontmatter: 40,691 bytes;
  - native files: 1,496,988 bytes;
  - vendored growth: 1,509,050 bytes.
- **Boundary note.** `tests/unit/native-artifacts.sh` is outside the P1 edit boundary in the work
  map. The coordinator authorized it in the M1 fix instruction.
- **Candidate branch correction (MasterCoordinator decision B, 2026-09-29).**
  - Commit `f2fa4d94` on the original branch was made from a shell with a synthetic `HOME` and
    carried an unintended author identity.
  - The four unpushed commits `f2fa4d94..941b20c1` were re-created with the approved identity on the
    NEW branch `jokerman-microsoft-copilot-native-1a` (`c3fc63b1`, `eaaba346`, `9ee0efbf`,
    `5957a7ea`). Trees and messages are identical; the final tree is `8f995fc5`.
  - The original branch `jokerman-microsoft-copilot-skill-loading-research` stays at `941b20c1` and
    is never published.
  - The same reviewer verified the mapping from the Git receipts (`identity-correction-receipt.json`
    `f058fef6`, `identity-correction-git-receipts.txt` `a2f2264c`).
  - The candidate branch supersedes the "Branch" line at the top of this log.

## PR-1a integration and live acceptance (2026-09-29)

- `67eea278`: an ordinary merge of the preparation lane `2ead5ac9`, which carried:
  - P4 hints on 96 skills and 69 agents. 11 agents are `level: degraded` with an `AgentMemory`
    degradation: SOC2Reviewer, GHActionsReviewer, K8sManifestReviewer, TerraformReviewer,
    WebExperienceCritic, WordTechnicalEditor, CodeReviewer, RegressionDetective, TestRunner,
    DependencyAuditor and ThreatModelDrafter.
  - The PR-1a P5 documentation and registry-source leaves.
- **Coordinator edits after the merge:**
  - `f1945c15`: the skills-root contract in COPILOT.md and the CHANGELOG.
  - `9ed344e1`: README, glossary and FAQ (5.3.b).
  - `71698ed7`: six manifests at 0.13.0 (5.4.c).
  - `595026e4`: the wiki regenerated (4.2.a).

  The native files and `skills/CATALOG.md` regenerated with no diff.
- **Join checks** at `595026e4`, run once in a fresh LF clone. Receipts: `join-receipts-595026e4.txt`
  (`129b6a33`); every check exited 0 except the EOL note below.
  - Frontmatter lint, catalog and wiki checks, and `li-copilot check`.
  - The three catalog units and the three registry units.
  - The manifest validity and identity checks. Version parity was confirmed separately because
    `jq` is absent locally.
  - The native units, and the LF guard: PASS, 0 findings, on the clean clone
    (`join-lf-guard-clean-595026e4.log`, `72363b49`).
  - EOL note on 6.1.a: after regeneration, only `docs/wiki/schemas.md` differs, and only in line
    endings. On Windows `li-wiki-gen` writes CRLF for the schema summaries, and its own `--check`
    strips CR by design.
- `fd151979`: an ordinary merge of `origin/main` `1cf7d099` (PR #111 and #112; 14 presentation
  paths only).
- **P6A live acceptance** on `fd151979` with Copilot CLI 1.0.89-5, recorded in
  `evidence/copilot-acceptance.md` (`5389f94f`):
  - both routes discovered all 96 skills, including `li-pause`;
  - `li-cycle` was delivered with a SHA-256-equal body on both routes;
  - the plugin route selected `li:CodeReviewer`.

  The registry observations followed in `2f2c382c`, and the docs and CHANGELOG in `269ce3d1`.
- **Hosted gates still REQUIRED before any merge:** the seven vendored installation cases, the
  complete `copilot-kit.py` (52) and `universal-adapters.py` (17) suites, and the full CI matrix.
