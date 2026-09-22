# P11 direct design recheck

**2026-09-22: complete scoped SPEC PASS; first whole eligible QUALITY FAIL.**
D1-D3 are closed. Open findings: **P1 0 / P2 2 / P3 0** (D4-D5 below).
Hold A14.1-A14.4 direct-unit acceptance. Accepted A16 is unchanged; this does
not accept A14.5, all P11 or release clearance.

## Immutable scope and reviewer

Same independent reviewer: app `d823e773-d8dc-4d02-9716-77506a7a260e`, CLI
`1f655ca9-eb2b-4325-9996-72ed8539c13b`, distinct from builder `f413bdcb`.
No product fix or nested reviewer. Prior `5d3404a` and accepted A16 review
`3049811` refs are preserved.

| Input | Verified identity |
|---|---|
| Original complete design base | `336513e0178a1e9df39286ac7a69de5989f7a5ef` |
| Repair source | `7c3940f07481d2ae9ac7aa3350501c7b3b26069d` |
| Repair parent, artifact-only report | `5e2a94000561e6d69232ed19ab900c65bc0264c1` |
| Builder report / this review's parent | `e96dd0f765cde0c7d4c4b082cb5d4c76e921894e` |
| Builder report Git-byte SHA-256 | `d1f542794c1fc2a7cf43f8b65cdfa6d05db159edece6cbbcc7dc981d525bdfe1` |
| Repair authority | `0e84e6c6c5d1acc94d54af80816b6f68d8c47321` |

Verified the full original 24-path unit, all four repairs and report-only child.
The 1173-line report preserves its exact 975/1090-line historical prefixes;
both intervening appendices (115 artifact-history lines, 83 repair lines) were
read completely. Source was clean/detached and sealed before execution.
The 20 other design paths, shared providers and accepted browser source are
unchanged; this is not a four-file-only review or an A16 re-audit.

Selection remains the five frontend roles, thirteen design/frontend/generate
skill methods, common schema/helper/reference and three focused tests enumerated
in `5d3404a`. Complete manifest and 62 input seals remain in private evidence.
Only this report is added by the reviewer.

## Sequential per-leaf results

SPEC completed before QUALITY. Earlier passing unchanged DNA/token/static and
five-role method-preservation evidence remains applicable; current direct tests
recheck real P03/P05/P07/P09 calls, not a replacement mocked contract.

| Leaf | SPEC | First whole QUALITY |
|---|---|---|
| A14.1 | PASS: D1-D3 and original shared design/profile/control/domain scenarios pass. | FAIL: D4 loses the pipeline content identity; D5 breaks the retained solo-fragment validation route. |
| A14.2 | PASS: both canonical envelope names, literal paths, variant/stack/output/customer-share and option negatives pass. | FAIL: D4 maps a run whose consumed content differs from the verified source. |
| A14.3 | PASS: none/CSS/empty-library, both no-shader forms and unrelated mandatory controls retained. | FAIL for solo method completion through D5; no forced-library/no-shader correction is reopened. |
| A14.4 | PASS: actual bound manifests constrain both flags; genuinely new/supported projects and profile precedence/drift cases pass. | PASS in reviewed scope: actual-source/version/license fields are data, not legal/runtime certification. |

**D1 closed:** alternate frontend and pipeline filenames remain inspectable but
directory mapping refuses them; canonical positives preserve the exact selected
file. **D2 closed:** original React/react-scripts-to-Next input refuses for both
`existing` values, including nested/case-varied manifests; supported stacks pass.
**D3 closed:** web and app now require an active non-`none`, non-null-library
shader; null and non-null no-shader objects remain dependency-free. These are
data/method results, not observed renderer output.

## QUALITY findings

| ID | Severity | File:lines | Finding and bounded fix | Confidence |
|---|---|---|---|---|
| D4 | P2 | `skills\design-dna\scripts\design_contract.py:212-214,343,380-385`; `skills\generate-web\SKILL.md:62-69` | The pipeline binding verifies an arbitrary brief/content file, but `--from-pipeline <run>` consumes `<run>/content.md`. Bind/check that exact consumed path and hash before directory handoff, or use a genuinely supported exact-input interface. Preserve valid canonical content; no new schema/provider is needed. | 10/10 |
| D5 | P2 | `skills\frontend-typography\SKILL.md:59,151-152`; `skills\frontend-motion\SKILL.md:61,172-173`; `skills\frontend-shader\SKILL.md:59,125-126` | Retained solo `out=/dev/stdout` is passed to the new rooted-file validator, which rejects it. Validate parsed fragment data before stdout emission, or validate an owned relative staging file and then emit it. Preserve solo use and P03's boundary; do not allow special/absolute files or silently require `--out`. | 10/10 |

