# Source selections

`lib/capability-selections.json` is an additive projection over the existing catalog's
canonical IDs, not a second skill inventory. The first pilot is `demo-script`: accepted
DemoNarrativeArc Plan/Critique methods, DemoNarratorJunior and SlideNarrationCritic. It
does not supply a PPT renderer, register an agent or establish an independent actor.

## Read-only operations

From the loaded trusted `LINTEL_SOURCE_ROOT`, with an available permitted shell:

```bash
python3 "$LINTEL_SOURCE_ROOT/bin/li-catalog.py" --json --list-selections
python3 "$LINTEL_SOURCE_ROOT/bin/li-catalog.py" --json --selection=demo-script
python3 "$LINTEL_SOURCE_ROOT/bin/li-catalog.py" --json --selection=demo-script --kind=agent
python3 "$LINTEL_SOURCE_ROOT/bin/li-catalog.py" --json --selection=demo-script --name=DemoNarrativeArc
```

`python` can replace `python3` when it is the Python 3 command. Source/parser dependencies
and explicit source/target boundaries are the [existing metadata contract](metadata.md).
An explicitly approved `--source-root` selects data only; helpers remain script-bound.
No selection input is interpolated into a shell command or treated as a glob, regex,
path or executable instruction.

`--selection` may be repeated for a union of different IDs. Unknown, blank or repeated
IDs fail; IDs are exact kebab-case strings. `--list-selections` lists source definitions
and source-stage evidence and cannot be combined with query/kind filters or a selection.
Both operations require `--json` and cannot be combined with `--check` or generation.

Selection defaults to both skill and agent kinds. Ordinary `--json` still defaults to
skills, with exactly its existing output, and does not read or require the descriptor.
Default Markdown generation/check retain their exact bytes/messages and stdlib-only
dependency floor. A missing optional selection descriptor cannot break default discovery.

## One declared data contract

The strict shared data loader reads the descriptor and the existing declaration-only
`install/upstream-sources.yaml` provenance registry. It never executes a registry recipe.
Unknown fields or invalid types in selection definitions fail; no guessed fallback or
second YAML/profile/host parser is used.

| Descriptor field | Contract |
|---|---|
| `schema_version` | Integer `1`; discovery-selection syntax only, not product or P07 feature semver |
| `shared` | Required selection ID included in every projection; currently `core` |
| `selections` | Nonempty map of selection IDs to the exact fields below |
| `source_stages` | Optional-in-content map of canonical IDs to explicit unknown or evidenced staged declarations; the map itself is required |

| Selection field | Contract |
|---|---|
| `source` | Explicit responsible source file |
| `members` | Nonempty unique exact canonical `skill:<name>` / `agent:<name>` IDs, not aliases or copied frontmatter |
| `requires` | Unique selection IDs; no unknown dependency or dependency cycle |
| `resources` | Unique explicit source files required by this source method, not globs or an inferred import graph |
| `provenance` | Unique IDs in the existing `bundled_materials` registry |
| `inputs`, `outputs`, `limitations` | Nonempty arrays of distinct descriptive strings, never executed or treated as observed results |
| `example` | `{path, heading}` pointing at a source file and exact Markdown heading; a worked source example, not a test receipt |

Paths are normalized, source-relative, regular files with exact source spelling. Absolute,
drive/UNC, backslash, traversal, dot/hidden-component, repeated-separator, linked/reparse,
missing and directory-as-file paths fail before output. The provenance registry's
`local_paths` may also name directories; these define component scope without glob-reading
their contents. Discovery does not read personal packs, target policy files or runtime state.

All selection definitions, dependencies, source-stage declarations and referenced
provenance/resources are checked before querying. An invalid unselected definition or a
no-match filter cannot hide a bad descriptor. The full existing canonical inventory still
enforces name/alias ownership before any projection.

The shared `core` selection retains the nine phase entrypoints, cycle, resume utility and
compliance-gate; source references point to the actual P05 review, P06 host and P07 profile
contracts. It does not parse, bind, activate or weaken any of them. Applicable company
requirements continue to resolve through P07 in the actual authorized workflow. Choosing
a customer-domain role does not select company identity or replace a failed required
profile with neutral policy. Absence of a selection never removes on-disk access.

