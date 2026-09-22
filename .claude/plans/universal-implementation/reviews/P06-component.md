# P06 independent component review

**Date:** 2026-09-20.
**Reviewer:** independent `lintel-reviewer`, Universal adapters review session
`08ffd693-ae70-44aa-912f-94cc1bb2faec`.
**Component verdict:** FAIL; one reproducible source-link preservation defect.
**Stage 1 (component specification):** FAIL, seven leaves pass and one has a deviation.
**Stage 2 (quality):** NOT RUN; Stage 1 has not passed.
**Findings:** P0 0, P1 0, P2 1, P3 0.
**Final integrated acceptance / live-client support:** NOT GRANTED.

This reviewer did not implement P06, repair product files, delegate to nested agents,
or change shared plan/runtime state. The only authored repository change is this report.
Passing mechanical tests below does not override the observed deviation or establish
whole-repository release acceptance.

## Immutable scope and authority

| Role | Exact reference |
|---|---|
| P06 product candidate | `6f5d665cd4e3831c2dd6516199c924a2922fba10` |
| Submitted report-only snapshot / review checkout | `4a277f7e899101308995b107e967127f96bb8085` |
| Product comparison base | `40c279520a86945cc7e607692355bf5231446ff1` |
| Disposable P04 composition input | `02be6cb1448cd9def1572ae55e321f07d974a33b` |
| P04 delta base used for that composition | `e74849db6b33c7b93baadb86206009cb9f9eb6d5` |

The product commit has the stated comparison base as its parent. The submitted snapshot
has the product commit as its parent and changes only `reports\P06.md`, adding 43 lines.
Consequently, the checkout's product bytes match the immutable product candidate.
The subsequent report commit is not a new reviewed product revision.

Authority read: repository and scoped shim instructions, Copilot and Universal adapters,
canonical review workflow, ADR-0024/0025/0028, memory including L-030 through L-032,
architecture, the validated Universal work map, mapped spec/plan, P06 package and report,
the audit's A05/A06 acceptance and client sources, and `reports\host-source-research.md`.
Existing authorization is read-only component review plus hermetic fixtures and this report;
it does not authorize product repair, publication, real client invocation or profile changes.

The base-to-product delta contains **38 paths: 37 product/test/documentation paths and the
builder report**, not 38 independent client implementations. Those paths were inspected:

