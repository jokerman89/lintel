# P13 remaining consumers independent review

**Complete released-unit SPEC: FAIL. QUALITY: NOT STARTED. P1: 0 / P2: 1 / P3: 0.**
Same distinct reviewer as the accepted compact-discovery and A+B units. No product
implementation, repair or nested reviewer. This is source-consumer review, not
model/client execution, native A13/P08, P10, whole-P13/initiative or SHIP acceptance.

## Exact authority and selection

| Item | Identity |
|---|---|
| Released authority and sole product parent | `a5d77f93dc40f2968bff7fd6aa3eacd5ccaee92e` |
| Frozen product | `7884ddd0e4880d09c6cf3025822c6f5a0ed0c161` |
| Report-only checkpoint, sole parent product; required review parent | `5df8e9977a091b1a2c207cae2274dbae0f3a9969` |
| `reports/P13.md` Git-byte SHA-256 | `abb031bbe2beec682b920fb53648d545ec52c2984ffebb0a63cec0b81f3907a0` |
| Retained first-unit PASS | `09a3c6ec3c3fa2c3232e921f52accc9262088e8b` |
| Retained A+B PASS | `7bf3f253a77bcf18efb2dc0365cb560dfbad7237` |

Read startup/Copilot/Universal contracts, accepted ADR-0028/0029, relevant memory,
selected work/spec/plan and original A18/A19/A20 acceptance. Read the full 214-line
P13 card, including the explicit welcome/status body transfer at lines 164-214.
Underlying P06/P08/P07 providers remain outside this owner's write scope.

Independently verified both sole-parent links, the entire twelve-path base-to-product
diff and the report-only delta. The 736-line report retains the exact previously read
546-line prefix; all new lines 547-736 were read. Prior accepted reports are retained
evidence, not newly issued acceptance. No later parent WIP or blocked P10 engine was imported.

Exactly these twelve product paths were selected:

| Paths | Responsibility |
|---|---|
| `skills/catalog/SKILL.md`, `skills/help/SKILL.md`, `skills/skill-router/SKILL.md` | Selection-aware metadata-first discovery and bounded body guidance |
| `skills/welcome/SKILL.md`, `skills/status/SKILL.md` | Nonmutating orientation and original work/cycle/profile observations |
| `skills/skillify/SKILL.md`, `scaffolding/01-foundation/TEMPLATE-skill.md` | Owned draft preflight, useful authoring method and exact-file validation |
| `skills/uniformity/SKILL.md`, `skills/eval/SKILL.md` | Real diagnostic exits and honest scoped calibration |
| `skills/catalog/references/consumer-checks.md` | Actual-test versus instruction/model evidence boundaries |
| `tests/unit/catalog-consumers.py`, `tests/unit/catalog-consumers.sh` | Focused consumer checks |

Reviewer writes are this report and private evidence only. Original rejection and
both earlier PASS refs remain preserved; product, builder report and shared state are immutable.

## SPEC result and finding

Complete scoped SPEC was frozen **2026-09-22 20:53:39 UTC**. One required control
fails; the other eleven pass at their stated source/test evidence level. No aggregate
score overrides the failure, and QUALITY has not begun.

| ID | Severity | Source | Confidence | Finding and required correction |
|---|---|---|---|---|
| F01 (consumer unit) | P2 | `skills/skillify/SKILL.md:96-103`, specifically `:99` | 10/10 | The new-destination guard uses ordinary `draft.exists()` after the shared safe-path resolver. On the actual Windows host it returns false for an existing owned 297-character draft path, so the shipped preflight exits 0 and prints the path as usable. Observe existence through the already accepted native-path spelling, retaining logical identity/ownership, and add this caller regression. No provider or installer redesign is needed. |

