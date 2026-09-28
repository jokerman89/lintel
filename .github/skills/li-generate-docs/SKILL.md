---
name: li-generate-docs
description: Use to generate source-grounded reference documentation, customer guides or onboarding tutorials while retaining API behavior, examples, provenance and limitations.
---

> **Lintel on GitHub Copilot.** Generated from `skills/generate-docs/SKILL.md`; edit the canonical file, then run
> `li-copilot init`.
> - **Resource root:** `../../..` from this skill's base directory (the Lintel source with `bin/`,
>   `lib/`, `skills/`). Write plans, state and evidence into the working repository's `.claude/`
>   tree, never into the resource root.
> - **Shell steps:** run Bash snippets with Bash (Git for Windows' `bash.exe` on Windows, never
>   `System32\bash.exe`). Save a snippet to a temporary `.sh` file and run
>   `bash "<resource root>/bin/li-run" <file>`; it prepares `LINTEL_SOURCE_ROOT`, `LINTEL_REPO_ROOT`
>   and the profile context.
> - **Tools:** Read=`view`, Write=`create`, Edit=`edit`, Bash=`bash`/`powershell`, Grep=`grep`,
>   Glob=`glob`, AskUserQuestion=`ask_user`, TodoWrite=the plan checklist, Task or a named role=`task`
>   with that custom agent, WebFetch=`web_fetch`.
> - **Other Lintel workflows** are native skills: invoke `/li-<name>` rather than reading their
>   files. Named roles such as `CodeReviewer` are custom agents.

# /generate-docs

Generate Markdown documentation from selected source code and its actual behavior.
Keep engineering reference, customer-guide and tutorial outcomes. This is distinct
from the `DocWriter` method for detecting drift and revising existing documentation,
and from `generate`, which renders a content brief into document formats.

## Inputs

| Input | Contract |
|---|---|
| `--source <path-or-glob>` | Required selected source files within the authorized repository; expand and retain the exact set |
| `--target <reference\|customer-guide\|tutorial>` | Required documentation type |
| `--voice <internal\|pack>` | Reference/tutorial default internal; customer-guide uses the actual configured customer-facing voice when available |
| `--out <path>` | Default `docs/<source-stem>.md`, `docs/guides/<source-stem>.md` or `docs/tutorials/<source-stem>.md` respectively |
| `--depth <shallow\|deep>` | Shallow documents public signatures and concise behavior; deep adds examples, edge cases, caveats and relevant internal helpers |

These are skill inputs, not a bundled parser. Reject missing, unknown, duplicate
or conflicting options before writing. For a multi-root glob without one source
stem, choose an explicit output instead of inventing an ambiguous default.
An existing output requires an authorized overwrite, append or alternate path.
Never silently concatenate a second reference into an existing document.

## Workflow

1. **Read sources and authority.** Validate the selected map, original task and
   P07 profile when supplied. Use rooted, no-link source reads. Expand the source
   list before writing; read the complete selected files and their relevant
   imports, types and public exports. Missing/unreadable files remain failures,
   not empty modules. Do not execute imported source code merely to document it.
2. **Read behavior evidence.** Inspect sibling tests, callers, existing docs and
   relevant local history. Build an inventory of signatures, parameters/defaults,
   return values, errors, side effects, authorization and platform/version
   constraints. Cite actual source locations. Separate observed behavior from
   comments, assumptions and proposed behavior. A test example is not a claim
   that its test ran in this invocation.
3. **Draft the selected target without losing meaning.**

   | Target | Retained structure |
   |---|---|
   | reference | Module overview, public API table, per-export signature/parameters/return/errors/examples, related-module links; deep mode includes relevant internals and edge cases |
   | customer-guide | Purpose, useful task-oriented sections, common pitfalls, limitations and next steps; mark DRAFT pending actual distribution controls |
   | tutorial | Outcome, prerequisites, numbered what/why/command/expected-result steps, common failures/recovery and continuation paths |

   Preserve facts, code examples, table values, units, citations, assumptions and
   material limitations. Do not turn an example response into a guaranteed API
   response or invent a "successful" command output. Label illustrative output.
   Section counts are a presentation choice, never a reason to drop source detail.
4. **Check coverage and policy.** Map each relevant public export/source claim to
   its documentation section. Check signatures, defaults, errors, links and code
   snippets against the actual sources. Run safe requested examples/tests only
   inside their authorization and record which ran. Keep missing tests/examples
   and unverified claims explicit. Apply the actual configured data/voice controls;
   do not invent a neutral vocabulary gate or infer hook activation from files.
5. **Publish atomically.** Write only the selected output within ownership, retain
   the original preimage if replacement was authorized, and read it back.
   Keep source identities and coverage in the run report. Customer-guide or
   pack-voice output stays DRAFT until its applicable controls actually pass.
   Generation never uploads or distributes the artifact.
6. **Report.** Return source/output paths, target, chosen depth/voice, coverage,
   grounded examples, actual checks, failures and limitations. File size, an
   empty issue list and a polished voice do not prove source fidelity.

## Format handoff

The generated Markdown can become the explicit complete brief for `generate`
or a standalone `generate-word`, `generate-ppt`, `generate-web`, `generate-pdf`
or `generate-xlsx` route. Keep the original code/evidence sources selected as
provenance. Do not rename a documentation file to `content.md` and claim the
shared pipeline already ran.

For an actual pipeline follow the existing
[source-fidelity and input admission](../../../skills/generate-write/references/fidelity-and-evidence.md)
procedure: retain `brief.md`, `outline.md`, `content.md`, `speaker-notes.md` when
needed, `design-spec.json` and their existing hash/section contracts. No new
interchange schema or document layout projection is introduced.

Word editability, slide notes/rendering, workbook formula/recalculation/reopen and
PDF print/page inspection remain format-specific observations. The PDF writer
remains available, but no removed reader is restored; unavailable inspection
stays unverified. Documentation generation cannot clear another format's gates.

## Failure boundaries

- No public exports: clarify whether internal helpers are the desired scope;
  do not fabricate a public API.
- Missing optional tests: retain source-grounded documentation and mark examples
  unverified. Missing required behavior evidence blocks the affected claim.
- Required profile/voice/data control missing or failed: block that action; no
  silent neutral fallback or invented customer-facing voice.
- Unavailable optional voice corpus: retain an explicitly unvalidated DRAFT, not
  a distribution-ready guide or an instruction to install personal tooling.
- Changed source during generation: refresh the affected coverage and evidence
  before publication. Do not reuse stale source hashes or review decisions.

Use `DocWriter` for later drift checks and `lessons-add` for an explicitly
authorized reusable documentation lesson. Neither is automatically invoked.
