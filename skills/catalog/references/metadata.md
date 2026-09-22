# Compact source discovery

`bin/li-catalog.py` owns both the deterministic Markdown catalog and the read-only
metadata/query view used by catalog, help and skill-router. There is no second generated
inventory, cache, classifier, capability manifest or installation-selection engine.

## Operations and dependencies

| Operation | Behavior |
|---|---|
| No arguments | Generate `skills/CATALOG.md` beside this trusted helper's source, as before |
| `--check` | Compare that catalog without writing; preserve the existing messages and exits |
| `--json` | Emit compact metadata to stdout, without regeneration, activation or target writes |
| `--json --kind skill\|agent\|all` | Select source skills (default), agent roles, or both |
| `--query TEXT` / `--search TEXT` | Case-insensitive literal substring of name, description, alias, category or family |
| `--family TEXT` | Literal case-insensitive skill name/alias prefix or agent category prefix |
| `--name TEXT` | Exact case-insensitive name or retained alias |
| `--category TEXT`, `--voice TEXT` | Exact case-insensitive display category or declared voice |
| `--cli SURFACE` | Filter declarations for one registry surface; accepted legacy aliases resolve through P06 |
| `--source-root ABSOLUTE_PATH` | Explicit metadata data source only; never redirects executable helpers or generation |

All selectors require `--json`; combining them with generation or `--check` is an error.
Selectors combine with AND. They do not execute, expand globs, interpret regex, read a path
from a query, rank results or modify the user's intent. Pass values as single arguments,
using `--query="$keyword"` in Bash or an equivalent literal argument API. An empty or
whitespace-only supplied filter is invalid; omit the filter to list the inventory.

Python 3.9+ is required. Ordinary generation and `--check` remain standard-library-only.
Metadata reuses `lib/envelope_contract.py`'s existing strict data loader, not a new YAML
parser; canonical YAML metadata needs the existing optional PyYAML 6.x dependency declared
in `lib/envelope-requirements.txt`. Missing helpers or PyYAML fail visibly before output.
Do not automatically install dependencies as part of discovery. A JSON fixture accepted
without PyYAML does not prove that the canonical YAML inventory is usable without it.

## Source and target binding

Invoke the helper from the resource root identified by the loaded trusted adapter
(`LINTEL_SOURCE_ROOT`), not from arbitrary target code or a user-global fallback. The
default data root and all executable reader modules are bound to the invoked script's
location. An explicit absolute `--source-root` changes only the data being inspected.
It must identify an approved source/fixture; it does not grant permission to read it.

Data is read from `skills/*/SKILL.md`, `agents/*/*.md`, the accepted
`lib/cli-tiers.yaml`, and, for skill discovery, `config/aliases.yaml`. Relative record
paths resolve beneath the output's `source_root`, never beneath `LINTEL_REPO_ROOT` or
the current directory. Linked/reparse source entries and escaping paths are refused.
The selected source does not supply Python code, shell code or plugin initialization.

The source-relative shared P06 reader validates the registry and normalizes surface
aliases. It does not resolve policy, bind a profile, execute tools or promote documentation
to observation. No personal settings, telemetry, credentials, hooks or runtime state are
read by discovery. No bytecode, index, catalog, activation marker or project artifact is
written. Only the explicitly authorized default generation operation writes the catalog.

Frontmatter reading stops at the closing delimiter, with a 64 KiB header ceiling.
Prompt bodies, tool/model directives and degradation recipes are not returned. The shared
strict loader rejects malformed metadata, duplicate keys, executable tags and YAML
anchors/aliases. The legacy Markdown renderer retains its three one-line scalar fields,
ordering, Unicode, 120-character description truncation, pipe escaping and source links;
empty, repeated or malformed required scalars fail before publication.
Ordinary generation and `--check` also reject duplicate or case-equivalent canonical
skill names across folders and layers, before opening or certifying a catalog. An
already-generated ambiguous catalog cannot pass `--check`. This validation uses the same
case-insensitive identity rule as metadata without adding a parser dependency.

