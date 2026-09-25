# P04 component review at 02be6cb

Date: 2026-09-20

## Decision and scope

**Stage 1 specification: FAIL; changes required.** Finding counts: **P0 0 / P1 2 /
P2 1 / P3 0**. **Stage 2 integration quality: not reached**, because specification
approval is a prerequisite. This is an independent component review: the reviewer
did not implement the product changes and made no product fixes.

| Reference | Exact commit |
|---|---|
| Reviewed candidate | `02be6cb1448cd9def1572ae55e321f07d974a33b` |
| Candidate parent, public-accessor correction | `8ea0fc4e4280803d1093468d06828daa54f9c700` |
| Product-delta base, historical merge checkpoint | `e74849db6b33c7b93baadb86206009cb9f9eb6d5` |
| Preserved, accepted historical review commit | `4bf5315d4636206f1df6a5f0c7a68a52e9341cae` |

The reviewed range is the full `e74849d..02be6cb` product/component delta, including
the narrow `8ea0fc4` ancestor: 30 paths, 3,031 insertions and 1,406 deletions.
Inspection and tests used a clean, separate candidate checkout under this
reviewer's workspace. The original review branch and `4bf5315` were unchanged.
The later report-only commit is not the reviewed product snapshot.

Authority: repository/Copilot instructions; the P04 package card and Universal
specification; the exact SW-01..06 audit and A21/A22 action plan; preservation
requirements; current P04 implementation/preservation reports; accepted ADR-0026
and reconciled ADR-0027. Findings below are **unclosed component acceptance gaps**,
not newly attributed regressions in the previously accepted historical merge.

**A22.7 and final Swarming/Universal acceptance remain OPEN.** In particular,
declared actor references are not independent corroboration, and this review does
not close the P05/P07/P08/P09 binding or review the final combined initiative.

## Findings

All line numbers refer to the immutable candidate above.

| ID | Severity | Primary location | Specification consequence |
|---|---|---|---|
| F01 | P1 | `lib/swarm_contract.py:116-134` | Hard-linked handoff artifacts bypass coordinator ownership protection. |
| F02 | P1 | `lib/envelope_contract.py:74-79` | A malformed legacy YAML constructor exposes forbidden payload in diagnostics before validation. |
| F03 | P2 | `lib/swarm_contract.py:465-468` | Valid root-level package edit boundaries are silently discarded. |

### F01: hard-linked report/review can alias the authoritative plan

`_path_identity` resolves pathname components and symlinks, but two hard links to
one existing file retain different identities. `_validate_artifact_ownership`
uses that comparison at `lib/swarm_contract.py:587-594`; actor scope subsequently
allows the lane's own report/review at `lib/swarm_contract.py:730-739`.

Reproduced twice in fresh `SwarmFixture` directories: create the declared report
parent, then `os.link(root / "plan.md", root / lane["report"])`; repeat separately
for `lane["review"]`. In both cases `os.path.samefile` confirms that the artifact
and authoritative plan are the same file. Coordination validation succeeds,
the real `li-swarm.py validate` exits 0, and `check_lane_scope` accepts that
artifact for the corresponding worker/reviewer actor. No write through the
linked artifact was needed or performed.

The permitted ordinary report/review write would therefore mutate the mapped
plan itself. This contradicts A22.3.a and the charter's filesystem-alias rule;
the actor-specific and reducer safeguards cannot receive blanket acceptance
while their shared ownership comparison has this hole. Existing symlink and
ancestor negatives do not cover hard links. This is a local filesystem ownership
defect, not a claim that Git commits encode hard-link relationships.

Required correction: compare existing files by same-file identity as well as
retaining lexical/resolved ancestor checks for paths not yet created. Add
hard-link negatives for authority/handoff ownership and both actor scope paths.

### F02: invalid YAML boolean leaks the rejected scalar through a traceback

