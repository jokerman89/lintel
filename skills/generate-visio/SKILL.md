---
name: generate-visio
layer: foundation
description: ⚠ TEMPLATE ONLY — Slot for Visio diagram generation (architecture sketches, network topologies, process flows). Content not curated. AI generates fresh at invocation per L-001.
color: orange
tools: Read, Write, Bash, Glob
voice: internal
cli_support:
  - cli: claude-code
    level: full
  - cli: codex
    level: degraded
---

## ⚠ TEMPLATE ONLY — Slot for Visio generation

This skill is a **scaffolding slot** per L-001 (Lintel = scaffolding, not curated content). The frontmatter + agent-mapping entry exist; the workflow body does not. When an operator invokes this skill, the AI generates the appropriate workflow content at invocation time using the design-spec.json + content.md from the shared pipeline.

## Why a slot exists

Visio diagrams are highly content-specific: architecture topology, sequence diagram, swimlane, network layout, deployment pipeline. The shared pipeline cannot pre-bake a "general Visio workflow" because what gets diagrammed depends entirely on what's being engaged. AI-at-invocation reads content.md → detects what should be diagrammed → produces appropriate stencil/connector layout.

Alternative consideration: Visio diagrams are often delivered as `.vsdx` (Visio format), `.svg` (vector), or `.png` (raster export). The slot accepts `--output-format <vsdx|svg|png|drawio>` to handle the spectrum.

## At-invocation contract

When invoked (via `/li:generate-visio --from-pipeline <run-dir>` or directly):

1. **Diagram-type detection:** AI reads content.md + identifies sections with diagrammable content (architecture sketches in §X, network topologies in §Y, process flows in §Z). Detection signals: keywords like "topology," "flow," "sequence," "deployment," explicit Visio mentions in `notes_for_writer` from outline.
2. **Diagram-type selection:** Per detected section, AI picks the right Visio diagram-type (Cloud Architecture, Network, Cross-functional Flowchart, Sequence Diagram, etc.). For cloud-architecture content, defaults to a cloud-architecture stencil set (provider-specific stencils contributed by the active pack if present).
3. **Stencil + connector layout:** AI lays out shapes per standard architecture-diagram reference patterns. Uses design-spec.json's palette for color-coding (primary for compute, secondary for network, accent for identity, etc.).
4. **Output-format selection:** Default `vsdx` for editable handoff. `svg` for embedded artifacts. `png` for slide-embed. `drawio` for collaborative editing if customer prefers draw.io over Visio.
5. **Build:** Use python-vsdx or libvsx-equivalent (or generate via draw.io XML format if more reliable). Brand-template from `~/.lintel/brand/visio-templates/` if present.
6. **QA hand-off:** Pass produced diagram to `/li:generate-qa` for validation (mostly visual — stencil-consistency, connector-validity).

## Brand template

`~/.lintel/brand/visio-templates/` slot exists. Templates might include: `cloud-architecture-base.vsdx`, `network-topology-base.vsdx`, `swimlane-base.vsdx`. If template present, AI uses it as starting stencil set. If empty, AI uses generic shapes (or a provider stencil set contributed by the active pack).

## Agent dispatch

Per `skills/generate/agent-mapping.yaml`:
- Primary: SystemArchitect (default architecture/topology diagrams)
- Conditional: NetworkArchitect if topology-focused content
- Conditional: SecurityAuditor if diagram includes security boundaries (trust zones, DMZ)

## Voice tier

`voice: internal` default. Diagrams have minimal prose (labels, captions). Voice constraints apply to labels but loosely.

If invoked with `--customer-share`, requires an upstream PASS from the active pack's voice gate (none by default) on any text labels in diagram (orchestrator-level gate).

## Status protocol

- **DONE** — diagram produced (vsdx/svg/png/drawio) + qa-handoff successful
- **DONE_WITH_CONCERNS** — produced but qa flagged stencil-inconsistency or label issues
- **BLOCKED** — content.md has no diagrammable sections + no fresh-architecture strategy declared
- **NEEDS_CONTEXT** — `--from-pipeline` directory missing, design-spec absent, or output-format unspecified for ambiguous content

## When to promote from slot to curated

If a recurring diagram-pattern emerges (e.g., always the same cloud-architecture with same shape-layout), promote that pattern into the SKILL.md body — that becomes a canonical Visio-builder for that scenario.

Until then: AI generates fresh per invocation. Repo stays clean.

## Recommended next steps

After invocation:
- For QA: `/li:generate-qa --artifacts <diagram-path>`
- For embedding in deck: chain `/li:generate-ppt --include-diagram <svg-path>` after diagram approved
- For collaborative editing: invoke with `--output-format drawio` and share .drawio file
- For multi-format consistency: invoke parent `/li:generate` instead of solo-invocation