**Concrete reproduction:** in a synthetic authorized target, use noncolliding
`skill_name=private-repeatable-task` and create
`drafts/bounded-<72 a characters>/existing-<55 b characters>/SKILL.md`.
The selected target makes the full logical path 297 characters. Its existing content is
`EXISTING OWNED DEEP DRAFT\n`, SHA-256
`bf6ce5e717df278e50d11785693086c68ebb6e34cd6ec2db1a6daa46a7b36d72`.
Run the unchanged shipped **Check name and destination** Bash block with the explicit
existing Python executable. The accepted `safe_path` resolves this file;
`native_io_path(draft).is_file()` is true while `draft.exists()` is false.
Actual result: exit **0**, stdout is the logical draft path, stderr empty.
Expected: the existing refusal path, exit **2**, before any authoring.

This was reproduced twice with exact caller/environment receipts. The normal shorter
existing-draft control refuses correctly. The preflight's wrong success can mislead the
subsequent authoring step; **no model authoring or overwrite was executed**, and the
existing file and complete fixture tree remained unchanged. The defect is this
consumer's existence observation, not a new general Windows/Git compatibility project.
It violates the commissioned nonoverwrite control, the released card's owned-target
requirement at lines 191-197 and the skill's step 5 at lines 60-62. Earlier
compact-discovery F01/F02 stay closed.

| Control | Verdict and evidence |
|---|---|
| S01 - Exact release and preservation | PASS: exact chain/scope/hash; all 196 opening headers and modes preserved, all 69 role blobs unchanged, 127 skills/46 aliases, 126+Swarm map, catalog, descriptors and all provider/installer paths unchanged. |
| S02 - Catalog/help/router | PASS: actual literal queries/selections preserve canonical/alias IDs and 15-member demo/core closure. Ordinary discovery remains available. At-most-three body selection and role/manual boundaries are structural instruction evidence, not model behavior. |
| S03 - Welcome | PASS: actual registry/query/footer reads, staged PDF description and unknown maturity retained; unrelated cwd/target decoys do not execute; orientation creates no runtime state. |
| S04 - Skillify new owned destination | **FAIL, F01:** canonical/module alias and short existing-path controls refuse, but the confirmed existing deep draft is incorrectly admitted as new. Bare names versus wrappers and literal-input handling otherwise remain intact. |
| S05 - Template and exact-file validation | PASS: real opening header, explicit ownership, lesson/method/exclusions/examples retained. Actual `validate_lintel_frontmatter` rejects missing/header-body-decoy/unclosed headers. Field presence is not claimed as semantic validity, host support or activation. |
| S06 - Uniformity | PASS: real trusted floor and generator on owned fixtures; workflow and block-hook floor failures retain nonzero exits. Clean, stale, missing/error and recorded-matrix-only outcomes are distinguished without regeneration or target fallback. Injected exits remain labeled injections. |
| S07 - Original work and cycle | PASS: actual readers retain original IDs across two initiatives/current or explicit cycles, conflicting maps refuse, STARTING/BLOCKED/INCOMPLETE do not become DONE; `release_clearance: false` remains false. |
| S08 - Profile and read errors | PASS: real data-only verify then required-policy with the verified reference; same-mtime drift, missing pin, mismatched reference/policy and missing/malformed original artifacts refuse without rebind, audit writes or partial success output. |
| S09 - Jobs and footer | PASS: mapped work remains visible with absent jobs; repo-local observations and opt-in archives never select the synthetic personal registry. Job command text remains data. The actual status/footer composition stays on the explicitly selected cycle. |
| S10 - Eval truthfulness | PASS at source/arithmetic level: separate good/bad denominators, expected/evaluated counts, fixed input/evidence scope, partial/empty/insufficient/unrun limits and owned output. No evaluator/model/gateway/audit/ship enforcement was run or inferred. |
| S11 - Actual caller/no-write evidence | PASS: shipped Bash blocks exercised with accepted providers and inspected synthetic environments; full fixture file/directory snapshots and source seals unchanged on positive and refused reads. F01 is incorrect admission, not a performed write. |
| S12 - Retained and bounded checks | PASS: 97 frozen/retained methods, three focused shapes, exact source/header checks, stdlib catalog check and syntax checks, with the invocation/aggregation qualifications below. |

## Actual checks, failures retained and limits

