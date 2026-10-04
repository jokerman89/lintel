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

## Owned source and output selection

Select sources by literal path within an explicitly authorized root, or by the
actual configured path resolved from the unchanged verified P07 reference. A
profile name, palette name or conventional folder name is not a directory to
search. Use `profile_asset` for the selected design profile; for other assets,
retain the actual configuration source and resolved path. Missing configuration
does not authorize a personal-home scan or an invented brand/template field.

Before generation, select an owned output root and the literal output path(s).
Standalone callers supply `--out`/`--out-dir`; an orchestrator may supply an
already authorized run path explicitly. No output selection, a missing root or
an unwritable output is a visible failure, not permission to use the current
directory, HOME, a neighboring artifact or another run. New children are allowed
only inside that selected writable root, within the authorized write set.

Use existing P03 `checked_root`, `selector_path`, `read_owned` and `atomic_write`
for rooted, no-link reads and publication. Capture each destination's original
state before generation; an absent file is `None`, not overwrite permission.
Require explicit replacement authorization for existing outputs, compare the
original preimage at publication (`expected=...`, `check_expected=True`), and
read back the bytes. Preserve source files. If any publication/readback fails,
report the exact failure and any partial output at the selected paths; do not
report a completed artifact set, retry elsewhere or delete prior evidence.

These are owned-path procedures, not a claim that a model or native provider is
an OS sandbox. Keep each consumer's existing provider, input-admission, retention,
collision and overwrite contract.

The typography, motion and shader callers use one `emit_fragment` procedure in
`design_contract.py`. It validates and emits the exact partial fields to stdout
or a rooted output with expected-preimage publication and byte readback. It
does not synthesize a binding, verify a license or clear a profile requirement.
Retain selected source/profile evidence through synthesis; `load_design` still
verifies the complete design against the external current P05/P07 context.
Invalid fragments publish nothing; failed readback remains a visible partial
output, not permission to retry in another directory.

## Selected asset evidence

These are named **manual/source-inspection procedures**, not a scanner, hook or
license determination. Reuse P05's generic `kind: check`; do not invent new
control kinds or command flags. Before observing results, select the applicable
IDs below from the actual brief/profile, record their policy source/version and
scope, and include any required ones in the original `qa_requirements`.
Preserve that inventory and the same work/profile identity through consumption.

| Procedure/control ID | Exact selected scope and observations |
|---|---|
| `font-licensing` | For each selected font/file/release, read the supplied or authorized primary license/entitlement evidence. Record the intended use (such as local use, web embedding or redistribution), applicable grants/restrictions, required notices and any missing permission. A family name, “free” label, system installation or example is not a grant. |
| `motion-licensing` | Identify each selected runtime, plugin, editor and animation asset by source/version. Inspect their actual terms separately for the intended delivery; record attribution, distribution and entitlement requirements. No-motion/CSS-only does not establish rights to separately included assets. |
| `shader-licensing` | Identify each selected renderer, shader snippet, import and artwork by source/version or file hash. Inspect the supplied primary terms and reuse/notice requirements, including distinct runtime versus shader/asset licenses. A no-shader choice excludes only genuinely unused GPU components. |
| `brand-source` | Read the exact selected palette/profile/template/logo and its source/version. Compare the requested tokens or asset identity to that reference, recording the field/value and evidence location. For a one-color question, read that named token only; no extraction run, personal-library scan or diagnostic CLI is needed. Extraction describes a source; it does not approve a new brand. |
| `brand-freshness` | Compare the selected asset's evidenced revision/effective date with the actual brief/profile's pinned version or refresh requirement. Record the requirement, observed revision/date and discrepancy. File mtime alone is not brand currency; there is no universal 90-day threshold. A permitted advisory exception records its reason and authority, without waiving a mandatory requirement. |

For each selected procedure, retain the source excerpts/paths, asset identity,
intended use, actual observer/method and observation date in an owned evidence
note. Record what was inspected and what was not. Use `pass` only when that
procedure was actually performed and its stated criteria were met; record a
known mismatch as `fail`, execution/read failure as `error`, and missing terms,
unknown applicability, unavailable inspection or unresolved permission as
`unverified`. A source checksum is identity evidence, not legal approval.
Refer a legal/entitlement determination to the authorized qualified owner where
needed; do not manufacture one from a model's recommendation.