The optional PyYAML path catches `yaml.YAMLError`, but the supported parser's
boolean constructor raises `KeyError` for an invalid explicitly tagged scalar.
The outer exception list at `lib/envelope_contract.py:579-582` does not handle
that error. `lib/brief-forge.sh:128-129` redirects construction stdout, not its
stderr, so the exception text reaches the full public handoff caller.

Reproduction used a synthetic lowercase forbidden marker, generated as
`"sk-" + "z" * 45`, in this otherwise bounded brief:

```yaml
task: !!bool <synthetic-marker>
constraints: [local only]
acceptance: [reject without echo]
```

With already-installed PyYAML **6.0.3**, both `forge_handoff subagent_spawn swarm
FixtureWorker brief <file>` and `bin/li-envelope-validate <file>` exit 1 with empty
stdout, but stderr contains a traceback and the **exact synthetic marker** in
`KeyError`. An earlier unsupported-extra-field variant also reached the same
constructor failure. No actual secret was used. No marker was found in the
temporary audit records, and no receiver envelope was released.

Thus this is a diagnostic disclosure, not successful dispatch or raw-payload
audit persistence. It violates A21.2 and the documented promise that rejected
payloads are never echoed in diagnostics. Ordinary JSON forbidden-content
rejection is safe, and the `python -S` missing-optional-parser path fails safely;
neither covers this installed-parser branch.

Required correction: normalize optional-parser constructor failures to
payload-free diagnostics before a traceback can escape. Add this invalid-tag
case at the actual handoff and validator boundaries, asserting absence of the
marker from stderr as well as stdout and audit.

### F03: package boundary recognition requires a slash

The package parser retains an `Owner / edit boundary` entry only when it contains
`/`. Enforcement at `lib/swarm_contract.py:519-522` is conditional on a nonempty
result, so dropping every legitimate root-level path disables that check.

Reproduced with an authoritative package row selecting leaf `T1`, boundary
`builder; README.md`, and a lane claiming `write_scope: ["docs/output"]`.
Both library validation and the real validation CLI accept it. A root directory
boundary `builder; src` also accepts the unrelated scope. The control boundary
`builder; src/core` correctly fails with `package.scope` and CLI exit 1.

The canonical package template permits allowed paths/components; it does not
require nested paths. Root files and directories are normal ownership choices.
Silently treating these explicit restrictions as absent violates
SW-02/A22.4.b, even though leaf membership/dependency and nested-boundary tests
pass.

Required correction: recognize valid repository-relative root files/directories
without requiring a slash, and do not turn an uninterpretable explicit boundary
into unrestricted scope. Add root-file/root-directory positive and widening
negative cases.

## Audit and leaf dispositions

The current implementation report's SW-01/SW-02/SW-04/SW-06 clearance and
all-alias/boundary assertions at `reports/P04.md:52-57,76-79`, and its absence-of-
local-P1/P2 statement at lines 60-62, are not confirmed by this review. The listed
tests did pass, but they omit the cases above. A21.2's broad rejection claim at
line 81 also needs qualification. These are not accusations of fabricated test
execution: the independent counterexamples limit the claimed coverage.

| Audit finding | Component disposition |
|---|---|
| SW-01 | Incomplete: F01 defeats the promised authority/alias protection. |
| SW-02 | Incomplete: F03 loses explicit root-path package ownership. ADR and real leaf-format reconciliation are preserved. |
| SW-03 | Local content/attempt/report binding improvements observed; actor corroboration and shared trust binding remain OPEN, not repaired by distinct strings. |
| SW-04 | Machine-readable coordinator/reducer paths and direct/ancestor negatives work; F01 prevents complete alias-protection acceptance. |
| SW-05 | Actual rich brief-to-JSON/Forge bridge works and preserves content/references; the separate A21.2 diagnostic boundary remains blocked by F02. |
| SW-06 | Direct worker/reviewer scope separation works, including real Git reviewer diffs; the aliased own-review case in F01 remains unsafe. |

