---
name: generate-visio
layer: foundation
description: Use when a request calls for architecture, network or process-flow diagrams through the Visio scaffolding slot; no curated generation workflow is supplied.
color: orange
tools: Read, Write, Bash, Glob
voice: internal
cli_support:
  - cli: claude-code
    level: full
  - cli: codex
    level: degraded
  - cli: copilot
    level: full
---

## Visio format preflight

Lintel has no bundled writer for this entrypoint. The public name and source
mapping remain a staged template slot, not an implemented VSDX generator.
This preflight establishes what the operator actually requested and what an
available authorized writer can produce and inspect; it does not invent a
workflow, renderer or tool. A frontmatter `full` hint is not live availability.

The retained `--output-format <vsdx|svg|png|drawio>` spelling expresses the
actual requested format, not a promise that all four can be written. Accept
`--from-pipeline <run-dir>` or a directly supplied brief. No output format is
silently substituted when the requested writer is absent.

## Preflight before an output write

1. **Confirm the requested result.** Read the explicit brief and, for a selected
   pipeline run, its current `content.md`, outline/`notes_for_writer` and
   `design-spec.json` where applicable. Keep source facts, topology, qualifications,
   captions and evidence pointers. Architecture sketches, network layouts,
   deployment pipelines, swimlanes, cross-functional flowcharts and sequence
   diagrams remain supported planning subjects, not proof of file-generation
   capability. Confirm whether the requested result is editable VSDX/drawio or an
   explicitly requested SVG or PNG export. Ambiguous format/content or a missing
   required run/design input returns NEEDS_CONTEXT, not an invented architecture.
2. **Keep source/profile authority.** Retain the selected work, current P07
   reference and applicable controls. Use the shared
   [source-fidelity method](../generate-write/references/fidelity-and-evidence.md).
   GENERATE's input helper currently admits Word/PPT/PDF/XLSX, not Visio; reading
   pipeline files here does not claim that helper accepted a Visio input or that
   the run's other formats passed. No new admission schema or renderer is supplied.
3. **Identify the real writer and inspection operations.** Inspect the current
   host's actual tools, supported formats and operation permissions. Name the
   available authorized writer for the exact requested format, plus its save,
   reopen/edit, connector/label readback and required inspection operations.
   Neither an agent, a catalog selection, a library name nor an installed app
   alone supplies these operations. Missing writer/editor operations keep the
   requested artifact blocked. This missing capability blocks only that output;
   preserve independent supported outputs and report their separate status.
4. **Select authorized inputs and output.** Use only explicitly supplied or
   verified-profile template/stencil sources with actual access and applicable
   brand/provenance permission. This method does not install libraries, search
   personal template homes or assume a template exists. A neutral shape/stencil
   choice needs an explicit applicable choice, not a required-brand bypass.
   Confirm an owned output path and preserve supplied artifacts; no implicit
   overwrite, personal-home or current-directory fallback.
5. **Declare proof before production.** Record the required format, source
   retention, editable reopen, connectors, labels and required inspection
   observations under the existing evidence/profile contract. Required missing,
   failed or unverified observations block completion. Plan the appropriate
   diagram type, layout and connector directions from the supplied source.
   Use the selected design palette and applicable provider stencils when present;
   do not infer live cloud topology or choose a provider from a generic example.

## Conditional production and actual proof

Proceed only through the writer established above and within its granted scope.
This section is an evidence obligation for an externally supplied capability,
not a bundled implementation.

- Record the actual writer operation, output path and result. Verify the saved
  artifact's actual requested format; a file extension is not format evidence.
  **No image-as-VSDX substitution:** an embedded raster, renamed SVG/PNG, preview
  or screenshot cannot satisfy an editable VSDX/drawio request. Switching formats
  requires an explicit changed request, never an implicit fallback.
- For editable output, reopen the saved artifact using the available authorized
  editor. Observe native shapes, connectors with their actual endpoint bindings
  and directions, and editable labels. Exercise a bounded edit on an owned copy,
  save and reopen it, then read back the changed label/connection. Preserve the
  original supplied sources and identify which final artifact was inspected.
  An opaque imported image or a package that merely opens is insufficient.
- Compare every source entity, connection, label/caption and qualification with
  the saved result. Inspect stencil consistency and visible layout at the actual
  permitted rendering layer, recording missing, clipped or disconnected content.
  SVG/PNG exports need actual format/content and required visual observations;
  they do not establish editable-diagram proof or VSDX support.
- Invoke `/li:generate-qa --artifacts <diagram-path>` only on an actually produced
  selected artifact, retaining report-only QA and its source comparison. Repair
  requires a distinct authorized output and renewed affected evidence.
  **QA handoff is not completion evidence.** Consume actual QA/inspection results
  for the same artifact, source and profile. Missing rendering, readback or required
  independent review stays unverified; an empty issues list cannot clear it.
- Return requested versus produced format, source/artifact identities, actual
  operations and observations, gates, unavailable capabilities and the next
  supported action. A preview can be reported as a preview, never as a completed
  requested editable deliverable.

## Optional architecture advice

Per `skills/generate/agent-mapping.yaml`, these retained names are source hints,
not automatic dispatch:
- Primary: SystemArchitect — architecture/topology advice when requested.
- Conditional: SecurityAuditor — advice on trust zones/DMZ when requested and authorized.

Use only the roles actually declared by that mapping and available on the host.
SystemArchitect can advise on topology; neither role is a Visio writer or proof
that a requested output format can be produced. No new actor is required to
report an unavailable writer, and advisory work does not satisfy independent review.

## Voice and sharing

`voice: internal` is the default. Labels and captions retain the applicable
voice/source-fidelity obligations. With `--customer-share`, preserve the actual
upstream voice-gate result on unchanged labels where the active pack requires it
(`voice.gates_active`; none by default), plus all applicable brand, compliance,
honest-limitations and provenance requirements. A mandatory unverified gate
blocks that output. A produced diagram or successful QA is not distribution
permission; this preflight sends nothing.

## Reusable patterns

Follow the [reusable pattern consumer contract](../pattern/references/consumer-contract.md).
Resolve or verify the supplied attachment and record each mandatory pattern clause
as unverified unless its presence in the produced diagram was actually inspected.
Patterns never promote this staged template slot, and diagrams are not verified
cloud state.

## Status protocol

- **DONE** — only the actual requested format was produced by an available
  authorized writer, its required source/format, connector/label, QA and required
  inspection evidence (including editable reopen for editable outputs) were
  observed for the same artifact, and
  every applicable mandatory control and pattern clause passed. This does not
  claim Lintel implements a VSDX writer.
- **DONE_WITH_CONCERNS** — the same required proof as DONE, with only explicitly
  advisory limitations; never a missing writer, required inspection or failed
  mandatory clause.
- **BLOCKED** — a requested writer/operation, authority or required proof is
  missing, failed or unverified. Keep other independent requested outputs separate.
- **NEEDS_CONTEXT** — the requested format, diagram source, selected run/design,
  output ownership or required template choice is unresolved.

## Next supported action

Report the missing operation and preserve any source preparation. The operator
may explicitly select a real authorized writer or change the requested output;
neither is assumed. Feed an actually approved export into the selected deck or
document method only through its supported input contract. For several requested
formats, GENERATE retains the separate per-format gates and unfinished-output
report. Repeated requests or a useful layout do not automatically promote the
slot, install dependencies or waive format acceptance.