**D4 actual counterexample:** canonical `run with spaces/design-spec.json` binds
`brief with spaces.md` and its matching `source_content_hash`; both that file
and a different `run with spaces/content.md` are current, selected fixture files.
Actual `load_design` reports `verification:current_inputs`; mapping returns
`generate-web --from-pipeline "run with spaces" --variant single-file --out output`.
The documented consumer reads the sibling `content.md`, whose SHA-256 differs
from the verified brief. The positive case with the binding naming that sibling
passes. No renderer was executed; the defect is the verified-input/consumer-path
mismatch, not a fabricated visual outcome.

**D5 actual counterexample:** valid typography, no-motion and no-shader fragments
pass the API and named relative-file CLI (exit 0). Each documented default call
with `--file /dev/stdout` returns exit 2:
`ERROR [lintel/design]: Unsafe relative path: '/dev/stdout'`.
Rejection occurs before outside I/O. The stdout default predates this unit;
the cumulative unit's newly wired validator does not preserve that declared
route. This is a caller integration correction, not a new OS or CLI feature.

## Actual checks and preserved evidence

| Sealed reviewer command | Outcome |
|---|---|
| `bash --noprofile --norc tests\integration\design-contract.sh` | Exit 0; 14/14 tests, zero errors/failures/skips; own run `d-6t9uo9rs`, browser/rendered artifacts `not_run`. |
| `bash --noprofile --norc tests\integration\frontend-design-roundtrip.sh` | Exit 0; actual Python compatibility reader ran; optional jq assertions used the existing grep branch. |
| `python -I -B <private>\spec_probes.py` | Exit 0; 6/6 independent SPEC cases, including exact D1/D2 reproductions, D3 source-backed predicates, preserved mappings/precedence and mandatory-control negatives. |
| `python -I -B <private>\quality_probes.py` | Exit 1; 7 cases, 5 pass/2 failures, zero errors/skips. D4/D5 reproduced. |

Passing QUALITY probes cover non-clearing/deep-copy behavior, exact provenance
sets/override evidence, JSON/version/path refusal, projection conflicts/active
shader fallbacks and QA-evidence mutation. The full source/method review covers
correctness, failure/ownership boundaries, boundedness, maintainability and
coverage across all 24 selected paths. No aggregate pass erases D4/D5.

Every product call/import, including outer comparisons, used inspected
per-process synthetic allowlisted HOME/USERPROFILE/AppData/temp/XDG/LINTEL and
derived roots, explicit PATHEXT and fixture Git configuration/ceilings.
All 62 product/provider/test seals stayed unchanged. No running script edits,
dependency install, personal configuration access, source fix, extra actor,
browser/server/native operation, network call or full suite occurred.

Private evidence is in this CLI session's `files\p11-design-recheck\`: pin,
sequential stage checkpoints, fixtures, command/environment/seal records and
complete logs. Reproducer SHA-256:
`cbcb0997f0c679b7da904425f456a83f9dcdb076786c049d82c428148a562cf7`;
observed counterexamples SHA-256:
`09e89b9197a12e872d4b94c52768334b2d09ba80efd53611cc074a51d92ded93`.

## Limits and next action

Artifact-only `5e2a940` is read as history, not independently reverified here.
Its static batches retain original `f72f316` attribution, failed contrast history
and image-view clarification. TLS/missing-Vite framework results keep A14.5
blocked; this review neither demands a framework build for direct data-contract
SPEC nor treats metadata/current mapping as semantic rendering or new native
execution. A16's accepted source-bound evidence and limitations remain unchanged.

No P05 decision/corroboration record was requested or persisted for this review.
Synthetic provider-test contexts are not release records. Later artifact,
installed-consumer, P08 and P12/Office gates remain separate.

**Next:** release D4-D5 to the original owner with focused positive/negative
consumer tests, then return an immutable repair for the same review stages.
Retain D1-D3 closures and passed methods; do not reopen platform/browser work or
declare A14/full-P11 acceptance from this completed review checkpoint.
