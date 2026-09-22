# P11 direct design-contract review

**2026-09-22: complete scoped SPEC FAIL. QUALITY was not eligible and was not
run.** Open findings: **P1 0 / P2 3 / P3 0**. Hold A14.1-A14.4 acceptance for
the three bounded corrections below. Accepted A16 is unchanged; this is not an
A14.5 artifact review, whole-P11 decision or strict v2 release clearance.

## Exact source and independent context

Reviewer app `d823e773-d8dc-4d02-9716-77506a7a260e`, CLI
`1f655ca9-eb2b-4325-9996-72ed8539c13b`, distinct from builder `f413bdcb`.
No source fix or nested actor was used. Prior A16 review `3049811` and earlier
review refs are preserved.

| Input | Pinned identity |
|---|---|
| Complete unit base | `336513e0178a1e9df39286ac7a69de5989f7a5ef` |
| Main implementation | `559f3fc9a079c24d1ebca83921b0ce7abef40e10` |
| Final product | `f72f3169e4a9408df5c8af845ed665bc871a95b7` |
| Builder report / this review's parent | `c91e83de9de134912dcdafb8c65bb1f0615a5dc6` |
| Report Git-byte SHA-256 | `5504a0e76f09bb5b7ba4f419c916bd8ea66567afff5e8477157ed28e879824a3` |
| Direct-unit authority | `235d5bf1c94956ee7fe76fde3e962df6636f3aae` |

Verified the exact ancestry, full 24-path cumulative unit and report-only child,
not merely the final four-file correction. Read the 123-line addendum; the
975-line report preserves the exact prior 852-line prefix. Clean detached source
was pinned before execution. All eleven accepted browser blobs are unchanged.
No moving builder tip, separate A14 runtime/WIP or later artifact work was read.

Complete product selection:

- Five `agents\frontend\` roles: DesignSystemAuditor, FrontendArchitect,
  MotionDirector, ShaderEngineer, TypographyCurator.
- Thirteen `skills\<name>\SKILL.md` files: design-dna, design-html, design-review,
  design-shotgun, frontend-design-review, frontend-design, frontend-motion,
  frontend-shader, frontend-style-extract, frontend-typography, generate-app,
  generate-design, generate-web.
- `skills\design-dna\references\design-contract.md`,
  `design-contract.schema.json`, and `scripts\design_contract.py`.
- `tests\integration\design-contract.py`, `design-contract.sh`,
  `frontend-design-roundtrip.sh`.

All selected source/consumer bodies, original-method diffs, relevant ADR0015-17
and actual P03/P05/P07/P09/token/static-validator interfaces were read. No shared
provider, P12 producer, installer, registry or generated-output edit is included.

## Complete scoped SPEC

| Leaf | Verdict | Preserved behavior and deviation |
|---|---|---|
| A14.1 | FAIL | One compatibility helper/schema, legacy readability, current P05/P07 binding and actual non-clearing P09 artifact handoff work. D1 breaks exact selected-design identity at renderer handoff. |
| A14.2 | FAIL | Canonical single-file/Next/app argument arrays, spaces/literal output paths, customer-share and long-key review aliases work; duplicate/unknown options reject. D1 validates one filename but maps the consumer to another. |
| A14.3 | FAIL | Helper none/CSS/empty-library/no-shader branches and active-shader boolean/fallback negatives pass; immutable keyboard/contrast obligations remain enforced. D3's web-renderer instruction still forces GPU output for an accepted no-shader object. |
| A14.4 | FAIL | Brief override/profile/corpus methods, selected asset hashes, drift/missing-policy failures and provenance data are retained. D2 allows an existing unsupported project to bypass stack constraints through a contradictory `existing:false` declaration. |

The five frontend-role frontmatters are byte-equivalent to the base; substantive
P09 font, motion, shader, architecture and audit methods remain. Retrieval,
composition, three-layer token emission, static validation, mockup/variation and
pattern extraction retain their useful methods. These passes do not erase the
failed leaves. Provenance tests validate data/evidence identity, not licenses,
cryptographic authority or runtime compatibility.

## Findings and specific fixes

| ID | Severity | File:lines | Finding / fix | Confidence |
|---|---|---|---|---|
| D1 | P2 | `skills\design-dna\scripts\design_contract.py:375-381` | `renderer_args` discards the selected basename. Require the canonical filename for the chosen envelope before mapping, or use a genuinely supported exact-file consumer interface. Do not claim verification of one file while selecting another. Cover frontend and pipeline mappings. | 10/10 |
| D2 | P2 | `skills\design-dna\scripts\design_contract.py:286-314` | Rejection of an unrecognized existing framework depends on the caller's `project.existing` flag even when its actual manifest is present and bound. Derive/enforce existing-project constraints from that evidence; reject the unsupported target rather than accepting a false new-project label. No expanded framework catalog is required. | 10/10 |
| D3 | P2 | `skills\generate-web\SKILL.md:95-101` | The consumer still says `shader != null` means emit Paper/OGL. An accepted non-null `visual_thesis:none, library:null` object therefore triggers GPU output. Match generate-app's active/non-`none` branch and emit no GPU dependency for either no-shader representation. | 9/10 |

**D1 actual reproduction:** keep a valid single-file
`run with spaces/frontend-design-spec.json`; write and select an app/vite design
as `run with spaces/alternate.json`. Actual `load_design` succeeds, then
`renderer_args` emits:

```text
generate-app --from-frontend-design "run with spaces" --stack vite-react --out output
```

The documented consumer reads `run with spaces/frontend-design-spec.json`, whose
target is `single-file`, not the validated alternate app input. The positive
canonical-filename mapping still passes.

**D2 actual reproduction:** selected `package.json` contains
`{"dependencies":{"react":"18.3.1","react-scripts":"5.0.1"}}`.
With bound project `stack:next-app, existing:true`, actual loading rejects.
Change only `existing` to `false`: loading reports `verification:current_inputs`
and maps to `generate-app --stack next-app`. No manifest bytes or runtime
capability changed; this is the forbidden unsupported-project fallback.

**D3 source-backed reproduction:** the real helper accepts and preserves
`{"schema_version":1,"visual_thesis":"none","library":null}` inside a resolved
single-file design with no libraries. The web consumer's explicit non-null
condition still selects a GPU component; the app consumer correctly excludes
`none`. This is a method-wiring contradiction, not a claim that rendering ran.

## Commands and actual outcomes

| Reviewer command in sealed synthetic environment | Outcome |
|---|---|
| `bash --noprofile --norc tests\integration\design-contract.sh` | Exit 0; 11/11 tests, zero errors/failures/skips; real helper/CLI/P03/P05/P07/P09 links. Own run `d-d9m311bc`; browser/rendered artifacts `not_run`. |
| `bash --noprofile --norc tests\integration\frontend-design-roundtrip.sh` | Exit 0; retained fixture plus real compatibility helper. Existing optional jq assertions used the documented grep branch; Python validation was executed. |
| `python -I -B <private>\preservation.py` | Exit 0; retained DNA domain/stack/composition, token layers, static positive/negative checks, five unchanged role frontmatters. Fourteen true command exits retained; not fourteen live-artifact tests. |
| `python -I -B <private>\spec_probes.py` | Exit 1; 6 tests, 4 pass/2 failures, zero errors/skips. D1/D2 reproduced. Literal variants/CLI rejection, none/CSS/shader fallback, explicit brief override/drift, and immutable mandatory-control negatives passed. |

The independent P05 negative used 3.5:1 normal text plus unavailable keyboard
observation with 100-point typography advice: both remained blockers. Dropping,
downgrading or declaring the keyboard requirement N/A was rejected. This is
synthetic control evidence, not accessibility certification.

Every product import/call and outer comparison used inspected per-process
allowlisted synthetic HOME/USERPROFILE/AppData/LocalAppData/temp/XDG/LINTEL and
derived roots, explicit PATHEXT and fixture Git configuration/ceilings. All 62
selected product/provider/test seals remained unchanged before/after execution.
No running script was edited or dependency installed. No personal configuration/
profile, remote service or owner runtime was accessed; no browser/server launched
or OS policy changed. No full repository suite ran.

Private evidence: this CLI session's `files\p11-design-review\`, including pin,
per-file original diffs, full logs, commands/environments, fixtures and source
seals. Reproducer SHA-256:
`ed91780732d795477141bd42a27e2be06bda58f28b9d9c2b33e724e689c41399`.
Observed counterexamples SHA-256:
`1956d8fd43b7d33cbedd1dc0ca4958a0a96e29403906c760af8fbcc3c3438fff`.
Two oversized read-only diff outputs were host-captured; neither capture was
inspected or cleaned. Complete diffs were separately captured in private evidence
and read by path. This did not affect any test exit or source seal.

## Stages, limitations and handoff

**QUALITY and formal subsequent clearance were not run because SPEC failed.**
A14.5 new static-page/app build, health, UI, contrast, responsive/motion and
artifact outcomes remain unobserved in this checkpoint. They were not demanded
as prerequisites for this direct data-contract unit. Automatic P08 lifecycle,
installed consumers, Office/P12 and minimum Python-runtime execution are likewise
not claimed; Python 3.9 grammar is not a Python 3.9 run.

Accepted A16 and its original source-bound observations/limitations are unchanged,
not re-audited or reassigned to design. The coordinator should release only D1-D3
corrections to the original owner, preserve the passed methods and separate
artifact work, then return an immutable repair for complete scoped SPEC before
eligible QUALITY. This report-only checkpoint does not accept A14 or all P11.
