---
name: li-catalog
description: Use to discover Lintel skills and agents by intent, name, purpose, category, voice or declared client support, or regenerate the committed skill catalog after frontmatter changes.
---

> **Lintel on GitHub Copilot.** Generated from `skills/catalog/SKILL.md`; edit the canonical file, then run
> `li-copilot init`.
> - **Resource root:** `../../..` from this skill's base directory (the Lintel source with `bin/`,
>   `lib/`, `skills/`). Write plans, state and evidence into the working repository's `.claude/`
>   tree, never into the resource root.
> - **Skill-relative paths:** this skill's own `scripts/`, `references/` and `data/` folders (and a
>   `<base>` that the workflow defines as its own directory) mean
>   `../../../skills/catalog/` in the Lintel source, not this generated folder.
>   `${LINTEL_SKILLS_DIR:-skills}` means the skills root, `../../../skills`. A `bin/li-run` step
>   runs in the working repository, so use `$LINTEL_SKILLS_DIR/catalog/` there.
> - **Shell steps:** run Bash snippets with Bash (Git for Windows' `bash.exe` on Windows, never
>   `System32\bash.exe`). Save a snippet to a temporary `.sh` file and run
>   `bash "<resource root>/bin/li-run" <file>`; it prepares `LINTEL_SOURCE_ROOT`, `LINTEL_REPO_ROOT`
>   and the profile context.
> - **Tools:** Read=`view`, Write=`create`, Edit=`edit`, Bash=`bash`/`powershell`, Grep=`grep`,
>   Glob=`glob`, AskUserQuestion=`ask_user`, TodoWrite=the plan checklist, Task or a named role=`task`
>   with that custom agent, WebFetch=`web_fetch`.
> - **Other Lintel workflows** are native skills: invoke `/li-<name>` rather than reading their
>   files. Named roles such as `CodeReviewer` are custom agents.

# Skills and agents catalog

`skills/CATALOG.md` is a generated view of canonical `skills/*/SKILL.md` frontmatter.
Use the existing generator's compact metadata for discovery before reading selected canonical
skill or role bodies. Source declarations are not native discovery, permission or verified
host execution. Native entrypoints are adapter-specific; use actual client discovery,
not a source inventory, to establish which `li-*` entries are available.

## Discover without regeneration

Resolve `LINTEL_SOURCE_ROOT` from the loaded trusted adapter or explicit operator-selected
Lintel source, not the target repository's working directory or a personal installation.
Use an available permitted shell and Python 3.9+ (`python` when that is the Python 3 command):

```bash
python3 -B "$LINTEL_SOURCE_ROOT/bin/li-catalog.py" --json
python3 -B "$LINTEL_SOURCE_ROOT/bin/li-catalog.py" --json --query="$keyword"
python3 -B "$LINTEL_SOURCE_ROOT/bin/li-catalog.py" --json --family=context
python3 -B "$LINTEL_SOURCE_ROOT/bin/li-catalog.py" --json --kind=agent --query="$keyword"
python3 -B "$LINTEL_SOURCE_ROOT/bin/li-catalog.py" --json --name=skill-router
python3 -B "$LINTEL_SOURCE_ROOT/bin/li-catalog.py" --json --kind=all
python3 -B "$LINTEL_SOURCE_ROOT/bin/li-catalog.py" --json --kind=all --category=qa
python3 -B "$LINTEL_SOURCE_ROOT/bin/li-catalog.py" --json --kind=skill --category=engineering
python3 -B "$LINTEL_SOURCE_ROOT/bin/li-catalog.py" --json --kind=all --voice=internal --cli=copilot
```

Only pass a nonempty keyword from the operator's supplied request. `--search` is an alias
for `--query`. Family filters are literal prefixes, not globs; query/filter values are
data, never shell fragments. Pass each as one quoted argument, without `eval` or command
construction. Listing and filtering do not write or regenerate `skills/CATALOG.md`.

For a general help/onboarding request, use `--kind=all` and group the actual returned
declarations by category. The category API retains `qa` as a display grouping, not a
command name. Show counts from the result, voice and declared support, and add full
descriptions when the operator asks for detail. Registry aliases select one client
surface, not a vendor's entire product family.

The `engineering` category includes the six existing skills `ta`, `da`, `sc`, `dh`,
`tq` and `full-engineering-pass`, separately from operational utilities. Select a
named module for its full/loop/single-capability method, or the composition only
when all five domains were requested. `--query` remains a literal substring filter,
not ranked search; for example `--category=engineering --query=migration` narrows
metadata without claiming a relevance ranking.

This is not an inventory of active tools or registered hooks. A canonical agent file
needs a real permitted host delegation binding or an explicitly labelled manual
handoff. For hook availability, use `/li-hooks-status` and actual host evidence; for
installation health, `/li-doctor`; for task-first onboarding, `/li-welcome`.

Use returned names, descriptions, aliases and source-relative paths to choose the relevant
entry. Then read only the selected body beneath the returned, trusted `source_root`.
Preserve template/staged warnings and alias notes; inspect the selected method before
promising an output. `maturity: unknown` and frontmatter `full` hints do not establish
implemented formats, native registration or execution.

