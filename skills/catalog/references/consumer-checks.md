# Discovery consumer checks

The catalog/selection [metadata](metadata.md) and [selection](selections.md) contracts
remain the only inventory. Catalog, help, router and welcome query them before selected
body reads. Status uses them for method names/aliases, never for progress. Skillify
uses the same name/alias query before authoring an explicitly owned new draft.

## Run the focused source checks

From an authorized source checkout with Python 3.9+, its existing PyYAML dependency
and Bash (Git Bash on Windows):

```bash
python3 -B tests/unit/catalog-consumers.py
python3 -B tests/unit/catalog-metadata.py
python3 -B tests/unit/catalog-selection.py
```

The consumer test launches the actual Bash blocks in the owned skill files, with
the actual catalog, work-map, state, profile, frontmatter and uniformity helpers.
It reuses the metadata fixture support. Its parent and every product child use
inspected synthetic home/profile/application/temp/target roots and fixture Git
ceilings. Source Git identity and source files are not normalized. Windows fixture
snapshots and cleanup use the accepted native-path spelling helper without changing
the logical roots. Missing prerequisites are errors, not skipped passing cases.

## Evidence boundaries

- Literal alias/selection and welcome queries run from an unrelated cwd with target
  helper/import decoys. The helper returns metadata and paths, not prompt bodies.
  Instruction assertions additionally preserve the router's bounded shortlist;
  they are not proof of a model's later context choices.
- Status setup creates synthetic maps, pins and cycle records through existing
  producers. The **consumer** then performs only reads. Two-initiative selection,
  STARTING/BLOCKED/incomplete entries, missing artifacts, missing pins and profile
  drift are compared against complete fixture file-and-directory snapshots.
  An explicitly injected resume-reader error additionally checks that a later
  formatting command cannot hide the exit; it is not a native provider failure.
- Status intentionally uses data-only `profile_context.py verify`, followed by
  `required-policy` with that exact verified reference. The shell workflow/profile
  wrappers can create audit directories or record failures; this read-only caller
  does not invoke them or suppress their controls. It reuses the state ledger
  readers and original work-map provider rather than introducing a parser or ledger.
- Skillify exercises catalog collision and existing path checks, the corrected
  opening template, and `validate_lintel_frontmatter` on the exact synthetic draft.
  That validator checks field presence/boundaries, not YAML semantics, actual skill
  quality or host registration. Draft instantiation is fixture setup, not a measured
  model-authoring run. No activation or symlink is performed.
- Uniformity invokes real floor/generator code on a synthetic source; missing
  resources, a real floor violation, a real diff and actual helper errors are
  distinguished. Additional injected exit failures test caller propagation and
  are labeled separately from real-helper scenarios. No source matrix is generated
  by the consumer; fixture setup alone captures `--stdout` as its input matrix.
- Eval examples check the separate known-good/known-bad arithmetic and incomplete
  scope guidance. No evaluator, model, gateway, paid benchmark, audit writer or
  downstream certification is executed by these checks.

These checks do not accept an installer, live client, independent reviewer or the
whole Universal initiative. Installed discovery/alias/notice closure and actual
model behavior require their own attributable evidence. The full source bundle,
ordinary catalog output, aliases, canonical frontmatter, stage declarations and
underlying provider semantics are preserved by this consumer unit.
