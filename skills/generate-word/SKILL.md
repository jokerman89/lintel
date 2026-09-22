---
name: generate-word
layer: foundation
description: Produce an editable Word document through available native tools or a declared library, preserving source detail and reporting actual inspection evidence.
color: orange
tools: Read, Write, Bash, Glob
voice: mixed
cli_support:
  - cli: claude-code
    level: full
  - cli: codex
    level: degraded
    degradation:
      - capability: AskUserQuestion
        strategy: auto-pick-recommended
license_note: produces customer-bound output; honors the active pack's compliance gates for customer-facing variants
---

# /generate-word

Editable Word document generation with source fidelity and applicable configured
policy. Three target variants:

- **`technical`** — engineering-internal deliverable (technical spec, runbook, ADR-style doc) — voice: internal
- **`customer-summary`** — customer-bound engagement summary — voice: pack-resolved (customer-facing tier), gated
- **`transparency-note`** — AI-feature transparency note — voice: pack-resolved (customer-facing tier), gated, includes honest-limitations check

`--brief` is a standalone route: it does not require generate-design, a domain
envelope or an invented shared design input. Preserve the complete brief and its
evidence, not just an outline or slide summary.

## Prerequisites

Discover the host's actual create/read/edit/render operations and their schemas.
Prefer a native Word artifact API when available. On the Copilot canvas surface,
call `list_canvas_capabilities` for `word`, then `open_canvas` on an explicit owned
path; use the discovered `get_model` and `batch` actions. The
[native Word procedure](references/native-word.md) documents that observed route
and its page-render boundary. Never guess an action or claim a tool ran from its
presence in a manifest.

Retain the existing declared library alternatives: `docxtemplater` plus `pizzip`
for a compatible `.docx` template, or `docx` for programmatic generation. Check the
selected task-local environment before use. Only after an actual missing-tool
failure may an authorized task-local restore be considered; do not install
automatically/globally or assume every library can consume every template.
If no writer exists, retain the Markdown source and mark DOCX generation blocked.
An explicitly chosen Markdown/PDF alternative is not an editable DOCX substitute.

## When to use

- Customer engagement summary deliverable
- Technical spec / architecture doc with the active pack's brand identity
- AI-feature transparency note (compliance artifact, if the active pack requires one)

## When NOT to use

- Quick markdown note — use direct editing
- Slide content — use `/generate-ppt`
- Multi-page wiki/site — use `/generate-web`

## Inputs

- Required `--brief <path|inline>` — content brief or source markdown **OR** `--from-pipeline <dir>` (shared pipeline mode)
- Required `--target <technical|customer-summary|transparency-note>` — variant
- Optional `--template <name|path>` — explicit selection overrides the omitted-flag default `<target>.docx` in the verified configured brand directory
- Optional `--audience <text>` — primary audience
- Optional `--voice` — voice tier override (default per target)
- Optional `--use-defaults` — use an available neutral template or an explicitly blank native document; never invent a missing bundled template
- Optional `--ignore-stale-brand <reason>` — record an advisory staleness exception; cannot waive mandatory policy
- Optional `--out <path>` — explicit new `.docx` output (default: `<brief-stem>.docx` in the working directory)

### Standalone template selection

Without `--template` and without `--use-defaults`, select `<target>.docx` from
the already verified configured brand directory:

| Target | Default template filename |
|---|---|
| `technical` | `technical.docx` |
| `customer-summary` | `customer-summary.docx` |
| `transparency-note` | `transparency-note.docx` |

Explicit `--template` takes precedence over `<target>.docx` on this brand route:
use its explicit path, or resolve its name inside that same verified directory.
`--use-defaults` selects the explicit neutral/default route described above
instead of the implicit brand-template lookup; required policy still applies.
Omitting `--template` does not imply `--use-defaults`.
No personal-directory scan is permitted. If the selected template/directory is
unavailable, report that gap; do not silently choose another variant or claim a
blank document satisfies required brand policy.

## From-pipeline mode (v3.5 Phase 2 — generate-pipeline integration)

If invoked with `--from-pipeline <run-dir>` instead of `--brief`:

Keep this existing entry path and field names. The full shared design/profile/work
binding is still the A15.3.shared integration gate; standalone evidence does not
establish that binding. Validate the supplied artifacts against their released
contracts before consuming them. Do not fabricate design-spec.json to unblock it.

1. **Read shared pipeline-output:**
   - `<run-dir>/content.md` — sections with H1/H2/H3 hierarchy + bodies + voice-annotations
   - `<run-dir>/design-spec.json` — read `per_format.word.sections` for heading-levels + slot-mappings

2. **Replace brief-parsing logic** with direct-read of content.md (per target-variant):
   - `technical`: headings + paragraphs + code blocks + tables
   - `customer-summary`: narrative paragraphs + key findings + next steps
   - `transparency-note`: capabilities + limitations + data + decisions + appeals

3. **Apply format-specific design-pass via design_pass_hook:**
   - Reads `per_format.word.sections[N].design_pass_hook` (canonical: WordTechnicalEditor)
   - Invokes agent for a Word-specific fidelity-pass (heading-style consistency, technical-tone, tables-formatting)
   - Per Reviewer Concern #7: WordTechnicalEditor stays word-specific

4. **CLI stays backward-compat:** existing `--brief`-flag invocations work unchanged. `--from-pipeline` is additive.

