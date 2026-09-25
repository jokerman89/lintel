---
slug: native-workflows
date: 2026-09-25
cycle_id: legacy-cleanup-e9c20b62
operator: authorized cleanup coordinator
affected_paths:
  - skills/
  - agents/
  - hooks/shared/
  - bin/
  - lib/capability-selections.json
  - config/aliases.yaml
  - docs/
  - shims/
risk_class: high
breaking_change: true
---

# Structure change: Native workflow consolidation

## What changed

The source now declares 94 canonical skills and retains all 69 agent roles. Six
attributable lanes consolidate duplicate methods, with a single coordinator
joining actual provider, helper, installer, generator and evidence consumers.
[ADR-0034](../../decisions/0034-native-workflow-consolidation.md) records the decision.
Frontmatter requirements and shared review/profile/work-map schemas are unchanged.

## Backward compatibility

Old saved checkpoints, memory grammar, job-step/phase resume, selected-work
precedence, native path ownership and install receipts stay readable. Required
review/QA controls, latest rejection and actual independent corroboration remain.
Browser and extraction implementation bytes are retained at their new canonical
resource paths. PDF preparation/printing and workbook capabilities stay; the
reader removed by ADR-0033 is not restored.

Public command names and selected argument spellings intentionally change.
Verification no longer implies repair. Removed aliases do not delete old data.
The optional freeze hook is still advisory, and generated adapter files are not
proof of host activation, permission or successful model execution.

## Migration path

Use [the operator migration guide](../../../docs/migrations/2026-09-25-native-workflows.md).
Re-run the existing owned installer or repository adapter update; conflicts with
user edits must stop rather than overwrite. No dependency, policy, client or
personal configuration is installed by this cleanup.

## Forward compatibility

One method owns each consolidated capability, keeping public choices separate from
the shared evidence and provider contracts. Source metadata keeps legitimate
vendor support and required provenance. Explicit source-era observations are
reported separately from current routing, without a blanket historical exemption.

## Verification

Focused checks cover plan/repo lenses, read-only versus repair contracts, literal
resume classification, safe context/memory callers, freeze producer/hook agreement,
browser/PDF consumer linkage, metadata closure, aliases and stale routing.
Generated outputs follow their existing generators. Strict hosted sharding and
independent specification then quality review remain required; unfinished checks
are recorded in the selected plan rather than labelled successful.

The actual `li-compat-audit --against 77cb8d3f893d2ef42be2631fe35ae45594f21bd3
--output native-workflows` result is **RED**: 60 frontmatter-change candidates,
13 moves, 26 possible-default candidates and two shared shell helpers (101 total
category entries, not 101 independent defects). These include the explicitly
authorized entry renames and verification-default change. No field/schema
requirement was relaxed to hide them. The raw generated report is preserved in
session evidence with SHA-256
`77754f46ece923734e545741af4863cd97d8d5f33d5a11eff2da2ec76acebf64`.
Its structural warning requires the migration/callsite and independent review
already selected for this initiative; it is not represented as a green audit.

The initial integrated PDF-consumer fixture used a non-executable synthetic Python
path and failed before print. The corrected fixture uses the real read-only URL
policy helper and synthetic browser methods, covering successful/failed print
cleanup without producing a PDF or launching a browser. This is not native print
acceptance. Native Windows newline argument transport required the selector's
invalid-input fixture to construct its literal newline inside Bash.

## Rollback

Preserve the original lane commits and integration mapping. A rollback is a
reviewed forward change or ordinary revert of the selected batch; never rewrite
history, delete user data, resurrect stale clearance or restore the removed reader
without a new decision. Presentation publication and the separate upstream record
follow-up are outside this change.