The [metadata reference](../../../skills/catalog/references/metadata.md) defines the output, filters, shared parser
dependency and source binding. On a helper/parser error, report the error rather than
inventing an empty inventory or parsing every prompt yourself. If execution is unavailable,
the existing trusted `skills/CATALOG.md` is a skills-only fallback; disclose that it is a
committed snapshot without agent metadata. An explicitly named canonical file can still
be read through a permitted file tool. Neither fallback activates a workflow.

## Match intent

For free-text intent, follow [intent narrowing](../../../skills/catalog/references/intent.md), the sole owner
of the metadata-first shortlist and selected-body checks. `skill-router`, `orientator`
and `welcome` retain their public names and delegate here. SENSE retains its actual
mechanical navigation/high-risk confirmation, not a competing discovery method.
No ranking engine, model selection policy or measured success rate is introduced.

## Select a capability without changing installation

Choose one operation, rather than loading the entire selection and all of its bodies:

```bash
python3 -B "$LINTEL_SOURCE_ROOT/bin/li-catalog.py" --json --list-selections
```

Set `selection` to the exact nonempty ID returned by the first operation. The
[selection reference](../../../skills/catalog/references/selections.md) owns the operation and closure contract.
The `demo-script` pilot returns the three demo roles plus the shared core metadata; read
only the chosen Plan, draft or critique method at its returned path. A dependency/resource
list is not an instruction to warm every file. Filters narrow displayed entries, not the
required closure. Do not combine `--list-selections` with filters.

No selection keeps ordinary discovery unchanged. Unknown, blank or malformed selections
are errors, not a reason to regenerate, prune files, activate wrappers or invent another
inventory. Preserve source-stage warnings, aliases and `maturity: unknown`. A selected
role still needs an actual permitted host binding or explicit serial/manual handoff.

`engineering-modules` selects exactly those six existing skills and requires the
unchanged `core` selection. Its resource pointers include the shared domain
admission contract and each module's decision methods. It does not add engineering
to every other family, execute every module, choose phases, change the full pass,
or promote unknown maturity/client observations. Read only the requested method.
The effective resource closure combines inherited `core` references (including the
P05 evidence and P07 profile documentation) with the engineering selection's
declared admission helpers and schemas. Each returned resource's `reasons` identifies
its owner; name/category filters do not remove those dependencies. This does not
transfer live profile inputs or establish installed/runtime acceptance.

```bash
python3 -B "$LINTEL_SOURCE_ROOT/bin/li-catalog.py" --json \
  --selection=engineering-modules --kind=skill --name=da
```

### Selected capability

Run one literal selection query after choosing an ID. `python_cmd` may name the
inspected Python 3 executable; an absent/blank ID fails before the helper runs.

```bash
: "${LINTEL_SOURCE_ROOT:?select the trusted Lintel source}"
: "${selection:?select a nonempty capability ID}"
"${python_cmd:-python3}" -B "$LINTEL_SOURCE_ROOT/bin/li-catalog.py" \
  --json --selection="$selection"
```

Repeat `--selection` only for distinct explicitly requested IDs. Existing category,
voice, client and kind filters may narrow displayed entries but cannot erase the
required dependency/resource/provenance closure. `--list-selections` is a separate
operation, not a filter. A source declaration never proves native availability.

## Generate and check

From the Lintel source root, run:

```bash
python3 bin/li-catalog.py
python3 bin/li-catalog.py --check
```

Use generation only when source maintenance is authorized, not while answering discovery
requests. The same deterministic generator runs in CI. CI fails on stale output and never commits
or pushes the catalog on behalf of the operator. Edit source descriptions, regenerate,
review the diff and commit both together. Missing frontmatter and an empty source tree
are errors; never replace a usable catalog with an empty or guessed result.

A trends overlay requires separately available, authorized usage data. Do not inspect
personal telemetry or add a transient sort order to the committed catalog.

## Engineering module example

**Inputs.** An approved request for a migration plan, its original work/acceptance
and the existing store/consumer facts. No live database access is implied.

**Method and output.** Query `--selection=engineering-modules --kind=skill --name=da`
with the existing catalog helper. It returns DA metadata and the retained
core/shared-method resource closure. Read DA's migration capability and required
shared admission before doing the authorized planning work; a source query creates
no plan, profile, actor or migration.

**Negative.** An unknown selection is an error, not an empty success. During later
module admission, missing original work or required policy blocks dependent work;
neither selecting DA nor excluding displayed entries can erase those requirements.
Selecting one capability does not silently request `full-engineering-pass`.

**Evidence limit.** Metadata is source discovery, not a ranked recommendation,
executed module, tested recovery or independent acceptance. Maturity remains unknown;
the full pass retains all five required domains when it is explicitly selected.

## Source and output boundaries

In a consumer repo, read the catalog from the adapter's resource root. Regenerate only when
the task actually changes that source. Do not write the tooling catalog into project state.
Descriptions and source links are public output: keep them accurate and company-neutral.
The [consumer checks](../../../skills/catalog/references/consumer-checks.md) distinguish executed helper examples
from structural guidance, installed acceptance and unrun model/client behavior.
