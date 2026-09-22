# ADR-0029: Required policy and content-bound profile contexts

**Status:** Accepted within the authorized P07 implementation of 2026-09-20.
**Scope:** A07 and A20.3/4; dependent acceptance remains with P05/P06/P08/P14.
**Authority:** `.claude/plans/universal-implementation/packages/P07.md`.

## Context

The old resolver documented optional active-pack fallback and emergency hardcoded
neutral values. Its PID-derived cache did not survive fresh tool processes, ignored
pointer changes and deletions, and used modification times for manifest freshness.
A failed corporate-policy load could therefore look like advisory activation.
Historic internal v4/v5 labels also cannot be compared to the public 0.x version.

## Decision

Keep one active pack, the existing source/target boundary, and whole-top-level-block
inheritance. Keep the public shell functions as adapters over one structured,
data-only Python implementation. That implementation parses the documented manifest
subset once per input, and uses the same typed objects for validation, effective
values, provenance, compatibility and content fingerprints. No manifest is executed.
Extension-pack declarations remain awareness, not discovery or hook activation.

An optional target `.claude/profile-requirements.json` declares a required named pack
outside that pack's manifest. Repository requirements outrank a global preference;
a conflicting explicit invocation fails rather than replacing that requirement.
Explicit `LINTEL_PROFILE_PACK` selection is also required. A missing, malformed or
incompatible required pack produces an unresolved error, never neutral success.

Only the legacy active-pack pointer is an optional preference. An invalid optional
preference may use the validated neutral baseline with a diagnostic and an explicit
`fallback` status. No selection means valid neutral first use. An invalid neutral
baseline or unavailable parser is an error; there are no hardcoded emergency values.
The legacy `profile.yaml` mode/role preferences do not select a pack.

Pack directory precedence remains configured store, target repository, then installed
source bundle. Explicit approved source/target/store paths remain honored. Requirements
cannot be bypassed by choosing a second requirements file. Source paths and all ancestry
content are part of identity, not just a display name or version.

A host supplies a stable work/session context, or explicitly carries its context file
and reference. `LINTEL_PROFILE_CONTEXT`, explicit `LINTEL_SESSION_ID` and a real host
`CLAUDE_SESSION_ID` are supported; a PID or PPID is never invented as session identity.
Without a stable context, one-shot reads still work, but cannot produce a pinned handoff.
The lifecycle bootstrap does not leave this as advice: `lintel_copilot_env` atomically
creates or verifies a repository-local selected work reference when no host ID is supplied,
and exports it for the tool process. Subsequent fresh bootstraps verify that same reference.
This is a selected repository work context, not an invented host session ID. Explicit
context IDs separate independent work; resume references outrank a new ambient host ID.

Runtime records live under the selected `LINTEL_HOME` or target `.claude/runtime/`.
Every read of a bound context verifies its inputs by SHA-256, including the active
pointer, requirements, selected manifests, parents, defaults and compatibility source.
Same-mtime edits, deletion, source/target changes and a changed pointer block the read.
No implicit re-resolution is permitted. An explicit, reason-bearing rebind validates
the new context and archives the previous generation without destroying old evidence.
The operator then replans affected work and obtains new dependent review evidence.
The legacy `clear_pack_cache` name requests this explicit rebind, not evidence deletion.

A compact, versioned profile reference binds context, generation and digest to the
effective pack name/version. Producers and handoff/resume consumers use the shared
reference validator. A content digest is not proof of an actor, policy enforcement or
independent review. A different target checkout is not silently substituted for the
bound source/target; its transfer needs an explicit context decision.

Pack schema, pack release, public product and feature compatibility are independent:

- Missing `schema_version` retains legacy schema-1 syntax; explicit unsupported schemas fail.
- `version` is the pack's own semantic version.
- `requires_lintel_product` constrains the actual installed product version.
- `requires_capabilities` constrains the resolver's declared feature contract versions,
  not host permissions or observed client support.
- Exact historical `requires_lintel: ">=4.0.0"` is a documented legacy pack-v1 marker,
  not a requirement that today's public product be v4. Other historical ranges require
  explicit migration; they are not guessed into a new meaning.

Compatibility is evaluated for every ancestor, so a child cannot erase an incompatible
parent requirement by replacing a top-level field.

## Alternatives

1. Keep advisory fallback and document a caller check. Rejected: a broken manifest can
   erase the very declaration that tells callers a check was mandatory.
2. Add a global configuration service or host-specific session daemon. Rejected: it
   adds authority and lifecycle machinery that small local records do not need.
3. **Selected:** external requirement data, one parser/representation, explicit stable
   context and verified references over the existing pack and runtime locations.

## Compatibility and verification

This explicitly supersedes only the old resolver's emergency-success, pointer-ignore,
deletion-tolerance and mtime-refresh semantics. Historic ADRs are not rewritten.
ADR-0018's extension contract, whole-block replacement, missing-field neutral defaults,
explicit null/false/empty/list values and normal shell accessors remain.

Synthetic-fixture tests cover producer -> fresh process -> delegated handoff -> cold
resume, source/target precedence, required failure, fallback labeling, type/provenance
preservation, duplicate keys, incompatible versions and same-mtime parent/pointer drift.
Real private packs, host hook registration and paid model runs are not part of this work.
Independent review and joined P05/P06/P08 acceptance remain distinct from these tests.