## Deterministic closure and output

`--list-selections` returns source definitions, their shared root and explicitly recorded
source-stage evidence. `--selection` retains the ordinary metadata envelope and adds:

| `selection` field | Meaning |
|---|---|
| `requested` | Sorted explicit selection IDs |
| `order` | Deterministic dependency-before-dependent closure, including the shared core |
| `definitions` | Only the selected closure's source/input/output/example/limit records |
| `reasons` | Selection inclusion reasons: `requested`, `shared`, `required-by:<id>` |
| `members` | Deduplicated canonical IDs with every `member-of:<id>` reason |
| `resources` | Deduplicated paths with source/example/member/resource/notice/attribution reasons |
| `provenance` | Selected existing source/license/modification/notice records; unknown historical import stays null |
| `source_stages` | Selected members' explicit evidence or `{status: unknown, evidence: null}` |

Returned entry descriptions, identities, aliases, paths and `maturity: unknown` are the
same existing metadata objects. Kind/query/family/name/category/voice/client filters
affect displayed entries only, not required dependency/resource/provenance closure.
`total` counts closure members in the requested kind before filters; `matched` counts
displayed entries. Literal filters reuse the existing matcher. The helper returns paths
and metadata, never selected or unrelated prompt bodies, notice text or example bodies.

Known adapted component paths cannot omit their existing provenance ID. Selected notice
and attribution files must exist and be nonempty and join the resource closure. This
checks recorded source obligations, not license sufficiency, historical import accuracy,
installed distribution, legal clearance or endorsement. Existing records and notices
remain authoritative; no new content is copied and no import revision is guessed.

## Stage evidence without readiness inflation

An explicit stage record has exactly `status` and `evidence`. `unknown` requires null
evidence. `staged` requires `{path, description_sha256, quote}`: the path must be that
member's canonical source; SHA-256 must match its current full UTF-8 parsed description;
the literal quote must still appear in that description. Only this bounded frontmatter
evidence is consumed, not a corpus-wide scan of role/skill bodies.

The descriptor currently records the exact `TEMPLATE ONLY` declarations for PDF, Visio
and XLSX. A changed/missing description, wrong path/digest/quote or unknown member fails
until the descriptor is deliberately reviewed and updated. `mature`, `implemented` and
`verified` are not accepted stage statuses. A body repair alone does not upgrade maturity.
The legacy `maturity` output remains `unknown`; a source-stage label is a declaration,
not execution, independent review or a promised format capability.

The demo roles have accepted content methods, but no maturity promotion follows. P09's
role preservation and review reports are distinct historical evidence; live mode
dispatch, rehearsal and independent critique still require actual host evidence.

## Worked pilot and failure behavior

For an approved eight-minute synthetic duplicate-submission demo, list/select
`demo-script`, then read only the appropriate selected role:

1. DemoNarrativeArc **Plan mode** accepts the blank brief and returns `arc-DRAFT.md`.
2. DemoNarratorJunior consumes the approved arc and returns words, pacing and factual
   recovery cues. Without a supplied fallback, it acknowledges the missing result.
3. A separate reviewer may use DemoNarrativeArc **Critique mode** and SlideNarrationCritic
   after the script exists. The drafter cannot declare its own independent critique.

The authorized caller persists the named artifacts. Selecting metadata creates no
draft, phase, profile, registration or actor. With no permitted delegation, the same
methods can be read as serial/manual guidance, with independent review explicitly open.
Source example pointers are declaration references; the focused tests resolve their
actual headings separately, not by returning those bodies in a query.

All input/dependency failures return nonzero with a diagnostic and no JSON/partial
success. Source/target files remain unchanged. A valid no-match projection has zero
entries but still names its required closure. Missing runtime PyYAML remains a visible
metadata error and the existing disclosed skills-only catalog snapshot remains a
fallback; discovery never installs dependencies.

The full source bundle and default entrypoints remain intact. This unit does not change
installation, native wrappers, receipt formats, private policy, status/welcome, product
versions or generated outputs. Actual installed alias/selection/notice closure is a
separate coordinator/P10 join; this source query is not its acceptance test. Physical
pruning, external relocation and a new installer/scheduler were not selected.