## JSON contract

The schema version is a discovery-output version, not a Lintel product, capability or pack
version. One compact JSON object is emitted with an LF terminator:

| Field | Meaning |
|---|---|
| `schema_version` | `1` |
| `source_root` | Absolute resolved root binding every returned relative path |
| `evidence_level` | `source-metadata`, never a live acceptance claim |
| `executed` | Always `false` |
| `total` | Source entries for the requested kind before query filters |
| `matched` | Number of returned entries |
| `entries` | Stable `id` order; no prompt bodies |

Each entry contains:

| Field | Meaning |
|---|---|
| `id`, `kind`, `name` | Stable `skill:<name>` or `agent:<name>` identity; aliases do not rename it |
| `path` | Canonical source-relative file path, independent of the name/folder relationship |
| `description` | Full declared description, retaining Unicode and staged/template warnings |
| `layer` | Declared skill layer; `null` for agents |
| `category` | Generator-owned skill display grouping or the declared agent category |
| `family` | Skill name segment before the first hyphen, or agent category |
| `voice` | Declared voice string, not a resolved policy |
| `aliases` | `{name, source, note}` entries from frontmatter and the existing alias registry |
| `cli_support` | `{cli, surface, level}` declarations; `level: null` for ungraded list hints |
| `maturity` | `unknown`; this unit does not decide or infer capability maturity |

Skill display categories retain help's heuristic grouping: plan/office-hours, QA and
review/investigate, ship/review-and-ship, compliance, eval's voice group, discovery/meta
tools, and an ops remainder. These are presentation labels, not optional capability
packages, dependency declarations, policy or P08 intent routing. Agent categories come
from agent frontmatter. Selection never moves or deletes canonical content.

Central alias records take precedence over matching frontmatter aliases for the same
target, retaining their migration note. Missing targets, collisions and ambiguous
identities are errors. Agent frontmatter aliases follow the same cross-record ownership
rules: an alias may not match any canonical name (including its own) or another entry's
alias, case-insensitively, anywhere in the agent inventory. Validation precedes every
filter, including a query with no matches. Skill and agent namespaces remain distinct:
the same spelling in those different kinds is allowed and retains separate IDs.
Recorded dates do not silently expire aliases. Notes may require
arguments or a sub-method: inspect the selected canonical body rather than inventing an
executable rewrite from the alias spelling.

A `full` frontmatter hint remains a declaration; it is not proof of a completed renderer,
available model/tool, native wrapper, agent registration, activated hook or observed host
execution. For example, a format's `TEMPLATE ONLY` description remains visible even when
its old `cli_support` says `full`. Maturity and actual execution require separate evidence.

## Selection and failure behavior

Catalog/help can list metadata without reading any body. Skill-router shortlists at most
three entries, then reads only those selected canonical bodies to check applicability,
exclusions and prerequisites. It recommends a real host invocation only when discovered
and permitted; otherwise it names an explicit canonical-file or serial/manual fallback.
Listing or recommendation never invokes the selected method.

The complete requested-kind inventory and alias/registry inputs are validated before
filtering. A malformed source cannot disappear behind a no-match query. A valid no-match
query returns `matched: 0` and an empty `entries` array; an empty/missing source, invalid
frontmatter, missing required data/helper or malformed filter exits nonzero, writes a
diagnostic to stderr, emits no partial JSON and leaves an existing good catalog untouched.

Without permitted helper execution, the existing trusted `skills/CATALOG.md` is an explicit
skills-only snapshot fallback. It does not supply agent metadata or live host evidence.
Do not rebuild the inventory in model context by reading every canonical body.

Optional installed selection, native wrapper/resource closure, provenance-notice
distribution acceptance, welcome/status integration and final maturity/version decisions
remain separate P13/coordinator gates. The source metadata tests do not establish those
outcomes or live model/client execution.