| Check | Actual result |
|---|---|
| Frozen consumer methods | 31/31 PASS |
| Retained metadata / selection / registry methods | 31/31, 19/19 and 16/16 PASS; 97 distinct methods total, no skips |
| Independent scenarios | Nine distinct methods: eight valid PASS, one product FAIL (F01), after only the two command-spelling cases were rerun using the documented existing Python |
| F01 confirmation | Existing native file observed; unchanged caller again exits 0; file/tree unchanged |
| Focused shapes | Catalog drift, deprecated aliases and frontmatter shape checks passed; catalog invocation adaptation below |
| Source facts | Exact twelve-path delta; unchanged 196 headers/69 role bodies/modes, aliases/map/catalog/providers; canonical JSON has 196 entries, 46 aliases, unknown maturity and `executed: false` |
| Default dependency floor | Actual `python -I -S -B bin/li-catalog.py --check`: exit 0, exact `Catalog matches skill frontmatter.` Windows CRLF message |
| Syntax | Consumer Python passes Python 3.9 grammar; 17 skill-body Bash blocks plus one consumer-reference Bash block pass `bash -n` |

The 97 methods ran directly through an inspected outer Python harness with unchanged
test sources; this reviewer did not claim another wrapper run as extra coverage.
Actual status/profile setup writes are explicitly fixture preparation; the subsequent
consumer calls are read-only. The existing injected resume-reader and uniformity exits
test propagation and are not mislabeled as native provider failures.

All initial failures remain in private evidence. The first independent run had six
passes and three failures: F01 plus two absent-`python3` command-spelling failures.
Those two pass through the documented existing-Python route: an ephemeral Bash function
forwards `python3` to the inspected executable, leaving the literal caller block unchanged.
No executable, package, PATH installation or global setting was added. The unadapted
catalog shape reported SKIP; it is not counted as completed drift evidence. Its adapted
run executed the actual check. A separate reviewer roll-up incorrectly expected 17
blocks across both skills and reference after all 18 syntax calls succeeded; its true
nonzero aggregate is retained and the corrected 17+1 count was rechecked. None of these
reviewer corrections repairs or excuses F01.

Every outer product import/call and launched child was inspected under allowlisted
synthetic HOME/USERPROFILE/AppData/temp/XDG/Claude/Copilot/Lintel/source/target/derived
roots, explicit PATH/PATHEXT and fixture Git ceilings. Bash startup's synthetic path
conversion was inspected before product calls. Source Git EOL identity remained separate
from fixture configuration. Logs were opened before commands and real exits retained.
This is inspected test isolation, not a claim of a host-enforced security sandbox.

Private evidence: `p13-consumers-review/`, including selection/authority/diff, original
and adapted receipts, complete snapshots, preserved harness versions, `finding-f01.json`,
`spec-decision.json` and source-check records. The 2,315-file evidence manifest SHA-256 is
`8d78728f685828873109fde3eac5a36a38625000e1498861aa242b2f2e48f145`.
It includes the actual deep draft using the accepted native spelling. Report delivery
receipts are separate. Builder's prior failures/owned-cleanup history remains unchanged
in its report; reviewer reruns do not rewrite that history.

Actual host: Windows build 26200, Python 3.11.9, existing PyYAML 6.0.3 and Git Bash.
Python 3.9 is grammar-only evidence; no minimum-runtime, Linux/macOS, full-suite,
new dependency, private-home/global-state, network, native P08/P10, installer or model
run occurred. Accepted first-unit/A+B knowledge and maps were reused, not a new
196-body/126-record audit. The parent's actual installed P06 pilot remains separate
evidence and does not close P10.

## Next action

Recovery `88aecc43-40f9-41d4-8947-6c2fb0a55481` routes F01 to original owner
`c4e9de1c-1c81-4897-ba82-019d58b635d7` for the bounded skillify observation/regression
repair. Preserve this frozen source/report and failed evidence; return a new exact
product/report pair to the SAME reviewer. Recheck the complete released SPEC using
unchanged evidence where valid, then perform the first eligible QUALITY. No new
provider, platform sweep, reviewer or broader acceptance is requested.
