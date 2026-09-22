# Direct design contract

`design-contract.schema.json` is the design-owned vocabulary.
`../scripts/design_contract.py` is its only compatibility/validation helper. It
does not generate a site, launch a browser, dispatch a role, install dependencies
or grant permission. The director makes decisions; the existing renderer creates
files; P05 owns controls and independent review.

## Existing envelopes, one resolved design

Keep `frontend-design-spec.json` with `schema_version: 1` and
`source: frontend-design`. Its existing typography, motion, shader, libraries,
layout, interaction, palette and thesis fields are the common design.

Keep pipeline `design-spec.json` with `version: "1.0"` and `per_format` layout
mappings. A new resolved web output adds `schema_version: 1`, `source: pipeline`,
`web_design` (the same common design definition) and `binding`. Retain its existing
palette/font hints for document consumers; overlapping web colors/font roles must
agree. This is not a migration of P12's document-format producers.

Both envelopes carry the same additive `binding`:

| Field | Required input |
|---|---|
| `profile_ref` | Unchanged P07 reference, including context, generation and digest |
| `profile_asset` | Selected design asset `{name, origin: pack\|source, sha256}` from `profile_asset` |
| `brief` | P05 `{path, sha256}` for the actual input: frontend's selected brief, or pipeline's exact sibling `content.md` |
| `retrieval` | P05 file references for retained design-DNA search results |
| `project` | `{existing, stack, manifests}`; manifest/lockfile references are selected input bytes |
| `customer_share` | Explicit boolean propagated to the renderer |
| `provenance` | One record per selected font/library: kind, name, exact version, primary source, license, rationale and evidence-file references; libraries also declare source-supported `stacks` |
| `overrides` | Explicit brief-backed `{field, reason, evidence}` for changed profile choices, e.g. `palette.ink` or `typography.body` |

Historical inputs remain readable with `validate_spec`; an absent binding/motion
mode is **unresolved**, not an invented default. Unknown versions, contradictory
projections and bad declared values fail. Render only after `load_design` succeeds
against an external current P05 prepared context. A legacy `contrast_verified`
boolean is not measurement evidence and is never a clearance input.

## Decisions and precedence

P07 chooses and pins the effective pack; this helper never bootstraps, rebinds or
rescues a required-policy failure. Resolve `design.profile` from that verified
record. Check the declaring pack's `profiles/<id>.yaml`, then the same named
bundled profile. Only an absent design selection uses `anthropic-default`.
Missing/invalid explicitly selected assets do not become another brand.

Reuse the existing ADR-0017 token emitter/parser. It exposes the documented scalar
token subset, not every nested profile field; its fixed spacing scale and other
documented limitations are not silently changed. The actual asset hash plus the
resolved decision bytes are bound; a profile name alone is insufficient.

Aesthetic precedence remains **brief > profile > corpus** (ADR-0016). Record
brief overrides and retain the corpus retrieval. Required policy and the existing
project's technology are constraints, not aesthetic defaults. A brief does not
authorize replacing Vue with React. Existing `package.json` cannot be omitted
from selected inputs by declaring a project new; unknown/incompatible frameworks
block the requested renderer instead of falling back.
Any present bound `package.json` supplies that constraint, independently of the
caller-supplied `existing` flag. Unrecognized evidence such as a React/react-scripts
project cannot become Next.js by setting the flag false. Genuinely new projects
without a manifest and compatible supported manifests keep their existing routes.

Motion is explicitly `none`, `css` or `library`. None permits empty libraries and
animations, native scrolling and no page transition. CSS permits zero JS libraries
and CSS animations with reduced-motion handling. Library mode requires an actual
chosen library and its source/license evidence. Empty component-library lists are
valid. `shader: null`, or `visual_thesis: none` with `library: null`, needs no GPU
dependency; an active shader still needs its fallback/reduced-motion budget.
Do not import a library, emit setup instructions or generate a canvas merely
because an older example contained it.

Existing manifests/lockfiles and official selected-release documentation govern
version/license advice. Preserve source/attribution, runtime versus editor/asset
terms and a rationale for a new dependency. An unresolved license is not a free
license; a source-file checksum proves identity, not legal verification. No helper
operation installs or upgrades anything.

## Actual interfaces

Python:

```python
validate_spec(data, kind=None)  # frontend/pipeline, or typography/motion/shader fragments; shape only
profile_asset(verified_profile_record, explicit_profile_config)  # asset ref, scalar leaves
load_design(repo, path, expected=prepared_context, profile_config=explicit_profile_config)
renderer_args(loaded_design, out="explicit relative output")
normalize_dimensions(["typography", "accessibility"])  # canonical long keys
validate_review(data, dimensions=None)  # advisory only
review_result(data, repo=repo, expected=prepared_context, qa=p05_qa,
              design_path=selected_spec, profile_config=explicit_profile_config)
```