| P04 leaf | Review disposition and evidence |
|---|---|
| A22.1.a | Preserved. Both merge parents, historical Swarming, main and the public-accessor ancestor remain ancestors of the candidate. |
| A22.1.b | Preserved. Coordinator plan/spec/prompt/work map/todo and current memory are unchanged from the accepted merge. Hybrid sources remain unchanged. |
| A22.1.c | Source preservation confirmed for enterprise/source-target and work-map consumers; actual callers inspected. No independent rerun of the implementer's six Copilot-kit scenarios is claimed. |
| A22.1.d | All 76 mapped source destinations and file modes retained; historical records remain unchanged. |
| A22.2 | Main ADR-0026 byte-identical; original Swarming decision body retained under unique ADR-0027, with additive reconciliation. |
| A22.3.a | FAIL: F01. Other direct, ancestor, symlink/junction and cross-artifact cases are covered by passing focused tests. |
| A22.3.b | Partial: reducer declaration and separate actual actor diffs verified; shared alias gap F01 prevents full clearance. |
| A22.4.a | Real flat/phased/tree short-leaf and Spec Kit formats, plus legacy singletons, verified by focused fixtures and parser/template inspection. |
| A22.4.b | FAIL: F03. Membership, acceptance, dependencies, review depth and per-leaf evidence checks otherwise exercised. |
| A21.1 | Explicit invocation retained; no automatic host callback, scheduler, hook activation or receiver dispatcher added. Disabled/bypass is not success. |
| A21.2 | FAIL: F02. Other exercised payload/shape/evaluator/audit failures block release; malformed YAML diagnostics do not meet the confidentiality contract. |
| A21.3 | Rich Markdown preserved unabridged as data; actual CLI exports work/package/leaf/scope/acceptance references. Default JSON/Markdown path works without third-party Python packages. |
| A21.4 | Public-accessor, trusted-source, evaluator and audit-receipt paths exercised. Missing optional YAML parser is explicit and safe; installed-parser failure still requires F02's correction. |
| A22.5 | Local actual Git/result/acceptance/report binding, stale/rework rejection and explicit verification-only work exercised. File-only and declared-actor limitations remain explicit. |
| A22.6 | Local native-capacity/serial/manual selection, genuine isolated Git fan-in, interruption and conflict recovery exercised. This does not certify client spawning or real actor independence. |
| A22.7 | OPEN by instruction: final P05/P07/P08/P09 contract binding, corroboration and combined-tree acceptance are outside this review. |

## Checks actually run

Commands ran from the pinned candidate with temporary homes, configuration,
pack stores, audits and test repositories. Global/system Git configuration and
prompts were disabled; tests did not activate hooks. Python bytecode writes
were disabled. Existing Python 3.11, Git Bash and the authorized jq 1.8.2 were
used through a per-process PATH; jq's supplied SHA-256 was verified. Nothing was
installed, no real network/authentication was invoked, and no agents were spawned.

| Check | Actual outcome |
|---|---|
| `python -B tests/unit/swarm-contract.py` | 40 tests passed; 43.096 seconds. |
| `python -B tests/integration/swarm-workflow.py` | Mapped/legacy workflow and actual Git isolation/fan-in/conflict/recovery scenarios passed. |
| `python -B tests/integration/brief-forge-boundary.py` | 14 tests passed; 192.690 seconds, including real CLI/Forge and stdlib-only paths. |
| Independent hard-link probes, report and review separately | Reproduced F01: same physical file, validation success, actor scope success, real validation CLI exit 0. |
| Independent package-boundary probes | Reproduced F03 for `README.md` and `src`; slash-containing `src/core` control rejected correctly. |
| Independent malformed-YAML full handoff and validator probes | Reproduced F02 in both public paths with exact lowercase-marker assertions; empty stdout, marker in stderr, not audit. |
| Same YAML probe under `python -S` | Safe nonzero failure with explicit optional-PyYAML diagnostic, no traceback or marker echo. |
| Ordinary forbidden JSON and false-success audit-writer controls | Forbidden JSON safely rejected; a writer returning 0 without a persisted receipt still produced failure/no envelope. No false-success handoff finding for that audit path. |
| Object-based ancestry, inventory and historical preservation checks | All comparisons described below passed after a Windows path-length harness correction. |
| `git diff --check e74849d 02be6cb` | Passed. Both reviewer checkouts were clean before authoring this report. |