5. **Apply the same fidelity/inspection and configured controls as standalone mode.**
   Shared content must survive in full; heading/slot mappings cannot discard
   unmapped paragraphs, tables, citations or qualifications.

## Workflow

1. **Preflight and policy.** Follow the
   [P05/P07 fidelity and evidence procedure](../generate-write/references/fidelity-and-evidence.md).
   Resolve source/output paths and the standalone template selection above;
   refuse unapproved replacement.
   Verify the pinned profile and requested controls. Use only configured brand/voice
   rules and their actual applicability. A required template, policy or inspection
   that is unavailable remains blocked. Neutral mode needs no personal brand scan.

2. **Read the complete brief and compose the target.**
   - **technical:** meaningful heading styles, multi-paragraph reasoning, code,
     editable tables with headers/units, references and material limitations.
   - **customer-summary:** audience-appropriate narrative, supported findings and
     next steps; retain qualifications rather than enforcing a fixed page count.
   - **transparency-note:** capabilities, material limitations and failure
     conditions, data, decision impact, appeals and disclosure as required by the
     brief/policy. Map each material claim to its evidence and relevant boundary.
   Preserve the claim/evidence ledger and citation targets. Label missing evidence;
   do not invent a legal basis, retention period, contact or measured result.

3. **Use WordTechnicalEditor as the format-specific review method.**
   Read its accepted source; delegate only through a real available host operation,
   with read-only source/artifact inputs. It checks structure and claim accuracy;
   pack voice scoring remains separate. Source-only advice is pre-generation
   review, not DOCX inspection. A builder's own pass is self-review, not independent.

4. **Create editable content through the selected writer.**
   With native operations, inspect available styles, insert complete paragraphs,
   apply real heading styles, and create/edit table cells. With a declared library,
   fill only a compatible explicit template or create the same document structure.
   Keep code and list semantics, cross-references, table headers and cited evidence.
   If an unsupported field, footnote, image or layout is required, report that
   specific gap instead of silently flattening it or claiming fidelity.

5. **Reopen, edit/read back, and inspect the actual artifact.**
   Open the saved `.docx` through the available application/API. Read body, tables,
   styles, headers/footers and relevant notes/fields. Make a small authorized edit,
   read it back and restore it if it is only a verification marker. Compare the
   full source ledger to the saved content. Render every page where supported;
   inspect pagination, heading orphans, table continuation, margins, references,
   clipping and legibility. A ZIP parse or `get_model` is not rendered page evidence.

6. **Record actual outcomes, not a four-score shortcut.**
   Retain the familiar voice, brand, honest-limitations and provenance categories
   with grounded applicability, plus source retention, editability and rendered
   inspection. Mandatory failure/error/unverified blocks the affected completion
   or distribution regardless of other scores. An absent optional brand/voice
   requirement is not failed compliance or verified enterprise enforcement.
   Persist P05 evidence bound to the final artifact and current P07 reference.
   Keep incomplete output at its explicit owned path, clearly marked unverified;
   do not move it through an implicit personal draft directory.

## Report format

Report the exact source/output paths and hashes; target; actual template or blank
choice; verified profile reference; writer/tool/provider/instance/actions; retained
claims, paragraphs, tables, citations and limitations; reopen/edit result; rendered
pages inspected or precise missing renderer; each configured control's observed
status and evidence; and the remaining acceptance/review gates. Do not fill this
report with illustrative PASS scores, invented provenance IDs or guessed page counts.

## Compliance integration

- Honor applicable configured controls and the brief's disclosure requirements.
  A transparency note needs claim-to-evidence/limitation coverage, not a count ratio.
- No customer data, secrets, macro execution or external upload in synthetic validation.
- Generation is not authorization to distribute. Required independent review and
  delivery controls stay open until their actual evidence exists.

## Failure modes

- **Template/placeholder mismatch:** preserve the source and identify the missing slot; do not drop content.
- **Material limitation/evidence missing:** name the uncovered claim and keep the relevant control unresolved.
- **Required voice/template unavailable:** block that action; `--use-defaults` cannot override required policy.
- **Page renderer absent:** retain editable DOCX and model evidence, with rendered layout unverified.
- **Only Markdown/PDF available:** disclose the alternative and keep promised DOCX editability open.

## Examples

**Technical spec:**
```
> /generate-word --brief docs/spec/auth-rewrite.md --target technical
[Resolve applicable controls, select an available writer, then inspect actual output.]
```

**Customer summary:**
```
> /generate-word --brief summary-brief.md --target customer-summary --audience "Technical decision makers" --out summary.docx
[Preserve sources and qualifications; run the configured customer-facing controls.]
```

**Transparency note:**
```
> /generate-word --brief case-analysis-design.md --target transparency-note
[Check material claim boundaries and required disclosures; no limitation-count proxy.]
```

**Neutral standalone:**
```
> /generate-word --brief synthetic-brief.md --target technical --use-defaults --out synthetic.docx
[Use an explicitly blank native document when available; no personal template lookup.]
```

## See also

- [Native Word procedure](references/native-word.md)
- [Content fidelity and evidence](../generate-write/references/fidelity-and-evidence.md)
- `WordTechnicalEditor` agent
- The active pack's compliance gates (`resolve_pack_field compliance.hooks`; none by default)
- `/generate-ppt`, `/generate-web`
