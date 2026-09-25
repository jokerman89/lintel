---
name: catalog
layer: foundation
description: Use to discover Lintel skills and agents by name, purpose, category, voice or declared client support, or regenerate the committed skill catalog after frontmatter changes.
color: yellow
tools: Read, Write, Bash, Glob, Grep
voice: internal
cli_support: [claude-code, codex, copilot]
---

# Skills and agents catalog

`skills/CATALOG.md` is a generated view of canonical `skills/*/SKILL.md` frontmatter.
Use the existing generator's compact metadata for discovery before reading selected canonical
skill or role bodies. Source declarations are not native discovery, permission or verified
host execution. Copilot's native entrypoints remain the smaller, separately verified `li-*` set.

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
python3 -B "$LINTEL_SOURCE_ROOT/bin/li-catalog.py" --json --kind=all --voice=internal --cli=copilot
```

Only pass a query when the operator supplied a nonempty keyword. `--search` is an alias
for `--query`. Family filters are literal prefixes, not globs; query/filter values are
data, never shell fragments. Pass each as one quoted argument, without `eval` or command
construction. Listing and filtering do not write or regenerate `skills/CATALOG.md`.

For a general help/onboarding request, use `--kind=all` and group the actual returned
declarations by category. The category API retains `qa` as a display grouping, not a
command name. Show counts from the result, voice and declared support, and add full
descriptions when the operator asks for detail. Registry aliases select one client
surface, not a vendor's entire product family.

This is not an inventory of active tools or registered hooks. A canonical agent file
needs a real permitted host delegation binding or an explicitly labelled manual
handoff. For hook availability, use `/li:hooks-status` and actual host evidence; for
installation health, `/li:doctor`; for task-first onboarding, `/li:welcome`.

Use returned names, descriptions, aliases and source-relative paths to choose the relevant
entry. Then read only the selected body beneath the returned, trusted `source_root`.
Preserve template/staged warnings and alias notes; inspect the selected method before
promising an output. `maturity: unknown` and frontmatter `full` hints do not establish
implemented formats, native registration or execution.

The [metadata reference](references/metadata.md) defines the output, filters, shared parser
dependency and source binding. On a helper/parser error, report the error rather than
inventing an empty inventory or parsing every prompt yourself. If execution is unavailable,
the existing trusted `skills/CATALOG.md` is a skills-only fallback; disclose that it is a
committed snapshot without agent metadata. An explicitly named canonical file can still
be read through a permitted file tool. Neither fallback activates a workflow.

## Select a capability without changing installation

Choose one operation, rather than loading the entire selection and all of its bodies:

```bash
python3 -B "$LINTEL_SOURCE_ROOT/bin/li-catalog.py" --json --list-selections
```

Set `selection` to the exact nonempty ID returned by the first operation. The
[selection reference](references/selections.md) owns the operation and closure contract.
The `demo-script` pilot returns the three demo roles plus the shared core metadata; read
only the chosen Plan, draft or critique method at its returned path. A dependency/resource
list is not an instruction to warm every file. Filters narrow displayed entries, not the
required closure. Do not combine `--list-selections` with filters.

No selection keeps ordinary discovery unchanged. Unknown, blank or malformed selections
are errors, not a reason to regenerate, prune files, activate wrappers or invent another
inventory. Preserve source-stage warnings, aliases and `maturity: unknown`. A selected
role still needs an actual permitted host binding or explicit serial/manual handoff.

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

## Source and output boundaries

In a consumer repo, read the catalog from the adapter's resource root. Regenerate only when
the task actually changes that source. Do not write the tooling catalog into project state.
Descriptions and source links are public output: keep them accurate and company-neutral.
The [consumer checks](references/consumer-checks.md) distinguish executed helper examples
from structural guidance, installed acceptance and unrun model/client behavior.