| Group | Reviewed paths |
|---|---|
| Entry prose, 5 | `AGENT-INSTRUCTIONS.md`, `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `README.md` |
| Registry and helpers, 6 | `lib\cli-tiers.yaml`, `lib\cli-tiers.sh`, `lib\client_capabilities.py`, `bin\li-client-capabilities.py`, `bin\li-adapter.py`, `bin\li-copilot.py` |
| Public guides, 8 | `docs\README.md`, `docs\architecture.md`, `docs\claude-code.md`, `docs\client-adapters.md`, `docs\copilot.md`, `docs\enterprise-adoption.md`, `docs\getting-started.md`, `docs\multi-cli.md` |
| Adapters, 5 | `shims\AGENTS.md`, `shims\CLAUDE.md`, `shims\copilot-instructions.md`, `shims\copilot\COPILOT.md`, `shims\universal\ADAPTER.md` |
| Assigned skills, 6 | `skills\{careful,cli-fingerprint,codex,instruction-parity-check,pair-agent,welcome}\SKILL.md` |
| Tests, 7 | `tests\unit\client-capabilities.py`, `tests\unit\client-capabilities.sh`, `tests\unit\cli-tiers.sh`, `tests\unit\copilot-capabilities.sh`, `tests\integration\copilot-kit.py`, `tests\integration\universal-adapters.py`, `tests\integration\universal-adapters.sh` |
| Builder evidence, 1 | `.claude\plans\universal-implementation\reports\P06.md`, including the report-only snapshot |

## Stage 1: specification and per-leaf preservation

| Leaf | Original problem, retained value and actual evidence | Result |
|---|---|---|
| A06.1 | Vendor-wide tiers are replaced by 38 distinct surface records and 15 semantic operations. The shared validator rejects malformed kinds, colliding aliases and unsafe discovery roots. All old shell entry functions remain; native format is not classified as blanket `full` support. Registry tests and real CLI consumers pass. | PASS |
| A06.2 | `describe` retains separate vendor/source/date/version conditions, delivered binding, and observed scenario fields. Missing claims stay `unknown`; missing runs stay `not_run`. Three Copilot App observations retain partial status and unknown exact version/revision instead of borrowing a candidate SHA. JSON round-trip and negative observation tests pass. | PASS |
| A06.3 | Actual caller-inspected tool names survive selection; no compulsory `AskUserQuestion` spelling. Denied operations block, unresolved permission requires approval, and absent tools use explicit fallbacks. Native-isolated, serial and manual paths retain review as outstanding. The original work-map/profile reference is transported without asserting policy validation. Named tests plus 120 operation/permission/availability cases pass. | PASS |
| A06.4 | Missing hook/plugin/model controls are unsupported. Unknown surfaces and invented `--enable`, `--model` and `--global` options fail before target writes. Fingerprinting, careful mode and outside-opinion instructions no longer invent a detector, permission control or Codex flags. Useful authorized inspection/manual handoff remains. P05's final evidence implementation is explicitly pending, not duplicated here. | PASS |
| A05.1 | README, start and enterprise guides lead with a bounded task, acceptance, review and cold handoff, before client choice. Reviews remain read-only; small work does not require venture framing. Native and explicit-file entry routes are explained without measured productivity claims. | PASS |
| A05.2 | Copilot's 14 core wrappers and three profiles, Claude's plugin/agents/optional hooks, other existing manifests, and manual canonical workflows are retained. All selected installer routes, fresh consumers, a real pre-P06 upgrade and native coexistence pass. However, the newly bundled README points to seven source-existing files omitted from that bundle; finding P06-C01 violates the requested source-relative navigation preservation. | FAIL: P06-C01 |
| A05.3 | Assigned onboarding/skills remain neutral about company, vendor, retention and venture defaults while retaining specialist depth, pairing, outside critique and high-stakes recovery. No private policy, model configuration or global detector is installed. The unchanged wider role/catalog/profile work is not claimed complete. | PASS |
| A05.4 | Entry prose and architecture point to the actual shared registry/operation contract. Canonical protocol content and four synchronized blocks remain unchanged and pass the real checker. Coordinator-owned reducers remain untouched. Temporary regeneration/checks and a second identical generation pass; this does not close actual integrated reducer drift. | PASS, bounded to component sources |

Preserved skill methods were checked individually, not inferred from surviving filenames:

| Skill | Retained method and corrected boundary |
|---|---|
| `welcome` | Task selection, setup diagnosis, proportionate workflow choice, optional cycle preview and specialist discovery; no settings edits or fabricated hook demonstration. |
| `cli-fingerprint` | Explicit declaration, conflict resolution, reinspection and capability reporting; actual metadata/tools replace secret-adjacent folder probes and a fictional global cache. |
| `pair-agent` | Bounded specialist turns, scope, disagreement handling and synthesis; absent delegation retains an external brief, not role-play independence. |
| `codex` | Diff/plan/code/hypothesis second opinions, strict/exploratory styles, agreement/disagreement and actual usage limits. Ad-hoc snapshot/inspection remains non-release evidence without a synthetic work map or full planning ceremony. |
| `careful` | Mutation scope, scoped confirmation, owned recovery, audit and final verification; unsafe whole-tree rollback and invented permission/overhead claims are removed. |
| `instruction-parity-check` | Read-only authority/entry checks and explicit repair handoff; exact protocol and consumer-integrity checks replace fuzzy similarity and clobbering project prose. |

### P06-C01: newly bundled README has unresolved local navigation

**Priority:** P2, must fix. **Confidence:** 10/10.
**Locations:** `bin\li-copilot.py:29-33,152-154,386-391`;
the copied links are at `README.md:171-174`.

P06 adds `README.md` to `DOCS`, so every vendored consumer now receives it under
`.github\lintel\README.md`. The README's following relative link targets exist in the
immutable source but are not included in the consumer bundle:

```text
docs/README.md
docs/faq.md
docs/concepts/engineering-modules.md
docs/concepts/pack-resolver.md
CONTRIBUTING.md
CODE_OF_CONDUCT.md
CHANGELOG.md
```

Reproduced on a pristine archive of the exact P06 product, selecting `other`, with no
P04/P05/P07/P08 overlay. `li-adapter.py init` returns 0 and creates 351 managed files.
The **installed bundle's own** `li-adapter.py check` also returns 0. An assertion over the
new README's source-existing relative file links then fails with exactly the seven
targets above. The same gap was observed after a real base-version Copilot installation
was upgraded to P06. This is not a generated README-table issue: regenerating that table
does not supply these files.

The integrity checker only checks native wrappers, Copilot entries and `START.md`; it
skips the newly shipped documentation bodies. Thus the passing installer tests and
`check` result do not establish this navigation boundary. In a fresh consumer, the
bundled product introduction cannot lead the reader to its documentation index, FAQ,
engineering-depth or pack guide through the supplied local links.

**Required repair:** preserve those routes with a deliberately closed documentation
bundle, or explicitly identify source-repository navigation and provide valid reviewed
source links where files are intentionally not bundled. Add an installed-consumer
regression that resolves the newly distributed README/guide links, rather than checking
only file presence and wrapper links. Retain notices and project ownership. Do not
expand this into copying private/internal knowledge or deleting useful methods.

The existing `docs\getting-started.md` pack-resolution link is also unresolved in a
consumer, but it was present before P06; it is not counted as another new finding.
This finding is limited to the README newly added to the distributed source surface.

## Stage 2: quality gate

**NOT RUN.** Stage 1 is not clear, so no quality PASS, code-quality severity sweep or
whole-tree compliance/release verdict is issued. Inspection and tests needed to establish
the component specification and the finding above are not being relabeled as Stage 2.
The builder must repair P06-C01, then a separately attributable reviewer must review the
new immutable candidate before this gate can advance.

## Actual verification

Environment: Windows, Python 3.11.9, Git Bash 5.3.15. Tests used disposable consumers,
fake HOME/USERPROFILE/XDG locations, isolated Git configuration and disabled bytecode
writes. No real client/model/account operation, private-profile access, remote Git/GitHub
call or hook activation occurred.
The task-approved jq executable was verified before use against SHA-256
`a6fc67fedaf9128a3309a1e2ebb8b986aeccf70122ee46d2cb4849e423f0c627`;
it was added only to child-process PATH, not installed/configured globally.

| Command or scenario actually run | Outcome and scope |
|---|---|
| `python -B -S bin\li-work-artifacts.py --repo . --map .claude\plans\universal-implementation\work.json` | PASS; the explicit approved map selects the original spec, plan/tasks and prompt. |
| `python -B -S tests\unit\client-capabilities.py` | 16 tests PASS, no skips. Real CLI subprocesses, malformed data, aliases, observation identities, permission and fallback behavior. |
| `python -B -S tests\integration\universal-adapters.py` | 8 tests PASS, no skips. All 38 selections/12 native roots, real installed consumers, explicit manual route, shared-root coexistence, conflicts, tampered inventory, spaces and fake-home refusal. |
| `python -B -S tests\integration\copilot-kit.py` | 22 tests PASS, no skips. Existing clone/update/protocol/ownership/CRLF/scaffold/resource negatives retained; actual symlink case executed. See fixture qualifications below. |
| Additional `resolve` matrix | 120 cases PASS: all 15 operations x four permission states x two availability states. No tool execution or independent-review clearance is returned. |
| Archived base installer -> archived P06 `init --client codex-cli` -> installed-source `check` | PASS. Legacy inventory without `clients` retains `copilot-cli`, adds Codex, preserves the Copilot wrapper and custom lessons, and is byte-idempotent on repeat. |
| Additional native-root boundary fixture | PASS. A `.agents` directory symlink is rejected before target/outside writes; an outside sentinel survives. Direct adapter commands leave the fake home empty and reject that home as a target. |
| Installed source identity/notices | PASS. Root LICENSE, design attribution and both third-party license files, actual `.claude-plugin\plugin.json`, and both canonical shim files match pinned source bytes and managed SHA-256 entries. |
| `tests\unit\cli-tiers.sh`, `tests\unit\copilot-capabilities.sh` via Git Bash | PASS. Compatibility aliases are conservative; unknown IDs warn and use manual hints without claiming runtime dispatch. |
| `tests\shape\welcome-wiring.sh`, `tests\unit\plugin-manifests-valid.sh`, `tests\shape\hooks-registration-safe.sh`, `tests\shape\frontmatter-lint-all.sh` via Git Bash | PASS; structural evidence only, not execution of native discovery, roles or hooks. |
| `python -B -S bin\li-instructions.py check` | PASS for all four synchronized entry/template blocks. |
| Actual checkout `tests\shape\cli-tiers-sync.sh` | Expected exit 1: coordinator-owned README table is stale. No root reducer was repaired or disguised. |
| Immutable P06 archive: instruction sync, catalog generation, wiki generation, local adapter init, their checks and CLI-table guard | PASS. A second generation is byte-identical across the disposable tree; hashes confirm authored checkout files were unchanged. |
| Exact disposable P06+P04 installed-source composition | Four real helper tests PASS with no skips, detailed below. |
| Pristine P06 manual consumer, installed `check`, newly bundled README link assertion | Reproduced FAIL, P06-C01: init/check return 0 but seven source-existing targets are absent. |
| Base/product scoped Git comparisons and `git diff --check` | PASS. Existing client manifests, hooks, synchronized protocol source, native generated wrappers/agents, catalog/wiki and generated inventory are not changed by P06. |

The Python `-S` runner and Universal install/consumer subprocesses exercise the new
standard-library paths. Not every legacy bundled shell helper or Copilot child process
was executed with site packages disabled; no such wider dependency-free claim is made.
Python 3.9 itself, macOS and Linux were not run by this reviewer.

### Fixture qualifications, not hidden passes

The initial test harness nested suite temporary directories inside the session-artifact
directory. Windows path-length failures caused seven Universal and fifteen Copilot test
failures. That run is retained as failed evidence, not counted as a pass. Repeating the
unchanged tests using the normal, shorter OS temporary location gave 16/8/22 passes,
without enabling long paths or changing product code.

The second harness also asserted an empty fake home after the complete legacy Copilot
suite. All 22 tests passed, but that additional harness assertion exited 1 because the
legacy scaffold/migration path wrote `.lintel\audit\migration.jsonl` **inside the fake
home**. `bin\li-scaffold:250-253` invokes the migration and
`bin\li-migrate-claude-home:198-202` deliberately records an operator-global migration
event. Both helpers are unchanged from the comparison base. This is not reported as
an empty-home aggregate pass or a newly introduced P06 installer defect. The Universal
suite and separate direct-adapter fixtures independently leave their fake homes empty.
All temporary fixture trees were cleaned; no real home/profile was used.

Session-local logs retain the actual runs: `p06-component-tests.log`,
`p06-component-tests-shorttemp.log`, `p06-upgrade-boundaries.log`,
`p06-structural.log`, `p06-p04-installed.log`, `p06-regeneration.log` and
`p06-bundled-navigation-negative.log`. These are supplemental scratch evidence, not
additional committed product or review artifacts.

### Exact installed P04 helper evidence

The reviewer independently archived the immutable P06 product, then overlaid only
the P04 delta between the two full refs above. The P04 and P06 changed-path sets were
checked for intersection; there was none. The generator remained byte-identical to
P06. No merge/cherry-pick or moving builder branch was used.

That exact generator installed a consumer selecting `codex-cli` and `copilot-app`.
Both source-driven and installed-source checks passed. Installed
`lib\envelope_contract.py`, `lib\swarm_snapshot.py`, `bin\li-envelope-validate`,
`bin\li-envelope-replay` and optional `lib\envelope-requirements.txt` matched immutable
P04 bytes and manifest hashes.

The real P04 `BriefForgeBoundaryTests` module was loaded from that exact source with
its `ROOT` pointed at the **installed consumer bundle**. These cases all passed:

- `test_actual_swarm_cli_brief_reaches_the_shared_handoff_boundary`
- `test_standard_library_default_and_missing_optional_yaml_parser`
- `test_json_replay_and_metadata_only_audit_do_not_imply_dispatch`
- `test_json_validator_rejects_duplicate_and_forged_nested_keys`

This verifies actual brief production, forge/validation/replay, malformed/duplicate
rejection and an explicit missing optional YAML parser. It does not prove agent dispatch,
the full P04 package, required-policy pinning, work lifecycle or final joined acceptance.

## Surface-by-surface boundary

All rows were selected by the real consumer installer and inspected through its installed
registry CLI. The routes below are generated files or a manual entry, **not live client
observations**. The source URLs, dates and version/condition strings were reviewed against
the pinned registry and host-source research; they were not independently refetched or
converted into runtime evidence in this review.

| Surface | Delivered repository route | Live workflow evidence |
|---|---|---|
| `claude-code` | `.claude/skills` | `not_run` |
| `claude-desktop` | `.claude/skills` | `not_run` |
| `copilot-cli` | `.github/skills` and three profiles | `not_run` |
| `copilot-app` | `.github/skills` and three profiles | Three partial source-reported question/delegation/worktree observations only |
| `copilot-vscode` | `.github/skills` and three profiles | `not_run` |
| `copilot-cloud` | `.github/skills` and three profiles | `not_run` |
| `codex-cli` | `.agents/skills` | `not_run` |
| `codex-desktop` | `.agents/skills` | `not_run` |
| `codex-ide` | `.agents/skills` | `not_run` |
| `codex-cloud` | Manual `START.md` | `not_run` |
| `cursor-cli` | `.cursor/skills` | `not_run` |
| `cursor-ide` | `.cursor/skills` | `not_run` |
| `cursor-cloud` | `.cursor/skills` | `not_run` |
| `gemini-cli` | `.gemini/skills` | `not_run` |
| `opencode-cli` | `.opencode/skills` | `not_run` |
| `opencode-desktop` | Manual `START.md` | `not_run` |
| `opencode-ide` | Manual `START.md` | `not_run` |
| `droid-cli` | `.factory/skills` | `not_run` |
| `factory-desktop` | Manual `START.md` | `not_run` |
| `factory-cloud` | Manual `START.md` | `not_run` |
| `antigravity-cli` | `.agents/skills` | `not_run` |
| `antigravity-desktop` | `.agents/skills` | `not_run` |
| `antigravity-ide` | `.agents/skills` | `not_run` |
| `kiro-cli` | `.kiro/skills` | `not_run` |
| `kiro-ide` | `.kiro/skills` | `not_run` |
| `kiro-web` | `.kiro/skills` | `not_run` |
| `devin-desktop` | `.windsurf/skills` | `not_run` |
| `devin-cli` | `.devin/skills` | `not_run` |
| `devin-local` | Manual `START.md` | `not_run` |
| `devin-cloud` | Manual `START.md` | `not_run` |
| `junie-cli` | `.junie/skills` | `not_run` |
| `junie-ide` | Manual `START.md` | `not_run` |
| `cline-ide` | `.cline/skills` | `not_run` |
| `cline-cli` | Manual `START.md` | `not_run` |
| `continue-ide` | Manual `START.md` | `not_run` |
| `continue-cli` | Manual `START.md` | `not_run` |
| `aider-cli` | Manual `START.md` | `not_run` |
| `other` | Explicit unidentified/manual `START.md` | `not_run` |

The 25 native-format surface selections share 12 roots; 13 selections remain manual.
Claude's preserved optional hook adapter is distinct from the portable kit, which
installs none. Legacy IDs select one surface, not a vendor-wide capability. An actual
tool binding remains separate from permission, attribution and evidence of execution.

## Final-pending gates and handoff

1. **P06 repair/re-review:** resolve P06-C01 in the product, reproduce the installed
   documentation-link regression as passing, and review the new exact candidate.
   Stage 2 remains outstanding until the component spec passes.
2. **P04/P07 resource preflight:** after the approved producers land, explicitly require
   `lib\envelope_contract.py`, `lib\swarm_snapshot.py`, `lib\profile_context.py` and
   `lib\profile-context-schema.json`, with one-at-a-time missing-source refusal before
   target writes. Broad bundling and the positive P04 composition do not waive this gate.
   These absent future-module checks are acknowledged integration work, not counted as
   an additional P06 component defect against this pre-integration source.
3. **P05 evidence:** the Codex skill delegates mapped prepare/log/latest-reader/
   corroboration and non-release snapshot/inspect to the shared owner. Validate those
   against the final actual helper/schema, including mandatory-control failures and
   missing corroboration. The report's later P05 source
   `7a7a50a1273ec4c04ed51118a9cfb2e3c85b246d` was not composed or executed here.
4. **P07 policy:** unchanged `profile_ref` transport is not pinning or enforcement.
   The coordinator-reported shell-reference policy-loss defect in older P07 `912420f`
   remains a joined gate for the repaired source; it was not independently reproduced
   in this P06 review. Exercise reference-only resume and required-policy retention
   through actual installed helper shells.
5. **P08 work identity and final integration:** retain original work-map paths, leaf IDs
   and policy/review identity through real execution and recovery. Rebuild all shared
   reducers on the reconciled tree, run joined negative/consumer tests, strict suite
   and CI, then obtain independent integrated review. None is waived by this component.
6. **A24 live acceptance:** all new live client/model/account behavior is unrun.
   Separately authorize and record exact host/version/revision, native discovery,
   actual tool/permission use, independent review and cold resume before advertising
   support. No real private-profile or enterprise-control validation occurred here.

The next action is the bounded P06 documentation-bundle repair, not a product mutation
by this reviewer or release approval. The remaining packages and final reviewer retain
their original responsibilities.
