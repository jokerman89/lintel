# Client adapters

Lintel supports GitHub Copilot, Claude, Codex and Cursor (ADR-0035); any other host uses
the manual `other` route. Choose the exact surface, not just its vendor. Every listed route
preserves canonical planning, build, review and resume resources. Native-format files
are generated only where the project discovery root is documented. Other routes are
plainly manual.

## Install and inspect one surface

From a reviewed local checkout:

```bash
python3 bin/li-client-capabilities.py list
python3 bin/li-client-capabilities.py show --client <surface>
python3 bin/li-adapter.py init --client <surface> --target <project>
python3 bin/li-adapter.py check --target <project>
```

Use actual values for the placeholders. Repeat `--client` to select multiple surfaces in
one invocation. The existing inventory preserves previously selected clients. One managed
source bundle serves them all; surfaces that share a discovery root receive one identical
set of generated files rather than one copy per surface. No user-global installation,
enablement, model or hook command exists in this helper.

`show` returns official URLs with their check dates and version/conditions, the delivered route
and observed evidence per operation. These dates describe source checks, not client runs.
All live workflows remain unrun here except the explicitly limited Copilot App session
observations. Locally exercised installer fixtures do not establish discovery or model quality.

## Client-specific routes

No client is the default. The GitHub Copilot surfaces receive a complete generated native
skill for every canonical skill and a custom agent for every canonical agent. The other
native routes generate `li-<skill>` wrappers for the core workflow entry points. Invoke
either through the host's own mechanism (slash command, `$` reference, skills UI or skill
tool). The Claude Code plugin keeps its namespaced `/li:<skill>` form. Manual routes read
the canonical `skills/<skill>/SKILL.md` through `START.md`. Former workflow names are mapped
in the [native workflow migration](migrations/2026-09-25-native-workflows.md), not aliased.

**GitHub Copilot:** `copilot-cli`, `copilot-app`, `copilot-vscode`, `copilot-cloud` each select
the `.github/skills` and `.github/agents` kit: every canonical skill as a complete `li-<skill>`
skill, every canonical agent as a custom agent, and the three `lintel-*` role profiles.
Organization policy and available APIs still differ. Other Copilot IDEs use `other` until
their contracts are verified. The [dedicated guide](copilot.md) covers the native kit, the
plugin routes and the surface matrix.

**Claude:** `claude-code` and `claude-desktop` select `.claude/skills` for CLI and Desktop
Code local respectively. This does not cover Chat, Cowork or cloud. The
[Claude guide](claude-code.md) retains plugin skills/agents and separately activated hooks.

**Codex:** `codex-cli`, `codex-desktop`, `codex-ide` select the documented `.agents/skills`
route. Invocation follows the surface: CLI/IDE skills UI or `$` references, desktop's UI.
`codex-cloud` is a manual handoff until that integration is separately verified. The
existing `.codex-plugin/plugin.json` is preserved; no fictional enable/disable marker is used.

**Cursor:** `cursor-cli`, `cursor-ide`, `cursor-cloud` select project `.cursor/skills`
according to the skills documentation. Repository skills are not personal skill sync.
The existing `.cursor-plugin/plugin.json` remains; inspect the installed host's plugin UI
instead of assuming an old `/add-plugin` command or universal settings contract.

**Other hosts:** `other` installs the same manual entry without claiming native discovery.
Use it for any host outside the four supported families. Unknown IDs, including the
families removed by ADR-0035, are refused rather than silently choosing a different client.

## Manual does not mean discarded

Ask the approved host to read `.github/lintel/START.md`, project instructions and the selected
canonical workflow. Use actual file/shell tools where permitted, otherwise export the original
package brief for another actor. Preserve work-map paths, leaf IDs, acceptance, effective
profile reference, actual result and next action. Keep independent review outstanding until
it occurs. See [the Universal contract](../shims/universal/ADAPTER.md).

The generator preserves unrelated files and project-owned knowledge, manages only its own
files/protocol blocks and refuses modified managed content before writes. Review upgrades
and rollback through normal repository changes; never delete an entire host or knowledge
directory. [Getting started](getting-started.md) gives the common first-task walkthrough.

Repository publication also records an exact owned transaction. `inspect` and explicit
`recover` use its target/store/ID; partial writes never become a successful re-init by
adopting current bytes. The original inventory and client/protocol ownership remain with
this generator. See [lifecycle and recovery](lifecycle.md); bare native installation
remains a [separate Python-free operation](native-installation.md).