The actual Git integration creates independent temporary worker worktrees,
checks worker and reviewer base/head diffs, preserves a report-only interrupted
attempt as `awaiting_review`, rejects close until review exists, merges passing
lanes serially with ancestry checks, rejects a new untracked scoped file, and
blocks on a deliberate merge conflict while retaining both change sets.
Manual review export does not manufacture PASS. Its synthetic actors test
binding mechanics, not real independent people/models or host permission policy.

Preservation was checked against Git objects, not a working-tree approximation:
all 76 source-delta paths have retained destinations/modes and exactly match the
preservation inventory; 60 destinations remain byte-identical to the merge;
all 17 original swarm artifacts (including briefs/reports/reviews) and all 23
historical Swarming plan paths remain unchanged; 26 memory/audit/package paths and five coordinator
authority paths remain unchanged. Main ADR-0026 is identical, the original
Swarming ADR's context-onward body is retained, and all 27 ADR numbers are unique.
Enterprise helpers, hybrid plan/build sources and entry documents checked against
the merge are unchanged.

One initial `git show ref:path` comparison hit Windows' long-path ambiguity.
It was not counted as a pass. The completed comparison used tree object IDs and
`cat-file`, with command-local long-path support, and all assertions passed.

## Reviewed changed paths

```text
.claude/decisions/0027-first-class-swarming.md
.claude/plans/universal-implementation/reports/P04-preservation.md
.claude/plans/universal-implementation/reports/P04.md
bin/li-envelope-replay
bin/li-envelope-validate
bin/li-swarm.py
docs/concepts/brief-forge.md
docs/concepts/envelope.md
docs/concepts/swarming-work.md
lib/brief-forge-evaluators.sh
lib/brief-forge.sh
lib/envelope-requirements.txt
lib/envelope-schema.yaml
lib/envelope_contract.py
lib/swarm-schema.json
lib/swarm_contract.py
lib/swarm_snapshot.py
scaffolding/01-foundation/templates/swarm/agent-brief.template.md
scaffolding/01-foundation/templates/swarm/agent-report.template.md
scaffolding/01-foundation/templates/swarm/agent-review.template.md
scaffolding/01-foundation/templates/swarm/charter.template.md
scaffolding/01-foundation/templates/swarm/coordination.template.json
skills/brief-forge/SKILL.md
skills/swarm/SKILL.md
tests/integration/brief-forge-boundary.py
tests/integration/brief-forge-boundary.sh
tests/integration/swarm-workflow.py
tests/shape/brief-forge-handoffs-canonical.sh
tests/unit/brief-forge-evaluator-runs.sh
tests/unit/swarm-contract.py
```

Actual consumer inspection included `bin/li-copilot.py` and
`bin/li-work-artifacts.py`. The Copilot generator's broad `bin`/`lib` resource copy
includes the new modules; an incomplete explicit preflight list is not evidence
of a missing bundled module. P06 dependency-preflight integration remains the
implementation report's declared follow-up, not a new finding here.

## Limitations and handoff

No whole-repository suite, production operation, real client session/spawning,
private-home configuration, deployment, remote action or final shared-contract
integration was exercised. Additional checks listed only in the builder's report
were not relabeled as reviewer execution. Git regular-file snapshots and
CRLF-normalized text identity are not validation of symlink/submodule delivery;
file-only snapshots cannot prove a base diff or host isolation.

The prior historical merge-preservation acceptance is unchanged. This candidate
requires F01-F03 corrections and a new bounded specification review before
quality Stage 2 can run. Even a later component PASS cannot close A22.7 or replace
independent review of the final reconciled initiative.

The sole authored artifact is this report. No product findings were fixed, no
shared plan/memory/historical evidence was edited, and no source branch was
modified. Hand back this report's local commit SHA with the failed specification
verdict; do not treat its commit as a different reviewed product candidate.