All file inputs use accepted P03 rooted, no-link, bounded reads. JSON is parsed by
P05. The context/work/controls and profile reference are validated by P05/P07,
not copied into a second authority. The caller prepares context after selecting
actual input/artifact bytes; keep final context outside the content it hashes.
Shared schema references use P05's canonical schema ID; the helper resolves them
to its trusted bundled `review_contract` API without any network request.

The CLI exposes `validate`, `renderer-args` and `review`. `validate --kind` selects
`frontend`, `pipeline`, `typography`, `motion` or `shader`; fragments never establish
render readiness. Every option occurs
once; unknown, duplicate or missing options fail. Supply explicit `--repo` and
`--file`. `renderer-args` also requires `--expected`, `--out`, `--profile-home`,
`--profile-packs`, `--profile-pointer`, with optional `--profile-context-file`.
`review` requires `--expected`, `--qa`, `--design` and the same explicit profile
configuration, and accepts `--dimensions`.
All data paths are literal repository-relative paths, with Windows separators
accepted at the CLI input boundary. There is no shell-string evaluation.

Renderer mapping returns a skill name and **argument array**, not a command to
execute automatically:

| Target | Existing renderer call |
|---|---|
| `single-file` | `generate-web --from-frontend-design <run> --variant single-file --out <out>` |
| `nextjs` | `generate-web --from-frontend-design <run> --variant nextjs-scaffold --out <out>` |
| `app` | `generate-app --from-frontend-design <run> --stack <next-app\|vite-react\|svelte-kit> --out <out>` |

Pipeline web uses `--from-pipeline` instead. Pipeline-to-app is not an existing
entry point: explicitly prepare a frontend envelope rather than inventing one.
Directory-based handoff requires the exact canonical filename for its envelope:
`frontend-design-spec.json` or `design-spec.json`. An alternate filename can be
read/validated, but mapping rejects it rather than discarding its basename and
making the renderer consume a different sibling. No new exact-file flag is invented.
For a pipeline, the implicit consumed set also includes that directory's
`content.md`. Its exact repository-relative path must be `binding.brief.path`,
its current bytes must match `binding.brief.sha256`, and it must be selected in
the external P05 context together with the design spec. A `source_content_hash`
of a different brief, even one with identical bytes, cannot stand in for the file
the renderer opens. Missing, changed or unselected sibling content blocks; a
frontend's explicitly bound brief remains unrestricted by this pipeline convention.
The brief is the bound input carried through the envelope, not a second conflicting
`--brief` input alongside `--from-*`. Direct `generate-web --brief` remains useful;
resolve that brief into the same contract before rendering. `--customer-share`
propagates when selected. Argument mapping reports `executed: false`.

Exit 0 means the requested data operation succeeded, not artifact acceptance.
Exit 2 reports invalid/missing/drifted input; exit 3 reports mandatory QA blockers.
The helper does not publish a result or change the task state.

### Fragment emission

Typography, motion and shader keep solo stdout as their default. Their Step 4
recipes call the existing `validate_spec(fragment, kind)` on the actual parsed
value **before** emission, then serialize only the validated fragment. Absence
of `--out` is an output-stream choice, never `/dev/stdout` as an input path.
Named output uses the same validation first, followed by existing P03 rooted
atomic publication against the authorized original preimage and readback.
Unknown versions/invalid choices emit neither a fragment nor a pass receipt;
errors go to stderr with nonzero exit. Existing named-file CLI validation remains.
No special-file/absolute exception, new flag or helper API is introduced.
Required licensing or other policy checks still apply to either output mode.

## Review and domain handoff

Canonical dimension keys are `typography_hierarchy`, `motion_coherence`,
`shader_perf_budget`, `accessibility_wcag`, `brand_conformance`,
`responsive_fidelity`. Short aliases normalize once; duplicate aliases, unknown
keys and incomplete selected subsets fail. A score is advisory. Null score means
unverified feedback, not a synthetic 100. Grounded no-shader applicability belongs
in the P05 control; it cannot remove keyboard or contrast obligations.

`review_result` rechecks the selected design/profile, then calls actual P05
`verify_qa` with the unchanged inventory and external context. A 3.5:1 normal-text result remains blocked regardless of all-green
advisory scores; missing required observations stay unverified. The helper does
not establish independent review or latest-log clearance.

For a selected TA/TQ handoff use accepted `domain_result.validate_request`,
`record_checkpoint` and `verify_result`. Design JSON is an artifact in an existing
domain checkpoint, not a new domain enum/result format. Bind original input context,
publication preimages, start/result, artifact and evidence bytes; prepare the final
context externally after outputs exist. Preserve `release_clearance: false` and
`review: not_evaluated`.

Direct validation does not need P08. Automatic cycle/module dispatch, shared audit,
context warming and cold resume remain P08 work; installed closure and document
consumers have their own owners. A14.5 requires actual static-page/app build,
health, UI and browser measurements from the same profile. These data checks
and older browser evidence do not establish those new artifact outcomes.