Mandatory license/brand obligations stay mandatory whenever selected by the
brief/profile, even without `--customer-share` or when emitting stdout.
An applicable mandatory `fail`, `error` or `unverified` blocks the affected
acceptance/sharing action. Grounded `not_applicable` requires source/version,
scope rationale and evidence; missing tools or terms are not exemptions.
Unrequired advice remains advisory, not silently promoted to a new policy.

Attach these actual observations to the existing P05 controls and evaluate via
the [compliance-gate procedure](../../compliance-gate/SKILL.md#aggregate-through-the-shared-implementation).
That procedure uses `bin/li-review-evidence.py controls` with the real controls
and unchanged `required_policy`; it does not perform the inspections above.
Bind their evidence bytes through the existing review contract. A
no-applicable-controls result, valid fragment, extracted palette or advisory
exception is not licensing, brand or release clearance.

## Measured text contrast

Keep `validate_design.check` / `validate_design.py` for its existing static
HTML/CSS checks. It does not compute paint, inherit backgrounds or run a browser.
Use the read-only standard-library `../scripts/measure_contrast.py` for actual
observed **opaque solid sRGB** color pairs, separately from those checks:

```text
python <trusted-source>/skills/design-dna/scripts/measure_contrast.py --foreground "rgb(0, 0, 0)" --background "rgb(255, 255, 255)" --text-size normal
```

The colors above are an illustrative numerical input, not evidence about an
artifact. For a real artifact retain the exact read/provider/route/viewport,
theme, element and color observation used; measure each required text/background
pair in each required theme. The Python `contrast_observation(foreground,
background, text_size=...)` returns only `{"ratio": ..., "text_size": ...}`.
The CLI emits that same observation: exit 0 meets the normal 4.5:1 or large
3:1 threshold, exit 1 is below it, exit 2 is refused/unverified input and emits
no observation. Decisions use the unrounded ratio.

`browser_observation(element, text_size=..., background_image=...)` reuses the
actual `web-session` read element's `color` and `background` keys. The equivalent
CLI accepts `--element-json` with that literal element and `--background-image`.
The current browser read does **not** report background images or text size:
obtain those observations separately, not by filling in a default. Only an
observed `background_image="none"` qualifies. A computed `backgroundColor`
alone does not rule out a painted gradient/image, ancestor opacity, an overlay,
blending or other unresolved compositing; such cases remain unverified and
must not be passed as a resolved solid pair. “Large” requires observed size of
at least 18pt (24 CSS px), or 14pt bold (18 2/3 CSS px); otherwise use normal
only with a supported classification, not from a tag name or intended token.

Missing/invalid colors, transparent/translucent values, unresolved backgrounds,
gradient/image values, unsupported color spaces or nonfinite channels are
refused rather than clamped, composited or assumed white. The helper has no
CSS cascade or alpha-compositing engine. Pure numerical color input can compute
a ratio without establishing a rendered background or any browser execution.

Carry the returned object unchanged as the existing P05 `contrast` control's
`observation`, with the actual source evidence and original requirements.
Keep browser execution as a separate control; no helper result supplies its
`executed` field. Missing observations remain unverified. Neither a numerical
pass nor static validation produces an independent review or clearance record.

## Actual interfaces

Python:

```python
validate_spec(data, kind=None)  # frontend/pipeline, or typography/motion/shader fragments; shape only
emit_fragment(fragment, kind, repo=explicit_target, out=None, original_output_state=None)
profile_asset(verified_profile_record, explicit_profile_config)  # asset ref, scalar leaves
load_design(repo, path, expected=prepared_context, profile_config=explicit_profile_config,
            pattern_lock=None, pattern_context=None)  # optional verified pattern selection
renderer_args(loaded_design, out="explicit relative output")
normalize_dimensions(["typography", "accessibility"])  # canonical long keys
validate_review(data, dimensions=None)  # advisory only
review_result(data, repo=repo, expected=prepared_context, qa=p05_qa,
              design_path=selected_spec, profile_config=explicit_profile_config,
              pattern_lock=None, pattern_context=None)
```

**Reusable patterns (ADR-0038, spec section 9).** A pinned profile palette colour normally
changes only through a brief-evidenced override. `pattern_lock` and `pattern_context` are
repository-relative paths of a pattern lock and the current resolution context. They are the
only way a selected pattern palette winner, such as a repository or pack default, outranks the
pinned profile. The profile and corpus files stay unchanged.

- **Verification.** The loader imports the trusted `lib/patterns.py` and `lib/pattern_visual.py`
  only then. It runs the core `verify_lock` against that context, with roots taken from this
  repository, the P07 home and the verified P07 record's pack context. Only `ok` continues.
- **Consistency checks:**
  - The spec's `pattern_context` must name the same selection.
  - A frontend spec's `validate_visual` must report `passed` or `incomplete`, with no failed
    check. `incomplete` means only that unmapped settings remain open review items.
  - A pipeline attachment must pass `verify_design_attachment`, with its `lock_ref` naming
    the supplied lock.
  - Every palette winner must equal the design's value.
- **P05 selection.** The lock, the context and every file under `.claude/patterns` must be
  selected by the external P05 context with their current bytes. Pack and personal pattern
  bytes are pinned by the lock and re-read by `verify_lock`.
- **References are not authority.** A spec that carries a `pattern_context` without a supplied
  lock is refused. Neither a forged context nor a caller-claimed winner admits anything.
- **Precedence.** Pass explicit brief decisions to the resolver as `--overrides`: the verified
  winner then reflects brief precedence. A brief never bypasses a `must` clause, because
  resolution is a conflict.
- **Palette-only admission.** This admission governs only palette tokens that differ from the
  pinned profile. It is not render or review clearance. generate-web and generate-app still
  require `validate_visual` `passed` before rendering. Mandatory clauses, including prose and
  unmapped settings, still need their own QA evidence, and incomplete or unknown mandatory
  coverage never becomes a pass.
- **Recheck.** `verify_lock` runs again just before the loader returns.
- **No pattern.** Without a pattern selection, loading is unchanged.

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
`--profile-packs`, `--profile-pointer`, with optional `--profile-context-file`, and optional
`--pattern-lock` with `--pattern-context` (supplied together).
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
The read-only CLI does not publish a result or change the task state. The explicit
Python `emit_fragment` procedure below publishes only its validated partial.

### Fragment emission

Typography, motion and shader keep solo stdout as their default. Their Step 4
recipes call `emit_fragment(fragment, kind, repo=..., out=...,
original_output_state=...)`, which calls `validate_spec` on the actual parsed
value **before** emission and serializes only that validated fragment. Absence
of `--out` is an output-stream choice, never `/dev/stdout` as an input path.
Named output uses the same validation first, followed by existing P03 rooted
atomic publication against the authorized original preimage and readback.
Unknown versions/invalid choices emit neither a fragment nor a pass receipt;
errors go to stderr with nonzero exit. Existing named-file CLI validation remains.
No special-file/absolute exception, new flag or design schema is introduced.
Required licensing or other policy checks still apply to either output mode.

## Review and domain handoff

Canonical dimension keys are `typography_hierarchy`, `motion_coherence`,
`shader_perf_budget`, `accessibility_wcag`, `brand_conformance`,
`responsive_fidelity`. Short aliases normalize once; duplicate aliases, unknown
keys and incomplete selected subsets fail. A score is advisory. Null score means
unverified feedback, not a synthetic 100. Grounded no-shader applicability belongs
in the P05 control; it cannot remove keyboard or contrast obligations.

These are the only scored dimensions, in JSON and the human report. Visual polish,
copy and layout/density questions feed their relevant findings, not a second
scoring system. `shader_perf_budget` remains null/unverified without compatible
runtime measurement. FPS, FOIT and scroll-jank require actual compatible timing/
performance evidence for the named route, device, viewport, state and workload;
DOM, source and screenshots cannot supply those measurements. Do not deduct or
award timing points from a declaration, library name or apparent smoothness.
Typography/motion scores may describe observed non-timing aspects only, with
timing coverage explicitly unverified; use null if missing timing is necessary
for the selected dimension's judgment. Compare measured results to the actual
brief/profile budget, not a universal timing threshold. This helper normalizes
advice; it does not collect or authenticate performance evidence.

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
