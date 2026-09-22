---
name: help
layer: foundation
description: List the Lintel skills + agents + hooks available in this session. Filter by category, voice tier, or CLI support.
color: blue
tools: Read, Bash, Grep, Glob
voice: internal
cli_support:
  - cli: claude-code
    level: full
  - cli: codex
    level: degraded
  - cli: copilot
    level: degraded
---

# /li:help

List the source-declared skills and agents using the same compact inventory as catalog and
skill-router. This is not a list of tools actually registered or permitted in the current host.
Do not turn a frontmatter support hint, a hook file or a native wrapper into execution evidence.
For installation/version health use `/li:doctor`; this discovery read changes no installation.

## When to use

- First session after install — discover what's there
- Picking the right skill for a task (filter by category)
- Onboarding a teammate to Lintel
- Finding a source method and distinguishing it from observed host availability

## Inputs

Optional flags:
- `--category <name>` — exact display category (`plan`, `qa`, `ship`, `compliance`, `voice`, `meta`, `ops`, or an agent category)
- `--voice <internal|customer|mixed>` — filter by voice tier
- `--cli <surface-or-alias>` — filter declared hints through the accepted surface registry, not measured support
- `--verbose` — include description per entry (default: one-line entries)

No arguments: source-declared skills and agents grouped by category. Counts come from the
returned inventory, not a hardcoded fleet or hook count.

## Workflow

1. Resolve `LINTEL_SOURCE_ROOT` from the loaded trusted adapter or explicitly selected Lintel
   source. Keep it separate from the working project's `LINTEL_REPO_ROOT`. Never fall back to
   arbitrary target code, personal settings or another checkout.
2. Use an available permitted shell and Python 3.9+ to read metadata:

   ```bash
   python3 "$LINTEL_SOURCE_ROOT/bin/li-catalog.py" --json --kind=all
   python3 "$LINTEL_SOURCE_ROOT/bin/li-catalog.py" --json --kind=all --category=qa
   python3 "$LINTEL_SOURCE_ROOT/bin/li-catalog.py" --json --kind=all --voice=internal --cli=copilot
   ```

   Pass only supplied filters, as separate quoted literal arguments. `--verbose` changes
   presentation, not the query. `python` may replace `python3` when that is the installed
   Python 3 command. See the [single metadata reference](../catalog/references/metadata.md).
3. Present the returned names, categories, declared voice/support hints and aliases. Use
   full descriptions when requested; retain template/staged warnings even in a short view.
   An absent level or `maturity: unknown` stays unknown. Do not label a `full` declaration
   as implemented or tested. Registry aliases select one surface, not the whole client family.
4. Listing requires no prompt bodies. Only after an entry is selected, read its returned
   `path` relative to the same trusted `source_root`. For an agent, a role file is not proof
   of native registration: inspect the current host's real delegation API and inventory.
   If unavailable, offer the selected role as explicit serial/manual guidance, without
   claiming independent execution or bypassing a denial.
5. For hooks or actual availability questions, inspect the chosen host's real tools and
   evidence only when requested and permitted. The catalog does not inventory activated
   hooks. Missing observations stay unverified; use `/li:hooks-status` through its actual
   adapter or explicit canonical-file fallback rather than making up counts or enablement.

## Report format

Populate this shape from the query; these are placeholders, not measured availability:

```
Lintel source inventory — <matched> of <total> declarations
Source: <trusted source_root>
Evidence: source-metadata; execution not observed by this query

## <category>
- <kind>:<name> [<voice>; <declared surface and level>; maturity unknown]
  <description, including any staged/template warning>
  <source-relative path; aliases and migration note where applicable>
```

Use `/li:<name>` only for an applicable plugin route. For a verified native `li-*` wrapper,
show that host's actual invocation; otherwise name the canonical file and explicit read
fallback. Do not imply that the query installed, registered or activated anything.

## Errors and fallback

- A valid zero-match response means no source declarations match; suggest a broader filter.
- Missing/empty/malformed source or parser failure is an error, not a partial list. Report
  it without skipping broken entries, regenerating the catalog or inventing support.
- Without the helper/interpreter/parser, use the trusted committed `skills/CATALOG.md` as
  a disclosed skills-only snapshot, or read an explicitly named selected file. Do not
  recreate the inventory by globbing and parsing every skill/agent body in model context.
- Missing trusted source or denied read permission blocks discovery; never choose another
  root or channel to bypass that boundary. Dependency installation needs its own authority.

## See also

- `/li:catalog` — compact discovery and explicit source-maintenance generation
- `/li:doctor` — install + version + hook-firing health (cross-CLI)
- `/li:hooks-status` — live hook activation state
- `AGENT-INSTRUCTIONS.md` — canonical session-start ritual