## Portable documentation boundary

The source bundle keeps README, the standard notices and the public documentation reached
through their literal local links, including transitive guides and linked public assets.
`init` refuses an omitted public target before writing; `check` verifies those local targets
against the managed bundle as well as checking file hashes. A stray project file cannot
stand in for a missing bundled guide. The installed source can reproduce the same navigation
in another checkout without reading the original workstation.

The bundle also carries the exact public alias registry (`config/aliases.yaml`)
and provenance declarations (`install/upstream-sources.yaml`), not their entire
parent directories. These files are data; installation never runs the historical
upstream recipes. Compact catalog queries use the same trusted readers and
aliases after copying. Their optional YAML parser remains an operation-specific
dependency, not a new prerequisite for native bare installation. Required work,
review, domain, browser, selected-design and document helper/schema/reference
files are checked before consumer writes. This includes the source-fidelity and
native-format guides, workbook integrity reader and PDF preparation/print adapters,
plus the shared document input-admission helper. Lintel supplies no PDF reader;
produced PDF text, page and visual inspection remain unverified without a separately
authorized observer. An explicit
`document-content` selection union supplies that helper's declared preflight
resources without forcing pipeline dependencies onto standalone format choices.
File presence does not prove a renderer, recalculation engine, browser or live
client is available; missing native observations remain open.

Some public guides also cite source-repository-only instructions, CI or internal engineering
records. Their bundled copies explicitly label that boundary and link to the canonical
repository's public `main` branch instead of copying those records into your project.
Those external links are navigation, not pinned acceptance evidence; the installer neither
fetches nor live-verifies them. It does not follow links into personal settings, private packs,
hidden documentation folders or `.claude/` knowledge/runtime content.

The local navigation check covers literal Markdown inline/reference destinations and HTML
`href`/`src` paths in the public guides, not examples inside code/comments or placeholder paths.
HTML tags and attributes are parsed structurally: a script's opening `src` is retained,
its body is not executed or scanned as navigation, and quoted `>` characters do not end a
tag. Markdown destinations follow escaped punctuation, balanced/wrapped labels and reference
definitions rather than a substring match; an escaped opening bracket is plain text.
Only a used reference definition contributes a destination, with the first matching definition
retained. One logical line/container view supplies code boundaries and residual indentation
to reference, inline and HTML-exclusion processing. A titled reference can end at EOF just
as at a line ending; quote/list prefixes do not erase the remaining indentation that makes
an example code. Tabs are measured in columns without changing source bytes. No physical
newline is added to make an otherwise valid file pass. Code contexts and source spans stay separate so rewriting a source-only destination
does not rewrite its surrounding examples or markup. Text assets use LF; binary assets retain
their source bytes.
It verifies file/directory targets, not external URL availability, heading fragments, rendered
layout or arbitrary HTML/CSS/JavaScript execution. A complete client pilot remains separate.

## Shared source-boundary facts

`lib/markdown_source.py` supplies the stateless, standard-library
`classify_markdown(text)` provider. Its immutable result types are defined in that one
module. It receives the complete original Unicode string, never a rendered or pre-stripped
excerpt, and reports logical lines, quote/list containers, literal regions and actual
structural list-marker occurrences. Continuation lines and checkbox-shaped examples are
not new item occurrences.

Spans are zero-based, half-open Python Unicode-codepoint positions in the unchanged input,
not UTF-8 byte offsets. CRLF occupies two positions. Line end excludes its terminator;
next-start includes it, and both may equal EOF. Tabs use four-column stops; parse-local
container IDs are not durable work identities. Region annotations can overlap.

An item's `prose` classification describes its start context, not permission to reinterpret
all later text in that item. Quote, code, raw HTML, comment, opaque and unknown facts remain
significant. Consumers must use the actual marker/content occurrence and precise region
spans for their own operation, and classify the full source before selecting excerpts.
The helper knows no task IDs, checkbox-normalization policy, review clearance or credentials.
It does not read files or execute/fetch content.

Navigation consumes these shared boundaries while keeping destination parsing and safe
source/target policy in the adapter. Recognized opening HTML tags may still provide resource
attributes before raw body text is excluded. The portable bundle includes the exact provider
and refuses a missing provider before writing; it does not import a replacement from the
inspected target. This is a bounded static-source contract, not full CommonMark rendering
or proof that another consumer's identity/clearance logic works.
